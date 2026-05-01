from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingSettings(BaseSettings):
    """Settings for embedding service."""

    model_config = SettingsConfigDict(env_prefix="EMBEDDING_", case_sensitive=False)

    model: str = "all-MiniLM-L6-v2"


embedding_settings = EmbeddingSettings()
