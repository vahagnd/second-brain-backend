from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    api_prefix: str = "/api/v1"


class SimilaritySearchSettings(BaseSettings):
    """Settings for similarity search."""

    model_config = SettingsConfigDict(env_prefix="SIMILARITY_SEARCH_", case_sensitive=False)

    top_k: int = 5
    threshold: float = 0.95


class PaginationSettings(BaseSettings):
    """Settings for pagination."""

    model_config = SettingsConfigDict(env_prefix="PAGINATION_", case_sensitive=False)

    limit: int = 10


app_settings = AppSettings()
similarity_search_settings = SimilaritySearchSettings()
pagination_settings = PaginationSettings()
