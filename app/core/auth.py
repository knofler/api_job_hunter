from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings


class AuthError(Exception):
    pass


@lru_cache(maxsize=1)
def _issuer() -> str:
    if settings.AUTH0_ISSUER:
        return settings.AUTH0_ISSUER.rstrip("/")
    if settings.AUTH0_DOMAIN:
        return f"https://{settings.AUTH0_DOMAIN.rstrip('/')}"
    raise AuthError("Auth0 domain/issuer not configured")


@lru_cache(maxsize=1)
def _jwks_uri() -> str:
    return f"{_issuer()}/.well-known/jwks.json"


@lru_cache(maxsize=1)
def _audience() -> Optional[str]:
    return settings.AUTH0_AUDIENCE


@lru_cache(maxsize=1)
def _algorithms() -> List[str]:
    return [alg.strip() for alg in settings.AUTH0_ALGORITHMS.split(",") if alg.strip()] or ["RS256"]


@lru_cache(maxsize=1)
def _jwks() -> Dict[str, Any]:
    # Fetch JWKS once; Render dynos will refresh on deploy
    with httpx.Client(timeout=5.0) as client:
        resp = client.get(_jwks_uri())
        resp.raise_for_status()
        return resp.json()


def _get_key(token: str) -> Dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise AuthError("Missing kid in token header")
    keys = _jwks().get("keys", [])
    for key in keys:
        if key.get("kid") == kid:
            return key
    raise AuthError("Unable to find matching JWK for token")


def verify_jwt(token: str) -> Dict[str, Any]:
    key = _get_key(token)
    issuer = _issuer()
    audience = _audience()
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=_algorithms(),
            audience=audience if audience else None,
            issuer=issuer,
            options={"verify_aud": bool(audience)},
        )
        return claims
    except JWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc


def get_roles_from_claims(claims: Dict[str, Any]) -> List[str]:
    # Try common locations for roles
    # 1) Auth0 RBAC custom claim (e.g., https://your-domain/roles)
    for k, v in claims.items():
        if isinstance(v, list) and all(isinstance(i, str) for i in v) and k.endswith("/roles"):
            return list(v)
    # 2) Standard permissions array
    if isinstance(claims.get("permissions"), list):
        return [str(p) for p in claims["permissions"]]
    # 3) No roles
    return []


def get_org_from_claims(claims: Dict[str, Any]) -> Optional[str]:
    # Prefer org_id custom claim if present
    for key in ("org_id", "organization", "org"):
        if key in claims and isinstance(claims[key], str):
            return claims[key]
    # Auth0 Organizations provide 'org_id' in the ID token; may be absent in access token
    return None
