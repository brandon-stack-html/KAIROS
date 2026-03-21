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
│   │   └── errors.py                # DomainError, EntityNotFoundError, ConflictError
│   └── user/ ✅                     # User aggregate
│       ├── user.py                  # Aggregate root + UserId, Email value objects
│       ├── repository.py            # IUserRepository (DRIVEN PORT)
│       ├── events.py                # UserRegistered, UserDeactivated
│       └── errors.py                # InvalidEmailError, InvalidUserNameError
│
├── application/                     # Use cases — orchestrates domain, defines ports
│   ├── shared/
│   │   ├── unit_of_work.py          # AbstractUnitOfWork (async context manager)
│   │   ├── event_publisher.py       # AbstractEventPublisher
│   │   ├── password_hasher.py       # AbstractPasswordHasher (DRIVEN PORT)
│   │   └── errors.py                # NotFoundError, ConflictError
│   ├── register_user/ ✅            # Use case: POST /users
│   │   ├── command.py
│   │   ├── handler.py
│   │   └── ports.py
│   └── login_user/ ✅               # Use case: POST /auth/login
│       ├── command.py
│       ├── handler.py
│       └── ports.py
│
└── infrastructure/                  # Adapters — implements ports defined in domain/application
    ├── api/ ✅                       # Presentation layer — FastAPI entry point
    │   ├── main.py                  # FastAPI app + lifespan + CORS + security middleware
    │   ├── dependencies.py          # get_current_user — JWT Bearer dependency for protected routes
    │   ├── rate_limiter.py          # Shared slowapi Limiter instance
    │   ├── logging.py               # structlog configuration helper
    │   ├── routers/
    │   │   ├── users.py             # POST /api/v1/users (rate limited)
    │   │   └── auth.py              # POST /api/v1/auth/login (rate limited)
    │   ├── middleware/
    │   │   ├── exception_handler.py # GlobalErrorHandler → JSON error envelope
    │   │   ├── security_headers.py  # X-Frame-Options, HSTS, X-Content-Type-Options, etc.
    │   │   └── tracing.py           # TracingMiddleware — X-Correlation-ID per request
    │   └── schemas/
    │       └── user_schemas.py      # UserCreate, UserResponse, LoginResponse
    ├── config/
    │   ├── settings.py              # pydantic-settings — reads from .env
    │   └── container.py             # Composition root — wire all dependencies here
    ├── persistence/
    │   ├── sqlalchemy/
    │   │   ├── database.py          # Async engine + metadata
    │   │   ├── types.py             # Custom column types
    │   │   ├── repository.py        # Generic SqlAlchemyRepository[T]
    │   │   ├── tables/
    │   │   │   └── users_table.py   # Table definition (imperative mapping)
    │   │   ├── mappers/
    │   │   │   └── user_mapper.py   # start_mappers() — maps User domain → ORM table
    │   │   ├── user_repository.py   # SqlAlchemyUserRepository
    │   │   └── unit_of_work.py      # SqlAlchemyUnitOfWork
    │   └── in_memory/               # In-memory repos for unit tests
    ├── security/
    │   ├── jwt_handler.py           # JwtTokenGenerator.generate() + decode_token()
    │   └── password_hasher.py       # BcryptPasswordHasher
    ├── messaging/
    │   └── in_memory/               # In-memory event publisher for tests
    └── external/                    # Third-party service adapters (Stripe, email, etc.)
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

## Decisiones de diseño tomadas

- Mapeo imperativo (no declarativo) para mantener el dominio limpio de anotaciones SQLAlchemy
- `AbstractUnitOfWork` como context manager async para garantizar atomicidad entre repositorios
- Value objects inmutables con `__eq__` por valor, no identidad
- Rate limiting con slowapi (in-memory) — reemplazar por Redis en producción multi-instancia
- Security headers via middleware propio para control total sin dependencias extra

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
- JWT authentication + BcryptPasswordHasher
- slowapi rate limiting (in-memory)
- structlog + TracingMiddleware (X-Correlation-ID)
- Security headers middleware (HSTS, X-Frame-Options, etc.)
- CORS middleware con whitelist explícita
- Environment variables via `.env` (gitignored)

## Current Implementation Status

✅ **Domain:** Entity, AggregateRoot, ValueObject, DomainEvent, DomainError, ConflictError, EntityNotFoundError
✅ **Application shared:** AbstractUnitOfWork, AbstractEventPublisher, AbstractPasswordHasher
✅ **User aggregate:** User, UserId, Email, IUserRepository, UserRegistered, UserDeactivated
✅ **Use cases:** RegisterUser, LoginUser (JWT)
✅ **Infrastructure API:** FastAPI app, /health, users + auth routers, GlobalErrorHandler
✅ **Infrastructure persistence:** SQLAlchemy async, imperative mapping, generic SqlAlchemyRepository[T], SqlAlchemyUnitOfWork
✅ **Infrastructure security:** BcryptPasswordHasher, JwtTokenGenerator, decode_token, get_current_user dependency
✅ **Observability:** structlog + TracingMiddleware (X-Correlation-ID)
✅ **Security hardening:** CORS, rate limiting (slowapi), security headers, HTTPS redirect (prod), error sanitization
✅ **Migrations:** Alembic configured, initial migration applied
✅ **Tests:** SQLite in-memory fixtures, AsyncClient, session-scoped mappers
✅ **Style:** Ruff configured (pyproject.toml)
✅ **Docker:** Dockerfile + docker-compose with pgvector/pg16

🔜 **Next:** Multi-tenancy (tenant_id on aggregates), Stripe integration, email sending adapter, refresh token endpoint, Redis rate limiting (multi-instance)

## Development Workflow

1. **Define domain:** Create aggregate in `src/domain/{aggregate}/`
2. **Define use case:** Create handler in `src/application/{use_case}/`
3. **Implement adapter:** Create SQLAlchemy table + mapper + repository in `src/infrastructure/persistence/sqlalchemy/`
4. **Create API route:** Add endpoint in `src/infrastructure/api/routers/{aggregate}.py`
5. **Run migrations:** `uv run alembic upgrade head`
6. **Test:** `uv run pytest`
