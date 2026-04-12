# Second Brain - Next Phase Plan

## Current State
- FastAPI gateway
- PostgreSQL database
- Notes can be created and retrieved(only all for now)
- Basic repository pattern in place
- Docker + Alembic configured

---

## Next Goals (CRUD Completion)

### 1. Get Note by ID
- Endpoint: `GET /notes/{id}`
- Return single note
- Return 404 if not found

---

### 2. Update Note
- Endpoint: `PUT /notes/{id}`
- Update note content
- Return updated note
- Return 404 if not found

---

### 3. Delete Note
- Endpoint: `DELETE /notes/{id}`
- Remove note from database
- Return success response (204 or boolean)

---

### 4. Search Notes
- Endpoint: `GET /notes?query=...`
- Case-insensitive search in content
- Limit results (10–20)
- Order by newest first

---

## Constraints
- No new services
- No architecture changes
- No service layer introduction
- Keep logic in gateway + repository
- Keep implementation minimal and consistent

---

## Completion Criteria
- Full CRUD for notes
- Search functionality working
- Stable API behavior with proper error handling


TODO: add pre-commit hoooks, editorconfig and other inital repo setup things if needed
