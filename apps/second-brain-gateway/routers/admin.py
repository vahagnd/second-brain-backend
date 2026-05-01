from dependencies.auth import AdminUserDependency
from dependencies.repositories import UserRepositoryDependency
from fastapi import APIRouter, HTTPException, status
from models.user import UserCreate, UserDetail, UserListResponse, UserUpdate, UserUpdatePassword
from second_brain_service.services.auth import AuthService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    create_body: UserCreate,
) -> UserDetail:
    """Create a new user in db."""
    password_hash = AuthService.hash_password(create_body.password)
    if user_repo.get_one_or_none_by_username(create_body.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = user_repo.add(create_body.username, password_hash, create_body.role)
    return UserDetail(id=user.id, username=user.username, role=user.role)


@router.get("/users", status_code=status.HTTP_200_OK)
def list_users(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
) -> UserListResponse:
    """List all users."""
    users = user_repo.get_all()
    user_list = [UserDetail(id=user.id, username=user.username, role=user.role) for user in users]
    return UserListResponse(total=len(user_list), items=user_list)


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    admin_user: AdminUserDependency,
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> UserDetail:
    """Get a user by ID."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserDetail(id=user.id, username=user.username, role=user.role)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    admin_user: AdminUserDependency,
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> None:
    """Delete a user by ID."""
    deleted = user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.patch("/users/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    user_id: int,
    update_body: UserUpdate,
) -> UserDetail:
    """Update a user's username."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if update_body.new_username is not None:
        taken = user_repo.get_one_or_none_by_username(update_body.new_username)
        if taken is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    updated = user_repo.update(user_id=user_id, username=update_body.new_username)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)


@router.patch("/users/{user_id}/password", status_code=status.HTTP_200_OK)
def update_user_password(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    user_id: int,
    update_body: UserUpdatePassword,
) -> UserDetail:
    """Update a user's password."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_hash = AuthService.hash_password(update_body.new_password)
    updated = user_repo.update_password(user_id=user_id, password_hash=password_hash)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)
