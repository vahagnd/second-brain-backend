from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

    model_config = ConfigDict(extra="forbid")


class UserDetail(BaseModel):
    id: int
    username: str
    role: str


class UserListResponse(BaseModel):
    total: int
    items: list[UserDetail]


class UserUpdate(BaseModel):
    new_username: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str

    model_config = ConfigDict(extra="forbid")


class UserUpdatePassword(BaseModel):
    new_password: str

    model_config = ConfigDict(extra="forbid")
