"""Per-OS application data, log, and settings paths (offline-first).

Standard library only. Honors ``STUDYGUARD_HOME`` for tests/portable builds.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "StudyGuardAI"


def data_dir() -> Path:
    """Return (and create) the app data directory for the current OS."""
    override = os.environ.get("STUDYGUARD_HOME")
    if override:
        base = Path(override)
    elif sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / APP_NAME
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / APP_NAME
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        base = (Path(xdg) if xdg else Path.home() / ".local" / "share") / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def log_dir() -> Path:
    """Return (and create) the log directory."""
    path = data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> str:
    """Return the SQLite database path inside the app data directory."""
    return str(data_dir() / "studyguard.db")


def settings_path() -> Path:
    """Return the settings.json path."""
    return data_dir() / "settings.json"
