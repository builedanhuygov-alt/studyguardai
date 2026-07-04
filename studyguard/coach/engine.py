"""Generate explainable coaching messages from analytics + raw metric points.

Pure functions only. Every message is backed by evidence and a confidence that
scales with the amount of supporting data — no fabricated numbers.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from studyguard.analytics.engine import burnout_risk, metric_trend, study_streak
from studyguard.analytics.models import DailyStats, MetricPoint
from studyguard.coach.models import CoachMessage, Confidence

_MIN_FOCUS_DELTA = 1.0
_TIME_OF_DAY_MIN_SAMPLES = 60
_TIME_BUCKETS = ((5, 12, "morning"), (12, 17, "afternoon"), (17, 22, "evening"))


def focus_by_hour(points: Sequence[MetricPoint]) -> dict[int, float]:
    """Average focus per hour-of-day (UTC) from raw focus points."""
    buckets: dict[int, list[float]] = defaultdict(list)
    for point in points:
        if point.metric == "focus":
            buckets[point.ts.hour].append(point.value)
    return {hour: round(sum(values) / len(values), 3) for hour, values in buckets.items()}


def _time_of_day(hour: int) -> str:
    for start, end, label in _TIME_BUCKETS:
        if start <= hour < end:
            return label
    return "night"


def _confidence_from_days(day_count: int) -> Confidence:
    if day_count >= 5:
        return Confidence.HIGH
    if day_count >= 3:
        return Confidence.MEDIUM
    return Confidence.LOW


def coach_messages(
    daily: Sequence[DailyStats],
    points: Sequence[MetricPoint] = (),
) -> list[CoachMessage]:
    """Build coaching messages. ``points`` enables time-of-day insights."""
    if not daily:
        return [
            CoachMessage(
                key="welcome",
                category="habit",
                title="Let's begin",
                message="Start a study session and I'll begin coaching you with your own data.",
                confidence=Confidence.LOW,
            )
        ]

    messages: list[CoachMessage] = []
    day_confidence = _confidence_from_days(len(daily))

    if len(daily) >= 2:
        today, previous = daily[-1], daily[-2]
        delta = round(today.avg_focus - previous.avg_focus, 1)
        if abs(delta) >= _MIN_FOCUS_DELTA:
            improved = delta > 0
            messages.append(
                CoachMessage(
                    key="focus_vs_prev_day",
                    category="focus",
                    title="Focus vs. yesterday",
                    message=(
                        f"You focused {'better' if improved else 'less'} than the previous "
                        f"study day ({delta:+.0f} points)."
                    ),
                    evidence=(
                        f"today avg focus {today.avg_focus:.0f} vs previous {previous.avg_focus:.0f}",
                    ),
                    supporting_metrics={
                        "today_focus": today.avg_focus,
                        "previous_focus": previous.avg_focus,
                        "delta": delta,
                    },
                    confidence=Confidence.MEDIUM,
                )
            )

    hourly = focus_by_hour(points)
    total_focus_samples = sum(1 for point in points if point.metric == "focus")
    if hourly and total_focus_samples >= _TIME_OF_DAY_MIN_SAMPLES:
        best_hour = max(hourly, key=lambda hour: hourly[hour])
        messages.append(
            CoachMessage(
                key="best_time_of_day",
                category="habit",
                title="Your peak study time",
                message=f"You tend to focus best in the {_time_of_day(best_hour)}.",
                evidence=(f"highest average focus {hourly[best_hour]:.0f} around {best_hour:02d}:00 UTC",),
                supporting_metrics={"best_hour": float(best_hour), "best_hour_focus": hourly[best_hour]},
                confidence=day_confidence,
            )
        )

    streak = study_streak(daily)
    if streak >= 2:
        messages.append(
            CoachMessage(
                key="streak",
                category="habit",
                title="Consistency",
                message=f"You're on a {streak}-day study streak — keep the momentum!",
                evidence=(f"{streak} consecutive study days",),
                supporting_metrics={"streak_days": float(streak)},
                confidence=Confidence.HIGH,
            )
        )

    planned_total = sum(point.value for point in points if point.metric == "planned_minutes")
    if planned_total > 0:
        actual_total = sum(day.study_minutes for day in daily)
        diff = round(planned_total - actual_total, 1)
        if abs(diff) >= 1.0:
            behind = diff > 0
            messages.append(
                CoachMessage(
                    key="planned_vs_actual",
                    category="habit",
                    title="Planned vs. actual",
                    message=(
                        f"You studied {abs(diff):.0f} min "
                        f"{'less than' if behind else 'more than'} you planned."
                    ),
                    evidence=(f"planned {planned_total:.0f} min vs actual {actual_total:.0f} min",),
                    supporting_metrics={
                        "planned_minutes": round(planned_total, 1),
                        "actual_minutes": round(actual_total, 1),
                        "delta": diff,
                    },
                    confidence=Confidence.MEDIUM,
                )
            )

    posture = metric_trend(daily, "avg_posture")
    if posture.direction == "declining":
        messages.append(
            CoachMessage(
                key="posture_decline",
                category="posture",
                title="Posture is slipping",
                message="Your posture score has been trending down; a quick chair reset can help.",
                evidence=(f"posture slope {posture.slope_per_day:+.1f}/day",),
                supporting_metrics={"posture_slope": posture.slope_per_day},
                confidence=day_confidence,
            )
        )

    level, score = burnout_risk(daily)
    if level != "low":
        messages.append(
            CoachMessage(
                key="burnout",
                category="wellbeing",
                title="Take care of yourself",
                message="Signs of study fatigue are building up; consider a lighter session or a rest day.",
                evidence=(f"burnout risk {level} (score {score:.0%})",),
                supporting_metrics={"burnout_score": score},
                confidence=Confidence.MEDIUM,
            )
        )
    return messages
