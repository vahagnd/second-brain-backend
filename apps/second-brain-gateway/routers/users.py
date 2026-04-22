from dependencies.auth import CurrentUserDependency
from dependencies.repositories import UserRepositoryDependency
from fastapi import APIRouter, HTTPException, status
from models.user import UserDetail, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", status_code=status.HTTP_200_OK)
def read_current_user(current_user: CurrentUserDependency) -> dict:
    """Get the current authenticated user's details."""
    return UserDetail.model_validate(current_user)


@router.patch("/me", status_code=status.HTTP_200_OK)
def update_me(
    update_body: UserUpdate,
    current_user: CurrentUserDependency,
    user_repo: UserRepositoryDependency,
) -> UserDetail:

    if update_body.username is not None:
        taken = user_repo.get_one_or_none_by_username(update_body.username)
        if taken is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    updated = user_repo.update(user_id=current_user.id, username=update_body.username, role=current_user.role)
    return UserDetail.model_validate(updated)
