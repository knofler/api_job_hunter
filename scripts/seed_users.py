import os
from pymongo import MongoClient

def seed_users():
    """Seed the users collection with dummy data if it's empty."""
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
    client = MongoClient(MONGO_URI)
    db = client.get_database()

    # Dummy users data
    users = [
        {"name": "Alice", "email": "alice@example.com", "age": 25},
        {"name": "Bob", "email": "bob@example.com", "age": 30},
        {"name": "Charlie", "email": "charlie@example.com", "age": 35},
        {"name": "Diana", "email": "diana@example.com", "age": 28},
        {"name": "Eve", "email": "eve@example.com", "age": 22},
        {"name": "Frank", "email": "frank@example.com", "age": 40},
        {"name": "Grace", "email": "grace@example.com", "age": 27},
        {"name": "Hank", "email": "hank@example.com", "age": 33},
        {"name": "Ivy", "email": "ivy@example.com", "age": 29},
        {"name": "Jack", "email": "jack@example.com", "age": 31},
    ]

    if db.users.count_documents({}) == 0:  # Only seed if the collection is empty
        db.users.insert_many(users)
        print(f"Inserted {len(users)} users into the 'users' collection.")
    else:
        print("Users collection already seeded.")