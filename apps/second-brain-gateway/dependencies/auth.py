from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from second_brain_db.db.models import User
from second_brain_db.repository.user import UserRepository
from second_brain_db.services import AuthService
from settings import jwt_settings

from dependencies.db import DBSessionDependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

TokenDependency = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(
    token: TokenDependency,
    session: DBSessionDependency,
) -> User:
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

    user = await UserRepository(session).get_one_or_none(user_id)
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
