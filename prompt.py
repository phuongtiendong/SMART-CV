def prompt_extract_candidate_info(text_content: str) -> str:
    return f"""
        Please read the following markdown and extract all available candidate information into a single JSON object without code block.

        Markdown content:
        {text_content}

        Your task:
        - Parse the markdown and identify the candidate's details.
        - Return only a JSON object without code block containing the following fields:

        {{  
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
        }}

        Guidelines:
        - Each list field should contain full extracted items.
        - Fill each field with the extracted information from the markdown.
        - If a field is not present or cannot be determined, leave it as an empty string.
        - "education" is a list of dictionaries, each dictionary contains "start - end", "school name", "degree", "description" by order of time.
        - "experience" is a list of dictionaries, each dictionary contains "start - end", "company name", "position", "description" by order of time.
        - "skills" is a list of strings.
        - "projects" is a list of dictionaries, each dictionary contains "name", "description", "technologies used".
        - "awards" is a list of dictionaries, each dictionary contains "name", "date", "description".
        - "publications" is a list of dictionaries, each dictionary contains "title", "date", "description".
        - "languages" is a list of strings.
        - Return only valid JSON, no additional text or explanation.
    """

def prompt_compute_score_education(jd_text: str, sub_infor: str) -> str:
    return f"""
        Please read the following JD and information about education of candidate in CV and compute the score between them. Score will be [0-100].

        JD content:
        {jd_text}

        information about education of candidate in CV content:
        {sub_infor}

        Criteria:
        - The score is computed based on the similarity between the information about field of study required in JD and the information about education of candidate in CV.
        - Point will be higher if the university is famous and the final point of degree is higher.
        - Return text **only** json object by following format:
        {{
            "score": 0-100,
            "reason": "reason for the score"
        }}
        - Reason should be in same language as the language of the CV.
        - Reason should be in markdown format. And short and concise.
    """ 

def prompt_compute_score_experience(jd_text: str, sub_infor: str) -> str:
    return f"""
        Please read the following JD and information about experience of candidate in CV and compute the score between them. Score will be [0-100].

        JD content:
        {jd_text}

        information about experience of candidate in CV content:
        {sub_infor}

        Criteria:
        - The score is computed based on the similarity between the JD and the information about experience of candidate in CV.
        - Point will be higher if the experience is relevant to the JD and the experience is more recent.
        - Return text **only** json object by following format:
        {{
            "score": 0-100,
            "reason": "reason for the score"
        }}
        - Reason should be in same language as the language of the CV.
        - Reason should be in markdown format. And short and concise.
    """

def prompt_compute_score_skills(jd_text: str, sub_infor: str) -> str:
    return f"""
        Please read the following JD and information about skills of candidate in CV and compute the score between them. Score will be [0-100].

        JD content:
        {jd_text}

        information about skills of candidate in CV content:
        {sub_infor}

        Criteria:
        - The score is computed based on the similarity between the JD and the information about skills of candidate in CV.
        - Point will be higher if the skills are relevant to the JD and the skills are more recent.
        JD content:
        - Return text **only** json object by following format:
        {{
            "score": 0-100,
            "reason": "reason for the score"
        }}
        - Reason should be in same language as the language of the CV.
        - Reason should be in markdown format. And short and concise.
    """

def prompt_compute_score_awards(jd_text: str, sub_infor: str) -> str:
    return f"""
        Please read the following JD and information about awards of candidate in CV and compute the score between them. Score will be [0-100].

        JD content:
        {jd_text}

        information about awards of candidate in CV content:
        {sub_infor}

        Criteria:
        - The score is computed based on the similarity between the JD and the information about awards of candidate in CV.
        - Point will be higher if the awards are relevant to the JD and the awards are more recent.
        - Return text **only** json object by following format:
        {{
            "score": 0-100,
            "reason": "reason for the score"
        }}
        - Reason should be in same language as the language of the CV.
        - Reason should be in markdown format. And short and concise.
    """

def prompt_compute_score_languages(jd_text: str, sub_infor: str) -> str:
    return f"""
        Please read the following JD and information about languages of candidate in CV and compute the score between them. Score will be [0-100].
    
        JD content:
        {jd_text}

        information about languages of candidate in CV content:
        {sub_infor}

        Criteria:
        - The score is computed based on the similarity between the JD and the information about languages of candidate in CV.
        - Point will be higher if the languages are relevant to the JD and the languages are more recent.
        - More languages will be better.
        - Return text **only** json object by following format:
        {{
            "score": 0-100,
            "reason": "reason for the score"
        }}
        - Reason should be in same language as the language of the CV.
        - Reason should be in markdown format. And short and concise.
    """