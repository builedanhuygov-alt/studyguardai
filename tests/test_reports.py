from datetime import datetime, timedelta, timezone

import pytest

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.models import MetricPoint
from studyguard.reports.weekly import build_report, render_markdown


def _series(days: int):
    points = []
    for index in range(days):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=index)
        for i in range(30):
            ts = base + timedelta(seconds=i)
            points += [
                MetricPoint(ts, "present", 1.0),
                MetricPoint(ts, "focus", 70.0 - index * 5),
                MetricPoint(ts, "posture", 80.0),
            ]
    return daily_stats(points, sample_period_s=60.0)


def test_report_has_required_sections():
    report = build_report(_series(5), period="week", audience="student")
    headings = [section.heading for section in report.sections]
    assert "What happened" in headings
    assert any("Why" in h for h in headings)
    assert "Suggested improvements" in headings
    assert "Confidence" in headings


def test_confidence_scales_with_data():
    assert build_report(_series(5)).confidence == "high"
    assert build_report(_series(3)).confidence == "medium"
    assert build_report(_series(1)).confidence == "low"


def test_render_markdown_contains_title():
    md = render_markdown(build_report(_series(3)))
    assert md.startswith("# Weekly study report")


def test_empty_report_is_safe():
    report = build_report([], period="week")
    assert report.confidence == "low"


def test_invalid_arguments_raise():
    with pytest.raises(ValueError):
        build_report(_series(2), period="decade")
    with pytest.raises(ValueError):
        build_report(_series(2), audience="alien")
