"""Demo mode with seed data."""

from __future__ import annotations

from studyguard.api import StudyGuardService


def build_demo_service(days: int = 14) -> StudyGuardService:
    """Build a demo service with seed data."""
    return StudyGuardService()
