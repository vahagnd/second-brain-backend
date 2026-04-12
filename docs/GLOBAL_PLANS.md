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

## Core Principles

- Keep architecture minimal until complexity is needed
- Avoid unnecessary services or abstraction layers
- Prefer direct and readable code over overengineering
- One source of truth for configuration (settings.py)
- No runtime migration execution logic inside API

---

## Completed Milestones

- Dockerized application (gateway + database)
- PostgreSQL integration working
- Alembic migrations configured
- Notes table implemented
- Create and retrieve notes working
- Repository pattern introduced
- Environment configuration standardized

---

## Current Phase

### Goal: Complete CRUD + Search

Implement missing core functionality:

- Get note by ID
- Update note
- Delete note
- Search notes

Criteria:
- Stable API endpoints
- Proper error handling (404 where needed)
- Simple repository-based DB access
- No architectural changes

---

## Next Phase (Post-CRUD)

### Phase: Usability Layer

Focus on making the system usable:

- Pagination for notes
- Improved search filtering
- Basic sorting (date, relevance)
- Input validation improvements
- Consistent response schemas

---

## Future Phase (Optional Expansion)

Only after system is stable:

### Phase: Knowledge Structuring

- Tags for notes
- Categories or collections
- Basic relationships between notes
- Metadata (source, type, priority)

---

### Phase: Intelligence Layer (Optional)

- Semantic search
- Embeddings-based retrieval
- AI-assisted note querying
- RAG-style architecture (only if needed)

---

## What Will NOT Be Done (For Now)

- Microservices expansion
- Message queues
- Caching layers (Redis etc.)
- AI integration
- Complex domain decomposition
- Event-driven architecture

---

## Success Definition

The project is successful when:

- CRUD is fully functional
- Search is reliable
- System is stable in Docker
- Schema is versioned via migrations
- Code remains simple and readable
