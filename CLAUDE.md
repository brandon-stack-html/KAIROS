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
│   │   ├── password_hasher.py       # IPasswordHasher (DRIVEN PORT)
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
    │   ├── main.py                  # FastAPI app + lifespan + /health
    │   ├── routers/
    │   │   ├── users.py             # POST /api/v1/users
    │   │   └── auth.py              # POST /api/v1/auth/login
    │   ├── middleware/
    │   │   └── exception_handler.py # GlobalErrorHandler → JSON error envelope
    │   └── schemas/
    │       └── user_schemas.py      # UserCreate, UserResponse, LoginResponse
    ├── config/
    │   ├── settings.py              # pydantic-settings — reads from .env
    │   └── container.py             # Composition root — wire all dependencies here
    ├── persistence/
    │   ├── sqlalchemy/
    │   │   ├── database.py          # Async engine + metadata
    │   │   ├── types.py             # Custom column types
    │   │   ├── tables/
    │   │   │   └── users_table.py   # Table definition (imperative mapping)
    │   │   ├── mappers/
    │   │   │   └── user_mapper.py   # start_mappers() — maps User domain → ORM table
    │   │   ├── user_repository.py   # SqlAlchemyUserRepository
    │   │   └── unit_of_work.py      # SqlAlchemyUnitOfWork
    │   └── in_memory/               # In-memory repos for unit tests
    ├── security/
    │   ├── jwt_handler.py           # create_access_token, decode_token
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

### Adding a new aggregate (e.g. `user`)

Create one folder per aggregate following this pattern:

```
src/domain/user/
├── user.py              # Aggregate root (extends AggregateRoot)
├── value_objects.py     # Email, UserId, etc.
├── events.py            # UserRegistered, UserDeactivated, etc.
├── repository.py        # IUserRepository interface (DRIVEN PORT)
├── services.py          # Domain services if needed
└── errors.py            # UserNotFoundError, EmailAlreadyTakenError, etc.

src/application/register_user/
├── command.py           # RegisterUserCommand DTO
├── handler.py           # RegisterUserHandler (USE CASE)
└── port.py              # IRegisterUserUseCase interface

src/infrastructure/persistence/sqlalchemy/
├── models/user_model.py
└── mappers/user_mapper.py
```

### Skills available

| Skill | Invoke | Covers |
|-------|--------|--------|
| `python-backend` | `/python-backend` | FastAPI, SQLAlchemy async, JWT/OAuth2, Upstash Redis, rate limiting |
| `clean-ddd-hexagonal` | `/clean-ddd-hexagonal` | DDD patterns, ports & adapters, CQRS, domain events, aggregate design |

## Stack

- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy (async) + pydantic-settings + Alembic (migrations)
- JWT authentication + error handling middleware
- Environment variables via `.env` (gitignored)

## Current Implementation Status

✅ **Domain:** Entity, AggregateRoot, ValueObject, DomainEvent, DomainError, ConflictError, EntityNotFoundError
✅ **Application shared:** AbstractUnitOfWork, AbstractEventPublisher, IPasswordHasher
✅ **User aggregate:** User, UserId, Email, IUserRepository, UserRegistered, UserDeactivated
✅ **Use cases:** RegisterUser, LoginUser (JWT)
✅ **Infrastructure API:** FastAPI app, /health, users + auth routers, GlobalErrorHandler
✅ **Infrastructure persistence:** SQLAlchemy async, imperative mapping, SqlAlchemyUnitOfWork
✅ **Infrastructure security:** BcryptPasswordHasher, JWT handler
✅ **Migrations:** Alembic configured, initial migration applied
✅ **Style:** Ruff configured (pyproject.toml)

🔜 **Next:** Generic SQLAlchemyRepository[T], TracingMiddleware + structlog, Docker + pgvector, test fixtures

## Development Workflow

1. **Define domain:** Create aggregate in `src/domain/{aggregate}/`
2. **Define use case:** Create handler in `src/application/{use_case}/`
3. **Implement adapter:** Create SQLAlchemy model and mapper in `src/infrastructure/persistence/sqlalchemy/`
4. **Create API route:** Add endpoint in `src/infrastructure/api/routers/{aggregate}.py`
5. **Run migrations:** `uv run alembic upgrade head`
6. **Test:** `uv run pytest`
