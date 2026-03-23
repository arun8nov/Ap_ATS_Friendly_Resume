import json
from utils.gemini_client import get_gemini_response

def extract_jd_keywords(jd_text: str) -> dict:
    prompt = f"""You are an ATS (Applicant Tracking System) expert. 
Extract everything an ATS scanner would care about from the following Job Description.

Return ONLY a valid JSON object with the exact structure below, without any markdown formatting, backticks, or extra text:

{{
  "required_skills": [],
  "preferred_skills": [],
  "job_titles": [],
  "tools_and_frameworks": [],
  "action_verbs": [],
  "key_phrases": []
}}

Job Description:
{jd_text}
"""
    response_text = get_gemini_response(prompt)
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {"error": "Failed to parse JSON: " + str(e), "raw_response": response_text}
