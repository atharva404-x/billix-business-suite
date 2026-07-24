# Billix — Architecture

> Canonical architecture reference for all AI assistants. Read before any structural change.
> See [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) for stack and status, [AI_RULES.md](./AI_RULES.md) for constraints.

---

## 1. Complete Folder Structure

### Frontend (this repository)

```
project/
├─ docs/                       # Project documentation (this folder)
│  ├─ PROJECT_CONTEXT.md
│  ├─ ARCHITECTURE.md
│  ├─ ROADMAP.md
│  ├─ AI_RULES.md
│  └─ CHANGELOG.md
├─ public/
│  └─ favicon.ico
├─ src/
│  ├─ components/
│  │  ├─ auth/                 # Auth screen layouts (e.g. AuthLayout)
│  │  ├─ common/               # Shared presentational widgets (KPI, toolbar, empty state, etc.)
│  │  ├─ layout/               # App shell, sidebar, topbar, page header
│  │  └─ ui/                   # shadcn/ui primitives (button, card, dialog, …)
│  ├─ hooks/
│  │  └─ use-mobile.tsx
│  ├─ lib/
│  │  ├─ error-capture.ts      # SSR error capture for h3-swallowed errors
│  │  ├─ error-page.ts         # Static HTML fallback page
│  │  ├─ lovable-error-reporting.ts
│  │  ├─ mock-data.ts          # Demo/seed data — DO NOT use in production paths
│  │  └─ utils.ts              # cn() helper
│  ├─ routes/                  # TanStack Router file-based routes
│  │  ├─ __root.tsx            # Root layout — DO NOT remove <Outlet />
│  │  ├─ index.tsx             # Landing page
│  │  ├─ login.tsx, register.tsx, forgot-password.tsx
│  │  ├─ dashboard.tsx
│  │  ├─ invoices.tsx, invoices.new.tsx, invoices.$id.tsx
│  │  ├─ customers.tsx, suppliers.tsx
│  │  ├─ products.tsx, categories.tsx, inventory.tsx
│  │  ├─ analytics.tsx, reports.tsx
│  │  ├─ business-profiles.tsx
│  │  ├─ settings.tsx, profile.tsx
│  │  └─ README.md             # Routing conventions
│  ├─ routeTree.gen.ts         # AUTO-GENERATED — never edit by hand
│  ├─ router.tsx               # Router + QueryClient factory
│  ├─ server.ts                # SSR entry wrapper (error normalization)
│  ├─ start.ts                 # TanStack Start config + middleware
│  └─ styles.css               # Tailwind v4 theme + design tokens
├─ .lovable/project.json
├─ components.json             # shadcn/ui config (new-york, slate)
├─ eslint.config.js
├─ prettier config / tsconfig / vite.config.ts
└─ package.json
```

### Backend (separate repository — target structure)

```
backend/
├─ app/
│  ├─ main.py                  # FastAPI app factory
│  ├─ core/                     # Config, settings, security, logging
│  │  └─ config.py
│  ├─ auth/                     # Clerk integration, middleware, dependencies
│  ├─ models/                   # SQLAlchemy ORM models (one module per domain)
│  ├─ schemas/                  # Pydantic v2 request/response schemas
│  ├─ api/                      # API routers (one per domain)
│  │  └─ v1/
│  ├─ services/                 # Business logic layer
│  ├─ repositories/             # Data access layer
│  ├─ middleware/               # Auth, tenant, error, request-id middleware
│  └─ utils/
├─ alembic/                     # Migrations
│  ├─ versions/
│  └─ env.py
├─ tests/
│  ├─ unit/
│  └─ integration/
├─ requirements.txt / pyproject.toml
└─ .env.example
```

---

## 2. Backend Architecture

### Layering (strict, top-down only)

```
API routers (app/api/v1)
      ↓
Services / use cases (app/services)
      ↓
Repositories / data access (app/repositories)
      ↓
Models / ORM (app/models)  ←  Alembic migrations
```

- **Routers** validate input via Pydantic schemas, call services, return responses. No business logic.
- **Services** orchestrate business rules, transactions, and cross-module coordination. No HTTP awareness.
- **Repositories** encapsulate SQLAlchemy queries. No business rules.
- **Models** declare tables and relationships only.

### Principles

- Dependency injection via FastAPI `Depends`.
- Async-first (`async def`, async SQLAlchemy sessions).
- All write paths go through Alembic migrations — never `Base.metadata.create_all` in production.
- Every domain module is self-contained and loosely coupled.

---

## 3. Frontend Architecture

### Routing

