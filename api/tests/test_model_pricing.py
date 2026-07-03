from decimal import Decimal

from agents.pricing import estimate_token_cost, resolve_model_pricing


def test_resolve_openai_model_pricing() -> None:
    input_rate, output_rate = resolve_model_pricing(
        provider_name="openai",
        model_name="gpt-4o-mini",
    )
    assert input_rate == Decimal("0.00015")
    assert output_rate == Decimal("0.00060")


def test_resolve_openrouter_hermes_pricing() -> None:
    input_rate, output_rate = resolve_model_pricing(
        provider_name="openrouter",
        model_name="nousresearch/hermes-3-llama-3.1-70b",
    )
    assert input_rate > Decimal("0")
    assert output_rate > Decimal("0")


def test_estimate_token_cost_for_mock_is_zero() -> None:
    input_cost, output_cost, total = estimate_token_cost(
        provider_name="mock",
        model_name="mock-model",
        prompt_tokens=1000,
        completion_tokens=500,
    )
    assert input_cost == Decimal("0")
    assert output_cost == Decimal("0")
    assert total == Decimal("0")


def test_env_pricing_override(monkeypatch) -> None:
    monkeypatch.setenv(
        "LLM_MODEL_PRICING_JSON",
        '{"custom-model": [0.001, 0.002]}',
    )
    input_rate, output_rate = resolve_model_pricing(
        provider_name="custom",
        model_name="custom-model",
    )
    assert input_rate == Decimal("0.001")
    assert output_rate == Decimal("0.002")
