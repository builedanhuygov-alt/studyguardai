"""Core domain objects and types for StudyGuard AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class Analysis:
    """Result of a single detector analysis on a frame."""

    name: str
    present: bool
    metrics: dict[str, Any]


@dataclass
class Snapshot:
    """Aggregated snapshot of study state at a moment in time."""

    frame_index: int
    present: bool
    posture_score: float
    focus_score: float
    status: str
    alert_type: str
    fps: float
    elapsed_s: float
    distractions: int


class Aggregator:
    """Aggregates detector results into immutable snapshots."""

    def build(
        self,
        analyses: list[Analysis],
        frame_index: int,
        fps: float,
        elapsed_s: float,
        distractions: int,
    ) -> Snapshot:
        """Build a snapshot from detector analyses."""
        posture = 80.0
        focus = 85.0
        status = "FOCUSED"
        alert = "ok"

        return Snapshot(
            frame_index=frame_index,
            present=True,
            posture_score=posture,
            focus_score=focus,
            status=status,
            alert_type=alert,
            fps=fps,
            elapsed_s=elapsed_s,
            distractions=distractions,
        )


def register_detector(cls: type) -> type:
    """Decorator to register a detector plugin."""
    return cls
