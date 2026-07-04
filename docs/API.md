# API Reference

Stable, public API of the `studyguard` package. Types are simplified for
readability; see docstrings for full detail.

## `studyguard.core`

### Value objects (immutable)
- `Analysis(name, present, metrics={}, face_box=None)` — one detector's result.
- `Snapshot(frame_index, present, posture, focus, status, message, fps, elapsed_s, distractions, face_box=None)` — render-ready aggregate.

### Protocols
- `Detector` — `name: str`, `analyze(frame: np.ndarray) -> Analysis`.
- `Repository` — `save(snapshot: Snapshot) -> None`, `close() -> None`.

### Registry
- `register_detector(cls) -> cls` — class decorator.
- `build_detectors() -> list[Detector]`.
- `registered_detector_classes() -> tuple[type, ...]`.
- `clear_registry() -> None`.

### Aggregation & engine
- `Aggregator(smoothing=0.3, posture_alert_below=55.0, focus_alert_below=50.0)`
  with `build(analyses, *, frame_index, fps, elapsed_s, distractions) -> Snapshot`.
- `Engine(read_frame, detectors, aggregator, *, repository=None, sample_every=5, poll_timeout=0.5)`
  with `start()`, `stop()`, context-manager support, `running: bool`,
  `error`, and `latest() -> tuple[np.ndarray, Snapshot] | None`.

## `studyguard.detectors`
- `PostureFocusDetector` — face-based posture/focus (OpenCV Haar), stateless.
- `FakeDetector(posture=80.0, focus=90.0, present=True)` — deterministic.

## `studyguard.plugins`
- `load_detectors(*, use_fake=False) -> list[Detector]` — builtin + entry-point discovery.

## `studyguard.storage`
- `SQLiteRepository(path="studyguard.db")`, `NullRepository()` — both implement `Repository`.

## `studyguard.session`
- `SessionConfig`, `SessionEvent`, `SessionState`, `SessionTracker(config=None, *, max_gap_s=5.0)`.
- `AlertConfig`, `Alert`, `AlertManager(config=None, messages=None)`.
- `SessionConsumer(*, session=None, alerts=None, posture_alert_below=55.0, focus_alert_below=50.0, clock=time.monotonic)`
  with `observe(snapshot) -> list[str]`.

## `studyguard.eval` / `studyguard.eval_gates`
- `evaluate(frames, expected_status, detector, aggregator) -> EvalReport`.
- `meets_threshold(report, threshold) -> bool`.
- `evaluate_metric(frames, expected_bands, key, detector, aggregator) -> EvalReport`.
- `passes_gates(posture_report, focus_report) -> bool`; `POSTURE_MIN_ACCURACY`, `FOCUS_MIN_ACCURACY`.

## `studyguard.privacy`
- `contains_raw_media(obj) -> bool`, `assert_persistable(obj) -> None`.

## `studyguard.config` / `studyguard.logging_conf`
- `Config` dataclass with `Config.load(path=None)` and `merged(**overrides)`.
- `setup_logging(level="INFO", log_file=None) -> None`.

## `studyguard.cli`
- `main(argv=None) -> None` — console entry (`studyguard`, `python -m studyguard`).
