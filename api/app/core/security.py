from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import get_settings


class AuthError(Exception):
    pass


def create_access_token(*, subject: str, email: str, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp_minutes = expires_minutes or settings.auth_access_token_exp_minutes
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
        "iss": "creatoros-api",
        "aud": "creatoros-clients",
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=settings.auth_jwt_algorithm)


def verify_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.auth_secret,
            algorithms=[settings.auth_jwt_algorithm],
            audience="creatoros-clients",
            issuer="creatoros-api",
        )
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired access token.") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise AuthError("Token missing subject.")
    return payload
