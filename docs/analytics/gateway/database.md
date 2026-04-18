# Gateway — Database

## Overview

The gateway uses **PostgreSQL 16** as its primary data store. The schema is managed by **Alembic** and the ORM layer is **SQLAlchemy 2.0** (synchronous, via `psycopg2`).

---

## `notes` Table Schema

```sql
CREATE TABLE notes (
    id         INTEGER       PRIMARY KEY,
    content    TEXT          NOT NULL,
    embedding  JSONB         NULL,
    created_at TIMESTAMPTZ   DEFAULT now(),
    updated_at TIMESTAMPTZ   DEFAULT now()
);
```

### Column Reference

| Column | SQL Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `INTEGER` | No | auto-increment (PK) | Unique identifier for the note |
| `content` | `TEXT` | No | — | The full text content of the note |
| `embedding` | `JSONB` | Yes | `NULL` | Serialised float vector produced by the embedding model. `NULL` for notes created before embeddings were introduced. |
| `created_at` | `TIMESTAMPTZ` | Yes | `now()` | Timestamp of note creation (set by the DB server) |
| `updated_at` | `TIMESTAMPTZ` | Yes | `now()` | Timestamp of last update; refreshed on every `UPDATE` via SQLAlchemy's `onupdate=func.now()` |

### Notes on `embedding`

- Stored as **JSONB** (a JSON array of floats), not a native vector type (e.g., `pgvector`).
- Cosine similarity is computed **in Python** (NumPy), not in SQL — all notes are fetched and scored in-memory.
- A note may have `embedding = NULL` if it was inserted before the embedding column was added (migration `c41bc437f0fd`). Such notes are silently excluded from semantic search results.

---

## SQLAlchemy ORM Model

Defined in `packages/second-brain-db/src/second_brain_db/db/models.py`.

```python
class Note(Base):
    __tablename__ = "notes"

    id:         Mapped[int]              = mapped_column(Integer, primary_key=True)
    content:    Mapped[str]              = mapped_column(Text, nullable=False)
    embedding:  Mapped[list[float]|None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime|None]    = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime|None]    = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

The `Base` class auto-generates `__tablename__` as `<ClassName>.lower() + "s"`, but `Note` overrides this explicitly with `__tablename__ = "notes"`.

---

## Database Engine

Defined in `packages/second-brain-db/src/second_brain_db/db/engine.py`.

```python
engine = create_engine(
    db_settings.sqlalchemy_uri_v2_sync,
    echo=db_settings.echo,
    pool_pre_ping=True,
)
session_maker = sessionmaker(engine, expire_on_commit=False)
```

| Option | Value | Effect |
|---|---|---|
| `echo` | `False` (default) | SQL statements are not logged; set `POSTGRES_ECHO=true` to enable |
| `pool_pre_ping` | `True` | Validates connections before use — prevents stale connection errors after DB restarts |
| `expire_on_commit` | `False` | ORM objects remain accessible after `commit()` without triggering a lazy reload |

---

## Migration History

Migrations are managed with **Alembic** and live in `migrations/versions/`.

| Revision | Date | Description |
|---|---|---|
| `e1bea6be2256` | 2026-04-12 | **Initial migration** — creates the `notes` table with `id`, `content`, `created_at`, `updated_at` |
| `c41bc437f0fd` | 2026-04-14 | **Add embedding column** — adds `embedding JSONB NULL` to the `notes` table |

### Migration Chain

```
(base)
  └── e1bea6be2256  (init notes table)
        └── c41bc437f0fd  (add embedding column)
                              ← HEAD
```

### Running Migrations

In Docker Compose, the `migrations` service runs automatically before the gateway starts:

```bash
alembic upgrade head
```

For local development:

```bash
uv run alembic upgrade head
```

To roll back one step:

```bash
uv run alembic downgrade -1
```

---

## Alembic Configuration (`alembic.ini`)

- Script location: `migrations/`
- The `env.py` connects to the database using the same `db_settings` from `second-brain-db`.
- Migration scripts are generated with `alembic revision --autogenerate`.
