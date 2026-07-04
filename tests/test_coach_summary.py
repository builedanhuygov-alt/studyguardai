from datetime import datetime, timedelta, timezone

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.models import MetricPoint
from studyguard.coach.summary import weekly_summary


def _points(days=5):
    points = []
    for i in range(days):
        base = datetime(2026, 1, 5, 20, tzinfo=timezone.utc) + timedelta(days=i)  # Mon 8 PM
        for minute in range(60):
            ts = base + timedelta(minutes=minute)
            points += [
                MetricPoint(ts, "present", 1.0),
                MetricPoint(ts, "focus", 80.0),
                MetricPoint(ts, "posture", 80.0),
            ]
    return points


def test_weekly_summary_narrative():
    points = _points(5)
    summary = weekly_summary(daily_stats(points, sample_period_s=60.0), points)
    assert summary["hours"] > 0
    assert summary["peak_window"] is not None
    assert any("hours" in line for line in summary["narrative"])
    assert summary["confidence"] == "high"


def test_weekly_summary_empty_safe():
    summary = weekly_summary([], [])
    assert summary["hours"] == 0
    assert summary["peak_window"] is None
