"""Core contracts + Engine for StudyGuard.

- Detector.analyze(frame) -> Analysis   (stateless; immutable result)
- Aggregator smooths raw analyses into an immutable Snapshot for the HUD
- Repository.save(snapshot) persists results (impl in storage.py)
- Engine runs capture + inference on background threads (newest-frame-wins),
  is headless-capable, and never blocks capture on inference or persistence.
"""
from __future__ import annotations

import logging
import queue
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Protocol, runtime_checkable

import numpy as np

from studyguard.heuristics import clamp

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Analysis:
    """Immutable per-detector result for a single frame."""

    name: str
    present: bool
    metrics: Mapping[str, float] = field(default_factory=dict)
    face_box: tuple[int, int, int, int] | None = None


@dataclass(frozen=True, slots=True)
class Snapshot:
    """Immutable, render-ready aggregate of all detectors for one frame."""

    frame_index: int
    present: bool
    posture: float
    focus: float
    status: str
    message: str
    fps: float
    elapsed_s: float
    distractions: int
    face_box: tuple[int, int, int, int] | None = None


@runtime_checkable
class Detector(Protocol):
    """Stateless per-frame analyzer."""

    name: str

    def analyze(self, frame: np.ndarray) -> Analysis:
        """Return an immutable Analysis for one BGR frame."""


@runtime_checkable
class Repository(Protocol):
    """Persistence seam — SQLite for demo, Postgres/Timescale for scale."""

    def save(self, snapshot: Snapshot) -> None:
        """Persist one snapshot."""

    def close(self) -> None:
        """Flush and release resources."""


_REGISTRY: list[type] = []


def register_detector(cls: type) -> type:
    """Class decorator: register a detector so the app finds it without edits."""
    if cls not in _REGISTRY:
        _REGISTRY.append(cls)
    return cls


def build_detectors() -> list[Detector]:
    """Instantiate all registered detectors (zero-arg constructors)."""
    return [cls() for cls in _REGISTRY]


def clear_registry() -> None:
    """Remove all registrations (test isolation)."""
    _REGISTRY.clear()


class Aggregator:
    """Smooths raw detector metrics and derives an immutable Snapshot.

    Smoothing state lives here (not in detectors), so detectors stay pure.
    """

    def __init__(
        self,
        smoothing: float = 0.3,
        posture_alert_below: float = 55.0,
        focus_alert_below: float = 50.0,
    ) -> None:
        self._alpha = smoothing
        self._posture_alert = posture_alert_below
        self._focus_alert = focus_alert_below
        self._ema: dict[str, float] = {}

    def reset(self) -> None:
        self._ema.clear()

    def _smooth(self, key: str, value: float) -> float:
        prev = self._ema.get(key)
        current = value if prev is None else prev + (value - prev) * self._alpha
        self._ema[key] = current
        return current

    @staticmethod
    def _avg(analyses: Sequence[Analysis], key: str, default: float) -> float:
        values = [a.metrics[key] for a in analyses if key in a.metrics]
        return sum(values) / len(values) if values else default

    def build(
        self,
        analyses: Sequence[Analysis],
        *,
        frame_index: int,
        fps: float,
        elapsed_s: float,
        distractions: int,
    ) -> Snapshot:
        present = any(a.present for a in analyses)
        posture = clamp(self._smooth("posture", self._avg(analyses, "posture", 60.0)))
        focus = clamp(self._smooth("focus", self._avg(analyses, "focus", 0.0 if not present else 100.0)))
        face_box = next((a.face_box for a in analyses if a.face_box is not None), None)
        if not present:
            status, message = "AWAY", "No face detected"
        elif focus < self._focus_alert:
            status, message = "DISTRACTED", "Eyes on the screen!"
        elif posture < self._posture_alert:
            status, message = "SLOUCHING", "Sit up straight"
        else:
            status, message = "FOCUSED", "Great posture and focus"
        return Snapshot(
            frame_index=frame_index,
            present=present,
            posture=posture,
            focus=focus,
            status=status,
            message=message,
            fps=fps,
            elapsed_s=elapsed_s,
            distractions=distractions,
            face_box=face_box,
        )


FrameReader = Callable[[], "np.ndarray | None"]


