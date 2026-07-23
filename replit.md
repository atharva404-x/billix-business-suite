# Billix

**Billix** is a production-grade, multi-tenant GST Billing, Inventory & Business Management SaaS for Indian SME businesses.

## Project Overview

- **Frontend**: React 19 + TanStack Start (SSR) + TanStack Router + shadcn/ui + Tailwind CSS v4
- **Backend**: FastAPI + SQLAlchemy 2.0 (async) + Alembic + PostgreSQL (Neon)
- **Auth**: Clerk
- **Storage**: Appwrite (file/blob storage — logo, invoice PDFs)
- **Monitoring**: Sentry

## How to Run

### Frontend

```bash
npm install
npm run dev
```

The dev server starts on port 5173 (Vite).

### Backend

The FastAPI backend lives in `app/`. The original Windows start script (`scripts/start-backend.ps1`) is not usable on Linux/Replit. To run the backend:

```bash
pip install fastapi uvicorn sqlalchemy[asyncio] alembic asyncpg python-jose httpx
uvicorn app.main:app --reload --port 8000
```

Set environment variables (see `.env.example` if present) — at minimum `DATABASE_URL` and Clerk keys.

### Database Migrations

```bash
alembic upgrade head
```

## Project Structure

```
app/               FastAPI backend
  api/v1/          Route handlers (one file per module)
  models/          SQLAlchemy ORM models
  schemas/         Pydantic request/response schemas
  repositories/    DB access layer (no business logic)
  services/        Business logic layer
  auth/            Clerk JWT verification + dependencies
  core/            Config, database engine
  utils/           Shared validation helpers
alembic/           Database migrations
docs/              Architecture, roadmap, changelog, AI rules
src/               TanStack Start frontend
```

## Key Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — patterns, folder structure, protected files
- [docs/ROADMAP.md](docs/ROADMAP.md) — milestones and engineering tickets
- [docs/AI_RULES.md](docs/AI_RULES.md) — mandatory rules for AI assistants
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — completed ticket history

## User Preferences

- Follow the layered architecture strictly: Router → Service → Repository → Model.
- Never skip layers or duplicate logic across layers.
- Always update `docs/CHANGELOG.md` after completing any engineering ticket.
- Keep tenant isolation enforced on every domain table via `business_id`.
