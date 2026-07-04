# Developer Guide

## Prerequisites
- Python 3.11+ (uses `tomllib`)
- A webcam for live runs (optional — use `--fake` or `--video`)

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Running
```bash
python -m studyguard              # webcam + HUD + SQLite
python -m studyguard --fake       # deterministic, no camera needed
python -m studyguard --video clip.mp4
python -m studyguard --headless --no-save   # CI / servers
studyguard --help                 # installed console script
```
Configuration precedence: defaults < `studyguard.toml` < `STUDYGUARD_*` env vars
< CLI flags. See `studyguard/config.py`.

## Testing
```bash
pytest                                   # unit + integration
pytest tests/integration                 # integration only
pytest --cov=studyguard --cov-report=term-missing
pytest --cov=studyguard --cov-report=html   # htmlcov/index.html
```

## Quality gates
```bash
ruff check .
black --check .
mypy studyguard
```
`make lint format typecheck test cov bench` wrap these.

## Benchmarks
```bash
python benchmarks/benchmark_pipeline.py            # 300 frames @ 640x480
python benchmarks/benchmark_pipeline.py 500 1280 720
```

## Docker
```bash
docker build -t studyguard-ai .
docker run --rm studyguard-ai            # prints CLI help
docker compose run --rm tests            # runs the suite
```
Webcam passthrough is host-specific (Linux: `--device /dev/video0`).

## Releasing (SemVer)
1. Update `CHANGELOG.md` and bump `version` in `pyproject.toml` + `studyguard/__init__.py`.
2. Commit with `chore(release): vX.Y.Z` and tag `vX.Y.Z`.
3. Pushing the tag triggers `.github/workflows/release.yml` (build + GitHub Release).

## Repository layout
```
studyguard/      core, detectors, storage, session, cli, config, ...
tests/           unit tests (+ tests/integration/)
benchmarks/      performance scripts
examples/        runnable examples + label format
docs/            architecture, API, developer guide
.github/         CI + release workflows, issue/PR templates
```
