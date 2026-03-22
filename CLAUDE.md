# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> This is a **SaaS boilerplate**. Every new SaaS project starts from this structure.
> Keep it generic — no domain-specific code belongs here.

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
uv run pytest                                           # Run all tests
uv run pytest tests/path/to_test.py::test_name          # Run a single test
```

## Sub-Agentes

Claude Code = Arquitecto Jefe / Orquestador.

| Agente | Rol | Comando |
|--------|-----|---------|
| **Gemini** | Auditoría de contexto — coherencia DDD, errores entre módulos | `gemini --prompt "[instrucción]"` |
| **Aider/OpenRouter** | Escritura bruta — Repositories, Entities, Unit Tests | `aider --model gpt-4o-mini --message "[instrucción]"` |

> **Nota técnica:** Aider usa `OPENAI_API_BASE=https://openrouter.ai/api/v1` para enrutar a OpenRouter.
> Ambas variables están configuradas en `~/.claude/settings.json`.

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
│   └── organization/ ✅             # Organization aggregate
│       ├── organization.py          # Aggregate root — create(), add_member(), remove_member(), change_member_role(), dissolve()
│       ├── membership.py            # Membership entity (org_id: OrganizationId, NOT str — SA cascade)
│       ├── invitation.py            # Invitation entity — create(), accept(), is_expired() (org_id: str)
│       ├── repository.py            # IOrganizationRepository + IInvitationRepository (DRIVEN PORTS)
│       ├── events.py                # OrganizationCreated, MemberAdded, MemberRemoved, MemberRoleChanged, OrganizationDissolved, InvitationSent, InvitationAccepted
│       └── errors.py                # OrganizationNotFoundError, MemberAlreadyExistsError, MemberNotFoundError, InsufficientRoleError, CannotRemoveLastOwnerError, InvitationExpiredError, InvitationAlreadyAcceptedError, InvalidOrgNameError, InvalidOrgSlugError
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
│   └── change_member_role/ ✅       # Use case: PATCH /api/v1/organizations/{id}/members/{uid}/role
│       ├── command.py               # ChangeMemberRoleCommand(org_id, changer_id, user_id, new_role, tenant_id)
│       ├── handler.py               # Returns full Organization
│       └── ports.py
│
└── infrastructure/                  # Adapters — implements ports defined in domain/application
    ├── api/ ✅                       # Presentation layer — FastAPI entry point
    │   ├── main.py                  # FastAPI app + lifespan + middleware chain
    │   ├── dependencies.py          # get_current_user — JWT Bearer dependency
    │   ├── rate_limiter.py          # Shared slowapi Limiter instance
    │   ├── logging.py               # structlog configuration helper
    │   ├── routers/
    │   │   ├── users.py             # POST /api/v1/users (rate limited)
    │   │   ├── auth.py              # POST /login, /refresh, /logout (all rate limited)
    │   │   └── organizations.py     # 6 org endpoints — all JWT-protected, 30/min rate limit
    │   ├── middleware/
    │   │   ├── exception_handler.py # GlobalErrorHandler → JSON error envelope
    │   │   ├── security_headers.py  # X-Frame-Options, HSTS, X-Content-Type-Options, etc.
    │   │   ├── tracing.py           # TracingMiddleware — X-Correlation-ID per request
    │   │   └── tenant.py            # TenantMiddleware — extracts 'tid' from JWT, 401 if missing
    │   └── schemas/
    │       ├── user_schemas.py      # UserCreate (tenant_id: UUID), UserResponse, LoginResponse
    │       └── organization_schemas.py  # OrgCreate, OrgResponse, MemberResponse, InvitationCreate, InvitationResponse, ChangeMemberRoleRequest
    ├── config/
    │   ├── settings.py              # pydantic-settings — reads from .env
    │   └── container.py             # Composition root — wire all dependencies here
    ├── persistence/
    │   ├── sqlalchemy/
    │   │   ├── database.py          # Async engine + metadata
    │   │   ├── types.py             # Custom column types — TenantIdType, OrganizationIdType, MembershipIdType, InvitationIdType, RoleType, UserIdType, UserEmailType
    │   │   ├── repository.py        # Generic SqlAlchemyRepository[T]
    │   │   ├── tenant_context.py    # set_tenant() — SET LOCAL for PostgreSQL RLS
    │   │   ├── tables/
    │   │   │   ├── users_table.py         # users table + tenant_id FK + composite index
    │   │   │   ├── tenants_table.py       # tenants table definition
    │   │   │   ├── organizations_table.py # organizations — tenant_id FK, unique (tenant_id, slug)
    │   │   │   ├── memberships_table.py   # memberships — org_id: OrganizationIdType (cascade FK!)
    │   │   │   └── invitations_table.py   # invitations — org_id: String(36) (no cascade, direct merge)
    │   │   ├── mappers/
    │   │   │   ├── user_mapper.py         # start_mappers() — maps User domain → ORM table
    │   │   │   ├── tenant_mapper.py       # start_mappers() — maps Tenant domain → ORM table
    │   │   │   ├── organization_mapper.py # Maps Membership first, then Organization with selectin _memberships + cascade
    │   │   │   └── invitation_mapper.py   # Maps Invitation → invitations_table
    │   │   ├── user_repository.py          # SqlAlchemyUserRepository (tenant-scoped WHERE)
    │   │   ├── tenant_repository.py        # SqlAlchemyTenantRepository
    │   │   ├── refresh_token_repository.py # SqlAlchemyRefreshTokenStore (merge-based upsert)
    │   │   ├── organization_repository.py  # SqlAlchemyOrganizationRepository (merge + JOIN find_by_user)
    │   │   ├── invitation_repository.py    # SqlAlchemyInvitationRepository (merge-based upsert)
    │   │   └── unit_of_work.py             # SqlAlchemyUnitOfWork (users + tenants + refresh_tokens + organizations + invitations)
        │   └── in_memory/
    │       ├── refresh_token_store.py   # InMemoryRefreshTokenStore (tests)
    │       └── email_sender.py          # InMemoryEmailSender — captures sent emails for test assertions
    ├── security/
    │   ├── jwt_handler.py           # JwtTokenGenerator — adds 'tid' claim to JWT
    │   └── password_hasher.py       # BcryptPasswordHasher (bcrypt direct, no passlib)
    ├── messaging/
    │   ├── in_memory/               # In-memory event publisher for tests
    │   └── email_event_handler.py   # EmailEventHandler — reacts to InvitationSent domain event
    └── external/
        └── email/
            ├── console_email_sender.py  # ConsoleEmailSender — prints to stdout via structlog (dev)
            └── resend_email_sender.py   # ResendEmailSender — calls Resend API (prod), 3 attempts + backoff
