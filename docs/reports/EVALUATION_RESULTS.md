# Model Evaluation Results

> **Self-evaluation on a synthetic geometry dataset with noise** — it measures
> how well the posture/focus decision logic recovers the latent study state.
> These are **not** human-validated accuracy numbers. To produce those, label
> real clips with `tools/label_clip.py` and re-run this script.

Samples: 2000 (present: 1705).

## Posture detection (poor-posture class)
- Precision: 100.0%
- Recall: 88.2%
- F1: 93.8%

## Focus detection (distracted class)
- Precision: 100.0%
- Recall: 92.4%
- F1: 96.0%
- ROC AUC: 1.0

## Status classification (macro)
- Precision: 95.9%
- Recall: 95.0%
- F1: 95.3%

### Confusion matrix (rows = true, cols = predicted)

| | AWAY | DISTRACTED | SLOUCHING | FOCUSED |
| --- | --- | --- | --- | --- |
| **AWAY** | 295 | 0 | 0 | 0 |
| **DISTRACTED** | 0 | 633 | 15 | 37 |
| **SLOUCHING** | 0 | 0 | 346 | 49 |
| **FOCUSED** | 0 | 0 | 0 | 625 |

