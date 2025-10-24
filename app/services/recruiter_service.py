from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from app.core.database import db


def _serialise_recruiter(document: Dict[str, Any]) -> Dict[str, Any]:
    recruiter = document.copy()
    recruiter["id"] = str(recruiter.pop("_id", ""))

    updated_at = recruiter.get("updated_at")
    if isinstance(updated_at, datetime):
        recruiter["updated_at"] = updated_at.isoformat()

    created_at = recruiter.get("created_at")
    if isinstance(created_at, datetime):
        recruiter["created_at"] = created_at.isoformat()

    return recruiter


async def list_recruiters(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    skip = (page - 1) * page_size

    total = await db.recruiters.count_documents({})
    cursor = (
        db.recruiters.find()
        .sort("updated_at", -1)
        .skip(skip)
        .limit(page_size)
    )
    documents = await cursor.to_list(length=page_size)

    return {
        "items": [_serialise_recruiter(document) for document in documents],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
