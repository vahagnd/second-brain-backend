from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    content: str


class NoteCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    created: bool = True
