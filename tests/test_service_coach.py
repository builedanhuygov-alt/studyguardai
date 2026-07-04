import sqlite3
from datetime import datetime, timedelta, timezone

from studyguard.api import StudyGuardService


def _seed(path, days=3):
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT,"
        " frame_index INTEGER, present INTEGER, posture REAL, focus REAL, status TEXT, distractions INTEGER)"
    )
    focus_by_day = [50.0, 60.0, 72.0]
    for day in range(days):
        base = datetime(2026, 1, 1, 19, 0, tzinfo=timezone.utc) + timedelta(days=day)
        for minute in range(60):
            ts = (base + timedelta(seconds=minute * 60)).isoformat()
            conn.execute(
                "INSERT INTO samples (ts, frame_index, present, posture, focus, status, distractions)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, minute, 1, 80.0, focus_by_day[day % 3], "FOCUSED", 0),
            )
    conn.commit()
    conn.close()


def _service(tmp_path):
    db = tmp_path / "c.db"
    _seed(str(db))
    service = StudyGuardService(db_path=str(db), sample_period_s=60.0)
    service.grant_consent("camera")
    service.connect_source("camera")
    return service


def test_get_coach(tmp_path):
    coach = _service(tmp_path).get_coach()
    assert any(m["key"] == "focus_vs_prev_day" for m in coach)
    assert all("confidence" in m and "evidence" in m for m in coach)


def test_get_goals(tmp_path):
    goals = _service(tmp_path).get_goals()
    assert goals["level"] >= 1
    assert goals["daily_goal"]["period"] == "daily"
    assert isinstance(goals["achievements"], list)


def test_export(tmp_path):
    service = _service(tmp_path)
    assert '"days"' in service.export("json")["content"]
    assert service.export("csv")["content"].splitlines()[0].startswith("date,")
    assert "markdown" in service.export_formats()
