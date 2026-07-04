"""Immutable, sensor-agnostic domain records for learning analytics.

``MetricPoint`` is intentionally generic (any metric from any sensor) so the
platform can grow beyond the webcam — e.g. keyboard cadence, app usage, or a
wearable — without changing the analytics engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class MetricPoint:
    """A single timestamped measurement from any sensor."""

    ts: datetime
    metric: str
    value: float


@dataclass(frozen=True, slots=True)
class DailyStats:
    """Aggregated metrics for one calendar day (UTC)."""

    day: date
    study_minutes: float
    avg_focus: float
    avg_posture: float
    sample_count: int


@dataclass(frozen=True, slots=True)
class Trend:
    """A linear trend of a metric over time."""

    metric: str
    slope_per_day: float
    direction: str  # "improving" | "declining" | "stable"


@dataclass(frozen=True, slots=True)
class Insight:
    """A human-readable observation about study behavior."""

    key: str
    title: str
    detail: str
    severity: str  # "positive" | "info" | "warning"


@dataclass(frozen=True, slots=True)
class Recommendation:
    """An actionable, personalized suggestion with its rationale."""

    key: str
    message: str
    rationale: str