```

### Dependency rule

```
infrastructure/api → application → domain ← infrastructure/persistence
```

Domain never imports from application, api, or infrastructure.

### Adding a new aggregate (e.g. `subscription`)

Create one folder per aggregate following this pattern:

```
src/domain/subscription/
├── subscription.py      # Aggregate root (extends AggregateRoot)
├── value_objects.py     # SubscriptionId, Plan, etc.
├── events.py            # SubscriptionCreated, SubscriptionCancelled, etc.
├── repository.py        # ISubscriptionRepository interface (DRIVEN PORT)
├── services.py          # Domain services if needed
└── errors.py            # SubscriptionNotFoundError, etc.

src/application/create_subscription/
├── command.py           # CreateSubscriptionCommand DTO
├── handler.py           # CreateSubscriptionHandler (USE CASE)
└── ports.py             # ICreateSubscriptionUseCase interface

src/infrastructure/persistence/sqlalchemy/
├── tables/subscription_table.py
├── mappers/subscription_mapper.py
└── subscription_repository.py
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
- **Fixtures de test** con override de todos los handlers (`get_register_user_handler`, `get_login_user_handler`, `get_refresh_token_handler`, `get_logout_handler`) para inyectar la session factory in-memory; evita que el cliente HTTP use el dev.db de producción
- **Refresh token rotation** obligatoria: cada uso de `/auth/refresh` revoca el token viejo y emite uno nuevo; `session.merge()` (no `add()`) para upsert del token revocado sin violar UNIQUE constraint
- **`InvalidRefreshTokenError` → 401** registrado explícitamente en `_STATUS_MAP` del exception handler (hereda de `DomainError` que mapea a 400)
- **Rate limiter** reseteado entre tests via `limiter._storage.reset()` en fixture `autouse=True`; evita que el límite de `/api/v1/users/` (3/min) se agote entre tests de integración
- **FK TypeDecorator rule**: columnas FK en tablas hijo que reciben su valor via SA cascade merge (`cascade="all, delete-orphan"`) DEBEN usar el mismo TypeDecorator que el PK del padre. SA setea el atributo FK al valor del PK del padre (un VO), y el TypeDecorator convierte VO → str en `process_bind_param`. Sin él, el VO llega crudo a SQLite → `ProgrammingError`. Si no hay cascade (se guarda directo via `session.merge(child)`), `String(36)` es seguro.
  - `memberships.org_id` → `OrganizationIdType` (cascade via relationship)
  - `invitations.org_id` → `String(36)` (sin cascade; `session.merge(invitation)` directo)
