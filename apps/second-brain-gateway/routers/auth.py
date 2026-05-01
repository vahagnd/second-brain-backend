from datetime import UTC, datetime, timedelta

from dependencies.auth import (
    CurrentUserPayloadDependency,
    RefreshTokenRepositoryDependency,
    RevokedAccessTokenRepositoryDependency,
)
from dependencies.repositories import UserRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, status
from models.auth import LoginRequest, RefreshRequest, TokenResponse
from second_brain_service.services.auth import AuthService
from settings import jwt_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
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
        raise invalid
    if not AuthService.verify_password(login_body.password, user.password_hash):
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

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")  # noqa: S106


@router.post("/refresh", status_code=status.HTTP_200_OK)
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
        raise unauthorized
    if token.revoked:
        raise unauthorized
    if token.expires_at < datetime.now(tz=UTC):
        raise unauthorized

    user = user_repo.get_one_or_none(token.user_id)
    if user is None:
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
    return {"message": "Logged out successfully"}
