import os
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

MODEL = "meta/llama-3.1-8b-instruct"



def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        top_p=0.95,
        max_tokens=16384,
        stream=True
    )
    full_response = ""
    for chunk in completion:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
    return full_response


# ──────────────────────────────────────────────
# LOAD ALL RESUMES FROM /resumes FOLDER
# ──────────────────────────────────────────────
def load_all_resumes(folder: str = "resumes") -> dict:
    """Returns {filename: latex_content} for all .tex files in folder"""
    resumes = {}
    if not os.path.exists(folder):
        os.makedirs(folder)
    for path in glob.glob(os.path.join(folder, "*.tex")):
        name = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            resumes[name] = f.read()
    return resumes


# ──────────────────────────────────────────────
# AGENT 1 — ATS Keyword Analyzer
# ──────────────────────────────────────────────
def agent_keyword_analyzer(jd_text: str, resume_latex: str) -> dict:
    system_prompt = """You are an ATS (Applicant Tracking System) expert and resume analyst.
Your job is to compare a Job Description with a candidate's resume and provide a detailed keyword analysis.

Return your response in this EXACT format:

## JOB TITLE DETECTED
<detected job title from JD>

## MATCH SCORE
<percentage 0-100>%

## MATCHED KEYWORDS
<comma separated list of keywords already in resume>

## MISSING CRITICAL KEYWORDS
<comma separated list of must-have keywords from JD missing in resume>

## MISSING NICE-TO-HAVE KEYWORDS
<comma separated list of secondary keywords missing>

## SKILLS GAP SUMMARY
<2-3 sentence summary of gaps>

## RECOMMENDED CHANGES
<bullet points of specific changes to make>
"""
    user_prompt = f"""JOB DESCRIPTION:
{jd_text}

RESUME (LaTeX):
{resume_latex}

Analyze the resume against the JD and provide the keyword analysis."""

    result = call_llm(system_prompt, user_prompt, temperature=0.3)
    return {"raw": result}


# ──────────────────────────────────────────────
# AGENT 3 — Multi-Resume Assembler
# ──────────────────────────────────────────────
def agent_resume_assembler(jd_text: str, resumes: dict, keyword_analysis: str) -> dict:
    """
    Reads all resumes, picks the best content from each section
    across all resumes based on JD, assembles one master resume
    in the same LaTeX format as main.tex
    """

    # Build resume bundle text
    resume_bundle = ""
    for filename, content in resumes.items():
        resume_bundle += f"\n\n{'='*60}\nRESUME FILE: {filename}\n{'='*60}\n{content}"

    system_prompt = """You are an expert resume writer and LaTeX specialist.

You have multiple versions of a candidate's resume for different roles.
Your job is to read all of them and assemble ONE best resume tailored to the Job Description.

STRICT RULES:
1. Return ONLY valid LaTeX code — no explanation, no markdown, no commentary
2. Use the SAME LaTeX structure and formatting as the input resumes
3. Pick the BEST and MOST RELEVANT content from each resume section based on the JD
4. Combine skills, experiences, and achievements that best match the JD
5. Keep it to ONE page
6. Update the job title/headline to exactly match the JD role
7. Add missing critical keywords naturally
8. Do NOT invent or fabricate any experience or skills
9. Only use content that actually exists across the provided resumes
10. Output must start with \\documentclass
"""

    user_prompt = f"""JOB DESCRIPTION:
{jd_text}

KEYWORD ANALYSIS:
{keyword_analysis}

ALL RESUME VERSIONS:
{resume_bundle}

Now assemble the best single LaTeX resume by picking the strongest matching content from all the resumes above.
Return ONLY the LaTeX code starting from \\documentclass."""

    result = call_llm(system_prompt, user_prompt, temperature=0.3)

    # Clean up markdown fences if any
    if "```latex" in result:
        result = result.split("```latex")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()

    return {"latex": result}


# ──────────────────────────────────────────────
# AGENT 2 — ATS Resume Optimizer (final polish)
# ──────────────────────────────────────────────
def agent_resume_optimizer(jd_text: str, resume_latex: str, keyword_analysis: str) -> dict:
    system_prompt = f"""You are an expert LaTeX resume writer and ATS optimization specialist.

You strictly follow these professional resume rules:
{open("RESUME_RULES.md", "r", encoding="utf-8").read()}

STRICT RULES:
1. Return ONLY valid LaTeX code — no explanation, no markdown, no commentary
2. Do NOT change the overall structure or layout
3. Keep it to ONE page
4. Make Summary Very Professinol donot start with Aspiring
5. Donot reduce work experience
5. Ensure job title/headline matches the JD
6. Verify all critical keywords are present
7. Make it fully ATS parsable — no tables for critical info, no graphics for text
8. Keep all section headers the same
9. Do NOT add new sections
10. Output must start with \\documentclass
"""

    user_prompt = f"""JOB DESCRIPTION:
{jd_text}

ASSEMBLED RESUME (LaTeX):
{resume_latex}

KEYWORD ANALYSIS:
{keyword_analysis}

Do a final ATS optimization pass and return the polished LaTeX code."""

    result = call_llm(system_prompt, user_prompt, temperature=0.3)

    if "```latex" in result:
        result = result.split("```latex")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()

    return {"latex": result}