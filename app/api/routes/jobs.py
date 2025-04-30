from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_jobs():
    return {"message": "List of jobs"}

@router.post("/")
async def create_job(job: dict):
    return {"message": "Job created", "job": job}