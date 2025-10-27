from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

LLMProviderName = Literal["openai", "anthropic", "google", "deepseek", "bedrock"]

WORKFLOW_STEP_NAMES = {
    "core_skills",
    "ai_analysis",
    "ranked_shortlist",
    "detailed_readout",
    "engagement_plan",
    "fairness_guidance",
    "interview_preparation",
}


class LLMProviderConfig(BaseModel):
    provider: LLMProviderName
    model: str
    api_key: Optional[str] = Field(default=None, description="API key or secret token for the provider")
    base_url: Optional[str] = Field(default=None, description="Optional override for the provider base URL")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    extra_headers: Dict[str, str] = Field(default_factory=dict)
    extra_payload: Dict[str, Any] = Field(default_factory=dict)


class LLMWorkflowStepConfig(BaseModel):
    step: str
    config: LLMProviderConfig


class LLMWorkflowSettings(BaseModel):
    _id: str = Field(default="global", alias="id")
    default: LLMProviderConfig
    steps: Dict[str, LLMProviderConfig] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

    def masked(self) -> "LLMWorkflowSettings":
        return LLMWorkflowSettings(
            id=self._id,
            default=_mask_config(self.default),
            steps={step: _mask_config(cfg) for step, cfg in self.steps.items()},
            updated_at=self.updated_at,
        )


def _mask_secret(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def _mask_config(config: LLMProviderConfig) -> LLMProviderConfig:
    return LLMProviderConfig(
        provider=config.provider,
        model=config.model,
        api_key=_mask_secret(config.api_key),
        base_url=config.base_url,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        extra_headers=config.extra_headers,
        extra_payload=config.extra_payload,
    )


class LLMSettingsUpdatePayload(BaseModel):
    default: LLMProviderConfig
    steps: Dict[str, LLMProviderConfig] = Field(default_factory=dict)
