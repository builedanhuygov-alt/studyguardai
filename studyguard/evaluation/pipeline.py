"""End-to-end evaluation of the posture/focus decision logic.

We sample a **latent** study state (present / good-posture / good-focus), render
*noisy* face geometry consistent with it, then measure how well the heuristic
(`studyguard.heuristics`) + aggregator recover that latent state. This yields
honest, non-trivial metrics (errors occur near thresholds) for the decision
layer — it is NOT a human-validated accuracy of face detection.
"""
from __future__ import annotations

import random
from collections.abc import Sequence

from studyguard.core import Aggregator, Analysis
from studyguard.evaluation.metrics import auc, calibration_curve, confusion_matrix, precision_recall_f1, roc_curve
from studyguard.heuristics import PostureFocusConfig, score_focus, score_posture

STATUSES = ["AWAY", "DISTRACTED", "SLOUCHING", "FOCUSED"]
_POSTURE_ALERT = 55.0
_FOCUS_ALERT = 50.0


def _gt_status(present: bool, posture_good: bool, focus_good: bool) -> str:
    if not present:
        return "AWAY"
    if not focus_good:
        return "DISTRACTED"
    if not posture_good:
        return "SLOUCHING"
    return "FOCUSED"


def generate_dataset(n: int = 1000, seed: int = 7) -> list[dict]:
    """Create a labeled synthetic geometry dataset with realistic noise."""
    rng = random.Random(seed)
    samples: list[dict] = []
    for _ in range(n):
        present = rng.random() < 0.85
        posture_good = rng.random() < 0.6
        focus_good = rng.random() < 0.6
        if posture_good:
            center_y = rng.gauss(0.42, 0.04)
            face_ratio = rng.gauss(0.34, 0.03)
        else:
            center_y = rng.gauss(0.72, 0.05)
            face_ratio = rng.gauss(0.22, 0.03)
        if focus_good:
            center_x = rng.gauss(0.5, 0.06)
        else:
            center_x = rng.gauss(0.5 + rng.choice((-1, 1)) * 0.32, 0.05)
        samples.append(
            {
                "present": present,
                "posture_good": posture_good,
                "focus_good": focus_good,
                "center_x": center_x,
                "center_y": center_y,
                "face_ratio": face_ratio,
                "gt": _gt_status(present, posture_good, focus_good),
            }
        )
    return samples


def _scores(sample: dict, config: PostureFocusConfig) -> tuple[float, float]:
    if not sample["present"]:
        return config.absent_posture, config.absent_focus
    posture = score_posture(sample["center_y"], sample["face_ratio"], config)
    focus = score_focus(sample["center_x"], config)
    return posture, focus


def predict_status(sample: dict, config: PostureFocusConfig | None = None) -> str:
    """Predict the aggregated status for one sample (fresh aggregator, no lag)."""
    cfg = config or PostureFocusConfig()
    posture, focus = _scores(sample, cfg)
    analysis = Analysis("study", sample["present"], {"posture": posture, "focus": focus})
    snapshot = Aggregator(smoothing=1.0).build(
        [analysis], frame_index=0, fps=0.0, elapsed_s=0.0, distractions=0
    )
    return snapshot.status


def _binary(y_true: list[str], y_pred: list[str], positive: str = "poor") -> dict:
    result = precision_recall_f1(y_true, y_pred, ["ok", positive])
    return result["per_label"][positive]


def evaluate(samples: Sequence[dict], config: PostureFocusConfig | None = None) -> dict:
    """Return status confusion + posture/focus binary metrics + focus ROC/AUC."""
    cfg = config or PostureFocusConfig()
    y_true = [s["gt"] for s in samples]
    y_pred = [predict_status(s, cfg) for s in samples]
    status_metrics = precision_recall_f1(y_true, y_pred, STATUSES)
    status_conf = confusion_matrix(y_true, y_pred, STATUSES)

    present = [s for s in samples if s["present"]]
    posture_true = ["poor" if not s["posture_good"] else "ok" for s in present]
    posture_pred = ["poor" if _scores(s, cfg)[0] < _POSTURE_ALERT else "ok" for s in present]
    focus_true = ["poor" if not s["focus_good"] else "ok" for s in present]
    focus_pred = ["poor" if _scores(s, cfg)[1] < _FOCUS_ALERT else "ok" for s in present]

    roc_labels = [0 if s["focus_good"] else 1 for s in present]
    roc_scores = [1.0 - _scores(s, cfg)[1] / 100.0 for s in present]
    fpr, tpr = roc_curve(roc_labels, roc_scores)

    return {
        "n": len(samples),
        "n_present": len(present),
        "status": {"labels": STATUSES, "confusion": status_conf, "macro": status_metrics["macro"], "per_label": status_metrics["per_label"]},
        "posture_detection": _binary(posture_true, posture_pred),
        "focus_detection": _binary(focus_true, focus_pred),
        "focus_roc_auc": auc(fpr, tpr),
        "focus_calibration": calibration_curve(roc_labels, roc_scores, bins=5),
    }
