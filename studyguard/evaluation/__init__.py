"""Classification-metric toolkit for reproducible AI evaluation.

Pure standard-library implementations (no scikit-learn dependency) so metrics
are deterministic, auditable, and runnable anywhere.
"""
from studyguard.evaluation.metrics import (
    auc,
    calibration_curve,
    confusion_matrix,
    precision_recall_f1,
    roc_curve,
)

__all__ = [
    "confusion_matrix",
    "precision_recall_f1",
    "roc_curve",
    "auc",
    "calibration_curve",
]
