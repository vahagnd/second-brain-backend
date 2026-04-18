from typing import Annotated

from fastapi.params import Depends

from sb_gateway.dependencies.db import DBSessionDependency
from second_brain_db.repository.note import NoteRepository


def get_notes_repository(session: DBSessionDependency) -> NoteRepository:
    return NoteRepository(session)


NoteRepositoryDependency = Annotated[
    NoteRepository,
    Depends(get_notes_repository),
]
