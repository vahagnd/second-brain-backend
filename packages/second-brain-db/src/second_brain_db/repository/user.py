from sqlalchemy import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import User


class UserRepository:
    def __init__(self, session: Session):
        """Initialize the UserRepository with a SQLAlchemy session."""
        self.session = session

    def add(self, username: str) -> User:
        """Add a new user with the given username."""
        user = User(username=username)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_all(self) -> list[User]:
        """Get all users."""
        stmt = select(User).order_by(User.created_at.desc())
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get_one_or_none(self, user_id: int) -> User | None:
        """Get a user by their ID, or return None if they don't exist."""
        stmt = select(User).where(User.id == user_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def get_one_or_none_by_username(self, username: str) -> User | None:
        """Get a user by their username, or return None if they don't exist."""
        stmt = select(User).where(User.username == username)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def delete(self, user_id: int) -> bool:
        """Delete a user by their ID. Returns True if the user was deleted, False if they didn't exist."""
        user = self.get_one_or_none(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True
