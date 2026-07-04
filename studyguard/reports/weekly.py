"""Study reports that explain what happened, why (as correlation), what to do,
and with what confidence.

One builder serves multiple audiences and periods; parent/teacher framing are
documented refinements of the same structure.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from studyguard.analytics.engine import metric_trend, study_streak
from studyguard.analytics.models import DailyStats
from studyguard.insight.engine import generate

_AUDIENCES = {"student", "parent", "teacher", "personal"}
_PERIODS = {"week", "month"}


@dataclass(frozen=True, slots=True)
class ReportSection:
    """A titled block of report prose."""

    heading: str
    body: str


@dataclass(frozen=True, slots=True)
class Report:
    """A structured, audience-aware study report."""

    title: str
    audience: str
    period: str
    confidence: str
    sections: tuple[ReportSection, ...]


def _overall_confidence(daily: Sequence[DailyStats]) -> str:
    days = len(daily)
    if days >= 5:
        return "high"
    if days >= 3:
        return "medium"
    return "low"


def build_report(daily: Sequence[DailyStats], *, period: str = "week", audience: str = "student") -> Report:
    """Build a structured report from daily statistics."""
    if period not in _PERIODS:
        raise ValueError(f"period must be one of {sorted(_PERIODS)}")
    if audience not in _AUDIENCES:
        raise ValueError(f"audience must be one of {sorted(_AUDIENCES)}")

    if not daily:
        return Report(
            title=f"{period.capitalize()}ly study report",
            audience=audience,
            period=period,
            confidence="low",
            sections=(ReportSection("What happened", "No study data recorded for this period yet."),),
        )

    total_minutes = sum(day.study_minutes for day in daily)
    avg_focus = sum(day.avg_focus for day in daily) / len(daily)
    avg_posture = sum(day.avg_posture for day in daily) / len(daily)
    streak = study_streak(daily)
    focus_trend = metric_trend(daily, "avg_focus")
    insight = generate(daily)

    what = (
        f"You studied about {total_minutes:.0f} minutes across {len(daily)} day(s). "
        f"Average focus was {avg_focus:.0f} and posture {avg_posture:.0f}. "
        f"Focus is {focus_trend.direction}. Current streak: {streak} day(s)."
    )
    why = (
        insight.inference.statement
        if insight.inference is not None
        else "Not enough corroborating signals to infer causes for this period."
    )
    if insight.recommendations:
        suggestions = "\n".join(f"- {rec.message} ({rec.rationale})" for rec in insight.recommendations)
    else:
        suggestions = "- Keep your current routine; metrics are stable or improving."
    confidence = _overall_confidence(daily)
    confidence_body = (
        f"Overall confidence: {confidence}. Based on {len(daily)} day(s) of "
        "on-device metrics from the camera source only; correlations are not causes."
    )

    return Report(
        title=f"{period.capitalize()}ly study report",
        audience=audience,
        period=period,
        confidence=confidence,
        sections=(
            ReportSection("What happened", what),
            ReportSection("Why (correlations, not causes)", why),
            ReportSection("Suggested improvements", suggestions),
            ReportSection("Confidence", confidence_body),
        ),
    )


def render_markdown(report: Report) -> str:
    """Render a report as Markdown."""
    lines = [f"# {report.title}", "", f"_Audience: {report.audience} · Confidence: {report.confidence}_", ""]
    for section in report.sections:
        lines.append(f"## {section.heading}")
        lines.append(section.body)
        lines.append("")
    return "\n".join(lines).strip() + "\n"
