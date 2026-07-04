from studyguard.evaluation.pipeline import evaluate, generate_dataset, predict_status


def _sample(present=True, cx=0.5, cy=0.4, ratio=0.34):
    return {"present": present, "center_x": cx, "center_y": cy, "face_ratio": ratio}


def test_predict_status_cases():
    assert predict_status(_sample(present=False)) == "AWAY"
    assert predict_status(_sample()) == "FOCUSED"
    assert predict_status(_sample(cx=0.95)) == "DISTRACTED"
    assert predict_status(_sample(cy=0.75, ratio=0.2)) == "SLOUCHING"


def test_evaluate_metrics_are_sane():
    report = evaluate(generate_dataset(500, seed=1))
    assert 0.0 <= report["posture_detection"]["f1"] <= 1.0
    assert 0.0 <= report["focus_detection"]["f1"] <= 1.0
    assert report["status"]["macro"]["f1"] > 0.7
    assert 0.0 <= report["focus_roc_auc"] <= 1.0
    assert len(report["status"]["confusion"]) == 4
