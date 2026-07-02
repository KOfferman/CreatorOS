from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Generic, TypeVar

from ai_core import AIProviderError, BaseLLMProvider, TokenUsage
from database import AgentRun, get_session_factory
from pydantic import BaseModel

InputSchemaT = TypeVar("InputSchemaT", bound=BaseModel)
OutputSchemaT = TypeVar("OutputSchemaT", bound=BaseModel)


class AgentExecutionError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AgentCost:
    input_cost_usd: Decimal
    output_cost_usd: Decimal
    total_cost_usd: Decimal


@dataclass(frozen=True, slots=True)
class AgentExecutionMeta:
    agent_run_id: str | None
    provider_name: str
    model_name: str
    usage: TokenUsage
    cost: AgentCost


@dataclass(frozen=True, slots=True)
class AgentExecutionResult(Generic[OutputSchemaT]):
    output: OutputSchemaT
    meta: AgentExecutionMeta


class BaseAgent(ABC, Generic[InputSchemaT, OutputSchemaT]):
    name: str = "base-agent"
    description: str = ""
    input_schema: type[InputSchemaT]
    output_schema: type[OutputSchemaT]

    _MODEL_PRICING_PER_1K_TOKENS: dict[str, tuple[Decimal, Decimal]] = {
        "gpt-4o-mini": (Decimal("0.00015"), Decimal("0.00060")),
    }

    def __init__(
        self,
        *,
        llm_provider: BaseLLMProvider,
        logger: logging.Logger | None = None,
        session_factory=None,
    ) -> None:
        if not hasattr(self, "input_schema") or not hasattr(self, "output_schema"):
            raise AgentExecutionError(
                f"{self.__class__.__name__} must define input_schema and output_schema."
            )
        self.llm_provider = llm_provider
        self.logger = logger or logging.getLogger(f"agents.{self.name}")
        self.session_factory = session_factory or get_session_factory()

    @abstractmethod
    def _run_with_usage(self, input_data: InputSchemaT) -> tuple[OutputSchemaT | dict[str, Any], TokenUsage]:
        raise NotImplementedError

    def run(
        self,
        *,
        user_id: str,
        payload: InputSchemaT | dict[str, Any],
    ) -> AgentExecutionResult[OutputSchemaT]:
        started_at = datetime.now(timezone.utc)
        run_record: AgentRun | None = None

        try:
            input_obj = self.input_schema.model_validate(payload)
            run_record = self._create_agent_run(
                user_id=user_id, input_obj=input_obj, started_at=started_at
            )
            self.logger.info(
                "agent_run_started",
                extra={
                    "agent_name": self.name,
                    "agent_run_id": run_record.id if run_record else None,
                    "provider_name": self.llm_provider.provider_name,
                    "model_name": self.llm_provider.model_name,
                },
            )
            raw_output, usage = self._run_with_usage(input_obj)
            output_obj = self.output_schema.model_validate(raw_output)
            cost = self._estimate_cost(usage=usage)
            finished_at = datetime.now(timezone.utc)
            latency_ms = round((finished_at - started_at).total_seconds() * 1000, 2)
            self._complete_agent_run(
                run_record=run_record,
                output_obj=output_obj,
                usage=usage,
                cost=cost,
                finished_at=finished_at,
            )
            self.logger.info(
                "agent_run_completed",
                extra={
                    "agent_name": self.name,
                    "agent_run_id": run_record.id if run_record else None,
                    "provider_name": self.llm_provider.provider_name,
                    "model_name": self.llm_provider.model_name,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "cost_usd": str(cost.total_cost_usd),
                    "latency_ms": latency_ms,
                },
            )
            return AgentExecutionResult(
                output=output_obj,
                meta=AgentExecutionMeta(
                    agent_run_id=run_record.id if run_record else None,
                    provider_name=self.llm_provider.provider_name,
                    model_name=self.llm_provider.model_name,
                    usage=usage,
                    cost=cost,
                ),
            )
        except AIProviderError:
            self._fail_agent_run(run_record=run_record, error="AI provider error")
            self.logger.exception(
                "agent_provider_error",
                extra={
                    "agent_name": self.name,
                    "agent_run_id": run_record.id if run_record else None,
                },
            )
            raise
        except Exception as exc:
            self._fail_agent_run(run_record=run_record, error=str(exc))
            self.logger.exception(
                "agent_run_failed",
                extra={
                    "agent_name": self.name,
                    "agent_run_id": run_record.id if run_record else None,
                },
            )
            raise AgentExecutionError(str(exc)) from exc

    def _estimate_cost(self, *, usage: TokenUsage) -> AgentCost:
        input_rate, output_rate = self._MODEL_PRICING_PER_1K_TOKENS.get(
            self.llm_provider.model_name,
            (Decimal("0"), Decimal("0")),
        )
        input_cost = (Decimal(usage.prompt_tokens) / Decimal(1000)) * input_rate
        output_cost = (Decimal(usage.completion_tokens) / Decimal(1000)) * output_rate
        total_cost = input_cost + output_cost
        return AgentCost(
            input_cost_usd=input_cost.quantize(Decimal("0.0000001")),
            output_cost_usd=output_cost.quantize(Decimal("0.0000001")),
            total_cost_usd=total_cost.quantize(Decimal("0.0000001")),
        )

    def _create_agent_run(
        self,
        *,
        user_id: str,
        input_obj: InputSchemaT,
        started_at: datetime,
    ) -> AgentRun:
        with self.session_factory() as session:
            run_record = AgentRun(
                user_id=user_id,
                agent_name=self.name,
                status="running",
                input_payload=input_obj.model_dump(mode="json"),
                started_at=started_at,
            )
            session.add(run_record)
            session.commit()
            session.refresh(run_record)
            return run_record

    def _complete_agent_run(
        self,
        *,
        run_record: AgentRun | None,
        output_obj: OutputSchemaT,
        usage: TokenUsage,
        cost: AgentCost,
        finished_at: datetime,
    ) -> None:
        if run_record is None:
            return
        with self.session_factory() as session:
            db_run = session.get(AgentRun, run_record.id)
            if db_run is None:
                return
            db_run.status = "completed"
            db_run.output_payload = {
                "result": output_obj.model_dump(mode="json"),
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "cost": {
                    "input_cost_usd": str(cost.input_cost_usd),
                    "output_cost_usd": str(cost.output_cost_usd),
                    "total_cost_usd": str(cost.total_cost_usd),
                },
            }
            db_run.finished_at = finished_at
            session.add(db_run)
            session.commit()

    def _fail_agent_run(self, *, run_record: AgentRun | None, error: str) -> None:
        if run_record is None:
            return
        with self.session_factory() as session:
            db_run = session.get(AgentRun, run_record.id)
            if db_run is None:
                return
            db_run.status = "failed"
            db_run.error_message = error[:2000]
            db_run.finished_at = datetime.now(timezone.utc)
            session.add(db_run)
            session.commit()
