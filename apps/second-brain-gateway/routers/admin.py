from dependencies.repositories import UserRepositoryDependency
from fastapi import APIRouter, HTTPException, status
from models.user import User, UserCreatedResponse, UserListResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(username: str, user_repo: UserRepositoryDependency) -> UserCreatedResponse:
    """Create a new user in db."""
    if user_repo.get_one_or_none_by_username(username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    user = user_repo.add(username)
    return UserCreatedResponse(id=user.id, username=user.username, created=True)


@router.get("/users", status_code=status.HTTP_200_OK)
def list_users(
    user_repo: UserRepositoryDependency,
) -> UserListResponse:
    """List all users."""
    users = user_repo.get_all()
    user_list = [User(id=user.id, username=user.username) for user in users]
    return UserListResponse(total=len(user_list), items=user_list)


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> User:
    """Get a user by ID."""
    user = user_repo.get_one_or_none(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(id=user.id, username=user.username)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_repo: UserRepositoryDependency,
) -> None:
    """Delete a user by ID."""
    deleted = user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
