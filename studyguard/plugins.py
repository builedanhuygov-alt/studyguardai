"""Plugin system for detectors and data sources."""

from __future__ import annotations

from typing import Any


def load_detectors() -> list[Any]:
    """Load all registered detector plugins."""
    return []
