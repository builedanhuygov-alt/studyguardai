from studyguard.heuristics import PostureFocusConfig, clamp, score_focus, score_posture

CFG = PostureFocusConfig()


def test_clamp_bounds():
    assert clamp(150.0) == 100.0
    assert clamp(-5.0) == 0.0
    assert clamp(42.0) == 42.0


def test_upright_scores_maximum_posture():
    assert score_posture(center_y=0.4, face_ratio=0.35, config=CFG) == 100.0


def test_slouching_lowers_posture():
    upright = score_posture(0.4, 0.35, CFG)
    slouched = score_posture(0.8, 0.35, CFG)
    assert slouched < upright


def test_leaning_back_lowers_posture():
    assert score_posture(0.4, 0.10, CFG) < 100.0


def test_centered_focus_is_maximum():
    assert score_focus(0.5, CFG) == 100.0


def test_off_center_lowers_focus():
    assert score_focus(0.9, CFG) < score_focus(0.55, CFG)


def test_extreme_offset_is_clamped_to_zero():
    assert score_focus(1.5, CFG) == 0.0


def test_config_is_injectable():
    strict = PostureFocusConfig(off_center_penalty=400.0)
    assert score_focus(0.7, strict) < score_focus(0.7, CFG)
