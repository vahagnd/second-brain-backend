import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    content: str

    model_config = ConfigDict(extra="forbid")


class Note(BaseModel):
    id: int
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    user_id: int


class NoteWithScore(Note):
    score: float


class NoteListResponse(BaseModel):
    total: int
    search_type: Literal["like", "semantic"] | None = None
    page: int | None = None
    limit: int | None = None
    pages: int | None = None
    items: list[Note] | list[NoteWithScore]


class NoteListDuplicateResponse(BaseModel):
    message: str
    similar_notes: list[NoteWithScore]
