import sqlite3

from studyguard.core import Snapshot
from studyguard.storage import SQLiteRepository


def test_sqlite_round_trip(tmp_path):
    db = tmp_path / "t.db"
    repo = SQLiteRepository(str(db))
    repo.save(Snapshot(frame_index=0, present=True, posture=88.0, focus=91.0,
                       status="FOCUSED", message="ok", fps=30.0, elapsed_s=1.0, distractions=0))
    repo.close()
    conn = sqlite3.connect(str(db))
    rows = conn.execute("SELECT posture, focus, status FROM samples").fetchall()
    conn.close()
    assert rows == [(88.0, 91.0, "FOCUSED")]
