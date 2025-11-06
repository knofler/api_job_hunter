from datetime import datetime
from typing import List, Optional
import json

from fastapi import APIRouter, File, Form, Header, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.api.dependencies import UserDependency
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


@router.post("/upload-jd", status_code=201)
async def upload_job_description(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
    title: str = Form(...),
    file: UploadFile = File(...),
    company: Optional[str] = Form(default=None),
    budget: Optional[str] = Form(default=None),
    job_brief: Optional[str] = Form(default=None),
    additional_details: Optional[str] = Form(default=None, description="JSON-encoded additional details"),
):
    """Upload a job description file and create a job entry."""
    from app.core.config import settings
    from app.api.dependencies import _extract_bearer_token
    from app.core.auth import verify_jwt, get_roles_from_claims, get_org_from_claims, AuthError

    # Check for admin token first
    expected_admin_token = settings.ADMIN_API_KEY
    if expected_admin_token and x_admin_token == expected_admin_token:
        # Admin user
        user = {"sub": "admin", "roles": ["admin"], "org_id": None}
    else:
        # Try JWT authentication
        token = _extract_bearer_token(authorization)
        if not token:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        try:
            claims = verify_jwt(token)
            user = {
                "sub": claims.get("sub"),
                "email": claims.get("email"),
                "email_verified": claims.get("email_verified", False),
                "roles": get_roles_from_claims(claims),
                "org_id": get_org_from_claims(claims),
                "claims": claims,
            }
        except AuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    # Verify the user has recruiter role
    roles = user.get("roles", [])
    if "recruiter" not in roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Recruiter role required")

    # Get recruiter_id from authenticated user
    recruiter_id = user["sub"]

    file_bytes = await file.read()

    # Parse additional details if provided
    parsed_details = None
    if additional_details:
        try:
            parsed_details = json.loads(additional_details)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid additional_details JSON")

    job_id = await job_service.upload_job_description(
        recruiter_id=recruiter_id,
        title=title,
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
        original_filename=file.filename or title,
        company=company,
        budget=budget,
        job_brief=job_brief,
        additional_details=parsed_details,
    )

    return {
        "job_id": job_id,
        "message": "Job description uploaded and processed successfully"
    }


@router.get("/recruiter/{recruiter_id}")
async def get_jobs_by_recruiter(
    recruiter_id: str,
    user: dict = UserDependency,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    """Get all jobs uploaded by a specific recruiter."""
    # Verify the user has recruiter role or is admin
    roles = user.get("roles", [])
    if "recruiter" not in roles and "admin" not in roles:
        raise HTTPException(status_code=403, detail="Recruiter role required")

    # Users can only see their own jobs unless they're admin
    if "admin" not in roles and recruiter_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Can only access your own jobs")

    return await job_service.get_jobs_by_recruiter(recruiter_id, page, page_size)


@router.get("/company/{company}")
async def get_jobs_by_company(
    company: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
):
    """Get all jobs for a specific company."""
    return await job_service.get_jobs_by_company(company, page, page_size)