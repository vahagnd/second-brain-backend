# `second-brain-db` — Note Repository

## Overview

`NoteRepository` is the data access layer for the `notes` table. It follows the **Repository pattern** — all SQL queries are encapsulated here, keeping the gateway routers free of database concerns.

Defined in: `packages/second-brain-db/src/second_brain_db/repository/note.py`

---

## Instantiation

```python
class NoteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
```

A `NoteRepository` is created per request by the FastAPI dependency `get_notes_repository(session)`, which injects the current SQLAlchemy `Session`. The session is opened and closed by the `get_session()` generator dependency.

---

## Methods

### `add(content, embedding=None)` → `Note`

Inserts a new note into the database.

```python
def add(self, content: str, embedding: list[float] | None = None) -> Note:
    note = Note(content=content, embedding=embedding)
    self.session.add(note)
    self.session.commit()
    self.session.refresh(note)
    return note
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `content` | `str` | ✅ | The text content of the note |
| `embedding` | `list[float] \| None` | No | Pre-computed embedding vector; `None` if not provided |

- `session.refresh(note)` is called after commit to populate server-generated fields (`id`, `created_at`, `updated_at`).
- `expire_on_commit=False` on the session maker means the ORM object is not expired after commit, but `refresh` is still called explicitly to ensure the returned object is fully populated.

**Called by:** `POST /notes` route handler.

---

### `get_all()` → `list[Note]`

Returns all notes ordered by creation date (newest first).

```python
def get_all(self) -> list[Note]:
    stmt = select(Note).order_by(Note.created_at.desc())
    result = self.session.execute(stmt)
    return result.scalars().all()
```

**SQL equivalent:**
```sql
SELECT * FROM notes ORDER BY created_at DESC;
```

**Called by:**
- `GET /notes` (no search param) — returns all notes to the client
- `search_by_embedding()` — fetches all notes for in-memory similarity scoring

---

### `get_one_or_none(note_id)` → `Note | None`

Fetches a single note by primary key, or returns `None` if not found.

```python
def get_one_or_none(self, note_id: int) -> Note | None:
    stmt = select(Note).where(Note.id == note_id)
    result = self.session.execute(stmt)
    return result.scalars().first()
```

**SQL equivalent:**
```sql
SELECT * FROM notes WHERE id = :note_id LIMIT 1;
```

**Called by:**
- `GET /notes/{note_id}` route handler
- `delete()` — to check existence before deletion

---

### `delete(note_id)` → `bool`

Deletes a note by ID. Returns `True` if deleted, `False` if not found.

```python
def delete(self, note_id: int) -> bool:
    note = self.get_one_or_none(note_id)
    if not note:
        return False
    self.session.delete(note)
    self.session.commit()
    return True
```

**SQL equivalent:**
```sql
SELECT * FROM notes WHERE id = :note_id;  -- existence check
DELETE FROM notes WHERE id = :note_id;
```

Note: this performs **two queries** — a SELECT to check existence, then a DELETE. This is intentional to provide a meaningful boolean return value to the caller.

**Called by:** `DELETE /notes/{note_id}` route handler.

---

### `search_by_content(query)` → `list[Note]`

Performs a case-insensitive substring search on note content.

```python
def search_by_content(self, query: str) -> list[Note]:
    stmt = select(Note).where(Note.content.ilike(f"%{query}%")).order_by(Note.created_at.desc())
    result = self.session.execute(stmt)
    return result.scalars().all()
