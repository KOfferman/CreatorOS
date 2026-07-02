from __future__ import annotations

from typing import Literal

from ai_core import TokenUsage
from pydantic import BaseModel, Field, ValidationError

from .base import AgentExecutionError, BaseAgent

SupportedPlatform = Literal["instagram", "tiktok", "youtube_shorts", "linkedin", "blog_newsletter"]


class ContentWriterInput(BaseModel):
    topic: str = Field(min_length=1)
    platform: SupportedPlatform
    creator_voice: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    audience: str = Field(min_length=1)


class ContentWriterOutput(BaseModel):
    hook: str = Field(min_length=1)
    caption: str = Field(min_length=1)
    script: str = Field(min_length=1)
    hashtags: list[str] = Field(default_factory=list)
    cta: str = Field(min_length=1)
    suggested_format: str = Field(min_length=1)


class ContentWriterAgent(BaseAgent[ContentWriterInput, ContentWriterOutput]):
    name = "content-writer-agent"
    description = "Generates platform-tailored creator content for growth goals."
    input_schema = ContentWriterInput
    output_schema = ContentWriterOutput

    PLATFORM_STYLE_GUIDE: dict[SupportedPlatform, str] = {
        "instagram": (
            "Optimize for save/share behavior. Use concise hook, story-led caption, and strong CTA. "
            "Prioritize carousel or reel structures."
        ),
        "tiktok": (
            "Optimize for watch time in first 3 seconds. Script should be fast-paced and spoken. "
            "Use native, trend-aware phrasing."
        ),
        "youtube_shorts": (
            "Optimize for retention and replay value. Script should include tight scene beats and "
            "clear payoff by the end."
        ),
        "linkedin": (
            "Optimize for authority and comments. Keep a professional but human tone with practical insights."
        ),
        "blog_newsletter": (
            "Optimize for clarity and depth. Provide structured narrative with takeaways and scannable sections."
        ),
    }

    def __init__(self, *, llm_provider, max_output_validation_retries: int = 2, logger=None, session_factory=None):
        super().__init__(llm_provider=llm_provider, logger=logger, session_factory=session_factory)
        self.max_output_validation_retries = max_output_validation_retries

    def _run_with_usage(self, input_data: ContentWriterInput) -> tuple[ContentWriterOutput, TokenUsage]:
        prompt = self._build_prompt(input_data)
        total_usage = TokenUsage()
        last_validation_error: ValidationError | None = None

        for _ in range(self.max_output_validation_retries + 1):
            json_result = self.llm_provider.generate_json(
                prompt=prompt,
                system_prompt=(
                    "You are CreatorOS Content Writer. Produce practical, ready-to-publish content. "
                    "Return JSON only."
                ),
                temperature=0.6,
            )
            total_usage = self._add_usage(total_usage, json_result.usage)

            try:
                output = self.output_schema.model_validate(json_result.data)
                return output, total_usage
            except ValidationError as exc:
                last_validation_error = exc

        raise AgentExecutionError(
            "ContentWriterAgent failed to produce valid output after retries."
        ) from last_validation_error

    def _build_prompt(self, input_data: ContentWriterInput) -> str:
        platform_guide = self.PLATFORM_STYLE_GUIDE[input_data.platform]
        return (
            "Create platform-specific content with the requested voice and objective.\n"
            f"Topic: {input_data.topic}\n"
            f"Platform: {input_data.platform}\n"
            f"Creator voice: {input_data.creator_voice}\n"
            f"Goal: {input_data.goal}\n"
            f"Audience: {input_data.audience}\n"
            f"Platform style guide: {platform_guide}\n\n"
            "Return JSON with this exact shape:\n"
            "{\n"
            '  "hook": "string",\n'
            '  "caption": "string",\n'
            '  "script": "string",\n'
            '  "hashtags": ["string"],\n'
            '  "cta": "string",\n'
            '  "suggested_format": "string"\n'
            "}\n"
            "Rules:\n"
            "- hashtags should be relevant to the platform and topic\n"
            "- script should fit the platform format\n"
            "- suggested_format should be concrete (e.g., reel, talking-head, carousel, short, post, newsletter)"
        )

    @staticmethod
    def _add_usage(base: TokenUsage, extra: TokenUsage) -> TokenUsage:
        return TokenUsage(
            prompt_tokens=base.prompt_tokens + extra.prompt_tokens,
            completion_tokens=base.completion_tokens + extra.completion_tokens,
            total_tokens=base.total_tokens + extra.total_tokens,
        )
