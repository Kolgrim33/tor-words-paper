"""Load SynthPAI and build one text sample per synthetic author."""

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from torwords.normalize import education_level, relationship

ATTRIBUTES = [
    "age",
    "sex",
    "city_country",
    "birth_city_country",
    "education",
    "occupation",
    "income_level",
    "relationship_status",
]


@dataclass
class Profile:
    author: str
    text: str
    truth: dict[str, str | int]
    labelled: list[str]


def _truth(profile: dict) -> dict[str, str | int]:
    t = {a: profile[a] for a in ATTRIBUTES}
    t["education"] = education_level(profile["education"])
    t["relationship_status"] = relationship(profile["relationship_status"])
    return t


def load_profiles(path: Path, n: int = 100, seed: int = 2026, max_chars: int = 3000) -> list[Profile]:
    comments: dict[str, list[str]] = defaultdict(list)
    labelled: dict[str, set[str]] = defaultdict(set)
    profiles: dict[str, dict] = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            author = r["author"]
            comments[author].append(r["text"])
            profiles[author] = r["profile"]
            for attr in ATTRIBUTES:
                if r["reviews"]["human"][attr]["hardness"] > 0:
                    labelled[author].add(attr)
    eligible = sorted(a for a in profiles if labelled[a])
    chosen = random.Random(seed).sample(eligible, min(n, len(eligible)))
    return [
        Profile(
            author=a,
            text="\n\n".join(comments[a])[:max_chars],
            truth=_truth(profiles[a]),
            labelled=[x for x in ATTRIBUTES if x in labelled[a]],
        )
        for a in chosen
    ]
