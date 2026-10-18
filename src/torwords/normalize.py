"""Normalize free-text SynthPAI labels and model guesses to comparable values."""

EDUCATION_LEVELS = ("high school", "bachelors", "masters", "phd", "other")
RELATIONSHIPS = ("single", "in a relationship", "engaged", "married", "divorced", "widowed")


def education_level(s: str) -> str:
    t = s.lower().replace("'", "").replace("’", "")
    if "phd" in t or "doctor" in t:
        return "phd"
    if "master" in t or "mba" in t:
        return "masters"
    if "bachelor" in t or "undergrad" in t:
        return "bachelors"
    if "high school" in t or "secondary" in t:
        return "high school"
    return "other"


def relationship(s: str) -> str:
    t = s.lower().strip()
    if "relationship" in t:
        return "in a relationship"
    return t
