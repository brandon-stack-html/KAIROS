# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **LanceFlow** — Client Portal for Freelancers. Built on a Clean Architecture + DDD + Hexagonal boilerplate.
> Domains: User, Tenant, Organization, Project, Deliverable, Invoice, AI Summary.

## Package Manager

This project uses `uv` for dependency management.

```bash
uv sync                        # Install dependencies
uv add <package>               # Add a dependency
uv run <command>               # Run a command in the project environment
```

## Running the App

```bash
uv run uvicorn src.infrastructure.api.main:app --reload   # Dev server
```

## Testing

```bash
uv run pytest                                           # Run all tests (170 passing)
uv run pytest tests/path/to_test.py::test_name          # Run a single test
```

## Linting / Formatting

```bash
uv run ruff check .          # Lint
uv run ruff check . --fix    # Auto-fix
uv run ruff format .         # Format
```

## Architecture

Clean Architecture + DDD + Hexagonal (ports & adapters). Four layers under `src/`:

```
src/
├── domain/                          # Pure business logic — ZERO external dependencies
│   ├── shared/                      # Base building blocks (reuse in every aggregate)
│   │   ├── entity.py                # Entity[TId] — equality by identity
│   │   ├── aggregate_root.py        # AggregateRoot[TId] — manages domain events
│   │   ├── value_object.py          # ValueObject — immutable, equality by value
│   │   ├── domain_event.py          # DomainEvent — base for all domain events
│   │   ├── errors.py                # DomainError, EntityNotFoundError, ConflictError, InvalidRefreshTokenError
│   │   ├── tenant_id.py             # TenantId value object (UUID v4)
│   │   ├── refresh_token.py         # RefreshToken value object — issue(), revoke(), is_expired()
│   │   ├── organization_id.py       # OrganizationId VO (frozen, UUID v4)
│   │   ├── membership_id.py         # MembershipId VO (frozen, UUID v4)
│   │   ├── invitation_id.py         # InvitationId VO (frozen, UUID v4)
│   │   ├── project_id.py            # ProjectId VO (frozen, UUID v4) — generate(), from_str(), __composite_values__()
│   │   ├── deliverable_id.py        # DeliverableId VO (frozen, UUID v4) — same pattern as ProjectId
│   │   └── role.py                  # Role enum (OWNER/ADMIN/MEMBER) — can_invite(), can_delete_org()
│   ├── user/ ✅                     # User aggregate
│   │   ├── user.py                  # Aggregate root + UserId, Email, tenant_id field
│   │   ├── repository.py            # IUserRepository (DRIVEN PORT)
│   │   ├── events.py                # UserRegistered, UserDeactivated
│   │   └── errors.py                # InvalidEmailError, InvalidUserNameError
│   ├── tenant/ ✅                   # Tenant aggregate
│   │   ├── tenant.py                # Aggregate root — provision(), slug validation
│   │   ├── repository.py            # ITenantRepository (DRIVEN PORT)
│   │   ├── events.py                # TenantCreated
│   │   └── errors.py                # TenantNotFoundError, SlugAlreadyTakenError, etc.
│   ├── organization/ ✅             # Organization aggregate
│   │   ├── organization.py          # Aggregate root — create(), add_member(), remove_member(), change_member_role(), dissolve()
│   │   ├── membership.py            # Membership entity (org_id: OrganizationId, NOT str — SA cascade)
│   │   ├── invitation.py            # Invitation entity — create(), accept(), is_expired() (org_id: str)
│   │   ├── repository.py            # IOrganizationRepository + IInvitationRepository (DRIVEN PORTS)
│   │   ├── events.py                # OrganizationCreated, MemberAdded, MemberRemoved, MemberRoleChanged, OrganizationDissolved, InvitationSent, InvitationAccepted
│   │   └── errors.py                # OrganizationNotFoundError, MemberAlreadyExistsError, MemberNotFoundError, InsufficientRoleError, CannotRemoveLastOwnerError, InvitationExpiredError, InvitationAlreadyAcceptedError, InvalidOrgNameError, InvalidOrgSlugError
│   ├── project/ ✅                  # Project aggregate
│   │   ├── project.py               # Aggregate root — create(), ProjectStatus(ACTIVE/COMPLETED), name 2-100 chars
│   │   ├── repository.py            # IProjectRepository (DRIVEN PORT)
│   │   ├── events.py                # ProjectCreated
│   │   └── errors.py                # ProjectNotFoundError, InvalidProjectNameError
│   └── deliverable/ ✅              # Deliverable aggregate
│       ├── deliverable.py           # Aggregate root — create(), approve(approver_id), request_changes(reviewer_id)
│       │                            # DeliverableStatus(PENDING/APPROVED/CHANGES_REQUESTED)
│       │                            # title: 2-100 chars; approve/request_changes raise DeliverableAlreadyReviewedError if not PENDING
│       ├── repository.py            # IDeliverableRepository (DRIVEN PORT)
│       ├── events.py                # DeliverableSubmitted, DeliverableApproved, ChangesRequested
│       └── errors.py                # DeliverableNotFoundError, DeliverableAlreadyReviewedError, InvalidDeliverableTitleError, InvalidDeliverableUrlError
│
├── application/                     # Use cases — orchestrates domain, defines ports
│   ├── shared/
│   │   ├── unit_of_work.py          # AbstractUnitOfWork (async context manager)
│   │   ├── event_publisher.py       # AbstractEventPublisher
│   │   ├── password_hasher.py       # AbstractPasswordHasher (DRIVEN PORT)
│   │   ├── refresh_token_store.py   # AbstractRefreshTokenStore (DRIVEN PORT)
│   │   ├── email_sender.py          # AbstractEmailSender, EmailMessage, EmailTemplate, build_email()
│   │   └── errors.py                # NotFoundError, ConflictError, EmailConfigurationError
│   ├── register_user/ ✅            # Use case: POST /users
│   │   ├── command.py               # RegisterUserCommand — includes tenant_id: str
│   │   ├── handler.py
│   │   └── ports.py                 # IUserUnitOfWork — users + refresh_tokens repos
│   ├── login_user/ ✅               # Use case: POST /auth/login
│   │   ├── command.py
│   │   ├── handler.py               # Issues access token + refresh token on login
│   │   └── ports.py                 # ITokenGenerator.generate() includes tenant_id param
│   ├── refresh_token/ ✅            # Use case: POST /auth/refresh
│   │   ├── command.py
│   │   ├── handler.py               # Validates + rotates refresh token, returns new pair
│   │   └── ports.py
│   ├── logout_user/ ✅              # Use case: POST /auth/logout
│   │   ├── command.py
│   │   ├── handler.py               # Revokes refresh token (idempotent)
│   │   └── ports.py
│   ├── create_organization/ ✅      # Use case: POST /api/v1/organizations
│   │   ├── command.py               # CreateOrganizationCommand(name, slug, owner_id, tenant_id)
│   │   ├── handler.py               # Returns full Organization (not just ID)
│   │   └── ports.py                 # IOrganizationUnitOfWork — organizations + invitations repos
│   ├── list_organizations/ ✅       # Use case: GET /api/v1/organizations
│   │   ├── command.py               # ListOrganizationsCommand(user_id, tenant_id)
│   │   └── handler.py               # Returns list[Organization]
│   ├── invite_member/ ✅            # Use case: POST /api/v1/organizations/{id}/invitations
│   │   ├── command.py               # InviteMemberCommand(org_id, inviter_id, invitee_email, role, tenant_id)
│   │   ├── handler.py               # Returns full Invitation
│   │   └── ports.py
│   ├── accept_invitation/ ✅        # Use case: POST /api/v1/invitations/{id}/accept
│   │   ├── command.py               # AcceptInvitationCommand(invitation_id, user_id, tenant_id)
│   │   ├── handler.py               # Returns full Organization
│   │   └── ports.py
│   ├── remove_member/ ✅            # Use case: DELETE /api/v1/organizations/{id}/members/{uid}
│   │   ├── command.py               # RemoveMemberCommand(org_id, remover_id, user_id, tenant_id)
│   │   ├── handler.py               # Returns None
│   │   └── ports.py
│   ├── change_member_role/ ✅       # Use case: PATCH /api/v1/organizations/{id}/members/{uid}/role
│   │   ├── command.py               # ChangeMemberRoleCommand(org_id, changer_id, user_id, new_role, tenant_id)
│   │   ├── handler.py               # Returns full Organization
│   │   └── ports.py
│   ├── create_project/ ✅           # Use case: POST /api/v1/projects
│   │   ├── command.py               # CreateProjectCommand(name, description, org_id, owner_id, tenant_id)
│   │   ├── handler.py               # Verifies Role.OWNER, calls Project.create(), returns full Project
│   │   └── ports.py                 # IProjectUnitOfWork — organizations + projects repos
│   ├── list_projects/ ✅            # Use case: GET /api/v1/projects
│   │   ├── command.py               # ListProjectsCommand(user_id, tenant_id, org_id: str|None)
│   │   └── handler.py               # Returns list[Project] (filtered by org if org_id provided)
│   ├── submit_deliverable/ ✅       # Use case: POST /api/v1/projects/{id}/deliverables
│   │   ├── command.py               # SubmitDeliverableCommand(title, url_link, project_id, submitter_id, tenant_id)
│   │   ├── handler.py               # Fetches project, calls Deliverable.create(), returns full Deliverable
│   │   └── ports.py                 # IDeliverableUnitOfWork — projects + deliverables + organizations repos
│   ├── approve_deliverable/ ✅      # Use case: PATCH /api/v1/deliverables/{id}/approve
│   │   ├── command.py               # ApproveDeliverableCommand(deliverable_id, approver_id, tenant_id)
│   │   └── handler.py               # Verifies OWNER|ADMIN, calls deliverable.approve(), returns full Deliverable
│   └── request_changes/ ✅          # Use case: PATCH /api/v1/deliverables/{id}/request-changes
│       ├── command.py               # RequestChangesCommand(deliverable_id, reviewer_id, tenant_id)
│       └── handler.py               # Verifies OWNER|ADMIN, calls deliverable.request_changes(), returns full Deliverable
│
└── infrastructure/                  # Adapters — implements ports defined in domain/application
    ├── api/ ✅                       # Presentation layer — FastAPI entry point
    │   ├── main.py                  # FastAPI app + lifespan (mappers registered in FK order) + middleware chain
    │   ├── dependencies.py          # get_current_user — JWT Bearer dependency
    │   ├── rate_limiter.py          # Shared slowapi Limiter instance
    │   ├── logging.py               # structlog configuration helper
    │   ├── routers/
    │   │   ├── users.py             # POST /api/v1/users (rate limited)
    │   │   ├── auth.py              # POST /login, /refresh, /logout (all rate limited)
    │   │   ├── organizations.py     # 6 org endpoints — all JWT-protected, 30/min rate limit
    │   │   ├── projects.py          # POST /api/v1/projects, GET /api/v1/projects — JWT, 30/min + 60/min
    │   │   └── deliverables.py      # POST /projects/{id}/deliverables, PATCH /deliverables/{id}/approve,
    │   │                            # PATCH /deliverables/{id}/request-changes — JWT, 30/min
    │   ├── middleware/
    │   │   ├── exception_handler.py # GlobalErrorHandler → JSON error envelope
    │   │   ├── security_headers.py  # X-Frame-Options, HSTS, X-Content-Type-Options, etc.
    │   │   ├── tracing.py           # TracingMiddleware — X-Correlation-ID per request
    │   │   └── tenant.py            # TenantMiddleware — extracts 'tid' from JWT, 401 if missing
    │   └── schemas/
    │       ├── user_schemas.py          # UserCreate (tenant_id: UUID), UserResponse, LoginResponse
    │       ├── organization_schemas.py  # OrgCreate, OrgResponse, MemberResponse, InvitationCreate, InvitationResponse, ChangeMemberRoleRequest
    │       ├── project_schemas.py       # ProjectCreate(name, description, org_id), ProjectResponse
    │       └── deliverable_schemas.py   # DeliverableCreate(title, url_link), DeliverableResponse
    ├── config/
    │   ├── settings.py              # pydantic-settings — reads from .env
    │   └── container.py             # Composition root — wire all dependencies here
    ├── persistence/
    │   ├── sqlalchemy/
    │   │   ├── database.py          # Async engine + metadata
    │   │   ├── types.py             # Custom column types:
    │   │   │                        #   TenantIdType, UserIdType, UserEmailType
    │   │   │                        #   OrganizationIdType, MembershipIdType, InvitationIdType, RoleType
    │   │   │                        #   ProjectIdType, ProjectStatusType
    │   │   │                        #   DeliverableIdType, DeliverableStatusType
    │   │   │                        # RULE: every VO and every enum column needs a TypeDecorator
    │   │   ├── repository.py        # Generic SqlAlchemyRepository[T]
    │   │   ├── tenant_context.py    # set_tenant() — SET LOCAL for PostgreSQL RLS
    │   │   ├── tables/
    │   │   │   ├── tenants_table.py         # tenants table definition
    │   │   │   ├── users_table.py           # users + tenant_id FK + composite index
    │   │   │   ├── organizations_table.py   # organizations — tenant_id FK, unique (tenant_id, slug)
    │   │   │   ├── memberships_table.py     # memberships — org_id: OrganizationIdType (cascade FK!)
    │   │   │   ├── invitations_table.py     # invitations — org_id: String(36) (no cascade, direct merge)
    │   │   │   ├── projects_table.py        # projects — org_id: OrganizationIdType FK, status: ProjectStatusType
    │   │   │   └── deliverables_table.py    # deliverables — project_id: ProjectIdType FK,
    │   │   │                                # status: DeliverableStatusType, url_link: String(2048), updated_at
    │   │   ├── mappers/
    │   │   │   ├── tenant_mapper.py         # start_mappers() — idempotent (_mapped flag + UnmappedClassError guard)
    │   │   │   ├── user_mapper.py
    │   │   │   ├── refresh_token_mapper.py
    │   │   │   ├── organization_mapper.py   # Maps Membership first, then Organization with selectin + cascade
    │   │   │   ├── invitation_mapper.py
    │   │   │   ├── project_mapper.py        # Registered after organization_mapper (FK dependency)
    │   │   │   ├── deliverable_mapper.py    # Registered after project_mapper (FK dependency)
    │   │   │   └── invoice_mapper.py        # Registered after organization_mapper (FK dependency)
    │   │   ├── tenant_repository.py
    │   │   ├── user_repository.py           # Tenant-scoped WHERE
    │   │   ├── refresh_token_repository.py  # merge-based upsert
    │   │   ├── organization_repository.py   # merge + JOIN find_by_user
    │   │   ├── invitation_repository.py     # merge-based upsert
    │   │   ├── project_repository.py        # save=merge, find_by_id, find_by_org, find_by_user_orgs (JOIN memberships)
    │   │   ├── deliverable_repository.py    # save=merge, find_by_id(tenant_id), find_by_project(project_id, tenant_id)
    │   │   ├── invoice_repository.py        # save=merge, find_by_id(tenant_id), find_by_org(org_id, tenant_id)
    │   │   └── unit_of_work.py             # SqlAlchemyUnitOfWork
    │   │                                   # repos: users, tenants, refresh_tokens, organizations,
    │   │                                   #        invitations, projects, deliverables, invoices
    │   └── in_memory/
    │       ├── refresh_token_store.py   # InMemoryRefreshTokenStore (tests)
    │       ├── email_sender.py          # InMemoryEmailSender — captures sent emails for test assertions
    │       └── ai_service.py            # InMemoryAiService — records calls + configurable response (tests)
    ├── security/
    │   ├── jwt_handler.py           # JwtTokenGenerator — adds 'tid' claim to JWT
    │   └── password_hasher.py       # BcryptPasswordHasher (bcrypt direct, no passlib)
    ├── messaging/
    │   ├── in_memory/               # In-memory event publisher for tests
    │   └── email_event_handler.py   # EmailEventHandler — reacts to InvitationSent domain event
    └── external/
        ├── email/
        │   ├── console_email_sender.py  # ConsoleEmailSender — prints to stdout via structlog (dev)
        │   └── resend_email_sender.py   # ResendEmailSender — calls Resend API (prod), 3 attempts + backoff
        └── ai/
            └── openrouter_ai_service.py # OpenRouterAiService — POST to OpenRouter, retry 3x, 1s backoff, raises AiServiceError → 502
```

