from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import AuthenticatedUser, require_authenticated_user
from app.schemas.task import TaskEnqueueResponse
from app.schemas.trend import (
    LatestTrendsResponse,
    RunTrendResearchRequest,
    TrendReportResponse,
)
from app.services.trend_service import TrendService

router = APIRouter(prefix="/trends")


def get_trend_service() -> TrendService:
    return TrendService()


@router.get("/latest", response_model=LatestTrendsResponse)
def get_latest_trends(
    user: AuthenticatedUser = Depends(require_authenticated_user),
    limit: int = Query(default=10, ge=1, le=50),
    service: TrendService = Depends(get_trend_service),
) -> LatestTrendsResponse:
    return service.get_latest_trends(user_id=user.user_id, limit=limit)


@router.post("/run-research", response_model=TaskEnqueueResponse, status_code=status.HTTP_202_ACCEPTED)
def run_trend_research_manually(
    payload: RunTrendResearchRequest,
    service: TrendService = Depends(get_trend_service),
) -> TaskEnqueueResponse:
    return service.run_trend_research_manually(payload)


@router.get("/{trend_report_id}", response_model=TrendReportResponse)
def get_trend_report_by_id(
    trend_report_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    service: TrendService = Depends(get_trend_service),
) -> TrendReportResponse:
    try:
        return service.get_trend_report_by_id(
            trend_report_id=trend_report_id, user_id=user.user_id
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
