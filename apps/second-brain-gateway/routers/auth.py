import logging
from datetime import UTC, datetime, timedelta

from dependencies.auth import (
    CurrentUserPayloadDependency,
    RefreshTokenRepositoryDependency,
    RevokedAccessTokenRepositoryDependency,
)
from dependencies.repositories import UserRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, status
from models.auth import LoginRequest, RefreshRequest, SignupRequest, TokenResponse
from models.user import UserDetail
from second_brain_service.services.auth import AuthService
from settings import jwt_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Username already exists"}},
)
def signup(
    signup_body: SignupRequest,
    user_repo: UserRepositoryDependency,
) -> UserDetail:
    """Create a regular user account."""
    if user_repo.get_one_or_none_by_username(signup_body.username):
        logger.warning("Signup failed: username already exists: %s", signup_body.username)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    password_hash = AuthService.hash_password(signup_body.password)
    user = user_repo.add(signup_body.username, password_hash, "user")
    logger.info("Signup successful: user_id=%s username=%s", user.id, user.username)
    return UserDetail(id=user.id, username=user.username, role=user.role)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Invalid credentials"}},
)
def login(
    login_body: LoginRequest,
    user_repo: UserRepositoryDependency,
    refresh_token_repo: RefreshTokenRepositoryDependency,
) -> TokenResponse:
    """Authenticate a user and return access and refresh tokens."""
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    user = user_repo.get_one_or_none_by_username(login_body.username)
    if not user:
        logger.warning("Login failed: unknown username=%s", login_body.username)
        raise invalid
    if not AuthService.verify_password(login_body.password, user.password_hash):
        logger.warning("Login failed: wrong password for user_id=%s", user.id)
        raise invalid

    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role},
        secret_key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
        expires_delta=timedelta(minutes=jwt_settings.access_token_expire_minutes),
    )

    refresh_token = AuthService.create_refresh_token()
    refresh_token_repo.create(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(tz=UTC) + timedelta(days=jwt_settings.refresh_token_expire_days),
    )

    logger.info("Login successful: user_id=%s", user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")  # noqa: S106


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Invalid or expired refresh token"}},
)
def refresh(
    body: RefreshRequest,
    user_repo: UserRepositoryDependency,
    refresh_token_repo: RefreshTokenRepositoryDependency,
) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    token = refresh_token_repo.get_by_token(body.refresh_token)
    if token is None:
        logger.warning("Refresh failed: token not found")
        raise unauthorized
    if token.revoked:
        logger.warning("Refresh failed: token already revoked: user_id=%s", token.user_id)
        raise unauthorized
    if token.expires_at < datetime.now(tz=UTC):
        logger.warning("Refresh failed: token expired: user_id=%s", token.user_id)
        raise unauthorized

    user = user_repo.get_one_or_none(token.user_id)
    if user is None:
        logger.warning("Refresh failed: user not found: user_id=%s", token.user_id)
        raise unauthorized

    refresh_token_repo.revoke(body.refresh_token)

    new_refresh_token = AuthService.create_refresh_token()
    refresh_token_repo.create(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.now(tz=UTC) + timedelta(days=jwt_settings.refresh_token_expire_days),
    )

    new_access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role},
        secret_key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
        expires_delta=timedelta(minutes=jwt_settings.access_token_expire_minutes),
    )

    logger.info("Token refreshed: user_id=%s", user.id)
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")  # noqa: S106


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: CurrentUserDependency,
    payload: CurrentUserPayloadDependency,
    refresh_token_repo: RefreshTokenRepositoryDependency,
    revoked_access_token_repo: RevokedAccessTokenRepositoryDependency,
) -> dict:
    """Revoke all refresh tokens for the current user and blacklist the current access token."""
    refresh_token_repo.revoke_all_for_user(current_user.id)
    revoked_access_token_repo.add(
        jti=payload["jti"],
        user_id=current_user.id,
        expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
    )
    logger.info("Logout: user_id=%s", current_user.id)
    return {"message": "Logged out successfully"}
