# Architecture Report

Summary of the audit against the architecture. Full design lives in
[../ARCHITECTURE.md](../ARCHITECTURE.md), the platform view in
[../PLATFORM.md](../PLATFORM.md), and data sources in
[../DATA_SOURCES.md](../DATA_SOURCES.md).

## Findings
- **Dependency rule respected.** Infrastructure (`camera`, `storage`) and
  plugins (`detectors`, `sources`) depend on core abstractions (`Detector`,
  `Repository`, `MetricPoint`) — not the reverse. `insight`, `reports`, and
  `api` sit above analytics/sources. No circular imports.
- **SOLID.** SRP per module; OCP via two registries (detectors, sources); DIP
  via protocols; ISP via small protocols (5-method `DataSource`).
- **Extensibility proven.** Adding a detector or a whole data source is one new
  class + registration; the service, analytics, insight, and reports consume it
  with no edits (validated by tests).
- **Concurrency.** Capture thread + inference worker + async writer; newest-
  frame-wins backpressure; main-thread rendering. Threads (not asyncio) chosen
  deliberately for CPU-bound OpenCV that releases the GIL.
- **Boundaries.** The service returns JSON-serializable dicts, decoupling any
  frontend/HTTP transport from domain objects.

## Layer map
```
presentation : hud
application  : cli, session, reports, api
domain/core  : core (engine, protocols, models, aggregator), analytics, insight
plugins      : detectors, sources
infrastructure: camera, storage
cross-cutting: config, logging_conf, privacy, heuristics
```

## Recommended evolution (no rework required)
1. Add a `session_id` dimension to storage → exact study time (Repository stays).
2. Introduce a learned recommender behind the existing `insight` functions.
3. Add the HTTP adapter over `StudyGuardService` (1:1 route mapping).
None of these change existing interfaces — the seams were designed for them.
