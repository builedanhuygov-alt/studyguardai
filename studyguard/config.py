"""Configuration management.

Precedence (low -> high): dataclass defaults < TOML file < environment
variables < explicit CLI arguments. Standard library only (``tomllib``).

Example ``studyguard.toml``::

    [studyguard]
    frame_width = 800
    posture_alert_below = 60.0

Environment overrides use the ``STUDYGUARD_`` prefix, e.g.
``STUDYGUARD_FRAME_WIDTH=800``.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, fields
from typing import Any

_ENV_PREFIX = "STUDYGUARD_"


@dataclass
class Config:
    """Typed application configuration."""

    camera_index: int = 0
    video_path: str | None = None
    frame_width: int = 640
    mirror: bool = True
    reconnect_attempts: int = 3
    reconnect_backoff_s: float = 0.5
    smoothing: float = 0.3
    posture_alert_below: float = 55.0
    focus_alert_below: float = 50.0
    sample_every: int = 5
    db_path: str = "studyguard.db"
    persist: bool = True
    headless: bool = False
    use_fake: bool = False
    window_name: str = "StudyGuard AI"
    log_level: str = "INFO"
    log_file: str | None = None

    @classmethod
    def load(cls, path: str | None = None, *, env: dict[str, str] | None = None) -> "Config":
        """Build a Config from an optional TOML file plus environment overrides."""
        environ = os.environ if env is None else env
        valid = {f.name: f for f in fields(cls)}
        data: dict[str, Any] = {}

        candidate = path or environ.get(_ENV_PREFIX + "CONFIG") or "studyguard.toml"
        if os.path.exists(candidate):
            with open(candidate, "rb") as handle:
                loaded = tomllib.load(handle)
            section = loaded.get("studyguard", loaded)
            data.update({k: v for k, v in section.items() if k in valid})

        for name, spec in valid.items():
            raw = environ.get(_ENV_PREFIX + name.upper())
            if raw is not None:
                data[name] = _coerce(spec.type, raw)
        return cls(**data)

    def merged(self, **overrides: Any) -> "Config":
        """Return a copy with the given non-None overrides applied."""
        current = {f.name: getattr(self, f.name) for f in fields(self)}
        current.update({k: v for k, v in overrides.items() if v is not None})
        return Config(**current)


def _coerce(type_hint: Any, raw: str) -> Any:
    text = str(type_hint)
    if "bool" in text:
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    if "int" in text:
        return int(raw)
    if "float" in text:
        return float(raw)
    return raw
