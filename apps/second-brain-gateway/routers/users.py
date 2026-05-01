from dependencies.repositories import UserRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, status
from models.user import UserDetail, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user(current_user: CurrentUserDependency) -> UserDetail:
    """Get the current authenticated user's details."""
    return UserDetail(id=current_user.id, username=current_user.username, role=current_user.role)


@router.patch("/me", status_code=status.HTTP_200_OK)
def update_me(
    update_body: UserUpdate,
    current_user: CurrentUserDependency,
    user_repo: UserRepositoryDependency,
) -> UserDetail:
    if update_body.new_username is not None:
        taken = user_repo.get_one_or_none_by_username(update_body.new_username)
        if taken is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    updated = user_repo.update(user_id=current_user.id, username=update_body.new_username)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)
