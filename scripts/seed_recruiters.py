import os
from datetime import datetime, timedelta
from typing import List

from pymongo import MongoClient, ReturnDocument

RECRUITER_COUNT = 20

SPECIALTIES = [
    "Full-Stack Engineering",
    "Data & AI",
    "Product Management",
    "UX & Research",
    "DevOps & Cloud",
    "Cybersecurity",
    "Sales Leadership",
    "Marketing & Growth",
    "People & Talent",
    "Finance & Operations",
]

REGIONS = [
    "Sydney, NSW",
    "Melbourne, VIC",
    "Brisbane, QLD",
    "Perth, WA",
    "Adelaide, SA",
    "Canberra, ACT",
    "Gold Coast, QLD",
    "Newcastle, NSW",
]

COMPANIES = [
    "TalentBridge",
    "Elevate Partners",
    "Northstar Search",
    "BlueSky Talent",
    "Momentum Recruiting",
    "Harbor & Co.",
    "Crescent Talent",
    "Beacon Search",
    "Lighthouse People",
    "Summit Placements",
]

FIRST_NAMES = [
    "Harper",
    "Elliot",
    "Rowan",
    "Skye",
    "Finley",
    "Avery",
    "Morgan",
    "Dakota",
    "Peyton",
    "Jules",
]

LAST_NAMES = [
    "Brooks",
    "Hayes",
    "Kennedy",
    "Parker",
    "Sawyer",
    "Ellis",
    "Campbell",
    "Reid",
    "Lennox",
    "Monroe",
]


def _name_for_index(index: int) -> str:
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
    return f"{first} {last}"


def seed_recruiters():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
    client = MongoClient(mongo_uri)
    db = client.get_database()

    allowed_ids: List[str] = []

    for idx in range(1, RECRUITER_COUNT + 1):
        recruiter_id = f"recruiter_{idx}"
        allowed_ids.append(recruiter_id)

        name = _name_for_index(idx)
        specialty = SPECIALTIES[(idx - 1) % len(SPECIALTIES)]
        focus_area = SPECIALTIES[(idx + 2) % len(SPECIALTIES)]
        region = REGIONS[idx % len(REGIONS)]
        company = COMPANIES[idx % len(COMPANIES)]
        email_handle = name.lower().replace(" ", ".")

        doc = {
            "recruiter_id": recruiter_id,
            "name": name,
            "email": f"{email_handle}@{company.lower().replace(' ', '')}.com",
            "company": company,
            "specialties": [specialty, focus_area],
            "regions": [region, REGIONS[(idx + 3) % len(REGIONS)]],
            "updated_at": datetime.utcnow() - timedelta(days=idx % 10),
            "bio": (
                f"{name} partners with high-growth teams to place {specialty.lower()} and "
                f"{focus_area.lower()} talent across {region}."
            ),
        }

        db.recruiters.find_one_and_update(
            {"recruiter_id": recruiter_id},
            {
                "$set": doc,
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    db.recruiters.delete_many(
        {
            "$and": [
                {"recruiter_id": {"$regex": "^recruiter_"}},
                {"recruiter_id": {"$nin": allowed_ids}},
            ]
        }
    )


if __name__ == "__main__":
    seed_recruiters()
