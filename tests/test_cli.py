from studyguard.cli import _parse_overrides


def test_parse_flags():
    config_path, overrides = _parse_overrides(
        ["--fake", "--headless", "--width", "800", "--no-save", "--db", "x.db"]
    )
    assert config_path is None
    assert overrides["use_fake"] is True
    assert overrides["headless"] is True
    assert overrides["frame_width"] == 800
    assert overrides["persist"] is False
    assert overrides["db_path"] == "x.db"


def test_unset_flags_are_none():
    _, overrides = _parse_overrides([])
    assert overrides["frame_width"] is None
    assert overrides["use_fake"] is None
    assert "mirror" not in overrides  # only set when --no-mirror is passed


def test_no_mirror_sets_false():
    _, overrides = _parse_overrides(["--no-mirror"])
    assert overrides["mirror"] is False
