import sqlite3
from datetime import datetime, timezone

import pytest

from studyguard.api import StudyGuardService
from studyguard.camera import Camera
from studyguard.config import Config


def _seed(path: str) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT,"
        " frame_index INTEGER, present INTEGER, posture REAL, focus REAL, status TEXT, distractions INTEGER)"
    )
    conn.execute(
        "INSERT INTO samples (ts, frame_index, present, posture, focus, status, distractions)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), 0, 1, 80.0, 90.0, "FOCUSED", 0),
    )
    conn.commit()
    conn.close()


def test_health_reports_storage_and_plugins(tmp_path):
    db = tmp_path / "h.db"
    _seed(str(db))
    service = StudyGuardService(db_path=str(db))
    service.grant_consent("camera")
    service.connect_source("camera")
    health = service.get_health()
    assert health["api"] == "ok"
    assert "camera" in health["plugins"]["registered"]
    assert "camera" in health["plugins"]["connected"]
    assert health["storage"]["status"] == "ok"
    assert health["sources"]["camera"]["status"] == "connected"


def test_health_empty_storage(tmp_path):
    service = StudyGuardService(db_path=str(tmp_path / "missing.db"))
    assert service.get_health()["storage"]["status"] == "empty"


def test_camera_read_before_open_raises():
    camera = Camera(Config())
    with pytest.raises(RuntimeError):
        camera.read()
