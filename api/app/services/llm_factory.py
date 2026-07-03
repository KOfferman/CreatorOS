from __future__ import annotations

from ai_core import BaseLLMProvider, build_provider

from app.core.config import Settings


def build_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Build the configured LLM provider for agents (coach, content writer, etc.)."""
    provider = settings.llm_provider.strip().lower()
    model = settings.resolved_llm_model()

    if provider == "openclaw":
        return build_provider(
            "openclaw",
            api_key=settings.openclaw_gateway_token or "local",
            model=settings.openclaw_model or model,
            api_base=f"{settings.openclaw_gateway_url.rstrip('/')}/v1/chat/completions",
        )

    if provider in {"hermes", "hermes-local", "ollama"}:
        return build_provider(
            "hermes",
            api_key="ollama",
            model=settings.ollama_model or model,
            api_base=f"{settings.ollama_base_url.rstrip('/')}/v1/chat/completions",
        )

    if provider == "openrouter":
        return build_provider(
            "openrouter",
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model or model,
            extra_headers={
                "HTTP-Referer": settings.auth_url,
                "X-Title": "CreatorOS",
            },
        )

    if provider == "openai":
        return build_provider(
            "openai",
            api_key=settings.openai_api_key,
            model=settings.openai_model or model,
        )

    if provider == "mock":
        return build_provider("mock", model=model)

    return build_provider(
        provider,
        api_key=settings.openai_api_key,
        model=model,
    )
