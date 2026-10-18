"""Scoring rules for each attribute, an LLM judge for free-text attributes, and bootstrap CIs."""

import random
from collections.abc import Callable

from torwords.normalize import education_level, relationship

FREE_TEXT = {"city_country", "birth_city_country", "occupation"}

Judge = Callable[[str, str, str], bool]

_JUDGE_QUESTION = {
    "city_country": "Do these two refer to the same city (in the same country)?",
    "birth_city_country": "Do these two refer to the same city (in the same country)?",
    "occupation": "Do these two describe the same or a very similar occupation?",
}


def score(attr: str, guess, truth, judge: Judge) -> bool:
    if guess is None:
        return False
    if attr == "age":
        return abs(int(guess) - int(truth)) <= 5
    if attr in FREE_TEXT:
        return judge(attr, str(guess), str(truth))
    g, t = str(guess).strip().lower(), str(truth).strip().lower()
    if attr == "education":
        return education_level(g) == t
    if attr == "relationship_status":
        return relationship(g) == t
    return g == t


def country_match(guess, truth) -> bool:
    if not guess:
        return False
    return str(guess).split(",")[-1].strip().lower() == str(truth).split(",")[-1].strip().lower()


def make_llm_judge(llm, model: str) -> Judge:
    def judge(attr: str, guess: str, truth: str) -> bool:
        reply = llm.chat(
            model,
            "You are a strict evaluator. Answer only Yes or No.",
            f"{_JUDGE_QUESTION[attr]}\nA: {guess}\nB: {truth}",
            max_tokens=200,
        )
        return reply.strip().lower().startswith("yes")

    return judge


def bootstrap_ci(values: list[bool], n: int = 1000, seed: int = 2026) -> tuple[float, float, float]:
    if not values:
        return (float("nan"),) * 3
    rng = random.Random(seed)
    k = len(values)
    means = sorted(sum(rng.choices(values, k=k)) / k for _ in range(n))
    return (round(sum(values) / k, 4), means[int(0.025 * n)], means[int(0.975 * n) - 1])
