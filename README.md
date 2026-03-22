# SaaS Boilerplate — Python + FastAPI

Production-ready B2B SaaS backend. Clone it, add your domain, ship faster.

Built with **Clean Architecture + DDD + Hexagonal (ports & adapters)**. Every new SaaS project starts from this structure — no domain-specific code lives here.

---

## What's included out of the box

| Feature | Status |
|---|---|
| JWT authentication (access + refresh tokens) | ✅ |
| Refresh token rotation + logout | ✅ |
| Multi-tenancy (tenant isolation per request) | ✅ |
| Organizations with roles (OWNER / ADMIN / MEMBER) | ✅ |
| Member invitations via email | ✅ |
| Transactional email (Resend + console fallback) | ✅ |
| Rate limiting (slowapi) | ✅ |
| Security headers + CORS middleware | ✅ |
| Structured logging (structlog + X-Correlation-ID) | ✅ |
| Alembic migrations (PostgreSQL + pgvector) | ✅ |
| Docker + docker-compose | ✅ |
| 107 tests (unit + integration + E2E) | ✅ |

---

## Stack

- **Python 3.12** + **FastAPI** + **Uvicorn**
- **SQLAlchemy async** (imperative mapping — domain stays clean)
- **Alembic** — migrations
- **pydantic-settings** — environment config
- **bcrypt** — password hashing (no passlib)
- **PyJWT** — token generation/validation
- **slowapi** — rate limiting (swap for Redis in multi-instance prod)
- **structlog** — structured JSON logging
- **httpx** — HTTP client (Resend email API)
- **pytest + pytest-asyncio + httpx** — test suite

---

## Architecture

```
src/
├── domain/          # Pure business logic — ZERO external dependencies
├── application/     # Use cases — orchestrates domain, defines ports
└── infrastructure/  # Adapters — FastAPI, SQLAlchemy, JWT, email
```

**Dependency rule:**
```
infrastructure/api → application → domain ← infrastructure/persistence
```

Domain never imports from application, api, or infrastructure.

### Layer breakdown

**Domain** — your business rules, nothing else:
- `AggregateRoot`, `Entity`, `ValueObject`, `DomainEvent` base classes
- `User` aggregate (email + name validation, events)
- `Tenant` aggregate (slug validation, provisioning)
- `Organization` aggregate (memberships, invitations, role enforcement)
- `Role` enum with `can_invite()` and `can_delete_org()` methods
- `RefreshToken` value object (issue, revoke, expiry)

**Application** — one folder per use case:
```
register_user/   login_user/   refresh_token/   logout_user/
create_organization/   list_organizations/   invite_member/
accept_invitation/   remove_member/   change_member_role/
```
Each use case has `command.py` (DTO) + `handler.py` (logic) + `ports.py` (interfaces).

**Infrastructure** — adapters implementing ports:
- FastAPI routers, middleware, schemas
- SQLAlchemy repositories with imperative mapping
- JWT handler, bcrypt password hasher
- Email adapters: `ConsoleEmailSender` (dev) / `ResendEmailSender` (prod)
- In-memory adapters for tests

---

## API Endpoints

| Method | Path | Auth | Rate limit |
|--------|------|------|-----------|
| `GET` | `/health` | ❌ | — |
| `POST` | `/api/v1/users/` | ❌ | 3/min |
| `POST` | `/api/v1/auth/login` | ❌ | 5/min |
| `POST` | `/api/v1/auth/refresh` | ❌ | 10/min |
| `POST` | `/api/v1/auth/logout` | ❌ | 10/min |
| `POST` | `/api/v1/organizations` | ✅ JWT | 30/min |
| `GET` | `/api/v1/organizations` | ✅ JWT | 60/min |
| `POST` | `/api/v1/organizations/{id}/invitations` | ✅ JWT | 30/min |
| `POST` | `/api/v1/organizations/{id}/invitations/{inv_id}/accept` | ✅ JWT | 30/min |
| `DELETE` | `/api/v1/organizations/{id}/members/{uid}` | ✅ JWT | 30/min |
| `PATCH` | `/api/v1/organizations/{id}/members/{uid}/role` | ✅ JWT | 30/min |

---

## Quick start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for PostgreSQL)

### 1. Clone and install

```bash
git clone https://github.com/brandon-stack-html/boiler-plate-saas.git my-saas
cd my-saas
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mydb
SECRET_KEY=your-secret-key-at-least-32-chars
ENVIRONMENT=development
EMAIL_PROVIDER=console
FRONTEND_URL=http://localhost:3000
APP_NAME=My SaaS
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

API available at `http://localhost:8000` — docs at `http://localhost:8000/docs`

---

## Running tests

```bash
uv run pytest              # All 107 tests
uv run pytest -v           # Verbose
uv run pytest tests/e2e/   # E2E workflow only
uv run pytest tests/unit/  # Unit tests only
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
| `APP_NAME` | `boiler-plate-saas` | Used in email templates |

---

## Multi-tenancy

Every request is scoped to a tenant:

1. Client sends `tenant_id` (UUID) on registration
2. JWT stores `tid` claim
3. `TenantMiddleware` extracts `tid` from Bearer token on every protected request
4. Repositories filter with `WHERE tenant_id = ?` automatically
5. PostgreSQL RLS adds a second layer of isolation in production

---

## Adding a new aggregate

Follow this pattern for any new domain concept (e.g. `subscription`):

```
src/domain/subscription/
├── subscription.py      # AggregateRoot
├── value_objects.py     # SubscriptionId, Plan, etc.
├── events.py            # SubscriptionCreated, etc.
├── repository.py        # ISubscriptionRepository (port)
└── errors.py            # SubscriptionNotFoundError, etc.

src/application/create_subscription/
├── command.py           # CreateSubscriptionCommand
├── handler.py           # CreateSubscriptionHandler
└── ports.py             # ISubscriptionUnitOfWork

src/infrastructure/persistence/sqlalchemy/
├── tables/subscription_table.py
├── mappers/subscription_mapper.py
└── subscription_repository.py

src/infrastructure/api/routers/subscriptions.py
```

Then wire it in `src/infrastructure/config/container.py` and register the mapper in `src/infrastructure/api/main.py` lifespan.

---

## Key design decisions

- **Imperative SQLAlchemy mapping** — domain classes have zero ORM annotations
- **`session.merge()` for upsert** — used for refresh tokens and invitations to avoid UNIQUE constraint violations
- **Handlers return full domain objects** — routers build responses directly, no re-fetching
- **Fire-and-forget emails** — email failures never block the request, always logged as warnings
- **`bcrypt` direct** — passlib removed (incompatible with bcrypt ≥ 5.0)
- **FK TypeDecorator rule** — FK columns with SQLAlchemy cascade must use the same TypeDecorator as the parent PK

---

## License

MIT — use it, clone it, ship it.