- **Handlers retornan objetos de dominio completos** (no solo IDs) — evita re-fetching en el router via `SessionLocal` que bypasea los overrides de test; los routers construyen la respuesta directamente del objeto retornado
- **`InsufficientRoleError` → 403** registrado en `_STATUS_MAP` antes de `DomainError` (regla MRO: subclases primero)
- **`lazy="selectin"`** en relación `_memberships` — la org siempre carga sus memberships en la misma query
- **`cascade="all, delete-orphan"`** en `_memberships` — memberships se persisten como parte del save del aggregate Organization
- **`ListOrganizationsHandler` inyectable** — definido como handler separado para poder hacer override en tests (no hardcodeado en el router)
- **Email fire-and-forget**: `send()` se llama fuera del `async with self._uow` (después del commit). Si falla, se loguea `logger.warning()` pero el request NO falla. Nunca bloquear al usuario por un email que no se pudo enviar.
- **Dos patrones de email**:
  - *Directo* (en handler): para emails críticos sincrónicos — `RegisterUserHandler` → WELCOME, `InviteMemberHandler` → INVITATION. El handler tiene el contexto necesario (org.name, etc.) sin consultas extra.
  - *Event-driven* (EmailEventHandler): para emails reactivos a cambios de estado — suscribe a domain events publicados por el aggregate. Usar cuando el use case no debe saber nada de emails o cuando el mismo evento dispara acciones en múltiples handlers.
- **`InMemoryEmailSender`** fixture en conftest — compartido entre `client` y test function (mismo scope función). Tests afirman `email_sender.sent` o `email_sender.find_by_to()`.
- **`app_name` en `RegisterUserCommand`** y **`frontend_url` en `InviteMemberCommand`** — los routers inyectan `settings.app_name` y `settings.frontend_url`; la capa de aplicación no importa settings directamente.
- **`email_provider` en settings** (`"console"` | `"resend"`) — determina qué adapter se instancia en `container.py`; `RESEND_API_KEY` solo en `.env`.

## Lo que NO queremos en este boilerplate

- Lógica de negocio en los routers de FastAPI
- Imports de SQLAlchemy en el dominio
- Casos de uso que llamen a otros casos de uso directamente
- Secrets hardcodeados — todo por variables de entorno

## Convenciones de nombres

- Handlers se nombran `VerbNounHandler` (RegisterUserHandler)
- Commands se nombran `VerbNounCommand` (RegisterUserCommand)
- Ports/interfaces llevan prefijo `I` → `IUserRepository`, `ITokenGenerator`
- Clases abstractas de aplicación llevan prefijo `Abstract` → `AbstractPasswordHasher`, `AbstractUnitOfWork`
- Errores de dominio en `domain/{aggregate}/errors.py`

## Contexto del negocio

- Es un boilerplate SaaS B2B multi-tenant
- Se clona para iniciar nuevos proyectos, no se modifica directamente
- Cada nuevo SaaS agrega sus propios agregados encima

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

