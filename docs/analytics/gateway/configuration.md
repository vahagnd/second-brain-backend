# Gateway — Configuration

All configuration is managed via environment variables and loaded at startup using **pydantic-settings**. Settings are grouped into three classes, each with its own env prefix.

---

## Settings Classes

### `AppSettings` — prefix: `APP_`

Defined in `apps/second-brain-gateway/settings.py`.

| Env Variable | Python Field | Type | Default | Description |
|---|---|---|---|---|
| `APP_API_PREFIX` | `api_prefix` | `str` | `/api/v1` | Root path prefix for all API routes |

---

### `SimilaritySearchSettings` — prefix: `SIMILARITY_SEARCH_`

Defined in `apps/second-brain-gateway/settings.py`.

| Env Variable | Python Field | Type | Default | Description |
|---|---|---|---|---|
| `SIMILARITY_SEARCH_TOP_K` | `top_k` | `int` | `5` | Max number of results returned by semantic search and used during deduplication check |
| `SIMILARITY_SEARCH_THRESHOLD` | `threshold` | `float` | `0.95` | Minimum cosine similarity score to consider a note a duplicate. **Only used during `POST /notes` deduplication — not during search.** |

---

### `DatabaseSettings` — prefix: `POSTGRES_`

Defined in `packages/second-brain-db/src/second_brain_db/settings.py`.

| Env Variable | Python Field | Type | Default | Description |
|---|---|---|---|---|
| `POSTGRES_HOST` | `host` | `str` | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | `port` | `int` | `5432` | PostgreSQL server port |
| `POSTGRES_USER` | `user` | `str` | `user` | Database username |
| `POSTGRES_PASSWORD` | `password` | `SecretStr` | *(required)* | Database password — treated as a secret, never logged |
| `POSTGRES_DB` | `db` | `str` | `second_brain` | Database name |

Two computed connection strings are derived from these fields:

| Property | Driver | Format |
|---|---|---|
| `sqlalchemy_uri_v2` | `asyncpg` (async) | `postgresql+asyncpg://user:pass@host:port/db` |
| `sqlalchemy_uri_v2_sync` | `psycopg2` (sync) | `postgresql+psycopg2://user:pass@host:port/db` |

The gateway uses the **sync** URI (`sqlalchemy_uri_v2_sync`) via `psycopg2`.

---

### `PaginationSettings` — prefix: `PAGINATION_`

Defined in `apps/second-brain-gateway/settings.py`.

| Env Variable | Python Field | Type | Default | Description |
|---|---|---|---|---|
| `PAGINATION_LIMIT` | `limit` | `int` | `10` | Default number of items per page returned by `GET /notes` |

---

### `EmbeddingSettings` — prefix: `EMBEDDING_`

Defined in `packages/second-brain-db/src/second_brain_db/settings.py`.

| Env Variable | Python Field | Type | Default | Description |
|---|---|---|---|---|
| `EMBEDDING_MODEL` | `model` | `str` | `all-MiniLM-L6-v2` | HuggingFace sentence-transformer model name used for generating embeddings |

---

## Full `.env` Reference

```dotenv
# ── Database ──────────────────────────────────────────────
POSTGRES_HOST=postgres          # hostname of the DB container
POSTGRES_PORT=5432
POSTGRES_DB=second_brain
POSTGRES_USER=                  # required — no default
POSTGRES_PASSWORD=              # required — no default

# ── Embeddings ────────────────────────────────────────────
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ── Similarity Search ─────────────────────────────────────
SIMILARITY_SEARCH_TOP_K=5       # used in both search and dedup
SIMILARITY_SEARCH_THRESHOLD=0.95  # used ONLY in dedup (POST /notes)

# ── Pagination ────────────────────────────────────────────
PAGINATION_LIMIT=10             # default page size for GET /notes

# ── Gateway ───────────────────────────────────────────────
APP_API_PREFIX=/api/v1
```

---

## Notes on Specific Settings

### `SIMILARITY_SEARCH_THRESHOLD`

This value controls the **deduplication gate** on `POST /notes`. A value of `0.95` means only notes that are 95%+ semantically similar will be blocked. Lowering this value makes deduplication more aggressive (more notes rejected); raising it makes it more permissive.

This threshold is **not** applied during `GET /notes?search_type=semantic` — search always returns the top `top_k` results regardless of their similarity score.

### `EMBEDDING_MODEL`

The model is downloaded from HuggingFace on first use and cached locally. The default `all-MiniLM-L6-v2` is a lightweight, fast model (22M parameters) that produces 384-dimensional embeddings. Changing this value after notes have already been stored will cause **embedding dimension mismatch** — all existing embeddings would need to be regenerated.

### `APP_API_PREFIX`

Sets the `root_path` on the FastAPI application. This affects how the OpenAPI docs and route matching work when the service is behind a reverse proxy. The default `/api/v1` means all routes are accessible at `/api/v1/notes`, `/api/v1/health`, etc.
