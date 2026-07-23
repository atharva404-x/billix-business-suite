# Billix — Deployment & Containerization Guide

This document is the canonical reference for building, running, and deploying the Billix SaaS Platform using Docker and Docker Compose.

---

## 1. Overview & Architecture

Billix uses a multi-container architecture separated into frontend, backend, database, and cache services:

- **Backend**: FastAPI running on Python 3.13-slim with Uvicorn.
- **Frontend**: React/Vite/TanStack Start built static assets served via high-performance Nginx Alpine.
- **Database**: PostgreSQL 16 Alpine database using `asyncpg` driver for production.
- **Cache**: Redis 7 Alpine cache and message broker.

```
                  ┌────────────────────────┐
                  │   Nginx (Frontend)     │
                  │   Port 80 / Port 443   │
                  └───────────┬────────────┘
                              │ HTTP / Static
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌────────────────────┐          ┌────────────────────┐
    │  FastAPI Backend   │          │   Clerk (Auth)     │
    │     Port 8000      │          └────────────────────┘
    └─────────┬──────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌──────────┐    ┌──────────────┐
│ Postgres │    │    Redis     │
│ Port 5432│    │  Port 6379   │
└──────────┘    └──────────────┘
```

---

## 2. Environment Variables

Copy `.env.example` to `.env` before starting services:

```bash
cp .env.example .env
```

### Key Environment Variables

| Variable | Description | Default | Required in Production |
| :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | Service display name | `Billix` | No |
| `ENV` | Environment identifier (`development`, `production`) | `development` | Yes |
| `PORT` | Backend binding port | `8000` | No |
| `DATABASE_URL` | Async PostgreSQL connection URI | `postgresql+asyncpg://...` | **Yes** |
| `POSTGRES_DB` | PostgreSQL database name | `billix_db` | **Yes** |
| `POSTGRES_USER` | PostgreSQL user | `billix_user` | **Yes** |
| `POSTGRES_PASSWORD` | PostgreSQL secret password | `billix_password` | **Yes** |
| `REDIS_URL` | Redis URI | `redis://localhost:6379/0` | **Yes** |
| `CLERK_PUBLISHABLE_KEY` | Clerk Auth publishable key | `pk_test_...` | **Yes** |
| `CLERK_SECRET_KEY` | Clerk Auth secret key | `sk_test_...` | **Yes** |
| `CLERK_JWKS_URL` | Clerk JWKS endpoint URI | `https://api.clerk.com/...` | **Yes** |
| `CLERK_JWT_AUDIENCE` | Expected JWT audience | `""` | Recommended |
| `VITE_API_BASE_URL` | Public API URL for Frontend | `http://localhost:8000` | **Yes** |

---

## 3. Local Development with Docker Compose

To spin up the entire development stack (Backend with hot-reload, Frontend, PostgreSQL, Redis):

```bash
# Start all development services in foreground
docker compose up

# Build and start in background (detached mode)
docker compose up -d --build

# View logs for backend
docker compose logs -f backend

# Stop development stack
docker compose down
```

### Access Points (Development)
- **Frontend App**: `http://localhost:80`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` or `http://localhost:8000/redoc`
- **Health check**: `http://localhost:8000/health`
- **Readiness check**: `http://localhost:8000/ready`

---

## 4. Production Container Build & Orchestration

### Building Production Docker Images

#### Backend Production Docker Image
```bash
docker build -t billix/backend:latest -f Dockerfile .
```

#### Frontend Production Docker Image
```bash
docker build -t billix/frontend:latest -f Dockerfile.frontend .
```

### Launching Production Stack with `docker-compose.prod.yml`

```bash
# Build and launch production stack in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# Verify running container status and healthchecks
docker compose -f docker-compose.prod.yml ps

# Inspect production container logs
docker compose -f docker-compose.prod.yml logs -f

# Tear down production stack
docker compose -f docker-compose.prod.yml down
```

---

## 5. Security & Best Practices

1. **Non-Root Execution**: The backend runtime container executes under unprivileged system user `billix:10001`.
2. **Multi-Stage Builds**: Build-time tools (compilers, git, dev dependencies) are stripped out of final runtime images.
3. **Healthchecks**: Built-in HTTP and CLI healthchecks enable automated container restarts and zero-downtime orchestration.
4. **Secret Protection**: All credentials are supplied dynamically through `.env` and are strictly excluded from repository commits by `.gitignore`.
