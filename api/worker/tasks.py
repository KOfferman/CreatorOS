from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from agents import (
    AudienceAnalystAgent,
    AudienceAnalystInput,
    ContentWriterAgent,
    ContentWriterInput,
    GrowthCoachAgent,
    GrowthCoachInput,
    TrendResearchAgent,
    TrendResearchInput,
)
from ai_core import TokenUsage, build_provider
from celery import Task
from database import AgentRun, User, get_session_factory
from pydantic_settings import BaseSettings, SettingsConfigDict

from worker_app import celery_app

logger = logging.getLogger(__name__)


class TaskSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    system_user_email: str = "system@creatoros.local"
    system_user_name: str = "CreatorOS System"


class BaseRetryTask(Task):
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_jitter = True
    retry_backoff_max = 60
    _task_started_at: dict[str, float] = {}

    def before_start(self, task_id, args, kwargs) -> None:
        self._task_started_at[task_id] = time.perf_counter()
        logger.info(
            "celery_task_started",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "args_size": len(args),
                "kwargs_keys": sorted(list(kwargs.keys())),
            },
        )
        super().before_start(task_id, args, kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo) -> None:
        started_at = self._task_started_at.pop(task_id, None)
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2) if started_at else None
        logger.info(
            "celery_task_finished",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "task_status": status,
                "latency_ms": elapsed_ms,
            },
        )
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo) -> None:
        logger.exception(
            "celery_task_failed",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "error": str(exc),
                "failed_job_tracked": True,
            },
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)


