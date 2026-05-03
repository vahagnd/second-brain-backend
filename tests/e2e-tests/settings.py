from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """E2E test settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_prefix="TESTS_",
        case_sensitive=False,
        extra="ignore",
    )

    base_url: str = "http://localhost:8050/api/v1"
    admin_username: str
    admin_password: str
    user_username: str
    user_password: str
