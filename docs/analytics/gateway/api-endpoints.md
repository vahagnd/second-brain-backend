# Gateway — API Endpoints

Base path: `/api/v1` (configurable via `APP_API_PREFIX`)

All note endpoints are under the `/notes` prefix. A separate `/health` endpoint is available for liveness checks.

---

## Table of Contents

- [Health Check](#health-check)
- [Create Note](#create-note)
- [List / Search Notes](#list--search-notes)
- [Get Note by ID](#get-note-by-id)
- [Delete Note](#delete-note)

---

## Health Check

```
GET /health
```

Returns the liveness status of the service. No authentication required.

**Response `200 OK`**

```json
{ "status": "ok" }
```

---

## Create Note

```
POST /notes
```

Creates a new note. Before persisting, the gateway generates an embedding for the note content and checks for semantic duplicates. If a note with cosine similarity ≥ `SIMILARITY_SEARCH_THRESHOLD` (default `0.95`) already exists, the request is rejected.

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | `string` | ✅ | The text content of the note |

```json
{
  "content": "FastAPI uses Pydantic for data validation."
}
```

### Responses

**`201 Created`** — Note was created successfully.

```json
{
  "id": 42,
  "content": "FastAPI uses Pydantic for data validation.",
  "created": true
}
```

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Auto-generated primary key |
| `content` | `string` | The note content as submitted |
| `created` | `boolean` | Always `true` on success |

---

**`409 Conflict`** — A semantically similar note already exists.

```json
{
  "detail": {
    "message": "Very similar notes already exist.",
    "similar_notes": [
      {
        "id": 7,
        "content": "Pydantic is used by FastAPI for validation.",
        "score": 0.97
      }
    ]
  }
}
```

| Field | Type | Description |
|---|---|---|
| `detail.message` | `string` | Human-readable error message |
| `detail.similar_notes` | `array` | List of conflicting notes |
| `similar_notes[].id` | `integer` | ID of the existing similar note |
| `similar_notes[].content` | `string` | Content of the existing similar note |
| `similar_notes[].score` | `float` | Cosine similarity score (0–1) |

---

## List / Search Notes

```
GET /notes
```

Returns a list of notes. Behaviour depends on the query parameters provided.

### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | `string` | `null` | Optional search query. If omitted, all notes are returned. |
| `search_type` | `"semantic"` \| `"like"` | `"semantic"` | Search strategy. Only used when `search` is provided. |
| `top_k` | `integer` (> 0) | `5` | Maximum results for semantic search. Ignored for `like` search and when no `search` is given. |
| `sort_by` | `"id"` \| `"content"` \| `"created_at"` \| `"updated_at"` | `"id"` | Field to sort results by. Ignored for semantic search (results are always ordered by relevance score). |
| `order_by` | `"asc"` \| `"desc"` | `"desc"` | Sort direction. Ignored for semantic search. |
| `page` | `integer` (> 0) | `1` | 1-based page number. |
| `limit` | `integer` (> 0) | `10` | Number of items per page. Configurable via `PAGINATION_LIMIT`. |

### Behaviour Matrix

| `search` | `search_type` | Behaviour |
|---|---|---|
| not provided | — | Returns all notes sorted by `sort_by` / `order_by`, paginated |
| provided | `"semantic"` | Embeds the query, runs cosine similarity search, returns top `top_k` results sorted by score descending, paginated |
| provided | `"like"` | Runs a case-insensitive SQL `ILIKE '%query%'` search, sorted by `sort_by` / `order_by`, paginated |

### Responses

**`200 OK`** — Plain list (no search or `like` search)

```json
{
  "total": 2,
  "search_type": null,
  "page": 1,
  "limit": 10,
  "pages": 1,
  "items": [
    { "id": 42, "content": "FastAPI uses Pydantic for data validation." },
    { "id": 41, "content": "SQLAlchemy is a Python ORM." }
  ]
}
```

**`200 OK`** — Semantic search result

```json
{
  "total": 1,
  "search_type": "semantic",
  "page": 1,
  "limit": 10,
  "pages": 1,
  "items": [
    { "id": 42, "content": "FastAPI uses Pydantic for data validation.", "score": 0.91 }
  ]
}
```

### Response Schema

| Field | Type | Description |
|---|---|---|
| `total` | `integer` | Total number of matching items (before pagination) |
| `search_type` | `"like"` \| `"semantic"` \| `null` | Indicates which search strategy was used |
| `page` | `integer` | Current page number (1-based) |
| `limit` | `integer` | Number of items per page |
| `pages` | `integer` | Total number of pages (`ceil(total / limit)`) |
| `items` | `array<Note>` or `array<NoteWithScore>` | List of notes for the current page |
| `items[].id` | `integer` | Note ID |
| `items[].content` | `string` | Note content |
| `items[].score` | `float` | Cosine similarity score — only present for semantic search |

---

## Get Note by ID

```
GET /notes/{note_id}
```

Retrieves a single note by its integer ID.

### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `note_id` | `integer` | The ID of the note to retrieve |

### Responses

**`200 OK`**

```json
{
  "id": 42,
  "content": "FastAPI uses Pydantic for data validation.",
  "created_at": "2026-04-14T10:30:00+00:00"
}
```

| Field | Type | Description |
|---|---|---|
| `id` | `integer` | Note ID |
| `content` | `string` | Note content |
| `created_at` | `string` (ISO 8601) | Creation timestamp |

**`404 Not Found`**

```json
{ "detail": "Note not found" }
```

---

## Delete Note

```
DELETE /notes/{note_id}
```

Permanently deletes a note by its ID.

### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `note_id` | `integer` | The ID of the note to delete |

### Responses

**`204 No Content`** — Note was deleted. Response body is empty.

**`404 Not Found`**

```json
{ "detail": "Note not found" }
```

---

## Pydantic Schemas Summary

| Schema | Used in | Fields |
|---|---|---|
| `NoteCreate` | `POST /notes` request body | `content: str` |
| `NoteCreatedResponse` | `POST /notes` response | `id: int`, `content: str`, `created: bool` |
| `Note` | `GET /notes`, `GET /notes/{id}` response | `id: int`, `content: str` |
| `NoteWithScore` | `GET /notes` semantic search response | `id: int`, `content: str`, `score: float` |
| `NoteListResponse` | `GET /notes` response wrapper | `total: int`, `search_type: str\|null`, `page: int\|null`, `limit: int\|null`, `pages: int\|null`, `items: list` |
