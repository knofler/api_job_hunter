from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Any, Dict, List, Optional

import boto3

from .base import LLMProvider, LLMRequest


class BedrockProvider(LLMProvider):
    name = "bedrock"

    async def generate(self, request: LLMRequest) -> str:
        aws_region = request.extra_payload.get("aws_region")
        if not aws_region:
            raise ValueError("AWS region is required for Bedrock requests")

        aws_access_key_id = request.extra_payload.get("aws_access_key_id")
        aws_secret_access_key = request.extra_payload.get("aws_secret_access_key") or request.api_key
        aws_session_token = request.extra_payload.get("aws_session_token")

        payload = self._build_payload(request)

        def _invoke() -> str:
            client = boto3.client(
                "bedrock-runtime",
                region_name=aws_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
            )
            response = client.invoke_model(
                modelId=request.model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload).encode("utf-8"),
            )
            body = response.get("body")
            if hasattr(body, "read"):
                raw = body.read()
            else:
                raw = body or b""
            return raw.decode("utf-8")

        raw_response: str = await asyncio.to_thread(partial(_invoke))
        data = json.loads(raw_response)
        return self._extract_text(data)

    def _build_payload(self, request: LLMRequest) -> Dict[str, Any]:
        # Align with Anthropic message schema for Bedrock Claude models.
        system_messages: List[str] = [message.content for message in request.messages if message.role == "system"]
        chat_messages: List[Dict[str, str]] = [
            {"role": message.role, "content": message.content}
            for message in request.messages
            if message.role != "system"
        ]
        payload: Dict[str, Any] = {
            "messages": chat_messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or 2048,
        }
        if system_messages:
            payload["system"] = "\n\n".join(system_messages)
        if request.extra_payload:
            # Remove AWS credential hints before forwarding to model.
            payload.update(
                {
                    key: value
                    for key, value in request.extra_payload.items()
                    if key
                    not in {"aws_region", "aws_access_key_id", "aws_secret_access_key", "aws_session_token"}
                }
            )
        return payload

    def _extract_text(self, data: Dict[str, Any]) -> str:
        content = data.get("content", [])
        if not content:
            raise RuntimeError("Bedrock response missing content")
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        if not parts:
            raise RuntimeError("Bedrock response contained no text segments")
        return "".join(parts)
