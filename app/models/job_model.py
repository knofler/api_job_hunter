from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    id: Optional[str]
    title: str
    description: str
    skills_required: list[str]
    location: str