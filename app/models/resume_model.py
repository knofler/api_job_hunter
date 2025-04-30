from pydantic import BaseModel, EmailStr
from typing import Optional

class Resume(BaseModel):
    id: Optional[str]
    name: str
    email: EmailStr
    skills: list[str]
    experience: int