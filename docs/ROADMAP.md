# Billix — Roadmap

> Full milestone breakdown for Billix. Each milestone lists its objective, engineering tickets, dependencies, and completion criteria.
> See [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) for current status and [AI_RULES.md](./AI_RULES.md) for scoping rules.

> **Rule:** Only the current milestone and its tickets are in scope. Do not implement future milestones.

---

## Milestone 1 — Backend Foundation

### Objective

Stand up the FastAPI backend skeleton, configuration, logging, and project tooling so all later milestones build on a stable base.

### Engineering Tickets

| Ticket      | Title                                                |
| ----------- | ---------------------------------------------------- |
| BE-FOUND-01 | FastAPI app factory + project structure              |
| BE-FOUND-02 | Settings / environment config (`app/core/config.py`) |
| BE-FOUND-03 | Logging + request-id middleware                      |
| BE-FOUND-04 | Error handling + standard response envelope          |
| BE-FOUND-05 | Health check + readiness endpoints                   |
| BE-FOUND-06 | Linting/formatting (ruff, black, mypy) + pre-commit  |

### Dependencies

- None (first milestone).

### Completion Criteria

- `uvicorn app.main:app` boots cleanly.
- `/health` returns 200; `/ready` checks DB connectivity.
- Settings load from `.env` with validation.
- CI runs ruff + mypy + tests green.

---

## Milestone 2 — Database Infrastructure

### Objective

Provision PostgreSQL on Neon, wire SQLAlchemy 2.0 (async), configure Alembic, and establish the baseline schema conventions.

### Engineering Tickets

| Ticket | Title                                                 |
| ------ | ----------------------------------------------------- |
| DB-01  | Neon Postgres provisioning + connection string        |
| DB-02  | SQLAlchemy 2.0 async engine + session factory         |
| DB-03  | Alembic setup + initial migration                     |
| DB-04  | Base model mixins (timestamps, soft delete, UUID PKs) |
| DB-05  | Database health checks + connection pooling           |

### Dependencies

- Milestone 1 (BE-FOUND-02 config).

### Completion Criteria

- App connects to Neon over async SQLAlchemy.
- `alembic upgrade head` runs cleanly.
- Base mixins available for all domain models.
- `/ready` verifies DB connectivity.

---

## Milestone 3 — Identity & Authentication

### Objective

Implement Clerk-based authentication end-to-end: frontend SDK, backend JWT verification, user model, role foundation, protected routes, and tests.

### Engineering Tickets

| Ticket   | Title                     | Status    |
| -------- | ------------------------- | --------- |
| AUTH-001 | Clerk Configuration       | Completed |
| AUTH-002 | Backend Clerk Integration | Upcoming  |
| AUTH-003 | User Model                | Upcoming  |
| AUTH-004 | Authentication Middleware | Upcoming  |
| AUTH-005 | Current User Dependency   | Upcoming  |
| AUTH-006 | Role Foundation           | Upcoming  |
| AUTH-007 | Protected Routes          | Upcoming  |
| AUTH-008 | Authentication Testing    | Upcoming  |

### Dependencies

- Milestone 1 (config, middleware plumbing).
- Milestone 2 (User model needs DB).

### Completion Criteria

- Frontend uses Clerk SDK; sign in / sign up / sign out flows work.
- Backend verifies Clerk JWT on every protected route.
- `current_user` dependency returns the authenticated user.
- Roles (Owner, Accountant, Cashier, …) defined and enforced on at least one route.
- Auth test suite (unit + integration) green.

---

## Milestone 4 — Multi-Tenant Business Foundation

### Objective

Allow a single Clerk user to own/operate multiple business profiles (GSTINs / branches) and scope all downstream data by the active business.

### Engineering Tickets

| Ticket    | Title                                      |
| --------- | ------------------------------------------ |
| TENANT-01 | `business_profiles` model + migration      |
| TENANT-02 | User ↔ Business membership model           |
| TENANT-03 | Active business context (header / session) |
| TENANT-04 | Tenant scoping middleware / dependency     |
| TENANT-05 | Business profile CRUD API                  |
| TENANT-06 | Frontend business switcher + persistence   |

