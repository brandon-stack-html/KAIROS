#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding demo data..."
python scripts/seed.py || echo "Seed already applied or failed, skipping."

echo "Starting server..."
exec uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000
