from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    api_prefix: str = "/api/v1"

app_settings = AppSettings()
