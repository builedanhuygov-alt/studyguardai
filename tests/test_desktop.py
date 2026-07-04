import os

import pytest

from desktop import paths, runtime
from desktop.settings import Settings, SettingsStore


def test_paths_use_override(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDYGUARD_HOME", str(tmp_path))
    assert paths.data_dir() == tmp_path
    assert paths.log_dir().exists()
    assert paths.db_path().endswith("studyguard.db")
    assert paths.settings_path().name == "settings.json"


def test_settings_roundtrip(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    assert store.load() == Settings()  # defaults when missing
    store.save(Settings(last_page="Analytics", window_width=1440, theme="Light"))
    loaded = store.load()
    assert loaded.last_page == "Analytics"
    assert loaded.window_width == 1440
    assert loaded.theme == "Light"


def test_settings_corrupt_file_falls_back(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text("not json", encoding="utf-8")
    assert SettingsStore(path).load() == Settings()


def test_choose_free_port_is_bindable():
    import socket

    port = runtime.choose_free_port()
    assert 1024 < port < 65536
    with socket.socket() as s:
        s.bind(("127.0.0.1", port))  # should be free right after selection


def test_build_desktop_app_if_fastapi_available(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    monkeypatch.setenv("STUDYGUARD_HOME", str(tmp_path))
    store = SettingsStore(paths.settings_path())
    app, service = runtime.build_desktop_app(paths.db_path(), store)
    routes = {getattr(r, "path", "") for r in app.routes}
    assert "/api/v1/health" in routes
    assert any(r.startswith("/desktop/settings") for r in routes)
    assert service is not None
