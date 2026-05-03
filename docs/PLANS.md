# Second Brain - Global Plan

## Overview
A minimal backend system for managing notes, built with FastAPI, PostgreSQL, Docker, and Alembic. Designed to evolve from simple CRUD into a structured personal knowledge system.

---

## Current Architecture

- Gateway: FastAPI application (all API logic)
- Database: PostgreSQL (Dockerized)
- Migrations: Alembic
- ORM: SQLAlchemy
- Config: Pydantic Settings (no os.getenv usage)
- Containerization: Docker + Docker Compose

Flow:
Client → Gateway → Repository → PostgreSQL

---

## Future Phase

Only after system is stable:

### Phase: Knowledge Structuring

- Tags for notes
- Categories or collections
- Basic relationships between notes
- Metadata (source, type, priority)

---

### Phase: Intelligence Layer

- AI-assisted note querying
- RAG-style architecture (only if needed)

---
