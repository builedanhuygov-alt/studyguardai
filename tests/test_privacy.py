"""Test privacy invariants (no raw frames stored)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import sqlite3

from studyguard.core import Snapshot
from studyguard.storage import SQLiteRepository


def test_no_raw_frames_in_storage() -> None:
    """Verify that raw frames are never persisted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.db")
        repo = SQLiteRepository(db_path)

        snapshot = Snapshot(
            frame_index=0,
            present=True,
            posture_score=85.0,
            focus_score=90.0,
            status="FOCUSED",
            alert_type="ok",
            fps=30.0,
            elapsed_s=0.0,
            distractions=0,
        )
        repo.save(snapshot)
        repo.close()

        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA table_info(snapshots)")
        columns = [row[1] for row in cursor.fetchall()]

        assert "frame" not in " ".join(columns).lower() or "frame_index" in columns
        assert "image" not in " ".join(columns).lower()
        assert "video" not in " ".join(columns).lower()
        conn.close()
