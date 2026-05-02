# Gateway API Analytics

**Base path:** `/api/v1`
**Total endpoints:** 17

---

## Summary Table

| # | Method | Path | Tag | Auth Required | Admin Only | Success Code |
|---|--------|------|-----|:---:|:---:|:---:|
| 1 | GET | `/health` | health | No | No | 200 |
| 2 | GET | `/version` | system | No | No | 200 |
| 3 | POST | `/auth/login` | auth | No | No | 200 |
| 4 | POST | `/auth/refresh` | auth | No | No | 200 |
| 5 | POST | `/auth/logout` | auth | Yes | No | 200 |
| 6 | GET | `/users/me` | users | Yes | No | 200 |
| 7 | PATCH | `/users/me` | users | Yes | No | 200 |
| 8 | GET | `/notes` | notes | Yes | No | 200 |
| 9 | POST | `/notes` | notes | Yes | No | 201 |
| 10 | GET | `/notes/{note_id}` | notes | Yes | No | 200 |
| 11 | DELETE | `/notes/{note_id}` | notes | Yes | No | 204 |
| 12 | POST | `/admin/users` | admin | Yes | Yes | 201 |
| 13 | GET | `/admin/users` | admin | Yes | Yes | 200 |
| 14 | GET | `/admin/users/{user_id}` | admin | Yes | Yes | 200 |
| 15 | DELETE | `/admin/users/{user_id}` | admin | Yes | Yes | 204 |
| 16 | PATCH | `/admin/users/{user_id}` | admin | Yes | Yes | 200 |
| 17 | PATCH | `/admin/users/{user_id}/password` | admin | Yes | Yes | 200 |

---

## Endpoints by Tag

---

### Health

#### `GET /health`

- **Description:** Health check endpoint.
- **Auth:** None
- **Response 200:**
  ```json
  { "status": "ok" }
  ```

---

### System

#### `GET /version`

- **Description:** Get the application version.
- **Auth:** None
- **Response 200:**
  ```json
  { "version": "string" }
  ```

---

### Auth

#### `POST /auth/login`

- **Description:** Authenticate a user and return access and refresh tokens.
- **Auth:** None
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response 200:**
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
  ```
- **Response 401:** Invalid credentials

---

#### `POST /auth/refresh`

- **Description:** Exchange a valid refresh token for a new access + refresh token pair.
- **Auth:** None
- **Request Body:**
  ```json
  { "refresh_token": "string" }
  ```
- **Response 200:**
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
  ```
- **Response 401:** Invalid or expired refresh token

---

#### `POST /auth/logout`

- **Description:** Revoke all refresh tokens for the current user and blacklist the current access token.
- **Auth:** Bearer token (JWT)
- **Response 200:**
  ```json
  { "message": "Logged out successfully" }
  ```

---

### Users

#### `GET /users/me`

- **Description:** Get the current authenticated user's details.
- **Auth:** Bearer token (JWT)
- **Response 200:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated

---

#### `PATCH /users/me`

- **Description:** Update the current authenticated user's username.
- **Auth:** Bearer token (JWT)
- **Request Body:**
  ```json
  { "new_username": "string | null" }
  ```
- **Response 200:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated
- **Response 409:** Username already taken

---

### Notes

#### `GET /notes`

- **Description:** List notes with sorting and pagination. Supports semantic and LIKE search. Admins see all notes; regular users see only their own.
- **Auth:** Bearer token (JWT)
- **Query Parameters:**

  | Parameter | Type | Default | Description |
  |-----------|------|---------|-------------|
  | `search` | string or null | null | Search query string |
  | `search_type` | "like" or "semantic" | "semantic" | Search mode |
  | `top_k` | int (> 0) | 5 | Max results for semantic search |
  | `sort_by` | "id", "content", "created_at", "updated_at" | "id" | Sort field |
  | `order_by` | "asc" or "desc" | "desc" | Sort direction |
  | `page` | int (> 0) | 1 | Page number (1-based) |
  | `limit` | int (> 0) | 10 | Items per page |

- **Response 200:**
  ```json
  {
    "total": 42,
    "search_type": "semantic | like | null",
    "page": 1,
    "limit": 10,
    "pages": 5,
    "items": [
      {
        "id": 1,
        "content": "string",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "user_id": 1,
        "score": 0.98
      }
    ]
  }
  ```
  > `score` field is only present when `search_type` is `"semantic"`.

- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - insufficient permissions

---

#### `POST /notes`

- **Description:** Create a new note. Checks for semantic duplicates before saving.
- **Auth:** Bearer token (JWT)
- **Request Body:**
  ```json
  { "content": "string" }
  ```
- **Response 201:**
  ```json
  {
    "id": 1,
    "content": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "user_id": 1
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - insufficient permissions
- **Response 409:** A similar note already exists
  ```json
  {
    "message": "One or more similar notes already exist",
    "similar_notes": [
      {
        "id": 1,
        "content": "string",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "user_id": 1,
        "score": 0.97
      }
    ]
  }
  ```

---

#### `GET /notes/{note_id}`

- **Description:** Get a single note by its ID. Admins can access any note; regular users can only access their own.
- **Auth:** Bearer token (JWT)
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `note_id` | int | Note ID |

- **Response 200:**
  ```json
  {
    "id": 1,
    "content": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "user_id": 1
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - insufficient permissions
- **Response 404:** Note not found

---

#### `DELETE /notes/{note_id}`

- **Description:** Delete a note by its ID. Admins can delete any note; regular users can only delete their own.
- **Auth:** Bearer token (JWT)
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `note_id` | int | Note ID |

- **Response 204:** No content
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - insufficient permissions
- **Response 404:** Note not found

---

### Admin

> All admin endpoints require an authenticated user with the `admin` role.

#### `POST /admin/users`

- **Description:** Create a new user.
- **Auth:** Bearer token (JWT) - admin role required
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string",
    "role": "user"
  }
  ```
- **Response 201:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required
- **Response 409:** Username already exists

---

#### `GET /admin/users`

- **Description:** List all users.
- **Auth:** Bearer token (JWT) - admin role required
- **Response 200:**
  ```json
  {
    "total": 5,
    "items": [
      {
        "id": 1,
        "username": "string",
        "role": "string"
      }
    ]
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required

---

#### `GET /admin/users/{user_id}`

- **Description:** Get a user by ID.
- **Auth:** Bearer token (JWT) - admin role required
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `user_id` | int | User ID |

- **Response 200:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required
- **Response 404:** User not found

---

#### `DELETE /admin/users/{user_id}`

- **Description:** Delete a user by ID.
- **Auth:** Bearer token (JWT) - admin role required
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `user_id` | int | User ID |

- **Response 204:** No content
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required
- **Response 404:** User not found

---

#### `PATCH /admin/users/{user_id}`

- **Description:** Update a user's username.
- **Auth:** Bearer token (JWT) - admin role required
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `user_id` | int | User ID |

- **Request Body:**
  ```json
  { "new_username": "string | null" }
  ```
- **Response 200:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required
- **Response 404:** User not found
- **Response 409:** Username already taken

---

#### `PATCH /admin/users/{user_id}/password`

- **Description:** Update a user's password.
- **Auth:** Bearer token (JWT) - admin role required
- **Path Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `user_id` | int | User ID |

- **Request Body:**
  ```json
  { "new_password": "string" }
  ```
- **Response 200:**
  ```json
  {
    "id": 1,
    "username": "string",
    "role": "string"
  }
  ```
- **Response 401:** Unauthenticated
- **Response 403:** Forbidden - admin role required
- **Response 404:** User not found

---

## Statistics

### Endpoint Count by Tag

| Tag | Count |
|-----|------:|
| health | 1 |
| system | 1 |
| auth | 3 |
| users | 2 |
| notes | 4 |
| admin | 6 |
| **Total** | **17** |

### HTTP Method Distribution

| Method | Count |
|--------|------:|
| GET | 8 |
| POST | 4 |
| PATCH | 3 |
| DELETE | 2 |
| **Total** | **17** |

### Auth Requirements

| Category | Count |
|----------|------:|
| No auth required | 4 |
| Auth required (any role) | 7 |
| Auth required (admin only) | 6 |
| **Total** | **17** |

### Status Code Usage

| Status Code | Meaning | Endpoint Count |
|-------------|---------|:--------------:|
| 200 | OK | 13 |
| 201 | Created | 2 |
| 204 | No Content | 2 |
| 401 | Unauthorized | 15 |
| 403 | Forbidden | 10 |
| 404 | Not Found | 6 |
| 409 | Conflict | 4 |
