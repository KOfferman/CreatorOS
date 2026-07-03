from __future__ import annotations

import os

import httpx

from app.core.config import Settings

_HERMES_PROVIDERS = {"hermes", "hermes-local", "ollama"}


def uses_local_ollama(settings: Settings) -> bool:
    return settings.llm_provider.strip().lower() in _HERMES_PROVIDERS


def ollama_tags_url(settings: Settings) -> str:
    return f"{settings.ollama_base_url.rstrip('/')}/api/tags"


def check_ollama_reachable(settings: Settings, *, timeout_seconds: float = 5.0) -> bool:
    if not uses_local_ollama(settings):
        return True
    try:
        response = httpx.get(ollama_tags_url(settings), timeout=timeout_seconds)
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False


async def verify_ollama_for_startup(settings: Settings) -> None:
    """Fail fast when Hermes/Ollama is configured but the daemon is not running."""
    if settings.environment.lower() == "test":
        return
    if os.environ.get("VERCEL"):
        return
    if os.environ.get("CI") == "true":
        return
    if not uses_local_ollama(settings):
        return

    base_url = settings.ollama_base_url.rstrip("/")
    tags_url = ollama_tags_url(settings)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(tags_url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"LLM_PROVIDER={settings.llm_provider} requires Ollama at {base_url}, "
            "but it is not reachable. Start it with:\n"
            "  brew services start ollama\n"
            "or run the API via:\n"
            "  cd api && make dev"
        ) from exc
