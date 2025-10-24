from fastapi import APIRouter, Query

from app.services import recruiter_service

router = APIRouter(prefix="/recruiters", tags=["recruiters"])


@router.get("/")
async def list_recruiters(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return await recruiter_service.list_recruiters(page=page, page_size=page_size)
