"""Draws the HUD from an immutable Snapshot (read-only)."""
from __future__ import annotations

import cv2

from studyguard.core import Snapshot

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_WHITE = (255, 255, 255)
_BAR_BG = (70, 70, 70)
_HEADER = (30, 30, 30)


def _color(value: float):
    if value >= 70.0:
        return (80, 220, 100)
    if value >= 50.0:
        return (0, 215, 255)
    return (60, 60, 235)


def _bar(img, label: str, value: float, y: int) -> None:
    x, width = 8, 170
    cv2.putText(img, label, (x, y - 1), _FONT, 0.5, _WHITE, 1, cv2.LINE_AA)
    bx = x + 78
    cv2.rectangle(img, (bx, y - 12), (bx + width, y), _BAR_BG, -1)
    cv2.rectangle(img, (bx, y - 12), (bx + int(width * value / 100.0), y), _color(value), -1)
    cv2.putText(img, f"{value:3.0f}", (bx + width + 8, y - 1), _FONT, 0.5, _WHITE, 1, cv2.LINE_AA)


def draw_hud(frame, snapshot: Snapshot):
    out = frame.copy()
    height, width = out.shape[:2]
    if snapshot.face_box is not None:
        x, y, fw, fh = snapshot.face_box
        cv2.rectangle(out, (x, y), (x + fw, y + fh), _color(snapshot.focus), 2)
    cv2.rectangle(out, (0, 0), (width, 34), _HEADER, -1)
    cv2.putText(out, f"StudyGuard AI  |  {snapshot.status}", (8, 23), _FONT, 0.6, _WHITE, 1, cv2.LINE_AA)
    cv2.putText(out, f"{snapshot.fps:4.1f} FPS", (width - 95, 23), _FONT, 0.5, _WHITE, 1, cv2.LINE_AA)
    _bar(out, "Posture", snapshot.posture, 62)
    _bar(out, "Focus", snapshot.focus, 92)
    minutes, seconds = divmod(int(snapshot.elapsed_s), 60)
    cv2.putText(out, snapshot.message, (8, height - 42), _FONT, 0.6,
                _color(min(snapshot.posture, snapshot.focus)), 2, cv2.LINE_AA)
    cv2.putText(out, f"Session {minutes:02d}:{seconds:02d}   Distractions: {snapshot.distractions}",
                (8, height - 14), _FONT, 0.55, _WHITE, 1, cv2.LINE_AA)
    return out
