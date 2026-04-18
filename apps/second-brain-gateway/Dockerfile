FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

ENV UV_CACHE_DIR=/root/.cache/uv
ENV UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y
    && apt-get install -y --only-upgrade openssl libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Install sources package
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=apps,target=apps \
    uv sync --locked --no-editable --package second-brain-gateway \
    && rm -rf packages

ENV PATH="/app/.venv/bin:$PATH"

COPY migrations ./migrations/
COPY alembic.ini ./

# Copy the service source code
COPY apps/second-brain-gateway/*.py ./
COPY apps/second-brain-gateway/routers ./routers
COPY apps/second-brain-gateway/models ./models
COPY apps/second-brain-gateway/dependencies ./dependencies

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
