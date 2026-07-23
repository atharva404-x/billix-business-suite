# ==============================================================================
# Billix Backend Production Dockerfile
# Multi-stage build for minimal image size and enhanced security
# ==============================================================================

# --- Stage 1: Builder ---
FROM python:3.13-slim AS builder

WORKDIR /build

# Install system build tools if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependency manifests
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Runtime ---
FROM python:3.13-slim AS runtime

LABEL maintainer="Billix Engineering <devops@billix.app>"
LABEL description="Billix SaaS Billing & Inventory Platform FastAPI Backend"

WORKDIR /app

# Install runtime system libraries (libpq for Postgres) and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user and group
RUN groupadd -g 10001 billix && \
    useradd -u 10001 -g billix -s /bin/false -m billix

# Copy virtualenv from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code and Alembic configurations
COPY --chown=billix:billix app/ ./app/
COPY --chown=billix:billix alembic/ ./alembic/
COPY --chown=billix:billix alembic.ini .

# Set environment defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Switch to non-root user
USER billix:billix

EXPOSE 8000

# Healthcheck targeting public /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Launch Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
