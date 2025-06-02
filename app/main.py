import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from app.api.routes import health, users, scrape_jobs_api  # Import the scrape_jobs_api router
from scripts.seed_users import seed_users  # Import the user seeding function
from scripts.seed_jobs import seed_jobs  # Import the job seeding function

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

# Include your routers
app.include_router(health.router, prefix="/health")
app.include_router(users.router, prefix="/users")
app.include_router(scrape_jobs_api.router, prefix="/api")  # Register the scrape_jobs_api router