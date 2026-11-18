"""Rule-based check of how specific an answer is. Measures detail, not who wrote it."""
import re

ACTIONS = r"\bI (built|wrote|fixed|used|set up|designed|debugged|deployed|chose|tested|created|implemented|configured|decided|learned|measured)\b"
REASONING = r"\b(because|so that|instead of|trade-?off|however|but|which meant|the reason)\b"


def specificity(answer: str) -> int:
    """Score 0-100 from length, numbers, first-person actions and reasoning words."""
    words = len(answer.split())
    numbers = len(re.findall(r"\d+", answer))
    actions = len(re.findall(ACTIONS, answer, re.I))
    reasons = len(re.findall(REASONING, answer, re.I))
    return round(min(words / 60, 1) * 40 + min(numbers, 2) * 10 + min(actions, 2) * 10 + min(reasons, 2) * 10)


def verdict_for(score: int) -> str:
    return "defended" if score >= 65 else "shaky" if score >= 35 else "unsupported"