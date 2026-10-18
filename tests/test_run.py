import json

from torwords.data import Profile
from torwords.infer import INFER_SYSTEM
from torwords.llm import LLMError
from torwords.rewrite import JUDGE_SYSTEM, REWRITE_SYSTEM
from torwords.run import planned_requests, run


class FakeLLM:
    live_calls = 0

    def __init__(self, fail_model=None):
        self.fail_model = fail_model

    def chat(self, model, system, user, **kw):
        if model == self.fail_model and system == INFER_SYSTEM:
            raise LLMError("boom")
        if system == INFER_SYSTEM:
            return '{"sex": "male", "age": 40, "city_country": "Toronto, Canada", "occupation": "banker"}'
        if system == REWRITE_SYSTEM:
            return "rewritten: " + user
        if system == JUDGE_SYSTEM:
            return "4"
        return "Yes"


def profiles():
    truth = {"sex": "male", "age": 43, "city_country": "Montreal, Canada", "occupation": "financial manager"}
    return [Profile(f"p{i}", f"text {i}", truth, ["sex", "age", "city_country", "occupation"]) for i in range(3)]


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_end_to_end_with_fake_llm(tmp_path):
    run(FakeLLM(), ["m1", "m2"], profiles(), tmp_path, meaning_sample=2)
    rows = read(tmp_path / "raw" / "predictions.jsonl")
    assert len(rows) == 3 * 2 * 2
    assert {r["condition"] for r in rows} == {"original", "rewritten"}
    r = rows[0]
    assert r["correct"] == {"sex": True, "age": True, "city_country": True, "occupation": True}
    assert r["country_correct"] is True
    rewrites = read(tmp_path / "raw" / "rewrites.jsonl")
    assert len(rewrites) == 3 and rewrites[0]["text"].startswith("rewritten: ")
    assert [w["meaning"] for w in rewrites] == [4, 4, None]
    meta = json.loads((tmp_path / "run_meta.json").read_text())
    assert meta["models"] == ["m1", "m2"] and meta["n"] == 3


def test_model_error_recorded_and_run_continues(tmp_path):
    run(FakeLLM(fail_model="m2"), ["m1", "m2"], profiles(), tmp_path, meaning_sample=0)
    rows = read(tmp_path / "raw" / "predictions.jsonl")
    bad = [r for r in rows if r["model"] == "m2"]
    assert len(bad) == 6 and all(r["error"] for r in bad)
    assert all(v is False for r in bad for v in r["correct"].values())
    assert json.loads((tmp_path / "run_meta.json").read_text())["errors"] == 6


def test_planned_requests():
    # 3 profiles x 2 models x 2 conditions + 3 rewrites + judge (2 free-text attrs x 12 rows) + 2 meaning
    assert planned_requests(profiles(), 2, meaning_sample=2) == 12 + 3 + 24 + 2