class Engine:
    """Capture + inference on background threads; headless-capable.

    capture thread  -> newest-frame-wins queue -> worker thread (detectors +
    aggregator) -> latest Snapshot; an optional writer thread persists snapshots
    without blocking capture. The main thread calls ``latest()`` to render.
    """

    def __init__(
        self,
        read_frame: FrameReader,
        detectors: Sequence[Detector],
        aggregator: Aggregator,
        *,
        repository: Repository | None = None,
        sample_every: int = 5,
        poll_timeout: float = 0.5,
    ) -> None:
        self._read_frame = read_frame
        self._detectors = list(detectors)
        self._aggregator = aggregator
        self._repository = repository
        self._sample_every = max(1, sample_every)
        self._poll_timeout = poll_timeout

        self._frames: queue.Queue = queue.Queue(maxsize=1)
        self._writes: queue.Queue = queue.Queue(maxsize=256)
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._capture_t: threading.Thread | None = None
        self._worker_t: threading.Thread | None = None
        self._capture_done = threading.Event()

        self._lock = threading.Lock()
        self._latest: Snapshot | None = None
        self._latest_frame: np.ndarray | None = None

        self._start_time = 0.0
        self._last_fps_ts: float | None = None
        self._fps = 0.0
        self._frame_index = 0
        self._distractions = 0
        self._was_distracted = False
        self._error: BaseException | None = None

    def start(self) -> None:
        if self._threads:
            return
        self._stop.clear()
        self._capture_done.clear()
        self._start_time = time.monotonic()
        self._capture_t = threading.Thread(target=self._capture_loop, name="sg-capture", daemon=True)
        self._worker_t = threading.Thread(target=self._worker_loop, name="sg-worker", daemon=True)
        self._threads = [self._capture_t, self._worker_t]
        if self._repository is not None:
            self._threads.append(threading.Thread(target=self._writer_loop, name="sg-writer", daemon=True))
        for thread in self._threads:
            thread.start()

    def stop(self, join_timeout: float = 2.0) -> None:
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=join_timeout)
        self._threads = []
        if self._repository is not None:
            self._drain_writes()
            self._safe_close()

    def __enter__(self) -> "Engine":
        self.start()
        return self

    def __exit__(self, *exc: object) -> bool:
        self.stop()
        return False

    @property
    def running(self) -> bool:
        capture_alive = self._capture_t is not None and self._capture_t.is_alive()
        worker_alive = self._worker_t is not None and self._worker_t.is_alive()
        return capture_alive or worker_alive

    @property
    def error(self) -> BaseException | None:
        return self._error

    def latest(self) -> tuple[np.ndarray, Snapshot] | None:
        with self._lock:
            if self._latest is None or self._latest_frame is None:
                return None
            return self._latest_frame, self._latest

    def _capture_loop(self) -> None:
        try:
            while not self._stop.is_set():
                frame = self._read_frame()
                if frame is None:
                    break
                self._offer(frame)
        except Exception as exc:
            self._error = exc
            logger.exception("Capture failed")
        finally:
            self._capture_done.set()
            try:
                self._frames.put_nowait(None)
            except queue.Full:
                logger.debug("Pending frame present; worker will drain then stop")

    def _offer(self, frame: np.ndarray) -> None:
        try:
            self._frames.put_nowait(frame)
        except queue.Full:
            try:
                self._frames.get_nowait()
            except queue.Empty:
                logger.debug("Input queue drained concurrently")
            try:
                self._frames.put_nowait(frame)
            except queue.Full:
                logger.debug("Dropped newest frame under load")

    def _worker_loop(self) -> None:
        try:
            while not self._stop.is_set():
                try:
                    frame = self._frames.get(timeout=self._poll_timeout)
                except queue.Empty:
                    if self._capture_done.is_set():
                        break
                    continue
                if frame is None:
                    break
                snapshot = self._process(frame)
                with self._lock:
                    self._latest = snapshot
                    self._latest_frame = frame
                self._enqueue_write(snapshot)
        except Exception as exc:
            self._error = exc
            logger.exception("Worker failed")

    def _process(self, frame: np.ndarray) -> Snapshot:
        analyses: list[Analysis] = []
        for detector in self._detectors:
            name = getattr(detector, "name", detector.__class__.__name__)
            try:
                analyses.append(detector.analyze(frame))
            except Exception:
                logger.exception("Detector %r failed", name)
                analyses.append(Analysis(name=name, present=False))
        now = time.monotonic()
        fps = self._tick_fps(now)
        index = self._frame_index
        self._frame_index += 1
        snapshot = self._aggregator.build(
            analyses,
            frame_index=index,
            fps=fps,
            elapsed_s=now - self._start_time,
            distractions=self._distractions,
        )
        if snapshot.status == "DISTRACTED" and not self._was_distracted:
            self._distractions += 1
            snapshot = replace(snapshot, distractions=self._distractions)
        self._was_distracted = snapshot.status == "DISTRACTED"
        return snapshot

    def _tick_fps(self, now: float) -> float:
        if self._last_fps_ts is not None:
            dt = now - self._last_fps_ts
            if dt > 0:
                inst = 1.0 / dt
                self._fps = inst if self._fps == 0.0 else self._fps * 0.9 + inst * 0.1
        self._last_fps_ts = now
        return self._fps

    def _enqueue_write(self, snapshot: Snapshot) -> None:
        if self._repository is None or snapshot.frame_index % self._sample_every != 0:
            return
        try:
            self._writes.put_nowait(snapshot)
        except queue.Full:
            logger.debug("Dropped snapshot write under load")

    def _writer_loop(self) -> None:
        while not self._stop.is_set():
            try:
                snapshot = self._writes.get(timeout=self._poll_timeout)
            except queue.Empty:
                continue
            self._safe_save(snapshot)

    def _drain_writes(self) -> None:
        while True:
            try:
                snapshot = self._writes.get_nowait()
            except queue.Empty:
                return
            self._safe_save(snapshot)

    def _safe_save(self, snapshot: Snapshot) -> None:
        assert self._repository is not None
        try:
            self._repository.save(snapshot)
        except Exception:
            logger.exception("Repository.save failed")

    def _safe_close(self) -> None:
        assert self._repository is not None
        try:
            self._repository.close()
        except Exception:
            logger.exception("Repository.close failed")