### Dependency rule

```
infrastructure/api → application → domain ← infrastructure/persistence
```

Domain never imports from application, api, or infrastructure.

### Mapper registration order (critical — FK dependency)

Both `main.py` lifespan and `tests/conftest.py` `register_mappers` fixture must register in this exact order:

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

### Adding a new aggregate (e.g. `invoice`)

```
src/domain/invoice/
├── invoice.py       # Aggregate root (extends AggregateRoot)
├── events.py        # InvoiceIssued, InvoicePaid (frozen, kw_only)
├── repository.py    # IInvoiceRepository (DRIVEN PORT)
└── errors.py        # InvoiceNotFoundError, InvoiceAlreadyPaidError

src/domain/shared/invoice_id.py  # VO following ProjectId pattern

src/application/issue_invoice/
├── command.py       # IssueInvoiceCommand DTO
├── handler.py       # IssueInvoiceHandler (USE CASE)
└── ports.py         # IInvoiceUnitOfWork — organizations + invoices repos

src/infrastructure/persistence/sqlalchemy/
├── types.py              # + InvoiceIdType, InvoiceStatusType TypeDecorators
├── tables/invoice_table.py
├── mappers/invoice_mapper.py   # register AFTER organization_mapper
└── invoice_repository.py
```

### Skills available

