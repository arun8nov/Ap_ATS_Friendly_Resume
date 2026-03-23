from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def read_base_resume() -> str:
    resume_path = BASE_DIR / "data" / "base_resume.tex"
    if not resume_path.exists():
        return ""
    with open(resume_path, "r", encoding="utf-8") as f:
        return f.read()

def read_projects() -> list[str]:
    projects_path = BASE_DIR / "data" / "projects.txt"
    if not projects_path.exists():
        return []
    with open(projects_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
