import datetime

from pydantic import BaseModel, ConfigDict


class FeedbackCreate(BaseModel):
    text: str

    model_config = ConfigDict(extra="forbid")


class Feedback(BaseModel):
    id: int
    text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    total: int
    items: list[Feedback]
