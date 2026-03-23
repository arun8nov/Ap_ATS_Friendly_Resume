import json
import re
from utils.gemini_client import get_gemini_response
from utils.file_reader import read_base_resume

def strip_latex(latex_str: str) -> str:
    text = re.sub(r'%.*?\n', '\n', latex_str)
    text = re.sub(r'\\[a-zA-Z]+\*?\{(.*?)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
    text = text.replace('{', '').replace('}', '').replace('\\', '')
    return text.strip()

def compare_resume_to_jd(jd_keywords: dict) -> dict:
    latex_resume = read_base_resume()
    if not latex_resume:
        return {"error": "Base resume not found. Please add data/base_resume.tex"}
        
    plain_text_resume = strip_latex(latex_resume)
    
    prompt = f"""You are an ATS (Applicant Tracking System) expert.
Compare the following candidate's resume against the Job Description keywords.
Identify what matches, what's missing, weak matches, and give suggestions.

Job Description Keywords:
{json.dumps(jd_keywords, indent=2)}

Candidate Resume (Plain Text extracted from LaTeX):
{plain_text_resume}

Return ONLY a valid JSON object with the exact structure below, without any markdown formatting, backticks, or extra text:

{{
  "matching_keywords": [],
  "missing_keywords": [],
  "weak_matches": [],
  "suggestions": []
}}
"""
    response_text = get_gemini_response(prompt)
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON: " + str(e)}
