"""Privacy invariant: StudyGuard persists/logs only derived metrics, never raw
frames. This module makes the invariant explicit and checkable in tests.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass

import numpy as np

_FORBIDDEN = (np.ndarray, bytes, bytearray, memoryview)


def contains_raw_media(obj: object) -> bool:
    """True if a value (or any dataclass field) holds raw image/byte data."""
    if isinstance(obj, _FORBIDDEN):
        return True
    if is_dataclass(obj) and not isinstance(obj, type):
        return any(contains_raw_media(getattr(obj, f.name)) for f in fields(obj))
    return False


def assert_persistable(obj: object) -> None:
    """Raise if a value would persist/log raw frames (privacy invariant)."""
    if contains_raw_media(obj):
        raise ValueError("Privacy invariant violated: raw media must never be persisted or logged")
