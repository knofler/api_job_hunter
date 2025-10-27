from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

LLMMessageRole = Literal["system", "user", "assistant"]


@dataclass
class LLMMessage:
    role: LLMMessageRole
    content: str


@dataclass
class LLMRequest:
    model: str
    messages: List[LLMMessage]
    api_key: str
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.2
    response_format: Literal["json", "text"] = "json"
    extra_headers: Dict[str, str] = field(default_factory=dict)
    extra_payload: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(abc.ABC):
    """Contract every concrete LLM provider implementation must follow."""

    name: str

    @abc.abstractmethod
    async def generate(self, request: LLMRequest) -> str:
        """Generate content from the underlying provider.

        Implementations must raise ``ValueError`` for configuration issues and ``RuntimeError`` for provider errors.
        """

    def supports_response_format(self, response_format: str) -> bool:
        """Return True if this provider natively supports the requested response format."""
        return response_format == "text"


class ProviderNotConfiguredError(RuntimeError):
    """Raised when a provider is selected but lacks credentials or configuration."""


def ensure_api_key(request: LLMRequest) -> None:
    if not request.api_key:
        raise ProviderNotConfiguredError("Missing API key for provider request")
