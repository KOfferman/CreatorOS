from dataclasses import dataclass


@dataclass(slots=True)
class TaskJob:
    task_id: str
    status: str = "queued"