| Skill | Invoke | Covers |
|-------|--------|--------|
| `python-backend` | `/python-backend` | FastAPI, SQLAlchemy async, JWT/OAuth2, Upstash Redis, rate limiting |
| `clean-ddd-hexagonal` | `/clean-ddd-hexagonal` | DDD patterns, ports & adapters, CQRS, domain events, aggregate design |
| `frontend-design` | `/frontend-design` | UI/UX design patterns, component design, accessibility, responsive layouts |

## Decisiones de diseño tomadas

- Mapeo imperativo (no declarativo) para mantener el dominio limpio de anotaciones SQLAlchemy
- `AbstractUnitOfWork` como context manager async para garantizar atomicidad entre repositorios
- Value objects inmutables con `__eq__` por valor, no identidad
- Rate limiting con slowapi (in-memory) — reemplazar por Redis en producción multi-instancia
- Security headers via middleware propio para control total sin dependencias extra
- **Multi-tenancy dual-layer:** isolación en capa de aplicación (WHERE tenant_id = ?) + PostgreSQL RLS como garantía adicional en producción; SQLite ignora RLS sin errores
- **tenant_id en request body** (Option A) — el cliente envía su tenant UUID al registrarse; el JWT almacena el `tid` claim para requests posteriores
- **TenantMiddleware** extrae `tid` del Bearer JWT antes de que llegue a los routers; rutas públicas definidas como set de tuplas `(method, path)` para O(1) lookup
- **passlib eliminado** — reemplazado por `bcrypt` directo (passlib es incompatible con bcrypt ≥ 5.0)
- **Fixtures de test** con override de todos los handlers en `tests/conftest.py` `client` fixture — inyecta session factory in-memory; evita que el cliente HTTP use el dev.db de producción
- **Refresh token rotation** obligatoria: cada uso de `/auth/refresh` revoca el token viejo y emite uno nuevo; `session.merge()` (no `add()`) para upsert del token revocado sin violar UNIQUE constraint
- **`InvalidRefreshTokenError` → 401** registrado explícitamente en `_STATUS_MAP` del exception handler (hereda de `DomainError` que mapea a 400)
- **Rate limiter** reseteado entre tests via `limiter._storage.reset()` en fixture `autouse=True`; evita que el límite de `/api/v1/users/` (3/min) se agote entre tests de integración
- **FK TypeDecorator rule**: columnas FK en tablas hijo que reciben su valor via SA cascade merge (`cascade="all, delete-orphan"`) DEBEN usar el mismo TypeDecorator que el PK del padre. SA setea el atributo FK al valor del PK del padre (un VO), y el TypeDecorator convierte VO → str en `process_bind_param`. Sin él, el VO llega crudo a SQLite → `ProgrammingError`. Si no hay cascade (se guarda directo via `session.merge(child)`), `String(36)` es seguro.
  - `memberships.org_id` → `OrganizationIdType` (cascade via relationship)
  - `invitations.org_id` → `String(36)` (sin cascade; `session.merge(invitation)` directo)
  - `projects.org_id` → `OrganizationIdType` (queries usan VO en WHERE, necesita TypeDecorator)
  - `deliverables.project_id` → `ProjectIdType` (mismo motivo)
