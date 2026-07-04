# Testing Report

## Test suites (pytest)
| File | Focus |
| --- | --- |
| `tests/test_core.py` | engine threading, immutability, registry, persistence |
| `tests/test_detectors.py` | detector no-face path |
| `tests/test_heuristics.py` | pure posture/focus scoring (happy/edge/clamp/DI) |
| `tests/test_session.py` | session state machine + gentle alerts (fake clock) |
| `tests/test_storage.py` | SQLite round-trip |
| `tests/test_privacy.py` | privacy invariant + schema guard |
| `tests/test_analytics.py` | trends, streaks, burnout, insights, empty-safe |
| `tests/test_sources.py` | data-source protocol, lifecycle, consent, data rights |
| `tests/test_insight.py` | multi-source inference, confidence, no causation |
| `tests/test_reports.py` | report sections, confidence scaling, validation |
| `tests/test_api.py` | service API end-to-end (analytics/insights/reports/export) |
| `tests/test_config.py` | config precedence (defaults/TOML/env/merge) |
| `tests/test_cli.py` | CLI argument parsing |
| `tests/test_service_health.py` | health surface + camera guard |
| `tests/test_camera_reconnect.py` | bounded reconnect + read-before-open guard |
| `tests/integration/test_pipeline.py` | engine → SQLite integration |
| `tests/test_engine_mock.py` | repository interaction via mock |

Coverage focus: business logic, edge cases, error recovery, plugin loading,
thread lifecycle, repository, API, and configuration.

## What was executed here (honest)
`pytest` is not installable in the offline build sandbox. Instead, the same
logic was executed via standalone runners and `py_compile`:

- Platform checks: **14/14** · Analytics: **8/8** · Session: **25/25** ·
  Heuristics: **8/8** · Final (config/CLI/health): **9/9**.
- All modules compile.

## Run the real suite locally / in CI
```bash
pip install -e ".[dev]"
pytest --cov=studyguard --cov-report=term-missing
```
CI runs this on Python 3.11 and 3.12 (`.github/workflows/ci.yml`).

## Known gaps
- Thread-safety is covered by lifecycle tests, not stress/fuzz tests.
- Camera **reconnect** is implemented and unit-tested via an injected capture
  factory; reconnect against real hardware disconnects is not yet tested.
- No coverage percentage is claimed until measured by CI.
