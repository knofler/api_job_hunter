from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from bson import ObjectId

from app.core.database import db
from app.services.ranking_service import calculate_ranking


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
        .sort("posted_at", -1)
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