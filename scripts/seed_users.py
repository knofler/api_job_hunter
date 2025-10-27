import os
import random

from pymongo import MongoClient

def seed_users():
    """Seed the users collection with diverse dummy data if it's empty."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobhunter-app")
    mongo_db = os.getenv("MONGO_DB_NAME", "jobhunter-app")
    client = MongoClient(mongo_uri)
    db = client.get_database(mongo_db)

    # Define possible skills
    skills = [
        "Python", "JavaScript", "React", "Node.js", "Django", "FastAPI", "Machine Learning",
        "Data Analysis", "AWS", "Docker", "Kubernetes", "Figma", "Sketch", "SEO", "Salesforce",
        "Flutter", "Swift", "Agile", "Scrum", "Penetration Testing", "Accounting", "Taxation"
    ]

    # Define possible locations (Australian cities and regions)
    locations = [
        "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", "Adelaide, SA",
        "Hobart, TAS", "Canberra, ACT", "Darwin, NT", "Gold Coast, QLD", "Newcastle, NSW"
    ]

    # Define possible genders
    genders = ["Male", "Female", "Non-binary", "Other"]

    # Generate 300 users
    users = []
    for i in range(300):
        user = {
            "name": f"User_{i+1}",
            "email": f"user_{i+1}@example.com",
            "age": random.randint(18, 60),  # Random age between 18 and 60
            "location": random.choice(locations),
            "gender": random.choice(genders),
            "skills": random.sample(skills, k=random.randint(2, 5))  # Random 2-5 skills
        }
        users.append(user)

    # Insert users into the database if the collection is empty
    if db.users.count_documents({}) == 0:  # Only seed if the collection is empty
        db.users.insert_many(users)
        print(f"Inserted {len(users)} users into the 'users' collection.")
    else:
        print("Users collection already seeded.")