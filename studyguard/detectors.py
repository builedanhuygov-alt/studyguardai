"""Detectors: register with ``@register_detector``; each is STATELESS and returns
an immutable ``Analysis``.

The posture/focus math lives in :mod:`studyguard.heuristics` so it can be tuned
and unit-tested without a camera (separation of CV from business rules).
"""
from __future__ import annotations

import cv2
import numpy as np

from studyguard.core import Analysis, register_detector
from studyguard.heuristics import PostureFocusConfig, score_focus, score_posture

_HAAR_FILE = "haarcascade_frontalface_default.xml"


@register_detector
class PostureFocusDetector:
    """Face-based posture + focus using OpenCV's bundled Haar cascade.

    Stateless: holds only the cascade model and an immutable tuning config.
    """

    name = "study"

    def __init__(self, config: PostureFocusConfig | None = None) -> None:
        self._config = config or PostureFocusConfig()
        self._face = cv2.CascadeClassifier(cv2.data.haarcascades + _HAAR_FILE)

    def _largest_face(self, gray: np.ndarray):
        faces = self._face.detectMultiScale(
            gray,
            scaleFactor=self._config.detection_scale_factor,
            minNeighbors=self._config.detection_min_neighbors,
            minSize=(self._config.detection_min_size, self._config.detection_min_size),
        )
        if len(faces) == 0:
            return None
        return max(faces, key=lambda box: int(box[2]) * int(box[3]))

    def analyze(self, frame: np.ndarray) -> Analysis:
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = self._largest_face(gray)
        if face is None:
            return Analysis(
                name=self.name,
                present=False,
                metrics={"posture": self._config.absent_posture, "focus": self._config.absent_focus},
            )
        x, y, fw, fh = (int(value) for value in face)
        center_x = (x + fw / 2) / width
        center_y = (y + fh / 2) / height
        face_ratio = fh / height
        return Analysis(
            name=self.name,
            present=True,
            metrics={
                "posture": score_posture(center_y, face_ratio, self._config),
                "focus": score_focus(center_x, self._config),
            },
            face_box=(x, y, fw, fh),
        )


class FakeDetector:
    """Deterministic detector for headless runs, demos, and tests (not registered)."""

    name = "study"

    def __init__(self, posture: float = 80.0, focus: float = 90.0, present: bool = True) -> None:
        self._posture = posture
        self._focus = focus
        self._present = present

    def analyze(self, frame: np.ndarray) -> Analysis:
        return Analysis(
            name=self.name,
            present=self._present,
            metrics={"posture": self._posture, "focus": self._focus},
        )
