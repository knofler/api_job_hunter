from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.database import db
from app.services.ranking_service import calculate_ranking


def _serialize_job(job: Dict[str, Any]) -> Dict[str, Any]:
    serialised = job.copy()
    serialised["id"] = str(serialised.pop("_id"))
    posted_at = serialised.get("posted_at")
    if isinstance(posted_at, datetime):
        serialised["posted_at"] = posted_at.isoformat()
    return serialised


def _serialize_resume(resume: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if resume is None:
        return None
    data = {
        "id": str(resume.get("_id")),
        "name": resume.get("name"),
        "summary": resume.get("summary", ""),
        "type": resume.get("type"),
    }
    last_updated = resume.get("last_updated")
    if isinstance(last_updated, datetime):
        data["last_updated"] = last_updated.date().isoformat()
    return data


def _serialize_application(document: Dict[str, Any]) -> Dict[str, Any]:
    application = document.copy()
    application["id"] = str(application.pop("_id"))

    applied_at = application.get("applied_at")
    if isinstance(applied_at, datetime):
        application["applied_at"] = applied_at.isoformat()

    updated_at = application.get("updated_at")
    if isinstance(updated_at, datetime):
        application["updated_at"] = updated_at.isoformat()

    job = application.pop("job", None)
    if job:
        application["job"] = _serialize_job(job)

    resume = application.pop("resume", None)
    application["resume"] = _serialize_resume(resume)

    return application


async def get_candidate_applications(candidate_id: str) -> List[Dict[str, Any]]:
    pipeline = [
        {"$match": {"candidate_id": candidate_id}},
        {
            "$lookup": {
                "from": "jobs",
                "localField": "job_id",
                "foreignField": "_id",
                "as": "job",
            }
        },
        {"$unwind": "$job"},
        {
            "$lookup": {
                "from": "resumes",
                "localField": "resume_id",
                "foreignField": "_id",
                "as": "resume",
            }
        },
        {
            "$unwind": {
                "path": "$resume",
                "preserveNullAndEmptyArrays": True,
            }
        },
        {"$sort": {"updated_at": -1}},
    ]

    cursor = db.applications.aggregate(pipeline)
    documents = await cursor.to_list(length=200)
    return [_serialize_application(document) for document in documents]


async def list_candidate_applications(
    candidate_id: str,
    *,
    page: int = 1,
    page_size: int = 25,
) -> Dict[str, Any]:
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    pipeline: List[Dict[str, Any]] = [
        {"$match": {"candidate_id": candidate_id}},
        {"$sort": {"updated_at": -1}},
        {
            "$lookup": {
                "from": "jobs",
                "localField": "job_id",
                "foreignField": "_id",
                "as": "job",
            }
        },
        {"$unwind": "$job"},
        {
            "$project": {
                "job": 1,
                "status": 1,
                "match_score": 1,
                "resume_id": 1,
                "applied_at": 1,
                "updated_at": 1,
            }
        },
        {"$skip": skip},
        {"$limit": page_size},
    ]

    total = await db.applications.count_documents({"candidate_id": candidate_id})
    cursor = db.applications.aggregate(pipeline)
    items: List[Dict[str, Any]] = []

    async for document in cursor:
        job = document.get("job", {})
        items.append(
            {
                "id": str(document.get("_id")),
                "status": document.get("status"),
                "match_score": document.get("match_score"),
                "applied_at": document.get("applied_at"),
                "updated_at": document.get("updated_at"),
                "resume_id": str(document.get("resume_id")) if document.get("resume_id") else None,
                "job": {
                    "id": str(job.get("_id")) if job else None,
                    "title": job.get("title") if job else None,
                    "company": job.get("company") if job else None,
                    "location": job.get("location") if job else None,
                },
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def create_application(
    *,
    candidate_id: str,
    job_id: str,
    resume_id: str,
    note: Optional[str] = None,
) -> str:
    try:
        job_object_id = ObjectId(job_id)
        resume_object_id = ObjectId(resume_id)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Invalid job_id or resume_id") from exc

    job = await db.jobs.find_one({"_id": job_object_id})
    resume = await db.resumes.find_one({"_id": resume_object_id})
    candidate = await db.candidates.find_one({"candidate_id": candidate_id})

    if not job or not resume:
        raise ValueError("Job or resume not found")

    candidate_skills = candidate.get("skills", []) if candidate else []
    resume_skills = resume.get("skills", []) if resume else []
    skillset = list({*candidate_skills, *resume_skills})
    match_score = calculate_ranking(skillset, job.get("skills", []))

    now = datetime.utcnow()
    payload = {
        "candidate_id": candidate_id,
        "job_id": job_object_id,
        "resume_id": resume_object_id,
        "status": "Applied",
        "applied_at": now,
        "updated_at": now,
        "match_score": match_score,
        "note": note,
    }

    result = await db.applications.update_one(
        {"candidate_id": candidate_id, "job_id": job_object_id},
        {"$set": payload, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )

    if result.upserted_id:
        return str(result.upserted_id)

    document = await db.applications.find_one(
        {"candidate_id": candidate_id, "job_id": job_object_id}
    )
    return str(document["_id"]) if document else ""


async def update_application_status(
    *,
    candidate_id: str,
    application_id: str,
    status: str,
) -> bool:
    try:
        object_id = ObjectId(application_id)
    except Exception:
        return False

    result = await db.applications.update_one(
        {"_id": object_id, "candidate_id": candidate_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )
    return result.modified_count > 0


async def get_pipeline_counts(candidate_id: str) -> Dict[str, int]:
    pipeline = [
        {"$match": {"candidate_id": candidate_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]

    cursor = db.applications.aggregate(pipeline)
    raw_counts = await cursor.to_list(length=50)
    counts: Dict[str, int] = {}
    for item in raw_counts:
        status = item.get("_id", "Unknown")
        counts[status] = item.get("count", 0)
    return counts