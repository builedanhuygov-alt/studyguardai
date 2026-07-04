# StudyGuard AI: A Privacy-First, Multi-Source Study-Intelligence Platform

**Abstract.** StudyGuard AI estimates focus, posture, and study-session state
on-device from a webcam and other optional signals, then produces explainable
coaching. We describe the architecture, the probabilistic-signal handling
(temporal smoothing + hysteresis + state machines), and a reproducible
evaluation procedure. We are explicit that current accuracy is **not yet
empirically validated** on a labeled human dataset.

## 1. Introduction
Students lack low-friction, private feedback on *how* they study. StudyGuard AI
treats the camera as one sensor among many and centers a domain that turns
signals into analytics, insights, and recommendations.

## 2. Method
- **Detection.** OpenCV Haar face geometry → posture/focus heuristics
  (`studyguard/heuristics.py`).
- **Stabilization.** EMA smoothing (Aggregator) + presence hysteresis + session
  state machine to avoid single-frame false positives.
- **Analytics.** Sensor-agnostic `MetricPoint`s → daily stats, trends, streaks,
  burnout signal.
- **Coach.** Rule-based v0 with evidence/confidence; swappable for an LLM behind
  a stable interface (`studyguard/coach/strategy.py`).

## 3. Evaluation (procedure)
Classification metrics (precision, recall, F1, confusion matrix, ROC/AUC,
calibration) via `studyguard/evaluation/metrics.py`, with acceptance gates
(`studyguard/eval_gates.py`). Reproducible from labeled clips in `datasets/`.

## 4. Related work
Attention/engagement estimation from webcams; productivity trackers
(RescueTime); habit systems (Forest, Duolingo); pose estimation (MediaPipe).
StudyGuard differs by being on-device, privacy-first, and plugin-extensible.

## 5. Limitations
Heuristic detection; no validated accuracy yet; approximate study time (no
session-grouped storage); single-user; UTC day bucketing.

## 6. Future work
MediaPipe pose/gaze; labeled dataset + published metrics; LLM coach; multi-user
cloud sync; calendar/LMS/wearable providers.
