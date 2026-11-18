"""Bullet Proof Score: does each resume bullet carry evidence?"""
import re

VERBS = {"built", "designed", "led", "created", "developed", "implemented", "reduced", "increased",
         "improved", "launched", "automated", "optimized", "migrated", "delivered", "analyzed", "mentored"}
OUTCOME = re.compile(r"\b(reduced|increased|improved|saved|grew|cut|boosted|achieved|delivered|enabled)\b", re.I)
WEAK = re.compile(r"\b(responsible for|worked on|helped with|duties included|assisted)\b", re.I)


def score_bullet(bullet: str) -> dict:
    text = bullet.strip(" •-*\t")
    first = text.split()[0].lower() if text.split() else ""
    has_verb, has_metric = first in VERBS, bool(re.search(r"\d", text))
    has_outcome, weak = bool(OUTCOME.search(text)), bool(WEAK.search(text))
    score = 30 * has_verb + 40 * has_metric + 30 * has_outcome - 20 * weak
    tips = []
    if not has_verb:
        tips.append("Start with a strong action verb (built, led, reduced...).")
    if not has_metric:
        tips.append("If you can measure this honestly, add the real figure. Do not invent one.")
    if weak:
        tips.append("Replace vague phrases like 'responsible for' with what you actually did.")
    return {"bullet": text, "score": max(0, min(score, 100)), "tips": tips}


def analyze_bullets(resume_text: str) -> list:
    lines = [ln for ln in resume_text.splitlines() if len(ln.split()) >= 4]
    return sorted((score_bullet(ln) for ln in lines), key=lambda b: b["score"])[:15]