"""Camera data source.

The live capture path is owned by the real-time :class:`~studyguard.core.Engine`;
this provider exposes the camera's *recorded* metrics to the multi-source layer
through the common :class:`~studyguard.sources.base.DataSource` interface.
"""
from __future__ import annotations

import os
from collections.abc import Sequence

from studyguard.analytics.models import MetricPoint
from studyguard.analytics.sqlite_source import metric_points_from_sqlite
from studyguard.sources.base import SourceHealth, SourceInfo, SourceStatus, register_source


@register_source("camera")
class CameraDataSource:
    """Provides posture/focus/presence metrics recorded by the camera engine."""

    info = SourceInfo(key="camera", title="Webcam", category="sensor", requires_consent=True)

    def __init__(self, db_path: str = "studyguard.db") -> None:
        self._db_path = db_path
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def collect(self) -> Sequence[MetricPoint]:
        if not self._connected or not os.path.exists(self._db_path):
            return []
        return metric_points_from_sqlite(self._db_path)

    def validate(self) -> bool:
        # The provider is validly configured whether or not data exists yet.
        return isinstance(self._db_path, str) and bool(self._db_path)

    def health_check(self) -> SourceHealth:
        if not self._connected:
            return SourceHealth(SourceStatus.DISCONNECTED)
        if os.path.exists(self._db_path):
            return SourceHealth(SourceStatus.CONNECTED, "database reachable")
        return SourceHealth(SourceStatus.CONNECTED, "connected; no data recorded yet")
