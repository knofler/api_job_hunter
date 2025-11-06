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
            "name": "core_skill_analysis",
            "category": "candidate_analysis",
            "content": """Analyze the candidate's resume and provide a comprehensive skill assessment.

Context:
- Resume Content: {resume_content}
- Job Requirements: {job_requirements}
- Candidate Experience: {candidate_experience} years

Please provide:
1. Core technical skills identified
2. Skill proficiency levels (Beginner/Intermediate/Advanced/Expert)
3. Gaps between candidate skills and job requirements
4. Recommendations for skill development
5. Overall match score (0-100) with detailed reasoning

Format your response as valid JSON with the following structure:
{
  "technical_skills": [{"skill": "Python", "level": "Advanced", "evidence": "..."}],
  "skill_gaps": ["Cloud Architecture", "DevOps"],
  "recommendations": ["Complete AWS certification", "Learn Kubernetes"],
  "match_score": 85,
  "reasoning": "Strong Python skills but lacks cloud experience"
}""",
            "variables": {
                "resume_content": "Full resume text content",
                "job_requirements": "Job description and required skills",
                "candidate_experience": "Years of experience"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Analyzes candidate skills against job requirements",
                "output_format": "JSON",
                "estimated_tokens": 1500
            }
        },
        {
            "name": "job_matching",
            "category": "job_matching",
            "content": """Match candidates to jobs based on skills, experience, and requirements.

Candidate Profile:
- Skills: {candidate_skills}
- Experience: {candidate_experience} years
- Location: {candidate_location}

Job Details:
- Title: {job_title}
- Required Skills: {job_skills}
- Location: {job_location}
- Description: {job_description}

Calculate a match score (0-100) considering:
1. Skill overlap and proficiency
2. Experience level compatibility
3. Location match
4. Overall cultural fit indicators

Provide detailed reasoning for the match score.

Response format:
{
  "match_score": 78,
  "skill_match": 85,
  "experience_match": 70,
  "location_match": 100,
  "reasoning": "Excellent skill match with Python and React, but limited senior experience",
  "recommendations": ["Consider for junior role", "Strong candidate for mid-level position"]
}""",
            "variables": {
                "candidate_skills": "List of candidate skills",
                "candidate_experience": "Years of experience",
                "candidate_location": "Candidate location",
                "job_title": "Job title",
                "job_skills": "Required job skills",
                "job_location": "Job location",
                "job_description": "Full job description"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Matches candidates to jobs with detailed scoring",
                "output_format": "JSON",
                "estimated_tokens": 1200
            }
        },
        {
            "name": "resume_health_analysis",
            "category": "candidate_analysis",
            "content": """Analyze resume health and provide improvement suggestions.

Resume Content: {resume_content}

Evaluate the resume on:
1. Structure and formatting
2. Content completeness
3. Keyword optimization for ATS
4. Impact statement quality
5. Contact information and personal branding
6. Length and conciseness
7. Industry-specific best practices

Provide specific, actionable recommendations for improvement.

Response format:
{
  "overall_score": 75,
  "categories": {
    "structure": {"score": 80, "feedback": "Good structure with clear sections"},
    "content": {"score": 70, "feedback": "Missing quantifiable achievements"},
    "ats_optimization": {"score": 85, "feedback": "Good keyword usage"},
    "impact": {"score": 65, "feedback": "Needs more specific accomplishments"}
  },
  "priority_improvements": [
    "Add metrics to work experience achievements",
    "Include industry-specific keywords",
    "Strengthen professional summary"
  ],
  "improvement_journey": [
    {"step": 1, "action": "Quantify achievements", "estimated_time": "2 hours"},
    {"step": 2, "action": "Optimize keywords", "estimated_time": "1 hour"}
  ]
}""",
            "variables": {
                "resume_content": "Full resume text content"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Analyzes resume quality and provides improvement suggestions",
                "output_format": "JSON",
                "estimated_tokens": 1000
            }
        },
        {
            "name": "recruiter_assistance",
            "category": "recruiter_assistance",
            "content": """Assist recruiters with candidate evaluation and hiring decisions.

Context:
- Job Requirements: {job_requirements}
- Candidate Profile: {candidate_profile}
- Interview Notes: {interview_notes}
- Current Stage: {recruitment_stage}

Provide insights on:
1. Candidate fit for the role
2. Potential concerns or red flags
3. Interview questions to ask next
4. Comparison with other candidates
5. Hiring recommendations

Response format:
{
  "candidate_fit": {
    "overall_rating": "Strong Match",
    "score": 88,
    "reasoning": "Excellent technical skills and cultural fit"
  },
  "concerns": ["Limited experience with specific technology X"],
  "next_questions": [
    "Can you describe your experience with technology X?",
    "How do you handle tight deadlines?"
  ],
  "comparison_notes": "Stronger technically than candidate A, better communication than candidate B",
  "recommendations": {
    "next_action": "Schedule technical interview",
    "priority": "High",
    "timeline": "Within 1 week"
  }
}""",
            "variables": {
                "job_requirements": "Job description and requirements",
                "candidate_profile": "Candidate resume and background",
                "interview_notes": "Previous interview feedback",
                "recruitment_stage": "Current recruitment stage"
            },
            "version": 1,
            "is_active": True,
            "metadata": {
                "description": "Assists recruiters with candidate evaluation",
                "output_format": "JSON",
                "estimated_tokens": 1300
            }
        }
    ]

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