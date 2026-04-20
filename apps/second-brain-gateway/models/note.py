from typing import Literal

from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class NoteCreatedResponse(NoteCreate):
    id: int
    created: bool = True


class Note(BaseModel):
    id: int
    content: str


class NoteWithScore(Note):
    score: float


class NoteListResponse(BaseModel):
    total: int
    search_type: Literal["like", "semantic"] | None = None
    page: int | None = None
    limit: int | None = None
    pages: int | None = None
    items: list[Note] | list[NoteWithScore]
