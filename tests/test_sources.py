import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from studyguard.sources import (
    ConsentError,
    ConsentStore,
    DataRights,
    DataSource,
    SourceStatus,
    available_source_keys,
    create_source,
    source_info,
)


def _seed(path: str, days: int = 2) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT,"
        " frame_index INTEGER, present INTEGER, posture REAL, focus REAL, status TEXT, distractions INTEGER)"
    )
    for day in range(days):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=day)
        for i in range(20):
            ts = (base + timedelta(seconds=i)).isoformat()
            conn.execute(
                "INSERT INTO samples (ts, frame_index, present, posture, focus, status, distractions)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, i, 1, 80.0, 70.0, "FOCUSED", 0),
            )
    conn.commit()
    conn.close()


def test_camera_source_satisfies_protocol():
    source = create_source("camera", db_path="nope.db")
    assert isinstance(source, DataSource)
    assert source_info("camera").category == "sensor"


def test_camera_source_lifecycle(tmp_path):
    db = tmp_path / "s.db"
    _seed(str(db))
    source = create_source("camera", db_path=str(db))
    assert source.health_check().status is SourceStatus.DISCONNECTED
    assert source.collect() == []  # nothing before connect
    source.connect()
    assert source.validate() is True
    assert source.health_check().status is SourceStatus.CONNECTED
    points = source.collect()
    assert any(p.metric == "focus" for p in points)
    source.disconnect()
    assert source.health_check().status is SourceStatus.DISCONNECTED


def test_registry_lists_camera():
    assert "camera" in available_source_keys()


def test_consent_required():
    consent = ConsentStore()
    with pytest.raises(ConsentError):
        consent.require("camera")
    consent.grant("camera")
    consent.require("camera")  # no error
    assert consent.has_consent("camera")
    consent.revoke("camera")
    assert not consent.has_consent("camera")


def test_data_rights_export_and_delete(tmp_path):
    db = tmp_path / "r.db"
    _seed(str(db), days=1)
    rights = DataRights(str(db))
    exported = rights.export()
    assert len(exported) == 20 and "focus" in exported[0]
    assert rights.delete_all() == 20
    assert rights.export() == []
