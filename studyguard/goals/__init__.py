"""Goals, streaks, XP, levels, achievements, and consistency (gamification)."""
from studyguard.goals.engine import compute_gamification, goal_progress
from studyguard.goals.models import Achievement, GamificationState, GoalProgress

__all__ = [
    "Achievement",
    "GamificationState",
    "GoalProgress",
    "compute_gamification",
    "goal_progress",
]
