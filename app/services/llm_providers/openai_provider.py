from __future__ import annotations

from typing import Any, Dict, List

import httpx

from .base import LLMProvider, LLMRequest, ProviderNotConfiguredError, ensure_api_key


class OpenAIProvider(LLMProvider):
    name = "openai"
    _default_base_url = "https://api.openai.com/v1"

    async def generate(self, request: LLMRequest) -> str:
        ensure_api_key(request)

        base_url = request.base_url or self._default_base_url
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(request.extra_headers)

        payload = self._build_payload(request)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code == 401:
            raise ProviderNotConfiguredError("Invalid OpenAI API key provided")

        if response.status_code == 400 and request.response_format == "json":
            # Retry without JSON mode for models that do not support response_format.
            fallback_payload = self._build_payload(request, force_text=True)
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                retry_response = await client.post(url, headers=headers, json=fallback_payload)
            retry_response.raise_for_status()
            return self._extract_text(retry_response.json())

        response.raise_for_status()
        data = response.json()

        if request.response_format == "json":
            return self._extract_json(data)
        return self._extract_text(data)

    def _build_payload(self, request: LLMRequest, *, force_text: bool = False) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = [
            {"role": message.role, "content": message.content} for message in request.messages
        ]
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        if request.response_format == "json" and not force_text:
            payload["response_format"] = {"type": "json_object"}

        if request.extra_payload:
            payload.update(request.extra_payload)
        return payload

    def _extract_json(self, data: Dict[str, Any]) -> str:
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("OpenAI response missing JSON content")
        return content

    def _extract_text(self, data: Dict[str, Any]) -> str:
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content")
        if content is None:
            raise RuntimeError("OpenAI response missing text content")
        if isinstance(content, list):
            # Some responses stream chunks; concatenate text segments.
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return str(content)
