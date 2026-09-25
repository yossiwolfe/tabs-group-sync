# --- Stage 1: Build & Sync dependencies ---
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for faster application start times
ENV UV_COMPILE_BYTECODE=1

# Copy only the files needed to install dependencies (leveraging Docker cache)
COPY pyproject.toml uv.lock ./

# Synchronize the project dependencies safely (creates the local .venv)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Final lightweight runtime container ---
FROM python:3.11-alpine

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy your actual source code into the container
COPY src/ /app/src/

# Place the virtual environment's executables directly onto the system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Disable Python output buffering to ensure logs appear instantly in Google Cloud Logging
ENV PYTHONUNBUFFERED=1

# Cloud Run injects a variable called PORT. We bind Uvicorn to 0.0.0.0 and pass $PORT dynamically.
CMD ["uvicorn", "tabs_proj.main:app", "--host", "0.0.0.0", "--port", "8080"]
