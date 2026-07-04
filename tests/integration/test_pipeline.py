"""Integration test: engine -> detector -> aggregator -> SQLite, end to end."""
from __future__ import annotations

import sqlite3
import time

import numpy as np

from studyguard.core import Aggregator, Engine
from studyguard.detectors import FakeDetector
from studyguard.storage import SQLiteRepository


def test_engine_persists_to_sqlite(tmp_path):
    frames = [np.zeros((120, 160, 3), dtype=np.uint8) for _ in range(6)] + [None]
    stream = iter(frames)
    db = tmp_path / "it.db"
    repo = SQLiteRepository(str(db))
    engine = Engine(
        lambda: next(stream, None),
        [FakeDetector(posture=70.0, focus=80.0)],
        Aggregator(),
        repository=repo,
        sample_every=1,
    )
    with engine:
        deadline = time.monotonic() + 3.0
        while engine.running and time.monotonic() < deadline:
            time.sleep(0.02)

    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    conn.close()
    assert count >= 1
    assert engine.error is None
