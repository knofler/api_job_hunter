import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from pymongo import MongoClient, ReturnDocument

TARGET_JOB_COUNT = 300


def _build_curated_jobs() -> List[Dict[str, Any]]:
    australia_locations = [
        "Sydney, NSW",
        "Melbourne, VIC",
        "Brisbane, QLD",
        "Perth, WA",
        "Adelaide, SA",
    ]

    today = datetime.utcnow()

    curated_jobs: List[Dict[str, Any]] = [
        {
            "slug": "acme-frontend-engineer",
            "title": "Frontend Engineer",
            "company": "Acme Corp",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$130k - $150k AUD",
            "category": "Frontend Developer",
            "description": "Work on modern React applications and collaborate closely with product and design teams to ship delightful user experiences.",
            "responsibilities": [
                "Implement new UI features using React and TypeScript",
                "Collaborate with designers to translate Figma prototypes",
                "Improve performance and accessibility across the product",
            ],
            "requirements": [
                "3+ years of experience with React",
                "Strong understanding of TypeScript and modern CSS",
                "Experience working with design systems",
            ],
            "skills": ["React", "TypeScript", "Tailwind", "Accessibility"],
            "posted_at": today - timedelta(days=2),
        },
        {
            "slug": "beta-product-manager",
            "title": "Product Manager",
            "company": "Beta Inc",
            "location": "New York, NY",
            "employment_type": "Hybrid",
            "salary_range": "$150k - $170k USD",
            "category": "Product Manager",
            "description": "Lead cross-functional teams to deliver impactful features across our SaaS platform.",
            "responsibilities": [
                "Define product roadmaps in collaboration with leadership",
                "Gather customer insights and translate them into requirements",
                "Drive agile ceremonies and ensure timely delivery",
            ],
            "requirements": [
                "2+ years experience as a product manager",
                "Strong stakeholder management skills",
                "Experience working with SaaS metrics",
            ],
            "skills": ["Agile", "Roadmapping", "Stakeholder Management", "Analytics"],
            "posted_at": today - timedelta(days=5),
        },
        {
            "slug": "dataworks-data-scientist",
            "title": "Data Scientist",
            "company": "DataWorks",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_range": "$140k - $160k USD",
            "category": "Data Scientist",
            "description": "Analyze large datasets and build predictive models that power decision making across the organization.",
            "responsibilities": [
                "Design and deploy machine learning models",
                "Collaborate with product teams to identify opportunities",
                "Communicate insights to stakeholders",
            ],
            "requirements": [
                "Strong Python and SQL fundamentals",
                "Experience with scikit-learn or TensorFlow",
                "Background in statistics or applied mathematics",
            ],
            "skills": ["Python", "Machine Learning", "SQL", "TensorFlow"],
            "posted_at": today - timedelta(days=1),
        },
        {
            "slug": "brandboost-marketing-specialist",
            "title": "Marketing Specialist",
            "company": "BrandBoost",
            "location": random.choice(australia_locations),
            "employment_type": "Contract",
            "salary_range": "$90k - $110k AUD",
            "category": "Marketing Strategist",
            "description": "Drive omni-channel marketing campaigns with a focus on content and SEO.",
            "responsibilities": [
                "Plan and execute integrated marketing campaigns",
                "Report on marketing performance and ROI",
                "Collaborate with product marketing and design",
            ],
            "requirements": [
                "Experience with SEO/SEM",
                "Hands-on with marketing automation tools",
                "Strong copywriting background",
            ],
            "skills": ["SEO", "SEM", "Content Marketing", "Google Analytics"],
            "posted_at": today - timedelta(days=7),
        },
        {
            "slug": "peoplefirst-hr-manager",
            "title": "HR Manager",
            "company": "PeopleFirst",
            "location": random.choice(australia_locations),
            "employment_type": "Full-time",
            "salary_range": "$110k - $130k AUD",
            "category": "People Partner",
            "description": "Manage end-to-end talent lifecycle and drive employee engagement across the APAC region.",
            "responsibilities": [
                "Oversee recruitment and onboarding operations",
                "Develop engagement and retention programs",
                "Ensure compliance with employment regulations",
            ],
            "requirements": [
                "3+ years in HR leadership roles",
                "Experience with HRIS systems",
                "Strong knowledge of local employment law",
            ],
            "skills": ["Talent Acquisition", "HRIS", "Employee Engagement", "Compliance"],
            "posted_at": today - timedelta(days=3),
        },
    ]

    return curated_jobs


