from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from bson import ObjectId
from PyPDF2 import PdfReader
import docx

from app.core.database import db
from app.services.ranking_service import calculate_ranking


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from PDF file."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return ""


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from DOCX file."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception:
        return ""


def _extract_text_from_file(file_bytes: bytes, content_type: str, filename: str) -> str:
    """Extract text content from uploaded file based on type."""
    filename_lower = filename.lower()

    if content_type == "application/pdf" or filename_lower.endswith(".pdf"):
        return _extract_text_from_pdf(file_bytes)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename_lower.endswith((".docx", ".doc")):
        return _extract_text_from_docx(file_bytes)
    else:
        # For other file types, try to decode as text
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return ""


def _serialize_job_document(document: Dict[str, Any]) -> Dict[str, Any]:
    job = document.copy()
    job["id"] = str(job.pop("_id"))
    posted_at = job.get("posted_at")
    if isinstance(posted_at, datetime):
        job["posted_at"] = posted_at.isoformat()
    return job


async def _get_candidate_skillset(candidate_id: str) -> List[str]:
    candidate = await db.candidates.find_one({"candidate_id": candidate_id})
    skills: List[str] = candidate.get("skills", []) if candidate else []

    latest_resume = await db.resumes.find_one(
        {"candidate_id": candidate_id},
        sort=[("last_updated", -1)],
    )
    if latest_resume:
        combined = set(skills) | set(latest_resume.get("skills", []))
        return sorted(combined)
    return skills


