from fastapi import APIRouter
from pymongo import MongoClient

router = APIRouter()

# MongoDB connection
MONGO_URI = "mongodb://mongo:27010"  # Use "mongo" as the hostname in Docker Compose
DATABASE_NAME = "ai_matching"
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

@router.get("/")
async def get_users():
    users = list(db.users.find({}, {"_id": 0}))  # Exclude the MongoDB `_id` field
    return {"users": users}