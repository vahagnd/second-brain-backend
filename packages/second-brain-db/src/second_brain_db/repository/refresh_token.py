from datetime import datetime

from sqlalchemy import delete, func, update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        """Initialize the RefreshTokenRepository with a SQLAlchemy session."""
        self.session = session

    def create(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Persist a new refresh token and return it."""
        obj = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_by_token(self, token: str) -> RefreshToken | None:
        """Look up a refresh token by its value."""
        return self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token),
        ).scalar_one_or_none()

    def revoke(self, token: str) -> bool:
        """Revoke a token. Returns True if it was found and revoked."""
        result = self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token, RefreshToken.revoked.is_(False))
            .values(revoked=True),
        )
        self.session.commit()
        return result.rowcount > 0

    def revoke_all_for_user(self, user_id: int) -> int:
        """Revoke all active tokens for a user. Returns number of revoked tokens."""
        result = self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True),
        )
        self.session.commit()
        return result.rowcount

    def delete_expired(self) -> int:
        """Delete all expired tokens. Returns number of deleted rows."""
        result = self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < func.now()),
        )
        self.session.commit()
        return result.rowcount
