from __future__ import annotations

from typing import Any

from celery import Celery
from celery.result import AsyncResult

ALLOWED_TASK_NAMES: set[str] = {
    "worker.tasks.summarize_text",
    "worker.tasks.run_daily_trend_research",
    "worker.tasks.generate_daily_briefing",
    "worker.tasks.analyze_audience_data",
    "worker.tasks.refresh_creator_score",
}


def _validate_payload(payload: dict[str, Any]) -> None:
    if len(payload) > 20:
        raise ValueError("Task payload has too many fields.")
    for key, value in payload.items():
        if len(key) > 120:
            raise ValueError(f"Task payload key '{key}' is too long.")
        if isinstance(value, str) and len(value) > 10000:
            raise ValueError(f"Task payload field '{key}' is too long.")


def safe_send_task(*, celery: Celery, task_name: str, kwargs: dict[str, Any]) -> AsyncResult:
    if task_name not in ALLOWED_TASK_NAMES:
        raise ValueError(f"Task '{task_name}' is not allowlisted for execution.")
    _validate_payload(kwargs)
    return celery.send_task(task_name, kwargs=kwargs)
