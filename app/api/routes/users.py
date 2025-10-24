from fastapi import APIRouter

from app.services import user_service

router = APIRouter()


@router.get("/")
async def get_users(limit: int = 100):
    users = await user_service.get_all_users(limit=limit)
    return {"users": users}