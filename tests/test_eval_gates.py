import numpy as np

from studyguard.core import Aggregator
from studyguard.detectors import PostureFocusDetector
from studyguard.eval_gates import evaluate_metric, passes_gates


def test_metric_gates_on_blank_frames():
    frames = [np.zeros((240, 320, 3), dtype=np.uint8) for _ in range(5)]
    # No face => posture holds the neutral 60 ("fair") and focus 0 ("poor").
    posture = evaluate_metric(frames, ["fair"] * 5, "posture", PostureFocusDetector(), Aggregator())
    focus = evaluate_metric(frames, ["poor"] * 5, "focus", PostureFocusDetector(), Aggregator())
    assert posture.accuracy == 1.0 and focus.accuracy == 1.0
    assert passes_gates(posture, focus)
