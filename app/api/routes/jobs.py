from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services import job_service

router = APIRouter()


class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    posted_at: Optional[datetime] = None


class JobDescriptionUpdate(BaseModel):
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)


@router.get("/")
async def list_jobs(
    candidate_id: Optional[str] = Query(default=None, description="Candidate identifier to compute match score"),
    search: Optional[str] = Query(default=None, description="Search term for title, company or location"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    exclude_applied: bool = Query(default=False, description="Exclude jobs already applied for by the candidate"),
):
    return await job_service.list_jobs(
        candidate_id=candidate_id,
        search=search,
        page=page,
        page_size=page_size,
        exclude_applied=exclude_applied,
    )


@router.get("/descriptions")
async def list_job_descriptions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    """List all job descriptions for the recruiter workflow."""
    return await job_service.list_job_descriptions(page=page, page_size=page_size)


@router.put("/descriptions/{job_id}")
async def update_job_description(job_id: str, update: JobDescriptionUpdate):
    """Update a job description."""
    updated_job = await job_service.update_job_description(job_id, update.dict(exclude_unset=True))
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job


@router.get("/{job_id}")
async def get_job(job_id: str, candidate_id: Optional[str] = None):
    job = await job_service.get_job(job_id, candidate_id=candidate_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", status_code=201)
async def create_job(job: JobCreate):
    job_id = await job_service.create_job(job.dict(exclude_unset=True))
    return {"job_id": job_id}