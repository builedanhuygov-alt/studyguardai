import sqlite3

import numpy as np
import pytest

from studyguard.core import Analysis, Snapshot
from studyguard.privacy import assert_persistable, contains_raw_media
from studyguard.storage import SQLiteRepository


def test_result_types_carry_no_raw_media():
    snapshot = Snapshot(0, True, 80.0, 90.0, "FOCUSED", "ok", 30.0, 1.0, 0)
    analysis = Analysis(name="s", present=True, metrics={"posture": 80.0})
    assert not contains_raw_media(snapshot)
    assert not contains_raw_media(analysis)
    assert_persistable(snapshot)  # must not raise


def test_guard_detects_raw_frames():
    assert contains_raw_media(np.zeros((2, 2, 3), dtype=np.uint8))
    with pytest.raises(ValueError):
        assert_persistable(np.zeros((2, 2), dtype=np.uint8))


def test_sqlite_schema_has_no_blob(tmp_path):
    repo = SQLiteRepository(str(tmp_path / "p.db"))
    repo.close()
    conn = sqlite3.connect(str(tmp_path / "p.db"))
    columns = conn.execute("PRAGMA table_info(samples)").fetchall()
    conn.close()
    assert "BLOB" not in {col[2].upper() for col in columns}