```

**SQL equivalent:**
```sql
SELECT * FROM notes
WHERE content ILIKE '%<query>%'
ORDER BY created_at DESC;
```

- Uses PostgreSQL's `ILIKE` for case-insensitive matching.
- No result limit — returns all matching notes.
- Results are ordered by `created_at` descending.

**Called by:** `GET /notes?search=...&search_type=like` route handler.

> **Note:** There is also a `search(query)` method (legacy) that applies a `LIMIT 10`. It is not currently called by any gateway endpoint and is superseded by `search_by_content`.

---

### `search_by_embedding(query_embedding, top_k=5, threshold=None)` → `list[tuple[Note, float]]`

Performs semantic similarity search using cosine similarity computed in Python.

```python
def search_by_embedding(
    self,
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float | None = None,
) -> list[(Note, float)]:
    all_notes = self.get_all()
    notes_with_embeddings = [note for note in all_notes if note.embedding is not None]

    if not notes_with_embeddings:
        return []

    similarities = [(note, cosine_similarity(query_embedding, note.embedding)) for note in notes_with_embeddings]

    if threshold is not None:
        similarities = [item for item in similarities if item[1] >= threshold]

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query_embedding` | `list[float]` | — | The embedding vector of the search query or new note |
| `top_k` | `int` | `5` | Maximum number of results to return |
| `threshold` | `float \| None` | `None` | Minimum similarity score to include a result. `None` means no filtering. |

**Returns:** `list[tuple[Note, float]]` — list of `(note, similarity_score)` pairs, sorted by score descending.

#### Algorithm

```
1. Fetch ALL notes from DB (get_all)
2. Filter out notes where embedding IS NULL
3. For each remaining note:
       score = cosine_similarity(query_embedding, note.embedding)
4. If threshold is set: discard notes where score < threshold
5. Sort by score descending
6. Return first top_k results
```

#### Cosine Similarity

Computed by `second_brain_db.utils.vector.cosine_similarity`:

```
similarity = dot(a, b) / (||a|| × ||b||)
```

Returns a value in `[-1, 1]`. A score of `1.0` means identical direction (semantically equivalent), `0.0` means orthogonal (unrelated), `-1.0` means opposite.

Returns `0.0` if either vector is a zero vector.

#### Performance Consideration

This is an **in-memory, brute-force** similarity search — all notes are loaded from the database and scored in Python. This approach is simple and correct but does not scale well:

| Notes count | Approximate behaviour |
|---|---|
| < 10,000 | Fast, acceptable latency |
| 10,000–100,000 | Noticeable latency, high memory usage |
| > 100,000 | Likely too slow for real-time requests |

For large datasets, a dedicated vector database (e.g., pgvector, Qdrant, Weaviate) or approximate nearest-neighbour (ANN) index would be needed.

#### Usage Contexts

| Caller | `threshold` | `top_k` | Purpose |
|---|---|---|---|
| `POST /notes` (dedup check) | `0.95` (from settings) | `5` (from settings) | Block near-duplicate notes |
| `GET /notes?search_type=semantic` | `None` | from request query param | Return most relevant notes |

---

## Legacy Method: `search(query)`

```python
def search(self, query: str) -> list[Note]:
    stmt = select(Note).where(Note.content.ilike(f"%{query}%")).order_by(Note.created_at.desc()).limit(10)
    result = self.session.execute(stmt)
    return result.scalars().all()
```

This method is identical to `search_by_content` but applies a hard `LIMIT 10`. It is **not called** by any current gateway endpoint and appears to be a legacy method superseded by `search_by_content`.

---

## Method Summary

| Method | SQL Operation | Returns | Called by |
|---|---|---|---|
| `add` | `INSERT` + `COMMIT` | `Note` | `POST /notes` |
| `get_all` | `SELECT *` | `list[Note]` | `GET /notes`, `search_by_embedding` |
| `get_one_or_none` | `SELECT WHERE id=` | `Note \| None` | `GET /notes/{id}`, `delete` |
| `delete` | `SELECT` + `DELETE` + `COMMIT` | `bool` | `DELETE /notes/{id}` |
| `search_by_content` | `SELECT WHERE ILIKE` | `list[Note]` | `GET /notes?search_type=like` |
| `search_by_embedding` | `SELECT *` + in-memory scoring | `list[(Note, float)]` | `POST /notes` (dedup), `GET /notes?search_type=semantic` |
| `search` *(legacy)* | `SELECT WHERE ILIKE LIMIT 10` | `list[Note]` | *(unused)* |
