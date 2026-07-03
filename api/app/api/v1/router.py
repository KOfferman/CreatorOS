from fastapi import APIRouter, Depends

from app.api.v1.routers.admin import router as admin_router
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.calendar import router as calendar_router
from app.api.v1.routers.coach import router as coach_router
from app.api.v1.routers.content_ideas import router as content_ideas_router
from app.api.v1.routers.creators import router as creators_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.integrations import legacy_social_router, router as integrations_router
from app.api.v1.routers.tasks import router as tasks_router
from app.api.v1.routers.trends import router as trends_router
from app.core.dependencies import require_authenticated_user, require_admin_user

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(auth_router, tags=["auth"])
api_v1_router.include_router(
    tasks_router, prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(
    creators_router, tags=["creators"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(
    trends_router, tags=["trends"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(
    content_ideas_router, tags=["content-ideas"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(
    calendar_router, tags=["calendar"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(
    coach_router, tags=["coach"], dependencies=[Depends(require_authenticated_user)]
)
api_v1_router.include_router(integrations_router, tags=["integrations"])
api_v1_router.include_router(legacy_social_router, tags=["integrations"])
api_v1_router.include_router(
    admin_router, tags=["admin"], dependencies=[Depends(require_admin_user)]
)
