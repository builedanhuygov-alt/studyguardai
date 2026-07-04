from datetime import datetime, timedelta, timezone

from studyguard.analytics.engine import (
    burnout_risk,
    daily_stats,
    generate_insights,
    metric_trend,
    recommend,
    study_streak,
)
from studyguard.analytics.models import MetricPoint


def _series(focus_by_day, *, posture=80.0, per_day=60):
    points = []
    for index, focus in enumerate(focus_by_day):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=index)
        for i in range(per_day):
            ts = base + timedelta(seconds=i)
            points.append(MetricPoint(ts, "present", 1.0))
            points.append(MetricPoint(ts, "focus", focus))
            points.append(MetricPoint(ts, "posture", posture))
    return points


def test_daily_stats_groups_by_day():
    daily = daily_stats(_series([50.0, 60.0]), sample_period_s=1.0)
    assert len(daily) == 2
    assert daily[0].avg_focus == 50.0
    assert daily[0].sample_count == 60
    assert round(daily[0].study_minutes, 1) == 1.0


def test_focus_trend_improving():
    trend = metric_trend(daily_stats(_series([40.0, 55.0, 70.0])), "avg_focus")
    assert trend.direction == "improving"
    assert trend.slope_per_day > 0


def test_study_streak_counts_trailing_days():
    daily = daily_stats(_series([60.0, 60.0, 60.0]))
    assert study_streak(daily, min_minutes=0.5) == 3


def test_burnout_elevated_when_focus_declines_and_hours_high():
    daily = daily_stats(_series([80.0, 70.0, 60.0, 50.0, 40.0]), sample_period_s=120.0)
    level, score = burnout_risk(daily)
    assert level in {"elevated", "high"}
    assert score >= 0.4


def test_insights_and_recommendations_are_generated():
    daily = daily_stats(_series([70.0, 60.0, 50.0]))
    assert any(insight.key == "focus_trend" for insight in generate_insights(daily))
    assert any(rec.key == "pomodoro" for rec in recommend(daily))


def test_empty_input_is_safe():
    assert daily_stats([]) == []
    assert generate_insights([]) == []
    assert recommend([])[0].key == "start"
