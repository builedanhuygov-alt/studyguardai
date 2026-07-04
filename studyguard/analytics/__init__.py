"""Learning-analytics domain layer.

Sensor-agnostic: consumes generic ``MetricPoint`` records (the camera is only
one source) and produces daily statistics, trends, habit/streak metrics, a
burnout-risk signal, insights, and recommendations. Pure and framework-free so
it can be tested without hardware and reused by any UI or export.
"""
from studyguard.analytics.engine import (
    burnout_risk,
    daily_stats,
    generate_insights,
    linear_trend,
    metric_trend,
    recommend,
    study_streak,
)
from studyguard.analytics.models import (
    DailyStats,
    Insight,
    MetricPoint,
    Recommendation,
    Trend,
)

__all__ = [
    "MetricPoint",
    "DailyStats",
    "Trend",
    "Insight",
    "Recommendation",
    "daily_stats",
    "linear_trend",
    "metric_trend",
    "study_streak",
    "burnout_risk",
    "generate_insights",
    "recommend",
]
