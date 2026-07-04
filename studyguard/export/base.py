"""Exporter protocol and registry."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol, runtime_checkable


@runtime_checkable
class Exporter(Protocol):
    """Serializes a payload dict to a string in a specific format."""

    format: str

    def export(self, payload: Mapping[str, object]) -> str:
        """Return the payload serialized in this exporter's format."""


_EXPORTERS: dict[str, type] = {}


def register_exporter(fmt: str) -> Callable[[type], type]:
    """Class decorator registering an exporter for ``fmt``."""

    def decorator(cls: type) -> type:
        _EXPORTERS[fmt] = cls
        return cls

    return decorator


def available_formats() -> tuple[str, ...]:
    """Return all registered export formats, sorted."""
    return tuple(sorted(_EXPORTERS))


def create_exporter(fmt: str) -> Exporter:
    """Instantiate an exporter for ``fmt``."""
    if fmt not in _EXPORTERS:
        raise KeyError(f"Unknown export format: {fmt!r} (available: {available_formats()})")
    return _EXPORTERS[fmt]()
