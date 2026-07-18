# Billix — Project Context

> Single source of truth for every AI assistant (Bolt AI, Cursor, Claude, ChatGPT, Jules, Trae, etc.) working on Billix.
> Read this document BEFORE writing any code or proposing any change.

---

## 1. Project Overview

**Billix** is a production-ready, cloud-based **GST Billing, Inventory & Business Management SaaS** built for Indian retail, wholesale, medical, hardware and SME businesses.

Billix allows a business owner to:
- Raise GST-compliant tax invoices (HSN, e-invoice, e-way bill ready).
- Manage live inventory across branches (batch, expiry, low-stock alerts).
- Track customers, suppliers, payables and receivables.
- Generate GST filings (GSTR-1, GSTR-3B, HSN summary) and P&L reports.
- Operate multiple GSTINs / branches from a single login.

Billix is **not** a demo, tutorial, or college project. It is engineered as production-quality software and must be treated as such at all times.

---

## 2. Purpose

Provide Indian businesses with a calm, modern, reliable workspace that replaces fragmented billing, inventory and accounting tools with a single, GST-compliant platform.

---

## 3. Core Features (Target State)

| Domain | Capability |
| --- | --- |
| Auth | Clerk-based identity, role-based access, multi-user teams |
| Multi-tenant | Multiple business profiles (GSTINs / branches) per account |
| Customers | B2B/B2C, GSTIN, credit limits, outstanding balances |
| Suppliers | Vendors, purchase orders, payables |
| Products | SKU catalogue, HSN, GST rate, units, categories |
| Inventory | Live stock, batch/expiry, low-stock alerts, stock transfers |
| Invoices | GST tax invoices, e-invoice (IRN), e-way bill, thermal print |
| Payments | UPI / cash / card / bank / credit tracking |
| Reports | GSTR-1, GSTR-3B, GSTR-2B, HSN summary, P&L, sales vs purchase |
| Settings | Business, invoice, tax, team, notifications, plan & billing |

---

## 4. Tech Stack

### Frontend
- React 19
- TypeScript
- Vite
- TanStack Router (file-based routing)
- TanStack Start (SSR)
- TanStack React Query
- TailwindCSS v4
- shadcn/ui (New York style, slate base)
- lucide-react icons
- recharts (charts)
- react-hook-form + zod

### Backend
- FastAPI
- Python 3.13+
- SQLAlchemy 2.0
- Alembic (migrations)
- PostgreSQL (Neon)

### Authentication
- Clerk

### Storage
- Appwrite

### Monitoring
- Sentry

### Deployment
- Frontend → Vercel
- Backend → DigitalOcean

> Note: The current repository state contains the **frontend** scaffold (TanStack Start + shadcn/ui). The FastAPI backend, Clerk wiring, Appwrite storage, and Sentry monitoring are referenced here as the canonical target stack per the project plan. Backend code lives in a separate repository unless otherwise instructed.

---

## 5. Deployment Architecture

```
                ┌──────────────────────────┐
                │        Vercel (FE)        │
                │   TanStack Start (SSR)    │
                └─────────────┬─────────────┘
                              │ HTTPS
              ┌───────────────┴───────────────┐
              │                                 │
              ▼                                 ▼
   ┌────────────────────┐            ┌────────────────────┐
   │  DigitalOcean (BE) │            │   Clerk (Auth)     │
   │  FastAPI + Uvicorn │            └────────────────────┘
   └─────────┬──────────┘
             │
   ┌─────────┴──────────┐
   │                    │
   ▼                    ▼
┌──────────┐    ┌──────────────┐
│ Neon DB  │    │  Appwrite    │
│ Postgres │    │  (Storage)   │
└──────────┘    └──────────────┘

Sentry observes FE + BE for error tracking.
```

---

## 6. Current Project Status

### Completed
- **Milestone 1 — Backend Foundation**
- **Milestone 2 — Database Infrastructure**
- **Milestone 3 (partial) — Identity & Authentication Foundation**
  - `AUTH-001` Clerk Configuration — Completed

### Current Milestone
- **Milestone 3 — Identity & Authentication Foundation**

### Upcoming Engineering Tickets
| Ticket | Title |
| --- | --- |
| AUTH-002 | Backend Clerk Integration |
| AUTH-003 | User Model |
| AUTH-004 | Authentication Middleware |
| AUTH-005 | Current User Dependency |
| AUTH-006 | Role Foundation |
| AUTH-007 | Protected Routes |
| AUTH-008 | Authentication Testing |

---

## 7. High-Level Roadmap

See [ROADMAP.md](./ROADMAP.md) for the full milestone breakdown, engineering tickets, dependencies, and completion criteria.

| Milestone | Theme |
| --- | --- |
| 1 | Backend Foundation |
| 2 | Database Infrastructure |
| 3 | Identity & Authentication |
| 4 | Multi-Tenant Business Foundation |
| 5 | Customer Module |
| 6 | Supplier Module |
| 7 | Product Module |
| 8 | Inventory Module |
| 9 | Invoice Module |
| 10 | Payments |
| 11 | Reports & Analytics |
| 12 | Deployment |

---

## 8. AI Project Overview

This project is operated by AI assistants across multiple tools (Bolt AI, Cursor, Claude, ChatGPT, Jules, Trae, etc.). To keep the codebase coherent across sessions and assistants:

- **Always read** `docs/AI_RULES.md` before starting any work.
- **Always read** `docs/ARCHITECTURE.md` before proposing structural changes.
- **Always check** `docs/CHANGELOG.md` for prior work on the same area.
- **Always scope** your work to exactly one engineering ticket.
- **Never assume** — ask for clarification when a requirement is ambiguous.
- **Never redesign** the architecture or move files between modules without approval.

### Companion Documents
- [ARCHITECTURE.md](./ARCHITECTURE.md) — structure, patterns, conventions
- [ROADMAP.md](./ROADMAP.md) — milestones and tickets
- [AI_RULES.md](./AI_RULES.md) — mandatory rules for every AI session
- [CHANGELOG.md](./CHANGELOG.md) — ticket history and decisions log
