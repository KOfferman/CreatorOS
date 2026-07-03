from database import TrendReport, get_session_factory


class TrendRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def get_latest(self, *, user_id: str, limit: int = 10) -> list[TrendReport]:
        with self.session_factory() as session:
            return (
                session.query(TrendReport)
                .filter(TrendReport.user_id == user_id)
                .order_by(TrendReport.created_at.desc())
                .limit(limit)
                .all()
            )

    def get_by_id(self, *, trend_report_id: str, user_id: str) -> TrendReport | None:
        with self.session_factory() as session:
            return (
                session.query(TrendReport)
                .filter(TrendReport.id == trend_report_id, TrendReport.user_id == user_id)
                .one_or_none()
            )
