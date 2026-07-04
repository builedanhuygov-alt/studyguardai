import numpy as np

from studyguard.detectors import PostureFocusDetector


def test_blank_frame_absent():
    analysis = PostureFocusDetector().analyze(np.zeros((240, 320, 3), dtype=np.uint8))
    assert analysis.present is False
    assert analysis.metrics["focus"] == 0.0
