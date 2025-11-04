from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4

from app.core.database import db
from app.models.chat_model import ChatMessage, ChatRequest, ChatSessionState

_sessions = db.chat_sessions


async def get_or_create_session(session_id: str) -> ChatSessionState:
    doc = await _sessions.find_one({"session_id": session_id})
    if doc:
        return ChatSessionState(**doc)
    
    new_session = ChatSessionState(session_id=session_id)
    await _sessions.insert_one(new_session.dict())
    return new_session


async def update_session(session: ChatSessionState) -> None:
    session.updated_at = datetime.utcnow()
    await _sessions.update_one(
        {"session_id": session.session_id},
        {"$set": session.dict()},
        upsert=True
    )


async def add_message(session_id: str, role: str, content: str) -> ChatMessage:
    msg = ChatMessage(role=role, content=content)
    await _sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": msg.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    return msg


async def update_context(session_id: str, job_id: Optional[str], resume_ids: Optional[list], workflow_context: Optional[Dict]) -> None:
    updates = {"updated_at": datetime.utcnow()}
    if job_id:
        updates["job_id"] = job_id
    if resume_ids:
        updates["resume_ids"] = resume_ids
    if workflow_context:
        updates["workflow_context"] = workflow_context
    
    await _sessions.update_one(
        {"session_id": session_id},
        {"$set": updates}
    )
