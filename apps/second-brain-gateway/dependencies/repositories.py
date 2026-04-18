from typing import Annotated

from fastapi.params import Depends
from second_brain_db.repository.note import NoteRepository

from dependencies.db import DBSessionDependency


def get_notes_repository(session: DBSessionDependency) -> NoteRepository:
    return NoteRepository(session)


NoteRepositoryDependency = Annotated[
    NoteRepository,
    Depends(get_notes_repository),
]
