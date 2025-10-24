from __future__ import annotations

import json
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services import resume_service

router = APIRouter()


class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    preview: Optional[str] = None
    skills: Optional[List[str]] = Field(default=None, description="List of skills to associate with the resume")
    type: Optional[str] = None


@router.get("/{candidate_id}")
async def list_resumes(candidate_id: str):
    resumes = await resume_service.get_resumes(candidate_id)
    return {"resumes": resumes}


@router.post("/", status_code=201)
async def upload_resume(
    candidate_id: str = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    summary: Optional[str] = Form(default=None),
    skills: Optional[str] = Form(default=None, description="JSON-encoded list of skills"),
    preview: Optional[str] = Form(default=None),
    resume_type: Optional[str] = Form(default=None),
):
    file_bytes = await file.read()

    parsed_skills: Optional[List[str]] = None
    if skills:
        try:
            parsed_skills = json.loads(skills)
        except json.JSONDecodeError as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="Invalid skills payload") from exc

    resume_id = await resume_service.upload_resume(
        candidate_id=candidate_id,
        name=name,
        file_bytes=file_bytes,
        content_type=file.content_type or "application/octet-stream",
        original_filename=file.filename or name,
        summary=summary,
        skills=parsed_skills,
        preview=preview,
        resume_type=resume_type,
    )

    return {"resume_id": resume_id}


@router.patch("/{resume_id}")
async def update_resume(resume_id: str, payload: ResumeUpdate):
    updated = await resume_service.update_resume(resume_id, payload.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"success": True}


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: str):
    deleted = await resume_service.delete_resume(resume_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")