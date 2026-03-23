# Kairos — Client Portal for Freelancers

**Kairos** is a full-stack client portal built for freelancers and agencies. Manage projects, share deliverables, send invoices, and keep clients in the loop — all in one place.

Built with **Clean Architecture + DDD + Hexagonal (ports & adapters)** on a Python/FastAPI backend.

---

## What Kairos does

Kairos solves the chaos of managing multiple clients as a freelancer:

- **Organize work by client** — each client gets their own organization with role-based access
- **Track projects end-to-end** — from kickoff to delivery, with status visibility for both freelancer and client
- **Share deliverables** — submit work links, clients approve or request changes in one click
- **Invoice from the same platform** — issue invoices tied to projects, mark them paid when received
- **AI-generated client updates** — auto-summarize project progress for client-facing updates
- **Multi-tenant isolation** — every freelancer's data is fully isolated from others

---

## Feature status

| Feature | Status |
|---|---|
| JWT authentication (access + refresh tokens) | ✅ |
| Refresh token rotation + logout | ✅ |
| Multi-tenancy (per-freelancer data isolation) | ✅ |
| Organizations with roles (OWNER / ADMIN / MEMBER) | ✅ |
| Client invitations via email | ✅ |
| Project management (create, list, detail) | ✅ |
| Deliverable workflow (submit → approve / request-changes) | ✅ |
| Invoice management (issue, mark paid) | ✅ |
| AI client update summary (OpenRouter) | ✅ |
| Tenant lookup by slug (pre-auth) | ✅ |
| Transactional email (Resend + console fallback) | ✅ |
| Rate limiting (slowapi) | ✅ |
| Security headers + CORS middleware | ✅ |
| Structured logging (structlog + X-Correlation-ID) | ✅ |
| Alembic migrations (PostgreSQL + pgvector) | ✅ |
| Docker + docker-compose | ✅ |
| 170 tests (unit + integration + E2E) | ✅ |

---

## Stack

**Backend**
- **Python 3.12** + **FastAPI** + **Uvicorn**
- **SQLAlchemy async** (imperative mapping — domain stays clean)
- **Alembic** — migrations
- **pydantic-settings** — environment config
- **bcrypt** — password hashing (no passlib)
- **PyJWT** — token generation/validation
- **slowapi** — rate limiting
- **structlog** — structured JSON logging
- **httpx** — HTTP client (email + AI APIs)
- **pytest + pytest-asyncio + httpx** — test suite

**Integrations**
- **Resend** — transactional email (invitations, welcome)
- **OpenRouter** — AI summary generation (GPT-4o-mini by default)

---

## Architecture

```
src/
├── domain/          # Pure business logic — ZERO external dependencies
├── application/     # Use cases — orchestrates domain, defines ports
└── infrastructure/  # Adapters — FastAPI, SQLAlchemy, JWT, email, AI
```

**Dependency rule:**
```
infrastructure/api → application → domain ← infrastructure/persistence
```

Domain never imports from application, api, or infrastructure.

### Domain aggregates

| Aggregate | Responsibility |
|-----------|---------------|
| `User` | Authentication, identity |
| `Tenant` | Freelancer workspace isolation |
| `Organization` | Client account with role-based access |
| `Project` | Unit of work tied to a client org |
| `Deliverable` | Submitted work item pending client review |
| `Invoice` | Billable document tied to a project/org |

### Use cases (application layer)

```
register_user/       login_user/          refresh_token/       logout_user/
create_tenant/       get_tenant_by_slug/  get_current_user/
create_organization/ list_organizations/  get_organization/
invite_member/       accept_invitation/   remove_member/       change_member_role/
create_project/      list_projects/       get_project/
submit_deliverable/  approve_deliverable/ request_changes/     list_deliverables/
issue_invoice/       mark_invoice_paid/   list_invoices/
generate_client_update/
```

---

## API Endpoints

