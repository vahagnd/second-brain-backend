"""Embedding service dependency."""

from typing import Annotated

from fastapi.params import Depends
from second_brain_service.services.embedding import EmbeddingService


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service instance."""
    return EmbeddingService()


EmbeddingServiceDependency = Annotated[
    EmbeddingService,
    Depends(get_embedding_service),
]
