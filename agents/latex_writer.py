import json
from utils.gemini_client import get_gemini_response
from utils.file_reader import read_base_resume

def rewrite_resume_latex(gap_report: dict, selected_projects: list) -> str:
    base_latex = read_base_resume()
    if not base_latex:
        return "Error: Base resume not found. Please add data/base_resume.tex"
        
    prompt = f"""You are an expert resume writer and LaTeX copy editor.
Treat the base LaTeX as sacred. You are a copy editor, not an author.
Never add new sections. Never remove sections. Never change \\section{{}} names.
Rewrite the bullet points and skills to naturally include missing JD keywords from the gap report.
Incorporate the selected projects into the projects section if there is one.
Keep content concise so it fits in one physical page (max 3 bullets per role, max 8 skills, max 2 projects).

Gap Report (Keywords to naturally weave in):
{json.dumps(gap_report, indent=2)}

Selected Target Projects:
{json.dumps(selected_projects, indent=2)}

Base LaTeX Resume:
{base_latex}

Return ONLY valid LaTeX, without any markdown formatting or explanation.
Wrap your entire LaTeX output strictly between these two exact markers:
%%% RESUME BEGIN %%%
\\documentclass...
%%% RESUME END %%%
"""
    response_text = get_gemini_response(prompt)
    
    if "%%% RESUME BEGIN %%%" in response_text and "%%% RESUME END %%%" in response_text:
        latex = response_text.split("%%% RESUME BEGIN %%%")[1].split("%%% RESUME END %%%")[0].strip()
        return latex
    
    clean_text = response_text.replace("```latex", "").replace("```", "").strip()
    return clean_text
