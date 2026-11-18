"""Resume text extraction and transparent heuristic scoring (not an ATS result)."""
import io
import re

TECH_SKILLS = ["python", "django", "flask", "java", "javascript", "typescript", "react", "node", "sql",
               "postgresql", "mongodb", "docker", "kubernetes", "aws", "git", "linux", "machine learning",
               "pandas", "numpy", "tensorflow", "rest", "api", "html", "css", "c++", "go", "redis", "celery"]
SOFT_SKILLS = ["communication", "leadership", "teamwork", "problem solving", "collaboration", "mentoring"]
SECTIONS = {"education": r"\beducation\b", "experience": r"\b(experience|employment)\b",
            "skills": r"\bskills\b", "projects": r"\bprojects?\b", "summary": r"\b(summary|objective|profile)\b"}
WEIGHTS = {"education": 20, "experience": 25, "skills": 20, "projects": 15, "summary": 5}


class ExtractionError(ValueError):
    pass


def extract_text(data: bytes, ext: str) -> str:
    ext = ext.lower().lstrip(".")
    if ext not in ("pdf", "docx"):
        raise ExtractionError("Only PDF and DOCX files are supported.")
    try:
        if ext == "pdf":
            from pypdf import PdfReader
            text = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
        else:
            import docx
            text = "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    except Exception as exc:
        raise ExtractionError("Could not read the file; it may be corrupted.") from exc
    if len(text.strip()) < 30:
        raise ExtractionError("No readable text found (scanned images are not supported).")
    return text


def find_terms(text: str, terms) -> list:
    low = text.lower()
    return sorted(t for t in terms if re.search(rf"(?<![a-z+]){re.escape(t)}(?![a-z])", low))


def analyze(text: str) -> dict:
    low = text.lower()
    present = {s for s, pat in SECTIONS.items() if re.search(pat, low)}
    tech, soft = find_terms(text, TECH_SKILLS), find_terms(text, SOFT_SKILLS)
    words = len(text.split())
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text))
    metrics = len(re.findall(r"\d+%|\$\d+|\b\d{2,}\+?\s*(users|customers|projects|requests)", low))
    length_ok = 250 <= words <= 1000
    score = sum(WEIGHTS[s] for s in present) + min(len(tech), 10) + (5 if has_email else 0) \
        + (5 if length_ok else 0) + min(metrics * 2, 10)
    missing = [f"Add a {s} section" for s in SECTIONS if s not in present]
    if not has_email:
        missing.append("Add a contact email")
    suggestions = list(missing)
    if metrics == 0:
        suggestions.append("Quantify achievements (e.g. 'reduced load time by 30%') where true.")
    if not length_ok:
        suggestions.append("Aim for roughly 250-1000 words.")
    strengths = ([f"{len(tech)} technical skills detected"] if tech else []) + [f"Has {s} section" for s in sorted(present)]
    return {"score": min(score, 100), "section_scores": {s: 100 if s in present else 0 for s in SECTIONS},
            "technical_skills": tech, "soft_skills": soft, "strengths": strengths, "weaknesses": missing,
            "suggestions": suggestions, "word_count": words,
            "disclaimer": "Heuristic estimate; not an official ATS score."}

HEADINGS = ["education", "experience", "work experience", "professional experience", "employment", "work history",
            "skills", "technical skills", "projects", "summary", "professional summary", "objective", "career objective",
            "profile", "certifications", "certificates", "achievements", "internship", "internships", "awards"]
_HEADING_RE = re.compile(r"^(" + "|".join(sorted(HEADINGS, key=len, reverse=True)) + r")\b")
MIN_RESUME_WORDS, MAX_RESUME_WORDS, MIN_SIGNALS = 80, 2500, 3


def validate_resume(text: str) -> tuple:
    """Return (is_resume, reason). Heuristic: needs enough resume-like signals; it cannot be perfect."""
    words = len(text.split())
    if words < MIN_RESUME_WORDS:
        return False, "This document is too short to be a resume."
    if words > MAX_RESUME_WORDS:
        return False, "This document is too long to be a resume. Upload your resume only."
    headings = set()
    for line in text.splitlines():
        s = line.strip().lower().strip(" :•-–|*#")
        if 0 < len(s) <= 60 and (m := _HEADING_RE.match(s)):
            headings.add(m.group(1))
    has_contact = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|(\+?\d[\d\s().-]{8,}\d)|linkedin\.com|github\.com", text, re.I))
    has_dates = len(re.findall(r"\b(19|20)\d{2}\b|\bpresent\b", text, re.I)) >= 2
    has_skills = len(find_terms(text, TECH_SKILLS + SOFT_SKILLS)) >= 3
    signals = (2 if len(headings) >= 2 else len(headings)) + has_contact + has_dates + has_skills
    if signals < MIN_SIGNALS:
        return False, ("This doesn't look like a resume. A resume usually has sections such as Education, "
                       "Experience or Skills, plus contact details and dates.")
    return True, ""