- **StatusType TypeDecorator rule**: columnas de enum/status DEBEN usar un TypeDecorator propio (e.g. `ProjectStatusType`, `DeliverableStatusType`). Sin él, SA devuelve `str` crudo al leer de DB; el router llama `.value` sobre ese str y lanza `AttributeError`. Seguir el patrón de `RoleType`.
- **Handlers retornan objetos de dominio completos** (no solo IDs) — evita re-fetching en el router via `SessionLocal` que bypasea los overrides de test; los routers construyen la respuesta directamente del objeto retornado
- **`InsufficientRoleError` → 403** registrado en `_STATUS_MAP` antes de `DomainError` (regla MRO: subclases primero)
- **`lazy="selectin"`** en relación `_memberships` — la org siempre carga sus memberships en la misma query
- **`cascade="all, delete-orphan"`** en `_memberships` — memberships se persisten como parte del save del aggregate Organization
- **`ListOrganizationsHandler` inyectable** — definido como handler separado para poder hacer override en tests (no hardcodeado en el router)
- **Email fire-and-forget**: `send()` se llama fuera del `async with self._uow` (después del commit). Si falla, se loguea `logger.warning()` pero el request NO falla. Nunca bloquear al usuario por un email que no se pudo enviar.
- **Dos patrones de email**:
  - *Directo* (en handler): para emails críticos sincrónicos — `RegisterUserHandler` → WELCOME, `InviteMemberHandler` → INVITATION.
  - *Event-driven* (EmailEventHandler): para emails reactivos a cambios de estado — suscribe a domain events.
