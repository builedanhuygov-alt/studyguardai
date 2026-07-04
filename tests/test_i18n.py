from studyguard.i18n import available_languages, translate


def test_translate_and_fallback():
    assert translate("nav.overview", "vi") == "T\u1ed5ng quan"
    assert translate("nav.overview", "ja")
    assert translate("missing.key", "en") == "missing.key"


def test_translate_format():
    assert "3" in translate("goal.streak", "en", days=3)


def test_supported_languages():
    assert set(available_languages()) == {"en", "vi", "ja"}
