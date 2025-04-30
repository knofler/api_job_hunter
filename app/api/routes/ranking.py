from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def calculate_ranking(data: dict):
    return {"message": "Ranking calculated", "data": data}