from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class NoteCreatedResponse(NoteCreate):
    id: int
    created: bool = True


class Note(BaseModel):
    id: int
    content: str
    created_at: str