- **`InMemoryEmailSender`** fixture en conftest — compartido entre `client` y test function (mismo scope función). Tests afirman `email_sender.sent` o `email_sender.find_by_to()`.
- **`app_name` en `RegisterUserCommand`** y **`frontend_url` en `InviteMemberCommand`** — los routers inyectan `settings.app_name` y `settings.frontend_url`; la capa de aplicación no importa settings directamente.
- **`email_provider` en settings** (`"console"` | `"resend"`) — determina qué adapter se instancia en `container.py`; `RESEND_API_KEY` solo en `.env`.
- **`IDeliverableUnitOfWork`** definido en `submit_deliverable/ports.py` y reutilizado por `approve_deliverable` y `request_changes` handlers (los tres necesitan projects + deliverables + organizations).
- **Autorización en handlers, no en dominio**: `Project.create()` no valida el rol del creador; esa validación ocurre en `CreateProjectHandler` (fetches org, checks membership role). Mismo patrón en `ApproveDeliverableHandler` y `RequestChangesHandler`.
- **`Decimal` en Invoice**: dominio usa `Decimal`, command recibe `str` (evita float en JSON), handler convierte con `Decimal(command.amount)`, router serializa como `str(invoice.amount)`. SA `Numeric(12, 2)` maneja `Decimal` nativamente — no necesita TypeDecorator.
- **AI call fuera del UoW**: `generate_project_update()` se llama DESPUÉS de `async with self._uow:` para no mantener transacción DB abierta durante HTTP call externo (potencialmente lento).
- **`AiServiceError` como `ApplicationError`** (no `DomainError`) — registrado en `_STATUS_MAP` con código 502; handler dedicado `ai_service_exception_handler()` en `main.py`. Separa errores externos (upstream) de errores de negocio.
- **`IAiSummaryService` fallback**: `container.py` instancia `OpenRouterAiService` si `OPENROUTER_API_KEY` está seteada, sino `InMemoryAiService`. Tests siempre usan override con `InMemoryAiService`.
- **Alembic migrations**: usar `sa.String(N)` en los archivos de migración aunque las tablas Python usen TypeDecorators — la migración solo necesita el tipo de storage, no la conversión Python.

