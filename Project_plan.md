# ATS Resume Builder — Vibe Coding Plan

## What We're Building

A local tool that reads your saved base resume in LaTeX, takes a job description you paste in,
and uses four AI agents (powered by Google Gemini) to generate a new ATS-optimized resume
in the exact same LaTeX format — one page, ready to copy and compile.

No uploads. No fuss. Your base resume lives in the project folder.
Your GitHub and portfolio links live in a text file in the same folder.
You paste a JD, click generate, and copy the new LaTeX.

---

## Project Folder Structure

```
ats-resume-builder/
│
├── data/
│   ├── base_resume.tex         # your LaTeX resume — edit this whenever your base changes
│   └── projects.txt            # paste your GitHub links and portfolio links here, one per line
│
├── backend/
│   ├── main.py                 # FastAPI app — two endpoints, clean and simple
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── jd_extractor.py     # Agent 1 — reads the JD, pulls out keywords
│   │   ├── resume_comparator.py # Agent 2 — compares base resume with JD keywords
│   │   ├── latex_writer.py     # Agent 3 — rewrites resume in LaTeX, same structure
│   │   └── project_selector.py # Agent 4 — picks best projects for this JD
│   └── utils/
│       ├── __init__.py
│       ├── gemini_client.py    # one place to talk to Gemini API
│       └── file_reader.py      # reads base_resume.tex and projects.txt from data/
│
├── frontend/
│   └── app.py                  # Streamlit UI — fast, minimal, just works
│
├── .env                        # GEMINI_API_KEY goes here
├── requirements.txt
└── README.md
```

---

## The Four Agents

### Agent 1 — JD Keyword Extractor

**File:** `backend/agents/jd_extractor.py`

**Job:** Read the raw JD text. Ask Gemini to extract everything an ATS scanner would care about.

**What it returns:**
```json
{
  "required_skills": ["Python", "FastAPI", "Docker"],
  "preferred_skills": ["Kubernetes", "AWS"],
  "job_titles": ["Backend Engineer", "Software Engineer"],
  "tools_and_frameworks": ["PostgreSQL", "Redis", "Git"],
  "action_verbs": ["designed", "built", "scaled", "led"],
  "key_phrases": ["cross-functional teams", "high-traffic systems"]
}
```

**Prompt style:** Direct. Tell Gemini to only return JSON, no extra text.

---

### Agent 2 — Resume Comparator

**File:** `backend/agents/resume_comparator.py`

**Job:** Strip the LaTeX formatting from `base_resume.tex` to get plain text.
Then ask Gemini to compare your resume against the keywords from Agent 1.
Find the gaps — what's missing, what's there but worded differently.

**What it returns:**
```json
{
  "matching_keywords": ["Python", "REST APIs"],
  "missing_keywords": ["Docker", "Kubernetes"],
  "weak_matches": ["built APIs" → "designed scalable REST APIs"],
  "suggestions": ["Add Docker to skills section", "Rephrase project bullet to mention high-traffic"]
}
```

**Important:** This agent does NOT change anything. It only reports.

---

### Agent 3 — LaTeX Resume Writer

**File:** `backend/agents/latex_writer.py`

**Job:** This is the main agent. Takes three inputs:
1. The original `base_resume.tex` (full content, unchanged structure)
2. The gap report from Agent 2
3. The selected projects from Agent 4

Asks Gemini to rewrite the bullet points and skills to naturally include JD keywords —
without ever changing the LaTeX structure, section names, or order.
Must stay within one page.

**Critical prompt rules baked in:**
- Never add new sections
- Never remove sections
- Never change `\section{}` names
- Rewrite bullet points using JD language naturally — not keyword stuffing
- Keep content to what fits in one page
- Return only valid LaTeX, nothing else
- Wrap output between `%%% RESUME BEGIN %%%` and `%%% RESUME END %%%` markers so parsing is clean

---

### Agent 4 — Project Selector

**File:** `backend/agents/project_selector.py`

