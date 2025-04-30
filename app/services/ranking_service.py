def calculate_ranking(user_skills, job_skills):
    # Example logic to calculate match score
    matching_skills = set(user_skills) & set(job_skills)
    match_score = len(matching_skills) / len(job_skills) * 100
    return round(match_score, 2)