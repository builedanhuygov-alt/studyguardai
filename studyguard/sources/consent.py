"""Consent management for data sources."""

from __future__ import annotations


class ConsentError(Exception):
    """Raised when consent is required but not granted."""

    pass


class ConsentStore:
    """Manages user consent for data sources."""

    def __init__(self) -> None:
        """Initialize consent store."""
        self._consents: dict[str, bool] = {}

    def has_consent(self, key: str) -> bool:
        """Check if consent is granted for a source."""
        return self._consents.get(key, False)

    def grant(self, key: str) -> None:
        """Grant consent for a source."""
        self._consents[key] = True

    def revoke(self, key: str) -> None:
        """Revoke consent for a source."""
        self._consents[key] = False