def _get_provider(settings: TaskSettings):
    return build_provider(
        provider_name=settings.llm_provider,
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_or_create_system_user_id(settings: TaskSettings) -> str:
    session_factory = get_session_factory()
    with session_factory() as session:
        user = session.query(User).filter(User.email == settings.system_user_email).one_or_none()
        if user is None:
            user = User(email=settings.system_user_email, full_name=settings.system_user_name, is_active=True)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user.id


def _create_agent_run(
    *,
    user_id: str,
    agent_name: str,
    input_payload: dict[str, Any],
) -> str:
    session_factory = get_session_factory()
    with session_factory() as session:
        run = AgentRun(
            user_id=user_id,
            agent_name=agent_name,
            status="running",
            input_payload=input_payload,
            started_at=_now(),
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return run.id


def _complete_agent_run(
    *,
    agent_run_id: str,
    output_payload: dict[str, Any],
) -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        run = session.get(AgentRun, agent_run_id)
        if run is None:
            return
        run.status = "completed"
        run.output_payload = output_payload
        run.finished_at = _now()
        latency_ms = None
        if run.started_at and run.finished_at:
            latency_ms = round((run.finished_at - run.started_at).total_seconds() * 1000, 2)
        session.add(run)
        session.commit()
        logger.info(
            "agent_run_completed",
            extra={
                "agent_run_id": agent_run_id,
                "agent_name": run.agent_name,
                "status": run.status,
                "latency_ms": latency_ms,
                "token_usage": output_payload.get("usage"),
                "cost": output_payload.get("cost"),
            },
        )


def _fail_agent_run(*, agent_run_id: str | None, error_message: str) -> None:
    if not agent_run_id:
        return
    session_factory = get_session_factory()
    with session_factory() as session:
        run = session.get(AgentRun, agent_run_id)
        if run is None:
            return
        run.status = "failed"
        run.error_message = error_message[:2000]
        run.finished_at = _now()
        latency_ms = None
        if run.started_at and run.finished_at:
            latency_ms = round((run.finished_at - run.started_at).total_seconds() * 1000, 2)
        session.add(run)
        session.commit()
        logger.error(
            "agent_run_failed",
            extra={
                "agent_run_id": agent_run_id,
                "agent_name": run.agent_name,
                "status": run.status,
                "error_message": run.error_message,
                "latency_ms": latency_ms,
                "failed_job_tracked": True,
            },
        )


def _usage_to_dict(usage: TokenUsage) -> dict[str, int]:
    return {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }


def _cost_to_dict(cost) -> dict[str, str]:
    if cost is None:
        return {"input_cost_usd": "0", "output_cost_usd": "0", "total_cost_usd": "0"}
    return {
        "input_cost_usd": str(getattr(cost, "input_cost_usd", Decimal("0"))),
        "output_cost_usd": str(getattr(cost, "output_cost_usd", Decimal("0"))),
        "total_cost_usd": str(getattr(cost, "total_cost_usd", Decimal("0"))),
    }


@celery_app.task(name="worker.tasks.summarize_text", base=BaseRetryTask)
def summarize_text(text: str) -> dict[str, str]:
    provider = _get_provider(TaskSettings())
    result = provider.generate_text(prompt=text, system_prompt="Summarize in plain language.")
    return {"summary": result.text}


@celery_app.task(name="worker.tasks.run_daily_trend_research", base=BaseRetryTask)
def run_daily_trend_research(
    creator_niche: str = "creator education",
    target_platforms: list[str] | None = None,
    audience_description: str = "early-stage creators seeking growth",
) -> dict[str, Any]:
    settings = TaskSettings()
    user_id = _get_or_create_system_user_id(settings)
    input_payload = {
        "creator_niche": creator_niche,
        "target_platforms": target_platforms or ["instagram", "tiktok", "youtube"],
        "audience_description": audience_description,
    }
    agent_run_id = _create_agent_run(user_id=user_id, agent_name="run_daily_trend_research", input_payload=input_payload)
    try:
        agent = TrendResearchAgent(llm_provider=_get_provider(settings))
        execution = agent.run(user_id=user_id, payload=TrendResearchInput(**input_payload))
        output_payload = {
            "result": execution.output.model_dump(mode="json"),
            "usage": _usage_to_dict(execution.meta.usage),
            "cost": _cost_to_dict(execution.meta.cost),
        }
        _complete_agent_run(agent_run_id=agent_run_id, output_payload=output_payload)
        return {"agent_run_id": agent_run_id, **output_payload}
    except Exception as exc:
        _fail_agent_run(agent_run_id=agent_run_id, error_message=str(exc))
        raise


@celery_app.task(name="worker.tasks.generate_daily_briefing", base=BaseRetryTask)
def generate_daily_briefing(
    creator_profile: dict[str, Any] | None = None,
    recent_trends: list[dict[str, Any]] | None = None,
    audience_insights: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    settings = TaskSettings()
    user_id = _get_or_create_system_user_id(settings)
    input_payload = {
        "creator_profile": creator_profile or {"niche": "creator education", "goal": "grow engaged audience"},
        "recent_trends": recent_trends or [],
        "audience_insights": audience_insights or [],
        "user_question": "What should I focus on today to maximize growth?",
    }
    agent_run_id = _create_agent_run(user_id=user_id, agent_name="generate_daily_briefing", input_payload=input_payload)
    try:
        agent = GrowthCoachAgent(llm_provider=_get_provider(settings))
        execution = agent.run(user_id=user_id, payload=GrowthCoachInput(**input_payload))
        output_payload = {
            "result": execution.output.model_dump(mode="json"),
            "usage": _usage_to_dict(execution.meta.usage),
            "cost": _cost_to_dict(execution.meta.cost),
        }
        _complete_agent_run(agent_run_id=agent_run_id, output_payload=output_payload)
        return {"agent_run_id": agent_run_id, **output_payload}
    except Exception as exc:
        _fail_agent_run(agent_run_id=agent_run_id, error_message=str(exc))
        raise


@celery_app.task(name="worker.tasks.analyze_audience_data", base=BaseRetryTask)
def analyze_audience_data(
    mock_analytics_data: list[dict[str, Any]],
    creator_niche: str,
    recent_content_performance: list[dict[str, Any]],
) -> dict[str, Any]:
    settings = TaskSettings()
    user_id = _get_or_create_system_user_id(settings)
    input_payload = {
        "mock_analytics_data": mock_analytics_data,
        "creator_niche": creator_niche,
        "recent_content_performance": recent_content_performance,
    }
    agent_run_id = _create_agent_run(user_id=user_id, agent_name="analyze_audience_data", input_payload=input_payload)
    try:
        agent = AudienceAnalystAgent(llm_provider=_get_provider(settings))
        execution = agent.run(user_id=user_id, payload=AudienceAnalystInput(**input_payload))
        output_payload = {
            "result": execution.output.model_dump(mode="json"),
            "usage": _usage_to_dict(execution.meta.usage),
            "cost": _cost_to_dict(execution.meta.cost),
        }
        _complete_agent_run(agent_run_id=agent_run_id, output_payload=output_payload)
        return {"agent_run_id": agent_run_id, **output_payload}
    except Exception as exc:
        _fail_agent_run(agent_run_id=agent_run_id, error_message=str(exc))
        raise


@celery_app.task(name="worker.tasks.refresh_creator_score", base=BaseRetryTask)
def refresh_creator_score(
    creator_profile: dict[str, Any] | None = None,
    recent_trends: list[dict[str, Any]] | None = None,
    audience_insights: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    settings = TaskSettings()
    user_id = _get_or_create_system_user_id(settings)
    input_payload = {
        "creator_profile": creator_profile or {"niche": "creator education", "goal": "drive consistency"},
        "recent_trends": recent_trends or [],
        "audience_insights": audience_insights or [],
        "topic": "daily creator score optimization",
    }
    agent_run_id = _create_agent_run(user_id=user_id, agent_name="refresh_creator_score", input_payload=input_payload)
    try:
        content_agent = ContentWriterAgent(llm_provider=_get_provider(settings))
        execution = content_agent.run(
            user_id=user_id,
            payload=ContentWriterInput(
                topic=input_payload["topic"],
                platform="linkedin",
                creator_voice="data-driven and practical",
                goal="increase authority and engagement",
                audience="creator economy founders",
            ),
        )
        score = min(
            100,
            50 + len(execution.output.hashtags) * 5 + min(execution.meta.usage.total_tokens // 10, 40),
        )
        output_payload = {
            "creator_score": score,
            "explanation": "Score refreshed from latest AI content signal proxy.",
            "content_signal": execution.output.model_dump(mode="json"),
            "usage": _usage_to_dict(execution.meta.usage),
            "cost": _cost_to_dict(execution.meta.cost),
        }
        _complete_agent_run(agent_run_id=agent_run_id, output_payload=output_payload)
        return {"agent_run_id": agent_run_id, **output_payload}
    except Exception as exc:
        _fail_agent_run(agent_run_id=agent_run_id, error_message=str(exc))
        raise
