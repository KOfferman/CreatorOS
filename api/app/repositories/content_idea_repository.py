from database import ContentIdea, get_session_factory


class ContentIdeaRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def list_by_user(self, *, user_id: str, limit: int = 50) -> list[ContentIdea]:
        with self.session_factory() as session:
            return (
                session.query(ContentIdea)
                .filter(ContentIdea.user_id == user_id)
                .order_by(ContentIdea.created_at.desc())
                .limit(limit)
                .all()
            )

    def create(
        self,
        *,
        user_id: str,
        title: str,
        description: str | None,
        status: str,
        trend_report_id: str | None,
        score: float | None,
    ) -> ContentIdea:
        with self.session_factory() as session:
            idea = ContentIdea(
                user_id=user_id,
                title=title,
                description=description,
                status=status,
                trend_report_id=trend_report_id,
                score=score,
            )
            session.add(idea)
            session.commit()
            session.refresh(idea)
            return idea

    def get_by_id(self, *, idea_id: str, user_id: str) -> ContentIdea | None:
        with self.session_factory() as session:
            return (
                session.query(ContentIdea)
                .filter(ContentIdea.id == idea_id, ContentIdea.user_id == user_id)
                .one_or_none()
            )

    def update_status(self, *, idea_id: str, user_id: str, status: str) -> ContentIdea | None:
        with self.session_factory() as session:
            idea = (
                session.query(ContentIdea)
                .filter(ContentIdea.id == idea_id, ContentIdea.user_id == user_id)
                .one_or_none()
            )
            if idea is None:
                return None
            idea.status = status
            session.add(idea)
            session.commit()
            session.refresh(idea)
            return idea

    def delete(self, *, idea_id: str, user_id: str) -> bool:
        with self.session_factory() as session:
            idea = (
                session.query(ContentIdea)
                .filter(ContentIdea.id == idea_id, ContentIdea.user_id == user_id)
                .one_or_none()
            )
            if idea is None:
                return False
            session.delete(idea)
            session.commit()
            return True
