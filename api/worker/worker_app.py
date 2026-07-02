from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_enable_beat: bool = False


settings = WorkerSettings()

celery_app = Celery(
    "creatoros-worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

if settings.celery_enable_beat:
    celery_app.conf.beat_schedule = {
        "run-daily-trend-research": {
            "task": "worker.tasks.run_daily_trend_research",
            "schedule": 60 * 60 * 24,
        },
        "generate-daily-briefing": {
            "task": "worker.tasks.generate_daily_briefing",
            "schedule": 60 * 60 * 24,
        },
    }
