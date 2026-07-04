# Project Status

Honest maturity of each component. Legend:

- **Implemented** — code complete.
- **Verified** — exercised by automated checks (see Evidence).
- **Experiment** — works, but the *quality/accuracy* is not validated on real data.
- **Planned** — interface/docs only; not built.

> Verification note: this repository's automated checks were executed in an
> **offline sandbox (Python 3.13, `opencv-python-headless`)** using `py_compile`
> plus standalone check scripts. `ruff`/`black`/`mypy`/`pytest`/`coverage` are
> configured and run in **GitHub Actions**, but were **not** run in the sandbox
> (no network to install them). Real-webcam behavior is **not** verified.

| Component | Status | Evidence |
| --- | --- | --- |
| Core engine (threads, newest-frame-wins) | Verified | headless engine + persistence checks |
| Camera reconnect (bounded, backoff) | Verified | reconnect unit checks (injected capture) |
| Detector plugin system + registry | Verified | plugin-load + registry checks |
| Posture/focus heuristic scoring | Experiment | pure `heuristics` unit checks (math only) |
| **Posture/focus accuracy on real users** | Planned | no labeled dataset yet |
| Session state machine + gentle alerts | Verified | 25 session checks (fake clock) |
| Analytics (trends, streaks, burnout) | Verified | 8 analytics checks |
| **Burnout risk / recommendations quality** | Experiment | rule-based v0, unvalidated |
| Multi-source insight engine | Verified | multi-source confidence + no-causation checks |
| Reports (weekly/monthly, markdown) | Verified | report checks |
| AI coach (evidence + confidence) | Verified | coach checks |
| Goals / gamification (XP/level/streak/achievements) | Verified | goals checks |
| Export (JSON/CSV/Markdown) | Verified | export + service checks |
| **Coaching advice quality** | Experiment | rule-based v0, unvalidated |
| PDF export | Planned | optional `reportlab` extra |
| Web dashboard (Streamlit) | Generated | compiles; GUI not executed in sandbox (needs local run) |
| Native desktop app logic (settings/paths/port/wiring) | Verified | desktop checks |
| Desktop icon generation | Verified | make_icon executed |
| Windows .exe / installer | Generated | build config only; requires local Windows build + run |
| AI evaluation metrics (P/R/F1/ROC/AUC/calibration) | Verified | metric checks |
| Weekly AI-coach narrative + strategy seam | Verified | summary checks |
| i18n (en/vi/ja) | Verified | i18n checks |
| Security primitives (JWT/API key/rate limit) | Verified | security checks |
| JSON logging | Verified | formatter check |
| Benchmark report generator | Verified | executed (writes results) |
| Static website | Generated | valid HTML; online deploy not performed |
| Prod docker-compose + monitoring | Generated | requires Docker; not run here |
| Alembic migrations | Generated | requires `[migrations]`; not run here |
| LLM coach / cloud sync / multi-user portals | Planned | architecture + extension points only |
| Evaluation pipeline + measured metrics (synthetic) | Verified | run_evaluation executed; results committed |
| Human-validated accuracy | Planned | needs labeled real clips (tools/label_clip.py) |
| Demo Mode / Presentation Mode | Verified | demo-mode checks + executed |
| Labeling tool | Generated | compiles; needs a real video to run |
| Diagrams (UML/sequence/ERD/component/deployment) | Generated | Mermaid renders on GitHub |
| Demo/pitch videos + GIFs | Planned | storyboard in docs/DEMO_SCRIPT.md; record locally |
| Mobile app | Planned | consume the service API |
| REST HTTP server | Planned | `docs/API_HTTP.md` mapping only |
| Notification plugin | Planned | plugin seam ready |
| Storage (SQLite Repository) | Verified | round-trip + API checks |
| Data sources (`DataSource` protocol) | Implemented/Verified | camera source lifecycle checks |
| Consent + data rights (export/delete) | Verified | consent + rights checks |
| Service API + health | Verified | 14 platform + 9 final checks |
| Config (TOML + env + CLI) | Verified | config/cli checks |
| Privacy invariant (no raw frames) | Verified | privacy guard + schema check |
| Calendar / LMS / Wearable / Mic providers | Planned | `docs/DATA_SOURCES.md` extension points |
| HTTP server (FastAPI/Flask) | Planned | `docs/API_HTTP.md` mapping only |
| Session-grouped storage (true study time) | Planned | study time currently approximated |
| CI / coverage / lint executed | Planned (local/CI) | not run in sandbox |
