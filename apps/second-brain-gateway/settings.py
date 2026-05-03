from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)

    api_prefix: str = "/api/v1"
    version: str = "v0.0.0"

    allow_origins: list[str] = ["http://localhost:4200"]

    @field_validator("allow_origins", mode="before")
    @classmethod
    def split_origins(cls, v):  # noqa: ANN001, ANN206
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v


class SimilaritySearchSettings(BaseSettings):
    """Settings for similarity search."""

    model_config = SettingsConfigDict(env_prefix="SIMILARITY_SEARCH_", case_sensitive=False)

    top_k: int = 5
    threshold: float = 0.95


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", case_sensitive=False)

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


class PaginationSettings(BaseSettings):
    """Settings for pagination."""

    model_config = SettingsConfigDict(env_prefix="PAGINATION_", case_sensitive=False)

    limit: int = 10


app_settings = AppSettings()
similarity_search_settings = SimilaritySearchSettings()
jwt_settings = JWTSettings()
pagination_settings = PaginationSettings()
