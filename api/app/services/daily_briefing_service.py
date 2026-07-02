from __future__ import annotations

from collections import Counter

from app.repositories.daily_briefing_repository import DailyBriefingContext, DailyBriefingRepository
from app.schemas.daily_briefing import DailyBriefingResponse


class DailyBriefingService:
    def __init__(self, repository: DailyBriefingRepository | None = None) -> None:
        self.repository = repository or DailyBriefingRepository()

    def generate(self, *, user_id: str) -> DailyBriefingResponse:
        context = self.repository.get_context(user_id=user_id)
        return DailyBriefingResponse(
            greeting=self._build_greeting(context),
            top_opportunity=self._build_top_opportunity(context),
            performance_insight=self._build_performance_insight(context),
            recommended_posts=self._build_recommended_posts(context),
            best_posting_time=self._build_best_posting_time(context),
            creator_score=self._build_creator_score(context),
        )

    def _build_greeting(self, context: DailyBriefingContext) -> str:
        if context.creator_profile and context.creator_profile.handle:
            return f"Good morning @{context.creator_profile.handle} - here is your daily briefing."
        if context.user and context.user.full_name:
            return f"Good morning {context.user.full_name} - here is your daily briefing."
        return "Good morning creator - here is your daily briefing."

    def _build_top_opportunity(self, context: DailyBriefingContext) -> str:
        trend_title = context.trend_reports[0].title if context.trend_reports else None
        idea_title = context.content_ideas[0].title if context.content_ideas else None
        if trend_title and idea_title:
            return f"Pair trend '{trend_title}' with content idea '{idea_title}' for a high-relevance post today."
        if trend_title:
            return f"Create a post on '{trend_title}' while audience interest is still rising."
        if idea_title:
            return f"Ship '{idea_title}' today to keep publishing consistency high."
        return "No fresh trend or idea signals found - prioritize one fast audience question post."

    def _build_performance_insight(self, context: DailyBriefingContext) -> str:
        if context.audience_insights:
            top_insight = context.audience_insights[0]
            confidence = top_insight.confidence_score
            if confidence is not None:
                return (
                    f"{top_insight.title} (confidence {confidence:.2f}) indicates your audience is "
                    "responding to focused educational content."
                )
            return f"{top_insight.title} is the strongest recent audience signal."
        if context.content_ideas:
            avg_score = sum(idea.score or 0 for idea in context.content_ideas) / len(context.content_ideas)
            return f"Recent content idea quality score is {avg_score:.1f}/100; refine hooks to improve conversion."
        return "Insufficient audience data today; publish one diagnostic post and review comments quality."

    def _build_recommended_posts(self, context: DailyBriefingContext) -> list[str]:
        recommendations: list[str] = []
        for idea in context.content_ideas[:3]:
            recommendations.append(f"{idea.title} ({idea.status})")
        if not recommendations and context.trend_reports:
            recommendations = [f"Trend explainers: {report.title}" for report in context.trend_reports[:3]]
        if not recommendations:
            recommendations = [
                "Quick niche myth-busting post",
                "Audience Q&A prompt post",
                "Behind-the-scenes process breakdown",
            ]
        return recommendations

    def _build_best_posting_time(self, context: DailyBriefingContext) -> str:
        hours = [
            item.scheduled_for.hour
            for item in context.calendar_items
            if item.scheduled_for is not None
        ]
        if not hours:
            return "12:00 local time (fallback until more schedule data is collected)"
        hour, _count = Counter(hours).most_common(1)[0]
        return f"{hour:02d}:00 local time"

    def _build_creator_score(self, context: DailyBriefingContext) -> int:
        trend_signal = min(len(context.trend_reports) * 5, 20)
        insights_signal = min(len(context.audience_insights) * 6, 24)
        idea_signal = min(len(context.content_ideas) * 4, 20)
        calendar_signal = min(len(context.calendar_items) * 3, 18)
        confidence_signal = 0
        if context.audience_insights:
            avg_confidence = sum(insight.confidence_score or 0 for insight in context.audience_insights) / len(
                context.audience_insights
            )
            confidence_signal = min(int(avg_confidence * 18), 18)

        score = 20 + trend_signal + insights_signal + idea_signal + calendar_signal + confidence_signal
        return max(0, min(100, score))
