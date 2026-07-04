"""Security primitives for the API: HS256 JWT, API keys, token-bucket rate limit.

Standard-library only (no PyJWT dependency). These are the building blocks the
FastAPI layer wires up (CORS/CSRF/security headers are configured there).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable


class AuthError(Exception):
    """Raised when a token/key is invalid or expired."""


def _b64url_encode(raw: bytes) -> bytes:
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def encode_jwt(payload: dict, secret: str) -> str:
    """Encode a HS256 JWT."""
    header = {"alg": "HS256", "typ": "JWT"}
    segments = (
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        + b"."
        + _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    )
    signature = hmac.new(secret.encode(), segments, hashlib.sha256).digest()
    return (segments + b"." + _b64url_encode(signature)).decode()


def decode_jwt(token: str, secret: str, *, now: float | None = None) -> dict:
    """Verify a HS256 JWT and return its payload. Raises :class:`AuthError`."""
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise AuthError("malformed token") from exc
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64url_decode(signature_b64)):
        raise AuthError("invalid signature")
    payload = json.loads(_b64url_decode(payload_b64))
    expiry = payload.get("exp")
    if expiry is not None and (now or time.time()) > expiry:
        raise AuthError("token expired")
    return payload


def verify_api_key(candidate: str, valid_keys: set[str]) -> bool:
    """Constant-time check that ``candidate`` is an accepted API key."""
    return any(hmac.compare_digest(candidate, key) for key in valid_keys)


class RateLimiter:
    """Simple per-identity token-bucket rate limiter."""

    def __init__(self, capacity: int, refill_per_second: float, *, clock: Callable[[], float] = time.monotonic) -> None:
        self._capacity = capacity
        self._refill = refill_per_second
        self._clock = clock
        self._buckets: dict[str, tuple[float, float]] = {}

    def allow(self, identity: str) -> bool:
        """Return True if a request from ``identity`` is within the limit."""
        now = self._clock()
        tokens, last = self._buckets.get(identity, (float(self._capacity), now))
        tokens = min(self._capacity, tokens + (now - last) * self._refill)
        if tokens < 1.0:
            self._buckets[identity] = (tokens, now)
            return False
        self._buckets[identity] = (tokens - 1.0, now)
        return True


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
