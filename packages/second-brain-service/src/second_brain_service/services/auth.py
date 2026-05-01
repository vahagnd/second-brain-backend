"""Auth service for handling user authentication and JWT token generation."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        return _pwd_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_refresh_token() -> str:
        """Generate a cryptographically secure opaque refresh token."""
        return secrets.token_urlsafe(64)

    @staticmethod
    def create_access_token(
        data: dict,
        secret_key: str,
        algorithm: str,
        expires_delta: timedelta,
    ) -> str:
        """Create a signed JWT access token with a unique jti claim."""
        payload = data.copy()
        payload["exp"] = datetime.now(tz=UTC) + expires_delta
        payload["jti"] = str(uuid4())
        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @staticmethod
    def decode_access_token(
        token: str,
        secret_key: str,
        algorithm: str,
    ) -> dict | None:
        """Decode and verify a JWT access token. Returns None if invalid."""
        try:
            return jwt.decode(token, secret_key, algorithms=[algorithm])
        except JWTError:
            return None
