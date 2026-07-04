"""Run the evaluation pipeline and write a results report (real numbers).

Usage: PYTHONPATH=. python tools/run_evaluation.py
Reads datasets/evaluation/synthetic/dataset.json if present, else generates it.
Writes docs/reports/EVALUATION_RESULTS.md and .json.
"""
from __future__ import annotations

import json
from pathlib import Path

from studyguard.evaluation.pipeline import evaluate, generate_dataset

_ROOT = Path(__file__).resolve().parents[1]
_DATA = _ROOT / "datasets" / "evaluation" / "synthetic" / "dataset.json"
_OUT = _ROOT / "docs" / "reports"


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _load_or_generate() -> list[dict]:
    if _DATA.exists():
        return json.loads(_DATA.read_text(encoding="utf-8"))
    return generate_dataset(2000, 7)


def _markdown(report: dict) -> str:
    posture = report["posture_detection"]
    focus = report["focus_detection"]
    lines = [
        "# Model Evaluation Results",
        "",
        "> **Self-evaluation on a synthetic geometry dataset with noise** — it measures",
        "> how well the posture/focus decision logic recovers the latent study state.",
        "> These are **not** human-validated accuracy numbers. To produce those, label",
        "> real clips with `tools/label_clip.py` and re-run this script.",
        "",
        f"Samples: {report['n']} (present: {report['n_present']}).",
        "",
        "## Posture detection (poor-posture class)",
        f"- Precision: {_pct(posture['precision'])}",
        f"- Recall: {_pct(posture['recall'])}",
        f"- F1: {_pct(posture['f1'])}",
        "",
        "## Focus detection (distracted class)",
        f"- Precision: {_pct(focus['precision'])}",
        f"- Recall: {_pct(focus['recall'])}",
        f"- F1: {_pct(focus['f1'])}",
        f"- ROC AUC: {report['focus_roc_auc']}",
        "",
        "## Status classification (macro)",
        f"- Precision: {_pct(report['status']['macro']['precision'])}",
        f"- Recall: {_pct(report['status']['macro']['recall'])}",
        f"- F1: {_pct(report['status']['macro']['f1'])}",
        "",
        "### Confusion matrix (rows = true, cols = predicted)",
        "",
        "| | " + " | ".join(report["status"]["labels"]) + " |",
        "| --- " + "| --- " * len(report["status"]["labels"]) + "|",
    ]
    for label, row in zip(report["status"]["labels"], report["status"]["confusion"], strict=True):
        lines.append(f"| **{label}** | " + " | ".join(str(v) for v in row) + " |")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    report = evaluate(_load_or_generate())
    (_OUT / "EVALUATION_RESULTS.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (_OUT / "EVALUATION_RESULTS.md").write_text(_markdown(report), encoding="utf-8")
    print(json.dumps({
        "posture": report["posture_detection"],
        "focus": report["focus_detection"],
        "focus_roc_auc": report["focus_roc_auc"],
        "status_macro": report["status"]["macro"],
    }, indent=2))


if __name__ == "__main__":
    main()
