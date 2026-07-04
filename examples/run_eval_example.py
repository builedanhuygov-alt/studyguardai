"""Example: run the accuracy eval harness on a tiny synthetic clip.

Real usage: capture a short webcam clip, label each sampled frame with the
expected status (see ``examples/labels.sample.json``), then feed real frames
into ``studyguard.eval.evaluate`` / ``studyguard.eval_gates``.
"""
from __future__ import annotations

import numpy as np

from studyguard.core import Aggregator
from studyguard.detectors import PostureFocusDetector
from studyguard.eval import evaluate


def main() -> None:
    # Blank frames contain no face, so the detector reports AWAY.
    frames = [np.zeros((240, 320, 3), dtype=np.uint8) for _ in range(10)]
    expected = ["AWAY"] * 10
    report = evaluate(frames, expected, PostureFocusDetector(), Aggregator())
    print(f"status accuracy on synthetic clip: {report.accuracy:.0%} ({report.correct}/{report.total})")


if __name__ == "__main__":
    main()
