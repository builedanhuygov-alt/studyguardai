"""Pure learning-analytics functions.

Input is a sequence of sensor-agnostic ``MetricPoint`` records; output is daily
stats, trends, habit/streak metrics, a burnout-risk signal, insights, and
recommendations. The recommendation logic is a rule-based **v0** kept behind
small pure functions so a learned model can replace it later without changing
callers.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import date, timedelta

from studyguard.analytics.models import (
    DailyStats,
    Insight,
    MetricPoint,
    Recommendation,
    Trend,
)

FOCUS = "focus"
POSTURE = "posture"
PRESENT = "present"

_TREND_EPSILON = 0.5      # |slope/day| below this is treated as "stable"
_PRESENT_TRUE = 0.5       # a "present" value >= this counts as present
_STREAK_MIN_MINUTES = 5.0
_BURNOUT_WINDOW = 5
_HEAVY_MINUTES = 120.0


def _average(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def daily_stats(points: Sequence[MetricPoint], *, sample_period_s: float = 1.0) -> list[DailyStats]:
    """Aggregate raw metric points into per-day statistics (UTC calendar days).

    ``study_minutes`` is approximated from the number of "present" samples times
    ``sample_period_s``; when no presence metric exists it falls back to the
    sample count. Days are returned in chronological order.
    """
    grouped: dict[date, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for point in points:
        grouped[point.ts.date()][point.metric].append(point.value)

    result: list[DailyStats] = []
    for day in sorted(grouped):
        metrics = grouped[day]
        focus = metrics.get(FOCUS, [])
        posture = metrics.get(POSTURE, [])
        present = metrics.get(PRESENT, [])
        sample_count = len(focus) or len(posture) or len(present)
        present_count = sum(1 for value in present if value >= _PRESENT_TRUE) if present else sample_count
        study_minutes = round(present_count * sample_period_s / 60.0, 3)
        result.append(
            DailyStats(
                day=day,
                study_minutes=study_minutes,
                avg_focus=_average(focus),
                avg_posture=_average(posture),
                sample_count=sample_count,
            )
        )
    return result


def linear_trend(values: Sequence[float]) -> float:
    """Least-squares slope of ``values`` against their index (per step)."""
    n = len(values)
    if n < 2:
        return 0.0
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(values))
    denominator = sum((x - mean_x) ** 2 for x in range(n))
    return numerator / denominator if denominator else 0.0


def metric_trend(daily: Sequence[DailyStats], attribute: str) -> Trend:
    """Compute the trend of a ``DailyStats`` attribute over time."""
    slope = linear_trend([getattr(day, attribute) for day in daily])
    if slope > _TREND_EPSILON:
        direction = "improving"
    elif slope < -_TREND_EPSILON:
        direction = "declining"
    else:
        direction = "stable"
    return Trend(metric=attribute, slope_per_day=round(slope, 3), direction=direction)


def study_streak(daily: Sequence[DailyStats], *, min_minutes: float = _STREAK_MIN_MINUTES) -> int:
    """Count consecutive study days ending on the most recent qualifying day."""
    qualifying = {day.day for day in daily if day.study_minutes >= min_minutes}
    if not qualifying:
        return 0
    cursor = max(qualifying)
    streak = 0
    while cursor in qualifying:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def burnout_risk(
    daily: Sequence[DailyStats],
    *,
    window: int = _BURNOUT_WINDOW,
    heavy_minutes: float = _HEAVY_MINUTES,
) -> tuple[str, float]:
    """Heuristic burnout-risk signal over the most recent ``window`` days.

    Risk rises with declining focus, increasing workload, and heavy average
    study time. Returns ``(level, score)`` where level is low/elevated/high.
    This is an explainable v0 signal, not a clinical measure.
    """
    recent = list(daily)[-window:]
    if len(recent) < 3:
        return ("low", 0.0)
    focus_trend = metric_trend(recent, "avg_focus")
    minutes_trend = metric_trend(recent, "study_minutes")
    avg_minutes = sum(day.study_minutes for day in recent) / len(recent)

    score = 0.0
    if focus_trend.direction == "declining":
        score += 0.4
    if minutes_trend.direction == "improving":  # rising workload
        score += 0.3
    if avg_minutes >= heavy_minutes:
        score += 0.3
    score = round(min(score, 1.0), 3)
    level = "high" if score >= 0.7 else "elevated" if score >= 0.4 else "low"
    return (level, score)


def generate_insights(daily: Sequence[DailyStats]) -> list[Insight]:
    """Turn daily stats into human-readable insights."""
    if not daily:
        return []
    insights: list[Insight] = []
    focus = metric_trend(daily, "avg_focus")
    posture = metric_trend(daily, "avg_posture")
    streak = study_streak(daily)
    best = max(daily, key=lambda day: day.avg_focus)

    focus_severity = (
        "positive" if focus.direction == "improving"
        else "warning" if focus.direction == "declining"
        else "info"
    )
    insights.append(
        Insight(
            "focus_trend",
            "Focus trend",
            f"Your focus is {focus.direction} ({focus.slope_per_day:+.1f}/day).",
            focus_severity,
        )
    )
    if streak >= 2:
        insights.append(
            Insight("streak", "Study streak", f"{streak} days in a row — keep it going!", "positive")
        )
    if posture.direction == "declining":
        insights.append(
            Insight("posture_trend", "Posture slipping", "Your posture score is trending down.", "warning")
        )
    insights.append(
        Insight(
            "best_day",
            "Best focus day",
            f"{best.day.isoformat()} with average focus {best.avg_focus:.0f}.",
            "info",
        )
    )
    level, score = burnout_risk(daily)
    if level != "low":
        insights.append(
            Insight("burnout", "Burnout watch", f"Burnout risk is {level} (score {score:.0%}).", "warning")
        )
    return insights


def recommend(daily: Sequence[DailyStats]) -> list[Recommendation]:
    """Produce personalized, actionable recommendations (rule-based v0)."""
    if not daily:
        return [Recommendation("start", "Log your first study session today.", "No study data yet.")]
    recommendations: list[Recommendation] = []
    focus = metric_trend(daily, "avg_focus")
    posture = metric_trend(daily, "avg_posture")
    level, _ = burnout_risk(daily)
    streak = study_streak(daily)

    if focus.direction == "declining":
        recommendations.append(
            Recommendation(
                "pomodoro",
                "Try 25-minute focus blocks with 5-minute breaks.",
                "Focus is trending down.",
            )
        )
    if posture.direction == "declining":
        recommendations.append(
            Recommendation(
                "posture",
                "Raise your screen to eye level and sit back in your chair.",
                "Posture is trending down.",
            )
        )
    if level != "low":
        recommendations.append(
            Recommendation("rest", "Plan a lighter day or a rest day this week.", f"Burnout risk is {level}.")
        )
    if streak == 0:
        recommendations.append(
            Recommendation("streak", "Study 10 focused minutes to start a new streak.", "No active streak.")
        )
    if not recommendations:
        recommendations.append(
            Recommendation("keep_going", "You're on track — keep your routine.", "Metrics are stable or improving.")
        )
    return recommendations
