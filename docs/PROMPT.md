You are a senior backend/devops engineer.

We already have a minimal system:

* sb_gateway (FastAPI app, contains all logic for now)
* second_brain_db (PostgreSQL database layer / schema if any)
* No services layer
* No AI
* No MinIO

Your task is to containerize the system using Docker.

---

# Goals

Create a fully working local Docker setup where:

* Gateway runs in a container
* PostgreSQL runs in a container
* Gateway connects to PostgreSQL via Docker network
* Everything runs with a single command: docker compose up

---

# Constraints

* No Kubernetes
* No production infra complexity
* No microservices splitting changes
* No rewriting application logic
* Keep everything minimal and local-dev focused

---

# Required Output

## 1. docker-compose.yml

Must include:

### Services:

* db (PostgreSQL 16 official image)
* gateway (FastAPI app container)

### Requirements:

* DB data must persist using Docker volume
* Gateway must depend on DB
* Gateway must use internal Docker network to connect to DB

---

## 2. Gateway Dockerfile

* Python 3.11 slim
* Install dependencies using uv (Astral package manager)
* Copy app code
* Run FastAPI using uvicorn

---

## 3. Environment handling

Gateway must use the following environment variables:

* DATABASE_HOST
* DATABASE_PORT
* DATABASE_NAME
* DATABASE_USER
* DATABASE_PASSWORD

IMPORTANT:

* DATABASE_HOST must be set to "db" inside Docker
* NOT localhost

The application must construct DATABASE_URL internally using pydantic-settings.

---

## 4. Database container

* Use postgres:16
* Set:
  POSTGRES_USER=user
  POSTGRES_PASSWORD=password
  POSTGRES_DB=second_brain
* Expose port 5432

---

## 5. Settings requirement

The application must use pydantic-settings.

Rules:

* Do NOT use os.getenv
* Do NOT use python-dotenv
* All configuration must be in settings.py
* DATABASE_URL must be a computed property from individual env vars

---

## 6. Networking rules

* Gateway must wait for DB availability (depends_on is enough for now)
* No external network config needed

---

## 7. Output expectation

After setup:

* docker compose up builds everything
* gateway accessible on localhost:8000
* /health endpoint works
* /notes endpoints work
* DB persists between restarts

---

# Do NOT include

* Kubernetes
* Redis
* MinIO
* multiple services beyond gateway + db
* async refactors
* architecture changes
* service layer reintroduction
