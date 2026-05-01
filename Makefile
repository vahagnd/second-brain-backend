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

ruff-fix-all:
	uv run ruff check --fix

# ===================================================================
# Migrations
# ===================================================================
alembic-upgrade-head:
	uv run --env-file .env.local alembic upgrade head

alembic-get-current:
	uv run --env-file .env.local alembic current
