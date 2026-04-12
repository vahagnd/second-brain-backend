from collections.abc import Callable

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from second_brain_db.settings import db_settings


engine = create_engine(db_settings.sqlalchemy_uri_v2, echo=db_settings.echo, pool_pre_ping=True)
session_maker = sessionmaker(engine, expire_on_commit=False)


def session_committed(method) -> Callable[..., Session]:
    """Wrapper for services providing session object."""

    def wrapper(*args, **kwargs) -> Session:
        with session_maker() as session:  # noqa: SIM117
            with session.begin():
                return method(*args, session=session, **kwargs)

    return wrapper
