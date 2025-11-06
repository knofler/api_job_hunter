import os
from datetime import datetime
from pymongo import MongoClient

def seed_prompts():
    """Seed the prompts collection with initial AI prompts for the application."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobhunter-app")
    mongo_db = os.getenv("MONGO_DB_NAME", "jobhunter-app")
    client = MongoClient(mongo_uri)
    db = client.get_database(mongo_db)

    # Initial prompts for different AI functionalities
    prompts = [
        {
            "name": "core_skills_analysis",
            "category": "candidate_analysis",
            "content": """# Core Skills Analysis Prompt

## Task
Analyze a job description and candidate resumes to identify the most critical skills and competencies required for the role. Focus on the essential "must-have" skills that candidates need to possess to be successful.

## Analysis Framework

### 1. Job Requirements Analysis
- Extract explicit skill requirements from job description
- Identify implicit skills needed for role success
- Categorize skills by importance (critical, important, nice-to-have)
- Consider technical, soft, and domain-specific skills

### 2. Candidate Evaluation
- Assess each candidate's skill alignment with job requirements
- Rate skill proficiency levels (Yes, Partial, No)
- Identify skill gaps and development opportunities
- Consider transferable skills and potential

### 3. Core Skills Identification
- Determine 5-8 most critical skills for role success
- Provide clear rationale for each core skill selection
- Explain business impact of each skill
- Suggest evaluation methods for each skill

## Output Structure
For each core skill, provide:
- **Skill Name**: Clear, specific skill identifier
- **Reason**: Why this skill is critical for the role
- **Evaluation Criteria**: How to assess this skill in candidates

## Guidelines
- Focus on skills that directly impact job performance
- Balance technical and behavioral competencies
- Consider both current and future role requirements
- Ensure skills are measurable and observable
- Avoid overemphasis on "nice-to-have" skills

Return JSON with key 'core_skills' containing objects with fields 'name' and 'reason'.""",
            "variables": {
                "job_description": "Full job description text",
                "candidate_resumes": "Array of candidate resume texts"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Identifies critical skills required for job success",
                "output_format": "JSON",
                "estimated_tokens": 1500
            }
        },
        {
            "name": "candidate_analysis",
            "category": "candidate_analysis",
            "content": """For each candidate, score the fit versus the job. Provide match_score (0-100), bias_free_score (0-100), a recruiter summary (<= 400 characters), up to three highlights, and a skill_alignment array with fields 'skill', 'status' (Yes/Partial/No), and 'evidence'. Also craft a recruiter-facing markdown summary and return it as 'ai_analysis_markdown'. Respond with JSON containing keys 'ai_analysis_markdown' and 'candidate_analysis'.""",
            "variables": {
                "job_description": "Job requirements and description",
                "candidates": "Array of candidate information"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Analyzes candidate fit against job requirements",
                "output_format": "JSON",
                "estimated_tokens": 2000
            }
        },
        {
            "name": "ranked_shortlist",
            "category": "candidate_ranking",
            "content": """Rank candidates based on job fit and provide a prioritized shortlist. Consider technical skills, experience level, cultural fit, and growth potential. Return JSON with 'ranked_candidates' array containing objects with 'candidate_id', 'rank', 'score', and 'justification'.""",
            "variables": {
                "job_requirements": "Job requirements and criteria",
                "candidates": "Array of candidate profiles"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Ranks candidates for shortlisting",
                "output_format": "JSON",
                "estimated_tokens": 1500
            }
        },
        {
            "name": "detailed_readout",
            "category": "candidate_analysis",
            "content": """Provide detailed analysis of top candidates including strengths, weaknesses, interview questions, and hiring recommendations. Return comprehensive markdown report.""",
            "variables": {
                "top_candidates": "Top ranked candidates",
                "job_details": "Job requirements and context"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Detailed candidate analysis report",
                "output_format": "Markdown",
                "estimated_tokens": 2000
            }
        },
        {
            "name": "engagement_plan",
            "category": "recruitment_strategy",
            "content": """Create a comprehensive engagement plan for top candidates including communication strategy, timeline, and follow-up actions. Return JSON with engagement steps and timeline.""",
            "variables": {
                "candidates": "Selected candidates for engagement",
                "job_details": "Job information and requirements"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Creates candidate engagement strategy",
                "output_format": "JSON",
                "estimated_tokens": 1200
            }
        },
        {
            "name": "fairness_guidance",
            "category": "compliance",
            "content": """Review candidate selection process for bias and fairness. Ensure diverse representation and equitable evaluation. Provide guidance on reducing unconscious bias.""",
            "variables": {
                "candidate_pool": "All candidates under consideration",
                "selection_criteria": "Evaluation criteria used"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Ensures fair and unbiased candidate evaluation",
                "output_format": "Text",
                "estimated_tokens": 1000
            }
        },
        {
            "name": "interview_preparation",
            "category": "interview_planning",
            "content": """Prepare comprehensive interview plan including questions, evaluation criteria, and assessment framework for top candidates.""",
            "variables": {
                "candidates": "Final candidates for interview",
                "job_requirements": "Key job competencies"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Creates interview preparation plan",
                "output_format": "JSON",
                "estimated_tokens": 1500
            }
        }
    ]

    # Insert prompts into database
    for prompt in prompts:
        existing = db.prompts.find_one({"name": prompt["name"]})
        if existing and existing.get("version", 1) < prompt.get("version", 1):
            db.prompts.update_one(
                {"name": prompt["name"]},
                {
                    "$set": {
                        **prompt,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "system"
                    }
                }
            )
            print(f"Updated prompt: {prompt['name']}")
        elif not existing:
            db.prompts.insert_one(prompt)
            print(f"Inserted prompt: {prompt['name']}")
        else:
            print(f"Prompt {prompt['name']} already up to date")

    print("Prompts seeding completed successfully!")


if __name__ == "__main__":
    seed_prompts()

    # Insert prompts into the database if the collection is empty
    if db.prompts.count_documents({}) == 0:
        for prompt in prompts:
            prompt.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": "system",
                "updated_by": "system"
            })
        db.prompts.insert_many(prompts)
        print(f"Inserted {len(prompts)} prompts into the 'prompts' collection.")
    else:
        print("Prompts collection already seeded.")

    # Update existing prompts if needed (for migrations)
    for prompt in prompts:
        existing = db.prompts.find_one({"name": prompt["name"]})
        if existing and existing.get("version", 1) < prompt.get("version", 1):
            db.prompts.update_one(
                {"name": prompt["name"]},
                {
                    "$set": {
                        **prompt,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "system"
                    }
                }
            )
            print(f"Updated prompt: {prompt['name']}")

if __name__ == "__main__":
    seed_prompts()