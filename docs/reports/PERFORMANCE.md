# Performance Report

**Measured values only.** Numbers below were produced by
`benchmarks/profile.py` in the CI/build sandbox and are **machine-dependent** —
re-run locally for your hardware.

## Environment
- Python 3.13, `opencv-python-headless`, shared virtualized CI sandbox.
- Single-threaded micro-benchmarks (the live app uses the threaded engine).
- ⚠️ CPU model and real-webcam FPS were **not** measurable in this environment.

## Results (measured)

| Metric | Value | How measured |
| --- | --- | --- |
| Detector+aggregator throughput @640×480 | **18.1 FPS** | 200 frames, `time.perf_counter` |
| Inference latency per frame @640×480 | **55.3 ms** | derived from the same run |
| Plugin load time (`load_detectors`) | **21.6 ms** | best of 5 |
| SQLite write throughput (commit per save) | **5,701 writes/s** | 1,000 inserts |
| Processing peak memory (Python objects) | **0.3 MB** | `tracemalloc` over 200 frames (excludes NumPy/OpenCV buffers) |
| Cold import of `studyguard.cli` (incl. interpreter) | **130.6 ms** | best of 5 subprocess imports |

## Interpretation (honest)
- ~18 FPS here is a **single-threaded, headless** Haar-cascade measurement on a
  shared VM. On a real laptop with the threaded engine and newest-frame-wins
  dropping, perceived responsiveness is typically better; **this is not yet
  measured on target hardware.**
- SQLite commits every sample; batching would raise throughput if ever needed
  (current rates far exceed the ~1 sample/sec the app writes).
- CPU utilization was not measured (no reliable per-core sampling in-sandbox).

## Reproduce
```bash
PYTHONPATH=. python benchmarks/profile.py            # full profile
PYTHONPATH=. python benchmarks/benchmark_pipeline.py 300 1280 720   # custom size
```
