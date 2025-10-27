from __future__ import annotations

import base64
import hashlib
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class EncryptionUnavailable(RuntimeError):
    """Raised when secret encryption is requested but no secret key is configured."""


def _derive_key(secret: str) -> bytes:
    stripped = secret.strip().encode("utf-8")
    try:
        Fernet(stripped)  # type: ignore[arg-type]
        return stripped
    except (ValueError, TypeError):  # noqa: PERF203 - explicit handling preferred
        digest = hashlib.sha256(stripped).digest()
        return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def _get_cipher() -> Fernet:
    secret = settings.LLM_SETTINGS_SECRET_KEY
    if not secret:
        raise EncryptionUnavailable(
            "LLM_SETTINGS_SECRET_KEY is not configured; store secrets via environment variables or set a key."
        )
    key = _derive_key(secret)
    return Fernet(key)


def encrypt_secret(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    cipher = _get_cipher()
    token = cipher.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_secret(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    cipher = _get_cipher()
    try:
        decrypted = cipher.decrypt(value.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken as exc:  # noqa: BLE001
        raise RuntimeError("Failed to decrypt stored secret; verify LLM_SETTINGS_SECRET_KEY") from exc