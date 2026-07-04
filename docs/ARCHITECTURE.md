# Architecture

StudyGuard AI follows a layered, dependency-inverted design. Computer vision is
isolated behind protocols so the domain logic (sessions, alerts, analytics) is
pure, deterministic, and unit-testable without a camera.

## Layers

| Layer | Package | Responsibility | Depends on |
| --- | --- | --- | --- |
| Presentation | `studyguard.hud` | Draw the HUD from an immutable snapshot | core (types) |
| Application | `studyguard.cli`, `studyguard.session` | Composition root (DI), session state, alerts | core, infra |
| Domain / Core | `studyguard.core` | Engine, protocols, immutable results, aggregator | — |
| Plugins | `studyguard.detectors`, `studyguard.plugins` | Detector implementations + discovery | core |
| Infrastructure | `studyguard.camera`, `studyguard.storage` | OpenCV capture, SQLite repository | core (types) |
| Cross-cutting | `studyguard.config`, `studyguard.logging_conf`, `studyguard.privacy` | Config, logging, privacy guard | — |

**Dependency rule:** dependencies point inward. Infrastructure and plugins
depend on core abstractions (`Detector`, `Repository`), never the reverse.

## Component view

```mermaid
flowchart LR
    Camera[CameraSource] -->|frames| Engine
    subgraph Core
      Engine -->|frame| Detectors[Detector registry]
      Detectors -->|Analysis| Aggregator
      Aggregator -->|immutable Snapshot| Engine
    end
    Engine -->|latest snapshot| HUD[cv2 HUD]
    Engine -->|buffered writes| Repo[(Repository / SQLite)]
    Engine -->|snapshot stream| Session[SessionConsumer]
    Session --> Alerts[AlertManager]
    CLI[cli: composition root] -.builds+injects.-> Engine
    Plugins[plugins.load_detectors] -.discovers.-> Detectors
```

## Class view (core contracts)

```mermaid
classDiagram
    class Detector {
      <<protocol>>
      +name: str
      +analyze(frame) Analysis
    }
    class Repository {
      <<protocol>>
      +save(snapshot) None
      +close() None
    }
    class Analysis {
      +name: str
      +present: bool
      +metrics: Mapping
      +face_box: tuple|None
    }
    class Snapshot {
      +posture: float
      +focus: float
      +status: str
      +present: bool
    }
    class Aggregator {
      +build(analyses) Snapshot
    }
    class Engine {
      +start() None
      +stop() None
      +latest() tuple|None
      +running: bool
    }
    Engine --> Detector : runs
    Engine --> Aggregator : composes
    Engine --> Repository : persists
    Aggregator --> Snapshot : produces
    Detector --> Analysis : produces
    SQLiteRepository ..|> Repository
    PostureFocusDetector ..|> Detector
    FakeDetector ..|> Detector
```

## Runtime sequence (one frame)

```mermaid
sequenceDiagram
    participant Cap as Capture thread
    participant Q as Newest-frame slot
    participant W as Inference worker
    participant Agg as Aggregator
    participant Main as Main thread
    participant DB as Repository
    Cap->>Q: put(frame) (drops stale)
    W->>Q: get() newest
    W->>W: run detectors
    W->>Agg: build(analyses)
    Agg-->>W: Snapshot
    W->>Main: publish latest
    W->>DB: enqueue write (throttled)
    Main->>Main: render HUD + session/alerts
```

## Session state machine

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> ACTIVE: presence confirmed (N frames)
    ACTIVE --> PAUSED: absent >= pause_after_s
    PAUSED --> ACTIVE: presence confirmed
    PAUSED --> ENDED: absent >= end_after_s
    ENDED --> [*]
```

## Concurrency & backpressure
- One **capture thread** owns the camera lifecycle and publishes the newest
  frame into a single-slot buffer (`queue.Queue(maxsize=1)`), dropping stale
  frames so latency never accumulates.
- One **inference worker** runs detectors + aggregator and publishes the latest
  snapshot; a separate **writer thread** persists throttled samples so the DB
  never blocks capture.
- The **main thread** renders (OpenCV GUI is main-thread only on macOS).
- We deliberately use threads rather than `asyncio`: the workload is CPU-bound
  OpenCV calls that release the GIL, and the model is simpler to reason about.

## Reliability & graceful degradation
- Camera cannot open -> friendly message + suggestion to use `--video`/`--fake`.
- A failing detector or consumer is caught and logged; the loop never dies.
- Temporary face/pose loss is absorbed by presence hysteresis (no single-frame
  state changes) before a session pauses or ends.
- Large time gaps (laptop asleep) are clamped so study statistics stay honest.

## Extension points
- **New detector:** implement `Detector.analyze` + `@register_detector` (+ entry
  point for external packages). No core changes.
- **New storage backend:** implement `Repository.save/close` (e.g. Postgres or
  TimescaleDB) and inject it in the composition root.

## Design decisions (ADRs)
Key decisions are recorded as ADRs in the project workspace: runtime/UI split,
concurrency & backpressure, detector/repository seams, and plan sequencing.
