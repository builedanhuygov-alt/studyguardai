"""Weekly narrative summary — the 'real AI coach' output.

Produces an explainable weekly narrative (hours, peak focus window, weekday
dips, and a concrete suggestion) from analytics + raw metric points. Pure and
deterministic; a future LLM coach can consume the same structured facts.
"""
from __future__ import annotations

import calendar
from collections import defaultdict
from collections.abc import Sequence

from studyguard.analytics.models import DailyStats, MetricPoint
from studyguard.coach.engine import focus_by_hour

_DIP_RATIO = 0.85  # <=85% of the weekly mean counts as a dip


def _format_hour(hour: int) -> str:
    period = "AM" if hour < 12 else "PM"
    twelve = hour % 12 or 12
    return f"{twelve} {period}"


def weekly_summary(daily: Sequence[DailyStats], points: Sequence[MetricPoint]) -> dict:
    """Return a structured weekly coaching summary with a natural-language narrative."""
    last7 = list(daily)[-7:]
    hours = round(sum(day.study_minutes for day in last7) / 60.0, 1)

    hourly = focus_by_hour(points)
    peak_window = None
    if hourly:
        best = max(hourly, key=lambda h: (hourly[h] + hourly.get((h + 1) % 24, hourly[h])) / 2)
        peak_window = f"{_format_hour(best)}\u2013{_format_hour((best + 2) % 24)}"

    by_weekday: dict[int, list[float]] = defaultdict(list)
    for point in points:
        if point.metric == "focus":
            by_weekday[point.ts.weekday()].append(point.value)
    weekday_avg = {day: sum(v) / len(v) for day, v in by_weekday.items() if v}

    dips = []
    if weekday_avg:
        mean = sum(weekday_avg.values()) / len(weekday_avg)
        for day, value in sorted(weekday_avg.items()):
            if mean > 0 and value <= mean * _DIP_RATIO:
                dips.append({"weekday": calendar.day_name[day], "drop_pct": round((1 - value / mean) * 100)})

    narrative = [f"This week you studied about {hours} hours."]
    if peak_window:
        narrative.append(f"Your focus is highest around {peak_window}.")
    if dips:
        names = " and ".join(item["weekday"] for item in dips)
        worst = max(item["drop_pct"] for item in dips)
        narrative.append(f"Performance drops on {names} (down about {worst}%).")
    suggestion = "Schedule your hardest subjects during your peak focus window."
    narrative.append(suggestion)

    confidence = "high" if len(last7) >= 5 else "medium" if len(last7) >= 3 else "low"
    return {
        "hours": hours,
        "peak_window": peak_window,
        "weekday_dips": dips,
        "narrative": narrative,
        "suggestion": suggestion,
        "confidence": confidence,
    }
