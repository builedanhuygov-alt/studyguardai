"""Camera / video capture with a resilient, testable lifecycle.

For a live webcam, transient read failures trigger a bounded reconnect with
backoff instead of ending the study session. A ``capture_factory`` can be
injected so reconnection is unit-tested without any hardware.
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable

import cv2
import numpy as np

from studyguard.config import Config

logger = logging.getLogger(__name__)

CaptureFactory = Callable[[object], "cv2.VideoCapture"]


class Camera:
    """Opens a webcam or a video file and yields resized BGR frames."""

    def __init__(self, config: Config, *, capture_factory: CaptureFactory = cv2.VideoCapture) -> None:
        self._config = config
        self._factory = capture_factory
        self._cap: cv2.VideoCapture | None = None
        self._reconnects = 0

    @property
    def is_open(self) -> bool:
        """True if the capture device is currently open."""
        return self._cap is not None and self._cap.isOpened()

    @property
    def reconnects(self) -> int:
        """Number of successful reconnects since ``open()`` (diagnostics)."""
        return self._reconnects

    @property
    def _source(self) -> object:
        return self._config.video_path if self._config.video_path else self._config.camera_index

    def open(self) -> "Camera":
        cap = self._factory(self._source)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video source: {self._source!r}")
        self._cap = cap
        return self

    def read(self) -> np.ndarray | None:
        """Return the next processed frame, or ``None`` when the source is exhausted."""
        if self._cap is None:
            raise RuntimeError("Camera is not open; call open() before read().")
        ok, frame = self._cap.read()
        if not ok:
            frame = self._recover()
            if frame is None:
                return None
        return self._postprocess(frame)

    def _recover(self) -> np.ndarray | None:
        # Video files simply loop; live cameras attempt a bounded reconnect.
        if self._config.video_path:
            if self._cap is None:
                return None
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self._cap.read()
            return frame if ok else None
        return self._reconnect()

    def _reconnect(self) -> np.ndarray | None:
        attempts = max(0, self._config.reconnect_attempts)
        for attempt in range(1, attempts + 1):
            logger.warning("Camera read failed; reconnect attempt %d/%d", attempt, attempts)
            self.release()
            if self._config.reconnect_backoff_s > 0:
                time.sleep(self._config.reconnect_backoff_s)
            try:
                cap = self._factory(self._source)
            except Exception:
                logger.exception("Reconnect attempt %d could not construct a capture", attempt)
                continue
            if not cap.isOpened():
                continue
            self._cap = cap
            ok, frame = cap.read()
            if ok:
                self._reconnects += 1
                logger.info("Camera reconnected after %d attempt(s)", attempt)
                return frame
        logger.error("Camera reconnect failed after %d attempt(s)", attempts)
        return None

    def _postprocess(self, frame: np.ndarray) -> np.ndarray:
        if self._config.mirror and not self._config.video_path:
            frame = cv2.flip(frame, 1)
        width = self._config.frame_width
        height = int(frame.shape[0] * width / frame.shape[1])
        return cv2.resize(frame, (width, height))

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
