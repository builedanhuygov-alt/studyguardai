"""Presence-driven study sessions and gentle alerting.

Pure, deterministic business logic kept separate from computer vision so it can
be unit-tested with a fake clock (no hidden time, no camera).

- ``SessionTracker`` turns a noisy per-frame presence signal into a stable study
  session using hysteresis (N consecutive observations) plus time thresholds, so
  a single dropped-face frame never pauses or ends a session, and a student who
  briefly looks away is not kicked out.
- ``AlertManager`` emits gentle, cooldown-limited reminders so the product feels
  helpful, not naggy: an alert fires only after a condition is *sustained* and
  never more often than the cooldown.
- ``SessionConsumer`` adapts the two to the engine's per-frame ``Snapshot``
  stream. It deduplicates repeated snapshots (the render loop may poll faster
  than inference produces frames) and returns human-readable notices.
"""
from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum

from studyguard.core import Snapshot


class SessionState(str, Enum):
    """Lifecycle of a single study session."""

    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ENDED = "ENDED"


@dataclass(frozen=True)
class SessionConfig:
    """Thresholds controlling session transitions.

    ``present_frames``/``absent_frames`` are hysteresis counts (consecutive
    observations) that debounce the raw presence signal. ``pause_after_s`` and
    ``end_after_s`` are measured from the moment confirmed absence begins.
    """

    present_frames: int = 5
    absent_frames: int = 5
    pause_after_s: float = 8.0
    end_after_s: float = 120.0

    def __post_init__(self) -> None:
        if self.present_frames < 1 or self.absent_frames < 1:
            raise ValueError("present_frames and absent_frames must be >= 1")
        if self.pause_after_s < 0.0 or self.end_after_s <= self.pause_after_s:
            raise ValueError("require 0 <= pause_after_s < end_after_s")


@dataclass(frozen=True)
class SessionEvent:
    """An immutable transition emitted by the tracker."""

    kind: str  # "started" | "paused" | "resumed" | "ended"
    at: float  # monotonic seconds
    active_seconds: float


class SessionTracker:
    """Deterministic presence -> session state machine.

    Call ``update(present, now)`` once per observation. ``now`` is supplied by
    the caller (monotonic seconds) so the tracker is fully testable.
    """

    def __init__(self, config: SessionConfig | None = None, *, max_gap_s: float = 5.0) -> None:
        self._cfg = config or SessionConfig()
        self._max_gap_s = max_gap_s
        self.reset()

    def reset(self) -> None:
        self._state = SessionState.IDLE
        self._present_streak = 0
        self._absent_streak = 0
        self._confirmed_present = False
        self._absent_since: float | None = None
        self._active_seconds = 0.0
        self._last_update: float | None = None
        self._session_start: float | None = None

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def active_seconds(self) -> float:
        return self._active_seconds

    @property
    def present(self) -> bool:
        return self._confirmed_present

    def _accumulate(self, now: float) -> None:
        # Count wall-clock time only while actively studying. Clamp large gaps
        # (app frozen / laptop asleep) so a resume does not add bogus hours.
        if self._state is SessionState.ACTIVE and self._last_update is not None:
            delta = now - self._last_update
            if 0.0 < delta <= self._max_gap_s:
                self._active_seconds += delta

    def _apply_hysteresis(self, present: bool, now: float) -> None:
        if present:
            self._present_streak += 1
            self._absent_streak = 0
        else:
            self._absent_streak += 1
            self._present_streak = 0
        if not self._confirmed_present and self._present_streak >= self._cfg.present_frames:
            self._confirmed_present = True
            self._absent_since = None
        elif self._confirmed_present and self._absent_streak >= self._cfg.absent_frames:
            self._confirmed_present = False
            self._absent_since = now

    def _transition(self, now: float) -> SessionEvent | None:
        if self._state is SessionState.IDLE:
            if self._confirmed_present:
                self._state = SessionState.ACTIVE
                self._session_start = now
                return SessionEvent("started", now, self._active_seconds)
        elif self._state is SessionState.ACTIVE:
            if not self._confirmed_present and self._absent_since is not None:
                if now - self._absent_since >= self._cfg.pause_after_s:
                    self._state = SessionState.PAUSED
                    return SessionEvent("paused", now, self._active_seconds)
        elif self._state is SessionState.PAUSED:
            if self._confirmed_present:
                self._state = SessionState.ACTIVE
                return SessionEvent("resumed", now, self._active_seconds)
            if self._absent_since is not None and now - self._absent_since >= self._cfg.end_after_s:
                self._state = SessionState.ENDED
                return SessionEvent("ended", now, self._active_seconds)
        return None

    def update(self, present: bool, now: float) -> SessionEvent | None:
        """Feed one presence observation; return a transition event or None."""
        self._accumulate(now)
        self._apply_hysteresis(present, now)
        event = self._transition(now)
        self._last_update = now
        return event


