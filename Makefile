# ===================================================================
# Docker
# ===================================================================

start:
	docker compose up
start-build:
	docker compose up --build
stop:
	docker compose down
restart:
	docker compose down && docker compose up
rebuild:
	docker compose down && docker compose up --build

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
