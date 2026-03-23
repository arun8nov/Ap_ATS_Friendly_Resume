import os
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
# AGENT 2 — ATS Resume Optimizer
# ──────────────────────────────────────────────
def agent_resume_optimizer(jd_text: str, resume_latex: str, keyword_analysis: str) -> dict:
    system_prompt = """You are an expert LaTeX resume writer and ATS optimization specialist.

Your task is to optimize a LaTeX resume for a specific job description.

STRICT RULES:
1. Return ONLY valid LaTeX code — no explanation, no markdown, no commentary
2. Do NOT change the overall structure or layout of the resume
3. Keep it to ONE page — remove less relevant content if needed
4. Update the job title/headline to match the JD
5. Add missing critical keywords naturally into existing bullet points
6. Remove keywords irrelevant to this specific JD
7. Keep all section headers the same
8. Do NOT add new sections
9. Make it ATS parsable — no tables, no columns in critical sections, no graphics for text
10. Use standard LaTeX resume formatting only
"""

    user_prompt = f"""JOB DESCRIPTION:
{jd_text}

ORIGINAL RESUME (LaTeX):
{resume_latex}

KEYWORD ANALYSIS FROM AGENT 1:
{keyword_analysis}

Now produce the optimized LaTeX resume code following all the rules strictly.
Return ONLY the LaTeX code starting from \\documentclass."""

    result = call_llm(system_prompt, user_prompt, temperature=0.3)

    # Clean up if model wraps in markdown
    if "```latex" in result:
        result = result.split("```latex")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()

    return {"latex": result}