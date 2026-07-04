# Deployment Guide

StudyGuard AI is a local, on-device application. "Deployment" means installing it
reliably on a student's machine (or a lab image), not hosting a server.

## Install from source
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
studyguard --help
```

## Configuration
Resolution order: defaults < `studyguard.toml` < `STUDYGUARD_*` env < CLI flags.
```toml
# studyguard.toml
[studyguard]
frame_width = 800
posture_alert_below = 60.0
db_path = "~/.studyguard/studyguard.db"
log_file = "~/.studyguard/studyguard.log"
```

## Data & privacy
- Only derived metrics are stored (SQLite at `db_path`). No frames are persisted.
- Back up / clear data by copying or deleting the SQLite file.
- To run without any persistence: `--no-save`.

## Docker
```bash
docker build -t studyguard-ai .
docker run --rm studyguard-ai              # prints CLI help
# Linux webcam passthrough:
docker run --rm --device /dev/video0 studyguard-ai python -m studyguard --no-save
```
GUI windows inside containers require extra host configuration; prefer
`--headless` in containers.

## Autostart (optional)
- **Linux (systemd user service)**: create `~/.config/systemd/user/studyguard.service`
  running `studyguard`, then `systemctl --user enable --now studyguard`.
- **Windows**: add a shortcut to `studyguard` in the Startup folder.

## Upgrading
```bash
git pull && pip install -e .
```
Review `CHANGELOG.md` for breaking changes (Semantic Versioning).

## Status
⚠️ Needs local validation on target hardware before real classroom use
(accuracy tuning + on-device performance measurement).
