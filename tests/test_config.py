from studyguard.config import Config


def test_defaults():
    config = Config()
    assert config.frame_width == 640
    assert config.persist is True
    assert config.log_level == "INFO"


def test_env_override(monkeypatch):
    monkeypatch.setenv("STUDYGUARD_FRAME_WIDTH", "800")
    monkeypatch.setenv("STUDYGUARD_PERSIST", "false")
    config = Config.load()
    assert config.frame_width == 800
    assert config.persist is False


def test_toml_file(tmp_path, monkeypatch):
    monkeypatch.delenv("STUDYGUARD_FRAME_WIDTH", raising=False)
    path = tmp_path / "studyguard.toml"
    path.write_text("[studyguard]\nframe_width = 720\n", encoding="utf-8")
    config = Config.load(str(path))
    assert config.frame_width == 720


def test_env_beats_file(tmp_path, monkeypatch):
    path = tmp_path / "studyguard.toml"
    path.write_text("[studyguard]\nframe_width = 720\n", encoding="utf-8")
    monkeypatch.setenv("STUDYGUARD_FRAME_WIDTH", "900")
    config = Config.load(str(path))
    assert config.frame_width == 900


def test_merged_ignores_none():
    config = Config().merged(frame_width=None, headless=True)
    assert config.frame_width == 640
    assert config.headless is True
