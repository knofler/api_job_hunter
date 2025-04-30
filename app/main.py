import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from app.api.routes import health, users  # Import your routes
from scripts.seed_users import seed_users  # Import the seeding function

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
    seed_users()

# Include your routers
app.include_router(health.router, prefix="/health")
app.include_router(users.router, prefix="/users")