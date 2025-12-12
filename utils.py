"""Utility functions for Smart CV application."""
import logging
import os
import re
import json
logger = logging.getLogger(__name__)


def ensure_dirs() -> None:
    """Create necessary directories if they don't exist."""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)


def clean_output(text: str) -> str:
    """Clean output from LLM."""
    if not text:
        return ""
    cleaned = text.replace("```markdown", "").replace("```", "")
    pattern = r"(<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>)"
    matches = re.findall(pattern, cleaned, re.DOTALL)
    for match in matches:
        cleaned = cleaned.replace(match[0], match[1])
    cleaned = (
        cleaned.replace("text", "")
        .replace("sub_title", "")
        .replace("table", "")
        .replace("image", "")
        .replace("```json", "")
        .replace("```", "")
    )
    return cleaned

def extract_json_from_text(text: str) -> str:
    if not text:
        return "{}"
    
    # Try parsing directly first
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    
    # Find JSON object in text by counting braces
    start_idx = text.find('{')
    if start_idx == -1:
        return "{}"
    
    # Count braces to find end position
    brace_count = 0
    in_string = False
    escape_next = False
    
    for i in range(start_idx, len(text)):
        char = text[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx:i+1]
    
    # If no valid JSON found, return text from { to end
    return text[start_idx:] if start_idx != -1 else "{}"