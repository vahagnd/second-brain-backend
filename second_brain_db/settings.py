from pydantic import computed_field
from pydantic.v1 import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", case_sensitive=False)

    host: str = "postgres"
    port: int = 5432
    user: str
    password: SecretStr
    name: str = "second_brain"

    echo: bool = False

    @computed_field
    @property
    def sqlalchemy_uri_v2(self) -> str:
        """Return SQLAlchemy URI string representation."""
        uri = f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        return uri

    @computed_field
    @property
    def sqlalchemy_uri_v2_sync(self) -> str:
        """Return SQLAlchemy URI string representation."""
        uri = f"postgresql+psycopg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        return uri


db_settings = DatabaseSettings()
