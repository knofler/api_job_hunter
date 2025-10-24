from fastapi import APIRouter, HTTPException, Query

from app.services import candidate_service

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/")
async def list_candidates(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    return await candidate_service.list_candidates(page=page, page_size=page_size)


@router.get("/{candidate_id}")
async def get_candidate_profile(candidate_id: str):
    profile = await candidate_service.get_candidate_profile(candidate_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return profile


@router.get("/{candidate_id}/resumes")
async def get_candidate_resumes(candidate_id: str):
    resumes = await candidate_service.get_candidate_resumes(candidate_id)
    return {"resumes": resumes}


@router.get("/{candidate_id}/resume-health")
async def get_resume_health(candidate_id: str):
    health = await candidate_service.get_resume_health(candidate_id)
    if not health:
        raise HTTPException(status_code=404, detail="Resume health not found")
    return health


@router.get("/{candidate_id}/suggested-actions")
async def get_suggested_actions(candidate_id: str):
    actions = await candidate_service.get_suggested_actions(candidate_id)
    return {"actions": actions}


@router.get("/{candidate_id}/pipeline")
async def get_pipeline(candidate_id: str):
    pipeline = await candidate_service.get_pipeline(candidate_id)
    return {"pipeline": pipeline}


@router.get("/{candidate_id}/top-matches")
async def get_top_matches(candidate_id: str, limit: int = 5):
    matches = await candidate_service.get_top_matches(candidate_id, limit)
    return {"jobs": matches}


@router.get("/{candidate_id}/dashboard")
async def get_dashboard(candidate_id: str):
    snapshot = await candidate_service.get_dashboard_snapshot(candidate_id)
    return snapshot
