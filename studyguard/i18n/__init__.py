"""Minimal internationalization (English, Vietnamese, Japanese).

Standard-library only. ``translate(key, lang)`` falls back to English, then to
the key itself, and supports ``str.format`` keyword substitution.
"""
from __future__ import annotations

DEFAULT_LANG = "en"
SUPPORTED = ("en", "vi", "ja")

_CATALOG: dict[str, dict[str, str]] = {
    "app.title": {"en": "StudyGuard AI", "vi": "StudyGuard AI", "ja": "StudyGuard AI"},
    "app.tagline": {
        "en": "Your privacy-first AI study coach",
        "vi": "Hu\u1ea5n luy\u1ec7n vi\u00ean h\u1ecdc t\u1eadp AI \u01b0u ti\u00ean ri\u00eang t\u01b0",
        "ja": "\u30d7\u30e9\u30a4\u30d0\u30b7\u30fc\u91cd\u8996\u306eAI\u5b66\u7fd2\u30b3\u30fc\u30c1",
    },
    "nav.overview": {"en": "Overview", "vi": "T\u1ed5ng quan", "ja": "\u6982\u8981"},
    "nav.coach": {"en": "AI Coach", "vi": "Hu\u1ea5n luy\u1ec7n AI", "ja": "AI\u30b3\u30fc\u30c1"},
    "nav.analytics": {"en": "Analytics", "vi": "Ph\u00e2n t\u00edch", "ja": "\u5206\u6790"},
    "coach.focus_up": {
        "en": "You focused better than yesterday",
        "vi": "B\u1ea1n t\u1eadp trung t\u1ed1t h\u01a1n h\u00f4m qua",
        "ja": "\u6628\u65e5\u3088\u308a\u96c6\u4e2d\u3067\u304d\u307e\u3057\u305f",
    },
    "goal.streak": {
        "en": "{days}-day streak",
        "vi": "Chu\u1ed7i {days} ng\u00e0y",
        "ja": "{days}\u65e5\u9023\u7d9a",
    },
}


def translate(key: str, lang: str = DEFAULT_LANG, **kwargs: object) -> str:
    """Translate ``key`` into ``lang`` with fallback to English then the key."""
    entry = _CATALOG.get(key, {})
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def available_languages() -> tuple[str, ...]:
    """Return supported language codes."""
    return SUPPORTED
