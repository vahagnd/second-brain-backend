# ===================================================================
# Docker
# ===================================================================

start:
	APP_VERSION=$(shell git describe --tags --always) \
	docker compose up --build --remove-orphans

stop:
	docker compose down

restart: stop start

start-daemon:
	APP_VERSION=$(shell git describe --tags --always) \
	docker compose up --build --remove-orphans -d

# ===================================================================
# Development
# ===================================================================

project-init-dev: --install-packages-dev --tools-install

project-init-run:
	uv sync --all-packages --no-dev --no-editable

--install-packages-dev:
	uv sync --all-packages --all-groups --no-editable

--tools-install:
	uv run pre-commit install --hook-type pre-commit

# ===================================================================
# Linting
# ===================================================================
lint:
	uv run pre-commit run --all-files

ruff-fix:
	uv run ruff check --fix

ruff-check:
	uv run ruff check .

# ===================================================================
# Migrations
# ===================================================================
alembic-upgrade-head:
	uv run --env-file .env.local alembic upgrade head

alembic-get-current:
	uv run --env-file .env.local alembic current

# ===================================================================
# Testing
# ===================================================================
tests-e2e:
	uv run --env-file .env pytest tests -m e2e

tests-admin:
	uv run --env-file .env pytest tests -m admin

tests-notes:
	uv run --env-file .env pytest tests -m notes

tests-auth:
	uv run --env-file .env pytest tests -m auth
