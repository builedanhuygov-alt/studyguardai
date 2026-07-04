"""AI study coach: evidence-backed, explainable coaching messages.

Every message carries evidence, supporting metrics, and a confidence level, so
the coach never feels like it is guessing.
"""
from studyguard.coach.engine import coach_messages, focus_by_hour
from studyguard.coach.models import CoachMessage

__all__ = ["CoachMessage", "coach_messages", "focus_by_hour"]
