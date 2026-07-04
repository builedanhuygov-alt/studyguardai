# Security & Privacy Review

| Area | Finding | Mitigation / status |
| --- | --- | --- |
| Logging privacy | Frames must never be logged | Results/snapshots hold no image data; `test_privacy.py` fails CI if a raw-media field is added |
| Data at rest | Only derived metrics in SQLite | No BLOB column (schema test); `DataRights.export/delete` for user control |
| Input validation | Config values coerced by type; report period/audience validated | `Config._coerce`, `build_report` raises on bad args; `detector_stride >= 1` enforced |
| Path handling | DB/config/log paths come from the user/config | Local paths by design; **recommend** callers pass trusted paths (documented) |
| Secret handling | No secrets in the codebase or logs | Camera/local only; future connectors must use OAuth tokens via env, never committed |
| Dependency risk | Runtime deps: `opencv-python`, `numpy` only | Small surface; dev/build tools pinned in `[dev]`; Dependabot recommended |
| Temporary files | Used only in tests/benchmarks via `tempfile` | No temp files in the runtime path |
| Consent | No source active without explicit consent | `ConsentStore.require` gates `connect_source` |
| Plugin trust | Entry-point plugins run in-process | Documented: install only trusted plugins |

## Residual risks (honest)
- Path traversal is **not** a concern in the current local-only design, but a
  future HTTP layer must validate/authorize paths and add authn/z.
- No sandboxing of third-party detector plugins (in-process).
- No dependency vulnerability scanning wired yet (recommend `pip-audit` in CI).
