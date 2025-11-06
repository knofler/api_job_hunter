from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Job(BaseModel):
    id: Optional[str]
    title: str
    description: str
    skills_required: list[str]
    location: str
    company: Optional[str]
    budget: Optional[str]  # e.g., "$100k-$120k", "Competitive"
    job_brief: Optional[str]  # Initial job brief from employer
    additional_details: Optional[Dict[str, Any]] = {}  # Other recruiter details
    jd_content: Optional[str]  # Full job description content
    jd_filename: Optional[str]  # Original filename if uploaded
    uploaded_by: Optional[str]  # Recruiter user ID
    uploaded_at: Optional[datetime]
    is_curated: bool = False
    code: Optional[str]  # e.g., "REQ-001"
    posted_at: Optional[datetime]
    status: str = "active"  # active, filled, cancelled