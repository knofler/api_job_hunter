from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Prompt(BaseModel):
    id: Optional[str]
    name: str  # e.g., "core_skill_analysis", "job_matching", "resume_health"
    category: str  # e.g., "candidate_analysis", "job_matching", "recruiter_assistance"
    content: str  # The actual prompt text
    variables: Optional[Dict[str, str]] = {}  # Template variables that can be substituted
    version: int = 1
    is_active: bool = True
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]  # User ID who created it
    updated_by: Optional[str]  # User ID who last updated it
    metadata: Optional[Dict[str, Any]] = {}  # Additional metadata

class PromptUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    content: Optional[str]
    variables: Optional[Dict[str, str]]
    is_active: Optional[bool]
    metadata: Optional[Dict[str, Any]]

class PromptCreate(BaseModel):
    name: str
    category: str
    content: str
    variables: Optional[Dict[str, str]] = {}
    metadata: Optional[Dict[str, Any]] = {}