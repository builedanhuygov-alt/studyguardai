"""Immutable records for the insight engine.

The separation of Observation / Inference / Recommendation is deliberate: we
report what we measured, what it *might* mean (with confidence, never as proven
cause), and what to do about it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Confidence(str, Enum):
    """How much corroborating evidence supports an inference."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class Observation:
    """A measured fact from a single source."""

    key: str
    source: str
    statement: str


@dataclass(frozen=True, slots=True)
class Inference:
    """A hedged, non-causal interpretation of several observations."""

    statement: str
    confidence: Confidence
    based_on: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CoachRecommendation:
    """An actionable suggestion with rationale and confidence."""

    key: str
    message: str
    rationale: str
    confidence: Confidence


@dataclass(frozen=True, slots=True)
class CombinedInsight:
    """Observations + optional inference + recommendations, combined."""

    observations: tuple[Observation, ...]
    inference: Inference | None
    recommendations: tuple[CoachRecommendation, ...]
