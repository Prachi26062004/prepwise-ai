"""AI layer. Falls back to simple heuristics when no AI provider is configured."""
import json
import logging
from contextvars import ContextVar

from django.conf import settings

log = logging.getLogger(__name__)
LAST_USAGE: ContextVar = ContextVar("last_usage", default=None)
BANK = {
    "technical": ["Explain how {s} works and where you have used it.", "What trade-offs did you face using {s}?"],
    "behavioral": ["Tell me about a time you resolved a team conflict.", "Describe a deadline you nearly missed."],
    "hr": ["Why do you want the {role} role?", "Where do you see yourself in 3 years?"],
}


class AIError(RuntimeError):
    pass


def _complete(prompt: str) -> dict:
    """Call the configured provider (Gemini or OpenAI); the reply must be a JSON object."""
    provider = settings.AI_PROVIDER
    try:
        if provider == "gemini" and settings.GEMINI_API_KEY:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            r = client.models.generate_content(
                model=settings.AI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json", "max_output_tokens": 2000},
            )
            data = json.loads(r.text)
            u = r.usage_metadata
            LAST_USAGE.set((u.prompt_token_count or 0, u.candidates_token_count or 0))
        elif provider == "openai" and settings.OPENAI_API_KEY:
            from openai import OpenAI
            r = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30).chat.completions.create(
                model=settings.AI_MODEL, max_tokens=900, response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}])
            data = json.loads(r.choices[0].message.content)
            LAST_USAGE.set((r.usage.prompt_tokens, r.usage.completion_tokens))
        else:
            raise AIError("No AI provider configured")
    except AIError:
        raise
    except Exception as exc:
        raise AIError(str(exc)) from exc
    if not isinstance(data, dict):
        raise AIError("Malformed AI response")
    return data


def generate_interview_questions(role: str, skills: list, category: str, level: str, n: int = 5) -> list:
    try:
        qs = _complete(f'Return JSON {{"questions":[str]}}: {n} {level} {category} interview questions for a {role} '
                       f"with skills {skills[:10]}.").get("questions")
        if isinstance(qs, list) and qs and all(isinstance(q, str) for q in qs):
            return qs[:n]
    except AIError:
        log.warning("AI unavailable; using template questions")
    pool = BANK.get(category, BANK["technical"])
    out = [pool[0].format(s=s, role=role) for s in skills] + [q.format(s="a recent project", role=role) for q in pool]
    return out[:n]


def evaluate_answer(question: str, answer: str) -> dict:
    try:
        d = _complete('Return JSON {"score":0-10,"feedback":str,"missing":[str]} evaluating this interview answer. '
                      f"Question: {question}\nAnswer: {answer[:2000]}")
        score = float(d["score"])
        if 0 <= score <= 10:
            return {"score": score, "feedback": str(d.get("feedback", "")), "missing": list(d.get("missing", [])),
                    "source": "ai"}
    except (AIError, KeyError, TypeError, ValueError):
        log.warning("AI evaluation failed; using heuristic")
    words = len(answer.split())
    return {"score": min(10, round(words / 15, 1)), "feedback": "Heuristic estimate based on completeness only.",
            "missing": [] if words >= 60 else ["Give more detail and a concrete example."], "source": "heuristic"}

def rewrite_bullet(bullet: str, role: str) -> dict:
    """Rewrite one resume bullet. Rejects output that adds numbers the user never wrote."""
    import re
    prompt = (
        'Return JSON {"rewrite": str}. Rewrite this resume bullet to start with a strong action verb '
        "and be clear and concise. Use ONLY facts in the original. Do NOT invent numbers, tools, "
        "results or responsibilities. Where a measurable result would help, write a placeholder like "
        f"[your real number]. Target role: {role}.\nBullet: {bullet[:400]}"
    )
    try:
        text = str(_complete(prompt).get("rewrite", "")).strip()
    except AIError:
        return {"rewrite": None, "source": "unavailable"}
    new_numbers = set(re.findall(r"\d+", re.sub(r"\[[^\]]*\]", "", text))) - set(re.findall(r"\d+", bullet))
    if not text or new_numbers or len(text) > 500:
        return {"rewrite": None, "source": "rejected"}
    return {"rewrite": text, "source": "ai"}