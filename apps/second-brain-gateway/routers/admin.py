import logging

from dependencies.repositories import UserRepositoryDependency
from dependencies.user import AdminUserDependency
from fastapi import APIRouter, HTTPException, status
from models.user import UserCreate, UserDetail, UserListResponse, UserUpdate, UserUpdatePassword
from second_brain_service.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden - admin role required"},
    },
)


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Username already exists"}},
)
def create_user(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    create_body: UserCreate,
) -> UserDetail:
    """Create a new user in db."""
    password_hash = AuthService.hash_password(create_body.password)
    if user_repo.get_one_or_none_by_username(create_body.username):
        logger.warning("Create user failed: username already exists: %s", create_body.username)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = user_repo.add(create_body.username, password_hash, create_body.role)
    logger.info("User created: id=%s username=%s role=%s", user.id, user.username, user.role)
    return UserDetail(id=user.id, username=user.username, role=user.role)


@router.get("/users", status_code=status.HTTP_200_OK)
def list_users(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
) -> UserListResponse:
    """List all users."""
    users = user_repo.get_all()
    user_list = [UserDetail(id=user.id, username=user.username, role=user.role) for user in users]
    logger.info("Listed users: total=%s", len(user_list))
    return UserListResponse(total=len(user_list), items=user_list)


@router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "User not found"}},
)
def get_user(
    admin_user: AdminUserDependency,
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> UserDetail:
    """Get a user by ID."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        logger.warning("Get user failed: not found: id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info("Got user: id=%s", user_id)
    return UserDetail(id=user.id, username=user.username, role=user.role)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "User not found"}},
)
def delete_user(
    admin_user: AdminUserDependency,
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> None:
    """Delete a user by ID."""
    deleted = user_repo.delete(user_id)
    if not deleted:
        logger.warning("Delete user failed: not found: id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info("User deleted: id=%s", user_id)


@router.patch(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "User not found"},
        409: {"description": "Username already taken"},
    },
)
def update_user(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    user_id: int,
    update_body: UserUpdate,
) -> UserDetail:
    """Update a user's username."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        logger.warning("Update user failed: not found: id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if update_body.new_username is not None:
        taken = user_repo.get_one_or_none_by_username(update_body.new_username)
        if taken is not None:
            logger.warning("Update user failed: username already taken: %s", update_body.new_username)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    updated = user_repo.update(user_id=user_id, username=update_body.new_username)
    logger.info("User updated: id=%s username=%s", updated.id, updated.username)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)


@router.patch(
    "/users/{user_id}/password",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "User not found"}},
)
def update_user_password(
    admin_user: AdminUserDependency,
    user_repo: UserRepositoryDependency,
    user_id: int,
    update_body: UserUpdatePassword,
) -> UserDetail:
    """Update a user's password."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        logger.warning("Update password failed: not found: id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_hash = AuthService.hash_password(update_body.new_password)
    updated = user_repo.update_password(user_id=user_id, password_hash=password_hash)
    logger.info("Password updated: id=%s", updated.id)
    return UserDetail(id=updated.id, username=updated.username, role=updated.role)
