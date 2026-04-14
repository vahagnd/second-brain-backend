```
You are working inside an existing FastAPI + SQLAlchemy project called `second_brain`.

## Context
- Postgres DB is already configured.
- The `notes` table already has an `embedding` column (JSONB or list[float]).
- The SQLAlchemy `Note` model already includes `embedding`.
- Notes CRUD already exists.
- Currently only keyword/LIKE search exists.

## Goal
Add local semantic search using embeddings.

## Requirements

### 1. Add local embedding model
Use:
- sentence-transformers/all-MiniLM-L6-v2

Create a service:

EmbeddingService:
- loads model once (IMPORTANT: no reload per request)
- methods:
  - embed(text: str) -> list[float]
  - embed_many(texts: list[str]) -> list[list[float]]

### 2. Ensure model is singleton / cached
- Use lru_cache or app-level singleton
- Model must be initialized once per app lifetime

### 3. Update note creation flow
When creating a note:
- generate embedding from note.content
- store it in note.embedding
- do NOT change DB schema

### 4. Implement semantic search in repository
Add method:

search_by_embedding(query_embedding: list[float], limit: int = 20)

Requirements:
- fetch all notes
- compute cosine similarity in Python
- rank by similarity (descending)
- return top N results

Use numpy for vector math.

### 5. Add cosine similarity helper

def cosine_similarity(a, b):
    # numpy implementation

### 6. Update GET /notes endpoint

Current behavior:
- search param uses keyword/LIKE search

Change to:
- if search is provided:
  - convert search query to embedding
  - use semantic search instead of LIKE
- else:
  - return all notes as-is

### 7. Keep everything compatible
- Do NOT break existing API response format
- Do NOT modify DB schema
- Do NOT introduce new dependencies beyond sentence-transformers + numpy
- Keep changes minimal and clean

### 8. Architecture constraints
- Router must NOT contain embedding logic directly
- Embedding generation must be in EmbeddingService
- Repository handles search logic

## Output
Apply all changes directly in codebase with clean structure.
```
