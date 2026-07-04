import dataclasses
import time

import numpy as np
import pytest

from studyguard.core import (
    Aggregator,
    Analysis,
    Engine,
    Snapshot,
    build_detectors,
    clear_registry,
    register_detector,
)
from studyguard.detectors import FakeDetector


def test_analysis_is_immutable():
    analysis = Analysis(name="x", present=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        analysis.present = False  # type: ignore[misc]


def test_aggregator_status_and_smoothing():
    away = Aggregator(smoothing=1.0).build(
        [Analysis(name="s", present=False, metrics={"posture": 60.0, "focus": 0.0})],
        frame_index=0, fps=0.0, elapsed_s=0.0, distractions=0,
    )
    assert away.status == "AWAY" and away.present is False
    good = Aggregator(smoothing=1.0).build(
        [Analysis(name="s", present=True, metrics={"posture": 90.0, "focus": 95.0})],
        frame_index=1, fps=0.0, elapsed_s=0.0, distractions=0,
    )
    assert good.status == "FOCUSED" and good.posture == 90.0


def test_registry_build_and_clear():
    clear_registry()
    try:

        @register_detector
        class Tmp(FakeDetector):
            """Test double."""

        built = build_detectors()
        assert len(built) == 1 and isinstance(built[0], Tmp)
    finally:
        clear_registry()


def test_engine_headless_produces_snapshots_and_persists():
    frames = [np.zeros((120, 160, 3), dtype=np.uint8) for _ in range(4)] + [None]
    stream = iter(frames)

    def read():
        return next(stream, None)

    saved: list[Snapshot] = []

    class Recorder:
        def save(self, snapshot: Snapshot) -> None:
            saved.append(snapshot)

        def close(self) -> None:
            return None

    engine = Engine(read, [FakeDetector(posture=80.0, focus=90.0)], Aggregator(),
                    repository=Recorder(), sample_every=1)
    last = None
    with engine:
        deadline = time.monotonic() + 2.0
        while engine.running and time.monotonic() < deadline:
            time.sleep(0.02)
        last = engine.latest()
    assert last is not None
    _, snapshot = last
    assert isinstance(snapshot, Snapshot) and snapshot.status == "FOCUSED"
    assert saved  # writer persisted at least one snapshot
    assert engine.error is None
