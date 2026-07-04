# 2-Minute Demo & Pitch Script

Storyboard for `demo.mp4` / `pitch.mp4` (record locally; we don't ship fabricated
video). GIFs go in `docs/assets/` and are referenced from the README.

## Shot list (≈120s)
1. **0:00–0:15 — Hook.** “Students study for hours with zero feedback. StudyGuard
   AI is a private, on-device study coach.” Show the landing page (`website/`).
2. **0:15–0:35 — One-click.** Double-click the installer / `studyguard-desktop`;
   the native window opens (splash → Overview). Capture as `docs/assets/desktop.gif`.
3. **0:35–0:55 — Live detection.** Sit upright (FOCUSED), slouch (SLOUCHING),
   look away (DISTRACTED), leave (AWAY). Capture `docs/assets/alert.gif`.
4. **0:55–1:20 — AI Coach.** Open AI Coach: show evidence-backed messages and the
   weekly narrative (“Focus peaks 8–10 PM; Tue/Fri dip ~25%…”). `coach.gif`.
5. **1:20–1:40 — Analytics.** Trends, streak, goals, heatmap. `analytics.gif`.
6. **1:40–1:55 — No webcam? Demo Mode.** Run `studyguard demo` in a terminal.
7. **1:55–2:00 — Close.** “Privacy-first, open source, extensible. Try it.”

## No-webcam fallback (for the judging room)
```bash
studyguard demo          # scripted walkthrough in the terminal
streamlit run dashboard/app.py   # full UI on seed data
```

## Recording tips
- 1440×900, dark theme; keep each GIF < 5 MB; trim to the action.
- Convert: `ffmpeg -i demo.mp4 -vf "fps=12,scale=900:-1" docs/assets/demo.gif`.
