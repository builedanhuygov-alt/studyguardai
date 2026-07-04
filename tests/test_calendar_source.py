from datetime import datetime, timezone

from studyguard.analytics.engine import daily_stats
from studyguard.analytics.planned import planned_vs_actual
from studyguard.sources import DataSource, create_source
from studyguard.sources.calendar_source import GoogleCalendarSource, MockCalendarClient


def _client():
    return MockCalendarClient(
        [
            (datetime(2026, 1, 1, 9, tzinfo=timezone.utc), 60.0),
            (datetime(2026, 1, 2, 9, tzinfo=timezone.utc), 45.0),
        ]
    )


def test_calendar_source_protocol_and_lifecycle():
    source = GoogleCalendarSource(_client())
    assert isinstance(source, DataSource)
    assert source.validate() is True
    assert source.collect() == []  # not connected
    source.connect()
    points = source.collect()
    assert [p.metric for p in points] == ["planned_minutes", "planned_minutes"]
    assert points[0].value == 60.0
    source.disconnect()
    assert source.collect() == []


def test_calendar_registered():
    assert isinstance(create_source("google_calendar"), GoogleCalendarSource)


def test_planned_vs_actual():
    source = GoogleCalendarSource(_client())
    source.connect()
    rows = planned_vs_actual(source.collect(), daily_stats([]))
    assert rows[0]["planned"] == 60.0
    assert rows[0]["actual"] == 0.0
    assert rows[0]["delta"] == -60.0
