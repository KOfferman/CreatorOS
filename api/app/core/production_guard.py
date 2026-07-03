from __future__ import annotations

import os

from app.auth.demo_auth import demo_auth_allowed
from app.core.config import Settings
from app.middlewares.rate_limit import is_production_redis_url
from app.services.llm_factory import resolve_llm_provider


def validate_production_settings(settings: Settings) -> None:
    env = settings.environment.strip().lower()
    if env not in {"production", "staging"}:
        return

    lowered_secret = settings.auth_secret.lower()
    if "changeme" in lowered_secret or "example" in lowered_secret:
        raise RuntimeError("AUTH_SECRET must be a real secret in production.")
    if len(settings.auth_secret.strip()) < 32:
        raise RuntimeError("AUTH_SECRET must be at least 32 characters in production.")

    if demo_auth_allowed(settings):
        raise RuntimeError(
            "DEMO_AUTH_ENABLED must be false in production. "
            "Use password auth (POST /auth/register) or set DEMO_AUTH_ENABLED only for staging demos."
        )

    if not settings.database_url or settings.database_url.startswith("sqlite"):
        raise RuntimeError("DATABASE_URL must be a persistent database in production.")

    token_key = settings.resolved_token_encryption_key()
    if len(token_key.strip()) < 32:
        raise RuntimeError("AUTH_SECRET (token encryption key) must be at least 32 characters in production.")

    if settings.llm_provider.lower() == "openai" and not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

    if os.environ.get("VERCEL"):
        resolved = resolve_llm_provider(settings)
        if resolved == "mock" and not settings.allow_mock_llm_in_production:
            raise RuntimeError(
                "Mock LLM is not allowed in production. "
                "Set OPENROUTER_API_KEY (Hermes) or ALLOW_MOCK_LLM_IN_PRODUCTION=true for demos."
            )

    if not settings.admin_user_ids:
        raise RuntimeError("ADMIN_USER_IDS must list at least one user id in production.")

    if not is_production_redis_url(settings.redis_url):
        raise RuntimeError(
            "REDIS_URL must point to a real Redis instance in production (e.g. Upstash)."
        )
