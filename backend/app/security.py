"""Verifies who is calling.

Two separate kinds of token, told apart by their issuer. Each issuer has its own
key and its own fixed list of algorithms, so one kind can never pass as the other.
  - Supabase access tokens (real Google login): asymmetric, checked against JWKS
  - Demo tokens (local development only): HS256 with our own secret
"""
from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

import httpx
import jwt

from app.config import Settings, get_settings
from app.errors import ApiError

log = logging.getLogger("jugnu.auth")

DEMO_ISSUER = "jugnu-demo"
SUPABASE_ALGORITHMS = ["ES256", "RS256"]
JWKS_TTL_SECONDS = 600  # Supabase asks clients not to cache keys longer than 10 minutes
JWKS_MIN_REFRESH_SECONDS = 10  # unknown key ids must not trigger a fetch on every request
CLOCK_SKEW_SECONDS = 30


@dataclass(frozen=True)
class Identity:
    """A verified token. It does not mean the person has a Jugnu account yet."""

    kind: str  # "supabase" or "demo"
    subject: uuid.UUID
    email: str | None = None
    suggested_name: str = ""


def _unauthorized(message: str = "Please log in again.") -> ApiError:
    return ApiError(401, "unauthorized", message)


class JwksCache:
    def __init__(self, fetch: Callable[[], dict[str, Any]]) -> None:
        self._fetch = fetch
        self._lock = threading.Lock()
        self._keys: dict[str, jwt.PyJWK] = {}
        self._loaded_at: float | None = None
        self._attempted_at: float | None = None

    def get(self, kid: str) -> jwt.PyJWK | None:
        with self._lock:
            now = time.monotonic()
            fresh = self._loaded_at is not None and now - self._loaded_at < JWKS_TTL_SECONDS
            if fresh and kid in self._keys:
                return self._keys[kid]
            recent = (
                self._attempted_at is not None
                and now - self._attempted_at < JWKS_MIN_REFRESH_SECONDS
            )
            if not recent:
                self._attempted_at = now
                self._refresh(now)
                fresh = self._loaded_at == now or fresh
            if not fresh:
                raise ApiError(503, "auth_unavailable", "Login is temporarily unavailable.")
            return self._keys.get(kid)

    def _refresh(self, now: float) -> None:
        try:
            entries = self._fetch().get("keys", [])
        except (httpx.HTTPError, ValueError):
            log.warning("could not load the Supabase signing keys", exc_info=True)
            return
        keys: dict[str, jwt.PyJWK] = {}
        for entry in entries:
            try:
                key = jwt.PyJWK.from_dict(entry)
            except jwt.PyJWTError:
                continue
            if key.key_id and key.algorithm_name in SUPABASE_ALGORITHMS:
                keys[key.key_id] = key
        if not keys:
            log.error("Supabase returned no asymmetric signing keys; enable JWT signing keys")
        self._keys, self._loaded_at = keys, now


@lru_cache
def get_jwks() -> JwksCache:
    url = f"{get_settings().supabase_url}/auth/v1/.well-known/jwks.json"

    def fetch() -> dict[str, Any]:
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    return JwksCache(fetch)


def verify_token(token: str, settings: Settings, jwks: JwksCache) -> Identity:
    try:
        issuer = jwt.decode(token, options={"verify_signature": False}).get("iss")
    except jwt.PyJWTError:
        raise _unauthorized() from None

    if issuer == DEMO_ISSUER:
        return _verify_demo(token, settings)
    if settings.supabase_url and issuer == f"{settings.supabase_url}/auth/v1":
        return _verify_supabase(token, issuer, jwks)
    raise _unauthorized()


def _verify_supabase(token: str, issuer: str, jwks: JwksCache) -> Identity:
    try:
        header = jwt.get_unverified_header(token)
        kid, alg = header.get("kid"), header.get("alg")
        if not isinstance(kid, str) or alg not in SUPABASE_ALGORITHMS:
            raise _unauthorized()
        key = jwks.get(kid)
        if key is None or key.algorithm_name != alg:
            raise _unauthorized()
        claims = jwt.decode(
            token, key.key, algorithms=[alg], issuer=issuer, audience="authenticated",
            leeway=CLOCK_SKEW_SECONDS, options={"require": ["exp", "sub", "iss", "aud"]},
        )
        subject = uuid.UUID(claims["sub"])
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized() from None
    if claims.get("is_anonymous") is True or claims.get("role") != "authenticated":
        raise _unauthorized()

    # user_metadata can be edited by the user: only ever a suggestion, never a permission.
    metadata = claims.get("user_metadata")
    name = metadata.get("full_name") or metadata.get("name") if isinstance(metadata, dict) else ""
    email = claims.get("email")
    return Identity(
        kind="supabase",
        subject=subject,
        email=email.strip().lower()[:320] or None if isinstance(email, str) else None,
        suggested_name=name.strip()[:60] if isinstance(name, str) else "",
    )


def _verify_demo(token: str, settings: Settings) -> Identity:
    if not settings.demo_login:
        raise _unauthorized()
    try:
        claims = jwt.decode(
            token, settings.demo_jwt_secret.get_secret_value(), algorithms=["HS256"],
            issuer=DEMO_ISSUER, options={"require": ["exp", "sub", "iss"]},
        )
        return Identity(kind="demo", subject=uuid.UUID(claims["sub"]))
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized() from None


def create_demo_token(user_id: uuid.UUID, settings: Settings) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode(
        {"iss": DEMO_ISSUER, "sub": str(user_id), "exp": expires},
        settings.demo_jwt_secret.get_secret_value(), algorithm="HS256",
    )
