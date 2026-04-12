from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)

    host: str = "localhost"
    port: int = 5432
    user: str = "user"
    password: str = "password"
    name: str = "second_brain"

    echo: bool = False

    @computed_field
    @property
    def sqlalchemy_uri_v2(self) -> str:
        """Return SQLAlchemy URI string representation."""
        uri = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return uri

    @computed_field
    @property
    def sqlalchemy_uri_v2_sync(self) -> str:
        """Return SQLAlchemy URI string representation."""
        uri = f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        return uri


db_settings = DatabaseSettings()
