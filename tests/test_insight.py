from datetime import datetime, timedelta, timezone

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.models import MetricPoint
from studyguard.insight.engine import build_insight, generate, observations_from_daily
from studyguard.insight.models import Confidence, Observation


def _declining_series():
    points = []
    for index, focus in enumerate([80.0, 65.0, 50.0, 35.0]):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=index)
        for i in range(30):
            ts = base + timedelta(seconds=i)
            points += [
                MetricPoint(ts, "present", 1.0),
                MetricPoint(ts, "focus", focus),
                MetricPoint(ts, "posture", 50.0 - index * 5),
            ]
    return daily_stats(points, sample_period_s=120.0)


def test_observations_include_focus_trend():
    obs = observations_from_daily(_declining_series())
    assert any(o.key == "focus_trend" for o in obs)
    assert all(o.source == "camera" for o in obs)


def test_inference_is_hedged_not_causal():
    insight = generate(_declining_series())
    assert insight.inference is not None
    assert "not a proven cause" in insight.inference.statement.lower()


def test_multi_source_raises_confidence():
    observations = [
        Observation("focus_trend", "camera", "Focus is declining."),
        Observation("planned_gap", "calendar", "Studied 40 minutes less than planned."),
        Observation("stress", "wearable", "Stress level increased."),
    ]
    insight = build_insight(observations)
    assert insight.inference is not None
    assert insight.inference.confidence is Confidence.HIGH


def test_no_inference_without_corroboration():
    insight = build_insight([Observation("streak", "camera", "2-day streak.")])
    assert insight.inference is None
