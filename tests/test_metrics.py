from studyguard.evaluation.metrics import (
    auc,
    calibration_curve,
    confusion_matrix,
    precision_recall_f1,
    roc_curve,
)


def test_confusion_matrix():
    assert confusion_matrix(["a", "a", "b"], ["a", "b", "b"], ["a", "b"]) == [[1, 1], [0, 1]]


def test_precision_recall_f1_perfect():
    result = precision_recall_f1(["a", "b", "a"], ["a", "b", "a"], ["a", "b"])
    assert result["macro"]["f1"] == 1.0


def test_roc_auc_known_value():
    fpr, tpr = roc_curve([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])
    assert auc(fpr, tpr) == 0.75


def test_calibration_curve():
    curve = calibration_curve([0, 1, 1], [0.2, 0.6, 0.9], bins=5)
    assert curve
    assert all("mean_predicted" in bucket and "fraction_positive" in bucket for bucket in curve)
