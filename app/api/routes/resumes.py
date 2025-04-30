from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_resumes():
    return {"message": "List of resumes"}

@router.post("/")
async def upload_resume(resume: dict):
    return {"message": "Resume uploaded", "resume": resume}