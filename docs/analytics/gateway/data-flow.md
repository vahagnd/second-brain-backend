# Gateway — Data Flow

This document describes the step-by-step request lifecycle for each operation exposed by the gateway.

---

## 1. Create Note (`POST /notes`)

This is the most complex flow because it includes embedding generation and semantic deduplication before persisting.

```
Client
  │
  │  POST /notes  { "content": "..." }
  ▼
FastAPI Router (routers/notes.py)
  │
  │  1. Validate request body via NoteCreate (Pydantic)
  │
  ├─► EmbeddingService.embed(content)
  │       │
  │       │  2. Load sentence-transformer model (cached via lru_cache)
  │       │  3. Encode content → list[float]  (all-MiniLM-L6-v2)
  │       │
  │       └─► returns embedding: list[float]
  │
  ├─► NoteRepository.search_by_embedding(embedding, top_k, threshold=0.95)
  │       │
  │       │  4. Fetch ALL notes from DB (SELECT * FROM notes ORDER BY created_at DESC)
  │       │  5. Filter notes that have an embedding
  │       │  6. Compute cosine_similarity(query_embedding, note.embedding) for each
  │       │  7. Filter results where similarity >= threshold (0.95)
  │       │  8. Sort by similarity descending, take top_k
  │       │
  │       └─► returns list[(Note, float)]
  │
  ├─ [duplicates found?]
  │       │
  │       YES ──► raise HTTPException 409 Conflict
  │       │         { "message": "...", "similar_notes": [...] }
  │       │
  │       NO
  │       │
  ├─► NoteRepository.add(content, embedding)
  │       │
  │       │  9.  INSERT INTO notes (content, embedding) VALUES (...)
  │       │  10. COMMIT
  │       │  11. REFRESH (fetch generated id, created_at, updated_at)
  │       │
  │       └─► returns Note ORM object
  │
  └─► Return NoteCreatedResponse  →  201 Created
```

**Key design decisions:**
- Embedding is generated **before** the duplicate check so the same vector is reused for both dedup and storage.
- The dedup threshold (`0.95`) is intentionally high to avoid false positives — only near-identical notes are blocked.
- The `top_k` used for dedup comes from `SIMILARITY_SEARCH_TOP_K` (default `5`), not from the request.

---

## 2. List All Notes (`GET /notes` — no search param)

```
Client
  │
  │  GET /notes
  ▼
FastAPI Router
  │
  ├─► NoteRepository.get_all()
  │       │
  │       │  SELECT * FROM notes ORDER BY created_at DESC
  │       │
  │       └─► returns list[Note]
  │
  └─► Return NoteListResponse(total=N, search_type=None, items=[Note, ...])
        →  200 OK
```

---

## 3. Search Notes — Semantic (`GET /notes?search=...&search_type=semantic`)

```
Client
  │
  │  GET /notes?search=<query>&search_type=semantic&top_k=5
  ▼
FastAPI Router
  │
  ├─► EmbeddingService.embed(search_query)
  │       │
  │       │  Encode query text → list[float]
  │       │
  │       └─► returns search_embedding: list[float]
  │
  ├─► NoteRepository.search_by_embedding(search_embedding, top_k=5)
  │       │
  │       │  1. Fetch ALL notes from DB
  │       │  2. Filter notes with embeddings
  │       │  3. Compute cosine_similarity for each
  │       │  4. No threshold filter (threshold=None for search)
  │       │  5. Sort descending, take top_k
  │       │
  │       └─► returns list[(Note, float)]
  │
  └─► Return NoteListResponse(total=N, search_type="semantic", items=[NoteWithScore, ...])
        →  200 OK
```

**Note:** Unlike deduplication, semantic search does **not** apply a similarity threshold — all notes are ranked and the top `top_k` are returned regardless of score.

---

## 4. Search Notes — LIKE (`GET /notes?search=...&search_type=like`)

```
Client
  │
  │  GET /notes?search=<query>&search_type=like
  ▼
FastAPI Router
  │
  ├─► NoteRepository.search_by_content(query)
  │       │
  │       │  SELECT * FROM notes
  │       │  WHERE content ILIKE '%<query>%'
  │       │  ORDER BY created_at DESC
  │       │
  │       └─► returns list[Note]
  │
  └─► Return NoteListResponse(total=N, search_type=None, items=[Note, ...])
        →  200 OK
```

**Note:** `search_type` in the response is `null` for LIKE search — only semantic search sets it to `"semantic"`.

---

## 5. Get Note by ID (`GET /notes/{note_id}`)

```
Client
  │
  │  GET /notes/42
  ▼
FastAPI Router
  │
  ├─► NoteRepository.get_one_or_none(note_id=42)
  │       │
  │       │  SELECT * FROM notes WHERE id = 42
  │       │
  │       └─► returns Note | None
  │
  ├─ [note found?]
  │       │
  │       NO  ──► raise HTTPException 404 Not Found
  │       │
  │       YES
  │       │
  └─► Return Note(id, content, created_at=ISO8601)  →  200 OK
```

---

## 6. Delete Note (`DELETE /notes/{note_id}`)

```
Client
  │
  │  DELETE /notes/42
  ▼
FastAPI Router
  │
  ├─► NoteRepository.delete(note_id=42)
  │       │
  │       │  1. SELECT * FROM notes WHERE id = 42  (get_one_or_none)
  │       │
  │       ├─ [note found?]
  │       │       │
  │       │       NO  ──► return False
  │       │       │
  │       │       YES
  │       │       │
  │       │       │  2. session.delete(note)
  │       │       │  3. session.commit()
  │       │       │
  │       │       └─► return True
  │       │
  │       └─► returns bool
  │
  ├─ [deleted?]
  │       │
  │       NO  ──► raise HTTPException 404 Not Found
  │       │
  │       YES
  │       │
  └─► Return None  →  204 No Content
```

---

## Dependency Injection Flow

FastAPI resolves dependencies in the following order for each request:

```
Request arrives
      │
      ▼
get_session()                    ← creates a new SQLAlchemy Session
      │
      ▼
get_notes_repository(session)    ← wraps session in NoteRepository
      │
      ▼
get_embedding_service()          ← returns EmbeddingService()
      │                             (model loaded once via lru_cache)
      ▼
Route handler executes
      │
      ▼
finally: session.close()         ← session closed after response
```

The DB session lifecycle is managed by a generator dependency (`get_session`) that ensures the session is always closed, even on exceptions.
