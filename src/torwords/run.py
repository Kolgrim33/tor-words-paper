"""Run the study: infer attributes on original and rewritten text for each model, then score.

Usage: uv run python -m torwords.run --models M1,M2,M3 --n 100 [--dry-run]
"""

import argparse
import datetime
import json
import os
from pathlib import Path

from torwords.data import Profile, load_profiles
from torwords.infer import infer
from torwords.llm import LLM, LLMError
from torwords.rewrite import meaning_score, rewrite
from torwords.score import FREE_TEXT, country_match, make_llm_judge, score

ROOT = Path(__file__).resolve().parents[2]


def planned_requests(profiles: list[Profile], n_models: int, meaning_sample: int = 30) -> int:
    rows = len(profiles) * n_models * 2
    judged = sum(len(FREE_TEXT & set(p.labelled)) for p in profiles) * n_models * 2
    return rows + len(profiles) + judged + min(meaning_sample, len(profiles))


def _score_row(profile: Profile, guess: dict, judge) -> dict[str, bool | None]:
    correct = {}
    for attr in profile.labelled:
        try:
            correct[attr] = score(attr, guess.get(attr), profile.truth[attr], judge)
        except LLMError:
            correct[attr] = None  # judge failed: excluded from accuracy
    return correct


def run(llm, models: list[str], profiles: list[Profile], out_dir: Path, meaning_sample: int = 30) -> dict:
    raw = Path(out_dir) / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    judge = make_llm_judge(llm, models[0])
    errors = 0

    rewrites = []
    for i, p in enumerate(profiles):
        try:
            text = rewrite(llm, models[0], p.text)
            err = None
        except LLMError as e:
            text, err = None, str(e)
            errors += 1
        meaning = None
        if text and i < meaning_sample:
            try:
                meaning = meaning_score(llm, models[0], p.text, text)
            except LLMError:
                pass
        rewrites.append({"author": p.author, "text": text, "meaning": meaning, "error": err})
    by_author = {w["author"]: w["text"] for w in rewrites}

    with (raw / "predictions.jsonl").open("w") as f:
        for model in models:
            for p in profiles:
                for condition in ("original", "rewritten"):
                    text = p.text if condition == "original" else by_author[p.author]
                    error = None
                    if text is None:
                        guess, error = {}, "rewrite failed"
                    else:
                        try:
                            guess = infer(llm, model, p, text=text)
                        except LLMError as e:
                            guess, error = {}, str(e)
                    if error:
                        errors += 1
                        correct = dict.fromkeys(p.labelled, False)
                    else:
                        correct = _score_row(p, guess, judge)
                    row = {
                        "author": p.author,
                        "model": model,
                        "condition": condition,
                        "guess": guess,
                        "truth": {a: p.truth[a] for a in p.labelled},
                        "correct": correct,
                        "country_correct": country_match(guess.get("city_country"), p.truth["city_country"])
                        if "city_country" in p.labelled
                        else None,
                        "error": error,
                    }
                    f.write(json.dumps(row) + "\n")

    with (raw / "rewrites.jsonl").open("w") as f:
        for w in rewrites:
            f.write(json.dumps(w) + "\n")
    meta = {
        "models": models,
        "rewrite_and_judge_model": models[0],
        "n": len(profiles),
        "date": datetime.date.today().isoformat(),
        "live_requests": llm.live_calls,
        "errors": errors,
    }
    (Path(out_dir) / "run_meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def load_env(path: Path) -> None:
    """Load KEY=VALUE lines from a gitignored .env without overriding the real environment."""
    if path.exists():
        for line in path.read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep and k.strip() and not line.lstrip().startswith("#"):
                os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    load_env(ROOT / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--meaning-sample", type=int, default=30)
    ap.add_argument("--out", type=Path, default=ROOT / "results")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache-only", action="store_true", help="use saved answers only; send no requests")
    args = ap.parse_args()
    models = args.models.split(",")
    profiles = load_profiles(ROOT / "data" / "raw" / "synthpai.jsonl", n=args.n)
    print(f"profiles={len(profiles)} models={models} planned_requests={planned_requests(profiles, len(models), args.meaning_sample)}")
    if args.dry_run:
        return
    llm = LLM(args.out / "cache" / "calls.jsonl", cache_only=args.cache_only)
    print(json.dumps(run(llm, models, profiles, args.out, args.meaning_sample), indent=2))


if __name__ == "__main__":
    main()
