"""Adapter: read the on-disk ``samples`` table into sensor-agnostic MetricPoints.

Keeps the analytics engine decoupled from storage. A future backend (Postgres,
Timescale, a wearable importer, ...) only needs to yield ``MetricPoint``s.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

from studyguard.analytics.models import MetricPoint


def metric_points_from_sqlite(path: str) -> list[MetricPoint]:
    """Load posture/focus/presence samples from a StudyGuard SQLite database."""
    connection = sqlite3.connect(path)
    try:
        rows = connection.execute(
            "SELECT ts, present, posture, focus FROM samples ORDER BY ts"
        ).fetchall()
    finally:
        connection.close()

    points: list[MetricPoint] = []
    for ts, present, posture, focus in rows:
        moment = datetime.fromisoformat(ts)
        points.append(MetricPoint(moment, "present", float(present)))
        points.append(MetricPoint(moment, "posture", float(posture)))
        points.append(MetricPoint(moment, "focus", float(focus)))
    return points
