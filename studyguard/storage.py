"""Storage layer for persisting metrics."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteRepository:
    """SQLite-based repository for storing snapshots."""

    def __init__(self, path: str) -> None:
        """Initialize SQLite repository."""
        self.path = path
        self.conn = sqlite3.connect(path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY,
                frame_index INTEGER,
                present BOOLEAN,
                posture_score REAL,
                focus_score REAL,
                status TEXT,
                alert_type TEXT,
                fps REAL,
                elapsed_s REAL,
                distractions INTEGER
            )
        """
        )
        self.conn.commit()

    def save(self, snapshot: Any) -> None:
        """Save a snapshot to the database."""
        self.conn.execute(
            """
            INSERT INTO snapshots
            (frame_index, present, posture_score, focus_score, status, alert_type, fps, elapsed_s, distractions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot.frame_index,
                snapshot.present,
                snapshot.posture_score,
                snapshot.focus_score,
                snapshot.status,
                snapshot.alert_type,
                snapshot.fps,
                snapshot.elapsed_s,
                snapshot.distractions,
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
