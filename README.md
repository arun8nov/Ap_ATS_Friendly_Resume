# 📄 AP ATS Friendly Resume Optimizer

An AI-powered resume optimizer that reads your Job Description and automatically tailors your LaTeX resume to pass ATS (Applicant Tracking System) filters — in under 2 minutes.

---

## 🚀 The Problem This Solves

Every job application requires a different resume. Manually editing keywords, updating project descriptions, and changing the job title in Overleaf takes **20+ minutes per application**.

This tool does it automatically — paste a JD, get an ATS-optimized `.tex` file ready to compile in Overleaf.

---

## ⚙️ How It Works

```
Paste JD
   ↓
Agent 1 — Keyword Analyzer
Reads all your resume versions, compares against JD
Finds matched keywords, missing keywords, ATS score
   ↓
Agent 3 — Resume Assembler
Picks the best matching resume from your collection
Assembles the strongest content based on JD
   ↓
Agent 2 — ATS Polisher
Adds missing keywords naturally
Updates job title to match JD
Ensures single page, ATS parsable output
   ↓
Download optimized .tex file
Paste into Overleaf → Compile → Apply
```

---

## 📁 Project Structure

```
project/
├── resumes/                  ← Your .tex resume versions go here
│   ├── data_analyst.tex
│   ├── data_science.tex
│   ├── ai_engineer.tex
│   └── mis_analyst.tex
├── app.py                    ← Streamlit web app
├── agents.py                 ← AI agent logic
├── RESUME_RULES.md           ← Resume writing rules followed by agents
├── main.tex                  ← Your master resume (not modified)
├── .env                      ← API key (never commit this)
├── requirements.txt
└── pyproject.toml
```

---

## 🛠️ Setup

### 1. Clone the repo
```powershell
git clone https://github.com/arun8nov/Ap_ATS_Friendly_Resume.git
cd Ap_ATS_Friendly_Resume
```

### 2. Install uv (if not installed)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install dependencies
```powershell
uv sync
```

### 4. Add your API key
Create a `.env` file:
```
NVIDIA_API_KEY=your_api_key_here
```
Get a free API key at: https://build.nvidia.com

### 5. Add your resumes
Place your `.tex` resume files inside the `resumes/` folder or upload in the app.
Each file should be a different version of your resume for different roles.

### 6. Run the app
```powershell
streamlit run app.py
```

---

## 🤖 The 3 Agents

| Agent | Job |
|-------|-----|
| **Agent 1** — Keyword Analyzer | Compares JD vs all your resumes. Returns ATS match score, matched keywords, missing keywords, and recommendations. |
| **Agent 3** — Resume Assembler | Reads all resume versions, picks the best matching one, assembles strongest content for the JD. |
| **Agent 2** — ATS Polisher | Final pass — adds missing keywords, updates title, ensures one page, ATS parsable LaTeX output. |

---

## 📋 How To Use

1. Open the app in browser
2. Paste the full Job Description in the text area
3. Choose resume source:
   - **Auto-assemble** — AI picks best content from all your resumes
   - **Single resume** — Use one specific resume as base
4. Click **Analyze & Build Resume**
5. Wait for all 3 agents to complete
6. Download the optimized `.tex` file
7. Paste into [Overleaf](https://overleaf.com) → Compile → Download PDF → Apply

---

## 💡 Tips for Best Results

- Paste the **complete** JD — include responsibilities, requirements, and skills sections
- Keep your resume versions **role-specific** — one for Data Analyst, one for Data Scientist, etc.
- All resumes in `resumes/` folder must be **your own** — do not mix resumes from different people
- The more detailed your resume versions, the better the output

---

## 🔒 Important Notes

- Your `.env` file is in `.gitignore` — API key is never pushed to GitHub
- `main.tex` is your master file — the app never overwrites it
- Resumes in `resumes/` folder should all belong to the same person

---

## 📦 Dependencies

- `streamlit` — Web UI
- `openai` — NVIDIA API client
- `python-dotenv` — Environment variables

---

## 📬 Author

**Arunprakash B**  
[GitHub](https://github.com/arun8nov)