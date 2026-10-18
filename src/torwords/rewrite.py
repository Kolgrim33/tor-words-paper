"""'Rewrite before posting' defense and a meaning-preservation judge."""

import re

REWRITE_SYSTEM = (
    "You are a privacy assistant. Rewrite these comments so they keep their meaning and tone "
    "but remove any clue about the author's age, sex, location, birthplace, education, job, "
    "income or relationship status. Output only the rewritten comments."
)

JUDGE_SYSTEM = (
    "You compare two versions of the same online comments. Rate how well the rewritten version "
    "keeps the meaning of the original, ignoring removed personal details, from 1 (meaning lost) "
    "to 5 (meaning fully kept). Reply with a single digit."
)


def rewrite(llm, model: str, text: str) -> str:
    out = llm.chat(model, REWRITE_SYSTEM, text, max_tokens=4000).strip()
    return out or text


def meaning_score(llm, judge_model: str, original: str, rewritten: str) -> int | None:
    reply = llm.chat(judge_model, JUDGE_SYSTEM, f"Original:\n{original}\n\nRewritten:\n{rewritten}", max_tokens=200)
    m = re.search(r"\b([1-9])\b", reply)
    if not m or not 1 <= int(m.group(1)) <= 5:
        return None
    return int(m.group(1))
