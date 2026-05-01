from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database settings."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", case_sensitive=False)

    host: str = "localhost"
    port: int = 5432
    user: str = "user"
    password: SecretStr
    db: str = "second_brain"

    echo: bool = False

    @computed_field
    @property
    def sqlalchemy_uri_v2(self) -> str:
        """Return SQLAlchemy URI string representation."""
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"

    @computed_field
    @property
    def sqlalchemy_uri_v2_sync(self) -> str:
        """Return SQLAlchemy URI string representation."""
        return f"postgresql+psycopg2://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"


db_settings = DatabaseSettings()
