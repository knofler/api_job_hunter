from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ranking_service import calculate_ranking as calculate_match


class RankingPayload(BaseModel):
    user_skills: List[str]
    job_skills: List[str]


router = APIRouter()


@router.post("/")
async def calculate_ranking(payload: RankingPayload):
    score = calculate_match(payload.user_skills, payload.job_skills)
    return {"match_score": score, "matching_skills": list({skill.lower() for skill in payload.user_skills} & {skill.lower() for skill in payload.job_skills})}