**Job:** Read `data/projects.txt` which has your GitHub repos and portfolio links.
Ask Gemini to pick 2–3 projects most relevant to this specific JD.
Return each chosen project with a one-line description rewritten to match JD language.

**What projects.txt looks like:**
```
github.com/yourname/fastapi-auth-service — JWT auth microservice in Python
github.com/yourname/ml-pipeline — end to end ML training pipeline with Airflow
yourportfolio.com/projects/dashboard — real-time analytics dashboard in React
github.com/yourname/cli-tool — developer CLI tool in Go
```

**What it returns:**
```json
[
  {
    "name": "fastapi-auth-service",
    "link": "github.com/yourname/fastapi-auth-service",
    "description": "Built a production JWT authentication microservice handling 50k+ requests/day"
  }
]
```

---

## FastAPI Backend

**File:** `backend/main.py`

Two endpoints only. Keep it clean.

### `POST /analyze`

Takes the JD text. Runs Agent 1 and Agent 2 in parallel using `asyncio.gather()`.
Returns the keyword list and the gap report. Used to show a preview before generating.

**Request:**
```json
{ "jd_text": "We are looking for a backend engineer..." }
```

**Response:**
```json
{
  "keywords": { ...Agent 1 output... },
  "gaps": { ...Agent 2 output... }
}
```

### `POST /generate`

Takes the JD text. Runs all four agents (1+4 in parallel, then 2, then 3).
Returns the new LaTeX string.

**Request:**
```json
{ "jd_text": "We are looking for a backend engineer..." }
```

**Response:**
```json
{
  "latex": "\\documentclass...",
  "projects_selected": [ ...Agent 4 output... ]
}
```

### Agent execution order in `/generate`

```
Step 1 (parallel):  Agent 1 (JD keywords)  +  Agent 4 (project selection)
Step 2:             Agent 2 (comparator — needs Agent 1 output)
Step 3:             Agent 3 (LaTeX writer — needs Agent 2 + Agent 4 output)
```

Running Step 1 in parallel saves 3–5 seconds per generation.

---

## Streamlit Frontend

**File:** `frontend/app.py`

Keep the UI fast and minimal. One screen, no navigation needed.

### Layout

```
─────────────────────────────────────────────────────────
  ATS Resume Builder
─────────────────────────────────────────────────────────

  [ Paste Job Description here                         ]
  [                                                     ]
  [                                                     ]

  [ Analyze JD ]          [ Generate Resume ]

─────────────────────────────────────────────────────────
  ↓ Keywords found    ↓ Gaps in your resume
  Python ✓            Docker ✗
  FastAPI ✓           Kubernetes ✗

─────────────────────────────────────────────────────────
  ↓ New Resume LaTeX (copy this)

  \documentclass[letterpaper,11pt]{article}
  ...
  [ Copy to clipboard ]

─────────────────────────────────────────────────────────
```

### Streamlit implementation notes

- Use `st.text_area()` for JD input — big, easy to paste into
- Use `st.spinner("Analyzing JD...")` and `st.spinner("Generating resume...")` during API calls
- Show keywords as `st.success()` chips and missing ones as `st.warning()` chips
- Show the LaTeX in `st.code(language="latex")` — syntax highlighted, easy to copy
- Use `st.session_state` to hold the last generated LaTeX so it doesn't vanish on re-render
- Call the FastAPI backend with `httpx` (async) or plain `requests`
- Two buttons: **Analyze** (just shows keywords + gaps, fast) and **Generate** (full pipeline, ~10–15s)

---

## Gemini Client

**File:** `backend/utils/gemini_client.py`

One function, used by all agents. Takes a prompt string, returns the response text.
All four agents call this same function — no duplicated API logic anywhere.

Uses `google-generativeai` Python SDK. Model: `gemini-1.5-flash` (fast and cheap for this task).

Set temperature to `0.3` — low enough to be consistent, not so low it gets robotic.