@dataclass(frozen=True)
class AlertConfig:
    """Controls how gentle the reminders are."""

    min_consecutive: int = 8
    cooldown_s: float = 45.0

    def __post_init__(self) -> None:
        if self.min_consecutive < 1:
            raise ValueError("min_consecutive must be >= 1")
        if self.cooldown_s < 0.0:
            raise ValueError("cooldown_s must be >= 0")


@dataclass(frozen=True)
class Alert:
    """An immutable, user-facing reminder."""

    kind: str
    message: str
    at: float


_DEFAULT_MESSAGES: dict[str, str] = {
    "posture": "Gentle reminder: sit up straight to protect your back.",
    "focus": "You seem distracted — take a breath and refocus.",
}


class AlertManager:
    """Emits gentle, cooldown-limited reminders per alert kind.

    A reminder fires only after its condition holds for ``min_consecutive``
    observations and never more often than ``cooldown_s`` — so the app never
    nags on a single bad frame.
    """

    def __init__(
        self,
        config: AlertConfig | None = None,
        messages: Mapping[str, str] | None = None,
    ) -> None:
        self._cfg = config or AlertConfig()
        self._messages = dict(messages) if messages else dict(_DEFAULT_MESSAGES)
        self._streak: dict[str, int] = {}
        self._last_fired: dict[str, float] = {}

    def reset(self) -> None:
        self._streak.clear()
        self._last_fired.clear()

    def update(self, kind: str, condition: bool, now: float) -> Alert | None:
        """Update one alert kind; return an Alert if a gentle reminder fires."""
        if not condition:
            self._streak[kind] = 0
            return None
        streak = self._streak.get(kind, 0) + 1
        self._streak[kind] = streak
        if streak < self._cfg.min_consecutive:
            return None
        last = self._last_fired.get(kind)
        if last is not None and now - last < self._cfg.cooldown_s:
            return None
        self._last_fired[kind] = now
        self._streak[kind] = 0
        message = self._messages.get(kind, f"Reminder: {kind}")
        return Alert(kind=kind, message=message, at=now)


class SessionConsumer:
    """Adapts per-frame ``Snapshot``s into session state + gentle notices.

    Deduplicates by ``frame_index`` (the render loop may re-observe the same
    snapshot), is thread-safe, and never raises into the caller's loop.
    """

    def __init__(
        self,
        *,
        session: SessionTracker | None = None,
        alerts: AlertManager | None = None,
        posture_alert_below: float = 55.0,
        focus_alert_below: float = 50.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._session = session or SessionTracker()
        self._alerts = alerts or AlertManager()
        self._posture_below = posture_alert_below
        self._focus_below = focus_alert_below
        self._clock = clock
        self._last_index = -1
        self._lock = threading.Lock()

    @property
    def state(self) -> SessionState:
        return self._session.state

    @property
    def active_seconds(self) -> float:
        return self._session.active_seconds

    def observe(self, snapshot: Snapshot) -> list[str]:
        """Feed one snapshot; return notices (state changes + gentle alerts)."""
        with self._lock:
            if snapshot.frame_index == self._last_index:
                return []
            self._last_index = snapshot.frame_index
            now = self._clock()
            notices: list[str] = []

            event = self._session.update(snapshot.present, now)
            if event is not None:
                notices.append(f"Session {event.kind} (active {event.active_seconds:.0f}s)")

            active = self._session.state is SessionState.ACTIVE and snapshot.present
            posture_alert = self._alerts.update("posture", active and snapshot.posture < self._posture_below, now)
            focus_alert = self._alerts.update("focus", active and snapshot.focus < self._focus_below, now)
            for alert in (posture_alert, focus_alert):
                if alert is not None:
                    notices.append(alert.message)
            return notices
