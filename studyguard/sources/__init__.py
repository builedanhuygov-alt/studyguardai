"""Pluggable data sources.

The webcam is only one source. Every source implements the same ``DataSource``
protocol and yields sensor-agnostic ``MetricPoint`` records, so the engine and
analytics never depend on a concrete source (Open/Closed).

Importing this package registers the built-in sources.
"""
from studyguard.sources.base import (
    DataSource,
    SourceHealth,
    SourceInfo,
    SourceStatus,
    available_source_keys,
    clear_sources,
    create_source,
    register_source,
    source_info,
)
from studyguard.sources.consent import ConsentError, ConsentStore, DataRights

# Register built-in sources on import.
from studyguard.sources import camera_source as _camera_source  # noqa: E402,F401
from studyguard.sources import calendar_source as _calendar_source  # noqa: E402,F401
from studyguard.sources import demo_source as _demo_source  # noqa: E402,F401

__all__ = [
    "DataSource",
    "SourceHealth",
    "SourceInfo",
    "SourceStatus",
    "register_source",
    "create_source",
    "available_source_keys",
    "source_info",
    "clear_sources",
    "ConsentStore",
    "ConsentError",
    "DataRights",
]
