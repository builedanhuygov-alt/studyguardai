# Roadmap

Prioritized by student value ("would a student still use this after 30 days?")
and reliability, not technical novelty.

## Now (v0.1.x) — reliability & honesty
- Resilient camera source: auto-reconnect with backoff; explicit
  "camera disconnected" state and recovery.
- Per-user **calibration** step (neutral posture) to cut false positives.
- Labeled eval clips + published accuracy numbers (replace heuristic guesses
  with measured results against the acceptance gates).

## Next (v0.2) — insight & UX
- Streamlit **analytics dashboard** over the SQLite store: focus/posture over
  time, distraction counts, study streaks, actionable weekly summary.
- Session-aware HUD (state + active time on screen) and calmer nudges.

## Later (v0.3+) — capability
- Upgrade detection to MediaPipe (pose + face mesh) behind the same `Detector`
  seam for gaze/head-pose and true posture landmarks.
- New detectors as plugins: **drowsiness**, **phone-in-hand**.
- Optional remote `Repository` (Postgres/TimescaleDB) for multi-device history.

## Explicitly out of scope (for now, per YAGNI)
- Cloud video processing (violates on-device privacy invariant).
- Multi-tenant SaaS backend until single-user value is proven.

## Product guardrails
Every new feature must answer: does it measurably improve studying, and does it
degrade gracefully when detection fails? If not, it is redesigned or dropped.
