"""Consent and personal-data rights (privacy-first).

No integration is active without explicit consent. Users can revoke consent,
delete imported data, and export their data. Stored personal information is
minimized — only derived metrics live in the database.
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field


class ConsentError(RuntimeError):
    """Raised when an action needs consent that has not been granted."""


@dataclass
class ConsentStore:
    """In-memory record of which sources the user has consented to.

    Intentionally simple and swappable; a persistent implementation can adopt
    the same interface without affecting callers.
    """

    _granted: set[str] = field(default_factory=set)

    def grant(self, source_key: str) -> None:
        """Record explicit consent for a source."""
        self._granted.add(source_key)

    def revoke(self, source_key: str) -> None:
        """Withdraw consent for a source (safe if not granted)."""
        self._granted.discard(source_key)

    def has_consent(self, source_key: str) -> bool:
        """Return True if consent is currently granted."""
        return source_key in self._granted

    def granted(self) -> tuple[str, ...]:
        """Return all consented source keys, sorted."""
        return tuple(sorted(self._granted))

    def require(self, source_key: str) -> None:
        """Raise :class:`ConsentError` unless consent has been granted."""
        if source_key not in self._granted:
            raise ConsentError(f"No consent granted for source {source_key!r}")


class DataRights:
    """Export and deletion of the user's locally stored metrics (GDPR-style)."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def export(self) -> list[dict]:
        """Return all stored samples as plain dicts (JSON-serializable)."""
        if not os.path.exists(self._db_path):
            return []
        connection = sqlite3.connect(self._db_path)
        try:
            columns = [row[1] for row in connection.execute("PRAGMA table_info(samples)")]
            rows = connection.execute("SELECT * FROM samples").fetchall()
        finally:
            connection.close()
        return [dict(zip(columns, row, strict=False)) for row in rows]

    def delete_all(self) -> int:
        """Delete all stored samples; return the number removed."""
        if not os.path.exists(self._db_path):
            return 0
        connection = sqlite3.connect(self._db_path)
        try:
            removed = connection.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
            connection.execute("DELETE FROM samples")
            connection.commit()
        finally:
            connection.close()
        return int(removed)
