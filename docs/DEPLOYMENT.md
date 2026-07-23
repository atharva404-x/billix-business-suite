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

## 6. Continuous Integration & Deployment (CI/CD)

Billix includes production-grade GitHub Actions workflows located in `.github/workflows/`:

- **CI Pipeline (`.github/workflows/ci.yml`)**: Automated pipeline triggered on every Pull Request and Push to `main`.
  - Runs Python 3.13 unit test suite (`pytest`).
  - Validates Alembic migration integrity (`alembic upgrade head`).
  - Runs ESLint, TypeScript type checking (`tsc --noEmit`), and Vite production builds.
  - Verifies multi-stage Docker builds (`Dockerfile` and `Dockerfile.frontend`).
- **CD Pipeline (`.github/workflows/deployment.yml`)**: Prepared deployment pipeline triggered via `workflow_dispatch` (manual trigger with `staging`/`production` selection) or GitHub Release tags (`v*`).

---

## 7. Required GitHub Secrets

To enable automated CD deployment to staging or production servers, configure the following secrets in GitHub Repository Settings (`Settings -> Secrets and variables -> Actions`):

### Container Registry & Code Access
| Secret Name | Description | Example / Note |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | Built-in GitHub Actions token for GHCR package publishing | Auto-provided |

### Server Deployment Secrets
| Secret Name | Description | Example / Note |
| :--- | :--- | :--- |
| `DEPLOY_HOST` | Production or Staging server IP address or FQDN | `203.0.113.10` |
| `DEPLOY_USER` | SSH user for container orchestration | `deploy` or `root` |
| `DEPLOY_SSH_KEY` | Private SSH key authorized on `DEPLOY_HOST` | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### Application Environment Secrets
| Secret Name | Description | Example / Note |
| :--- | :--- | :--- |
| `DATABASE_URL` | Production PostgreSQL connection string | `postgresql+asyncpg://...` |
| `POSTGRES_PASSWORD` | PostgreSQL secret password | `secret_db_password` |
| `CLERK_PUBLISHABLE_KEY` | Clerk Auth publishable key | `pk_live_...` |
| `CLERK_SECRET_KEY` | Clerk Auth secret key | `sk_live_...` |

