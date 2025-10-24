from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import application_service

router = APIRouter(prefix="/applications", tags=["applications"])
@router.get("/candidates/{candidate_id}")
async def list_candidate_applications(
    candidate_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    result = await application_service.list_candidate_applications(
        candidate_id=candidate_id,
        page=page,
        page_size=page_size,
    )
    return result


class ApplicationCreate(BaseModel):
    job_id: str
    resume_id: str
    note: str | None = None


class ApplicationUpdate(BaseModel):
    status: str



@router.post("/", status_code=201)
async def create_application(candidate_id: str, payload: ApplicationCreate):
    try:
        application_id = await application_service.create_application(
            candidate_id=candidate_id,
            job_id=payload.job_id,
            resume_id=payload.resume_id,
            note=payload.note,
        )
    except ValueError as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"application_id": application_id}


@router.patch("/{application_id}")
async def update_application(candidate_id: str, application_id: str, payload: ApplicationUpdate):
    updated = await application_service.update_application_status(
        candidate_id=candidate_id,
        application_id=application_id,
        status=payload.status,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"success": True}
