"""Tests for core domain objects."""

from __future__ import annotations

import numpy as np

from studyguard.core import Aggregator, Analysis
from studyguard.detectors import PostureFocusDetector


def test_detector_analyze() -> None:
    """Test that detector can analyze frames."""
    detector = PostureFocusDetector()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = detector.analyze(frame)
    assert isinstance(result, Analysis)
    assert result.name == "posture_focus"
    assert result.present is True


def test_aggregator_build() -> None:
    """Test aggregator builds snapshots."""
    aggregator = Aggregator()
    detector = PostureFocusDetector()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    analysis = detector.analyze(frame)

    snapshot = aggregator.build([analysis], frame_index=0, fps=30.0, elapsed_s=0.0, distractions=0)
    assert snapshot.frame_index == 0
    assert snapshot.posture_score > 0
    assert snapshot.focus_score > 0
