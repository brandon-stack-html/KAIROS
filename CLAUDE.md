# CLAUDE.md

> **Kairos** — Client Portal for Freelancers.
> Domains: User, Tenant, Organization, Project, Deliverable, Invoice, AI Summary.

## Commands

```bash
# Backend
uv sync                                                  # Install dependencies
uv run uvicorn src.infrastructure.api.main:app --reload   # Dev server
uv run pytest                                             # All 170 tests
uv run pytest tests/path/to_test.py::test_name            # Single test
uv run ruff check . --fix --unsafe-fixes                  # Lint + auto-fix
uv run ruff format .                                      # Format
uv run alembic upgrade head                               # Run migrations

# Frontend (inside /frontend)
npm install                     # Install dependencies
npm run dev                     # Dev server (port 3000)
```

## Architecture

Clean Architecture + DDD + Hexagonal (ports & adapters).

```
src/
├── domain/          # Pure business logic — ZERO external dependencies
├── application/     # Use cases — orchestrates domain, defines ports
└── infrastructure/  # Adapters — FastAPI, SQLAlchemy, JWT, email, AI
```

**Dependency rule:** `infrastructure/api → application → domain ← infrastructure/persistence`
Domain never imports from application, api, or infrastructure.

### Domain Aggregates

| Aggregate | Key entities | Statuses |
|-----------|-------------|----------|
| User | User, UserId, Email | — |
| Tenant | Tenant, TenantId, slug | — |
| Organization | Organization, Membership, Invitation, Role(OWNER/ADMIN/MEMBER) | — |
| Project | Project, ProjectId | ACTIVE, COMPLETED |
| Deliverable | Deliverable, DeliverableId | PENDING, APPROVED, CHANGES_REQUESTED |
| Invoice | Invoice, InvoiceId, amount(Decimal) | DRAFT, SENT, PAID |

### Mapper registration order (critical — FK dependency)

Both `main.py` lifespan and `tests/conftest.py` must register in this exact order:

```python
start_tenant_mappers()        # 1 — no FKs
start_user_mappers()          # 2 — FK → tenants
start_refresh_token_mappers() # 3 — FK → users
start_organization_mappers()  # 4 — FK → tenants + users
start_invitation_mappers()    # 5 — FK → organizations + users
start_project_mappers()       # 6 — FK → organizations + tenants
start_deliverable_mappers()   # 7 — FK → projects + tenants
start_invoice_mappers()       # 8 — FK → organizations + tenants
```

## Design Rules

- **Imperative SA mapping** — domain classes have zero ORM annotations
- **Handlers return full domain objects** — never just IDs; routers build response from returned object
- **Authorization in handlers, not domain** — role checks in use case handlers, domain stays policy-free
- **FK TypeDecorator rule**: FK columns with SA cascade MUST use same TypeDecorator as parent PK. Without cascade (`session.merge(child)` direct), `String(36)` is safe
- **StatusType TypeDecorator rule**: every enum/status column MUST have its own TypeDecorator (follow `RoleType` pattern)
- **Invoice Decimal**: domain uses `Decimal`, command receives `str`, handler converts with `Decimal(command.amount)`, router serializes as `str(invoice.amount)`. SA `Numeric(12,2)` — no TypeDecorator needed
- **Email fire-and-forget**: `send()` called outside `async with self._uow` (after commit). Failures logged as warning, never block the request
- **AI call outside UoW**: HTTP call to OpenRouter happens after DB transaction closes
- **Refresh token rotation**: every `/auth/refresh` revokes old + issues new; `session.merge()` for upsert
- **Multi-tenancy dual-layer**: WHERE tenant_id in app layer + PostgreSQL RLS in prod; SQLite ignores RLS
- **TenantMiddleware**: extracts `tid` from JWT; public paths use `startswith()` for `/docs`, `/tenants` and sub-paths
- **Query handlers**: only need UoW + command, no dedicated ports file
- **Alembic migrations**: use `sa.String(N)` in migration files, never TypeDecorators
- **`InsufficientRoleError` → 403** in `_STATUS_MAP` before `DomainError` (MRO: subclasses first)
- **`AiServiceError` → 502** as `ApplicationError`, not `DomainError`

## Lo que NO queremos

- Lógica de negocio en los routers de FastAPI
- Imports de SQLAlchemy en el dominio
- Casos de uso que llamen a otros casos de uso directamente
- Secrets hardcodeados — todo por variables de entorno
- Columnas de enum o status sin TypeDecorator
- Handlers que devuelvan solo IDs

## Naming Conventions

- Handlers: `VerbNounHandler` (RegisterUserHandler)
- Commands: `VerbNounCommand` (RegisterUserCommand)
- Ports/interfaces: prefijo `I` → `IUserRepository`, `ITokenGenerator`
- Abstract classes: prefijo `Abstract` → `AbstractPasswordHasher`, `AbstractUnitOfWork`
- Domain errors: `domain/{aggregate}/errors.py`
- Mappers: idempotent with `_mapped = False` + `UnmappedClassError` guard

## API Endpoints

