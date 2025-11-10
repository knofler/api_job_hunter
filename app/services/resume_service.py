from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from PyPDF2 import PdfReader
import docx

from app.core.database import db


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


def _serialise_resume(document: Dict[str, Any]) -> Dict[str, Any]:
    resume = document.copy()
    resume["id"] = str(resume.pop("_id"))

    last_updated = resume.get("last_updated")
    if isinstance(last_updated, datetime):
        resume["last_updated"] = last_updated.date().isoformat()

    created_at = resume.get("created_at")
    if isinstance(created_at, datetime):
        resume["created_at"] = created_at.isoformat()

    uploaded_at = resume.get("uploaded_at")
    if isinstance(uploaded_at, datetime):
        resume["uploaded_at"] = uploaded_at.isoformat()

    health = resume.get("health_score")
    if health and isinstance(health, dict):
        resume["health_score"] = {
            "score": health.get("score", 0),
            "sub_scores": health.get("sub_scores", []),
        }

    # For seeded resumes, summary and skills are direct fields
    # For uploaded resumes, they come from metadata
    if "summary" not in resume:
        metadata = resume.get("metadata", {})
        resume["summary"] = metadata.get("summary", "")
    if "skills" not in resume:
        metadata = resume.get("metadata", {})
        resume["skills"] = metadata.get("skills", [])

    # Remove sensitive fields
    resume.pop("file_blob", None)
    return resume


async def get_resumes(user_id: str) -> List[Dict[str, Any]]:
    """Get all resumes for a user."""
    cursor = db.resumes.find({
        "candidate_id": user_id,
        "$or": [
            {"is_active": True},
            {"is_active": {"$exists": False}}
        ]
    }).sort("last_updated", -1)
    documents = await cursor.to_list(length=100)
    return [_serialise_resume(document) for document in documents]


async def get_resume(resume_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific resume by ID."""
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return None

    document = await db.resumes.find_one({"_id": object_id})
    if not document:
        return None

    # For uploaded resumes, check is_active; for seeded resumes (no is_active field), consider them active
    is_active = document.get("is_active", True)
    if not is_active:
        return None

    return _serialise_resume(document)


async def upload_resume(
    *,
    user_id: str,
    name: str,
    file_bytes: bytes,
    content_type: str,
    original_filename: str,
    resume_type: str = "general",
    version: Optional[int] = None,
    summary: Optional[str] = None,
    skills: Optional[List[str]] = None,
) -> str:
    """Upload a resume and extract its text content."""

    # Extract text content from the file
    content = _extract_text_from_file(file_bytes, content_type, original_filename)

    # Determine version number
    if version is None:
        # Get the latest version for this user and resume type
        latest_resume = await db.resumes.find_one(
            {"user_id": user_id, "resume_type": resume_type, "is_active": True},
            sort=[("version", -1)]
        )
        version = (latest_resume.get("version", 0) if latest_resume else 0) + 1

    document: Dict[str, Any] = {
        "user_id": user_id,
        "name": name,
        "content": content,
        "version": version,
        "resume_type": resume_type,
        "filename": original_filename,
        "content_type": content_type,
        "uploaded_at": datetime.utcnow(),
        "is_active": True,
        "metadata": {
            "summary": summary,
            "skills": skills or [],
        },
    }

    result = await db.resumes.insert_one(document)
    return str(result.inserted_id)


async def update_resume(resume_id: str, updates: Dict[str, Any]) -> bool:
    """Update resume metadata."""
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return False

    payload = updates.copy()
    payload["uploaded_at"] = datetime.utcnow()
    result = await db.resumes.update_one({"_id": object_id}, {"$set": payload})
    return result.modified_count > 0


async def delete_resume(resume_id: str) -> bool:
    """Soft delete a resume."""
    try:
        object_id = ObjectId(resume_id)
    except Exception:
        return False

    result = await db.resumes.update_one(
        {"_id": object_id},
        {"$set": {"is_active": False, "uploaded_at": datetime.utcnow()}}
    )
    return result.modified_count > 0


async def get_resume_versions(user_id: str, resume_type: str = "general") -> List[Dict[str, Any]]:
    """Get all versions of a specific resume type for a user."""
    # For uploaded resumes, check is_active; for seeded resumes, include them
    cursor = db.resumes.find({
        "user_id": user_id,
        "resume_type": resume_type,
        "$or": [
            {"is_active": True},
            {"is_active": {"$exists": False}}
        ]
    }).sort("version", -1)
    documents = await cursor.to_list(length=50)
    return [_serialise_resume(document) for document in documents]