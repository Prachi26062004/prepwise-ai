from resumes.analysis import SOFT_SKILLS, TECH_SKILLS, find_terms


def match(resume_text: str, job_text: str) -> dict:
    wanted = set(find_terms(job_text, TECH_SKILLS + SOFT_SKILLS))
    have = set(find_terms(resume_text, TECH_SKILLS + SOFT_SKILLS))
    matched, missing = sorted(wanted & have), sorted(wanted - have)
    score = round(100 * len(matched) / len(wanted)) if wanted else 0
    return {"score": score, "matching_skills": matched, "missing_skills": missing,
            "advice": [f"If you have genuine experience with {s}, show it on your resume; otherwise consider learning it."
                       for s in missing],
            "disclaimer": "Estimated keyword overlap, not a hiring prediction."}