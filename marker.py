import json
import logging
from typing import Dict
from prompt import prompt_compute_score_education, prompt_compute_score_experience, prompt_compute_score_skills, prompt_compute_score_awards, prompt_compute_score_languages
from utils import extract_json_from_text
logger = logging.getLogger(__name__)


def compute_score(jd_text: str, sub_infor: str, model, name: str) -> Dict:
    """
    Compute score for a CV category against job description.
    
    Args:
        jd_text: Job description text
        sub_infor: Candidate information for the category
        model: LLM model instance
        name: Category name (Education, Experience, Skills, Awards, Languages)
        
    Returns:
        Dictionary with 'score' and 'reason' keys
    """
    if name == "Education":
        prompt = prompt_compute_score_education(jd_text, sub_infor)
    elif name == "Experience":
        prompt = prompt_compute_score_experience(jd_text, sub_infor)
    elif name == "Skills":
        prompt = prompt_compute_score_skills(jd_text, sub_infor)
    elif name == "Awards":
        prompt = prompt_compute_score_awards(jd_text, sub_infor)
    elif name == "Languages":
        prompt = prompt_compute_score_languages(jd_text, sub_infor)
    else:
        raise ValueError(f"Invalid name: {name}")

    try:
        response = model.generate_content(contents=prompt)
        return json.loads(extract_json_from_text(response.text))
    except Exception as exc:
        logger.warning("LLM score %s error: %s", name, exc)
        return {}

