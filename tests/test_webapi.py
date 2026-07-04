import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from studyguard.demo import build_demo_service  # noqa: E402
from studyguard.webapi.app import create_app  # noqa: E402


def _client() -> TestClient:
    service = build_demo_service(days=6)
    return TestClient(create_app(lambda: service))


def test_health():
    response = _client().get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["api"] == "ok"


def test_analytics_and_pagination():
    client = _client()
    assert client.get("/api/v1/analytics").status_code == 200
    paged = client.get("/api/v1/timeline?limit=2")
    assert paged.status_code == 200
    assert len(paged.json()) <= 2


def test_goals_and_coach_typed():
    client = _client()
    assert client.get("/api/v1/goals").json()["level"] >= 1
    assert isinstance(client.get("/api/v1/coach").json(), list)


def test_openapi_and_metrics():
    client = _client()
    assert "paths" in client.get("/openapi.json").json()
    client.get("/api/v1/health")
    assert client.get("/metrics").json()["requests"] >= 1


def test_invalid_report_period_returns_400():
    assert _client().get("/api/v1/reports?period=decade").status_code == 400
