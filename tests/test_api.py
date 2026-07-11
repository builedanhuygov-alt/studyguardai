"""Tests for the service API."""

from __future__ import annotations

from studyguard.api import StudyGuardService


def test_service_health() -> None:
    """Test service health check."""
    service = StudyGuardService()
    health = service.get_health()
    assert health["status"] == "healthy"


def test_service_goals() -> None:
    """Test getting user goals."""
    service = StudyGuardService()
    goals = service.get_goals()
    assert goals["level"] >= 1
    assert goals["streak_days"] >= 0
