from datetime import timedelta

from dependencies.auth import CurrentUserDependency
from dependencies.repositories import UserRepositoryDependency
from fastapi import APIRouter, HTTPException, status
from models.auth import LoginRequest, TokenResponse
from second_brain_service.services.auth import AuthService
from settings import jwt_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(login_body: LoginRequest, user_repo: UserRepositoryDependency) -> TokenResponse:
    """Authenticate a user and return their details."""
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

    return TokenResponse(access_token=access_token, token_type="bearer")  # noqa: S106


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: CurrentUserDependency) -> dict:
    """Logout a user. This is a no-op since we're using stateless JWTs, but it's here for completeness."""
    return {"message": "Logged out succesfully"}
