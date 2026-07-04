"""Desktop runtime wiring: local server + service, port selection, static SPA.

The desktop app hosts the same FastAPI transport over the same
StudyGuardService as the web dashboard, plus a small settings endpoint that
belongs to the desktop layer only. No business logic lives here.
"""
from __future__ import annotations

import socket
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent / "frontend"


def choose_free_port() -> int:
    """Return an available localhost TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def build_desktop_app(db_path: str, settings_store, *, static_dir: Path = FRONTEND_DIR):
    """Build the FastAPI app for the desktop: REST API + static SPA + settings.

    Imports FastAPI lazily so the module can be imported without the optional
    ``[desktop]`` dependencies installed.
    """
    from dataclasses import asdict

    from fastapi.staticfiles import StaticFiles

    from studyguard.api import StudyGuardService
    from studyguard.webapi.app import create_app
    import studyguard.sources  # noqa: F401  (register sources)

    service = StudyGuardService(db_path=db_path)
    service.grant_consent("camera")
    service.connect_source("camera", db_path=db_path)
    app = create_app(lambda: service)

    def get_settings() -> dict:
        return asdict(settings_store.load())

    def update_settings(payload: dict) -> dict:
        current = settings_store.load()
        for key, value in payload.items():
            if hasattr(current, key):
                setattr(current, key, value)
        settings_store.save(current)
        return asdict(current)

    app.add_api_route("/desktop/settings", get_settings, methods=["GET"], tags=["desktop"])
    app.add_api_route("/desktop/settings", update_settings, methods=["POST"], tags=["desktop"])
    app.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="app")
    return app, service


def make_server(app, host: str, port: int):
    """Create a controllable uvicorn server (run in a background thread)."""
    import uvicorn

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    return uvicorn.Server(config)
