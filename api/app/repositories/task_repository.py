import logging

from app.models.task import TaskJob

logger = logging.getLogger(__name__)


class TaskRepository:
    def save_enqueued(self, task: TaskJob) -> TaskJob:
        # Foundation layer: replace with SQL persistence in the next iteration.
        logger.info("task_enqueued", extra={"task_id": task.task_id, "status": task.status})
        return task
