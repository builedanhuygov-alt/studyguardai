import pytest

from studyguard.security import AuthError, RateLimiter, decode_jwt, encode_jwt, verify_api_key


def test_jwt_roundtrip():
    token = encode_jwt({"sub": "u1", "exp": 9999999999}, "secret")
    assert decode_jwt(token, "secret")["sub"] == "u1"


def test_jwt_wrong_secret():
    token = encode_jwt({"sub": "u1"}, "secret")
    with pytest.raises(AuthError):
        decode_jwt(token, "other")


def test_jwt_expired():
    token = encode_jwt({"sub": "u1", "exp": 1}, "secret")
    with pytest.raises(AuthError):
        decode_jwt(token, "secret", now=2.0)


def test_api_key():
    assert verify_api_key("k1", {"k1", "k2"})
    assert not verify_api_key("nope", {"k1"})


def test_rate_limiter():
    clock = [0.0]
    limiter = RateLimiter(2, 1.0, clock=lambda: clock[0])
    assert limiter.allow("a")
    assert limiter.allow("a")
    assert not limiter.allow("a")
    clock[0] = 1.0
    assert limiter.allow("a")
