from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict

import httpx

from .base import LLMProvider, LLMRequest, ProviderNotConfiguredError, ensure_api_key


class DeepSeekProvider(LLMProvider):
    name = "deepseek"

    async def generate(self, request: LLMRequest) -> str:
        ensure_api_key(request)

        base_url = request.base_url or "https://api.deepseek.com"
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
            raise ProviderNotConfiguredError("Invalid DeepSeek API key provided")

        response.raise_for_status()
        data = response.json()
        return self._extract_text(data)

    def _build_payload(self, request: LLMRequest) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": [
                {"role": message.role, "content": message.content} for message in request.messages
            ],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.extra_payload:
            payload.update(request.extra_payload)
        return payload

    def _extract_text(self, data: Dict[str, Any]) -> str:
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("DeepSeek response missing choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("DeepSeek response missing message content")
        return content

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate content with streaming support (token by token)."""
        ensure_api_key(request)

        base_url = request.base_url or "https://api.deepseek.com"
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {request.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(request.extra_headers)

        payload = self._build_payload(request)
        payload["stream"] = True  # Enable streaming

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code == 401:
                    raise ProviderNotConfiguredError("Invalid DeepSeek API key provided")
                
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip() or line.strip() == "data: [DONE]":
                        continue
                    
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
