from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from app.core.database import db
from app.models.prompt_model import PromptCreate, PromptUpdate


async def get_all_prompts(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all prompts with optional filtering."""
    cursor = db.prompts.find({"is_active": True}).limit(limit)
    prompts = await cursor.to_list(length=limit)
    for prompt in prompts:
        prompt["id"] = str(prompt.pop("_id"))
    return prompts


async def get_prompt_by_id(prompt_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific prompt by ID."""
    try:
        object_id = ObjectId(prompt_id)
    except Exception:
        return None

    prompt = await db.prompts.find_one({"_id": object_id})
    if prompt:
        prompt["id"] = str(prompt.pop("_id"))
    return prompt


async def get_prompt_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get a prompt by name."""
    prompt = await db.prompts.find_one({"name": name, "is_active": True})
    if prompt:
        prompt["id"] = str(prompt.pop("_id"))
    return prompt


async def create_prompt(prompt_data: PromptCreate, created_by: str = "system") -> str:
    """Create a new prompt."""
    document = {
        **prompt_data.dict(),
        "version": 1,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": created_by,
        "updated_by": created_by,
    }
    result = await db.prompts.insert_one(document)
    return str(result.inserted_id)


async def update_prompt(prompt_id: str, prompt_data: PromptUpdate, updated_by: str = "system") -> bool:
    """Update an existing prompt."""
    try:
        object_id = ObjectId(prompt_id)
    except Exception:
        return False

    # Get current prompt to increment version
    current = await db.prompts.find_one({"_id": object_id})
    if not current:
        return False

    update_data = prompt_data.dict(exclude_unset=True)
    update_data.update({
        "updated_at": datetime.utcnow(),
        "updated_by": updated_by,
        "version": current.get("version", 1) + 1,
    })

    result = await db.prompts.update_one(
        {"_id": object_id},
        {"$set": update_data}
    )
    return result.modified_count > 0


async def delete_prompt(prompt_id: str) -> bool:
    """Soft delete a prompt by setting is_active to False."""
    try:
        object_id = ObjectId(prompt_id)
    except Exception:
        return False

    result = await db.prompts.update_one(
        {"_id": object_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0


async def get_prompts_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all prompts for a specific category."""
    cursor = db.prompts.find({"category": category, "is_active": True})
    prompts = await cursor.to_list(length=None)
    for prompt in prompts:
        prompt["id"] = str(prompt.pop("_id"))
    return prompts


async def _serialize_prompt(prompt_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a prompt document for API response."""
    if "_id" in prompt_doc:
        prompt_doc["id"] = str(prompt_doc.pop("_id"))
    if "created_at" in prompt_doc and isinstance(prompt_doc["created_at"], datetime):
        prompt_doc["created_at"] = prompt_doc["created_at"].isoformat()
    if "updated_at" in prompt_doc and isinstance(prompt_doc["updated_at"], datetime):
        prompt_doc["updated_at"] = prompt_doc["updated_at"].isoformat()
    return prompt_doc