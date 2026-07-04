import numpy as np

from studyguard.core import Aggregator
from studyguard.detectors import PostureFocusDetector
from studyguard.eval import evaluate, meets_threshold


def test_eval_blank_frames_are_away():
    frames = [np.zeros((240, 320, 3), dtype=np.uint8) for _ in range(5)]
    expected = ["AWAY"] * 5
    report = evaluate(frames, expected, PostureFocusDetector(), Aggregator())
    assert report.accuracy == 1.0
    assert meets_threshold(report, 0.8)
