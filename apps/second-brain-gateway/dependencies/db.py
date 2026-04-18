from collections.abc import Generator
from typing import Annotated

from fastapi.params import Depends
from second_brain_db.db.engine import session_maker
from sqlalchemy.orm import Session


def get_session() -> Generator[Session, None]:
    try:
        session = session_maker()
        yield session
    finally:
        session.close()


DBSessionDependency = Annotated[
    Session,
    Depends(get_session),
]
