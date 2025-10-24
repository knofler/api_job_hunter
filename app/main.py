import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from app.api.routes import (
    applications,
    candidates,
    health,
    jobs,
    ranking,
    recruiters,
    resumes,
    scrape_jobs_api,
    users,
)
from scripts.seed_candidate_workflow import seed_candidate_workflow
from scripts.seed_jobs import seed_jobs
from scripts.seed_recruiters import seed_recruiters
from scripts.seed_users import seed_users

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get MongoDB URI from environment variable
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Seed data during startup
@app.on_event("startup")
async def startup_event():
    # Seed users and jobs
    seed_users()
    seed_jobs()
    seed_candidate_workflow()
    seed_recruiters()

# Include your routers
app.include_router(health.router, prefix="/health")
app.include_router(users.router, prefix="/users")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(resumes.router, prefix="/resumes")
app.include_router(candidates.router)
app.include_router(applications.router)
app.include_router(ranking.router, prefix="/ranking")
app.include_router(recruiters.router)
app.include_router(scrape_jobs_api.router, prefix="/api")  # Register the scrape_jobs_api router