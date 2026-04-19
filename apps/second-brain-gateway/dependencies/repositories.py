from typing import Annotated

from fastapi.params import Depends
from second_brain_db.repository.note import NoteRepository
from second_brain_db.repository.user import UserRepository

from dependencies.db import DBSessionDependency


def get_notes_repository(session: DBSessionDependency) -> NoteRepository:
    return NoteRepository(session)


def get_user_repository(session: DBSessionDependency) -> UserRepository:
    return UserRepository(session)


NoteRepositoryDependency = Annotated[
    NoteRepository,
    Depends(get_notes_repository),
]

UserRepositoryDependency = Annotated[
    UserRepository,
    Depends(get_user_repository),
]