---

## File Reader Utility

**File:** `backend/utils/file_reader.py`

Two functions:
- `read_base_resume()` — reads `data/base_resume.tex`, returns raw string
- `read_projects()` — reads `data/projects.txt`, returns list of lines

Both resolve paths relative to the project root so it works from any working directory.

---

## Environment Setup

**.env file:**
```
GEMINI_API_KEY=your_key_here
```

**requirements.txt:**
```
fastapi
uvicorn
google-generativeai
python-dotenv
streamlit
httpx
```

---

## Build Order — Step by Step

Follow this order exactly. Each step is testable before moving to the next.

### Step 1 — Project scaffold
Create all folders and empty files. Copy your base resume into `data/base_resume.tex`.
Add your GitHub and portfolio links to `data/projects.txt`.

### Step 2 — Gemini client
Write `gemini_client.py`. Test it with a simple "say hello" prompt.
If this works, everything else will work.

### Step 3 — File reader utility
Write `file_reader.py`. Print both files in a test script to confirm paths resolve correctly.

### Step 4 — Agent 1 (JD extractor)
Write the agent. Test it by pasting a sample JD and printing the JSON output.
Iterate the prompt until the JSON is clean and consistent.

### Step 5 — Agent 4 (project selector)
Write the agent. Test it with the same sample JD.
Check that the project descriptions sound natural and relevant.

### Step 6 — Agent 2 (resume comparator)
Write the LaTeX → plain text stripper first (regex-based, simple).
Then write the comparison prompt. Test and check the gap report makes sense.

### Step 7 — Agent 3 (LaTeX writer)
This one takes the most prompt iteration. Start with a simple JD and check:
- Is the LaTeX valid (does it compile)?
- Are all original sections present?
- Are keywords woven in naturally?
- Does it feel like one page of content?
Iterate the prompt until all four checks pass.

### Step 8 — FastAPI main.py
Wire all four agents into the two endpoints.
Test with curl or the FastAPI `/docs` page before touching the frontend.

### Step 9 — Streamlit frontend
Build the UI. Connect to FastAPI. Test the full end-to-end flow.

### Step 10 — Polish
- Add a loading message that explains what's happening ("Analyzing JD keywords...", "Comparing with your resume...", "Writing new LaTeX...")
- Add a small section showing which projects were selected and why
- Make the copy button actually copy to clipboard using `st.components.v1.html`

---

## Things to Watch Out For

**Agent 3 prompt discipline** — this is where most of the iteration will happen.
The model needs to understand it's editing, not rewriting. Add a line to the prompt like:
*"Treat the base LaTeX as sacred. You are a copy editor, not an author."*

**LaTeX parsing** — when extracting the output from Gemini's response, always use the
`%%% RESUME BEGIN %%%` / `%%% RESUME END %%%` markers. Never try to parse LaTeX by finding
`\documentclass` — Gemini sometimes adds explanation text before it.

**One page enforcement** — Gemini can't actually measure a compiled PDF page.
The prompt approach (asking it to keep content to X bullet points per section) is the
practical way to handle this. Set strict limits in the prompt: max 3 bullets per experience,
max 8 skills, max 2 projects.

**Gemini rate limits** — if you're testing rapidly, add a small `asyncio.sleep(1)` between
agent calls to avoid hitting the free tier limits.

---

## What "Human Written Code" Means Here

- No over-engineered abstractions. Each agent is just a function that calls Gemini with a prompt.
- No unnecessary classes. Functions are fine.
- Comments explain *why*, not *what*.
- Variable names are readable (`jd_keywords`, not `kws` or `extracted_data_dict`).
- Prompts are written as multi-line strings with clear structure — not one-liner messes.
- Error handling is simple — catch exceptions, return a readable message, don't crash silently.

---

## Ready to Start

Once you share your base LaTeX resume, the actual code generation starts.
The first files to generate will be `gemini_client.py` and `file_reader.py` —
both small, both testable immediately.