✅ **Domain:** Entity, AggregateRoot, ValueObject, DomainEvent, DomainError, ConflictError, EntityNotFoundError
✅ **Application shared:** AbstractUnitOfWork, AbstractEventPublisher, AbstractPasswordHasher, AbstractEmailSender, EmailMessage, EmailTemplate, build_email()
✅ **User aggregate:** User, UserId, Email, IUserRepository, UserRegistered, UserDeactivated
✅ **Use cases:** RegisterUser, LoginUser (JWT)
✅ **Infrastructure API:** FastAPI app, /health, users + auth routers, GlobalErrorHandler
✅ **Infrastructure persistence:** SQLAlchemy async, imperative mapping, generic SqlAlchemyRepository[T], SqlAlchemyUnitOfWork
✅ **Infrastructure security:** BcryptPasswordHasher, JwtTokenGenerator, decode_token, get_current_user dependency
✅ **Observability:** structlog + TracingMiddleware (X-Correlation-ID)
✅ **Security hardening:** CORS, rate limiting (slowapi), security headers, HTTPS redirect (prod), error sanitization
✅ **Migrations:** Alembic configured, initial migration applied
✅ **Tests:** SQLite in-memory fixtures, AsyncClient, session-scoped mappers, handler overrides for test isolation
✅ **Style:** Ruff configured (pyproject.toml)
✅ **Docker:** Dockerfile + docker-compose with pgvector/pg16
✅ **Multi-tenancy:** TenantId value object, Tenant aggregate, tenant_id on User, TenantMiddleware (JWT `tid` claim), repository-level WHERE filters, PostgreSQL RLS migration, 5 integration tests
✅ **Refresh tokens:** RefreshToken value object, AbstractRefreshTokenStore port, token rotation, InMemoryRefreshTokenStore (tests), SqlAlchemyRefreshTokenStore, POST /auth/refresh + POST /auth/logout endpoints, 10 unit tests + 5 integration tests
✅ **Organization aggregate:** OrganizationId/MembershipId/InvitationId VOs, Role enum (OWNER/ADMIN/MEMBER), Organization aggregate root with Membership + Invitation entities, 6 use cases (create, list, invite, accept, remove, change_role), 6 REST endpoints, PostgreSQL RLS migration, 35 tests total (11 unit + 4 integration + existing)
✅ **Email adapter:** AbstractEmailSender port, EmailMessage DTO, EmailTemplate enum, build_email() renderer, ConsoleEmailSender (dev), ResendEmailSender (prod, httpx + retry), InMemoryEmailSender (tests), EmailEventHandler (event-driven), fire-and-forget integration in RegisterUser + InviteMember, 50 tests total

🔜 **Next:** Stripe integration, Redis rate limiting (multi-instance)

## Development Workflow

1. **Define domain:** Create aggregate in `src/domain/{aggregate}/`
2. **Define use case:** Create handler in `src/application/{use_case}/`
3. **Implement adapter:** Create SQLAlchemy table + mapper + repository in `src/infrastructure/persistence/sqlalchemy/`
4. **Create API route:** Add endpoint in `src/infrastructure/api/routers/{aggregate}.py`
5. **Run migrations:** `uv run alembic upgrade head`
6. **Test:** `uv run pytest`

## API Endpoints

| Method | Path | Auth | Rate limit | Handler |
|--------|------|------|-----------|---------|
| `GET` | `/health` | ❌ | — | inline |
| `POST` | `/api/v1/users/` | ❌ | 3/min | RegisterUserHandler |
| `POST` | `/api/v1/auth/login` | ❌ | 5/min | LoginUserHandler |
| `POST` | `/api/v1/auth/refresh` | ❌ | 10/min | RefreshTokenHandler |
| `POST` | `/api/v1/auth/logout` | ❌ | 10/min | LogoutHandler |
| `POST` | `/api/v1/organizations` | ✅ JWT | 30/min | CreateOrganizationHandler |
| `GET` | `/api/v1/organizations` | ✅ JWT | 60/min | ListOrganizationsHandler |
| `POST` | `/api/v1/organizations/{id}/invitations` | ✅ JWT | 30/min | InviteMemberHandler |
| `POST` | `/api/v1/organizations/{id}/invitations/{inv_id}/accept` | ✅ JWT | 30/min | AcceptInvitationHandler |
| `DELETE` | `/api/v1/organizations/{id}/members/{uid}` | ✅ JWT | 30/min | RemoveMemberHandler |
| `PATCH` | `/api/v1/organizations/{id}/members/{uid}/role` | ✅ JWT | 30/min | ChangeMemberRoleHandler |

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
| `FRONTEND_URL` | `http://localhost:3000` | Base URL para links en emails (accept invitation, etc.) |
| `APP_NAME` | `boiler-plate-saas` | Nombre del producto (usado en emails) |
