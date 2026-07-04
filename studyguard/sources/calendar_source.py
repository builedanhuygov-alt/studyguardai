"""Calendar data source (planned study time).

Ships with a deterministic ``MockCalendarClient`` (a real implementation, useful
for tests/demos). A real Google OAuth client can be supplied behind the
``CalendarClient`` protocol without changing this source or the engine.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol, runtime_checkable

from studyguard.analytics.models import MetricPoint
from studyguard.sources.base import SourceHealth, SourceInfo, SourceStatus, register_source


@runtime_checkable
class CalendarClient(Protocol):
    """Supplies planned study events as ``(start, planned_minutes)`` pairs."""

    def planned_events(self) -> Sequence[tuple[datetime, float]]:
        """Return planned study events. Implementations must not raise here."""


class MockCalendarClient:
    """Deterministic in-memory calendar client for tests and demos."""

    def __init__(self, events: Sequence[tuple[datetime, float]] = ()) -> None:
        self._events = list(events)

    def planned_events(self) -> Sequence[tuple[datetime, float]]:
        return list(self._events)


@register_source("google_calendar")
class GoogleCalendarSource:
    """Maps planned calendar study time into ``planned_minutes`` metric points."""

    info = SourceInfo(
        key="google_calendar", title="Google Calendar", category="calendar", requires_consent=True
    )

    def __init__(self, client: CalendarClient | None = None) -> None:
        self._client: CalendarClient = client or MockCalendarClient()
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def validate(self) -> bool:
        return isinstance(self._client, CalendarClient)

    def health_check(self) -> SourceHealth:
        status = SourceStatus.CONNECTED if self._connected else SourceStatus.DISCONNECTED
        return SourceHealth(status, "calendar client ready")

    def collect(self) -> Sequence[MetricPoint]:
        if not self._connected:
            return []
        return [
            MetricPoint(start, "planned_minutes", float(minutes))
            for start, minutes in self._client.planned_events()
        ]
