import csv
import json

from torwords.report import build_report


def row(author, model, condition, correct, country=None, error=None):
    return {"author": author, "model": model, "condition": condition, "guess": {}, "truth": {},
            "correct": correct, "country_correct": country, "error": error}


def write_fixture(d):
    raw = d / "raw"
    raw.mkdir(parents=True)
    rows = [
        row("p1", "m1", "original", {"sex": True, "city_country": True}, country=True),
        row("p2", "m1", "original", {"sex": False, "city_country": None}, country=False),
        row("p1", "m1", "rewritten", {"sex": False, "city_country": False}, country=False),
        row("p2", "m1", "rewritten", {"sex": False, "city_country": False}, country=True),
    ]
    (raw / "predictions.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    (raw / "rewrites.jsonl").write_text(json.dumps({"author": "p1", "text": "x", "meaning": 4, "error": None}) + "\n")
    (d / "run_meta.json").write_text(json.dumps({"models": ["m1"], "n": 2}))


def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def test_report_from_fixture(tmp_path):
    write_fixture(tmp_path)
    build_report(tmp_path)
    acc = {(r["attr"], r["model"], r["condition"]): r for r in read_csv(tmp_path / "table_accuracy.csv")}
    assert acc[("sex", "m1", "original")]["acc"] == "0.5"
    assert acc[("sex", "m1", "original")]["n"] == "2"
    # None (judge failure) excluded from n
    assert acc[("city_country", "m1", "original")]["n"] == "1"
    assert acc[("country", "m1", "original")]["acc"] == "0.5"
    net = {r["attr"]: r for r in read_csv(tmp_path / "table_network_vs_text.csv")}
    assert net["sex"]["network_no_tor"] == "none"
    assert net["country"]["network_no_tor"].startswith("yes")
    assert net["country"]["network_tor"] == "none"
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["mean_meaning"] == 4.0
    assert summary["best_original"]["sex"]["acc"] == 0.5
    assert (tmp_path / "fig_accuracy.png").stat().st_size > 1000


def test_failed_requests_excluded_from_accuracy(tmp_path):
    write_fixture(tmp_path)
    p = tmp_path / "raw" / "predictions.jsonl"
    extra = row("p3", "m1", "original", {"sex": False}, country=False, error="HTTP 429")
    p.write_text(p.read_text() + json.dumps(extra) + "\n")
    summary = build_report(tmp_path)
    acc = {(r["attr"], r["condition"]): r for r in read_csv(tmp_path / "table_accuracy.csv")}
    assert acc[("sex", "original")]["n"] == "2"
    assert acc[("country", "original")]["n"] == "2"
    assert summary["n_errors"] == 1
