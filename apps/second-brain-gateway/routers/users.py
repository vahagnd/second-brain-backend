import logging

from dependencies.repositories import UserRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, status
from models.user import UserDetail, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={401: {"description": "Unauthenticated"}},
)


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user(current_user: CurrentUserDependency) -> UserDetail:
    """Get the current authenticated user's details."""
    logger.info("Get current user: user_id=%s", current_user.id)
    return UserDetail(id=current_user.id, username=current_user.username, role=current_user.role)


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={409: {"description": "Username already taken"}},
)
def update_me(
    update_body: UserUpdate,
    current_user: CurrentUserDependency,
    user_repo: UserRepositoryDependency,
) -> UserDetail:
    if update_body.new_username is not None:
        taken = user_repo.get_one_or_none_by_username(update_body.new_username)
        if taken is not None:
            logger.warning(
                "Update me failed: username already taken: %s user_id=%s",
                update_body.new_username,
                current_user.id,
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    updated = user_repo.update(user_id=current_user.id, username=update_body.new_username)
    logger.info("Updated me: user_id=%s username=%s", updated.id, updated.username)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)
