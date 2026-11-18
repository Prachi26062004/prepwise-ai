"""STAR Coach: which of Situation/Task/Action/Result does an answer cover?"""
import re

CUES = {
    "situation": r"\b(when|while|at my|during|in my|our team|project)\b",
    "task": r"\b(needed to|had to|goal|responsible|assigned|my role|challenge)\b",
    "action": r"\b(i (built|led|decided|created|wrote|implemented|organized|proposed|fixed))\b",
    "result": r"\b(result|outcome|as a result|reduced|increased|improved|learned|delivered|%)",
}


def star_check(answer: str) -> dict:
    found = {k: bool(re.search(p, answer, re.I)) for k, p in CUES.items()}
    return {"covered": found, "missing": [k for k, ok in found.items() if not ok],
            "note": "Keyword-based hint; it cannot judge answer quality."}