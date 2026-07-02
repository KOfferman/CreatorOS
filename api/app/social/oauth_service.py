from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from app.social.base import SocialProviderError


def create_oauth_state(*, user_id: str, platform: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "platform": platform,
        "purpose": "social_oauth_state",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "iss": "creatoros-api",
        "aud": "creatoros-social-oauth",
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=settings.auth_jwt_algorithm)


def verify_oauth_state(state: str) -> tuple[str, str]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            state,
            settings.auth_secret,
            algorithms=[settings.auth_jwt_algorithm],
            audience="creatoros-social-oauth",
            issuer="creatoros-api",
        )
    except jwt.PyJWTError as exc:
        raise SocialProviderError("Invalid or expired OAuth state.") from exc

    if payload.get("purpose") != "social_oauth_state":
        raise SocialProviderError("Invalid OAuth state purpose.")

    user_id = payload.get("sub")
    platform = payload.get("platform")
    if not isinstance(user_id, str) or not user_id:
        raise SocialProviderError("OAuth state missing user.")
    if not isinstance(platform, str) or not platform:
        raise SocialProviderError("OAuth state missing platform.")
    return user_id, platform
