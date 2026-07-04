"""Multi-source insight engine.

Combines observations from any number of sources into insights that explicitly
separate Observation, Inference, and Recommendation — and never claim causation.
"""
from studyguard.insight.engine import (
    build_insight,
    coach_recommendations,
    generate,
    observations_from_daily,
)
from studyguard.insight.models import (
    CoachRecommendation,
    CombinedInsight,
    Confidence,
    Inference,
    Observation,
)

__all__ = [
    "Confidence",
    "Observation",
    "Inference",
    "CoachRecommendation",
    "CombinedInsight",
    "observations_from_daily",
    "coach_recommendations",
    "build_insight",
    "generate",
]
