import json
from utils.gemini_client import get_gemini_response
from utils.file_reader import read_projects

def select_best_projects(jd_text: str) -> list:
    projects = read_projects()
    if not projects:
        return []
        
    projects_list_str = "\n".join(projects)
    
    prompt = f"""You are an expert technical recruiter.
I have a list of my actual GitHub projects below. Pick the 2 to 3 most relevant projects for this specific job.

CRITICAL RULES:
- You may ONLY select from the projects listed below. Do NOT invent or hallucinate any project names.
- For each chosen project, rewrite its description using language and keywords from the Job Description.
- If none of the projects are relevant, return an empty JSON array [].

My Projects (ONLY pick from these):
{projects_list_str}

Job Description:
{jd_text}

Return ONLY a valid JSON array of objects with the exact structure below, without any markdown formatting, backticks, or extra text:

[
  {{
    "name": "Exact project name from the list above",
    "link": "Exact link from the list above",
    "description": "One-line description rewritten to match JD keywords"
  }}
]
"""
    response_text = get_gemini_response(prompt)
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return [{"name": "Error", "link": "", "description": "Failed to parse JSON: " + str(e)}]
