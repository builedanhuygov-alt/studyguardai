# Security Policy

## Supported versions
StudyGuard AI is pre-1.0. Security fixes target the latest `main` and the most
recent tagged release.

## Reporting a vulnerability
Please report suspected vulnerabilities privately via GitHub Security Advisories
("Report a vulnerability" on the repository's Security tab) rather than opening a
public issue. We aim to acknowledge reports within a few days.

## Privacy by design
StudyGuard AI processes the webcam **on-device**. It is a core invariant that:
- Raw camera frames are **never persisted or logged** — only derived metrics
  (posture/focus scores, timestamps, session statistics) are stored.
- This is enforced structurally (result/snapshot value objects hold no image
  data; the SQLite schema has no binary column) and guarded by
  `tests/test_privacy.py`, which fails CI if a raw-media field is introduced.

## Hardening notes
- Persistence is local SQLite by default; no data leaves the machine unless a
  deployer adds a remote `Repository` implementation.
- Third-party detector plugins run in-process; only install plugins you trust.
