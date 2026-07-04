"""The data-source plugin contract and registry.

Every source — camera, calendar, LMS, wearable, keyboard, manual input —
implements :class:`DataSource` and yields ``MetricPoint`` records. New sources
are added by writing one class and registering it; no existing code changes.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from studyguard.analytics.models import MetricPoint


class SourceStatus(str, Enum):
    """Connectivity state of a data source."""

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class SourceHealth:
    """Result of a source health check (never raises to the caller)."""

    status: SourceStatus
    detail: str = ""


@dataclass(frozen=True, slots=True)
class SourceInfo:
    """Static metadata describing a data source."""

    key: str
    title: str
    category: str  # "sensor" | "calendar" | "lms" | "wearable" | "manual"
    requires_consent: bool = True


@runtime_checkable
class DataSource(Protocol):
    """Common interface every data source must implement."""

    info: SourceInfo

    def connect(self) -> None:
        """Establish access to the source. Idempotent."""

    def disconnect(self) -> None:
        """Release resources. Safe to call when already disconnected."""

    def collect(self) -> Sequence[MetricPoint]:
        """Return newly available metric points (possibly empty)."""

    def validate(self) -> bool:
        """Return True if the source is configured correctly."""

    def health_check(self) -> SourceHealth:
        """Report current connectivity/health without raising."""


_SOURCE_CLASSES: dict[str, type] = {}


def register_source(key: str) -> Callable[[type], type]:
    """Class decorator registering a ``DataSource`` under ``key``."""

    def decorator(cls: type) -> type:
        _SOURCE_CLASSES[key] = cls
        return cls

    return decorator


def available_source_keys() -> tuple[str, ...]:
    """Return the keys of all registered data sources, sorted."""
    return tuple(sorted(_SOURCE_CLASSES))


def source_info(key: str) -> SourceInfo:
    """Return the :class:`SourceInfo` for a registered source key."""
    return _SOURCE_CLASSES[key].info


def create_source(key: str, **kwargs: object) -> DataSource:
    """Instantiate a registered data source, passing through keyword config."""
    if key not in _SOURCE_CLASSES:
        raise KeyError(f"Unknown data source: {key!r}")
    return _SOURCE_CLASSES[key](**kwargs)


def clear_sources() -> None:
    """Remove all registrations (test isolation)."""
    _SOURCE_CLASSES.clear()
