from app.core.database import db

# Example service to fetch users
def get_all_users():
    return list(db.users.find())

# Example service to create a user
def create_user(user_data):
    result = db.users.insert_one(user_data)
    return str(result.inserted_id)