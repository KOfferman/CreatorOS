from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_core import (
    BaseLLMProvider,
    TokenUsage,
)
from pydantic import BaseModel, ValidationError

from .registry import PromptRegistry
from .system_prompts import SYSTEM_PROMPTS

_PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "reveal hidden instructions",
    "print your chain of thought",
    "<script",
    "javascript:",
)


class PromptExecutionError(Exception):
    pass


class PromptOutputValidationError(PromptExecutionError):
    pass


@dataclass(frozen=True, slots=True)
class PromptExecutionResult:
    output: BaseModel
    usage: TokenUsage
    provider_name: str
    model_name: str
    prompt_name: str
    prompt_version: str
    raw_response: dict[str, Any] | None = None


@dataclass(slots=True)
class PromptManager:
    registry: PromptRegistry
    max_validation_retries: int = 2

    @staticmethod
    def _assert_safe_text(value: str, *, field_name: str) -> None:
        lowered = value.lower()
        for pattern in _PROMPT_INJECTION_PATTERNS:
            if pattern in lowered:
                raise PromptExecutionError(
                    f"Prompt input field '{field_name}' contains disallowed injection pattern."
                )

    def _validate_input_guardrails(self, input_obj: BaseModel) -> None:
        for field_name, value in input_obj.model_dump(mode="json").items():
            if isinstance(value, str):
                self._assert_safe_text(value, field_name=field_name)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        self._assert_safe_text(item, field_name=field_name)

    def run_json(
        self,
        *,
        provider: BaseLLMProvider,
        prompt_name: str,
        prompt_version: str,
        input_data: BaseModel | dict[str, Any],
    ) -> PromptExecutionResult:
        template = self.registry.get(name=prompt_name, version=prompt_version)
        input_obj = template.input_schema.model_validate(input_data)
        self._validate_input_guardrails(input_obj)
        prompt = template.user_prompt_template.format(**input_obj.model_dump())
        system_prompt = SYSTEM_PROMPTS.get(template.system_prompt_key, "")

        last_validation_error: ValidationError | None = None

        for _ in range(self.max_validation_retries + 1):
            json_result = provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=template.temperature,
                max_tokens=template.max_tokens,
            )

            try:
                output_obj = template.output_schema.model_validate(json_result.data)
                return PromptExecutionResult(
                    output=output_obj,
                    usage=json_result.usage,
                    provider_name=json_result.provider_name,
                    model_name=json_result.model_name,
                    prompt_name=template.name,
                    prompt_version=template.version,
                    raw_response=json_result.raw_response,
                )
            except ValidationError as exc:
                last_validation_error = exc

        raise PromptOutputValidationError(
            "Prompt JSON output failed schema validation after retries."
        ) from last_validation_error

    def run_text(
        self,
        *,
        provider: BaseLLMProvider,
        prompt_name: str,
        prompt_version: str,
        input_data: BaseModel | dict[str, Any],
    ) -> str:
        template = self.registry.get(name=prompt_name, version=prompt_version)
        input_obj = template.input_schema.model_validate(input_data)
        self._validate_input_guardrails(input_obj)
        prompt = template.user_prompt_template.format(**input_obj.model_dump())
        system_prompt = SYSTEM_PROMPTS.get(template.system_prompt_key, "")

        result = provider.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=template.temperature,
            max_tokens=template.max_tokens,
        )
        return result.text


def build_default_prompt_manager() -> PromptManager:
    from .templates import SUMMARIZE_V1

    registry = PromptRegistry()
    registry.register(SUMMARIZE_V1)
    return PromptManager(registry=registry, max_validation_retries=2)