## Lo que NO queremos

- Lógica de negocio en los routers de FastAPI
- Imports de SQLAlchemy en el dominio
- Casos de uso que llamen a otros casos de uso directamente
- Secrets hardcodeados — todo por variables de entorno
- Columnas de enum o status sin TypeDecorator — siempre `String(N)` con TypeDecorator propio
- Handlers que devuelvan solo IDs — siempre devuelven el objeto de dominio completo

## Convenciones de nombres

- Handlers se nombran `VerbNounHandler` (RegisterUserHandler)
- Commands se nombran `VerbNounCommand` (RegisterUserCommand)
- Ports/interfaces llevan prefijo `I` → `IUserRepository`, `ITokenGenerator`
- Clases abstractas de aplicación llevan prefijo `Abstract` → `AbstractPasswordHasher`, `AbstractUnitOfWork`
- Errores de dominio en `domain/{aggregate}/errors.py`
- Mappers idempotentes: global `_mapped = False` + guard con `UnmappedClassError`

## Stack

- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy (async) + pydantic-settings + Alembic (migrations)
- JWT authentication + BcryptPasswordHasher (bcrypt directo, sin passlib)
- slowapi rate limiting (in-memory) — reemplazar por Redis en producción
- structlog + TracingMiddleware (X-Correlation-ID)
- Security headers middleware (HSTS, X-Frame-Options, etc.)
- CORS middleware con whitelist explícita
- httpx — HTTP client para Resend email API
- Resend — transactional email (prod); ConsoleEmailSender (dev); InMemoryEmailSender (tests)
- Environment variables via `.env` (gitignored)

## Current Implementation Status

