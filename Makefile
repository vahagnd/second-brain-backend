# ===================================================================
# Docker
# ===================================================================

start-daemon:
	APP_VERSION=$(shell git describe --tags --always) \
	docker compose up --build --remove-orphans -d

stop:
	docker compose down

restart: stop start-daemon


# ===================================================================
# Development
# ===================================================================

project-init-dev: --install-packages-dev --tools-install

project-init-run:
	uv sync --all-packages --no-dev

--install-packages-dev:
	uv sync --all-packages --all-groups

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

alembic-downgrade:
	uv run --env-file .env.local alembic downgrade -1

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
