"""Pydantic schemas for API validation."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class CoachMessageModel(BaseModel):
    """Coach message schema."""

    title: str
    message: str
    confidence: float
    evidence: Optional[list[str]] = None


class GoalsModel(BaseModel):
    """Goals schema."""

    level: int
    xp: int
    xp_to_next_level: int
    streak_days: int
    consistency: float
    daily_goal: dict[str, Any]
    weekly_goal: dict[str, Any]
    achievements: list[dict[str, Any]]


class ConnectSourceRequest(BaseModel):
    """Request to connect a data source."""

    config: dict[str, Any]