✅ **Domain shared:** Entity, AggregateRoot, ValueObject, DomainEvent, DomainError, ConflictError, EntityNotFoundError
✅ **Application shared:** AbstractUnitOfWork, AbstractEventPublisher, AbstractPasswordHasher, AbstractEmailSender, EmailMessage, EmailTemplate, build_email()
✅ **User aggregate:** User, UserId, Email, IUserRepository, UserRegistered, UserDeactivated — RegisterUser, LoginUser use cases
✅ **Tenant aggregate:** Tenant, TenantId, ITenantRepository, TenantCreated — multi-tenant isolation via JWT `tid` claim
✅ **Organization aggregate:** OrganizationId/MembershipId/InvitationId VOs, Role enum, Organization + Membership + Invitation entities — 6 use cases (create, list, invite, accept, remove, change_role), 6 REST endpoints
✅ **Auth:** JWT access token + refresh token rotation, POST /auth/login + /auth/refresh + /auth/logout
✅ **Email adapter:** AbstractEmailSender port, ConsoleEmailSender (dev), ResendEmailSender (prod, httpx + retry), InMemoryEmailSender (tests), EmailEventHandler (event-driven), fire-and-forget
✅ **Project aggregate:** ProjectId VO, ProjectStatus enum (ACTIVE/COMPLETED), Project aggregate root — CreateProject (OWNER only), ListProjects use cases, 2 REST endpoints
✅ **Deliverable aggregate:** DeliverableId VO, DeliverableStatus enum (PENDING/APPROVED/CHANGES_REQUESTED), Deliverable aggregate root — SubmitDeliverable, ApproveDeliverable (OWNER|ADMIN), RequestChanges (OWNER|ADMIN) use cases, 3 REST endpoints
✅ **Invoice aggregate:** InvoiceId VO, InvoiceStatus enum (DRAFT/SENT/PAID), Invoice aggregate root (amount: Decimal) — IssueInvoice (OWNER|ADMIN), MarkInvoicePaid (OWNER|ADMIN) use cases, 2 REST endpoints
✅ **AI Summary:** IAiSummaryService port, GenerateClientUpdateHandler, OpenRouterAiService (httpx + retry), InMemoryAiService (tests fallback), GET /api/v1/projects/{id}/summary
✅ **E2E test:** 16-step complete LanceFlow journey (register → login → refresh → org → invite → accept → project → deliverable → approve → invoice → paid → AI summary → logout → verify)
✅ **Alembic migration:** `5887c37e768c` adds projects + deliverables + invoices tables + missing indexes
✅ **Infrastructure:** SQLAlchemy async, imperative mapping, generic SqlAlchemyRepository[T], SqlAlchemyUnitOfWork (8 repos), all TypeDecorators, all tables + mappers
✅ **Security hardening:** CORS, rate limiting (slowapi), security headers, HTTPS redirect (prod), error sanitization
✅ **Tests:** 170 passing — SQLite in-memory, AsyncClient, session-scoped mappers, handler overrides
✅ **Style:** Ruff configured (pyproject.toml)
✅ **Docker:** Dockerfile + docker-compose with pgvector/pg16

✅ **Frontend-ready API:** Tenant lookup/create, GET /users/me, org/project detail, list deliverables/invoices, .env.example

🔜 **Next:** Frontend (Next.js), Stripe integration, Redis rate limiting (multi-instance), WebSocket support

## Development Workflow

1. **Define domain:** Create aggregate in `src/domain/{aggregate}/`
2. **Define use case:** Create handler in `src/application/{use_case}/`
3. **Implement adapter:** Create SQLAlchemy table + mapper + repository in `src/infrastructure/persistence/sqlalchemy/`
4. **Wire:** Add TypeDecorators to `types.py`, register mapper in `main.py` lifespan + `conftest.py`, add repo to `unit_of_work.py`, add factory to `container.py`, add handler override to `conftest.py` client fixture
5. **Create API route:** Add endpoint in `src/infrastructure/api/routers/{aggregate}.py`, include router in `main.py`
6. **Run migrations:** `uv run alembic upgrade head`
7. **Test:** `uv run pytest`

## API Endpoints

