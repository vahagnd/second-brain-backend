You are a senior backend engineer building a production-quality MVP called "Second Brain API".

You MUST strictly follow the rules defined in the `.clinerules/` directory and the `PROJECT_SPEC.md`.

---

# 🎯 Objective

Create a fully working backend foundation for the project.

This includes:

* FastAPI application setup
* PostgreSQL connection using SQLAlchemy
* basic project structure (already defined in spec)
* initial Notes model + CRUD foundation
* working /health endpoint
* working /notes endpoint (create + list)

---

# ⚙️ Hard Constraints

* Python 3.11+
* MUST use uv (Astral package manager)
* PostgreSQL only (no SQLite fallback)
* SQLAlchemy ORM only
* Pydantic for schemas
* No Docker
* No authentication
* No frontend
* No embeddings
* No vector database

---

# 📦 Required Setup Steps

## 1. Initialize project using uv

* assume uv is already installed
* use:

  * uv init (if needed)
  * uv add for dependencies

## 2. Install dependencies

Include:

* fastapi
* uvicorn
* sqlalchemy
* psycopg2-binary
* pydantic
* python-dotenv

---

# 🏗️ Architecture Requirements

Follow strict layering:

* api/ → routes only
* services/ → business logic
* models/ → DB tables
* schemas/ → validation
* db.py → database connection only

NO business logic in routes.

---

# 🧠 Core Features to Implement First

## 1. Health check

GET /health
→ returns {"status": "ok"}

---

## 2. Notes

### Create note

POST /notes
Body:

* content: string

Stores note in PostgreSQL.

---

### List notes

GET /notes
Returns all notes ordered by newest first.

---

# 🗄️ Database Model

Table: notes

* id (int primary key)
* content (text)
* created_at (timestamp default now)

---

# 🔌 Database Rules

* Use DATABASE_URL from environment variables
* Use SQLAlchemy session management properly
* No global sessions leaking

---

# 🧼 Code Quality Rules

* Keep functions small
* No unnecessary abstraction layers
* No overengineering
* No premature optimization
* Clear naming only

---

# 📁 Output Requirement

Generate full working code for:

* all required files
* correct imports
* runnable project

Ensure:

* `uv run python run.py` starts server successfully
* `/health` works immediately
* `/notes` CRUD works without modification

---

# 🚫 Do NOT include

* embeddings
* AI logic yet
* vector search
* authentication
* frontend
* Docker
* extra features beyond spec

---

# 🧭 After completion

Stop after backend foundation is working. Do not expand scope.
