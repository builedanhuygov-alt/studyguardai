import pytest

from studyguard.export import available_formats, create_exporter

PAYLOAD = {
    "days": [
        {"date": "2026-01-01", "study_minutes": 60.0, "avg_focus": 80.0, "avg_posture": 85.0}
    ],
    "streak": 1,
    "markdown": "# Weekly study report\n\nhello\n",
}


def test_formats_registered():
    formats = available_formats()
    assert {"json", "csv", "markdown"} <= set(formats)


def test_json_export():
    assert '"streak": 1' in create_exporter("json").export(PAYLOAD)


def test_csv_export():
    out = create_exporter("csv").export(PAYLOAD)
    assert out.splitlines()[0].startswith("date,study_minutes,avg_focus,avg_posture")
    assert "2026-01-01" in out


def test_markdown_prefers_payload_markdown():
    assert create_exporter("markdown").export(PAYLOAD).startswith("# Weekly study report")


def test_unknown_format_raises():
    with pytest.raises(KeyError):
        create_exporter("xml")
