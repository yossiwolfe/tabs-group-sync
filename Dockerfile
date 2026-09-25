# --- Stage 1: Build dependencies ---
FROM ghcr.io/astral-sh/uv:python3.11-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project specifications
COPY pyproject.toml uv.lock ./

# Synchronize dependencies without the buildkit mount syntax
RUN uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Production runtime ---
FROM python:3.11-slim

WORKDIR /app

# Copy the pre-built virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy source application files
# Line 24: Copy the entire src directory so the subfolders stay intact
COPY src/ /app/src/

# Place virtual environment binaries directly onto the system path
ENV PYTHONPATH="/app/src"

# Bind Uvicorn through python's direct module runner tool to port 8080
CMD ["python", "-m", "uvicorn", "tab_groups_proj.main:app", "--host", "0.0.0.0", "--port", "8080"]