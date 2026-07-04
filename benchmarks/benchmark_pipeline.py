"""Micro-benchmark for the per-frame hot path.

Measures throughput (frames/second) of the detector + aggregator pass on
synthetic frames, so regressions in the inference path are easy to catch.

Usage::

    python benchmarks/benchmark_pipeline.py [num_frames] [width] [height]
"""
from __future__ import annotations

import sys
import time

import numpy as np

from studyguard.core import Aggregator
from studyguard.detectors import PostureFocusDetector


def run(num_frames: int = 300, width: int = 640, height: int = 480) -> float:
    rng = np.random.default_rng(1234)
    frame = rng.integers(0, 255, size=(height, width, 3), dtype=np.uint8)
    detector = PostureFocusDetector()
    aggregator = Aggregator()

    for _ in range(10):  # warm up
        aggregator.build([detector.analyze(frame)], frame_index=0, fps=0.0, elapsed_s=0.0, distractions=0)

    start = time.perf_counter()
    for index in range(num_frames):
        aggregator.build([detector.analyze(frame)], frame_index=index, fps=0.0, elapsed_s=0.0, distractions=0)
    elapsed = time.perf_counter() - start
    throughput = num_frames / elapsed if elapsed > 0 else float("inf")
    print(
        f"frames={num_frames} size={width}x{height} "
        f"elapsed={elapsed:.3f}s throughput={throughput:.1f} FPS"
    )
    return throughput


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    run(*args)
