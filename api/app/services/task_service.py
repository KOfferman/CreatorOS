from celery import Celery

from app.core.config import get_settings
from app.core.task_safety import safe_send_task
from app.models.task import TaskJob
from app.repositories.task_repository import TaskRepository
from app.schemas.task import SummarizeRequest, TaskEnqueueResponse


class TaskService:
    def __init__(self, repository: TaskRepository | None = None) -> None:
        self.settings = get_settings()
        self.repository = repository or TaskRepository()
        self.celery = Celery(
            "creatoros-api",
            broker=self.settings.celery_broker_url,
            backend=self.settings.celery_result_backend,
        )

    def enqueue_summary(self, payload: SummarizeRequest) -> TaskEnqueueResponse:
        async_task = safe_send_task(
            celery=self.celery,
            task_name="worker.tasks.summarize_text",
            kwargs={"text": payload.text},
        )
        job = self.repository.save_enqueued(TaskJob(task_id=async_task.id))
        return TaskEnqueueResponse(task_id=job.task_id, status=job.status)
