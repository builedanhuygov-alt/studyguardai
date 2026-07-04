# Datasets

Reproducible data for evaluation and benchmarking. **No raw video is stored** —
only labels and derived metrics, consistent with the privacy invariant.

```
datasets/
  labels/       # per-clip status labels (JSON arrays)
  evaluation/   # curated labeled sets for accuracy metrics
  benchmark/    # inputs/config for performance benchmarks
```

## Label format
A label file is a JSON array of expected statuses per sampled frame, e.g.
`["AWAY", "FOCUSED", "SLOUCHING", ...]`. See `labels/sample_labels.json`.

Use with `studyguard.eval` / `studyguard.evaluation.metrics` (precision, recall,
F1, confusion matrix, ROC/AUC, calibration).

Status: ✅ folders + sample labels generated. ⚠ A real, consented labeled clip set
is still needed before publishing accuracy numbers (tracked in the roadmap).
