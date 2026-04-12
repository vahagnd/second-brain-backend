from typing import Annotated, Generator

from fastapi.params import Depends
from sqlalchemy.orm import Session
from second_brain_db.db.engine import session_maker


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
