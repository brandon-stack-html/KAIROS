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

No linter is configured yet. Add `ruff` via `uv add --dev ruff` when ready.

## subagentes
# Instrucciones de Orquestación

Eres el Arquitecto Jefe. Tienes dos sub-agentes a tu disposición vía terminal:

1. **Sub-Agente Gemini (@gemini):** Úsalo para "Auditoría de Contexto". 
   - Comando: `gemini --prompt "[instrucción]"`
   - Úsalo cuando el usuario pida revisar coherencia en múltiples módulos o buscar errores de DDD en todo el repo.

2. **Sub-Agente Codex (@codex):** Úsalo para "Escritura de Fuerza Bruta".
   - Comando: `aider --model openrouter/openai/gpt-5-codex --message "[instrucción]"`
   - Úsalo para generar Repositories, Entities o Unit Tests siguiendo el patrón hexagonal.

**Regla de Oro:** Siempre guarda el resultado de lo que hagan ellos en **Engram** usando `engram save "[resumen]"` para no perder el hilo.

## Architecture

Clean Architecture + DDD + Hexagonal (ports & adapters). Four layers under `src/`:

```
src/
├── domain/                          # Pure business logic — ZERO external dependencies
│   └── shared/                      # Base building blocks (reuse in every aggregate)
│       ├── entity.py                # Entity[TId] — equality by identity
│       ├── aggregate_root.py        # AggregateRoot[TId] — manages domain events
│       ├── value_object.py          # ValueObject — immutable, equality by value
│       ├── domain_event.py          # DomainEvent — base for all domain events
│       └── errors.py                # DomainError base
│
├── application/                     # Use cases — orchestrates domain, defines ports
│   └── shared/
│       ├── unit_of_work.py          # AbstractUnitOfWork (async context manager)
│       ├── event_publisher.py       # AbstractEventPublisher
│       └── errors.py                # NotFoundError, ConflictError
│
├── api/                             # Presentation layer — FastAPI entry point
│   ├── main.py                      # FastAPI app + /health
│   ├── routers/                     # One router per aggregate/feature
│   ├── middleware/                  # Auth, error handling, logging
│   └── schemas/                     # Pydantic request/response models
│
└── infrastructure/                  # Adapters — implements ports defined in domain/application
    ├── config/
    │   ├── settings.py              # pydantic-settings — reads from .env
    │   └── container.py             # Composition root — wire all dependencies here
    ├── persistence/
    │   ├── sqlalchemy/
    │   │   ├── database.py          # Async engine, SessionLocal, Base
    │   │   ├── models/              # SQLAlchemy ORM models (one file per aggregate)
    │   │   └── mappers/             # Domain ↔ ORM mapping functions
    │   └── in_memory/               # In-memory repos for unit tests
    ├── messaging/
    │   └── in_memory/               # In-memory event publisher for tests
    └── external/                    # Third-party service adapters (Stripe, email, etc.)
```

### Dependency rule

```
api → application → domain ← infrastructure
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
- SQLAlchemy (async) + pydantic-settings
- Environment variables via `.env` (gitignored)
