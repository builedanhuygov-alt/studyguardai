# Technical Debt Report

Audit of every module. Severity: High / Medium / Low.

## Fixed in this hardening phase
- **Reliability (Medium):** `camera.py` used `assert` for state (stripped under
  `python -O`) and had an untyped `read`. → now raises `RuntimeError` with a
  clear message, `read() -> np.ndarray | None`, added `is_open` for diagnostics.
- **Observability (Medium):** no aggregated health surface. → added
  `StudyGuardService.get_health()` reporting API, plugins, connected sources,
  and storage health (+ a storage probe).
- **Testability (Medium):** missing tests for config, CLI parsing, and health.
  → added `tests/test_config.py`, `tests/test_cli.py`, `tests/test_service_health.py`.
- **Magic numbers (Low, earlier phase):** posture/focus constants extracted to
  `heuristics.PostureFocusConfig`.
- **Reliability (Medium):** live-camera transient read failures ended the
  session. → `Camera` now performs a **bounded reconnect with backoff**
  (`reconnect_attempts` / `reconnect_backoff_s`), an injectable `capture_factory`
  for tests, and a `reconnects` diagnostic counter.
- **DRY (Low):** unified the two `clamp` helpers — `core` now imports
  `heuristics.clamp` (single implementation).

## Open debt (documented, not yet fixed)
| Item | Severity | Notes |
| --- | --- | --- |
| Study time approximated from sample counts | Medium | No `session_id`/duration in storage; planned schema addition |
| Posture/focus thresholds duplicated (Aggregator + SessionConsumer) | Low | Could centralize in `Config` |
| Day bucketing is UTC-only | Low | Local-timezone bucketing is a config follow-up |
| Engine health not surfaced via the service | Low | Engine exposes `running`/`error`; service owns sources/storage only |

## Checked and found clean
- **Circular dependencies:** none (import order verified; deps point inward:
  infra/plugins → core; insight/reports/api → analytics/sources).
- **Dead code / unused abstractions:** none found after the heuristics refactor.
- **Large classes/functions:** `Engine` is the largest but cohesive; no function
  exceeds a screen. **SOLID:** DIP via protocols; OCP via plugin registries.
- **Naming:** consistent (`*_source`, `*Config`, `score_*`, `get_*`).

## Not addressable in the sandbox
- `ruff`/`black`/`mypy`/`pytest`/`coverage` require network to install; they run
  in CI. Locally: `pip install -e ".[dev]" && ruff check . && black --check . && mypy studyguard && pytest --cov=studyguard`.
