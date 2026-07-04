"""Reproducible performance profile. Reports MEASURED values only.

Usage::

    PYTHONPATH=. python benchmarks/profile.py

All numbers are machine-dependent; re-run locally to get values for your setup.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import tracemalloc

import numpy as np

from studyguard.analytics.engine import daily_stats
from studyguard.core import Aggregator, Snapshot
from studyguard.detectors import PostureFocusDetector
from studyguard.plugins import load_detectors
from studyguard.sources.consent import ConsentStore  # noqa: F401  (import cost sampled below)
from studyguard.storage import SQLiteRepository

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bench_fps(num_frames: int = 200, width: int = 640, height: int = 480) -> tuple[float, float]:
    frame = np.random.default_rng(0).integers(0, 255, (height, width, 3), dtype=np.uint8)
    detector = PostureFocusDetector()
    aggregator = Aggregator()
    for _ in range(10):
        aggregator.build([detector.analyze(frame)], frame_index=0, fps=0.0, elapsed_s=0.0, distractions=0)
    start = time.perf_counter()
    for index in range(num_frames):
        aggregator.build([detector.analyze(frame)], frame_index=index, fps=0.0, elapsed_s=0.0, distractions=0)
    elapsed = time.perf_counter() - start
    return num_frames / elapsed, elapsed / num_frames * 1000.0


def bench_plugin_load(runs: int = 5) -> float:
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        load_detectors()
        best = min(best, (time.perf_counter() - start) * 1000.0)
    return best


def bench_sqlite(num_writes: int = 1000) -> float:
    path = os.path.join(tempfile.mkdtemp(), "profile.db")
    repo = SQLiteRepository(path)
    start = time.perf_counter()
    for index in range(num_writes):
        repo.save(Snapshot(index, True, 80.0, 90.0, "FOCUSED", "ok", 30.0, 1.0, 0))
    elapsed = time.perf_counter() - start
    repo.close()
    return num_writes / elapsed


def bench_memory(num_frames: int = 200, width: int = 640, height: int = 480) -> float:
    frame = np.random.default_rng(0).integers(0, 255, (height, width, 3), dtype=np.uint8)
    detector = PostureFocusDetector()
    aggregator = Aggregator()
    tracemalloc.start()
    for index in range(num_frames):
        aggregator.build([detector.analyze(frame)], frame_index=index, fps=0.0, elapsed_s=0.0, distractions=0)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1_000_000.0


def bench_startup(runs: int = 5) -> float:
    env = {**os.environ, "PYTHONPATH": _HERE}
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        subprocess.run([sys.executable, "-c", "import studyguard.cli"], check=True, cwd=_HERE, env=env)
        best = min(best, (time.perf_counter() - start) * 1000.0)
    return best


def main() -> None:
    fps, latency_ms = bench_fps()
    print(f"detector_pipeline_fps={fps:.1f}")
    print(f"inference_latency_ms={latency_ms:.2f}")
    print(f"plugin_load_ms={bench_plugin_load():.2f}")
    print(f"sqlite_writes_per_s={bench_sqlite():.0f}")
    print(f"processing_peak_mem_mb={bench_memory():.1f}")
    print(f"cold_import_ms={bench_startup():.1f}")


if __name__ == "__main__":
    main()
