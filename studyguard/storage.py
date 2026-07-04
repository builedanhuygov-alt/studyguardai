"""Repository implementations (persistence seam from ADR-3)."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from studyguard.core import Snapshot
from studyguard.privacy import assert_persistable


class NullRepository:
    """No-op repository (persistence disabled)."""

    def save(self, snapshot: Snapshot) -> None:
        return None

    def close(self) -> None:
        return None


class SQLiteRepository:
    """Stores snapshots in SQLite. Demo-grade; swap for Postgres/Timescale at scale."""

    def __init__(self, path: str = "studyguard.db") -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                frame_index INTEGER NOT NULL,
                present INTEGER NOT NULL,
                posture REAL NOT NULL,
                focus REAL NOT NULL,
                status TEXT NOT NULL,
                distractions INTEGER NOT NULL
            )
            """
        )
        self._conn.commit()

    def save(self, snapshot: Snapshot) -> None:
        assert_persistable(snapshot)  # privacy invariant: metrics only, no raw frames
        self._conn.execute(
            "INSERT INTO samples (ts, frame_index, present, posture, focus, status, distractions)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                snapshot.frame_index,
                int(snapshot.present),
                float(snapshot.posture),
                float(snapshot.focus),
                snapshot.status,
                snapshot.distractions,
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.commit()
        self._conn.close()