| Method | Path | Auth | Rate | Handler |
|--------|------|------|------|---------|
| `GET` | `/health` | ❌ | — | inline |
| `GET` | `/api/v1/tenants/by-slug/{slug}` | ❌ | 20/min | GetTenantBySlugHandler |
| `POST` | `/api/v1/tenants` | ❌ | 5/min | CreateTenantHandler |
| `POST` | `/api/v1/users/` | ❌ | 3/min | RegisterUserHandler |
| `GET` | `/api/v1/users/me` | ✅ | 60/min | GetCurrentUserHandler |
| `POST` | `/api/v1/auth/login` | ❌ | 5/min | LoginUserHandler |
| `POST` | `/api/v1/auth/refresh` | ❌ | 10/min | RefreshTokenHandler |
| `POST` | `/api/v1/auth/logout` | ❌ | 10/min | LogoutHandler |
| `POST` | `/api/v1/organizations` | ✅ | 30/min | CreateOrganizationHandler |
| `GET` | `/api/v1/organizations` | ✅ | 60/min | ListOrganizationsHandler |
| `GET` | `/api/v1/organizations/{id}` | ✅ | 60/min | GetOrganizationHandler |
| `GET` | `/api/v1/organizations/{id}/invoices` | ✅ | 60/min | ListInvoicesHandler |
| `POST` | `/api/v1/organizations/{id}/invitations` | ✅ | 30/min | InviteMemberHandler |
| `POST` | `/api/v1/organizations/{id}/invitations/{inv_id}/accept` | ✅ | 30/min | AcceptInvitationHandler |
| `DELETE` | `/api/v1/organizations/{id}/members/{uid}` | ✅ | 30/min | RemoveMemberHandler |
| `PATCH` | `/api/v1/organizations/{id}/members/{uid}/role` | ✅ | 30/min | ChangeMemberRoleHandler |
| `POST` | `/api/v1/projects` | ✅ | 30/min | CreateProjectHandler |
| `GET` | `/api/v1/projects` | ✅ | 60/min | ListProjectsHandler |
| `GET` | `/api/v1/projects/{id}` | ✅ | 60/min | GetProjectHandler |
| `GET` | `/api/v1/projects/{id}/deliverables` | ✅ | 60/min | ListDeliverablesHandler |
| `GET` | `/api/v1/projects/{id}/summary` | ✅ | 10/min | GenerateClientUpdateHandler |
| `POST` | `/api/v1/projects/{id}/deliverables` | ✅ | 30/min | SubmitDeliverableHandler |
| `PATCH` | `/api/v1/deliverables/{id}/approve` | ✅ | 30/min | ApproveDeliverableHandler |
| `PATCH` | `/api/v1/deliverables/{id}/request-changes` | ✅ | 30/min | RequestChangesHandler |
| `POST` | `/api/v1/organizations/{id}/invoices` | ✅ | 30/min | IssueInvoiceHandler |
| `PATCH` | `/api/v1/invoices/{id}/paid` | ✅ | 30/min | MarkInvoicePaidHandler |

## Error Response Format

```json
{ "error": { "message": "descripción del error" } }
```

`400` DomainError · `401` Not authenticated · `403` InsufficientRoleError · `404` EntityNotFoundError · `409` ConflictError · `422` Pydantic validation · `429` Rate limit · `502` AiServiceError

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | DB connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key (≥32 chars prod) |
| `ENVIRONMENT` | `development` | `production` enables security validations |
| `JWT_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_TTL_DAYS` | `30` | Refresh token lifetime |
| `ALLOWED_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | CORS whitelist |
| `EMAIL_PROVIDER` | `console` | `console` or `resend` |
| `RESEND_API_KEY` | `None` | Required when EMAIL_PROVIDER=resend |
| `EMAIL_FROM` | `noreply@example.com` | Sender address |
| `FRONTEND_URL` | `http://localhost:3000` | Base URL for email links |
| `APP_NAME` | `Kairos` | Product name (used in emails) |
| `OPENROUTER_API_KEY` | `None` | Required for AI summaries in prod |
| `AI_MODEL` | `openai/gpt-4o-mini` | Model via OpenRouter |

## Backend Stack

Python 3.12 · FastAPI · Uvicorn · SQLAlchemy async (imperative mapping) · Alembic · pydantic-settings · bcrypt (no passlib) · PyJWT · slowapi · structlog · httpx · Resend · pytest + pytest-asyncio

## Frontend (monorepo — `/frontend`)

**Stack:** Next.js 15 (App Router) · Tailwind CSS 4 · shadcn/ui · TypeScript · Zustand · TanStack Query v5 · React Hook Form + Zod · Axios

**Workflow:** see `kairos-frontend-workflow.md` (gitignored, local reference only)

## Backend Development Workflow

1. Define domain in `src/domain/{aggregate}/`
2. Define use case in `src/application/{use_case}/`
3. Implement adapter in `src/infrastructure/persistence/sqlalchemy/`
4. Wire: TypeDecorators → `types.py`, mapper → `main.py` + `conftest.py`, repo → `unit_of_work.py`, factory → `container.py`, handler override → `conftest.py`
5. Create API route in `src/infrastructure/api/routers/`
6. Run migrations: `uv run alembic upgrade head`
7. Test: `uv run pytest`

antes de compactar las conversaciones sube a engram lo mas importante de ellas
