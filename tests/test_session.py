import pytest

from studyguard.core import Snapshot
from studyguard.session import (
    AlertConfig,
    AlertManager,
    SessionConfig,
    SessionConsumer,
    SessionState,
    SessionTracker,
)


def _snap(index: int, present: bool, posture: float = 80.0, focus: float = 90.0) -> Snapshot:
    return Snapshot(
        frame_index=index, present=present, posture=posture, focus=focus,
        status="", message="", fps=0.0, elapsed_s=0.0, distractions=0,
    )


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_requires_consecutive_presence_to_start():
    t = SessionTracker(SessionConfig(present_frames=3, absent_frames=2, pause_after_s=5, end_after_s=30))
    assert t.update(True, 0.0) is None
    assert t.update(True, 0.1) is None
    event = t.update(True, 0.2)
    assert event is not None and event.kind == "started"
    assert t.state is SessionState.ACTIVE


def test_single_absent_frame_does_not_pause():
    t = SessionTracker(SessionConfig(present_frames=1, absent_frames=3, pause_after_s=2, end_after_s=30))
    t.update(True, 0.0)
    assert t.update(False, 0.1) is None
    assert t.state is SessionState.ACTIVE


def test_pause_resume_end_flow():
    t = SessionTracker(SessionConfig(present_frames=1, absent_frames=1, pause_after_s=1.0, end_after_s=3.0))
    assert t.update(True, 0.0).kind == "started"
    assert t.update(False, 0.5) is None
    assert t.update(False, 2.0).kind == "paused"
    assert t.state is SessionState.PAUSED
    assert t.update(True, 2.5).kind == "resumed"
    assert t.state is SessionState.ACTIVE
    t.update(False, 3.0)
    t.update(False, 4.2)
    assert t.update(False, 10.0).kind == "ended"
    assert t.state is SessionState.ENDED


def test_active_seconds_excludes_paused_time():
    t = SessionTracker(
        SessionConfig(present_frames=1, absent_frames=1, pause_after_s=0.0, end_after_s=100.0),
        max_gap_s=10.0,
    )
    t.update(True, 0.0)
    t.update(True, 1.0)
    t.update(False, 2.0)
    t.update(False, 5.0)
    t.update(True, 6.0)
    t.update(True, 7.0)
    assert round(t.active_seconds, 3) == 3.0


def test_large_gap_is_clamped():
    t = SessionTracker(
        SessionConfig(present_frames=1, absent_frames=1, pause_after_s=100, end_after_s=200),
        max_gap_s=5.0,
    )
    t.update(True, 0.0)
    t.update(True, 1000.0)
    assert t.active_seconds == 0.0


def test_invalid_session_config_raises():
    with pytest.raises(ValueError):
        SessionConfig(present_frames=0)
    with pytest.raises(ValueError):
        SessionConfig(pause_after_s=10, end_after_s=5)


def test_alert_requires_sustained_condition():
    m = AlertManager(AlertConfig(min_consecutive=3, cooldown_s=10))
    assert m.update("posture", True, 0.0) is None
    assert m.update("posture", True, 0.1) is None
    alert = m.update("posture", True, 0.2)
    assert alert is not None and alert.kind == "posture"


def test_alert_resets_when_condition_clears():
    m = AlertManager(AlertConfig(min_consecutive=3, cooldown_s=10))
    m.update("posture", True, 0.0)
    m.update("posture", True, 0.1)
    m.update("posture", False, 0.2)
    assert m.update("posture", True, 0.3) is None


def test_alert_cooldown():
    m = AlertManager(AlertConfig(min_consecutive=1, cooldown_s=10))
    assert m.update("posture", True, 0.0) is not None
    assert m.update("posture", True, 1.0) is None
    assert m.update("posture", True, 11.0) is not None


def test_invalid_alert_config_raises():
    with pytest.raises(ValueError):
        AlertConfig(min_consecutive=0)
    with pytest.raises(ValueError):
        AlertConfig(cooldown_s=-1)


def test_consumer_dedupes_by_frame_index():
    clock = _Clock()
    consumer = SessionConsumer(
        session=SessionTracker(SessionConfig(present_frames=1, absent_frames=1, pause_after_s=5, end_after_s=30)),
        alerts=AlertManager(AlertConfig(min_consecutive=100, cooldown_s=1)),
        clock=clock,
    )
    notices = consumer.observe(_snap(0, True))
    assert any("started" in n for n in notices)
    assert consumer.observe(_snap(0, True)) == []
    assert consumer.state is SessionState.ACTIVE


def test_consumer_emits_gentle_posture_alert():
    clock = _Clock()
    consumer = SessionConsumer(
        session=SessionTracker(SessionConfig(present_frames=1, absent_frames=1, pause_after_s=5, end_after_s=30)),
        alerts=AlertManager(AlertConfig(min_consecutive=3, cooldown_s=10)),
        clock=clock,
        posture_alert_below=55.0,
    )
    fired = False
    for i in range(6):
        clock.t = float(i)
        notices = consumer.observe(_snap(i, True, posture=40.0))
        if any("straight" in n.lower() for n in notices):
            fired = True
    assert fired
