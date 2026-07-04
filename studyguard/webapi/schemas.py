"""Typed request/response schemas for the REST API (pydantic v2)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ConnectSourceRequest(BaseModel):
    """Body for connecting a data source."""

    config: dict = Field(default_factory=dict)


class AchievementModel(BaseModel):
    key: str
    title: str
    description: str
    unlocked: bool


class GoalModel(BaseModel):
    period: str
    target_minutes: float
    actual_minutes: float
    progress: float
    achieved: bool


class GoalsModel(BaseModel):
    xp: int
    level: int
    xp_into_level: int
    xp_to_next_level: int
    streak_days: int
    consistency: float
    achievements: list[AchievementModel]
    daily_goal: GoalModel
    weekly_goal: GoalModel


class CoachMessageModel(BaseModel):
    key: str
    category: str
    title: str
    message: str
    evidence: list[str]
    supporting_metrics: dict[str, float]
    confidence: str
