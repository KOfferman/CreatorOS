from pydantic import BaseModel


class ComponentStatus(BaseModel):
    status: str
    details: dict[str, str | int | float | bool | None] = {}


class SystemStatusResponse(BaseModel):
    status: str
    environment: str
    uptime_seconds: int
    request_id: str | None = None
    components: dict[str, ComponentStatus]
