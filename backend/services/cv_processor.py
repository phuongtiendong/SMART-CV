"""CV processing service - handles OCR, parsing, and scoring."""
import json
import logging
from datetime import datetime
from typing import Dict, Optional

import google.generativeai as genai

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from config import GOOGLE_GENAI_API_KEY, GOOGLE_VISION_API_KEY, LLM_MODEL_NAME
from backend.models.database import get_db_connection
import ocr
import llm_processor
import marker

logger = logging.getLogger(__name__)


class CVProcessor:
    """Service for processing CVs: OCR, parsing, and scoring."""
    
    def __init__(self):
        """Initialize the CV processor with LLM model."""
        if not GOOGLE_GENAI_API_KEY:
            raise ValueError("GOOGLE_GENAI_API_KEY is not configured")
        
        genai.configure(api_key=GOOGLE_GENAI_API_KEY)
        self.model = genai.GenerativeModel(LLM_MODEL_NAME)
    
    def process_cv(self, file_bytes: bytes, job_id: int, jd_text: str) -> Dict:
        """
        Process a CV: OCR, parse, and score against JD.
        
        Args:
            file_bytes: PDF file bytes
            job_id: ID of the job position
            jd_text: Job description text
            
        Returns:
            Dictionary containing candidate info, scores, and reasons
        """
        # OCR PDF
        if not GOOGLE_VISION_API_KEY:
            raise ValueError("GOOGLE_VISION_API_KEY is not configured")
        
        cv_text = ocr.ocr_pdf(file_bytes, GOOGLE_VISION_API_KEY)
        if not cv_text:
            raise ValueError("Could not extract text from CV. Please try a different file.")
        
        # Parse CV with LLM
        info = llm_processor.parse_with_llm(cv_text, self.model)
        if not info:
            raise ValueError("Could not parse CV. Please try again.")
        
        # Prepare text for scoring
        education = info.get("education", "")
        experience = info.get("experience", "")
        skills = info.get("skills", "")
        projects = info.get("projects", "")
        awards = info.get("awards", "")
        publications = info.get("publications", "")
        languages = info.get("languages", "")
        
        education_text = "Education: " + str(education)
        experience_text = "Experience: " + str(experience)
        skills_text = "Skills: " + str(skills) + "Projects: " + str(projects)
        awards_text = "Awards: " + str(awards) + "Publications: " + str(publications)
        languages_text = "Languages: " + str(languages)
        
        # Compute scores for each category
        score_education = int(marker.compute_score(jd_text, education_text, self.model, "Education")["score"])
        score_experience = int(marker.compute_score(jd_text, experience_text, self.model, "Experience")["score"])
        score_skills = int(marker.compute_score(jd_text, skills_text, self.model, "Skills")["score"])
        score_awards = int(marker.compute_score(jd_text, awards_text, self.model, "Awards")["score"])
        score_languages = int(marker.compute_score(jd_text, languages_text, self.model, "Languages")["score"])
        
        # Calculate total score (average of all categories)
        total_score = (score_education + score_experience + score_skills + score_awards + score_languages) / 5
        
        score_dict = {
            "Education": score_education,
            "Experience": score_experience,
            "Skills": score_skills,
            "Awards": score_awards,
            "Languages": score_languages
        }
        
        # Get reasons for each score
        reason_dict = {
            "Education": marker.compute_score(jd_text, education_text, self.model, "Education")["reason"],
            "Experience": marker.compute_score(jd_text, experience_text, self.model, "Experience")["reason"],
            "Skills": marker.compute_score(jd_text, skills_text, self.model, "Skills")["reason"],
            "Awards": marker.compute_score(jd_text, awards_text, self.model, "Awards")["reason"],
            "Languages": marker.compute_score(jd_text, languages_text, self.model, "Languages")["reason"]
        }
        
        # Save to database
        self._save_analysis(info, job_id, jd_text, total_score)
        
        return {
            "info": info,
            "score_dict": score_dict,
            "reason_dict": reason_dict,
            "total_score": total_score
        }
    
    def _save_analysis(self, info: Dict, job_id: int, jd_text: str, score: float) -> None:
        """Save analysis result to database."""
        payload = {
            "info": info,
            "jd": jd_text,
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analyses (job_id, name, email, phone, score, jd_text, cv_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    info.get("name", ""),
                    info.get("email", ""),
                    info.get("phone", ""),
                    score,
                    jd_text,
                    json.dumps(payload, ensure_ascii=False),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
        
        logger.info("Saved analysis result for candidate: %s", info.get("name", "Unknown"))
