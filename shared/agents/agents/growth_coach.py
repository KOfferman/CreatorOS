from __future__ import annotations

from typing import Any

from ai_core import TokenUsage
from pydantic import BaseModel, Field, ValidationError

from .base import AgentExecutionError, BaseAgent


class GrowthCoachInput(BaseModel):
    creator_profile: dict[str, Any]
    recent_trends: list[dict[str, Any]] = Field(default_factory=list)
    audience_insights: list[dict[str, Any]] = Field(default_factory=list)
    user_question: str = Field(min_length=1)


class GrowthCoachOutput(BaseModel):
    direct_coaching_response: str = Field(min_length=1)
    recommended_next_actions: list[str] = Field(default_factory=list)
    content_ideas: list[str] = Field(default_factory=list)
    risk_warning: str | None = None


class GrowthCoachAgent(BaseAgent[GrowthCoachInput, GrowthCoachOutput]):
    name = "growth-coach-agent"
    description = "Provides creator coaching in a chat-style, action-oriented response."
    input_schema = GrowthCoachInput
    output_schema = GrowthCoachOutput

    def __init__(self, *, llm_provider, max_output_validation_retries: int = 2, logger=None, session_factory=None):
        super().__init__(llm_provider=llm_provider, logger=logger, session_factory=session_factory)
        self.max_output_validation_retries = max_output_validation_retries

    def _run_with_usage(self, input_data: GrowthCoachInput) -> tuple[GrowthCoachOutput, TokenUsage]:
        prompt = self._build_prompt(input_data)
        total_usage = TokenUsage()
        last_validation_error: ValidationError | None = None

        for _ in range(self.max_output_validation_retries + 1):
            json_result = self.llm_provider.generate_json(
                prompt=prompt,
                system_prompt=(
                    "You are CreatorOS Growth Coach. Reply like a helpful strategist in a chat "
                    "experience: clear, direct, and practical. Return JSON only."
                ),
                temperature=0.4,
            )
            total_usage = self._add_usage(total_usage, json_result.usage)

            try:
                output = self.output_schema.model_validate(json_result.data)
                return output, total_usage
            except ValidationError as exc:
                last_validation_error = exc

        raise AgentExecutionError(
            "GrowthCoachAgent failed to produce valid output after retries."
        ) from last_validation_error

    def _build_prompt(self, input_data: GrowthCoachInput) -> str:
        return (
            "Provide coaching guidance using creator context and the question.\n\n"
            f"Creator profile: {input_data.creator_profile}\n"
            f"Recent trends: {input_data.recent_trends}\n"
            f"Audience insights: {input_data.audience_insights}\n"
            f"User question: {input_data.user_question}\n\n"
            "Return JSON with this exact shape:\n"
            "{\n"
            '  "direct_coaching_response": "string",\n'
            '  "recommended_next_actions": ["string"],\n'
            '  "content_ideas": ["string"],\n'
            '  "risk_warning": "string or null"\n'
            "}\n"
            "Rules:\n"
            "- direct_coaching_response should read like a direct chat reply to the user\n"
            "- include 3-5 recommended_next_actions when possible\n"
            "- include 3-5 concrete content_ideas aligned to trends and audience\n"
            "- set risk_warning only when there is a meaningful caution or downside"
        )

    @staticmethod
    def _add_usage(base: TokenUsage, extra: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=base.prompt_tokens + extra.prompt_tokens,
            completion_tokens=base.completion_tokens + extra.completion_tokens,
            total_tokens=base.total_tokens + extra.total_tokens,
        )
