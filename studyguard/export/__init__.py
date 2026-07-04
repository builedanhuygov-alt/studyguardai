"""Report/analytics exporters (Strategy + plugin registry).

Built-in formats: JSON, CSV, Markdown. Register a new format with
``@register_exporter`` — no changes to callers.
"""
from studyguard.export.base import (
    Exporter,
    available_formats,
    create_exporter,
    register_exporter,
)
from studyguard.export import exporters as _exporters  # noqa: E402,F401  (registers built-ins)

__all__ = ["Exporter", "register_exporter", "create_exporter", "available_formats"]
