import time

from fastapi import APIRouter, Request
from sqlalchemy import func, text

from app.core.config import get_settings
from app.schemas.admin import ComponentStatus, SystemStatusResponse
from database import AgentRun, get_session_factory

router = APIRouter(prefix="/admin")
settings = get_settings()
service_started_at = time.time()


@router.get("/system-status", response_model=SystemStatusResponse)
def get_system_status(request: Request) -> SystemStatusResponse:
    session_factory = get_session_factory()

    db_status = ComponentStatus(status="ok", details={})
    agent_runs_status = ComponentStatus(status="ok", details={})
    try:
        with session_factory() as session:
            session.execute(text("SELECT 1"))

            failed_runs = session.query(func.count(AgentRun.id)).filter(AgentRun.status == "failed").scalar() or 0
            running_runs = session.query(func.count(AgentRun.id)).filter(AgentRun.status == "running").scalar() or 0
            completed_runs = (
                session.query(func.count(AgentRun.id)).filter(AgentRun.status == "completed").scalar() or 0
            )

            agent_runs_status = ComponentStatus(
                status="ok" if failed_runs == 0 else "degraded",
                details={
                    "failed_runs": int(failed_runs),
                    "running_runs": int(running_runs),
                    "completed_runs": int(completed_runs),
                },
            )
    except Exception as exc:
        db_status = ComponentStatus(status="error", details={"error": str(exc)})
        agent_runs_status = ComponentStatus(status="error", details={"error": "agent_runs_unavailable"})

    celery_status = ComponentStatus(
        status="ok",
        details={
            "broker_url_configured": bool(settings.celery_broker_url),
            "result_backend_configured": bool(settings.celery_result_backend),
        },
    )

    components = {
        "database": db_status,
        "agent_runs": agent_runs_status,
        "celery": celery_status,
    }
    overall_status = "ok"
    if any(component.status == "error" for component in components.values()):
        overall_status = "error"
    elif any(component.status == "degraded" for component in components.values()):
        overall_status = "degraded"

    return SystemStatusResponse(
        status=overall_status,
        environment=settings.environment,
        uptime_seconds=int(time.time() - service_started_at),
        request_id=getattr(request.state, "request_id", None),
        components=components,
    )