def seed_jobs():
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_matching")
    client = MongoClient(MONGO_URI)
    db = client.get_database()

    job_categories = [
        {"category": "Full-Stack Engineer", "skills": ["React", "TypeScript", "Node.js", "GraphQL", "SQL"]},
        {"category": "Backend Developer", "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis"]},
        {"category": "Frontend Developer", "skills": ["JavaScript", "React", "Next.js", "CSS", "Accessibility"]},
        {"category": "Data Scientist", "skills": ["Python", "TensorFlow", "Pandas", "SQL", "ML Ops"]},
        {"category": "Data Engineer", "skills": ["Spark", "Airflow", "Python", "DBT", "Kafka"]},
        {"category": "Machine Learning Engineer", "skills": ["PyTorch", "MLFlow", "Feature Engineering", "Kubernetes"]},
        {"category": "DevOps Engineer", "skills": ["AWS", "Terraform", "Docker", "CI/CD", "Observability"]},
        {"category": "Cloud Architect", "skills": ["Azure", "GCP", "Networking", "Security", "Kubernetes"]},
        {"category": "Cybersecurity Analyst", "skills": ["Penetration Testing", "SIEM", "Incident Response", "Zero Trust"]},
        {"category": "QA Automation Engineer", "skills": ["Selenium", "Playwright", "Python", "CI/CD", "Test Strategy"]},
        {"category": "Mobile Developer", "skills": ["Swift", "Kotlin", "React Native", "Flutter", "CI/CD"]},
        {"category": "Product Manager", "skills": ["Product Strategy", "Roadmapping", "Analytics", "Stakeholder Management"]},
        {"category": "UX Designer", "skills": ["UX Research", "UI Design", "Prototyping", "Design Systems"]},
        {"category": "Marketing Strategist", "skills": ["SEO", "Lifecycle Marketing", "Paid Media", "Analytics"]},
        {"category": "Sales Leader", "skills": ["Salesforce", "Negotiation", "Pipeline Management", "Forecasting"]},
        {"category": "Customer Success Manager", "skills": ["Customer Journey", "CRM", "Renewals", "Upsell"]},
        {"category": "People Partner", "skills": ["Talent Acquisition", "Employee Relations", "Compensation", "HRIS"]},
        {"category": "Finance Analyst", "skills": ["Financial Modeling", "Forecasting", "Power BI", "Excel"]},
        {"category": "Technical Writer", "skills": ["API Documentation", "Information Architecture", "Editing", "Developer Relations"]},
        {"category": "Support Engineer", "skills": ["Troubleshooting", "SQL", "APIs", "Customer Support"]},
    ]

    locations = [
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
        "Sunshine Coast, QLD",
        "Townsville, QLD",
        "Wollongong, NSW",
        "Geelong, VIC",
        "Ballarat, VIC",
    ]

    company_prefixes = [
        "Bright",
        "Lumen",
        "Nimbus",
        "Orbit",
        "Pulse",
        "Quantum",
        "River",
        "Summit",
        "Vertex",
        "Atlas",
        "Cobalt",
        "Aurora",
    ]

    company_suffixes = [
        "Labs",
        "Systems",
        "Works",
        "Dynamics",
        "Analytics",
        "Partners",
        "Solutions",
        "Networks",
        "Technologies",
        "Ventures",
    ]

    employment_types = ["Full-time", "Part-time", "Contract", "Hybrid"]
    salary_bands = [
        "$90k - $110k AUD",
        "$110k - $130k AUD",
        "$130k - $150k AUD",
        "$150k - $180k AUD",
    ]

    curated_jobs = _build_curated_jobs()

    for curated in curated_jobs:
        identifier = {"slug": curated["slug"]}
        doc = {k: v for k, v in curated.items() if k != "slug"}
        db.jobs.find_one_and_update(
            identifier,
            {"$set": doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    rng = random.Random(2025)
    allowed_slugs = {f"auto-job-{index}" for index in range(1, TARGET_JOB_COUNT + 1)}

    for index in range(1, TARGET_JOB_COUNT + 1):
        template = job_categories[(index - 1) % len(job_categories)]
        slug = f"auto-job-{index}"
        company = f"{rng.choice(company_prefixes)} {rng.choice(company_suffixes)} {100 + (index % 200)}"
        skills = template["skills"]
        sampled_skills = rng.sample(skills, k=min(3, len(skills)))

        job_document = {
            "title": template["category"],
            "company": company,
            "location": rng.choice(locations),
            "category": template["category"],
            "skills": sampled_skills,
            "description": f"Join our team as a {template['category']} to build and scale modern solutions.",
            "responsibilities": [
                f"Deliver value as a {template['category']}",
                "Collaborate with cross-functional partners",
                "Measure impact and iterate quickly",
            ],
            "requirements": list(
                dict.fromkeys(
                    [
                        "Relevant professional experience",
                        rng.choice(skills),
                        rng.choice(skills),
                    ]
                )
            ),
            "employment_type": rng.choice(employment_types),
            "salary_range": rng.choice(salary_bands),
            "posted_at": datetime.utcnow() - timedelta(days=rng.randint(0, 45)),
        }

        db.jobs.find_one_and_update(
            {"slug": slug},
            {"$set": job_document, "$setOnInsert": {"created_at": datetime.utcnow(), "slug": slug}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    db.jobs.delete_many(
        {
            "$and": [
                {"slug": {"$regex": "^auto-job-"}},
                {"slug": {"$nin": list(allowed_slugs)}}
            ]
        }
    )