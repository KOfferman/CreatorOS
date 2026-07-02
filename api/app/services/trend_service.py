from celery import Celery
from database import TrendReport

from app.core.config import get_settings
from app.core.task_safety import safe_send_task
from app.models.task import TaskJob
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskEnqueueResponse
from app.schemas.trend import (
    LatestTrendsResponse,
    RunTrendResearchRequest,
    TrendReportResponse,
)
from app.repositories.trend_repository import TrendRepository


class TrendService:
    def __init__(self, repository: TrendRepository | None = None) -> None:
        self.settings = get_settings()
        self.repository = repository or TrendRepository()
        self.task_repository = TaskRepository()
        self.celery = Celery(
            "creatoros-api",
            broker=self.settings.celery_broker_url,
            backend=self.settings.celery_result_backend,
        )

    def get_latest_trends(self, *, user_id: str | None = None, limit: int = 10) -> LatestTrendsResponse:
        trends = self.repository.get_latest(user_id=user_id, limit=limit)
        return LatestTrendsResponse(trends=[self._to_response(trend) for trend in trends])

    def run_trend_research_manually(self, payload: RunTrendResearchRequest) -> TaskEnqueueResponse:
        async_task = safe_send_task(
            celery=self.celery,
            task_name="worker.tasks.run_daily_trend_research",
            kwargs={
                "creator_niche": payload.creator_niche,
                "target_platforms": payload.target_platforms,
                "audience_description": payload.audience_description,
            },
        )
        job = self.task_repository.save_enqueued(TaskJob(task_id=async_task.id))
        return TaskEnqueueResponse(task_id=job.task_id, status=job.status)

    def get_trend_report_by_id(self, *, trend_report_id: str) -> TrendReportResponse:
        trend = self.repository.get_by_id(trend_report_id=trend_report_id)
        if trend is None:
            raise LookupError("Trend report not found.")
        return self._to_response(trend)

    @staticmethod
    def _to_response(trend: TrendReport) -> TrendReportResponse:
        return TrendReportResponse(
            id=trend.id,
            user_id=trend.user_id,
            title=trend.title,
            summary=trend.summary,
            source=trend.source,
            report_date=trend.report_date,
        )
