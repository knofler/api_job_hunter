from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from app.core.config import settings
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
    recruiter_workflow,
    admin_llm,
    admin_orgs,
    chat,
    prompts,
)
from scripts.seed_candidate_workflow import seed_candidate_workflow
from scripts.seed_jobs import seed_jobs
from scripts.seed_recruiters import seed_recruiters
from scripts.seed_users import seed_users
from scripts.seed_prompts import seed_prompts

app = FastAPI()

# Add CORS middleware
allow_all_origins = len(settings.cors_origins) == 1 and settings.cors_origins[0] == "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else settings.cors_origins,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS and not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure MongoDB client
client = MongoClient(settings.MONGO_URI)
db = client.get_database(settings.MONGO_DB_NAME)

# Seed data during startup
@app.on_event("startup")
async def startup_event():
    print("Starting application startup...")
    # Always seed prompts as they are critical for application functionality
    print("Seeding prompts...")
    seed_prompts(db)
    print("Prompts seeded successfully")

    if not settings.RUN_STARTUP_SEED:
        print("Skipping other seeding (RUN_STARTUP_SEED=false)")
        return

    print("Seeding other data...")
    seed_users()
    seed_jobs()
    seed_candidate_workflow()
    seed_recruiters()
    print("All seeding completed")

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
app.include_router(recruiter_workflow.router)
app.include_router(admin_llm.router)
app.include_router(admin_orgs.router)
app.include_router(chat.router)
app.include_router(prompts.router, prefix="/prompts")