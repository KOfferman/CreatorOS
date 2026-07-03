from database import ContentCalendarItem, get_session_factory


class CalendarRepository:
    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory or get_session_factory()

    def create_item(
        self,
        *,
        user_id: str,
        content_idea_id: str | None,
        platform: str | None,
        scheduled_for,
        status: str,
        notes: str | None,
    ) -> ContentCalendarItem:
        with self.session_factory() as session:
            item = ContentCalendarItem(
                user_id=user_id,
                content_idea_id=content_idea_id,
                platform=platform,
                scheduled_for=scheduled_for,
                status=status,
                notes=notes,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def list_items(self, *, user_id: str, limit: int = 100) -> list[ContentCalendarItem]:
        with self.session_factory() as session:
            return (
                session.query(ContentCalendarItem)
                .filter(ContentCalendarItem.user_id == user_id)
                .order_by(ContentCalendarItem.scheduled_for.asc(), ContentCalendarItem.created_at.desc())
                .limit(limit)
                .all()
            )

    def update_status(self, *, item_id: str, user_id: str, status: str) -> ContentCalendarItem | None:
        with self.session_factory() as session:
            item = (
                session.query(ContentCalendarItem)
                .filter(ContentCalendarItem.id == item_id, ContentCalendarItem.user_id == user_id)
                .one_or_none()
            )
            if item is None:
                return None
            item.status = status
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def move_item_date(self, *, item_id: str, user_id: str, scheduled_for) -> ContentCalendarItem | None:
        with self.session_factory() as session:
            item = (
                session.query(ContentCalendarItem)
                .filter(ContentCalendarItem.id == item_id, ContentCalendarItem.user_id == user_id)
                .one_or_none()
            )
            if item is None:
                return None
            item.scheduled_for = scheduled_for
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def delete_item(self, *, item_id: str, user_id: str) -> bool:
        with self.session_factory() as session:
            item = (
                session.query(ContentCalendarItem)
                .filter(ContentCalendarItem.id == item_id, ContentCalendarItem.user_id == user_id)
                .one_or_none()
            )
            if item is None:
                return False
            session.delete(item)
            session.commit()
            return True
