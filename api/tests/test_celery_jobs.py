from __future__ import annotations

from dataclasses import dataclass

import tasks as worker_tasks
from ai_core import TextGenerationResult, TokenUsage


class MockProvider:
    provider_name = "mock-provider"
    model_name = "mock-model"

    def generate_text(self, prompt: str, **kwargs):  # noqa: ANN003
        return TextGenerationResult(
            text=f"summary:{prompt[:20]}",
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            raw_response={"mock": True},
        )


@dataclass
class MockRunMeta:
    usage: TokenUsage
    cost: object


@dataclass
class MockExecution:
    output: object
    meta: MockRunMeta


class MockOutput:
    def model_dump(self, mode="json"):  # noqa: ARG002
        return {
            "trends": [
                {
                    "trending_topic": "mock trend",
                    "trend_score": 90,
                    "platform": "instagram",
                    "why_it_matters": "test",
                    "suggested_content_angle": "test angle",
                    "confidence_score": 0.8,
                }
            ]
        }


class MockAgent:
    def __init__(self, llm_provider):  # noqa: ANN001, ARG002
        pass

    def run(self, user_id: str, payload):  # noqa: ANN001, ARG002
        return MockExecution(
            output=MockOutput(),
            meta=MockRunMeta(
                usage=TokenUsage(prompt_tokens=12, completion_tokens=8, total_tokens=20),
                cost=None,
            ),
        )


def test_summarize_text_task(monkeypatch):
    monkeypatch.setattr(worker_tasks, "_get_provider", lambda settings: MockProvider())  # noqa: ARG005
    result = worker_tasks.summarize_text("hello world")
    assert "summary" in result
    assert result["summary"].startswith("summary:")


def test_run_daily_trend_research_task(monkeypatch):
    monkeypatch.setattr(worker_tasks, "_get_or_create_system_user_id", lambda settings: "user-1")  # noqa: ARG005
    monkeypatch.setattr(worker_tasks, "_create_agent_run", lambda **kwargs: "run-1")
    monkeypatch.setattr(worker_tasks, "_get_provider", lambda settings: object())  # noqa: ARG005
    monkeypatch.setattr(worker_tasks, "TrendResearchAgent", MockAgent)

    completed_payload = {}

    def _capture_complete(*, agent_run_id: str, output_payload: dict):
        completed_payload["agent_run_id"] = agent_run_id
        completed_payload["output_payload"] = output_payload

    monkeypatch.setattr(worker_tasks, "_complete_agent_run", _capture_complete)

    result = worker_tasks.run_daily_trend_research(
        creator_niche="education",
        target_platforms=["instagram"],
        audience_description="creators",
    )
    assert result["agent_run_id"] == "run-1"
    assert "usage" in result
    assert completed_payload["agent_run_id"] == "run-1"
