"""Coach strategy seam: swap the rule-based coach for an LLM coach later.

The pipeline (Raw -> FeatureStore -> Insight -> Coach -> XAI -> Recommendation
-> ActionPlan -> Follow-up) keeps a single stable interface, so a future
``LLMCoach`` can replace ``RuleBasedCoach`` without touching callers.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from studyguard.analytics.models import DailyStats, MetricPoint
from studyguard.coach.engine import coach_messages
from studyguard.coach.models import CoachMessage


@runtime_checkable
class CoachStrategy(Protocol):
    """Produces coaching messages from analytics + raw metric points."""

    name: str

    def generate(
        self, daily: Sequence[DailyStats], points: Sequence[MetricPoint]
    ) -> list[CoachMessage]:
        """Return coaching messages for the given data."""


class RuleBasedCoach:
    """Deterministic, explainable rule-based coach (current default)."""

    name = "rule_based_v0"

    def generate(
        self, daily: Sequence[DailyStats], points: Sequence[MetricPoint]
    ) -> list[CoachMessage]:
        return coach_messages(daily, points)


def default_coach() -> CoachStrategy:
    """Return the active coach strategy (swap here for an LLM coach later)."""
    return RuleBasedCoach()
