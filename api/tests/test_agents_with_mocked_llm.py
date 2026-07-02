from __future__ import annotations

from collections import deque

from agents import (
    ContentWriterAgent,
    ContentWriterInput,
    GrowthCoachAgent,
    GrowthCoachInput,
)
from ai_core import JSONGenerationResult, TokenUsage
from database import User


class MockJSONProvider:
    provider_name = "mock-provider"
    model_name = "mock-model"

    def __init__(self, responses: list[dict]):
        self._responses = deque(responses)

    def generate_json(self, prompt: str, **kwargs):  # noqa: ANN003
        data = self._responses.popleft()
        return JSONGenerationResult(
            data=data,
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=TokenUsage(prompt_tokens=25, completion_tokens=10, total_tokens=35),
            raw_response={"mock": True},
        )

    def generate_text(self, prompt: str, **kwargs):  # noqa: ANN003
        raise NotImplementedError

    def stream_text(self, prompt: str, **kwargs):  # noqa: ANN003
        raise NotImplementedError


def _create_user(session_factory):
    with session_factory() as session:
        user = User(email="agent-test@example.com", full_name="Agent Test", is_active=True)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id


def test_growth_coach_agent_with_mocked_llm(sqlite_session_factory):
    user_id = _create_user(sqlite_session_factory)
    provider = MockJSONProvider(
        responses=[
            {
                "direct_coaching_response": "Focus on one pillar this week.",
                "recommended_next_actions": ["Post 3 short videos", "Review watch-time daily"],
                "content_ideas": ["Behind-the-scenes workflow", "Weekly creator recap"],
                "risk_warning": None,
            }
        ]
    )
    agent = GrowthCoachAgent(llm_provider=provider, session_factory=sqlite_session_factory)
    result = agent.run(
        user_id=user_id,
        payload=GrowthCoachInput(
            creator_profile={"handle": "coach"},
            recent_trends=[],
            audience_insights=[],
            user_question="How do I grow faster?",
        ),
    )
    assert result.output.direct_coaching_response.startswith("Focus")
    assert result.meta.usage.total_tokens == 35
    assert result.meta.agent_run_id is not None


def test_content_writer_agent_retries_invalid_then_succeeds(sqlite_session_factory):
    user_id = _create_user(sqlite_session_factory)
    provider = MockJSONProvider(
        responses=[
            {"bad": "shape"},
            {
                "hook": "This one shift doubled my saves.",
                "caption": "Try this process today.",
                "script": "Open with pain point, then teach one tactic.",
                "hashtags": ["#creator", "#growth"],
                "cta": "Comment 'template' and I will share it.",
                "suggested_format": "reel",
            },
        ]
    )
    agent = ContentWriterAgent(llm_provider=provider, session_factory=sqlite_session_factory)
    result = agent.run(
        user_id=user_id,
        payload=ContentWriterInput(
            topic="creator systems",
            platform="instagram",
            creator_voice="clear and practical",
            goal="increase saves",
            audience="new creators",
        ),
    )
    assert result.output.suggested_format == "reel"
    # Two attempts at 35 tokens each from mocked provider.
    assert result.meta.usage.total_tokens == 70
