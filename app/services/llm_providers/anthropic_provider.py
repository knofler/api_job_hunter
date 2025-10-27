from __future__ import annotations

from typing import Any, Dict, List

import httpx

from .base import LLMMessage, LLMProvider, LLMRequest, ProviderNotConfiguredError, ensure_api_key


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    _endpoint = "https://api.anthropic.com/v1/messages"
    _api_version = "2023-06-01"

    async def generate(self, request: LLMRequest) -> str:
        ensure_api_key(request)

        headers = {
            "x-api-key": request.api_key,
            "Content-Type": "application/json",
            "anthropic-version": self._api_version,
        }
        headers.update(request.extra_headers)

        payload = self._build_payload(request)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(self._endpoint, headers=headers, json=payload)

        if response.status_code == 401:
            raise ProviderNotConfiguredError("Invalid Anthropic API key provided")

        response.raise_for_status()
        data = response.json()
        return self._extract_content(data)

    def _build_payload(self, request: LLMRequest) -> Dict[str, Any]:
        system_messages: List[str] = [message.content for message in request.messages if message.role == "system"]
        chat_messages: List[Dict[str, str]] = [
            {"role": message.role, "content": message.content}
            for message in request.messages
            if message.role != "system"
        ]
        payload: Dict[str, Any] = {
            "model": request.model,
            "messages": chat_messages,
            "max_tokens": request.max_tokens or 2048,
            "temperature": request.temperature,
        }
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)
        if request.extra_payload:
            payload.update(request.extra_payload)
        return payload

    def _extract_content(self, data: Dict[str, Any]) -> str:
        content = data.get("content", [])
        if not content:
            raise RuntimeError("Anthropic response missing content")
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        if not parts:
            raise RuntimeError("Anthropic response contained no text content")
        return "".join(parts)
