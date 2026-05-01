from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from second_brain_db.repository.refresh_token import RefreshTokenRepository
from second_brain_db.repository.revoked_access_token import RevokedAccessTokenRepository
from second_brain_service.services import AuthService
from settings import jwt_settings

from dependencies.db import DBSessionDependency

http_bearer = HTTPBearer()

CredentialsDependency = Annotated[
    HTTPAuthorizationCredentials,
    Depends(http_bearer),
]


def get_refresh_token_repository(session: DBSessionDependency) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepositoryDependency = Annotated[
    RefreshTokenRepository,
    Depends(get_refresh_token_repository),
]


def get_revoked_access_token_repository(session: DBSessionDependency) -> RevokedAccessTokenRepository:
    return RevokedAccessTokenRepository(session)


RevokedAccessTokenRepositoryDependency = Annotated[
    RevokedAccessTokenRepository,
    Depends(get_revoked_access_token_repository),
]


async def get_current_user_payload(
    credentials: CredentialsDependency,
) -> dict:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = AuthService.decode_access_token(
        credentials.credentials,
        secret_key=jwt_settings.secret_key,
        algorithm=jwt_settings.algorithm,
    )
    if payload is None:
        raise unauthorized
    return payload


CurrentUserPayloadDependency = Annotated[
    dict,
    Depends(get_current_user_payload),
]
