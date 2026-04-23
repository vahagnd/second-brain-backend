from typing import Literal

from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class Note(BaseModel):
    id: int
    content: str


class NoteWithScore(Note):
    score: float


class NoteListResponse(BaseModel):
    total: int
    search_type: Literal["like", "semantic"] | None = None
    items: list[Note] | list[NoteWithScore]


class NoteListDuplicateResponse(BaseModel):
    message: str
    similar_notes: list[NoteWithScore]
