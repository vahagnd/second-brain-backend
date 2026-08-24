# Flaws & Fixes

## Critical

- **Semantic search sort is broken** (`routers/notes.py:124`, `utils/pagination.py:8`): passing ORM `Note` objects keyed on `.score` never matches, so relevance sort is a no-op. Carry the similarity score through sorting.
- **Sync DB on async loop** (`db/engine.py:8`): driver is `psycopg2`; every query blocks the event loop. Unused asyncpg URI (`sqlalchemy_uri_v2`) hints at an unfinished async engine.
- **Inconsistent threshold** (`routers/notes.py:53,117`): `create` rejects near-duplicates at the threshold, but `search` ignores it — notes you can't create still appear in results.

## Performance

- **O(n) semantic search** (`repository/note.py:98`): loads all user notes and computes cosine similarity in Python. Use `pgvector`/ANN index for scale.
- **Full embedding JSONB loaded on every read** (`models.py:26`): defer/separate the column for non-semantic queries.

## Security

- **No rate limiting** on `/auth/login`, `/refresh`, `/signup` — brute-force risk.
- **Username enumeration** via distinct 409 on signup.
- **No password policy** — empty/trivial passwords allowed.
- **Refresh tokens stored in plaintext** (`repository/refresh_token.py`) — store a hash instead.

## Hygiene

- **Expired tokens never cleaned** — `delete_expired` exists but is never called.
- **First-admin lockout risk** — no seed/bootstrap path for the admin role.
- **Deploy**: Dockerfile runs `uv sync --locked` with no dev flag — packaging drift risk.

## Notes (not bugs)

- Access token uses a DB blacklist (`jti`) — fine, costs one query/request.
- Password change revokes refresh tokens but not the current access token.
- `Note.user_id` nullable vs `Feedback.user_id` non-null — inconsistent but likely intentional.
