# Reproducible AI Evaluation

Every AI component ships with a **measurable, reproducible** evaluation procedure.
Today the only learned-ish components are the posture/focus heuristic and the
rule-based burnout/recommendation logic — both are **Experiment** grade.

## Components & their evaluation

| Component | Dataset | Harness | Metric | Status |
| --- | --- | --- | --- | --- |
| Posture/Focus scoring | labeled clip (statuses) | `studyguard.eval` | status accuracy | Experiment |
| Per-metric bands | labeled bands | `studyguard.eval_gates` | posture ≥70%, focus ≥65% | Experiment (thresholds set, not met on real data yet) |
| Burnout / recommendations | — | deterministic unit checks | behavior correctness | Experiment (quality unvalidated) |

## Dataset format
A labeled clip is a JSON array of expected statuses per sampled frame — see
`examples/labels.sample.json`. Load with `studyguard.eval.load_labels`.

## Reproduce
```bash
PYTHONPATH=. python examples/run_eval_example.py   # synthetic clip demo
```
With a real labeled clip:
```python
from studyguard.core import Aggregator
from studyguard.detectors import PostureFocusDetector
from studyguard.eval import evaluate, load_labels
from studyguard.eval_gates import evaluate_metric, passes_gates
# frames: list[np.ndarray] sampled from the clip; labels: list[str]
report = evaluate(frames, load_labels("labels.json"), PostureFocusDetector(), Aggregator())
print(report.accuracy)
```

## Comparison report
Because thresholds are versioned constants (`POSTURE_MIN_ACCURACY`,
`FOCUS_MIN_ACCURACY`) and the harness is deterministic, two runs on the same
clip are directly comparable across commits.

## Honesty
No accuracy number is published yet because no real labeled dataset exists.
Producing one (a few short, consented, labeled clips across lighting/angles) is
the top item on the roadmap before any accuracy claim is made.
