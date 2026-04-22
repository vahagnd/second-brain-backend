from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserDetail(BaseModel):
    id: int
    username: str
    role: str


class UserListResponse(BaseModel):
    total: int
    items: list[UserDetail]


class UserUpdate(BaseModel):
    username: str | None = None


class UserUpdatePassword(BaseModel):
    new_password: str
