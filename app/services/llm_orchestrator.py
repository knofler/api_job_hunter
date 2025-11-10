from __future__ import annotations

from typing import Dict, Iterable

from app.models.llm_model import LLMProviderConfig
from app.services.llm_providers import (
    AnthropicProvider,
    BedrockProvider,
    DeepSeekProvider,
    GoogleGenerativeAIProvider,
    OpenAIProvider,
)
from app.services.llm_providers.base import LLMMessage, LLMRequest, LLMProvider, ProviderNotConfiguredError
from app.services.llm_settings_service import env_config_for_provider

_DEFAULT_TEMPERATURE = 0.2


class LLMOrchestrator:
    def __init__(self) -> None:
        self._providers: Dict[str, LLMProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleGenerativeAIProvider(),
            "deepseek": DeepSeekProvider(),
            "bedrock": BedrockProvider(),
        }

    async def generate(self, messages: Iterable[LLMMessage], config: LLMProviderConfig, response_format: str = "json") -> str:
        hydrated = self._hydrate_config(config)
        provider = self._providers.get(hydrated.provider)
        if provider is None:
            raise ValueError(f"Unsupported LLM provider '{hydrated.provider}'")

        request = LLMRequest(
            model=hydrated.model,
            messages=list(messages),
            api_key=hydrated.api_key or "",
            base_url=hydrated.base_url,
            max_tokens=hydrated.max_tokens,
            temperature=hydrated.temperature if hydrated.temperature is not None else _DEFAULT_TEMPERATURE,
            extra_headers=hydrated.extra_headers,
            extra_payload=hydrated.extra_payload,
            response_format=response_format,
        )

        if not request.api_key and hydrated.provider not in {"bedrock"}:
            raise ProviderNotConfiguredError(
                f"Provider '{hydrated.provider}' is missing an API key. Configure credentials in env vars or admin settings."
            )

        return await provider.generate(request)

    async def generate_stream(self, messages: Iterable[LLMMessage], config: LLMProviderConfig, response_format: str = "json"):
        """Generate content with streaming support (token by token)."""
        hydrated = self._hydrate_config(config)
        provider = self._providers.get(hydrated.provider)
        if provider is None:
            raise ValueError(f"Unsupported LLM provider '{hydrated.provider}'")

        request = LLMRequest(
            model=hydrated.model,
            messages=list(messages),
            api_key=hydrated.api_key or "",
            base_url=hydrated.base_url,
            max_tokens=hydrated.max_tokens,
            temperature=hydrated.temperature if hydrated.temperature is not None else _DEFAULT_TEMPERATURE,
            extra_headers=hydrated.extra_headers,
            extra_payload=hydrated.extra_payload,
            response_format=response_format,
        )

        if not request.api_key and hydrated.provider not in {"bedrock"}:
            raise ProviderNotConfiguredError(
                f"Provider '{hydrated.provider}' is missing an API key. Configure credentials in env vars or admin settings."
            )

        async for chunk in provider.generate_stream(request):
            yield chunk

    def _hydrate_config(self, config: LLMProviderConfig) -> LLMProviderConfig:
        env_defaults = env_config_for_provider(config.provider)

        return LLMProviderConfig(
            provider=config.provider,
            model=config.model or env_defaults.model,
            api_key=config.api_key or env_defaults.api_key,
            base_url=config.base_url or env_defaults.base_url,
            temperature=config.temperature if config.temperature is not None else env_defaults.temperature,
            max_tokens=config.max_tokens or env_defaults.max_tokens,
            extra_headers={**env_defaults.extra_headers, **config.extra_headers},
            extra_payload={**env_defaults.extra_payload, **config.extra_payload},
        )
