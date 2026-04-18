# Gateway — Overview

## Purpose

`second-brain-gateway` is the HTTP API layer of the Second Brain project. It exposes a REST API for managing notes, handles semantic deduplication on write, and supports both semantic and keyword-based search on read.

---

## Tech Stack

| Concern | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Data validation | Pydantic v2 |
| Settings management | pydantic-settings |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (sync, psycopg2) |
| Migrations | Alembic |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector math | NumPy |
| Package manager | uv (Astral) |
| Containerisation | Docker / Docker Compose |

---

## Repository Layout

```
apps/second-brain-gateway/
├── app.py                  # FastAPI application factory
├── run.py                  # Local dev entrypoint (uvicorn)
├── settings.py             # AppSettings, SimilaritySearchSettings
├── Dockerfile
├── pyproject.toml
├── routers/
│   ├── __init__.py         # init_routers() — registers all routers
│   ├── notes.py            # /notes CRUD + search endpoints
│   └── health.py           # /health liveness endpoint
├── models/
│   └── note.py             # Pydantic request/response schemas
└── dependencies/
    ├── __init__.py
    ├── db.py               # SQLAlchemy session dependency
    ├── embedding.py        # EmbeddingService dependency
    └── repositories.py     # NoteRepository dependency
```

The gateway depends on the internal `second-brain-db` workspace package for all database and embedding logic.

---

## Architecture Layers

```
HTTP Request
     │
     ▼
┌─────────────────────────────────┐
│         FastAPI Router          │  routers/notes.py, routers/health.py
│  (route matching, HTTP status)  │
└────────────────┬────────────────┘
                 │  FastAPI Dependency Injection
     ┌───────────┼───────────────┐
     ▼           ▼               ▼
┌─────────┐ ┌──────────┐ ┌────────────────┐
│  DB     │ │Embedding │ │  NoteRepository│
│ Session │ │ Service  │ │  (second-brain │
│  dep    │ │   dep    │ │     -db pkg)   │
└────┬────┘ └────┬─────┘ └───────┬────────┘
     │           │               │
     ▼           ▼               ▼
┌─────────────────────────────────────────┐
│          second-brain-db package        │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │NoteRepository│  │ EmbeddingService│  │
│  └──────┬───────┘  └────────┬────────┘  │
│         │                   │           │
│  ┌──────▼───────┐  ┌────────▼────────┐  │
│  │  SQLAlchemy  │  │sentence-transf. │  │
│  │   ORM/Engine │  │ (all-MiniLM-L6) │  │
│  └──────┬───────┘  └─────────────────┘  │
└─────────┼───────────────────────────────┘
          │
          ▼
    PostgreSQL 16
```

---

## Application Bootstrap

1. `app.py` creates a `FastAPI` instance with `root_path` set to `app_settings.api_prefix` (default `/api/v1`).
2. `init_routers()` registers the `notes` router first (higher route priority), then the `health` router.
3. In production the container runs `uvicorn app:app --host 0.0.0.0 --port 8000`.
4. In Docker Compose, a separate `migrations` service runs `alembic upgrade head` before the gateway starts.

---

## Deployment (Docker Compose)

Three services are defined:

| Service | Image | Role |
|---|---|---|
| `postgres` | `postgres:16` | Primary database |
| `migrations` | `second-brain-gateway:latest` | Runs `alembic upgrade head` once on startup |
| `gateway` | `second-brain-gateway:latest` | Serves the API on port `8000` |

Start order: `postgres` (healthy) → `migrations` (completed) → `gateway`.

The gateway image is built from `apps/second-brain-gateway/Dockerfile` using a multi-stage uv-based build that installs only the `second-brain-gateway` workspace package and its transitive dependencies.
