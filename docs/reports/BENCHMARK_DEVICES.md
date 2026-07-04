# Benchmark — by device

Reproduce on your machine: `PYTHONPATH=. python benchmarks/report.py`.

## Measured here (CI/build sandbox)
| Device | Detector FPS | Latency (ms) | SQLite writes/s | Plugin load (ms) | Cold import (ms) | Proc peak mem (MB) |
| --- | --- | --- | --- | --- | --- | --- |
| Linux CI sandbox (Py 3.13, headless) | 22.8 | 43.8 | 8322 | 16.2 | ~131 | 0.3 |

## Community devices (fill in locally — not measured by us)
| Device | Detector FPS | RAM | CPU | Startup | Latency |
| --- | --- | --- | --- | --- | --- |
| Intel i5-1135G7 | _run locally_ | | | | |
| Ryzen 5 5600H | _run locally_ | | | | |
| Apple M1 Air | _run locally_ | | | | |

> Honesty: we only publish numbers we actually measured. Per-device rows are a
> template for contributors to fill via a PR — we do not invent them.
