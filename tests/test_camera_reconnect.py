import numpy as np
import pytest

from studyguard.camera import Camera
from studyguard.config import Config


class FakeCapture:
    """A scripted cv2.VideoCapture stand-in for deterministic tests."""

    def __init__(self, reads, *, opened=True):
        self._reads = list(reads)
        self._opened = opened
        self.released = False

    def isOpened(self):
        return self._opened

    def read(self):
        return self._reads.pop(0) if self._reads else (False, None)

    def set(self, *_args):
        return True

    def release(self):
        self.released = True


def _frame():
    return np.zeros((8, 8, 3), dtype=np.uint8)


def _config(**overrides):
    base = {"mirror": False, "frame_width": 8, "reconnect_attempts": 2, "reconnect_backoff_s": 0.0}
    base.update(overrides)
    return Config(**base)


def test_reconnect_recovers_after_transient_failure():
    caps = [
        FakeCapture([(True, _frame()), (False, None)]),  # good read, then a drop
        FakeCapture([(True, _frame())]),                  # reconnect succeeds
    ]
    camera = Camera(_config(), capture_factory=lambda _src: caps.pop(0))
    camera.open()
    assert camera.read() is not None
    assert camera.read() is not None  # dropped, then reconnected
    assert camera.reconnects == 1


def test_reconnect_gives_up_after_attempts():
    caps = [FakeCapture([(False, None)]) for _ in range(3)]
    camera = Camera(_config(), capture_factory=lambda _src: caps.pop(0) if caps else FakeCapture([]))
    camera.open()
    assert camera.read() is None
    assert camera.reconnects == 0


def test_read_before_open_raises():
    with pytest.raises(RuntimeError):
        Camera(Config()).read()
