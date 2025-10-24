import os
from datetime import datetime, timedelta
from typing import Dict, List, Sequence


from bson import ObjectId
from pymongo import MongoClient, ReturnDocument


CANDIDATE_ID = "candidate_1"
TOTAL_CANDIDATES = 100
TOTAL_RESUMES = 100

CANDIDATE_TEMPLATES = [
    {
        "candidate_type": "Full-Stack Engineer",
        "primary_role": "Full-stack Developer",
        "resume_type": "Technical",
        "skills": ["React", "TypeScript", "Node.js", "SQL", "AWS", "GraphQL"],
        "summary": "Full-stack engineer building performant web applications.",
    },
    {
        "candidate_type": "Data Scientist",
        "primary_role": "Data Scientist",
        "resume_type": "Technical",
        "skills": ["Python", "TensorFlow", "Pandas", "SQL", "Airflow", "ML Ops"],
        "summary": "Data scientist delivering end-to-end machine learning solutions.",
    },
    {
        "candidate_type": "Product Manager",
        "primary_role": "Senior Product Manager",
        "resume_type": "Business",
        "skills": ["Product Strategy", "Roadmapping", "Stakeholder Management", "Agile", "OKRs"],
        "summary": "Product leader shipping impactful SaaS experiences.",
    },
    {
        "candidate_type": "UX Designer",
        "primary_role": "Lead UX Designer",
        "resume_type": "Creative",
        "skills": ["UX Research", "UI Design", "Accessibility", "Figma", "Design Systems"],
        "summary": "Experience designer crafting accessible digital products.",
    },
    {
        "candidate_type": "Marketing Strategist",
        "primary_role": "Growth Marketing Manager",
        "resume_type": "Business",
        "skills": ["SEO", "Lifecycle Marketing", "Content", "Analytics", "Paid Media"],
        "summary": "Growth marketer scaling B2B acquisition programs.",
    },
    {
        "candidate_type": "Sales Leader",
        "primary_role": "Enterprise Account Executive",
        "resume_type": "Business",
        "skills": ["Salesforce", "Negotiation", "Account Management", "Pipeline Management", "Forecasting"],
        "summary": "Enterprise seller exceeding ARR targets across SaaS.",
    },
    {
        "candidate_type": "DevOps Engineer",
        "primary_role": "Platform Engineer",
        "resume_type": "Technical",
        "skills": ["AWS", "Kubernetes", "Terraform", "CI/CD", "Observability"],
        "summary": "DevOps engineer automating reliable cloud infrastructure.",
    },
    {
        "candidate_type": "Cybersecurity Analyst",
        "primary_role": "Security Analyst",
        "resume_type": "Technical",
        "skills": ["Penetration Testing", "SIEM", "Incident Response", "Risk Assessment", "Zero Trust"],
        "summary": "Security analyst strengthening cloud and network posture.",
    },
    {
        "candidate_type": "Finance Analyst",
        "primary_role": "Senior Financial Analyst",
        "resume_type": "Business",
        "skills": ["Financial Modeling", "Forecasting", "SQL", "Power BI", "Budgeting"],
        "summary": "Finance partner enabling data-driven executive decisions.",
    },
    {
        "candidate_type": "People Partner",
        "primary_role": "HR Business Partner",
        "resume_type": "Business",
        "skills": ["Employee Relations", "Talent Acquisition", "L&D", "HRIS", "Compensation"],
        "summary": "People partner building high-performing, inclusive teams.",
    },
]

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Morgan",
    "Casey",
    "Riley",
    "Jamie",
    "Cameron",
    "Drew",
    "Avery",
    "Skyler",
    "Hayden",
    "Rowan",
    "Elliot",
    "Quinn",
    "Reese",
]

LAST_NAMES = [
    "Harper",
    "Lane",
    "Sawyer",
    "Ellis",
    "Monroe",
    "Parker",
    "Reid",
    "Spencer",
    "Sutton",
    "Reese",
    "Campbell",
    "Finley",
    "Hudson",
    "Kennedy",
    "Lennon",
    "Presley",
]

LOCATIONS = [
    "Sydney, NSW",
    "Melbourne, VIC",
    "Brisbane, QLD",
    "Perth, WA",
    "Adelaide, SA",
    "Hobart, TAS",
    "Canberra, ACT",
    "Darwin, NT",
    "Gold Coast, QLD",
    "Newcastle, NSW",
    "Wollongong, NSW",
    "Geelong, VIC",
]



def _connect_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
    client = MongoClient(mongo_uri)
    return client.get_database()


def _compute_match_score(candidate_skills: List[str], job_skills: List[str]) -> float:
    if not job_skills:
        return 0.0
    overlap = set(skill.lower() for skill in candidate_skills) & set(
        skill.lower() for skill in job_skills
    )
    return round(len(overlap) / len(job_skills) * 100, 2)


