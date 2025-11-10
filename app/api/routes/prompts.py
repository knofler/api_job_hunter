from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.prompt_service import (
    get_all_prompts,
    get_prompt_by_id,
    get_prompt_by_name,
    create_prompt,
    update_prompt,
    delete_prompt,
    get_prompts_by_category
)
from app.models.prompt_model import PromptCreate, PromptUpdate
from app.api.dependencies import AdminDependency

router = APIRouter(prefix="/api/admin/prompts", tags=["admin-prompts"], dependencies=[AdminDependency])


@router.get("")
async def get_prompts(
    category: Optional[str] = None,
    limit: int = 100,
    current_user: dict = AdminDependency
):
    """Get all prompts, optionally filtered by category."""
    if category:
        prompts = await get_prompts_by_category(category)
    else:
        prompts = await get_all_prompts(limit=limit)
    return {"prompts": prompts}


@router.get("/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    current_user: dict = AdminDependency
):
    """Get a specific prompt by ID."""
    prompt = await get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"prompt": prompt}


@router.get("/by-name/{name}")
async def get_prompt_by_name_endpoint(
    name: str,
    current_user: dict = AdminDependency
):
    """Get a prompt by name."""
    prompt = await get_prompt_by_name(name)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"prompt": prompt}


@router.post("")
async def create_new_prompt(
    prompt_data: PromptCreate,
    current_user: dict = AdminDependency
):
    """Create a new prompt."""
    try:
        prompt_id = await create_prompt(prompt_data, current_user.get("id", "system"))
        return {"message": "Prompt created successfully", "prompt_id": prompt_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create prompt: {str(e)}")


@router.put("/{prompt_id}")
async def update_existing_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    current_user: dict = AdminDependency
):
    """Update an existing prompt."""
    success = await update_prompt(prompt_id, prompt_data, current_user.get("id", "system"))
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found or update failed")
    return {"message": "Prompt updated successfully"}


@router.delete("/{prompt_id}")
async def delete_existing_prompt(
    prompt_id: str,
    current_user: dict = AdminDependency
):
    """Delete a prompt (soft delete)."""
    success = await delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found or delete failed")
    return {"message": "Prompt deleted successfully"}


@router.get("/categories/{category}")
async def get_prompts_by_category_endpoint(
    category: str,
    current_user: dict = AdminDependency
):
    """Get all prompts for a specific category."""
    prompts = await get_prompts_by_category(category)
    return {"prompts": prompts, "category": category}