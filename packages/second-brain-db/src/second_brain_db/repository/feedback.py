from sqlalchemy import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import Feedback


class FeedbackRepository:
    def __init__(self, session: Session) -> None:
        """Initialize the FeedbackRepository with a SQLAlchemy session."""
        self.session = session

    def add(self, user_id: int, text: str) -> Feedback:
        """Add a new feedback item for a user."""
        feedback = Feedback(user_id=user_id, text=text)
        self.session.add(feedback)
        self.session.commit()
        self.session.refresh(feedback)
        return feedback

    def get_all(self) -> list[Feedback]:
        """Get all feedback items."""
        stmt = select(Feedback).order_by(Feedback.created_at.desc())
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get_one_or_none(self, feedback_id: int) -> Feedback | None:
        """Get a feedback item by ID, or return None if it doesn't exist."""
        stmt = select(Feedback).where(Feedback.id == feedback_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def delete(self, feedback_id: int) -> bool:
        """Delete a feedback item by ID. Returns True if deleted, False if it doesn't exist."""
        feedback = self.get_one_or_none(feedback_id)
        if not feedback:
            return False
        self.session.delete(feedback)
        self.session.commit()
        return True
