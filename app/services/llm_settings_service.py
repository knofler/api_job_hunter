from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.core.database import db
from app.core.security import decrypt_secret, encrypt_secret
from app.models.llm_model import (
    LLMProviderConfig,
    LLMSettingsUpdatePayload,
    LLMWorkflowSettings,
    WORKFLOW_STEP_NAMES,
)

_collection = db.llm_settings


def _doc_id_for(org_id: Optional[str]) -> str:
    return f"org:{org_id}" if org_id else "global"


async def get_settings(org_id: Optional[str] = None) -> LLMWorkflowSettings:
    # Try tenant-specific first if org_id provided, else fallback to global
    key = _doc_id_for(org_id)
    document = await _collection.find_one({"_id": key})
    if document:
        return _document_to_settings(document)

    return _defaults_from_env()


async def update_settings(payload: LLMSettingsUpdatePayload, org_id: Optional[str] = None) -> LLMWorkflowSettings:
    key = _doc_id_for(org_id)
    existing_document = await _collection.find_one({"_id": key})
    existing_settings = _document_to_settings(existing_document) if existing_document else _defaults_from_env()

    merged_default = _merge_config(payload.default, existing_settings.default)
    merged_steps: Dict[str, LLMProviderConfig] = {}
    for step in WORKFLOW_STEP_NAMES:
        incoming = payload.steps.get(step)
        current = existing_settings.steps.get(step)
        if incoming:
            merged_steps[step] = _merge_config(incoming, current)
        elif current:
            merged_steps[step] = current

    document = {
        "_id": key,
        "org_id": org_id,
        "default": _config_to_document(merged_default),
        "steps": {step: _config_to_document(config) for step, config in merged_steps.items()},
        "updated_at": datetime.utcnow(),
    }

    await _collection.update_one({"_id": key}, {"$set": document}, upsert=True)
    return _document_to_settings(document)


def _defaults_from_env() -> LLMWorkflowSettings:
    default_config = _config_from_env()
    return LLMWorkflowSettings(default=default_config, steps={})


def env_config_for_provider(provider: str) -> LLMProviderConfig:
    return _config_from_env(provider)


