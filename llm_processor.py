"""LLM processing functions for parsing and scoring CVs."""
import json
import logging
import re
from typing import Dict
from prompt import prompt_extract_candidate_info
from utils import clean_output
from utils import extract_json_from_text
logger = logging.getLogger(__name__)



def parse_with_llm(markdown: str, model) -> Dict[str, object]:
    """
    Extract structured JSON from CV markdown using LLM.
    
    Args:
        markdown: CV content from OCR
        model: Initialized Google Generative AI model
        
    Returns:
        Dictionary containing candidate information
    """
    try:
        from google import genai  # type: ignore
    except Exception:
        logger.warning("google-genai not installed, fallback parse_cv.")

    prompt = prompt_extract_candidate_info(markdown)
    text = ""
    try:
        response = model.generate_content(contents=prompt)
        
        # Check if response has text
        if not response or not hasattr(response, 'text') or not response.text:
            logger.error("LLM response has no text")
            return {}
        
        # Clean output
        text = clean_output(response.text)
        
        # Extract JSON if there's extra text
        json_text = extract_json_from_text(text)
        
        # Parse JSON
        result = json.loads(json_text)
        
        # Ensure all required fields exist
        default_fields = {
            "name": "",
            "email": "",
            "phone": "",
            "address": "",
            "education": "",
            "experience": "",
            "skills": "",
            "projects": "",
            "awards": "",
            "publications": "",
            "languages": ""
        }
        
        # Merge with defaults to ensure all fields exist
        for key in default_fields:
            if key not in result:
                result[key] = default_fields[key]
        
        logger.info("LLM parse successful for candidate: %s", result.get("name", "Unknown"))
        return result
        
    except json.JSONDecodeError as exc:
        logger.error("Error parsing JSON from LLM response: %s. Text: %s", exc, text[:200] if text else "N/A")
        return {}
    except AttributeError as exc:
        logger.error("Attribute error from LLM response: %s", exc)
        return {}
    except Exception as exc:
        logger.error("LLM extract error: %s. Text: %s", exc, text[:200] if text else "N/A", exc_info=True)
        return {}