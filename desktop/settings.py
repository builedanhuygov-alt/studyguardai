"""Local desktop settings (remember last session, window size, theme).

Robust to a missing or corrupt file (falls back to defaults). Standard library
only; persisted as JSON in the app data directory.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """User-facing desktop preferences."""

    last_page: str = "Overview"
    window_width: int = 1200
    window_height: int = 800
    theme: str = "Dark"
    camera_index: int = 0
    start_minimized: bool = False
    enable_coach: bool = True


class SettingsStore:
    """Loads/saves :class:`Settings` as JSON."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def load(self) -> Settings:
        """Return stored settings, or defaults if missing/corrupt."""
        if not self._path.exists():
            return Settings()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("Could not read settings at %s; using defaults", self._path)
            return Settings()
        allowed = Settings().__dict__
        clean = {key: data[key] for key in allowed if key in data}
        return Settings(**clean)

    def save(self, settings: Settings) -> None:
        """Persist settings atomically."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
        tmp.replace(self._path)
