"""Command-line entry point and composition root (dependency injection).

All wiring lives here: configuration is resolved, collaborators are constructed
and injected into the :class:`~studyguard.core.Engine`, and the render loop runs.
Heavy imports (OpenCV) are deferred so ``--help`` and unit tests stay light.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time

from studyguard.config import Config
from studyguard.core import Aggregator, Engine
from studyguard.logging_conf import setup_logging
from studyguard.plugins import load_detectors
from studyguard.session import SessionConsumer
from studyguard.storage import NullRepository, SQLiteRepository

logger = logging.getLogger(__name__)


def _parse_overrides(argv: list[str] | None = None) -> tuple[str | None, dict]:
    parser = argparse.ArgumentParser(
        prog="studyguard",
        description="Privacy-first webcam study coach (posture, focus, sessions).",
    )
    parser.add_argument("--config", default=None, help="path to a TOML config file")
    parser.add_argument("--camera", type=int, default=None, dest="camera_index")
    parser.add_argument("--video", type=str, default=None, dest="video_path")
    parser.add_argument("--width", type=int, default=None, dest="frame_width")
    parser.add_argument("--no-mirror", action="store_true", default=None)
    parser.add_argument("--fake", action="store_true", default=None, dest="use_fake")
    parser.add_argument("--headless", action="store_true", default=None)
    parser.add_argument("--no-save", action="store_true", default=None)
    parser.add_argument("--db", type=str, default=None, dest="db_path")
    parser.add_argument("--log-level", type=str, default=None, dest="log_level")
    args = parser.parse_args(argv)

    overrides = {
        "camera_index": args.camera_index,
        "video_path": args.video_path,
        "frame_width": args.frame_width,
        "use_fake": args.use_fake,
        "headless": args.headless,
        "db_path": args.db_path,
        "log_level": args.log_level,
    }
    if args.no_mirror:
        overrides["mirror"] = False
    if args.no_save:
        overrides["persist"] = False
    return args.config, overrides


def build_engine(config: Config):
    """Construct and inject all collaborators. Returns (camera, engine)."""
    from studyguard.camera import Camera  # deferred: pulls in OpenCV

    camera = Camera(config).open()
    detectors = load_detectors(use_fake=config.use_fake)
    aggregator = Aggregator(
        smoothing=config.smoothing,
        posture_alert_below=config.posture_alert_below,
        focus_alert_below=config.focus_alert_below,
    )
    repository = SQLiteRepository(config.db_path) if config.persist else NullRepository()
    engine = Engine(
        camera.read,
        detectors,
        aggregator,
        repository=repository,
        sample_every=config.sample_every,
    )
    logger.info("Engine ready with detectors: %s", [type(d).__name__ for d in detectors])
    return camera, engine


def run(config: Config) -> None:
    """Run the capture/render loop until the user quits or the source ends."""
    import cv2

    from studyguard.hud import draw_hud

    setup_logging(config.log_level, config.log_file)
    try:
        camera, engine = build_engine(config)
    except RuntimeError as exc:
        logger.error("%s", exc)
        print(f"[StudyGuard] {exc}")
        print("[StudyGuard] Try --camera 1, --video clip.mp4, or --fake.")
        return

    consumer = SessionConsumer(
        posture_alert_below=config.posture_alert_below,
        focus_alert_below=config.focus_alert_below,
    )
    print("[StudyGuard] Running. Press 'q' or ESC to quit.")
    try:
        with engine:
            while engine.running:
                latest = engine.latest()
                if latest is not None:
                    frame, snapshot = latest
                    for notice in consumer.observe(snapshot):
                        print(f"[StudyGuard] {notice}")
                    if not config.headless:
                        cv2.imshow(config.window_name, draw_hud(frame, snapshot))
                        if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                            break
                if config.headless:
                    time.sleep(0.05)
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in {"demo", "present"}:
        from studyguard.demo_mode import run_demo

        run_demo(present=(args[0] == "present"), cycles=(0 if args[0] == "present" else 1))
        return
    config_path, overrides = _parse_overrides(args)
    config = Config.load(config_path).merged(**overrides)
    run(config)


if __name__ == "__main__":
    main()
