# `second-brain-db` — Embedding Service

## Overview

The embedding service converts plain text into dense float vectors (embeddings) using a pre-trained sentence-transformer model. These vectors are stored alongside notes and used for semantic similarity search and deduplication.

Defined in: `packages/second-brain-db/src/second_brain_db/services/embedding.py`

---

## Model

| Property | Value |
|---|---|
| Default model | `all-MiniLM-L6-v2` |
| Source | HuggingFace / sentence-transformers |
| Parameters | ~22 million |
| Embedding dimensions | 384 |
| Configurable via | `EMBEDDING_MODEL` env variable |

`all-MiniLM-L6-v2` is a lightweight, general-purpose model optimised for semantic similarity tasks. It offers a good balance between speed and quality for English text.

---

## Model Loading — `get_embedding_model()`

```python
@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(embedding_settings.model)
```

### Caching Strategy

The model is wrapped with `@lru_cache(maxsize=1)`, which means:

- The model is **loaded exactly once** per Python process, on the first call.
- Subsequent calls return the cached instance immediately — no disk I/O or model initialisation overhead.
- The cache is process-scoped, so each worker process (if using multi-worker Uvicorn) loads its own copy.

This is critical for performance: loading a sentence-transformer model takes several seconds and significant memory. Without caching, every request would incur this cost.

### Startup Behaviour

The model is **not** loaded at import time — it is loaded lazily on the first call to `EmbeddingService.embed()` or `EmbeddingService.embed_many()`. In practice this means the first request to `POST /notes` or `GET /notes?search=...` will be slower than subsequent ones.

---

## `EmbeddingService` Class

```python
class EmbeddingService:
    def __init__(self) -> None:
        self.model = get_embedding_model()

    def embed(self, text: str) -> list[float]: ...
    def embed_many(self, texts: list[str]) -> list[list[float]]: ...
```

A new `EmbeddingService` instance is created per request via FastAPI's dependency injection (`get_embedding_service()`), but since `get_embedding_model()` is cached, all instances share the same underlying model object.

---

## `embed(text)` — Single Text Encoding

```python
def embed(self, text: str) -> list[float]:
    embedding = self.model.encode(text, convert_to_tensor=False)
    return embedding.tolist()
```

| Parameter | Type | Description |
|---|---|---|
| `text` | `str` | The input text to encode |

**Returns:** `list[float]` — a 384-dimensional vector (for the default model).

- `convert_to_tensor=False` returns a NumPy array, which is then converted to a plain Python list via `.tolist()`.
- The list format is JSON-serialisable and stored directly in the `embedding` JSONB column.

**Used in:**
- `POST /notes` — to embed the note content before dedup check and storage
- `GET /notes?search=...&search_type=semantic` — to embed the search query

---

## `embed_many(texts)` — Batch Encoding

```python
def embed_many(self, texts: list[str]) -> list[list[float]]:
    embeddings = self.model.encode(texts, convert_to_tensor=False)
    return embeddings.tolist()
```

| Parameter | Type | Description |
|---|---|---|
| `texts` | `list[str]` | A list of input texts to encode in batch |

**Returns:** `list[list[float]]` — one embedding vector per input text.

Batch encoding is more efficient than calling `embed()` in a loop because the model can process multiple texts in a single forward pass.

**Currently used in:** scripts (`scripts/extract_notes_from_csv.py`, `scripts/extract_notes_from_txt.py`) for bulk note ingestion. Not called by any gateway endpoint at this time.

---

## Dependency Injection in the Gateway

```python
# dependencies/embedding.py

def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

EmbeddingServiceDependency = Annotated[
    EmbeddingService,
    Depends(get_embedding_service),
]
```

FastAPI injects `EmbeddingServiceDependency` into route handlers that need it (`create_note`, `list_notes`). The dependency is not cached at the FastAPI level — a new `EmbeddingService()` is instantiated per request — but this is cheap because the underlying model is cached via `lru_cache`.

---

## Performance Characteristics

| Operation | Typical latency (CPU) |
|---|---|
| First `embed()` call (model load) | 2–10 seconds |
| Subsequent `embed()` calls | 10–100 ms per text |
| `embed_many()` with N texts | Faster than N × `embed()` |

Latency depends on text length, hardware, and model. The CPU-only PyTorch build is used in production, so GPU acceleration is not available.

---

## Changing the Model

To use a different sentence-transformer model, set `EMBEDDING_MODEL` to any model name available on HuggingFace (e.g., `all-mpnet-base-v2`, `paraphrase-multilingual-MiniLM-L12-v2`).

> ⚠️ **Warning:** Changing the model after notes have been stored will cause **embedding incompatibility**. Existing embeddings were generated with the old model and will produce incorrect similarity scores when compared against new embeddings. All notes must be re-embedded after a model change.
