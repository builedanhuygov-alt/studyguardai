import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from studyguard.api import StudyGuardService
from studyguard.sources import ConsentError


def _seed(path: str, days: int = 3) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS samples (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT,"
        " frame_index INTEGER, present INTEGER, posture REAL, focus REAL, status TEXT, distractions INTEGER)"
    )
    focus_by_day = [70.0, 60.0, 50.0]
    for day in range(days):
        base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=day)
        for i in range(30):
            ts = (base + timedelta(seconds=i)).isoformat()
            conn.execute(
                "INSERT INTO samples (ts, frame_index, present, posture, focus, status, distractions)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, i, 1, 80.0, focus_by_day[day % 3], "FOCUSED", 0),
            )
    conn.commit()
    conn.close()


def _service(tmp_path):
    db = tmp_path / "api.db"
    _seed(str(db))
    service = StudyGuardService(db_path=str(db), sample_period_s=60.0)
    service.grant_consent("camera")
    service.connect_source("camera")
    return service


def test_connect_requires_consent(tmp_path):
    service = StudyGuardService(db_path=str(tmp_path / "x.db"))
    with pytest.raises(ConsentError):
        service.connect_source("camera")


def test_analytics_and_timeline(tmp_path):
    service = _service(tmp_path)
    analytics = service.get_analytics()
    assert len(analytics["days"]) == 3
    assert analytics["trends"]["focus"]["direction"] == "declining"
    assert len(service.get_timeline()) == 3
    assert len(service.get_sessions()) == 3


def test_insights_and_recommendations(tmp_path):
    service = _service(tmp_path)
    insights = service.get_insights()
    assert isinstance(insights["observations"], list)
    assert any(r["key"] == "pomodoro" for r in service.get_recommendations())


def test_report_endpoint(tmp_path):
    report = _service(tmp_path).get_report(period="week", audience="student")
    assert report["period"] == "week"
    assert report["markdown"].startswith("# Weekly study report")


def test_sources_listing_and_consent_flow(tmp_path):
    service = _service(tmp_path)
    sources = {s["key"]: s for s in service.list_sources()}
    assert sources["camera"]["connected"] is True
    assert sources["camera"]["consent"] is True


def test_export_and_delete(tmp_path):
    service = _service(tmp_path)
    assert len(service.export_data()) == 90  # 3 days x 30 rows
    assert service.delete_data() == {"deleted": 90}
    assert service.export_data() == []
