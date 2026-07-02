from __future__ import annotations

from dataclasses import dataclass

from database import (
    AudienceInsight,
    ContentCalendarItem,
    ContentIdea,
    CreatorProfile,
    TrendReport,
    User,
    get_session_factory,
)


@dataclass(frozen=True, slots=True)
class DailyBriefingContext:
    user: User | None
    creator_profile: CreatorProfile | None
    trend_reports: list[TrendReport]
    audience_insights: list[AudienceInsight]
    calendar_items: list[ContentCalendarItem]
    content_ideas: list[ContentIdea]


class DailyBriefingRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def get_context(self, *, user_id: str) -> DailyBriefingContext:
        with self.session_factory() as session:
            user = session.get(User, user_id)
            creator_profile = (
                session.query(CreatorProfile)
                .filter(CreatorProfile.user_id == user_id)
                .order_by(CreatorProfile.updated_at.desc())
                .first()
            )
            trend_reports = (
                session.query(TrendReport)
                .filter(TrendReport.user_id == user_id)
                .order_by(TrendReport.created_at.desc())
                .limit(5)
                .all()
            )
            audience_insights = (
                session.query(AudienceInsight)
                .filter(AudienceInsight.user_id == user_id)
                .order_by(AudienceInsight.created_at.desc())
                .limit(5)
                .all()
            )
            calendar_items = (
                session.query(ContentCalendarItem)
                .filter(ContentCalendarItem.user_id == user_id)
                .order_by(ContentCalendarItem.scheduled_for.asc())
                .limit(10)
                .all()
            )
            content_ideas = (
                session.query(ContentIdea)
                .filter(ContentIdea.user_id == user_id)
                .order_by(ContentIdea.score.desc(), ContentIdea.created_at.desc())
                .limit(10)
                .all()
            )
        return DailyBriefingContext(
            user=user,
            creator_profile=creator_profile,
            trend_reports=trend_reports,
            audience_insights=audience_insights,
            calendar_items=calendar_items,
            content_ideas=content_ideas,
        )
