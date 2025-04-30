from app.core.database import db

# Example service to fetch resumes
def get_all_resumes():
    return list(db.resumes.find())

# Example service to upload a resume
def upload_resume(resume_data):
    result = db.resumes.insert_one(resume_data)
    return str(result.inserted_id)