from dependencies.repositories import UserRepositoryDependency
from fastapi import APIRouter, status
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", status_code=status.HTTP_201_CREATED)
def get_current_user(user_repo: UserRepositoryDependency) -> User: ...