def _config_from_env(provider: str | None = None) -> LLMProviderConfig:
    target = (provider or settings.LLM_DEFAULT_PROVIDER).lower().strip() or "openai"

    def _maybe_key(value: Optional[str]) -> Optional[str]:
        return None if settings.DISABLE_ENV_LLM_KEYS else value

    if target == "openai":
        config = LLMProviderConfig(
            provider="openai",
            model=settings.OPENAI_MODEL,
            api_key=_maybe_key(settings.OPENAI_API_KEY),
            base_url=settings.OPENAI_BASE_URL,
        )
        _validate_base_url(config.provider, config.base_url)
        return config
    if target == "anthropic":
        config = LLMProviderConfig(
            provider="anthropic",
            model=settings.ANTHROPIC_MODEL,
            api_key=_maybe_key(settings.ANTHROPIC_API_KEY),
        )
        _validate_base_url(config.provider, config.base_url)
        return config
    if target == "google":
        config = LLMProviderConfig(
            provider="google",
            model=settings.GOOGLE_GEMINI_MODEL,
            api_key=_maybe_key(settings.GOOGLE_GEMINI_API_KEY),
        )
        _validate_base_url(config.provider, config.base_url)
        return config
    if target == "deepseek":
        config = LLMProviderConfig(
            provider="deepseek",
            model=settings.DEEPSEEK_MODEL,
            api_key=_maybe_key(settings.DEEPSEEK_API_KEY),
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        _validate_base_url(config.provider, config.base_url)
        return config
    if target == "bedrock":
        extra_payload = {
            key: value
            for key, value in {
                "aws_region": settings.AWS_REGION,
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": _maybe_key(settings.AWS_SECRET_ACCESS_KEY),
                "aws_session_token": _maybe_key(settings.AWS_SESSION_TOKEN),
            }.items()
            if value
        }
        config = LLMProviderConfig(
            provider="bedrock",
            model=settings.BEDROCK_MODEL,
            api_key=_maybe_key(settings.AWS_SECRET_ACCESS_KEY),
            extra_payload=extra_payload,
        )
        _validate_base_url(config.provider, config.base_url)
        return config
    raise ValueError(f"Unsupported LLM provider '{target}' in environment configuration")


def _document_to_settings(document: Dict[str, Any]) -> LLMWorkflowSettings:
    if not document:
        return _defaults_from_env()

    default_config = _config_from_document(document.get("default", {}))
    steps = {
        step: _config_from_document(config)
        for step, config in document.get("steps", {}).items()
        if step in WORKFLOW_STEP_NAMES
    }
    return LLMWorkflowSettings(
        id=document.get("_id", "global"),
        default=default_config,
        steps=steps,
        updated_at=document.get("updated_at", datetime.utcnow()),
    )


def _merge_config(new_config: LLMProviderConfig, existing: LLMProviderConfig | None) -> LLMProviderConfig:
    existing = existing or env_config_for_provider(new_config.provider)

    def _normalise_model(value: str | None) -> str:
        if value and value.strip():
            return value
        return existing.model

    def _normalise_base(value: str | None) -> Optional[str]:
        return value if value else existing.base_url

    def _normalise_temperature(value: float | None) -> Optional[float]:
        return value if value is not None else existing.temperature

    def _normalise_max_tokens(value: int | None) -> Optional[int]:
        return value if value is not None else existing.max_tokens

    def _normalise_api_key(value: str | None) -> Optional[str]:
        """Normalise API key updates.

        Rules:
        - None: keep existing key (no change submitted)
        - Empty string: explicitly clear the key
        - Masked (starts with ****): keep existing key
        - Otherwise: use provided value
        """
        if value is None:
            return existing.api_key
        if value == "":
            return None
        if value.startswith("****"):
            return existing.api_key
        return value

    merged_payload: Dict[str, Any] = {**existing.extra_payload, **new_config.extra_payload}
    merged_config = LLMProviderConfig(
        provider=new_config.provider,
        model=_normalise_model(new_config.model),
        api_key=_normalise_api_key(new_config.api_key),
        base_url=_normalise_base(new_config.base_url),
        temperature=_normalise_temperature(new_config.temperature),
        max_tokens=_normalise_max_tokens(new_config.max_tokens),
        extra_headers={**existing.extra_headers, **new_config.extra_headers},
        extra_payload=merged_payload,
    )
    _validate_base_url(merged_config.provider, merged_config.base_url)
    return merged_config


def _config_to_document(config: LLMProviderConfig) -> Dict[str, Any]:
    data = config.dict()
    api_key = data.get("api_key")
    if api_key:
        data["api_key"] = encrypt_secret(api_key)
        data["api_key_encrypted"] = True
    else:
        data["api_key"] = None
        data["api_key_encrypted"] = False

    data["extra_payload"] = _encode_payload(data.get("extra_payload", {}))
    return data


def _config_from_document(document: Dict[str, Any]) -> LLMProviderConfig:
    data = dict(document)
    provider = data.get("provider") or settings.LLM_DEFAULT_PROVIDER

    api_key = data.get("api_key")
    if data.get("api_key_encrypted") and api_key:
        api_key = decrypt_secret(api_key)

    extra_payload = _decode_payload(data.get("extra_payload", {}))

    config = LLMProviderConfig(
        provider=provider,
        model=data.get("model") or env_config_for_provider(provider).model,
        api_key=api_key,
        base_url=data.get("base_url"),
        temperature=data.get("temperature"),
        max_tokens=data.get("max_tokens"),
        extra_headers=data.get("extra_headers", {}),
        extra_payload=extra_payload,
    )
    _validate_base_url(config.provider, config.base_url)
    return config


_ALLOWED_BASE_HOST_SUFFIXES: Dict[str, tuple[str, ...]] = {
    "openai": ("api.openai.com", ".openai.azure.com"),
    "anthropic": ("api.anthropic.com",),
    "google": ("generativelanguage.googleapis.com",),
    "deepseek": ("api.deepseek.com",),
    # Bedrock uses the AWS SDK instead of HTTP base URLs, so we ignore base_url.
    "bedrock": tuple(),
}


def _validate_base_url(provider: str, base_url: Optional[str]) -> None:
    if not base_url or provider == "bedrock":
        return

    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Base URL for provider '{provider}' must be an https URL (got '{base_url}').")

    allowed_suffixes = _ALLOWED_BASE_HOST_SUFFIXES.get(provider, tuple())
    if not allowed_suffixes:
        return

    host = parsed.netloc.lower()
    if any(host == suffix or host.endswith(suffix) for suffix in allowed_suffixes):
        return

    allowed_text = ", ".join(allowed_suffixes)
    raise ValueError(
        f"Base URL '{base_url}' is not allowed for provider '{provider}'. Expected host to match: {allowed_text}."
    )


SENSITIVE_PAYLOAD_KEYS = {
    "aws_secret_access_key",
    "aws_session_token",
    "aws_access_key_id",
}


def _encode_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    encoded: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str) and key in SENSITIVE_PAYLOAD_KEYS:
            encoded[key] = encrypt_secret(value)
            encoded[f"{key}_encrypted"] = True
        else:
            encoded[key] = value
    return encoded


def _decode_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    decoded: Dict[str, Any] = {}
    for key, value in payload.items():
        if key.endswith("_encrypted"):
            continue
        if isinstance(value, str) and payload.get(f"{key}_encrypted"):
            decoded[key] = decrypt_secret(value)
        else:
            decoded[key] = value
    return decoded
