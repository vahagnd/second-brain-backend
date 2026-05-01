from datetime import datetime

from sqlalchemy import delete, func
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import RevokedAccessToken


class RevokedAccessTokenRepository:
    def __init__(self, session: Session) -> None:
        """Initialize the RevokedAccessTokenRepository with a SQLAlchemy session."""
        self.session = session

    def add(self, jti: str, user_id: int, expires_at: datetime) -> RevokedAccessToken:
        """Blacklist an access token and return it."""
        obj = RevokedAccessToken(jti=jti, user_id=user_id, expires_at=expires_at)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def is_revoked(self, jti: str) -> bool:
        """Return True if the given jti is blacklisted."""
        result = self.session.execute(
            select(RevokedAccessToken.id).where(RevokedAccessToken.jti == jti),
        )
        return result.scalar_one_or_none() is not None

    def delete_expired(self) -> int:
        """Delete all expired revoked tokens. Returns number of deleted rows."""
        result = self.session.execute(
            delete(RevokedAccessToken).where(RevokedAccessToken.expires_at < func.now()),
        )
        self.session.commit()
        return result.rowcount
