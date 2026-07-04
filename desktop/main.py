"""StudyGuard AI desktop entry point.

Starts the local API+SPA server and the camera engine in the background, then
opens a native window (pywebview) with a system tray icon. All heavy/optional
imports are deferred so this module imports cleanly for tests and packaging.
"""
from __future__ import annotations

import logging
import sys
import threading
import time

from desktop import paths, runtime
from desktop.settings import SettingsStore

logger = logging.getLogger(__name__)


def _setup_logging() -> None:
    log_file = paths.log_dir() / "studyguard.log"
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def _install_crash_handler() -> None:
    def hook(exc_type, exc, tb):
        logging.getLogger(__name__).critical("Unhandled error", exc_info=(exc_type, exc, tb))
        _show_error(f"StudyGuard AI hit an unexpected error:\n\n{exc}")
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = hook


def _show_error(message: str) -> None:
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, message, "StudyGuard AI", 0x10)  # type: ignore[attr-defined]
    except Exception:
        print(message, file=sys.stderr)


def _start_camera_engine(db_path: str, camera_index: int) -> None:
    """Best-effort: run the headless camera engine writing to the app database."""
    try:
        from studyguard.cli import build_engine
        from studyguard.config import Config

        config = Config(camera_index=camera_index, db_path=db_path, headless=True, persist=True)
        camera, engine = build_engine(config)
        engine.start()
        logger.info("Camera engine started")
    except Exception:
        logger.exception("Camera engine unavailable; dashboard will show existing data only")


def _build_tray(on_open, on_quit):
    import pystray
    from PIL import Image

    from desktop.assets import ICON_PATH

    image = Image.open(ICON_PATH)
    menu = pystray.Menu(
        pystray.MenuItem("Open StudyGuard", lambda *_: on_open()),
        pystray.MenuItem("Quit", lambda *_: on_quit()),
    )
    return pystray.Icon("studyguard", image, "StudyGuard AI", menu)


def main() -> None:  # pragma: no cover - GUI entry (requires desktop deps + display)
    import logging.handlers  # noqa: F401  (used by _setup_logging)

    _setup_logging()
    _install_crash_handler()
    logger.info("Starting StudyGuard AI desktop")

    store = SettingsStore(paths.settings_path())
    settings = store.load()
    db_path = paths.db_path()

    threading.Thread(target=_start_camera_engine, args=(db_path, settings.camera_index), daemon=True).start()

    app, _service = runtime.build_desktop_app(db_path, store)
    port = runtime.choose_free_port()
    server = runtime.make_server(app, "127.0.0.1", port)
    threading.Thread(target=server.run, daemon=True).start()
    _wait_for_server(port)

    import webview

    url = f"http://127.0.0.1:{port}/app/index.html"
    window = webview.create_window(
        "StudyGuard AI",
        url,
        width=settings.window_width,
        height=settings.window_height,
    )

    def on_closed() -> None:
        current = store.load()
        store.save(current)
        logger.info("Window closed; settings saved")

    window.events.closed += on_closed
    webview.start()


def _wait_for_server(port: int, timeout: float = 10.0) -> None:
    import urllib.request

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics", timeout=0.5)
            return
        except Exception:
            time.sleep(0.2)
    logger.warning("Server did not report ready within %.1fs", timeout)


if __name__ == "__main__":
    main()
