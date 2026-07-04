from datetime import datetime, timedelta, timezone

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.models import MetricPoint
from studyguard.goals.engine import compute_gamification, goal_progress


def _series(days, minutes_per_day=60, focus=80.0):
    points = []
    for index in range(days):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=index)
        for minute in range(minutes_per_day):
            ts = base + timedelta(seconds=minute * 60)
            points += [
                MetricPoint(ts, "present", 1.0),
                MetricPoint(ts, "focus", focus),
                MetricPoint(ts, "posture", 80.0),
            ]
    return daily_stats(points, sample_period_s=60.0)


def test_xp_and_level_are_deterministic():
    state = compute_gamification(_series(3, 60, 80.0))  # 76 xp/day -> 228
    assert state.xp == 228
    assert state.level == 3
    assert state.xp_into_level == 28
    assert state.xp_to_next_level == 72


def test_streak_and_consistency():
    state = compute_gamification(_series(3))
    assert state.streak_days == 3
    assert state.consistency == 1.0


def test_achievements_unlock():
    unlocked = {a.key: a.unlocked for a in compute_gamification(_series(7, 130, 95.0)).achievements}
    assert unlocked["first_session"]
    assert unlocked["streak_7"]
    assert unlocked["focus_master"]
    assert unlocked["marathon"]


def test_goal_progress_daily_and_weekly():
    daily = goal_progress(_series(1, 30), period="daily")
    assert daily.actual_minutes == 30
    assert daily.progress == 0.5
    assert daily.achieved is False
    weekly = goal_progress(_series(7, 60), period="weekly")
    assert weekly.achieved is True
