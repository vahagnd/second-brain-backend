# Plan: User Authentication & Authorization

## Overview

This plan describes all changes required to add a proper authentication and authorization system to the `second-brain-gateway` service. The system uses **JWT (Bearer tokens)** for stateless authentication and a simple **role-based access control** (`user` / `admin`) for authorization.

---

## Current State

- `users` table: `id`, `username`, `created_at`, `updated_at` — no password or role columns
- `notes` table: has `user_id` FK (nullable), not enforced by auth
- `UserRepository`: basic CRUD — no password or role support
- Admin router: `POST/GET/DELETE /admin/users` — no auth protection
- Auth router: empty stub
- Users router: empty
- No authentication or authorization anywhere

---

## Step 1 — Database Schema Changes

### 1.1 Update `User` ORM model (`packages/second-brain-db/src/second_brain_db/db/models.py`)

Add two new columns to the `User` SQLAlchemy model:

```python
password_hash: Mapped[str] = mapped_column(Text, nullable=False)
role: Mapped[str] = mapped_column(Text, nullable=False, server_default="user")
```

### 1.2 New Alembic Migration

Create a new migration file in `migrations/versions/` that:

- Adds `password_hash TEXT NOT NULL DEFAULT ''` to `users` table (empty default to satisfy NOT NULL for existing rows; should be populated before removing default in production)
- Adds `role TEXT NOT NULL DEFAULT 'user'` to `users` table

Migration chain: `536279ad4c75` → `<new_revision>`

---

## Step 2 — New Dependencies

Add to `apps/second-brain-gateway/pyproject.toml`:

- `python-jose[cryptography]` — JWT token creation and validation
- `passlib[bcrypt]` — password hashing with bcrypt

Install with `uv`:
```bash
uv add python-jose[cryptography] passlib[bcrypt] --project apps/second-brain-gateway
```

---

## Step 3 — JWT Settings

Add a new `JWTSettings` class to `apps/second-brain-gateway/settings.py`:

```python
class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", case_sensitive=False)

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

jwt_settings = JWTSettings()
```

