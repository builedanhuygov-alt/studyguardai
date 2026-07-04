"""Per-metric accuracy gates for the eval clip (ADR-4).

Acceptance: posture band-accuracy >= 70%, focus band-accuracy >= 65%.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from studyguard.core import Aggregator, Detector
from studyguard.eval import EvalReport

POSTURE_MIN_ACCURACY = 0.70
FOCUS_MIN_ACCURACY = 0.65


def band(value: float) -> str:
    """Map a 0-100 score to a coarse label used for evaluation."""
    if value >= 70.0:
        return "good"
    if value >= 50.0:
        return "fair"
    return "poor"


def evaluate_metric(
    frames: Sequence[np.ndarray],
    expected_bands: Sequence[str],
    key: str,
    detector: Detector,
    aggregator: Aggregator,
) -> EvalReport:
    """Score band-accuracy for a single metric ('posture' or 'focus')."""
    if key not in ("posture", "focus"):
        raise ValueError("key must be 'posture' or 'focus'")
    if len(frames) != len(expected_bands):
        raise ValueError("frames and expected_bands must have equal length")
    correct = 0
    for index, (frame, expected) in enumerate(zip(frames, expected_bands)):
        snapshot = aggregator.build(
            [detector.analyze(frame)], frame_index=index, fps=0.0, elapsed_s=0.0, distractions=0
        )
        value = snapshot.posture if key == "posture" else snapshot.focus
        if band(value) == expected:
            correct += 1
    return EvalReport(total=len(frames), correct=correct)


def passes_gates(posture: EvalReport, focus: EvalReport) -> bool:
    """True if both per-metric accuracy gates are met."""
    return posture.accuracy >= POSTURE_MIN_ACCURACY and focus.accuracy >= FOCUS_MIN_ACCURACY
