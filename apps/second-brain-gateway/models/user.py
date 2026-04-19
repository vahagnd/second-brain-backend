from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str


class UserCreatedResponse(UserCreate):
    id: int
    created: bool = True


class User(BaseModel):
    id: int
    username: str


class UserListResponse(BaseModel):
    total: int
    items: list[User]
