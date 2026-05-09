import logging

from dependencies.auth import RefreshTokenRepositoryDependency
from dependencies.repositories import FeedbackRepositoryDependency, UserRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, status
from models.feedback import Feedback, FeedbackCreate
from models.user import UserChangePassword, UserDetail, UserUpdate
from second_brain_service.services.auth import AuthService

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


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
def create_feedback(
    create_body: FeedbackCreate,
    current_user: CurrentUserDependency,
    feedback_repo: FeedbackRepositoryDependency,
) -> Feedback:
    """Create feedback for the current authenticated user."""
    feedback = feedback_repo.add(user_id=current_user.id, text=create_body.text)
    logger.info("Feedback created: id=%s user_id=%s", feedback.id, current_user.id)
    return Feedback(
        id=feedback.id,
        text=feedback.text,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
        user_id=feedback.user_id,
    )


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


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK,
    responses={401: {"description": "Unauthenticated or invalid current password"}},
)
def change_my_password(
    update_body: UserChangePassword,
    current_user: CurrentUserDependency,
    user_repo: UserRepositoryDependency,
    refresh_token_repo: RefreshTokenRepositoryDependency,
) -> UserDetail:
    """Update the current authenticated user's password."""
    if not AuthService.verify_password(update_body.current_password, current_user.password_hash):
        logger.warning("Change password failed: invalid current password: user_id=%s", current_user.id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid current password")

    password_hash = AuthService.hash_password(update_body.new_password)
    updated = user_repo.update_password(user_id=current_user.id, password_hash=password_hash)
    refresh_token_repo.revoke_all_for_user(current_user.id)
    logger.info("Changed password: user_id=%s", updated.id)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)
