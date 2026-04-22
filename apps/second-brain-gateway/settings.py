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


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", case_sensitive=False)

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


app_settings = AppSettings()
similarity_search_settings = SimilaritySearchSettings()
jwt_settings = JWTSettings()
