# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Real evaluation pipeline** (`studyguard/evaluation/pipeline.py`) + dataset
  generator + `tools/run_evaluation.py` producing measured Precision/Recall/F1,
  confusion matrix, and ROC/AUC on a noisy synthetic dataset (self-eval, clearly
  labeled as not human-validated). Results in `docs/reports/EVALUATION_RESULTS.md`.
- **Labeling tool** `tools/label_clip.py` to sample frames + emit a labels template.
- **Demo Mode** (`studyguard demo`) and **Presentation Mode** (`studyguard present`)
  — full walkthrough on seed data, no webcam.
- **Benchmark report** by device (`docs/reports/BENCHMARK_DEVICES.md`) with the
  measured sandbox row + a contributor template.
- **Diagrams** (`docs/DIAGRAMS.md`): UML, sequence, ERD, component, deployment.
- **Startup-style README**: badges (CI/coverage/license/python/release/docs) +
  nav (Demo/Download/Docs/Desktop/Dashboard/API/Paper/Benchmark) + model-eval
  and benchmark sections. Demo scenario guide + 2-minute demo/pitch script.
- **AI evaluation** (`studyguard/evaluation/`): confusion matrix, precision/
  recall/F1, ROC + AUC, calibration curve (pure Python).
- **Weekly AI-coach narrative** (`studyguard/coach/summary.py`) + `/coach/weekly`
  + a `CoachStrategy` seam (rule-based now, LLM later).
- **i18n** (en/vi/ja), **JSON logging**, and **security primitives**
  (HS256 JWT, API keys, token-bucket rate limit, security headers).
- API observability (`/readiness`, `/liveness`, `/metrics`), CORS + security
  headers middleware.
- Static marketing **website**, production **docker-compose** (api/nginx/
  Prometheus/Grafana), **Alembic** migrations scaffold + seed, **datasets/**,
  **docs/research** (paper + refs), commercial + LLM-coach architecture,
  plugin marketplace + Pomodoro example, wiki index, discussion template,
  auto-release-notes config, benchmark report generator. Extras `[monitoring]`,
  `[migrations]`, `[research]`.
- **Native desktop app** (`desktop/`): PyInstaller + pywebview shell that hosts
  the FastAPI service and an offline SPA (Overview/Analytics/Coach/Goals/
  Sessions/Settings/About), system tray, splash, crash handling, auto log
  folder, remembered settings — Dashboard → Service → Domain.
- **Windows packaging**: PyInstaller spec, version resource, icon generator,
  Inno Setup installer, portable zip, checksum tool, build script, and a
  `desktop-build.yml` GitHub Actions workflow. Docs in `docs/DESKTOP.md` +
  release-notes template. Extra `[desktop]`, script `studyguard-desktop`.
- **AI Coach** (`studyguard/coach/`): explainable coaching messages with
  evidence, supporting metrics, and confidence (focus-vs-previous-day,
  best-time-of-day, streak, posture, burnout).
- **Goals/gamification** (`studyguard/goals/`): XP, levels, streaks,
  consistency, achievements, and daily/weekly goal progress.
- **Export** (`studyguard/export/`): JSON/CSV/Markdown exporters via a Strategy
  plugin registry.
- Service API endpoints: `get_coach`, `get_goals`, `export`, `export_formats`.
- `docs/AI_COACH.md`.
- Observability: `StudyGuardService.get_health()` (API/plugin/source/storage) and
  `Camera.is_open`.
- Tests: `test_config.py`, `test_cli.py`, `test_service_health.py`.
- `benchmarks/profile.py` (measured startup/FPS/latency/throughput/memory).
- Engineering reports under `docs/reports/` and a `docs/STATUS.md` maturity matrix.

### Changed
- `Camera` no longer uses `assert` for state (raises `RuntimeError`); `read()` is
  now typed `-> np.ndarray | None`.
- **Reliability:** `Camera` now recovers from transient live-webcam read failures
  via a bounded reconnect with backoff (`reconnect_attempts`,
  `reconnect_backoff_s`), with an injectable capture factory and a `reconnects`
  counter. Added `tests/test_camera_reconnect.py`.
- **Maintainability:** unified duplicate `clamp` logic (`core` imports
  `heuristics.clamp`).
- **Multi-source platform**: `studyguard/sources/` — a `DataSource` plugin
  contract (`connect/disconnect/collect/validate/health_check`) + registry,
  a `CameraDataSource`, consent (`ConsentStore`) and data-rights
  (export/delete). The engine no longer depends on any concrete source.
- `studyguard/insight/` — multi-source insight engine separating
  Observation / Inference / Recommendation with confidence (never claims causation).
- `studyguard/reports/` — structured weekly/monthly reports (what / why /
  suggestions / confidence) with Markdown rendering.
- `studyguard/api/` — stable `StudyGuardService` facade (JSON-serializable) that
  the frontend/HTTP layer consumes; endpoint mapping in `docs/API_HTTP.md`.
- Docs: `docs/DATA_SOURCES.md`, `docs/API_HTTP.md` (with future providers as
  documented extension points).
- `studyguard/analytics/`: sensor-agnostic learning-analytics layer — daily
  stats, trends, study streaks, a burnout-risk signal, insights, and
  recommendations (rule-based v0 behind swappable pure functions) plus a SQLite
  source adapter. Foundation for the study-intelligence platform (`docs/PLATFORM.md`).
- `studyguard/heuristics.py`: pure, tunable posture/focus scoring (camera-free
  unit tests) with a `PostureFocusConfig` (removes magic numbers from the detector).
- `CODEOWNERS`, `py.typed` (PEP 561 typing marker), README status badges.
- Deployment, Troubleshooting, and Roadmap documentation.

### Changed
- `PostureFocusDetector` now delegates scoring to `studyguard.heuristics` and
  accepts an injectable `PostureFocusConfig` (behavior unchanged at defaults).

## [0.1.0] - 2026-07-04
### Added
- Threaded capture/inference **Engine** (newest-frame-wins, headless-capable).
- **Detector** protocol + registry and an entry-point **plugin system**.
- Built-in `PostureFocusDetector` (OpenCV Haar) and deterministic `FakeDetector`.
- Immutable `Analysis` / `Snapshot` value objects and a pure `Aggregator`.
- **Repository** pattern with `SQLiteRepository` and `NullRepository`; buffered
  async writer thread.
- Presence-driven **SessionTracker** state machine and gentle **AlertManager**.
- **Privacy invariant** (metrics only, never raw frames) enforced by tests.
- Accuracy **eval harness** and per-metric acceptance gates.
- Configuration management (TOML + environment), central logging, CLI.
- Unit, integration, and mock tests; benchmark script; example scripts.
- Docker support, pre-commit hooks, GitHub Actions CI + release workflow.
- Architecture, API, development, contribution, and security documentation.

[Unreleased]: https://github.com/builedanhuygov-alt/studyguard-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/builedanhuygov-alt/studyguard-ai/releases/tag/v0.1.0
