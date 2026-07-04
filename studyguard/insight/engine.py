"""Combine multi-source observations into insights (no causation claims).

Confidence scales with corroboration: more independent sources / observations
raise confidence. Inferences are always phrased as correlations, never causes.
"""
from __future__ import annotations

from collections.abc import Sequence

from studyguard.analytics.engine import burnout_risk, metric_trend, recommend, study_streak
from studyguard.analytics.models import DailyStats
from studyguard.insight.models import (
    CoachRecommendation,
    CombinedInsight,
    Confidence,
    Inference,
    Observation,
)

_CAMERA = "camera"
_POSITIVE_KEYS = {"streak"}  # observations that are good news never trigger a concern inference


def observations_from_daily(daily: Sequence[DailyStats]) -> list[Observation]:
    """Derive camera-based observations from daily statistics."""
    if not daily:
        return []
    observations: list[Observation] = []
    focus = metric_trend(daily, "avg_focus")
    posture = metric_trend(daily, "avg_posture")
    if focus.direction != "stable":
        observations.append(
            Observation("focus_trend", _CAMERA, f"Focus is {focus.direction} ({focus.slope_per_day:+.1f}/day).")
        )
    if posture.direction == "declining":
        observations.append(Observation("posture_trend", _CAMERA, "Posture is trending down."))
    level, _score = burnout_risk(daily)
    if level != "low":
        observations.append(
            Observation("burnout", _CAMERA, f"Sustained workload with reduced focus (risk: {level}).")
        )
    streak = study_streak(daily)
    if streak >= 2:
        observations.append(Observation("streak", _CAMERA, f"{streak}-day study streak."))
    return observations


def coach_recommendations(daily: Sequence[DailyStats]) -> list[CoachRecommendation]:
    """Map analytics recommendations into confidence-tagged coach suggestions."""
    return [
        CoachRecommendation(rec.key, rec.message, rec.rationale, Confidence.MEDIUM)
        for rec in recommend(daily)
    ]


def _confidence(observations: Sequence[Observation]) -> Confidence:
    sources = {observation.source for observation in observations}
    if len(sources) >= 3 or len(observations) >= 4:
        return Confidence.HIGH
    if len(sources) >= 2 or len(observations) >= 2:
        return Confidence.MEDIUM
    return Confidence.LOW


def build_insight(
    observations: Sequence[Observation],
    *,
    recommendations: Sequence[CoachRecommendation] = (),
) -> CombinedInsight:
    """Combine observations (from any sources) into a CombinedInsight.

    An inference is only produced when at least two "negative" signals
    corroborate, and it is always stated as a correlation, not a cause.
    """
    observations = tuple(observations)
    concerns = [obs for obs in observations if obs.key not in _POSITIVE_KEYS]
    inference: Inference | None = None
    if len(concerns) >= 2:
        inference = Inference(
            statement=(
                "These signals may be associated with one another — for example a "
                "heavier workload alongside lower focus and higher stress. This is a "
                "correlation, not a proven cause."
            ),
            confidence=_confidence(observations),
            based_on=tuple(sorted({obs.key for obs in concerns})),
        )
    return CombinedInsight(
        observations=observations,
        inference=inference,
        recommendations=tuple(recommendations),
    )


def generate(
    daily: Sequence[DailyStats],
    *,
    extra_observations: Sequence[Observation] = (),
) -> CombinedInsight:
    """Full pipeline: camera observations + external observations + recommendations.

    ``extra_observations`` lets future sources (calendar, wearable, LMS) feed the
    same combiner without any change here.
    """
    observations = [*observations_from_daily(daily), *extra_observations]
    return build_insight(observations, recommendations=coach_recommendations(daily))