async def list_jobs(
    *,
    candidate_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    exclude_applied: bool = False,
) -> Dict[str, Any]:
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    query: Dict[str, Any] = {}
    if search:
        query = {
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
            ]
        }

    total = await db.jobs.count_documents(query)

    cursor = (
        db.jobs.find(query)
        .sort([
            ("is_curated", -1),  # Sort curated jobs first
            ("posted_at", -1)
        ])
        .skip(skip)
        .limit(page_size * 2 if exclude_applied else page_size)
    )
    raw_jobs = await cursor.to_list(length=page_size * 2 if exclude_applied else page_size)

    candidate_skills: Iterable[str] = []
    applied_job_ids: set[ObjectId] = set()

    if candidate_id:
        candidate_skills = await _get_candidate_skillset(candidate_id)
        if exclude_applied:
            applied_cursor = db.applications.find(
                {"candidate_id": candidate_id},
                {"job_id": 1},
            )
            applied_job_ids = {
                application["job_id"] async for application in applied_cursor
            }

    serialised: List[Dict[str, Any]] = []
    for raw_job in raw_jobs:
        if exclude_applied and raw_job["_id"] in applied_job_ids:
            continue

        job = _serialize_job_document(raw_job)
        if candidate_skills:
            job["match_score"] = calculate_ranking(
                candidate_skills, raw_job.get("skills", [])
            )
        serialised.append(job)

    if exclude_applied and len(serialised) > page_size:
        serialised = serialised[:page_size]

    return {
        "items": serialised,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_job(job_id: str, *, candidate_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        object_id = ObjectId(job_id)
    except Exception:
        return None

    job = await db.jobs.find_one({"_id": object_id})
    if not job:
        return None

    serialised = _serialize_job_document(job)
    if candidate_id:
        candidate_skills = await _get_candidate_skillset(candidate_id)
        serialised["match_score"] = calculate_ranking(
            candidate_skills, job.get("skills", [])
        )
    return serialised


async def create_job(job_data: Dict[str, Any]) -> str:
    document = job_data.copy()
    document.setdefault("created_at", datetime.utcnow())
    document.setdefault("posted_at", datetime.utcnow())

    result = await db.jobs.insert_one(document)
    return str(result.inserted_id)


async def update_job(job_id: str, update_data: Dict[str, Any]) -> bool:
    try:
        object_id = ObjectId(job_id)
    except Exception:
        return False

    payload = {**update_data, "updated_at": datetime.utcnow()}
    result = await db.jobs.update_one({"_id": object_id}, {"$set": payload})
    return result.modified_count > 0


async def get_top_matches(
    candidate_id: str,
    *,
    limit: int = 5,
    exclude_applied: bool = True,
) -> List[Dict[str, Any]]:
    jobs_payload = await list_jobs(
        candidate_id=candidate_id,
        page=1,
        page_size=200,
        exclude_applied=exclude_applied,
    )
    jobs = jobs_payload["items"]
    sorted_jobs = sorted(
        jobs,
        key=lambda job: job.get("match_score", 0.0),
        reverse=True,
    )
    return sorted_jobs[:limit]


async def list_job_descriptions(*, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """List job descriptions for the recruiter workflow."""
    page = max(page, 1)
    page_size = max(1, min(page_size, 50))
    skip = (page - 1) * page_size

    # Only return curated jobs (not auto-generated ones) for the recruiter workflow
    query = {"is_curated": True}

    total = await db.jobs.count_documents(query)

    cursor = (
        db.jobs.find(query, {
            "_id": 1,
            "slug": 1,
            "title": 1,
            "company": 1,
            "description": 1,
            "jd_content": 1,
            "responsibilities": 1,
            "requirements": 1,
            "skills": 1,
            "location": 1,
            "employment_type": 1,
            "salary_range": 1,
            "code": 1,
            "is_curated": 1,
            "updated_at": 1
        })
        .sort("title", 1)
        .skip(skip)
        .limit(page_size)
    )

    raw_jobs = await cursor.to_list(length=page_size)
    serialised = []
    for job in raw_jobs:
        # Ensure required fields are present with defaults
        job.setdefault("skills", [])
        job.setdefault("responsibilities", [])
        job.setdefault("requirements", [])
        
        # If description is missing but jd_content exists, use jd_content as description
        if not job.get("description") and job.get("jd_content"):
            job["description"] = job["jd_content"][:500]  # Use first 500 chars of jd_content
        
        serialised.append(_serialize_job_document(job))

    return {
        "items": serialised,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def update_job_description(job_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a job description."""
    try:
        object_id = ObjectId(job_id)
    except Exception:
        return None

    payload = {**update_data, "updated_at": datetime.utcnow()}
    result = await db.jobs.update_one({"_id": object_id}, {"$set": payload})

    if result.modified_count > 0:
        updated_job = await db.jobs.find_one({"_id": object_id})
        return _serialize_job_document(updated_job) if updated_job else None

    return None


async def upload_job_description(
    *,
    recruiter_id: str,
    title: str,
    file_bytes: bytes,
    content_type: str,
    original_filename: str,
    company: Optional[str] = None,
    budget: Optional[str] = None,
    job_brief: Optional[str] = None,
    additional_details: Optional[Dict[str, Any]] = None,
) -> str:
    """Upload a job description and extract its text content."""

    # Extract text content from the file
    jd_content = _extract_text_from_file(file_bytes, content_type, original_filename)

    # Generate a unique code for the job
    code = f"REQ-{datetime.utcnow().strftime('%Y%m%d')}-{str(ObjectId())[:6].upper()}"

    document: Dict[str, Any] = {
        "title": title,
        "company": company,
        "budget": budget,
        "job_brief": job_brief,
        "jd_content": jd_content,
        "jd_filename": original_filename,
        "additional_details": additional_details or {},
        "uploaded_by": recruiter_id,
        "uploaded_at": datetime.utcnow(),
        "is_curated": True,
        "code": code,
        "status": "active",
        "skills": [],  # Initialize as empty array
        "responsibilities": [],  # Initialize as empty array
        "requirements": [],  # Initialize as empty array
        "skills_required": [],  # Will be extracted by AI later
        "location": "",  # Will be extracted by AI later
    }

    result = await db.jobs.insert_one(document)
    return str(result.inserted_id)


async def get_jobs_by_recruiter(recruiter_id: str, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
    """Get all jobs uploaded by a specific recruiter."""
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    query = {"uploaded_by": recruiter_id}

    total = await db.jobs.count_documents(query)

    cursor = (
        db.jobs.find(query)
        .sort("uploaded_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    raw_jobs = await cursor.to_list(length=page_size)
    serialised = [_serialize_job_document(job) for job in raw_jobs]

    return {
        "items": serialised,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_jobs_by_company(company: str, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
    """Get all jobs for a specific company."""
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    query = {"company": {"$regex": company, "$options": "i"}}

    total = await db.jobs.count_documents(query)

    cursor = (
        db.jobs.find(query)
        .sort("uploaded_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    raw_jobs = await cursor.to_list(length=page_size)
    serialised = [_serialize_job_document(job) for job in raw_jobs]

    return {
        "items": serialised,
        "total": total,
        "page": page,
        "page_size": page_size,
    }