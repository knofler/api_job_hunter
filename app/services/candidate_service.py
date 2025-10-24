from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.database import db
from app.services import job_service, resume_service
from app.services.application_service import get_pipeline_counts


def _serialise_candidate(document: Dict[str, Any]) -> Dict[str, Any]:
    candidate = document.copy()
    candidate.pop("_id", None)
    updated_at = candidate.get("updated_at")
    if isinstance(updated_at, datetime):
        candidate["updated_at"] = updated_at.isoformat()
    return candidate


async def list_candidates(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    total = await db.candidates.count_documents({})
    cursor = (
        db.candidates.find()
        .sort("updated_at", -1)
        .skip(skip)
        .limit(page_size)
    )
    documents = await cursor.to_list(length=page_size)

    return {
        "items": [_serialise_candidate(document) for document in documents],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_candidate_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
    document = await db.candidates.find_one({"candidate_id": candidate_id})
    if not document:
        return None
    return _serialise_candidate(document)


async def get_candidate_resumes(candidate_id: str) -> List[Dict[str, Any]]:
    return await resume_service.get_resumes(candidate_id)


async def get_resume_health(candidate_id: str) -> Optional[Dict[str, Any]]:
    resume = await db.resumes.find_one(
        {"candidate_id": candidate_id},
        sort=[("last_updated", -1)],
    )
    if not resume:
        return None
    health_score = resume.get("health_score") or {}
    return {
        "score": health_score.get("score", 0),
        "sub_scores": health_score.get("sub_scores", []),
        "resume": {
            "id": str(resume.get("_id")),
            "name": resume.get("name"),
        },
    }


async def get_suggested_actions(candidate_id: str) -> List[Dict[str, Any]]:
    cursor = (
        db.candidate_actions.find({"candidate_id": candidate_id})
        .sort("order", 1)
        .limit(20)
    )
    actions = await cursor.to_list(length=20)
    serialised: List[Dict[str, Any]] = []
    for action in actions:
        serialised.append(
            {
                "id": str(action.get("_id")),
                "text": action.get("text"),
                "priority": action.get("priority"),
                "category": action.get("category"),
            }
        )
    return serialised


async def get_pipeline(candidate_id: str) -> Dict[str, int]:
    return await get_pipeline_counts(candidate_id)


async def get_top_matches(candidate_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    return await job_service.get_top_matches(
        candidate_id,
        limit=limit,
        exclude_applied=True,
    )


async def get_dashboard_snapshot(candidate_id: str) -> Dict[str, Any]:
    profile = await get_candidate_profile(candidate_id)
    resumes = await get_candidate_resumes(candidate_id)
    resume_health = await get_resume_health(candidate_id)
    actions = await get_suggested_actions(candidate_id)
    pipeline = await get_pipeline(candidate_id)
    top_matches = await get_top_matches(candidate_id)

    return {
        "profile": profile,
        "resumes": resumes,
        "resume_health": resume_health,
        "actions": actions,
        "pipeline": pipeline,
        "top_matches": top_matches,
    }