Update `.env.example` with:
```
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Step 4 — `second-brain-db` Package Changes

### 4.1 Update `UserRepository` (`packages/second-brain-db/src/second_brain_db/repository/user.py`)

Update and add methods:

- **`add(username, password_hash, role="user") -> User`** — update signature to accept `password_hash` and `role`
- **`update(user_id, username=None) -> User | None`** — update username field; return updated user or None if not found
- **`update_password(user_id, password_hash) -> User | None`** — update `password_hash` field; return updated user or None if not found

### 4.2 New `AuthService` (`packages/second-brain-db/src/second_brain_db/services/auth.py`)

A stateless service (no `__init__` needed, all static/module-level functions) providing:

- **`hash_password(plain_password: str) -> str`** — bcrypt hash using `passlib.context.CryptContext`
- **`verify_password(plain_password: str, hashed_password: str) -> bool`** — bcrypt verify
- **`create_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta) -> str`** — encodes JWT with expiry using `python-jose`
- **`decode_access_token(token: str, secret_key: str, algorithm: str) -> dict | None`** — decodes JWT; returns payload dict or `None` on invalid/expired token

Export `AuthService` from `packages/second-brain-db/src/second_brain_db/services/__init__.py`.

---

## Step 5 — Gateway: New Pydantic Models

### 5.1 Update `apps/second-brain-gateway/models/user.py`

Add:

- **`UserDetail`** — `id: int`, `username: str`, `role: str`, `created_at: datetime`
- **`UserUpdate`** — `username: str | None = None`
- **`UserUpdatePassword`** — `new_password: str`

Update `UserCreatedResponse` to include `role: str`.

### 5.2 New `apps/second-brain-gateway/models/auth.py`

- **`LoginRequest`** — `username: str`, `password: str`
- **`TokenResponse`** — `access_token: str`, `token_type: str = "bearer"`

---

## Step 6 — Gateway: Auth Dependency

New file: `apps/second-brain-gateway/dependencies/auth.py`

### OAuth2 scheme

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

### `get_current_user(token, session) -> User ORM model`

1. Call `AuthService.decode_access_token(token, ...)` using `jwt_settings`
2. If payload is `None` → raise `401 Unauthorized` with `WWW-Authenticate: Bearer`
3. Extract `user_id = int(payload["sub"])`
4. Fetch user via `UserRepository(session).get_one_or_none(user_id)`
5. If user not found → raise `401 Unauthorized`
6. Return user ORM object

### `get_current_admin_user(current_user: CurrentUserDependency) -> User ORM model`

1. Check `current_user.role == "admin"`
2. If not → raise `403 Forbidden`
3. Return user

### Type aliases

```python
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
AdminUserDependency = Annotated[User, Depends(get_current_admin_user)]
```

---

## Step 7 — Auth Router (`apps/second-brain-gateway/routers/auth.py`)

Router prefix: `/auth`, tag: `auth`

### `POST /auth/login`

- Request body: `LoginRequest` (`username`, `password`)
- Fetch user by username via `UserRepository`; if not found → `401 Unauthorized` ("Invalid credentials")
- Verify password with `AuthService.verify_password`; if wrong → `401 Unauthorized` ("Invalid credentials")
- Create JWT: payload `{"sub": str(user.id), "role": user.role}`, expiry from `jwt_settings.access_token_expire_minutes`
- Return `TokenResponse(access_token=..., token_type="bearer")`

### `POST /auth/logout`

- Requires `CurrentUserDependency` (validates token is still valid)
- Stateless logout — server does not invalidate token (client is responsible for discarding it)
- Return `200 OK`: `{"message": "Logged out successfully"}`

---

## Step 8 — Users Router (`apps/second-brain-gateway/routers/users.py`)

Router prefix: `/users`, tag: `users`

### `GET /users/me`

- Requires `CurrentUserDependency`
- Return `UserDetail(id, username, role, created_at)` for the current user

### `PATCH /users/me`

- Requires `CurrentUserDependency`
- Request body: `UserUpdate` (`username: str | None`)
- If `username` provided: check it's not already taken via `user_repo.get_one_or_none_by_username(username)` → `400 Bad Request` if taken
- Call `user_repo.update(current_user.id, username=username)`
- Return updated `UserDetail`

---

## Step 9 — Admin Router Updates (`apps/second-brain-gateway/routers/admin.py`)

All admin endpoints must be protected with `AdminUserDependency`.

### Existing endpoints — add `AdminUserDependency`

- `POST /admin/users` — add `admin_user: AdminUserDependency` parameter
- `GET /admin/users` — add `admin_user: AdminUserDependency` parameter
- `GET /admin/users/{user_id}` — add `admin_user: AdminUserDependency` parameter
- `DELETE /admin/users/{user_id}` — add `admin_user: AdminUserDependency` parameter

### Update `POST /admin/users`

- Accept `username: str` and `password: str` in request body (use a `UserAdminCreate` Pydantic model: `username: str`, `password: str`, `role: str = "user"`)
- Hash password with `AuthService.hash_password(password)`
- Call `user_repo.add(username, password_hash=hashed, role=role)`
- Return `UserCreatedResponse`

### New `PATCH /admin/users/{user_id}`

- Requires `AdminUserDependency`
- Request body: `UserUpdate` (`username: str | None`)
- Validate user exists → `404 Not Found` if not
- If `username` provided: check not already taken → `400 Bad Request` if taken
- Call `user_repo.update(user_id, username=username)`
- Return updated `UserDetail`

### New `PATCH /admin/users/{user_id}/password`

- Requires `AdminUserDependency`
- Request body: `UserUpdatePassword` (`new_password: str`)
- Validate user exists → `404 Not Found` if not
- Hash new password with `AuthService.hash_password(new_password)`
- Call `user_repo.update_password(user_id, password_hash=hashed)`
- Return `204 No Content`

---

## Step 10 — Notes Router Authorization (`apps/second-brain-gateway/routers/notes.py`)

All note endpoints require `CurrentUserDependency`.

### `POST /notes`

- Add `current_user: CurrentUserDependency`
- Pass `user_id=current_user.id` to `notes_repo.add(content, embedding, user_id=current_user.id)`
- `NoteRepository.add()` must accept `user_id` parameter

### `GET /notes`

- Add `current_user: CurrentUserDependency`
- All repository calls (`get_all`, `search_by_content`, `search_by_embedding`) must filter by `user_id=current_user.id`
- `NoteRepository` methods need `user_id` filter parameter

### `GET /notes/{note_id}`

- Add `current_user: CurrentUserDependency`
- After fetching note, verify `note.user_id == current_user.id` → `404 Not Found` if not (do not reveal existence)

### `DELETE /notes/{note_id}`

- Add `current_user: CurrentUserDependency`
- After fetching note, verify `note.user_id == current_user.id` → `404 Not Found` if not
- `NoteRepository.delete()` should accept optional `user_id` for ownership check, or check is done in router before calling delete

---

## Step 11 — `NoteRepository` Updates (`packages/second-brain-db/src/second_brain_db/repository/note.py`)

Update methods to support `user_id` filtering:

- **`add(content, embedding=None, user_id=None) -> Note`** — pass `user_id` to `Note()`
- **`get_all(user_id=None) -> list[Note]`** — add `WHERE user_id = :user_id` filter when provided
- **`search_by_content(query, user_id=None) -> list[Note]`** — add `user_id` filter when provided
- **`search_by_embedding(query_embedding, top_k, threshold, user_id=None)`** — call `get_all(user_id=user_id)` internally
- **`get_one_or_none(note_id, user_id=None) -> Note | None`** — add `user_id` filter when provided

---

## Step 12 — Register Auth Router

Update `apps/second-brain-gateway/routers/__init__.py`:

```python
from routers import admin, auth, health, notes, users

