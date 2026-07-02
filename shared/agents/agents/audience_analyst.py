from __future__ import annotations

from typing import Any

from ai_core import TokenUsage
from pydantic import BaseModel, Field, ValidationError

from .base import AgentExecutionError, BaseAgent


class AudienceMetricPoint(BaseModel):
    platform: str = Field(min_length=1)
    metric_name: str = Field(min_length=1)
    metric_value: float
    period: str = Field(min_length=1)


class RecentContentPerformanceItem(BaseModel):
    content_title: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    impressions: int = Field(ge=0)
    engagement_rate: float = Field(ge=0.0)
    watch_time_seconds: float | None = Field(default=None, ge=0.0)
    saves: int | None = Field(default=None, ge=0)


class AudienceAnalystInput(BaseModel):
    mock_analytics_data: list[AudienceMetricPoint] = Field(min_length=1)
    creator_niche: str = Field(min_length=1)
    recent_content_performance: list[RecentContentPerformanceItem] = Field(min_length=1)


class AudienceAnalystOutput(BaseModel):
    best_performing_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    best_posting_times: list[str] = Field(default_factory=list)
    engagement_insights: list[str] = Field(default_factory=list)
    growth_recommendations: list[str] = Field(default_factory=list)


class AudienceAnalystAgent(BaseAgent[AudienceAnalystInput, AudienceAnalystOutput]):
    name = "audience-analyst-agent"
    description = "Analyzes creator audience/content performance to produce growth insights."
    input_schema = AudienceAnalystInput
    output_schema = AudienceAnalystOutput

    def __init__(self, *, llm_provider, max_output_validation_retries: int = 2, logger=None, session_factory=None):
        super().__init__(llm_provider=llm_provider, logger=logger, session_factory=session_factory)
        self.max_output_validation_retries = max_output_validation_retries

    def _run_with_usage(self, input_data: AudienceAnalystInput) -> tuple[AudienceAnalystOutput, TokenUsage]:
        prompt = self._build_prompt(input_data)
        total_usage = TokenUsage()
        last_validation_error: ValidationError | None = None

        for _ in range(self.max_output_validation_retries + 1):
            json_result = self.llm_provider.generate_json(
                prompt=prompt,
                system_prompt=(
                    "You are CreatorOS Audience Analyst. Use analytics to produce concise, "
                    "practical creator recommendations. Return JSON only."
                ),
                temperature=0.2,
            )
            total_usage = self._add_usage(total_usage, json_result.usage)

            try:
                output = self.output_schema.model_validate(json_result.data)
                return output, total_usage
            except ValidationError as exc:
                last_validation_error = exc

        raise AgentExecutionError(
            "AudienceAnalystAgent failed to produce valid output after retries."
        ) from last_validation_error

    def _build_prompt(self, input_data: AudienceAnalystInput) -> str:
        analytics_dump: list[dict[str, Any]] = [
            metric.model_dump(mode="json") for metric in input_data.mock_analytics_data
        ]
        performance_dump: list[dict[str, Any]] = [
            item.model_dump(mode="json") for item in input_data.recent_content_performance
        ]
        return (
            "Analyze the creator's audience and content performance data.\n"
            f"Creator niche: {input_data.creator_niche}\n\n"
            "Mock analytics data:\n"
            f"{analytics_dump}\n\n"
            "Recent content performance:\n"
            f"{performance_dump}\n\n"
            "Return JSON with this exact shape:\n"
            "{\n"
            '  "best_performing_topics": ["string"],\n'
            '  "weak_topics": ["string"],\n'
            '  "best_posting_times": ["string"],\n'
            '  "engagement_insights": ["string"],\n'
            '  "growth_recommendations": ["string"]\n'
            "}\n"
            "Rules:\n"
            "- Use evidence from provided data\n"
            "- Keep insights and recommendations concrete and actionable\n"
            "- Include at least 3 growth recommendations"
        )

    @staticmethod
    def _add_usage(base: TokenUsage, extra: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=base.prompt_tokens + extra.prompt_tokens,
            completion_tokens=base.completion_tokens + extra.completion_tokens,
            total_tokens=base.total_tokens + extra.total_tokens,
        )
