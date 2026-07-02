import logging
import time

from agents import GrowthCoachAgent, GrowthCoachInput
from ai_core import build_provider

from app.core.config import get_settings
from app.repositories.coach_repository import CoachRepository
from app.schemas.coach import CoachChatRequest, CoachChatResponse

logger = logging.getLogger(__name__)


class CoachService:
    def __init__(self, repository: CoachRepository | None = None) -> None:
        self.repository = repository or CoachRepository()
        self.settings = get_settings()

    def chat(self, payload: CoachChatRequest) -> CoachChatResponse:
        started_at = time.perf_counter()
        context = self.repository.get_context(user_id=payload.user_id)
        if context.user is None:
            raise LookupError("User not found.")

        provider = build_provider(
            provider_name=self.settings.llm_provider,
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
        )

        agent = GrowthCoachAgent(llm_provider=provider)
        execution = agent.run(
            user_id=payload.user_id,
            payload=GrowthCoachInput(
                creator_profile={
                    "handle": getattr(context.creator_profile, "handle", None),
                    "niche": getattr(context.creator_profile, "niche", None),
                    "bio": getattr(context.creator_profile, "bio", None),
                    "target_platforms": getattr(context.creator_profile, "target_platforms", []),
                    "creator_voice": getattr(context.creator_profile, "creator_voice", None),
                },
                recent_trends=[
                    {
                        "title": trend.title,
                        "summary": trend.summary,
                        "source": trend.source,
                        "report_date": str(trend.report_date) if trend.report_date else None,
                    }
                    for trend in context.recent_trends
                ],
                audience_insights=[
                    {
                        "insight_type": insight.insight_type,
                        "title": insight.title,
                        "details": insight.details,
                        "confidence_score": insight.confidence_score,
                    }
                    for insight in context.audience_insights
                ],
                user_question=payload.question,
            ),
        )
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "coach_chat_completed",
            extra={
                "user_id": payload.user_id,
                "agent_run_id": execution.meta.agent_run_id,
                "provider_name": execution.meta.provider_name,
                "model_name": execution.meta.model_name,
                "prompt_tokens": execution.meta.usage.prompt_tokens,
                "completion_tokens": execution.meta.usage.completion_tokens,
                "total_tokens": execution.meta.usage.total_tokens,
                "latency_ms": latency_ms,
            },
        )

        return CoachChatResponse(
            direct_coaching_response=execution.output.direct_coaching_response,
            recommended_next_actions=execution.output.recommended_next_actions,
            content_ideas=execution.output.content_ideas,
            risk_warning=execution.output.risk_warning,
            agent_run_id=execution.meta.agent_run_id,
        )