### Dependencies

- Milestone 3 (auth, users, roles).

### Completion Criteria

- A user can create and switch between multiple business profiles.
- All domain queries are scoped by `business_id`.
- Switching business changes the visible dataset across the app.

---

## Milestone 5 — Customer Module

### Objective

Deliver full CRUD + listing + search for B2B/B2C customers, with GSTIN, contact, credit limit, and outstanding balance tracking.

### Engineering Tickets

| Ticket  | Title                           |
| ------- | ------------------------------- |
| CUST-01 | Customer model + migration      |
| CUST-02 | Customer schemas (Pydantic)     |
| CUST-03 | Customer repository + service   |
| CUST-04 | Customer API (CRUD + search)    |
| CUST-05 | Customer list + detail UI       |
| CUST-06 | Customer form (create/edit)     |
| CUST-07 | Outstanding balance computation |
| CUST-08 | Customer tests                  |

### Dependencies

- Milestone 4 (tenant scoping).

### Completion Criteria

- Users can create, edit, list, search, and delete customers.
- Outstanding balance derives from invoices/payments.
- All data scoped by active business.

---

## Milestone 6 — Supplier Module

### Objective

Mirror the Customer module for vendors, with payables tracking.

### Engineering Tickets

| Ticket  | Title                         |
| ------- | ----------------------------- |
| SUPP-01 | Supplier model + migration    |
| SUPP-02 | Supplier schemas              |
| SUPP-03 | Supplier repository + service |
| SUPP-04 | Supplier API (CRUD + search)  |
| SUPP-05 | Supplier list + detail UI     |
| SUPP-06 | Supplier form (create/edit)   |
| SUPP-07 | Payables computation          |
| SUPP-08 | Supplier tests                |

### Dependencies

- Milestone 4 (tenant scoping).

### Completion Criteria

- Full supplier CRUD with payables derived from purchase invoices/payments.

---

## Milestone 7 — Product Module

### Objective

Product/SKU catalogue with HSN codes, GST rates, units, categories, and pricing.

### Engineering Tickets

| Ticket  | Title                                      |
| ------- | ------------------------------------------ |
| PROD-01 | Category model + migration                 |
| PROD-02 | Product model + migration                  |
| PROD-03 | Product schemas                            |
| PROD-04 | Category + product repositories/services   |
| PROD-05 | Category + product APIs                    |
| PROD-06 | Product list + detail UI                   |
| PROD-07 | Category management UI                     |
| PROD-08 | Product form (create/edit, HSN, GST, unit) |
| PROD-09 | Product tests                              |

### Dependencies

- Milestone 4 (tenant scoping).

### Completion Criteria

- Categories and products fully manageable; GST rate and HSN stored per product.

---

## Milestone 8 — Inventory Module

### Objective

Live stock tracking, batch/expiry, low-stock alerts, and stock transfers across branches.

### Engineering Tickets

| Ticket | Title                                                |
| ------ | ---------------------------------------------------- |
| INV-01 | Stock ledger model + migration                       |
| INV-02 | Batch / expiry model (where applicable)              |
| INV-03 | Inventory service (adjust, transfer)                 |
| INV-04 | Low-stock alert rules                                |
| INV-05 | Inventory API (stock levels, movements, adjustments) |
| INV-06 | Inventory dashboard UI                               |
| INV-07 | Stock transfer UI                                    |
| INV-08 | Inventory tests                                      |

### Dependencies

- Milestone 7 (products).
- Milestone 4 (multi-branch).

### Completion Criteria

- Stock levels always reflect latest movements.
- Low-stock alerts fire correctly.
- Transfers move stock between branches atomically.

---

## Milestone 9 — Invoice Module

### Objective

GST-compliant tax invoices with line items, HSN, CGST/SGST/IGST, e-invoice (IRN), e-way bill, and PDF generation.

### Engineering Tickets

