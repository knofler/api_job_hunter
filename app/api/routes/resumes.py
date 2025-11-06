from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.services import resume_service

router = APIRouter()


class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    resume_type: Optional[str] = None
    metadata: Optional[dict] = None


@router.get("/{user_id}")
async def list_resumes(user_id: str):
    """Get all resumes for a user."""
    resumes = await resume_service.get_resumes(user_id)
    return {"resumes": resumes}


@router.get("/{user_id}/versions/{resume_type}")
async def get_resume_versions(user_id: str, resume_type: str = "general"):
    """Get all versions of a specific resume type."""
    resumes = await resume_service.get_resume_versions(user_id, resume_type)
    return {"resumes": resumes}


@router.get("/resume/{resume_id}")
async def get_resume(resume_id: str):
    """Get a specific resume by ID."""
    resume = await resume_service.get_resume(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"resume": resume}


@router.post("/", status_code=201)
async def upload_resume(
    user_id: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    resume_type: str = Form(default="general"),
    version: Optional[int] = Form(default=None),
    summary: Optional[str] = Form(default=None),
    skills: Optional[str] = Form(default=None),
):
    """Upload a resume and extract text content."""
    file_bytes = await file.read()

    # Parse skills if provided
    parsed_skills = None
    if skills:
        try:
            parsed_skills = json.loads(skills)
        except json.JSONDecodeError:
            parsed_skills = []

    resume_id = await resume_service.upload_resume(
        user_id=user_id,
        name=name,
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
        original_filename=file.filename or name,
        resume_type=resume_type,
        version=version,
        summary=summary,
        skills=parsed_skills,
    )

    return {"resume_id": resume_id, "message": "Resume uploaded and processed successfully"}


@router.patch("/{resume_id}")
async def update_resume(resume_id: str, payload: ResumeUpdate):
    """Update resume metadata."""
    updated = await resume_service.update_resume(resume_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"success": True, "message": "Resume updated successfully"}


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str):
    """Soft delete a resume."""
    deleted = await resume_service.delete_resume(resume_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")