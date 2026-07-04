"""Pure gamification logic: XP, levels, streaks, consistency, achievements, goals.

Deterministic and framework-free; all tunables are named constants.
"""
from __future__ import annotations

from collections.abc import Sequence

from studyguard.analytics.engine import study_streak
from studyguard.analytics.models import DailyStats
from studyguard.goals.models import Achievement, GamificationState, GoalProgress

_XP_PER_STUDY_MINUTE = 1.0
_XP_PER_FOCUS_POINT = 0.2
_XP_PER_LEVEL = 100.0
_CONSISTENCY_WINDOW = 7
_CONSISTENCY_MIN_MINUTES = 5.0
_DAILY_TARGET_MINUTES = 60.0
_WEEKLY_TARGET_MINUTES = 300.0
_FOCUS_MASTER_THRESHOLD = 90.0
_MARATHON_MINUTES = 120.0


def _total_xp(daily: Sequence[DailyStats]) -> int:
    xp = sum(
        day.study_minutes * _XP_PER_STUDY_MINUTE + day.avg_focus * _XP_PER_FOCUS_POINT
        for day in daily
    )
    return int(xp)


def _consistency(daily: Sequence[DailyStats]) -> float:
    window = list(daily)[-_CONSISTENCY_WINDOW:]
    if not window:
        return 0.0
    active = sum(1 for day in window if day.study_minutes >= _CONSISTENCY_MIN_MINUTES)
    return round(active / len(window), 3)


def _achievements(daily: Sequence[DailyStats], streak: int) -> tuple[Achievement, ...]:
    studied = any(day.study_minutes > 0 for day in daily)
    focus_master = any(day.avg_focus >= _FOCUS_MASTER_THRESHOLD for day in daily)
    marathon = any(day.study_minutes >= _MARATHON_MINUTES for day in daily)
    definitions = [
        ("first_session", "First session", "Completed your first study session.", studied),
        ("streak_3", "On a roll", "Studied 3 days in a row.", streak >= 3),
        ("streak_7", "Week warrior", "Studied 7 days in a row.", streak >= 7),
        ("focus_master", "Focus master", "Reached an average focus of 90+ in a day.", focus_master),
        ("marathon", "Marathoner", "Studied 2+ hours in a single day.", marathon),
    ]
    return tuple(Achievement(key, title, desc, unlocked) for key, title, desc, unlocked in definitions)


def compute_gamification(daily: Sequence[DailyStats]) -> GamificationState:
    """Compute XP, level, streak, consistency, and achievements."""
    total_xp = _total_xp(daily)
    level = int(total_xp // _XP_PER_LEVEL) + 1
    xp_into_level = int(total_xp - (level - 1) * _XP_PER_LEVEL)
    xp_to_next = int(_XP_PER_LEVEL - xp_into_level)
    streak = study_streak(daily)
    return GamificationState(
        xp=total_xp,
        level=level,
        xp_into_level=xp_into_level,
        xp_to_next_level=xp_to_next,
        streak_days=streak,
        consistency=_consistency(daily),
        achievements=_achievements(daily, streak),
    )


def goal_progress(
    daily: Sequence[DailyStats],
    *,
    period: str = "daily",
    target_minutes: float | None = None,
) -> GoalProgress:
    """Compute progress toward a daily or weekly study-time goal."""
    if period == "daily":
        target = target_minutes if target_minutes is not None else _DAILY_TARGET_MINUTES
        actual = daily[-1].study_minutes if daily else 0.0
    elif period == "weekly":
        target = target_minutes if target_minutes is not None else _WEEKLY_TARGET_MINUTES
        actual = sum(day.study_minutes for day in list(daily)[-7:])
    else:
        raise ValueError("period must be 'daily' or 'weekly'")
    progress = round(min(actual / target, 1.0), 3) if target > 0 else 0.0
    return GoalProgress(
        period=period,
        target_minutes=target,
        actual_minutes=round(actual, 3),
        progress=progress,
        achieved=actual >= target,
    )
