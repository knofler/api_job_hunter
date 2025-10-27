from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings
from app.core.database import db


def get_database():
    return db


async def require_admin(x_admin_token: str = Header(default="", alias="X-Admin-Token")) -> None:
    expected = settings.ADMIN_API_KEY
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API key is not configured",
        )
    if x_admin_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin credentials")


AdminDependency = Depends(require_admin)