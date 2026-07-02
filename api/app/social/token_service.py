from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class TokenEncryptionError(Exception):
    pass


def _fernet() -> Fernet:
    settings = get_settings()
    key_material = settings.resolved_token_encryption_key().encode("utf-8")
    digest = hashlib.sha256(key_material).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_token(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_token(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise TokenEncryptionError("Failed to decrypt stored token.") from exc
