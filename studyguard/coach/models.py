"""Immutable records for the AI coach."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from studyguard.insight.models import Confidence

__all__ = ["CoachMessage", "Confidence"]


@dataclass(frozen=True, slots=True)
class CoachMessage:
    """A single coaching message with the evidence that justifies it."""

    key: str
    category: str  # "focus" | "posture" | "habit" | "wellbeing"
    title: str
    message: str
    evidence: tuple[str, ...] = ()
    supporting_metrics: Mapping[str, float] = field(default_factory=dict)
    confidence: Confidence = Confidence.LOW
