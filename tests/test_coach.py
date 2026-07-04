from datetime import datetime, timedelta, timezone

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.models import MetricPoint
from studyguard.coach.engine import coach_messages, focus_by_hour


def _points(focus_by_day, hour=19):
    points = []
    for index, focus in enumerate(focus_by_day):
        base = datetime(2026, 1, 1, hour, 0, tzinfo=timezone.utc) + timedelta(days=index)
        for second in range(60):
            ts = base + timedelta(seconds=second)
            points += [
                MetricPoint(ts, "present", 1.0),
                MetricPoint(ts, "focus", focus),
                MetricPoint(ts, "posture", 80.0),
            ]
    return points


def test_empty_returns_welcome():
    messages = coach_messages([], [])
    assert messages and messages[0].key == "welcome"


def test_focus_vs_previous_day_with_evidence():
    points = _points([50.0, 70.0])
    daily = daily_stats(points, sample_period_s=1.0)
    by_key = {m.key: m for m in coach_messages(daily, points)}
    assert "focus_vs_prev_day" in by_key
    message = by_key["focus_vs_prev_day"]
    assert message.supporting_metrics["delta"] == 20.0
    assert message.evidence


def test_best_time_of_day_is_evening():
    points = _points([70.0, 72.0, 74.0], hour=19)
    daily = daily_stats(points, sample_period_s=1.0)
    by_key = {m.key: m for m in coach_messages(daily, points)}
    assert "best_time_of_day" in by_key
    assert "evening" in by_key["best_time_of_day"].message


def test_focus_by_hour():
    assert focus_by_hour(_points([60.0], hour=8)).get(8) == 60.0