- File-based via TanStack Router (`src/routes/`).
- `__root.tsx` is the only root layout. It wraps `<Outlet />` with `QueryClientProvider`.
- Do **not** create `src/pages/`, `_app/index.tsx`, or `app/layout.tsx` — those are Next.js / Remix conventions.
- `routeTree.gen.ts` is auto-generated. Never edit by hand.

### Component Layers

| Layer               | Purpose                                            | Examples                                      |
| ------------------- | -------------------------------------------------- | --------------------------------------------- |
| `components/ui`     | shadcn/ui primitives — do not fork unless required | Button, Card, Dialog                          |
| `components/common` | Shared presentational widgets                      | KpiCard, DataToolbar, EmptyState, StatusBadge |
| `components/layout` | App shell, sidebar, topbar, page header            | AppShell, AppSidebar, PageHeader              |
| `components/auth`   | Auth screen layouts                                | AuthLayout                                    |
| `routes/*`          | Page-level components wired to routes              | dashboard.tsx, invoices.tsx                   |

### Data Fetching

- TanStack React Query for server state.
- Router context carries the `QueryClient` (see `src/router.tsx`).
- Mock data lives in `src/lib/mock-data.ts` and is for scaffolding only — production paths must use real API + Query.

### Styling

- TailwindCSS v4 with design tokens defined in `src/styles.css` using `oklch` colors.
- Theme: `@theme inline` maps CSS variables to Tailwind utilities.
- Fonts: Inter (sans) + Plus Jakarta Sans (display), loaded via Google Fonts in `__root.tsx`.
- Dark mode via `.dark` class on `<html>` (toggled in `AppTopbar`).
- shadcn/ui config: `new-york` style, `slate` base, `lucide` icons.

### SSR / Error Handling

- `src/server.ts` wraps the SSR entry and normalizes catastrophic h3-swallowed errors into a static HTML fallback (`src/lib/error-page.ts`).
- `src/lib/error-capture.ts` records the original error out-of-band so `server.ts` can recover the stack.
- `src/start.ts` adds server middleware that renders the same fallback on uncaught server errors.
- Root route defines `errorComponent` and `notFoundComponent`.

---

## 4. Database Architecture

- **Engine:** PostgreSQL on Neon (serverless Postgres).
- **ORM:** SQLAlchemy 2.0 (async).
- **Migrations:** Alembic — every schema change is a versioned migration. No manual schema drift.
- **Multi-tenancy:** every domain table is scoped by `business_id` (tenant). See Milestone 4.
- **Soft deletes:** domain entities use `is_active` / `deleted_at` where applicable; never hard-delete user data.
- **Timestamps:** all tables carry `created_at`, `updated_at` (UTC, timezone-aware).
- **IDs:** prefer `UUID` primary keys for public entities; sequential IDs allowed for internal/lookup tables.
- **Indexes:** add indexes for every foreign key and for columns used in filter/sort UI.

---

## 5. Authentication Architecture

- **Provider:** Clerk (frontend SDK + backend verification).
- **Frontend:** Clerk React SDK wraps the app; protected routes use Clerk's auth state.
- **Backend:** verify Clerk JWT in middleware (`AUTH-004`), expose `current_user` dependency (`AUTH-005`).
- **Roles:** defined in `AUTH-006` (Owner, Accountant, Cashier, etc.). Enforced in routers and services.
- **Sessions:** Clerk-managed. Billix never stores passwords.
- **Multi-tenant:** a Clerk user may belong to multiple `business_profiles`; the active profile is selected client-side and passed as a header / context to the backend.

---

## 6. Design Patterns

- **Layered architecture** (API → Service → Repository → Model) on the backend.
- **Repository pattern** for data access.
- **Dependency injection** via FastAPI `Depends`.
- **DTO / Schema separation** — Pydantic schemas never leak ORM models.
- **Module-per-domain** — customers, suppliers, products, inventory, invoices, payments are independent modules.
- **Composition over inheritance** — share behavior via small services and helpers, not base classes.
- **Server-driven UI state** — the backend is the source of truth; the frontend reflects it via React Query.
- **Error boundaries** — root route `errorComponent` + SSR fallback page.

---

## 7. Naming Conventions

### Frontend

- **Files:** `kebab-case.tsx` for routes and components; `PascalCase` only for component exports.
- **Components:** `PascalCase` (e.g. `KpiCard`, `AppShell`).
- **Hooks:** `useThing` (`use-mobile.tsx` → `useIsMobile`).
- **Routes:** file-based — `invoices.new.tsx` → `/invoices/new`, `invoices.$id.tsx` → `/invoices/:id`.
- **CSS:** Tailwind utilities + design tokens from `styles.css`. No inline color literals — use tokens.

