from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings
from app.core.database import db
from app.core.auth import AuthError, get_org_from_claims, get_roles_from_claims, verify_jwt


def get_database():
    return db


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


async def require_user(authorization: Optional[str] = Header(default=None, alias="Authorization")) -> dict:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        claims = verify_jwt(token)
        return {
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "email_verified": claims.get("email_verified", False),
            "roles": get_roles_from_claims(claims),
            "org_id": get_org_from_claims(claims),
            "claims": claims,
        }
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


async def require_admin(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
) -> dict:
    # Prefer JWT roles; fallback to legacy X-Admin-Token if ADMIN_API_KEY is set
    if authorization:
        user = await require_user(authorization)  # type: ignore[arg-type]
        roles = set(user.get("roles", []))
        if roles.intersection({"admin", "power_user"}):
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    expected = settings.ADMIN_API_KEY
    if expected and x_admin_token == expected:
        return {"sub": "admin-token", "roles": ["admin"]}
    if expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin credentials")
    # If no auth configured at all, deny by default
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


AdminDependency = Depends(require_admin)
UserDependency = Depends(require_user)