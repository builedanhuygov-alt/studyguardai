"""Mock-based test: the engine persists through the Repository abstraction."""
from __future__ import annotations

import time
from unittest.mock import MagicMock

import numpy as np

from studyguard.core import Aggregator, Engine
from studyguard.detectors import FakeDetector


def test_engine_uses_repository_and_closes_it():
    frames = [np.zeros((64, 64, 3), dtype=np.uint8) for _ in range(3)] + [None]
    stream = iter(frames)
    repo = MagicMock()
    engine = Engine(
        lambda: next(stream, None),
        [FakeDetector()],
        Aggregator(),
        repository=repo,
        sample_every=1,
    )
    with engine:
        deadline = time.monotonic() + 2.0
        while engine.running and time.monotonic() < deadline:
            time.sleep(0.02)
    assert repo.save.called
    repo.close.assert_called_once()
