"""Pure posture/focus scoring from a detected face box.

Kept free of OpenCV so the heuristic is deterministic, tunable (no magic
numbers), and unit-testable without a camera. All public functions are pure.
"""
from __future__ import annotations

from dataclasses import dataclass

_SCORE_MIN = 0.0
_SCORE_MAX = 100.0


@dataclass(frozen=True)
class PostureFocusConfig:
    """Tunable thresholds for the face-geometry posture/focus heuristic.

    Scoring parameters:
        screen_center_x: horizontal position treated as "looking at the screen".
        slouch_center_y: face-center-y above which a slouch penalty begins.
        slouch_penalty: penalty scale applied as the face drops in-frame.
        min_face_ratio: face-height / frame-height below which the user is
            considered to be leaning back.
        distance_penalty: penalty scale applied as the face shrinks.
        off_center_penalty: focus penalty scale for horizontal offset.
        absent_posture / absent_focus: values reported when no face is found.

    Detection parameters (OpenCV Haar cascade):
        detection_scale_factor, detection_min_neighbors, detection_min_size.
    """

    screen_center_x: float = 0.5
    slouch_center_y: float = 0.5
    slouch_penalty: float = 220.0
    min_face_ratio: float = 0.28
    distance_penalty: float = 200.0
    off_center_penalty: float = 200.0
    absent_posture: float = 60.0
    absent_focus: float = 0.0
    detection_scale_factor: float = 1.1
    detection_min_neighbors: int = 5
    detection_min_size: int = 60


def clamp(value: float, low: float = _SCORE_MIN, high: float = _SCORE_MAX) -> float:
    """Clamp a score into the ``[low, high]`` range."""
    return max(low, min(high, value))


def score_posture(center_y: float, face_ratio: float, config: PostureFocusConfig) -> float:
    """Score posture 0-100 from vertical face position and apparent size.

    A face that drifts toward the bottom of the frame (slouching) or shrinks
    (leaning back) reduces the score. The result is clamped to 0-100.
    """
    posture = _SCORE_MAX
    if center_y > config.slouch_center_y:
        posture -= (center_y - config.slouch_center_y) * config.slouch_penalty
    if face_ratio < config.min_face_ratio:
        posture -= (config.min_face_ratio - face_ratio) * config.distance_penalty
    return clamp(posture)


def score_focus(center_x: float, config: PostureFocusConfig) -> float:
    """Score focus 0-100 from horizontal face offset (looking away lowers it)."""
    return clamp(_SCORE_MAX - abs(center_x - config.screen_center_x) * config.off_center_penalty)
