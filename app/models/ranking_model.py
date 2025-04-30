from pydantic import BaseModel
from typing import List

class RankingRequest(BaseModel):
    user_id: str
    job_id: str
    skills: List[str]
    experience: int

class RankingResponse(BaseModel):
    job_id: str
    match_score: float