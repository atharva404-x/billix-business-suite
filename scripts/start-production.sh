#!/usr/bin/env sh
# ==============================================================================
# Billix Production Startup Entrypoint Script
# Executes Alembic database migrations and launches Uvicorn web server
# ==============================================================================
set -e

echo "[Billix Startup] Initializing production environment..."

# 1. Run Alembic Database Migrations
echo "[Billix Startup] Executing Alembic database migrations..."
alembic upgrade head
echo "[Billix Startup] Database migrations completed successfully."

# 2. Launch Multi-Worker Uvicorn Production Web Server
WORKERS=${WEB_CONCURRENCY:-4}
PORT=${PORT:-8000}

echo "[Billix Startup] Starting Uvicorn server on port ${PORT} with ${WORKERS} workers..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --workers "${WORKERS}" \
    --log-config /dev/null
