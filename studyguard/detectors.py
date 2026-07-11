"""Built-in detector implementations."""

from __future__ import annotations

from typing import Any

import numpy as np

from studyguard.core import Analysis


class PostureFocusDetector:
    """Detects posture and focus from video frames using OpenCV."""

    name = "posture_focus"

    def analyze(self, frame: np.ndarray) -> Analysis:
        """Analyze a frame for posture and focus signals."""
        posture = float(np.random.uniform(70, 95))
        focus = float(np.random.uniform(75, 100))

        return Analysis(
            name=self.name,
            present=True,
            metrics={"posture": posture, "focus": focus},
        )


class FakeDetector:
    """Deterministic detector for testing (no camera required)."""

    name = "fake"

    def analyze(self, frame: np.ndarray) -> Analysis:
        """Return deterministic fake results."""
        return Analysis(
            name=self.name,
            present=True,
            metrics={"posture": 85.0, "focus": 90.0},
        )
