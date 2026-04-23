from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import sessionmaker

from second_brain_db.settings import db_settings

engine = create_engine(db_settings.sqlalchemy_uri_v2_sync, echo=db_settings.echo, pool_pre_ping=True)
session_maker = sessionmaker(engine, expire_on_commit=False)
