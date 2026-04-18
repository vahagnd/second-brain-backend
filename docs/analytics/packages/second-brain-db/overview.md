# `second-brain-db` — Package Overview

## Purpose

`second-brain-db` is an internal workspace package that encapsulates all database and embedding logic for the Second Brain project. It is consumed by `second-brain-gateway` and is designed to be reusable across multiple apps in the monorepo.

It provides:
- **SQLAlchemy ORM models** and engine setup
- **Alembic-compatible** database settings
- **NoteRepository** — data access layer for the `notes` table
- **EmbeddingService** — text-to-vector encoding using sentence-transformers
- **Vector utilities** — cosine similarity computation

---

## Package Location

```
packages/second-brain-db/
├── pyproject.toml
└── src/
    └── second_brain_db/
        ├── __init__.py
        ├── expections.py          # (placeholder, currently empty)
        ├── settings.py            # DatabaseSettings, EmbeddingSettings
        ├── db/
        │   ├── __init__.py
        │   ├── engine.py          # SQLAlchemy engine & session_maker
        │   └── models.py          # Note ORM model, Base class
        ├── repository/
        │   ├── __init__.py
        │   └── note.py            # NoteRepository
        ├── services/
        │   ├── __init__.py
        │   └── embedding.py       # EmbeddingService, get_embedding_model
        └── utils/
            ├── __init__.py
            └── vector.py          # cosine_similarity()
```

---

## Dependencies

Declared in `packages/second-brain-db/pyproject.toml`.

| Package | Version | Role |
|---|---|---|
| `sqlalchemy` | `>=2.0.49` | ORM and database engine |
| `psycopg2-binary` | `>=2.9.11` | Synchronous PostgreSQL driver |
| `alembic` | `>=1.18.4` | Database migration management |
| `pydantic-settings` | `>=2.13.1` | Environment-based configuration |
| `sentence-transformers` | `>=2.2.0` | Text embedding model loading and inference |
| `torch` | CPU build (pytorch-cpu index) | Required by sentence-transformers for model inference |
| `numpy` | `>=1.24.0` | Vector math (cosine similarity) |

### PyTorch CPU Build

`torch` is sourced from the dedicated PyTorch CPU wheel index to avoid pulling in CUDA dependencies:

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

This keeps the Docker image lean and suitable for CPU-only deployments.

---

## Public API Surface

| Module | Exports | Used by |
|---|---|---|
| `second_brain_db.db.engine` | `engine`, `session_maker`, `session_committed` | `dependencies/db.py` in gateway |
| `second_brain_db.db.models` | `Note`, `Base` | `NoteRepository`, Alembic migrations |
| `second_brain_db.repository.note` | `NoteRepository` | `dependencies/repositories.py` in gateway |
| `second_brain_db.services.embedding` | `EmbeddingService`, `get_embedding_model` | `dependencies/embedding.py` in gateway |
| `second_brain_db.utils.vector` | `cosine_similarity` | `NoteRepository.search_by_embedding` |
| `second_brain_db.settings` | `db_settings`, `embedding_settings` | `engine.py`, `embedding.py`, Alembic `env.py` |

---

## Design Principles

- **Separation of concerns** — database models, repository logic, embedding, and vector math are each in their own module.
- **No FastAPI dependency** — the package is framework-agnostic and could be used in CLI scripts, background workers, or other services.
- **Singleton model loading** — the embedding model is loaded once per process via `lru_cache` and reused across all requests.
- **Sync-first** — the engine uses a synchronous driver (`psycopg2`) matching the synchronous FastAPI route handlers. An async URI (`asyncpg`) is also computed but not currently used.
