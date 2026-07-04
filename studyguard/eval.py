"""Accuracy evaluation harness (ADR-4 quality gate).

Compare detector + aggregator output against a labeled clip. A detector must
reach its accuracy threshold on the eval clip before its milestone is Done.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from studyguard.core import Aggregator, Detector


@dataclass(frozen=True)
class EvalReport:
    total: int
    correct: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0


def evaluate(
    frames: Sequence[np.ndarray],
    expected_status: Sequence[str],
    detector: Detector,
    aggregator: Aggregator,
) -> EvalReport:
    """Run the detector over labeled frames and score status accuracy."""
    if len(frames) != len(expected_status):
        raise ValueError("frames and expected_status must have equal length")
    correct = 0
    for index, (frame, expected) in enumerate(zip(frames, expected_status)):
        snapshot = aggregator.build(
            [detector.analyze(frame)],
            frame_index=index,
            fps=0.0,
            elapsed_s=0.0,
            distractions=0,
        )
        if snapshot.status == expected:
            correct += 1
    return EvalReport(total=len(frames), correct=correct)


def load_labels(path: str) -> list[str]:
    """Load a JSON array of expected statuses for a labeled clip."""
    with open(path, encoding="utf-8") as handle:
        return list(json.load(handle))


def meets_threshold(report: EvalReport, threshold: float) -> bool:
    """Acceptance check for the milestone gate."""
    return report.accuracy >= threshold
