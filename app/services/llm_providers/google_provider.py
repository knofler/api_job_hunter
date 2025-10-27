from __future__ import annotations

from typing import Any, Dict, List

import httpx

from .base import LLMProvider, LLMRequest, ProviderNotConfiguredError, ensure_api_key


class GoogleGenerativeAIProvider(LLMProvider):
    name = "google"
    _endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def generate(self, request: LLMRequest) -> str:
        ensure_api_key(request)

        url = self._endpoint.format(model=request.model)
        params = {"key": request.api_key}
        headers = {"Content-Type": "application/json"}
        headers.update(request.extra_headers)

        payload = self._build_payload(request)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(url, params=params, headers=headers, json=payload)

        if response.status_code == 401 or response.status_code == 403:
            raise ProviderNotConfiguredError("Google Generative AI rejected the API key or model access")

        response.raise_for_status()
        data = response.json()
        return self._extract_text(data)

    def _build_payload(self, request: LLMRequest) -> Dict[str, Any]:
        system_prompt_parts: List[str] = [message.content for message in request.messages if message.role == "system"]
        user_messages: List[Dict[str, Any]] = []

        prepend_system = "\n\n".join(system_prompt_parts) if system_prompt_parts else ""

        for message in request.messages:
            if message.role == "system":
                continue
            role = "user" if message.role == "user" else "model"
            text = message.content
            if role == "user" and prepend_system:
                text = f"{prepend_system}\n\nUser request:\n{text}"
                prepend_system = ""
            user_messages.append({"role": role, "parts": [{"text": text}]})

        if prepend_system:
            user_messages.insert(0, {"role": "user", "parts": [{"text": prepend_system}]})

        payload: Dict[str, Any] = {
            "contents": user_messages,
            "generationConfig": {
                "temperature": request.temperature,
            },
        }
        if request.max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = request.max_tokens
        if request.extra_payload:
            payload.update(request.extra_payload)
        return payload

    def _extract_text(self, data: Dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Google Generative AI response missing candidates")
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                text = part.get("text")
                if text:
                    return text
        raise RuntimeError("Google Generative AI response contained no text output")
