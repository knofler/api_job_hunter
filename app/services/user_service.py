from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId

from app.core.database import db


async def get_all_users(limit: int = 100) -> List[Dict[str, Any]]:
    cursor = db.users.find().limit(limit)
    users = await cursor.to_list(length=limit)
    for user in users:
        user["id"] = str(user.pop("_id"))
    return users


async def create_user(user_data: Dict[str, Any]) -> str:
    document = {
        **user_data,
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(document)
    return str(result.inserted_id)


async def delete_user(user_id: str) -> bool:
    try:
        object_id = ObjectId(user_id)
    except Exception:
        return False

    result = await db.users.delete_one({"_id": object_id})
    return result.deleted_count > 0