| Method | Path | Auth | Rate limit |
|--------|------|------|-----------|
| `GET` | `/health` | ❌ | — |
| `GET` | `/api/v1/tenants/by-slug/{slug}` | ❌ | 20/min |
| `POST` | `/api/v1/tenants` | ❌ | 5/min |
| `POST` | `/api/v1/users/` | ❌ | 3/min |
| `GET` | `/api/v1/users/me` | ✅ JWT | 60/min |
| `POST` | `/api/v1/auth/login` | ❌ | 5/min |
| `POST` | `/api/v1/auth/refresh` | ❌ | 10/min |
| `POST` | `/api/v1/auth/logout` | ❌ | 10/min |
| `POST` | `/api/v1/organizations` | ✅ JWT | 30/min |
| `GET` | `/api/v1/organizations` | ✅ JWT | 60/min |
| `GET` | `/api/v1/organizations/{id}` | ✅ JWT | 60/min |
| `GET` | `/api/v1/organizations/{id}/invoices` | ✅ JWT | 60/min |
| `POST` | `/api/v1/organizations/{id}/invitations` | ✅ JWT | 30/min |
| `POST` | `/api/v1/organizations/{id}/invitations/{inv_id}/accept` | ✅ JWT | 30/min |
| `DELETE` | `/api/v1/organizations/{id}/members/{uid}` | ✅ JWT | 30/min |
| `PATCH` | `/api/v1/organizations/{id}/members/{uid}/role` | ✅ JWT | 30/min |
| `POST` | `/api/v1/projects` | ✅ JWT | 30/min |
| `GET` | `/api/v1/projects` | ✅ JWT | 60/min |
| `GET` | `/api/v1/projects/{id}` | ✅ JWT | 60/min |
| `GET` | `/api/v1/projects/{id}/deliverables` | ✅ JWT | 60/min |
| `GET` | `/api/v1/projects/{id}/summary` | ✅ JWT | 10/min |
| `POST` | `/api/v1/projects/{id}/deliverables` | ✅ JWT | 30/min |
| `PATCH` | `/api/v1/deliverables/{id}/approve` | ✅ JWT | 30/min |
| `PATCH` | `/api/v1/deliverables/{id}/request-changes` | ✅ JWT | 30/min |
| `POST` | `/api/v1/organizations/{id}/invoices` | ✅ JWT | 30/min |
| `PATCH` | `/api/v1/invoices/{id}/paid` | ✅ JWT | 30/min |

---

## Quick start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for PostgreSQL)

### 1. Clone and install

```bash
git clone https://github.com/brandon-stack-html/KAIROS.git
cd KAIROS
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/kairos
SECRET_KEY=your-secret-key-at-least-32-chars
ENVIRONMENT=development
EMAIL_PROVIDER=console
FRONTEND_URL=http://localhost:3000
APP_NAME=Kairos
OPENROUTER_API_KEY=your-key-here   # optional — AI summaries
```

### 3. Start database

```bash
docker-compose up -d
```

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Start dev server

```bash
uv run uvicorn src.infrastructure.api.main:app --reload
```

API at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`

---

## Running tests

```bash
uv run pytest                        # All 170 tests
uv run pytest -v                     # Verbose
uv run pytest tests/e2e/             # E2E full workflow
uv run pytest tests/unit/            # Unit tests only
uv run pytest tests/integration/     # Integration tests only
```

Tests use SQLite in-memory — no database required.

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | DB connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key (≥32 chars in prod) |
| `ENVIRONMENT` | `development` | `production` enables security validations |
| `JWT_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_TTL_DAYS` | `30` | Refresh token lifetime |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS whitelist |
| `EMAIL_PROVIDER` | `console` | `console` or `resend` |
| `RESEND_API_KEY` | `None` | Required when `EMAIL_PROVIDER=resend` |
| `EMAIL_FROM` | `noreply@example.com` | Sender address |
| `FRONTEND_URL` | `http://localhost:3000` | Used in invitation email links |
| `APP_NAME` | `Kairos` | Used in email templates |
| `OPENROUTER_API_KEY` | `None` | Required for AI summaries in production |
| `AI_MODEL` | `openai/gpt-4o-mini` | Model used via OpenRouter |

---

## Multi-tenancy

Every freelancer workspace is fully isolated:

1. Client sends `tenant_id` (UUID) on registration
2. JWT stores `tid` claim
3. `TenantMiddleware` extracts `tid` from Bearer token on every protected request
4. Repositories filter with `WHERE tenant_id = ?` automatically
5. PostgreSQL RLS adds a second layer of isolation in production

---

## Key design decisions

- **Imperative SQLAlchemy mapping** — domain classes have zero ORM annotations
- **`session.merge()` for upsert** — used for refresh tokens and invitations to avoid UNIQUE constraint violations
- **Handlers return full domain objects** — routers build responses directly, no re-fetching
- **Fire-and-forget emails** — email failures never block the request, always logged as warnings
- **AI call outside UoW** — HTTP call to OpenRouter happens after DB transaction closes, never blocks it
- **`bcrypt` direct** — passlib removed (incompatible with bcrypt ≥ 5.0)
- **FK TypeDecorator rule** — FK columns with SQLAlchemy cascade must use the same TypeDecorator as the parent PK
- **Authorization in handlers, not domain** — role checks happen in use case handlers, domain stays policy-free

---

## License

MIT — use it, clone it, ship it.
