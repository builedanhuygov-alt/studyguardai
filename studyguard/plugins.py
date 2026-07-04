"""Detector plugin loading.

Built-in detectors register themselves via ``@register_detector`` at import
time. Third-party packages can add detectors without modifying this repository
by exposing an entry point in the ``studyguard.detectors`` group::

    [project.entry-points."studyguard.detectors"]
    my_detector = "my_package.module:MyDetector"

Importing the entry point triggers its ``@register_detector`` decorator.
"""
from __future__ import annotations

import importlib
import importlib.metadata as metadata
import logging

from studyguard.core import Detector, build_detectors

logger = logging.getLogger(__name__)

_BUILTIN_MODULES = ("studyguard.detectors",)
ENTRY_POINT_GROUP = "studyguard.detectors"


def load_detectors(*, use_fake: bool = False) -> list[Detector]:
    """Return the active detector instances.

    ``use_fake=True`` returns a single deterministic ``FakeDetector`` (useful for
    demos, CI, and machines without a camera). Otherwise built-in and
    entry-point detectors are discovered and instantiated.
    """
    if use_fake:
        from studyguard.detectors import FakeDetector

        return [FakeDetector()]

    for module in _BUILTIN_MODULES:
        importlib.import_module(module)
    _load_entry_point_plugins()

    detectors = build_detectors()
    if not detectors:
        logger.warning("No detectors registered; falling back to FakeDetector")
        from studyguard.detectors import FakeDetector

        return [FakeDetector()]
    return detectors


def _load_entry_point_plugins() -> None:
    try:
        entry_points = metadata.entry_points(group=ENTRY_POINT_GROUP)
    except TypeError:  # pragma: no cover - Python < 3.10 compatibility
        entry_points = metadata.entry_points().get(ENTRY_POINT_GROUP, [])  # type: ignore[attr-defined]
    for entry_point in entry_points:
        try:
            entry_point.load()
        except Exception:  # a broken third-party plugin must not crash startup
            logger.exception("Failed to load detector plugin %r", entry_point.name)
