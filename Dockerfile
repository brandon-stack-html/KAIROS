# ── Stage 1: build dependencies ──────────────────────────────────────
FROM python:3.12-slim AS builder

# uv is the package manager used by this project
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock* README.md* ./

# Install into a virtual env inside /app/.venv
RUN uv sync --frozen --no-dev --no-editable

# ── Stage 2: runtime image ────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy only the virtualenv and source from the builder
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

# Create uploads dir with correct ownership before dropping to app user
RUN mkdir -p /app/uploads && chown app:app /app/uploads

# Make sure the venv's bin is on PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 8000

COPY alembic/ ./alembic/
COPY alembic.ini ./alembic.ini

COPY scripts/ ./scripts/

CMD ["sh", "scripts/start.sh"]