| Ticket   | Title                                          |
| -------- | ---------------------------------------------- |
| INVCE-01 | Invoice model + line-item model + migration    |
| INVCE-02 | Invoice numbering / sequence                   |
| INVCE-03 | Invoice schemas                                |
| INVCE-04 | Invoice service (totals, GST split, round-off) |
| INVCE-05 | Invoice API (create, list, detail, cancel)     |
| INVCE-06 | New invoice UI (items, totals, summary)        |
| INVCE-07 | Invoice detail / print UI                      |
| INVCE-08 | e-Invoice (IRN) integration                    |
| INVCE-09 | e-Way bill integration                         |
| INVCE-10 | PDF generation + Appwrite storage              |
| INVCE-11 | Invoice tests                                  |

### Dependencies

- Milestone 5 (customers), 7 (products), 8 (inventory decrements on invoice).

### Completion Criteria

- Users can raise, list, view, cancel, and download GST tax invoices.
- Stock decrements on invoice finalization.
- IRN + e-way bill generation works for eligible invoices.

---

## Milestone 10 — Payments

### Objective

Track payments (UPI, cash, card, bank, credit) against invoices and suppliers; reconcile receivables/payables.

### Engineering Tickets

| Ticket | Title                                     |
| ------ | ----------------------------------------- |
| PAY-01 | Payment model + migration                 |
| PAY-02 | Payment schemas                           |
| PAY-03 | Payment service (allocate to invoices)    |
| PAY-04 | Payment API                               |
| PAY-05 | Payment capture UI (invoice + standalone) |
| PAY-06 | Receivables / payables dashboard          |
| PAY-07 | Payment tests                             |

### Dependencies

- Milestone 9 (invoices), 6 (suppliers).

### Completion Criteria

- Payments link to invoices/suppliers and update outstanding balances.
- Receivables/payables dashboard reflects real-time state.

---

## Milestone 11 — Reports & Analytics

### Objective

Deliver GST filings (GSTR-1, GSTR-3B, GSTR-2B, HSN summary), P&L, sales vs purchase, and analytics dashboards.

### Engineering Tickets

| Ticket | Title                                 |
| ------ | ------------------------------------- |
| RPT-01 | Reporting service layer (read models) |
| RPT-02 | GSTR-1 report + export                |
| RPT-03 | GSTR-3B report + export               |
| RPT-04 | GSTR-2B report + export               |
| RPT-05 | HSN summary report                    |
| RPT-06 | P&L report                            |
| RPT-07 | Sales vs purchase report              |
| RPT-08 | Analytics dashboard + charts          |
| RPT-09 | Report tests                          |

### Dependencies

- Milestones 5–10 (all transactional modules).

### Completion Criteria

- All listed reports generate correct figures and export (CSV/PDF).
- Analytics dashboard renders live data.

---

## Milestone 12 — Deployment

### Objective

Ship Billix to production with CI/CD, monitoring, and runbooks.

### Engineering Tickets

| Ticket | Title                              |
| ------ | ---------------------------------- |
| DEP-01 | Frontend CI/CD → Vercel            |
| DEP-02 | Backend CI/CD → DigitalOcean       |
| DEP-03 | Sentry integration (FE + BE)       |
| DEP-04 | Environment + secrets management   |
| DEP-05 | Database backups + restore runbook |
| DEP-06 | Health checks + alerting           |
| DEP-07 | Production smoke tests             |
| DEP-08 | Launch runbook + rollback plan     |

### Dependencies

- All prior milestones.

### Completion Criteria

- Frontend deploys on merge to main via Vercel.
- Backend deploys via CI to DigitalOcean with zero-downtime.
- Sentry captures errors from both surfaces.
- Backups + runbooks validated.

---

## Cross-References

- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) — current status.
- [ARCHITECTURE.md](./ARCHITECTURE.md) — structure and conventions.
- [AI_RULES.md](./AI_RULES.md) — scoping and conduct rules.
- [CHANGELOG.md](./CHANGELOG.md) — completed ticket history.
