from typing import Iterable


def _normalise(skills: Iterable[str]) -> set[str]:
    return {skill.lower().strip() for skill in skills if skill}


def calculate_ranking(user_skills: Iterable[str], job_skills: Iterable[str]) -> float:
    job_skill_set = _normalise(job_skills)
    if not job_skill_set:
        return 0.0

    user_skill_set = _normalise(user_skills)
    matching_skills = user_skill_set & job_skill_set
    match_score = len(matching_skills) / len(job_skill_set) * 100
    return round(match_score, 2)