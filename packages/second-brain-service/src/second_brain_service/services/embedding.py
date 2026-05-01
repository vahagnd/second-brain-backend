"""Embedding service for generating text embeddings."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from second_brain_service.settings import embedding_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load and cache the embedding model.

    This function uses lru_cache to ensure the model is loaded only once
    per application lifetime.

    Returns
    -------
    SentenceTransformer
        The loaded sentence transformer model.
    """
    return SentenceTransformer(embedding_settings.model)


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""

    def __init__(self) -> None:
        """Initialize the EmbeddingService."""
        self.model = get_embedding_model()

    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Parameters
        ----------
        text : str
            The text to embed.

        Returns
        -------
        list[float]
            The embedding vector.
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Parameters
        ----------
        texts : list[str]
            List of texts to embed.

        Returns
        -------
        list[list[float]]
            List of embedding vectors.
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
