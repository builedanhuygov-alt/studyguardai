"""Immutable records for the goal / gamification system."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GoalProgress:
    """Progress toward a study-time goal for a period."""

    period: str  # "daily" | "weekly"
    target_minutes: float
    actual_minutes: float
    progress: float  # 0.0 - 1.0
    achieved: bool


@dataclass(frozen=True, slots=True)
class Achievement:
    """An unlockable milestone."""

    key: str
    title: str
    description: str
    unlocked: bool


@dataclass(frozen=True, slots=True)
class GamificationState:
    """The learner's overall progression snapshot."""

    xp: int
    level: int
    xp_into_level: int
    xp_to_next_level: int
    streak_days: int
    consistency: float  # 0.0 - 1.0
    achievements: tuple[Achievement, ...]
