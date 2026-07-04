"""Generate the synthetic evaluation dataset and save it as JSON.

Usage: PYTHONPATH=. python tools/generate_eval_dataset.py [n] [seed]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from studyguard.evaluation.pipeline import generate_dataset

_OUT = Path(__file__).resolve().parents[1] / "datasets" / "evaluation" / "synthetic"


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    _OUT.mkdir(parents=True, exist_ok=True)
    dataset = generate_dataset(n, seed)
    path = _OUT / "dataset.json"
    path.write_text(json.dumps(dataset), encoding="utf-8")
    print(f"wrote {path} ({len(dataset)} samples, seed={seed})")


if __name__ == "__main__":
    main()
