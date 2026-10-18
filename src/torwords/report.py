"""Build tables, the figure and summary.json from results/raw.

Usage: uv run python -m torwords.report
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from torwords.data import ATTRIBUTES  # noqa: E402
from torwords.score import bootstrap_ci  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REPORT_ATTRS = ATTRIBUTES[:3] + ["country"] + ATTRIBUTES[3:]

# What a network observer learns from the IP address alone (cited background, not measured).
NETWORK = {
    "country": ("yes (IP geolocation)", "none"),
    "city_country": ("often (IP geolocation, city level is unreliable)", "none"),
}


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def build_report(results: Path) -> dict:
    preds = _read(results / "raw" / "predictions.jsonl")
    rewrites = _read(results / "raw" / "rewrites.jsonl")
    models = json.loads((results / "run_meta.json").read_text())["models"]

    cells: dict[tuple[str, str, str], list[bool]] = defaultdict(list)
    for r in preds:
        if r["error"]:
            continue  # request failed (quota, network): no answer to score
        for attr, ok in r["correct"].items():
            if ok is not None:
                cells[(attr, r["model"], r["condition"])].append(ok)
        if r["country_correct"] is not None:
            cells[("country", r["model"], r["condition"])].append(r["country_correct"])

    table = []
    for attr in REPORT_ATTRS:
        for model in models:
            for condition in ("original", "rewritten"):
                vals = cells.get((attr, model, condition), [])
                if not vals:
                    continue
                acc, lo, hi = bootstrap_ci(vals)
                table.append({"attr": attr, "model": model, "condition": condition, "n": len(vals),
                              "acc": round(acc, 4), "lo": round(lo, 4), "hi": round(hi, 4)})
    with (results / "table_accuracy.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["attr", "model", "condition", "n", "acc", "lo", "hi"])
        w.writeheader()
        w.writerows(table)

    def best(condition: str) -> dict:
        out = {}
        for attr in REPORT_ATTRS:
            rows = [t for t in table if t["attr"] == attr and t["condition"] == condition]
            if rows:
                top = max(rows, key=lambda t: t["acc"])
                out[attr] = {"model": top["model"], "acc": top["acc"], "lo": top["lo"], "hi": top["hi"], "n": top["n"]}
        return out

    best_orig, best_rew = best("original"), best("rewritten")
    with (results / "table_network_vs_text.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["attr", "network_no_tor", "network_tor", "best_text_acc", "best_text_acc_rewritten"])
        w.writeheader()
        for attr in REPORT_ATTRS:
            if attr not in best_orig:
                continue
            no_tor, tor = NETWORK.get(attr, ("none", "none"))
            w.writerow({"attr": attr, "network_no_tor": no_tor, "network_tor": tor,
                        "best_text_acc": best_orig[attr]["acc"],
                        "best_text_acc_rewritten": best_rew.get(attr, {}).get("acc", "")})

    meanings = [w["meaning"] for w in rewrites if w["meaning"] is not None]
    summary = {
        "models": models,
        "n_profiles": len({r["author"] for r in preds}),
        "n_predictions": len(preds),
        "n_errors": sum(1 for r in preds if r["error"]),
        "best_original": best_orig,
        "best_rewritten": best_rew,
        "mean_meaning": round(sum(meanings) / len(meanings), 2) if meanings else None,
        "n_meaning": len(meanings),
    }
    (results / "summary.json").write_text(json.dumps(summary, indent=2))
    _figure(table, models, results / "fig_accuracy.png")
    return summary


def _figure(table: list[dict], models: list[str], path: Path) -> None:
    attrs = [a for a in REPORT_ATTRS if any(t["attr"] == a for t in table)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    width = 0.8 / max(len(models), 1)
    for ax, condition in zip(axes, ("original", "rewritten")):
        for i, model in enumerate(models):
            xs, accs, err = [], [], [[], []]
            for j, attr in enumerate(attrs):
                t = next((t for t in table if t["attr"] == attr and t["model"] == model and t["condition"] == condition), None)
                if t:
                    xs.append(j + i * width)
                    accs.append(t["acc"])
                    err[0].append(t["acc"] - t["lo"])
                    err[1].append(t["hi"] - t["acc"])
            ax.bar(xs, accs, width, yerr=err, capsize=2, label=model.split("/")[-1])
        ax.set_xticks([j + width * (len(models) - 1) / 2 for j in range(len(attrs))])
        ax.set_xticklabels([a.replace("_", " ") for a in attrs], rotation=40, ha="right", fontsize=8)
        ax.set_title(f"{condition} text")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("accuracy")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    print(json.dumps(build_report(ROOT / "results"), indent=2))