def seed_candidate_profile(db):
    candidate_doc = {
        "candidate_id": CANDIDATE_ID,
        "name": "Jane Candidate",
        "email": "jane.candidate@example.com",
        "experience_years": 6,
        "primary_role": "Full-stack Developer",
        "candidate_type": "Full-Stack Engineer",
        "skills": [
            "React",
            "TypeScript",
            "Node.js",
            "AWS",
            "Agile",
            "Product Strategy",
            "SQL",
            "Machine Learning",
        ],
        "preferred_locations": ["Sydney, NSW", "Remote"],
        "updated_at": datetime.utcnow(),
    }

    db.candidates.update_one(
        {"candidate_id": CANDIDATE_ID},
        {"$set": candidate_doc},
        upsert=True,
    )


def seed_resumes(db) -> Dict[str, ObjectId]:
    resumes = [
        {
            "slug": "software-engineer-resume",
            "name": "Software Engineer Resume",
            "type": "Technical",
            "summary": "5+ years experience in full-stack development, React, Node.js, and cloud platforms.",
            "preview": (
                "Jane Candidate\nSoftware Engineer\n\n"
                "Professional Summary:\nResults-driven software engineer with 5+ years of experience building scalable web applications.\n"
                "Adept at React, Node.js, and AWS. Passionate about clean code and agile teams.\n\n"
                "Skills:\n- React.js\n- Node.js\n- AWS\n- TypeScript\n- REST APIs\n- Agile/Scrum\n\n"
                "Experience:\nAcme Corp (2021-2025): Senior Frontend Engineer\n"
                "Beta Inc (2018-2021): Full Stack Developer\n\n"
                "Education:\nB.Sc. in Computer Science, Tech University\n"
            ),
            "skills": [
                "React",
                "Node.js",
                "AWS",
                "TypeScript",
                "REST APIs",
                "Agile",
            ],
            "last_updated": datetime(2025, 7, 1),
            "health_score": {
                "score": 87,
                "sub_scores": [
                    {"label": "ATS", "value": 90},
                    {"label": "Skills", "value": 85},
                    {"label": "Format", "value": 80},
                ],
            },
        },
        {
            "slug": "product-manager-resume",
            "name": "Product Manager Resume",
            "type": "Business",
            "summary": "Experienced in product lifecycle, agile, and cross-functional teams.",
            "preview": (
                "Jane Candidate\nProduct Manager\n\n"
                "Professional Summary:\nStrategic product manager with a track record of launching successful SaaS products.\n"
                "Skilled in agile methodologies and cross-functional leadership.\n\n"
                "Skills:\n- Product Strategy\n- Agile/Scrum\n- Roadmapping\n- Stakeholder Management\n- User Research\n\n"
                "Experience:\nBeta Inc (2022-2025): Product Manager\n"
                "Acme Corp (2019-2022): Associate PM\n\n"
                "Education:\nMBA, Business School\n"
            ),
            "skills": [
                "Product Strategy",
                "Agile",
                "Roadmapping",
                "Stakeholder Management",
                "User Research",
            ],
            "last_updated": datetime(2025, 6, 28),
            "health_score": {
                "score": 82,
                "sub_scores": [
                    {"label": "ATS", "value": 84},
                    {"label": "Skills", "value": 78},
                    {"label": "Format", "value": 85},
                ],
            },
        },
        {
            "slug": "data-scientist-resume",
            "name": "Data Scientist Resume",
            "type": "Technical",
            "summary": "Expert in Python, machine learning, and data storytelling.",
            "preview": (
                "Jane Candidate\nData Scientist\n\n"
                "Professional Summary:\nData scientist with deep expertise in ML, Python, and analytics.\n"
                "Proven ability to turn data into actionable insights.\n\n"
                "Skills:\n- Python\n- Machine Learning\n- Data Visualization\n- SQL\n- Pandas\n\n"
                "Experience:\nDataWorks (2023-2025): Data Scientist\n"
                "AnalyticsPro (2020-2023): Data Analyst\n\n"
                "Education:\nM.Sc. in Data Science, Analytics University\n"
            ),
            "skills": ["Python", "Machine Learning", "SQL", "Pandas", "Data Visualization"],
            "last_updated": datetime(2025, 7, 5),
            "health_score": {
                "score": 89,
                "sub_scores": [
                    {"label": "ATS", "value": 92},
                    {"label": "Skills", "value": 90},
                    {"label": "Format", "value": 85},
                ],
            },
        },
    ]

    resume_id_map: Dict[str, ObjectId] = {}

    for resume in resumes:
        slug = resume["slug"]
        payload = {k: v for k, v in resume.items() if k != "slug"}
        payload.update(
            {
                "candidate_id": CANDIDATE_ID,
                "updated_at": datetime.utcnow(),
            }
        )

        doc = db.resumes.find_one_and_update(
            {"candidate_id": CANDIDATE_ID, "slug": slug},
            {"$set": payload, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        resume_id_map[slug] = doc["_id"]

    # Ensure only relevant resumes remain for the candidate
    db.resumes.delete_many(
        {
            "candidate_id": CANDIDATE_ID,
            "slug": {"$nin": [resume["slug"] for resume in resumes]},
        }
    )

    return resume_id_map


def _name_for_index(index: int) -> str:
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
    return f"{first} {last}"


def _pick_locations(index: int, pool: Sequence[str]) -> List[str]:
    primary = pool[index % len(pool)]
    secondary = pool[(index + 3) % len(pool)]
    return sorted({primary, secondary})


def seed_additional_candidates(db, target_candidates: int = TOTAL_CANDIDATES, target_resumes: int = TOTAL_RESUMES) -> None:
    """Generate additional candidate profiles and resumes to enrich demos."""

    allowed_candidate_ids = {f"candidate_{idx}" for idx in range(1, target_candidates + 1)}

    for idx in range(2, target_candidates + 1):
        template = CANDIDATE_TEMPLATES[(idx - 1) % len(CANDIDATE_TEMPLATES)]
        candidate_id = f"candidate_{idx}"
        name = _name_for_index(idx)
        email_handle = name.lower().replace(" ", ".")
        experience_years = 3 + (idx % 12)
        preferred_locations = _pick_locations(idx, LOCATIONS)

        candidate_doc = {
            "candidate_id": candidate_id,
            "name": name,
            "email": f"{email_handle}{idx}@example.com",
            "experience_years": experience_years,
            "primary_role": template["primary_role"],
            "candidate_type": template["candidate_type"],
            "skills": template["skills"],
            "preferred_locations": preferred_locations,
            "updated_at": datetime.utcnow() - timedelta(days=idx % 14),
        }

        db.candidates.update_one(
            {"candidate_id": candidate_id},
            {"$set": candidate_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
        )

        slug = f"{candidate_id}-primary"
        summary = template["summary"]
        resume_doc = {
            "candidate_id": candidate_id,
            "slug": slug,
            "name": f"{template['primary_role']} Resume",
            "type": template["resume_type"],
            "summary": summary,
            "skills": template["skills"],
            "preview": (
                f"{name}\n{template['primary_role']}\n\n"
                "Professional Summary:\n"
                f"{summary}\n\n"
                "Skills:\n- " + "\n- ".join(template["skills"]) + "\n"
            ),
            "last_updated": datetime.utcnow() - timedelta(days=idx % 10),
            "health_score": {
                "score": 75 + (idx % 20),
                "sub_scores": [
                    {"label": "ATS", "value": 70 + (idx * 3) % 20},
                    {"label": "Skills", "value": 72 + (idx * 5) % 20},
                    {"label": "Format", "value": 74 + (idx * 7) % 20},
                ],
            },
        }

        db.resumes.find_one_and_update(
            {"candidate_id": candidate_id, "slug": slug},
            {
                "$set": resume_doc,
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    # Trim excess autogenerated candidates and resumes if they exist
    db.candidates.delete_many(
        {
            "$and": [
                {"candidate_id": {"$regex": "^candidate_"}},
                {"candidate_id": {"$nin": list(allowed_candidate_ids)}}
            ]
        }
    )

    allowed_resume_candidates = list(allowed_candidate_ids)
    db.resumes.delete_many(
        {
            "$and": [
                {"candidate_id": {"$regex": "^candidate_"}},
                {"candidate_id": {"$nin": allowed_resume_candidates}}
            ]
        }
    )

    current_resume_count = db.resumes.count_documents({})
    if current_resume_count < target_resumes:
        # Ensure total resume count meets requirement by duplicating summaries for missing entries.
        shortfall = target_resumes - current_resume_count
        for offset in range(shortfall):
            template = CANDIDATE_TEMPLATES[offset % len(CANDIDATE_TEMPLATES)]
            candidate_id = f"candidate_{(offset % (target_candidates - 1)) + 2}"
            slug = f"{candidate_id}-supplement-{offset}"
            name = _name_for_index((offset % (target_candidates - 1)) + 2)
            db.resumes.find_one_and_update(
                {"candidate_id": candidate_id, "slug": slug},
                {
                    "$set": {
                        "candidate_id": candidate_id,
                        "slug": slug,
                        "name": f"{template['primary_role']} Portfolio",
                        "type": template["resume_type"],
                        "summary": template["summary"],
                        "skills": template["skills"],
                        "preview": (
                            f"{name}\n{template['primary_role']}\n\n"
                            "Professional Summary:\n"
                            f"{template['summary']}\n"
                        ),
                        "last_updated": datetime.utcnow() - timedelta(days=offset % 7),
                        "health_score": {
                            "score": 78 + (offset % 15),
                            "sub_scores": [
                                {"label": "ATS", "value": 72 + (offset * 2) % 18},
                                {"label": "Skills", "value": 74 + (offset * 3) % 18},
                                {"label": "Format", "value": 76 + (offset * 4) % 18},
                            ],
                        },
                    },
                    "$setOnInsert": {"created_at": datetime.utcnow()},
                },
                upsert=True,
            )


def seed_suggested_actions(db):
    actions = [
        {
            "slug": "update-portfolio",
            "text": "Add the latest case study from the fintech redesign project.",
            "category": "Brand",
            "priority": "High",
        },
        {
            "slug": "linkedin-refresh",
            "text": "Refresh LinkedIn headline to highlight AI/ML experience.",
            "category": "Profile",
            "priority": "Medium",
        },
        {
            "slug": "skill-assessment",
            "text": "Complete advanced TypeScript assessment to boost skill match.",
            "category": "Skill",
            "priority": "High",
        },
        {
            "slug": "network-outreach",
            "text": "Reach out to 2 alumni currently at DataWorks and Beta Inc.",
            "category": "Networking",
            "priority": "Medium",
        },
        {
            "slug": "resume-tailor",
            "text": "Tailor the Software Engineer resume for the Acme Corp role.",
            "category": "Resume",
            "priority": "High",
        },
    ]

    db.candidate_actions.delete_many({"candidate_id": CANDIDATE_ID})
    for index, action in enumerate(actions, start=1):
        db.candidate_actions.insert_one(
            {
                "candidate_id": CANDIDATE_ID,
                "order": index,
                **action,
            }
        )


def seed_applications(db, resume_ids: Dict[str, ObjectId]):
    today = datetime.utcnow()

    applications = [
        {
            "job_slug": "acme-frontend-engineer",
            "resume_slug": "software-engineer-resume",
            "status": "Applied",
            "applied_days_ago": 14,
            "updated_days_ago": 10,
        },
        {
            "job_slug": "beta-product-manager",
            "resume_slug": "product-manager-resume",
            "status": "Interview Round 1",
            "applied_days_ago": 18,
            "updated_days_ago": 5,
        },
        {
            "job_slug": "dataworks-data-scientist",
            "resume_slug": "data-scientist-resume",
            "status": "Shortlisted",
            "applied_days_ago": 9,
            "updated_days_ago": 3,
        },
        {
            "job_slug": "brandboost-marketing-specialist",
            "resume_slug": "product-manager-resume",
            "status": "Draft",
            "applied_days_ago": 0,
            "updated_days_ago": 0,
        },
        {
            "job_slug": "peoplefirst-hr-manager",
            "resume_slug": "product-manager-resume",
            "status": "Phone Interview",
            "applied_days_ago": 21,
            "updated_days_ago": 7,
        },
    ]

    candidate = db.candidates.find_one({"candidate_id": CANDIDATE_ID})
    candidate_skills = candidate.get("skills", []) if candidate else []

    for entry in applications:
        job = db.jobs.find_one({"slug": entry["job_slug"]})
        resume_id = resume_ids.get(entry["resume_slug"])
        if not job or not resume_id:
            continue

        resume = db.resumes.find_one({"_id": resume_id})
        resume_skills = resume.get("skills", []) if resume else []
        combined_skills = list({*candidate_skills, *resume_skills})
        match_score = _compute_match_score(combined_skills, job.get("skills", []))

        applied_at = today - timedelta(days=entry["applied_days_ago"])
        updated_at = today - timedelta(days=entry["updated_days_ago"])

        payload = {
            "candidate_id": CANDIDATE_ID,
            "job_id": job["_id"],
            "resume_id": resume_id,
            "status": entry["status"],
            "applied_at": applied_at,
            "updated_at": updated_at,
            "match_score": match_score,
        }

        db.applications.update_one(
            {"candidate_id": CANDIDATE_ID, "job_id": job["_id"]},
            {"$set": payload, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
        )

    # Remove stale applications for this candidate
    valid_job_ids = [
        db.jobs.find_one({"slug": app["job_slug"]})["_id"]
        for app in applications
        if db.jobs.find_one({"slug": app["job_slug"]})
    ]
    db.applications.delete_many(
        {
            "candidate_id": CANDIDATE_ID,
            "job_id": {"$nin": valid_job_ids},
        }
    )


def seed_candidate_workflow():
    db = _connect_db()
    seed_candidate_profile(db)
    resume_ids = seed_resumes(db)
    seed_suggested_actions(db)
    seed_applications(db, resume_ids)
    seed_additional_candidates(db)


if __name__ == "__main__":
    seed_candidate_workflow()