### Backend

- **Files:** `snake_case.py`.
- **Classes:** `PascalCase` (e.g. `User`, `CustomerRepository`).
- **Functions / variables:** `snake_case`.
- **Constants:** `UPPER_SNAKE_CASE`.
- **Tables:** plural `snake_case` (e.g. `users`, `business_profiles`, `invoices`).
- **Columns:** `snake_case` (e.g. `business_id`, `created_at`).

---

## 8. Coding Standards

- **TypeScript:** strict mode (see `tsconfig.json`). No `any` without justification.
- **Python:** type hints required everywhere; `mypy`/`ruff` clean.
- **SOLID:** every class/module has a single responsibility; depend on abstractions at module boundaries.
- **DRY:** reuse `components/common`, `lib/utils`, and backend services/repositories before adding new code.
- **No dead code:** delete what you replace; no `_old` files, no commented-out blocks.
- **No premature abstraction:** introduce a shared helper only with ≥2 concrete call sites.
- **Error handling:** validate at system boundaries (HTTP input, external APIs); trust internal code.
- **Comments:** default to none. Add a comment only when the _why_ is non-obvious.
- **Tests:** every backend ticket ships with unit + integration tests (`AUTH-008` sets the pattern).
- **Commits:** one ticket per commit/PR. Reference the ticket ID in the message.

---

## 9. Dependency Flow

```
Clerk (identity) ──► Frontend (React/TanStack) ──► FastAPI (auth middleware)
                                                            │
                                                            ▼
                                                   Services / Repos
                                                            │
                                                            ▼
                                                   PostgreSQL (Neon)
                                                            │
                                                            ▼
                                                   Appwrite (file storage)

Sentry observes Frontend + Backend end-to-end.
Vercel serves the frontend build; DigitalOcean runs the FastAPI backend.
```

- The frontend never talks to PostgreSQL directly.
- The backend never trusts a request without a verified Clerk JWT.
- Appwrite is used only for file/blob storage (e.g. invoice PDFs, logos), never as a primary database.

---

## 10. Project Principles

1. **Production-quality only.** No demo code, no throwaway scripts, no `console.log` left in committed code.
2. **One ticket at a time.** Do not implement future milestones or unrelated features.
3. **Reuse before you add.** Search existing components/services before creating new ones.
4. **Loose coupling.** Domain modules communicate via services, not by importing each other's internals.
5. **Migrations are immutable.** Never edit a shipped Alembic migration; always add a new one.
6. **User data is sacred.** No destructive operations without explicit confirmation and reversibility.
7. **Security by default.** RLS on every Supabase table, auth on every backend route, validation on every input.
8. **Explain every change.** Update `CHANGELOG.md` and reference the ticket ID.
9. **Ask, don't assume.** Ambiguity → clarification, not invention.

---

## 11. Files & Folders That Must Never Be Modified Without Approval

> Any change to the items below requires explicit approval. They are load-bearing or auto-generated.

### Frontend

- `src/routeTree.gen.ts` — auto-generated by TanStack Router.
- `src/routes/__root.tsx` — root layout; removing `<Outlet />` breaks all routes.
- `src/server.ts`, `src/start.ts` — SSR entry + error normalization; breaking these breaks SSR.
- `src/lib/error-capture.ts`, `src/lib/error-page.ts` — SSR error recovery.
- `src/styles.css` — design token source of truth; changes ripple across the whole UI.
- `components.json` — shadcn/ui registry config.
- `vite.config.ts` — build pipeline; `@lovable.dev/vite-tanstack-config` already wires required plugins.
- `tsconfig.json`, `eslint.config.js`, `.prettierrc` — project-wide tooling.
- `.lovable/project.json` — project metadata.
- `package.json`, lockfiles (`bun.lock`, `package-lock.json`) — dependency manifests.

### Backend (target repo)

- `app/core/config.py` — environment + secrets.
- `alembic/env.py` and any committed migration in `alembic/versions/` — immutable history.
- `.env`, `.env.example` — secrets and contract for env vars.

### Documentation

- `docs/PROJECT_CONTEXT.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/AI_RULES.md` — change only via an approved documentation ticket.
- `docs/CHANGELOG.md` — append-only; never rewrite past entries.

---

## 12. Cross-References

- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) — what Billix is and where it is today.
- [ROADMAP.md](./ROADMAP.md) — milestones and engineering tickets.
- [AI_RULES.md](./AI_RULES.md) — mandatory rules for every AI session.
- [CHANGELOG.md](./CHANGELOG.md) — chronological ticket history.
