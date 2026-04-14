FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_CACHE_DIR=/root/.cache/uv
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY sb_gateway/ ./sb_gateway/
COPY second_brain_db/ ./second_brain_db/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "sb_gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
