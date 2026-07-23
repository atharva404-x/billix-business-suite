# Billix — Production Deployment & Operations Guide

This document is the canonical reference for building, configuring, deploying, and validating the Billix SaaS Platform across production cloud infrastructure.

---

## 1. Cloud Architecture Overview

Billix operates a decoupled, cloud-native deployment model:

```
                ┌──────────────────────────┐
                │       Vercel (FE)        │
                │ React 19 + TanStack SSR  │
                └─────────────┬────────────┘
                              │ HTTPS
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌────────────────────┐          ┌────────────────────┐
    │ DigitalOcean /     │          │   Clerk (Auth)     │
    │ Render Backend     │          └────────────────────┘
    │ FastAPI + Uvicorn  │
    └─────────┬──────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌──────────┐    ┌──────────────┐
│  Neon DB │    │ Redis Cache  │
│ Postgres │    └──────────────┘
└──────────┘

Sentry observes FE + BE for error tracking and APM.
```

---

## 2. Frontend Deployment (Vercel)

1. Connect the Git repository to Vercel.
2. Select **Vite** project preset.
3. Configure Vercel build settings:
   - **Framework**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `.output/public`
4. Set Environment Variables in Vercel Dashboard:
   - `VITE_API_BASE_URL`: `https://api.billix.app`
   - `VITE_CLERK_PUBLISHABLE_KEY`: `pk_live_your_clerk_publishable_key`
5. The included `vercel.json` automatically configures routing rewrites and static asset caching.

---

## 3. Backend Cloud Deployment (DigitalOcean / Render)

### Option A: Render Cloud Deployment
1. Connect repository to Render.
2. Render detects `render.yaml` automatically and provisions:
   - `billix-backend` Python Web Service (`/health` health check path).
   - `billix-redis` Redis Instance.
3. Supply required environment variables (`DATABASE_URL`, `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY`).

### Option B: DigitalOcean App Platform
1. Select DigitalOcean App Platform and import `digitalocean.yaml`.
2. Configure environment variables in App Platform Settings.
3. DigitalOcean builds the multi-stage `Dockerfile` and deploys containerized instances automatically.

---

## 4. Neon PostgreSQL Database Setup

1. Create a PostgreSQL project on [Neon.tech](https://neon.tech).
2. Copy the Pooled Connection String (`postgresql+asyncpg://...`).
3. Ensure the connection string includes `sslmode=require` or `.neon.tech` domain name.
4. `app/core/database.py` automatically injects `connect_args={"ssl": "require"}` and configures pool options (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`).
5. Run migrations:
   ```bash
   alembic upgrade head
   ```

---

## 5. Environment Variables Inventory

Copy `.env.example` to `.env` for local configuration.

| Variable | Description | Production Example | Required |
| :--- | :--- | :--- | :--- |
| `ENV` | Environment mode | `production` | Yes |
| `PROJECT_NAME` | Application name | `Billix` | Yes |
| `PORT` | Backend port | `8000` | No |
| `DATABASE_URL` | Neon PostgreSQL async URI | `postgresql+asyncpg://user:pass@ep-...neon.tech/billix?sslmode=require` | **Yes** |
| `REDIS_URL` | Redis instance connection URI | `redis://...:6379/0` | **Yes** |
| `CLERK_PUBLISHABLE_KEY` | Clerk Publishable Key | `pk_live_...` | **Yes** |
| `CLERK_SECRET_KEY` | Clerk Secret Key | `sk_live_...` | **Yes** |
| `CLERK_JWKS_URL` | Clerk JWKS Endpoint | `https://api.clerk.com/v1/.well-known/jwks.json` | **Yes** |
| `LOG_LEVEL` | Logging level | `INFO` | Yes |
| `LOG_FORMAT` | Log format | `json` | Yes |
| `SENTRY_DSN` | Sentry DSN | `https://...` | Optional |

---

## 6. Continuous Integration & Deployment (CI/CD)

- **CI Pipeline (`.github/workflows/ci.yml`)**: Automated pipeline triggered on every Pull Request and Push to `main`.
  - Runs unit tests (`pytest`), Alembic dry-run migrations, ESLint, TypeScript type checking, and Docker image builds.
- **CD Pipeline (`.github/workflows/deployment.yml`)**: Prepared deployment workflow building, tagging, and pushing Docker images to GitHub Container Registry (`ghcr.io`).

---

## 7. Production Validation Checklist

Run through this checklist prior to launching in production:

- [x] **Docker**: Multi-stage `Dockerfile` and `Dockerfile.frontend` build cleanly under non-root system users.
- [x] **CI/CD**: GitHub Actions workflows (`ci.yml` and `deployment.yml`) pass with zero syntax or test errors.
- [x] **Logging**: Structured JSON logging (`app/core/logging.py`) configured with `request_id` and `correlation_id` contextvars.
- [x] **Sentry**: Sentry SDK initialization (`app/core/sentry.py`) configured with sensitive header redaction (`before_send`).
- [x] **Health Checks**: `/health` (service health) and `/ready` (active database probe) endpoints active and returning `200 OK`.
- [x] **Rate Limiting**: Sliding-window rate limiting (`RateLimitMiddleware`) enforced per client IP (120 req/min).
- [x] **Security**: Security headers (`X-Frame-Options`, `X-Content-Type-Options`, `CSP`), Request size limit (10MB), CORS hardening, and `TrustedHostMiddleware` enabled.
- [x] **Environment Variables**: All secret credentials documented in `.env.example` and excluded from Git by `.gitignore`.
- [x] **Deployment Configuration**: Cloud specifications (`vercel.json`, `render.yaml`, `digitalocean.yaml`) and production entrypoint script (`scripts/start-production.sh`) verified.
