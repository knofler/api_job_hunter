import os
from pymongo import MongoClient
import random

def seed_jobs():
    # Connect to MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
    client = MongoClient(MONGO_URI)
    db = client.get_database()

    # Define job categories and skills
    job_categories = [
        {"category": "Software Engineer", "skills": ["Python", "FastAPI", "Django"]},
        {"category": "Data Scientist", "skills": ["Python", "Machine Learning", "TensorFlow"]},
        {"category": "Frontend Developer", "skills": ["JavaScript", "React", "CSS"]},
        {"category": "Backend Developer", "skills": ["Node.js", "Express", "MongoDB"]},
        {"category": "DevOps Engineer", "skills": ["AWS", "Docker", "Kubernetes"]},
        {"category": "Mobile Developer", "skills": ["Flutter", "React Native", "Swift"]},
        {"category": "UI/UX Designer", "skills": ["Figma", "Sketch", "Adobe XD"]},
        {"category": "Project Manager", "skills": ["Agile", "Scrum", "JIRA"]},
        {"category": "Business Analyst", "skills": ["SQL", "Data Analysis", "Power BI"]},
        {"category": "Cybersecurity Specialist", "skills": ["Penetration Testing", "Network Security", "SIEM"]},
        {"category": "Cloud Engineer", "skills": ["Azure", "AWS", "Google Cloud"]},
        {"category": "Marketing Specialist", "skills": ["SEO", "Google Ads", "Content Marketing"]},
        {"category": "Sales Manager", "skills": ["CRM", "Salesforce", "Negotiation"]},
        {"category": "HR Specialist", "skills": ["Recruitment", "Employee Relations", "HRIS"]},
        {"category": "Accountant", "skills": ["Accounting", "Taxation", "Xero"]},
    ]

    # Define Australian states
    locations = [
        "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD", "Perth, WA", "Adelaide, SA",
        "Hobart, TAS", "Canberra, ACT", "Darwin, NT", "Gold Coast, QLD", "Newcastle, NSW"
    ]

    # Generate 100 job entries
    jobs = []
    for _ in range(100):
        category = random.choice(job_categories)
        job = {
            "title": category["category"],
            "company": f"Company_{random.randint(1, 50)}",
            "location": random.choice(locations),
            "skills": random.sample(category["skills"], k=random.randint(2, len(category["skills"])))
        }
        jobs.append(job)

    # Insert jobs into the database if they don't already exist
    for job in jobs:
        if not db.jobs.find_one({"title": job["title"], "company": job["company"], "location": job["location"]}):
            db.jobs.insert_one(job)
            print(f"Seeded job: {job['title']} at {job['company']} in {job['location']}")