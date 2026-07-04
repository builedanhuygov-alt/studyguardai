"""Run the performance profile and write a machine-readable + Markdown report.

Usage: PYTHONPATH=. python benchmarks/report.py
Writes benchmarks/results/benchmark.json and benchmark.md (measured values only).
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from benchmarks import profile

_OUT = Path(__file__).parent / "results"


def collect() -> dict:
    fps, latency_ms = profile.bench_fps()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "detector_pipeline_fps": round(fps, 1),
        "inference_latency_ms": round(latency_ms, 2),
        "plugin_load_ms": round(profile.bench_plugin_load(), 2),
        "sqlite_writes_per_s": round(profile.bench_sqlite()),
        "processing_peak_mem_mb": round(profile.bench_memory(), 1),
        "cold_import_ms": round(profile.bench_startup(), 1),
    }


def _to_markdown(data: dict) -> str:
    lines = ["# Benchmark Report", "", f"_Generated: {data['generated_at']}_", "", "| Metric | Value |", "| --- | --- |"]
    for key, value in data.items():
        if key in {"generated_at"}:
            continue
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("> Measured on the machine that ran this script; re-run locally for your hardware.")
    return "\n".join(lines) + "\n"


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    data = collect()
    (_OUT / "benchmark.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    (_OUT / "benchmark.md").write_text(_to_markdown(data), encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
