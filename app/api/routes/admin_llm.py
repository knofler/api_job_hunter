from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import AdminDependency
from app.models.llm_model import LLMSettingsUpdatePayload
from app.services import llm_settings_service

router = APIRouter(prefix="/admin/llm", tags=["admin-llm"], dependencies=[AdminDependency])


@router.get("/providers")
def list_providers() -> dict:
    return {
        "providers": [
            {
                "id": "openai",
                "label": "OpenAI",
                "supports_json_mode": True,
                "notes": "Supports GPT-4o, GPT-4.1, GPT-4o-mini, JSON mode recommended.",
            },
            {
                "id": "anthropic",
                "label": "Anthropic Claude",
                "supports_json_mode": True,
                "notes": "Use Claude 3 Haiku/Sonnet/Opus via Anthropic API.",
            },
            {
                "id": "google",
                "label": "Google Gemini",
                "supports_json_mode": False,
                "notes": "Gemini 1.5 Flash or Pro via Google Generative AI API.",
            },
            {
                "id": "deepseek",
                "label": "DeepSeek",
                "supports_json_mode": False,
                "notes": "DeepSeek Chat-style endpoint compatible with OpenAI schema.",
            },
            {
                "id": "bedrock",
                "label": "AWS Bedrock",
                "supports_json_mode": True,
                "notes": "Supports Claude on Bedrock. Provide region and AWS credentials.",
            },
        ]
    }


@router.get("/settings")
async def get_settings() -> dict:
    settings_doc = await llm_settings_service.get_settings()
    return settings_doc.masked().dict(by_alias=True)


@router.put("/settings")
async def put_settings(payload: LLMSettingsUpdatePayload) -> dict:
    try:
        updated = await llm_settings_service.update_settings(payload)
        return updated.masked().dict(by_alias=True)
    except RuntimeError as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
