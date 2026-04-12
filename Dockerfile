# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY sb_gateway/ ./sb_gateway/
COPY second_brain_db/ ./second_brain_db/

# Expose port 8000
EXPOSE 8000

# Run FastAPI application
CMD ["uv", "run", "uvicorn", "sb_gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
