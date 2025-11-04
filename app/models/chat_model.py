from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(description="user or assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSessionState(BaseModel):
    session_id: str
    job_id: Optional[str] = None
    resume_ids: List[str] = Field(default_factory=list)
    workflow_context: Dict = Field(default_factory=dict, description="Last generated workflow results")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    job_id: Optional[str] = None
    resume_ids: Optional[List[str]] = None
    workflow_context: Optional[Dict] = None
