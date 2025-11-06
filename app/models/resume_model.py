from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

class Resume(BaseModel):
    id: Optional[str]
    user_id: str  # Link to user
    name: str
    email: EmailStr
    skills: list[str]
    experience: int
    content: str  # Full resume content as text
    version: int = 1  # Version number for multiple resumes
    resume_type: str = "general"  # e.g., "general", "technical", "executive"
    filename: Optional[str]  # Original filename if uploaded
    uploaded_at: datetime = datetime.utcnow()
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = {}  # Additional extracted data
    improvement_journey: Optional[List[Dict[str, Any]]] = []  # Resume improvement tracking