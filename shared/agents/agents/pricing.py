from __future__ import annotations

import json
import os
from decimal import Decimal

# USD per 1K tokens: (input_rate, output_rate)
# Extend via LLM_MODEL_PRICING_JSON env: {"model-name": [input, output], ...}
DEFAULT_MODEL_PRICING_PER_1K: dict[str, tuple[Decimal, Decimal]] = {
    "gpt-4o-mini": (Decimal("0.00015"), Decimal("0.00060")),
    "gpt-4o": (Decimal("0.00250"), Decimal("0.01000")),
    "gpt-4o-mini-2024-07-18": (Decimal("0.00015"), Decimal("0.00060")),
    "nousresearch/hermes-3-llama-3.1-70b": (Decimal("0.00013"), Decimal("0.00039")),
    "hermes3": (Decimal("0"), Decimal("0")),
    "mock": (Decimal("0"), Decimal("0")),
    "mock-model": (Decimal("0"), Decimal("0")),
    "mock-coach": (Decimal("0"), Decimal("0")),
    "mock-provider": (Decimal("0"), Decimal("0")),
}

_PROVIDER_DEFAULTS: dict[str, tuple[Decimal, Decimal]] = {
    "openai": (Decimal("0.00015"), Decimal("0.00060")),
    "openrouter": (Decimal("0.00013"), Decimal("0.00039")),
    "mock": (Decimal("0"), Decimal("0")),
    "ollama": (Decimal("0"), Decimal("0")),
    "hermes": (Decimal("0"), Decimal("0")),
}


def _load_env_overrides() -> dict[str, tuple[Decimal, Decimal]]:
    raw = os.environ.get("LLM_MODEL_PRICING_JSON", "").strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    overrides: dict[str, tuple[Decimal, Decimal]] = {}
    for model, rates in parsed.items():
        if not isinstance(model, str) or not isinstance(rates, (list, tuple)) or len(rates) != 2:
            continue
        overrides[model] = (Decimal(str(rates[0])), Decimal(str(rates[1])))
    return overrides


def pricing_table() -> dict[str, tuple[Decimal, Decimal]]:
    table = dict(DEFAULT_MODEL_PRICING_PER_1K)
    table.update(_load_env_overrides())
    return table


def resolve_model_pricing(*, provider_name: str, model_name: str) -> tuple[Decimal, Decimal]:
    table = pricing_table()
    provider = provider_name.strip().lower()
    model = model_name.strip()

    if model in table:
        return table[model]

    provider_model_key = f"{provider}:{model}"
    if provider_model_key in table:
        return table[provider_model_key]

    return _PROVIDER_DEFAULTS.get(provider, (Decimal("0"), Decimal("0")))


def estimate_token_cost(
    *,
    provider_name: str,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> tuple[Decimal, Decimal, Decimal]:
    input_rate, output_rate = resolve_model_pricing(
        provider_name=provider_name,
        model_name=model_name,
    )
    input_cost = (Decimal(prompt_tokens) / Decimal(1000)) * input_rate
    output_cost = (Decimal(completion_tokens) / Decimal(1000)) * output_rate
    total = input_cost + output_cost
    return (
        input_cost.quantize(Decimal("0.0000001")),
        output_cost.quantize(Decimal("0.0000001")),
        total.quantize(Decimal("0.0000001")),
    )
