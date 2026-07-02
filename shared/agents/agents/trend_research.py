from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ai_core import TokenUsage
from pydantic import BaseModel, Field, ValidationError

from .base import AgentExecutionError, BaseAgent


class TrendResearchInput(BaseModel):
    creator_niche: str = Field(min_length=1)
    target_platforms: list[str] = Field(min_length=1)
    audience_description: str = Field(min_length=1)


class TrendSignal(BaseModel):
    topic: str
    platform: str
    signal_summary: str
    signal_strength: int = Field(ge=0, le=100)
    source: str


class TrendInsight(BaseModel):
    trending_topic: str = Field(min_length=1)
    trend_score: int = Field(ge=0, le=100)
    platform: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    suggested_content_angle: str = Field(min_length=1)
    confidence_score: float = Field(ge=0.0, le=1.0)


class TrendResearchOutput(BaseModel):
    trends: list[TrendInsight] = Field(default_factory=list)


class TrendDataSource(ABC):
    """Research source abstraction; swap mock with APIs/scrapers later."""

    @abstractmethod
    def fetch_signals(self, *, input_data: TrendResearchInput) -> list[TrendSignal]:
        raise NotImplementedError


class MockTrendDataSource(TrendDataSource):
    def fetch_signals(self, *, input_data: TrendResearchInput) -> list[TrendSignal]:
        niche = input_data.creator_niche.lower()
        platforms = {platform.lower() for platform in input_data.target_platforms}

        seed_signals = [
            TrendSignal(
                topic="Behind-the-scenes short tutorials",
                platform="tiktok",
                signal_summary="How-to micro-content with fast cuts is trending.",
                signal_strength=84,
                source="mock:tiktok-trending-feed",
            ),
            TrendSignal(
                topic="Carousel myth-busting posts",
                platform="instagram",
                signal_summary="Educational carousels with strong hooks are growing saves.",
                signal_strength=79,
                source="mock:instagram-explore",
            ),
            TrendSignal(
                topic="Long-form strategy breakdowns",
                platform="youtube",
                signal_summary="Deep tactical explainers show higher watch-time.",
                signal_strength=76,
                source="mock:youtube-discovery",
            ),
            TrendSignal(
                topic="Case-study threads with numbers",
                platform="x",
                signal_summary="Real metrics and post-mortems are driving reposts.",
                signal_strength=72,
                source="mock:x-topics",
            ),
        ]

        filtered = [signal for signal in seed_signals if signal.platform.lower() in platforms]
        if not filtered:
            filtered = seed_signals[:2]

        # Inject niche context for more relevant v1 mock signals.
        return [
            signal.model_copy(
                update={
                    "topic": f"{signal.topic} for {niche}",
                    "signal_summary": f"{signal.signal_summary} Niche context: {niche}.",
                }
            )
            for signal in filtered
        ]


class TrendResearchAgent(BaseAgent[TrendResearchInput, TrendResearchOutput]):
    name = "trend-research-agent"
    description = "Researches audience-relevant trends and suggests content angles."
    input_schema = TrendResearchInput
    output_schema = TrendResearchOutput

    def __init__(
        self,
        *,
        llm_provider,
        data_source: TrendDataSource | None = None,
        max_output_validation_retries: int = 2,
        logger=None,
        session_factory=None,
    ) -> None:
        super().__init__(llm_provider=llm_provider, logger=logger, session_factory=session_factory)
        self.data_source = data_source or MockTrendDataSource()
        self.max_output_validation_retries = max_output_validation_retries

    def _run_with_usage(self, input_data: TrendResearchInput) -> tuple[TrendResearchOutput, TokenUsage]:
        signals = self.data_source.fetch_signals(input_data=input_data)
        self.logger.info(
            "trend_signals_loaded",
            extra={"agent_name": self.name, "signal_count": len(signals)},
        )

        total_usage = TokenUsage()
        last_validation_error: ValidationError | None = None

        for _ in range(self.max_output_validation_retries + 1):
            json_result = self.llm_provider.generate_json(
                prompt=self._build_prompt(input_data=input_data, signals=signals),
                system_prompt=(
                    "You are a trend research analyst for creators. Return JSON only and do not "
                    "include markdown or explanations outside the JSON object."
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
            "TrendResearchAgent failed to produce valid output after retries."
        ) from last_validation_error

    def _build_prompt(self, *, input_data: TrendResearchInput, signals: list[TrendSignal]) -> str:
        return (
            "Analyze trend signals and produce actionable recommendations.\n"
            f"Creator niche: {input_data.creator_niche}\n"
            f"Target platforms: {', '.join(input_data.target_platforms)}\n"
            f"Audience description: {input_data.audience_description}\n\n"
            "Trend signals JSON:\n"
            f"{[signal.model_dump(mode='json') for signal in signals]}\n\n"
            "Return JSON with this exact shape:\n"
            "{\n"
            '  "trends": [\n'
            "    {\n"
            '      "trending_topic": "string",\n'
            '      "trend_score": 0,\n'
            '      "platform": "string",\n'
            '      "why_it_matters": "string",\n'
            '      "suggested_content_angle": "string",\n'
            '      "confidence_score": 0.0\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Constraints:\n"
            "- trend_score must be an integer 0-100\n"
            "- confidence_score must be a float 0.0-1.0\n"
            "- Use only requested target platforms\n"
            "- Include at least 3 trend entries when possible"
        )

    @staticmethod
    def _add_usage(base: TokenUsage, extra: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=base.prompt_tokens + extra.prompt_tokens,
            completion_tokens=base.completion_tokens + extra.completion_tokens,
            total_tokens=base.total_tokens + extra.total_tokens,
        )
