"""Example third-party plugin: a Pomodoro-schedule data source.

Demonstrates the marketplace path — a complete `DataSource` in one file that
registers itself and emits ``planned_minutes`` metric points from a schedule.
Load via ``import plugins.pomodoro_plugin`` (or an entry point in a real package).
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from studyguard.analytics.models import MetricPoint
from studyguard.sources.base import SourceHealth, SourceInfo, SourceStatus, register_source


@register_source("pomodoro")
class PomodoroDataSource:
    """Turns N daily Pomodoro blocks into planned study minutes."""

    info = SourceInfo(key="pomodoro", title="Pomodoro", category="manual", requires_consent=False)

    def __init__(self, days: int = 7, blocks_per_day: int = 4, block_minutes: int = 25) -> None:
        self._days = days
        self._blocks = blocks_per_day
        self._minutes = block_minutes
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def validate(self) -> bool:
        return self._blocks > 0 and self._minutes > 0

    def health_check(self) -> SourceHealth:
        status = SourceStatus.CONNECTED if self._connected else SourceStatus.DISCONNECTED
        return SourceHealth(status, "pomodoro schedule")

    def collect(self) -> Sequence[MetricPoint]:
        if not self._connected:
            return []
        start = datetime(2026, 1, 1, 9, tzinfo=timezone.utc)
        points: list[MetricPoint] = []
        for day in range(self._days):
            ts = start + timedelta(days=day)
            points.append(MetricPoint(ts, "planned_minutes", float(self._blocks * self._minutes)))
        return points
