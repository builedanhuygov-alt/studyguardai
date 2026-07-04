"""Classification metrics: confusion matrix, precision/recall/F1, ROC, AUC,
calibration. Pure Python for determinism and zero heavy dependencies.
"""
from __future__ import annotations

from collections.abc import Sequence


def confusion_matrix(y_true: Sequence, y_pred: Sequence, labels: Sequence) -> list[list[int]]:
    """Return the confusion matrix as rows=true, cols=predicted (label order)."""
    index = {label: i for i, label in enumerate(labels)}
    matrix = [[0] * len(labels) for _ in labels]
    for true, pred in zip(y_true, y_pred, strict=True):
        matrix[index[true]][index[pred]] += 1
    return matrix


def precision_recall_f1(y_true: Sequence, y_pred: Sequence, labels: Sequence) -> dict:
    """Per-label precision/recall/F1 plus macro averages."""
    matrix = confusion_matrix(y_true, y_pred, labels)
    per_label: dict[str, dict[str, float]] = {}
    precisions, recalls, f1s = [], [], []
    for i, label in enumerate(labels):
        tp = matrix[i][i]
        fp = sum(matrix[r][i] for r in range(len(labels))) - tp
        fn = sum(matrix[i]) - tp
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_label[str(label)] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
    count = len(labels) or 1
    return {
        "per_label": per_label,
        "macro": {
            "precision": round(sum(precisions) / count, 4),
            "recall": round(sum(recalls) / count, 4),
            "f1": round(sum(f1s) / count, 4),
        },
    }


def roc_curve(y_true: Sequence[int], scores: Sequence[float]) -> tuple[list[float], list[float]]:
    """Return (fpr, tpr) points for binary labels (0/1) and decision scores."""
    positives = sum(1 for y in y_true if y == 1)
    negatives = len(y_true) - positives
    ordered = sorted(zip(scores, y_true, strict=True), key=lambda pair: pair[0], reverse=True)
    tpr, fpr = [0.0], [0.0]
    tp = fp = 0
    for _score, label in ordered:
        if label == 1:
            tp += 1
        else:
            fp += 1
        tpr.append(tp / positives if positives else 0.0)
        fpr.append(fp / negatives if negatives else 0.0)
    return fpr, tpr


def auc(fpr: Sequence[float], tpr: Sequence[float]) -> float:
    """Trapezoidal area under the ROC curve."""
    area = 0.0
    for i in range(1, len(fpr)):
        area += (fpr[i] - fpr[i - 1]) * (tpr[i] + tpr[i - 1]) / 2.0
    return round(area, 4)


def calibration_curve(
    y_true: Sequence[int], probabilities: Sequence[float], bins: int = 10
) -> list[dict]:
    """Reliability bins: mean predicted probability vs observed positive rate."""
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for prob, label in zip(probabilities, y_true, strict=True):
        idx = min(int(prob * bins), bins - 1)
        buckets[idx].append((prob, label))
    curve = []
    for i, bucket in enumerate(buckets):
        if not bucket:
            continue
        mean_pred = sum(p for p, _ in bucket) / len(bucket)
        frac_pos = sum(y for _, y in bucket) / len(bucket)
        curve.append(
            {
                "bin": i,
                "mean_predicted": round(mean_pred, 4),
                "fraction_positive": round(frac_pos, 4),
                "count": len(bucket),
            }
        )
    return curve
