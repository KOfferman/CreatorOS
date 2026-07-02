from database import TrendReport, get_session_factory


class TrendRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def get_latest(self, *, user_id: str | None = None, limit: int = 10) -> list[TrendReport]:
        with self.session_factory() as session:
            query = session.query(TrendReport)
            if user_id:
                query = query.filter(TrendReport.user_id == user_id)
            return query.order_by(TrendReport.created_at.desc()).limit(limit).all()

    def get_by_id(self, *, trend_report_id: str) -> TrendReport | None:
        with self.session_factory() as session:
            return session.get(TrendReport, trend_report_id)
