# --- Stage 1: Build dependencies ---
# 💡 FIX: Updated target to use the valid python3.11-alpine tag
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

# --- Stage 2: Production runtime ---
# 💡 FIX: Changed the final stage to match the alpine base layer architecture
FROM python:3.11-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "uvicorn", "tab_groups_proj.main:app", "--host", "0.0.0.0", "--port", "8080"]
