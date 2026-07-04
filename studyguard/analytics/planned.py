"""Planned-vs-actual study-time analytics (calendar + camera).

Pure function combining calendar ``planned_minutes`` points with actual study
time from :class:`DailyStats`. Sensor-agnostic: works for any planning source.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from studyguard.analytics.models import DailyStats, MetricPoint


def planned_vs_actual(points: Sequence[MetricPoint], daily: Sequence[DailyStats]) -> list[dict]:
    """Return per-day planned vs actual study minutes and their delta."""
    planned: dict[object, float] = defaultdict(float)
    for point in points:
        if point.metric == "planned_minutes":
            planned[point.ts.date()] += point.value
    actual = {day.day: day.study_minutes for day in daily}
    days = sorted(set(planned) | set(actual))
    return [
        {
            "date": day.isoformat(),
            "planned": round(planned.get(day, 0.0), 2),
            "actual": round(actual.get(day, 0.0), 2),
            "delta": round(actual.get(day, 0.0) - planned.get(day, 0.0), 2),
        }
        for day in days
    ]
