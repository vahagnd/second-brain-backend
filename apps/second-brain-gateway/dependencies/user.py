from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from second_brain_db.db.models import User
from second_brain_service.services import AuthService
from settings import jwt_settings

from dependencies.auth import CredentialsDependency, RevokedAccessTokenRepositoryDependency
from dependencies.repositories import UserRepositoryDependency


async def get_current_user(
    credentials: CredentialsDependency,
    user_repo: UserRepositoryDependency,
    revoked_access_token_repo: RevokedAccessTokenRepositoryDependency,
) -> User:
    token = credentials.credentials

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.decode_access_token(
        token,
        secret_key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
    )
    if payload is None:
        raise unauthorized

    if revoked_access_token_repo.is_revoked(payload.get("jti")):
        raise unauthorized

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as err:
        raise unauthorized from err

    user = user_repo.get_one_or_none(user_id)
    if user is None:
        raise unauthorized

    return user


CurrentUserDependency = Annotated[
    User,
    Depends(get_current_user),
]


async def get_current_admin_user(
    current_user: "CurrentUserDependency",
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    return current_user


AdminUserDependency = Annotated[
    User,
    Depends(get_current_admin_user),
]
