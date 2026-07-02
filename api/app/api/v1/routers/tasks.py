from fastapi import APIRouter, Depends, status

from app.schemas.task import SummarizeRequest, TaskEnqueueResponse
from app.services.task_service import TaskService

router = APIRouter()


def get_task_service() -> TaskService:
    return TaskService()


@router.post("/summarize", response_model=TaskEnqueueResponse, status_code=status.HTTP_202_ACCEPTED)
def enqueue_summary(
    payload: SummarizeRequest, task_service: TaskService = Depends(get_task_service)
) -> TaskEnqueueResponse:
    return task_service.enqueue_summary(payload)
