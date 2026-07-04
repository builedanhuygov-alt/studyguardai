# StudyGuard AI — Study Intelligence Platform

The webcam is **one sensor**. The product is helping students study better, so
the architecture treats every behavioral signal uniformly and turns it into
learning analytics, habit insights, and personalized recommendations.

## North star
Every feature must answer: *"How does this measurably improve learning?"* and
*"Would a student still use it after a year?"* If not, it is redesigned or cut.

## Capability pillars → architecture seams

| Pillar | Where it lives / will live | Status |
| --- | --- | --- |
| Learning analytics | `analytics.engine.daily_stats` / `metric_trend` | ✅ v0 implemented + tested |
| Habit formation | `analytics.engine.study_streak` | ✅ v0 |
| Productivity trends | `analytics.engine.metric_trend` | ✅ v0 |
| Burnout detection | `analytics.engine.burnout_risk` | ✅ v0 heuristic (⚠ not clinically validated) |
| Personalized recommendations | `analytics.engine.recommend` | ✅ v0 rule-based (swappable for ML) |
| Long-term insights | `analytics.engine.generate_insights` | ✅ v0 |
| Focus prediction | future model behind the same `MetricPoint` input | ❌ planned |
| New sensors (keyboard cadence, app usage, wearable) | new `Detector`/source → `MetricPoint` | ❌ planned, seam ready |

## Data flow

```mermaid
flowchart LR
    subgraph Sensors
      Cam[Camera detector]
      Future[Future sensors: keyboard / app usage / wearable]
    end
    Cam -->|Analysis| Agg[Aggregator]
    Future -.->|Analysis| Agg
    Agg -->|Snapshot| Rec[Recorder]
    Rec --> Repo[(Repository)]
    Repo --> Src[MetricPoint source adapter]
    Src -->|MetricPoint[]| An[analytics.engine]
    An --> Stats[DailyStats / Trend / Streak / BurnoutRisk]
    Stats --> Ins[Insights + Recommendations]
    Ins --> UI[Dashboard / notifications / weekly digest]
    Ins --> ML[Future: learned recommender / focus predictor]
```

## Non-negotiable principles that keep the future open
1. **Sensor-agnostic core.** Analytics consume generic `MetricPoint(ts, metric,
   value)` — never camera-specific fields. Adding a sensor = new source that
   emits metric points; the engine is untouched.
2. **Storage behind a protocol.** `Repository` + source adapters mean SQLite can
   become Postgres/Timescale/cloud without touching analytics or detectors.
3. **Swappable intelligence.** Recommendations/insights are pure functions with
   stable signatures; a learned model can replace the rule engine behind them.
4. **Privacy invariant preserved at every layer.** Only derived metrics flow
   downstream — never raw frames — so richer analytics never weaken privacy.
5. **Explainable by default.** Every insight/recommendation carries a rationale,
   which is essential for trust and for later ML evaluation.

## Honesty about current maturity
The analytics layer is a tested **v0**: deterministic, rule-based, and validated
on synthetic data. Burnout risk and recommendations are heuristics, **not**
clinically or empirically validated on real students yet — that validation is
tracked in the [roadmap](ROADMAP.md).
