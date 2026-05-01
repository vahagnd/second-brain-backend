from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from second_brain_db.db.models import User
from second_brain_service.services import AuthService
from settings import jwt_settings

from dependencies.repositories import UserRepositoryDependency

http_bearer = HTTPBearer()

CredentialsDependency = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]


async def get_current_user(
    credentials: CredentialsDependency,
    user_repo: UserRepositoryDependency,
) -> User:
    token = credentials.credentials

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.decode_access_token(
        token,
        secret_key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
    )
    if payload is None:
        raise unauthorized

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as err:
        raise unauthorized from err

    user = user_repo.get_one_or_none(user_id)
    if user is None:
        raise unauthorized

    return user


async def get_current_admin_user(
    current_user: "CurrentUserDependency",
) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
AdminUserDependency = Annotated[User, Depends(get_current_admin_user)]