| Method | Path | Auth | Rate limit | Handler |
|--------|------|------|-----------|---------|
| `GET` | `/health` | ❌ | — | inline |
| `GET` | `/api/v1/tenants/by-slug/{slug}` | ❌ | 20/min | GetTenantBySlugHandler |
| `POST` | `/api/v1/tenants` | ❌ | 5/min | CreateTenantHandler |
| `POST` | `/api/v1/users/` | ❌ | 3/min | RegisterUserHandler |
| `GET` | `/api/v1/users/me` | ✅ JWT | 60/min | GetCurrentUserHandler |
| `POST` | `/api/v1/auth/login` | ❌ | 5/min | LoginUserHandler |
| `POST` | `/api/v1/auth/refresh` | ❌ | 10/min | RefreshTokenHandler |
| `POST` | `/api/v1/auth/logout` | ❌ | 10/min | LogoutHandler |
| `POST` | `/api/v1/organizations` | ✅ JWT | 30/min | CreateOrganizationHandler |
| `GET` | `/api/v1/organizations` | ✅ JWT | 60/min | ListOrganizationsHandler |
| `GET` | `/api/v1/organizations/{id}` | ✅ JWT | 60/min | GetOrganizationHandler |
| `GET` | `/api/v1/organizations/{id}/invoices` | ✅ JWT | 60/min | ListInvoicesHandler |
| `POST` | `/api/v1/organizations/{id}/invitations` | ✅ JWT | 30/min | InviteMemberHandler |
| `POST` | `/api/v1/organizations/{id}/invitations/{inv_id}/accept` | ✅ JWT | 30/min | AcceptInvitationHandler |
| `DELETE` | `/api/v1/organizations/{id}/members/{uid}` | ✅ JWT | 30/min | RemoveMemberHandler |
| `PATCH` | `/api/v1/organizations/{id}/members/{uid}/role` | ✅ JWT | 30/min | ChangeMemberRoleHandler |
| `POST` | `/api/v1/projects` | ✅ JWT | 30/min | CreateProjectHandler |
| `GET` | `/api/v1/projects` | ✅ JWT | 60/min | ListProjectsHandler |
| `GET` | `/api/v1/projects/{id}` | ✅ JWT | 60/min | GetProjectHandler |
| `GET` | `/api/v1/projects/{id}/deliverables` | ✅ JWT | 60/min | ListDeliverablesHandler |
| `GET` | `/api/v1/projects/{id}/summary` | ✅ JWT | 10/min | GenerateClientUpdateHandler |
| `POST` | `/api/v1/projects/{id}/deliverables` | ✅ JWT | 30/min | SubmitDeliverableHandler |
| `PATCH` | `/api/v1/deliverables/{id}/approve` | ✅ JWT | 30/min | ApproveDeliverableHandler |
| `PATCH` | `/api/v1/deliverables/{id}/request-changes` | ✅ JWT | 30/min | RequestChangesHandler |
| `POST` | `/api/v1/organizations/{id}/invoices` | ✅ JWT | 30/min | IssueInvoiceHandler |
| `PATCH` | `/api/v1/invoices/{id}/paid` | ✅ JWT | 30/min | MarkInvoicePaidHandler |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./dev.db` | DB connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key (≥32 chars en prod) |
| `ENVIRONMENT` | `development` | `production` activa validaciones de seguridad |
| `JWT_EXPIRE_MINUTES` | `30` | Duración del access token |
| `REFRESH_TOKEN_TTL_DAYS` | `30` | Duración del refresh token |
| `ALLOWED_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | CORS whitelist |
| `EMAIL_PROVIDER` | `console` | `console` \| `resend` |
| `RESEND_API_KEY` | `None` | API key de Resend (solo en prod) |
| `EMAIL_FROM` | `noreply@example.com` | Dirección remitente por defecto |
| `FRONTEND_URL` | `http://localhost:3000` | Base URL para links en emails |
| `APP_NAME` | `boiler-plate-saas` | Nombre del producto (usado en emails) |
| `OPENROUTER_API_KEY` | `None` | API key de OpenRouter (AI summary en prod) |
| `AI_MODEL` | `openai/gpt-4o-mini` | Modelo a usar via OpenRouter |

## Error Response Format

All errors follow this JSON envelope:

```json
{
  "error": {
    "message": "descripción del error"
  }
}
```

HTTP status codes:
- `400` → DomainError (business validation)
- `401` → Not authenticated / invalid token
- `403` → InsufficientRoleError
- `404` → EntityNotFoundError
- `409` → ConflictError (duplicate slug, etc.)
- `422` → Pydantic validation error
- `429` → Rate limit exceeded
- `502` → AiServiceError (upstream failure)

<!-- reglas loop -->
antes de compactar las conversaciones sube a engram lo mas importante de ellas 