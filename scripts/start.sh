#!/bin/sh
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Seeding demo data..."
uv run python scripts/seed.py || echo "Seed already applied, skipping."

echo "Starting server..."
exec uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000
