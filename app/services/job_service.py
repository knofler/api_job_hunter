from app.core.database import db

# Example service to fetch jobs
def get_all_jobs():
    return list(db.jobs.find())

# Example service to create a job
def create_job(job_data):
    result = db.jobs.insert_one(job_data)
    return str(result.inserted_id)