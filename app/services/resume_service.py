from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.binary import Binary

from app.core.database import db


def _serialise_resume(document: Dict[str, Any]) -> Dict[str, Any]:
    resume = document.copy()
    resume["id"] = str(resume.pop("_id"))

    last_updated = resume.get("last_updated")
    if isinstance(last_updated, datetime):
        resume["last_updated"] = last_updated.date().isoformat()

    created_at = resume.get("created_at")
    if isinstance(created_at, datetime):
        resume["created_at"] = created_at.isoformat()

    health = resume.get("health_score")
    if health and isinstance(health, dict):
        resume["health_score"] = {
            "score": health.get("score", 0),
            "sub_scores": health.get("sub_scores", []),
        }

    resume.pop("file_blob", None)
    return resume


async def get_resumes(candidate_id: str) -> List[Dict[str, Any]]:
    cursor = db.resumes.find({"candidate_id": candidate_id}).sort("last_updated", -1)
    documents = await cursor.to_list(length=100)
    return [_serialise_resume(document) for document in documents]


async def get_resume(resume_id: str) -> Optional[Dict[str, Any]]:
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return None

    document = await db.resumes.find_one({"_id": object_id})
    return _serialise_resume(document) if document else None


async def upload_resume(
    *,
    candidate_id: str,
    name: str,
    file_bytes: bytes,
    content_type: str,
    original_filename: str,
    summary: Optional[str] = None,
    skills: Optional[List[str]] = None,
    preview: Optional[str] = None,
    resume_type: Optional[str] = None,
) -> str:
    document: Dict[str, Any] = {
        "candidate_id": candidate_id,
        "name": name,
        "summary": summary or "",
        "skills": skills or [],
        "preview": preview or "",
        "content_type": content_type,
        "original_filename": original_filename,
        "file_blob": Binary(file_bytes),
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
    }

    if resume_type:
        document["type"] = resume_type

    result = await db.resumes.insert_one(document)
    return str(result.inserted_id)


async def update_resume(resume_id: str, updates: Dict[str, Any]) -> bool:
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return False

    payload = updates.copy()
    payload["last_updated"] = datetime.utcnow()
    result = await db.resumes.update_one({"_id": object_id}, {"$set": payload})
    return result.modified_count > 0


async def delete_resume(resume_id: str) -> bool:
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return False

    result = await db.resumes.delete_one({"_id": object_id})
    return result.deleted_count > 0