def init_routers(app: FastAPI):
    app.include_router(notes.router)
    app.include_router(admin.router)
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(health.router)
```

---

## File Change Summary

| File | Change Type |
|---|---|
| `packages/second-brain-db/src/second_brain_db/db/models.py` | Update — add `password_hash`, `role` to `User` |
| `packages/second-brain-db/src/second_brain_db/repository/user.py` | Update — add `update`, `update_password`, update `add` signature |
| `packages/second-brain-db/src/second_brain_db/repository/note.py` | Update — add `user_id` filter to all methods |
| `packages/second-brain-db/src/second_brain_db/services/auth.py` | **New** — `hash_password`, `verify_password`, `create_access_token`, `decode_access_token` |
| `packages/second-brain-db/src/second_brain_db/services/__init__.py` | Update — export `AuthService` |
| `migrations/versions/<new_revision>.py` | **New** — add `password_hash`, `role` columns to `users` |
| `apps/second-brain-gateway/pyproject.toml` | Update — add `python-jose[cryptography]`, `passlib[bcrypt]` |
| `apps/second-brain-gateway/settings.py` | Update — add `JWTSettings` |
| `apps/second-brain-gateway/models/auth.py` | **New** — `LoginRequest`, `TokenResponse` |
| `apps/second-brain-gateway/models/user.py` | Update — add `UserDetail`, `UserUpdate`, `UserUpdatePassword`, `UserAdminCreate` |
| `apps/second-brain-gateway/dependencies/auth.py` | **New** — `get_current_user`, `get_current_admin_user`, type aliases |
| `apps/second-brain-gateway/routers/auth.py` | Update — implement `POST /auth/login`, `POST /auth/logout` |
| `apps/second-brain-gateway/routers/users.py` | Update — implement `GET /users/me`, `PATCH /users/me` |
| `apps/second-brain-gateway/routers/admin.py` | Update — protect all endpoints, add `PATCH /admin/users/{id}`, `PATCH /admin/users/{id}/password` |
| `apps/second-brain-gateway/routers/notes.py` | Update — add `CurrentUserDependency` to all endpoints, pass `user_id` |
| `apps/second-brain-gateway/routers/__init__.py` | Update — register `auth` router |
| `.env.example` | Update — add `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` |

---

## API Endpoints Summary (After Implementation)

### Auth (`/auth`)

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/auth/login` | No | Login with username/password, returns JWT |
| `POST` | `/auth/logout` | Yes (any user) | Stateless logout (client discards token) |

### Users (`/users`)

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `GET` | `/users/me` | Yes (any user) | Get current user info |
| `PATCH` | `/users/me` | Yes (any user) | Update current user's username |

### Notes (`/notes`)

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/notes` | Yes (any user) | Create note (scoped to current user) |
| `GET` | `/notes` | Yes (any user) | List/search notes (scoped to current user) |
| `GET` | `/notes/{id}` | Yes (any user) | Get note by ID (must belong to current user) |
| `DELETE` | `/notes/{id}` | Yes (any user) | Delete note (must belong to current user) |

### Admin (`/admin`)

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/admin/users` | Yes (admin) | Create user with username, password, role |
| `GET` | `/admin/users` | Yes (admin) | List all users |
| `GET` | `/admin/users/{id}` | Yes (admin) | Get user by ID |
| `DELETE` | `/admin/users/{id}` | Yes (admin) | Delete user by ID |
| `PATCH` | `/admin/users/{id}` | Yes (admin) | Update user's username |
| `PATCH` | `/admin/users/{id}/password` | Yes (admin) | Change user's password |

---

## Notes & Decisions

- **JWT strategy**: Stateless access tokens only. No refresh tokens in this iteration.
- **Logout**: Server-side stateless — no token blacklist. Client discards the token. A future iteration could add a token blacklist in Redis.
- **Password storage**: bcrypt via `passlib`. Never stored in plain text.
- **Admin bootstrap**: The first admin user must be created directly in the DB or via a seed script (since `POST /admin/users` itself requires admin auth). A future iteration could add a seed/bootstrap command.
- **Note ownership**: Notes are scoped to the authenticated user. Users cannot see or modify other users' notes. `404` is returned (not `403`) to avoid revealing existence of other users' notes.
- **Role values**: `"user"` (default) and `"admin"`. Stored as plain text in DB.
- **Module size**: All files must stay under 400 lines per dev rules. Split into smaller modules if needed.
- **No pip**: All dependency installs use `uv`.
