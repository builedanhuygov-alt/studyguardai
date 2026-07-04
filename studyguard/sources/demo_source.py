"""Deterministic in-memory demo data source (seed data for the dashboard).

Provides realistic synthetic ``MetricPoint``s without a camera or database, so
the dashboard and API can be explored offline. This is the only sanctioned
source of seed data — no fake data is hard-coded into the UI.
"""
from __future__ import annotations

import math
import random
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from studyguard.analytics.models import MetricPoint
from studyguard.sources.base import SourceHealth, SourceInfo, SourceStatus, register_source

_START = datetime(2026, 1, 1, tzinfo=timezone.utc)


@register_source("demo")
class DemoDataSource:
    """Generates deterministic synthetic study metrics."""

    info = SourceInfo(key="demo", title="Demo (seed data)", category="sensor", requires_consent=False)

    def __init__(self, days: int = 14, samples_per_day: int = 90, seed: int = 7) -> None:
        self._days = days
        self._samples_per_day = samples_per_day
        self._seed = seed
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def validate(self) -> bool:
        return self._days > 0 and self._samples_per_day > 0

    def health_check(self) -> SourceHealth:
        status = SourceStatus.CONNECTED if self._connected else SourceStatus.DISCONNECTED
        return SourceHealth(status, "synthetic seed data")

    def collect(self) -> Sequence[MetricPoint]:
        if not self._connected:
            return []
        rng = random.Random(self._seed)
        points: list[MetricPoint] = []
        for day in range(self._days):
            base_focus = 55.0 + day * 1.2  # gentle upward trend
            hour = 18 if day % 2 == 0 else 10  # alternate evening/morning study
            day_start = _START + timedelta(days=day)
            for minute in range(self._samples_per_day):
                ts = day_start + timedelta(hours=hour, minutes=minute)
                focus = _clip(base_focus + 15.0 * math.sin(minute / 10.0) + rng.uniform(-5.0, 5.0))
                posture = _clip(78.0 - day * 0.3 + rng.uniform(-8.0, 8.0))
                points.append(MetricPoint(ts, "present", 1.0))
                points.append(MetricPoint(ts, "focus", round(focus, 2)))
                points.append(MetricPoint(ts, "posture", round(posture, 2)))
        return points


def _clip(value: float) -> float:
    return max(0.0, min(100.0, value))
