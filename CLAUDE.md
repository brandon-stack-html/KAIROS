# CLAUDE.md

> **Kairos** — Client Portal for Freelancers.
> Domains: User, Tenant, Organization, Project, Deliverable, Invoice, Conversation, Message, Document.

## Commands

```bash
# Backend
uv sync                                                  # Install dependencies
uv run uvicorn src.infrastructure.api.main:app --reload   # Dev server
uv run pytest                                             # All 227 tests
uv run pytest tests/path/to_test.py::test_name            # Single test
uv run ruff check . --fix --unsafe-fixes                  # Lint + auto-fix
uv run ruff format .                                      # Format
uv run alembic upgrade head                               # Run migrations

# Frontend (inside /frontend)
npm install                     # Install dependencies
npm run dev                     # Dev server (port 3000)
npm run build                   # Production build check
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
| User | User, UserId, Email, avatar_url(optional) | — |
| Tenant | Tenant, TenantId, slug | — |
| Organization | Organization, Membership, Invitation, Role(OWNER/ADMIN/MEMBER) | — |
| Project | Project, ProjectId | ACTIVE, COMPLETED |
| Deliverable | Deliverable, DeliverableId | PENDING, APPROVED, CHANGES_REQUESTED |
| Invoice | Invoice, InvoiceId, amount(Decimal) | DRAFT, SENT, PAID |
| Conversation | Conversation, ConversationId, ConversationType(ORG\|PROJECT) | — |
| Message | Message, MessageId, content(1–4000 chars) | — |
| Document | Document, DocumentId, MAX_FILE_SIZE=10MB, ALLOWED_FILE_TYPES(9 MIME) | — |

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
start_invoice_mappers()        # 8 — FK → organizations + tenants
start_conversation_mappers()   # 9 — FK → organizations + projects
start_message_mappers()        # 10 — FK → conversations
start_document_mappers()       # 11 — FK → organizations + projects
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
- **File storage outside UoW**: `IFileStorage.delete()` called AFTER `async with self._uow` closes (same pattern as AI/email)
- **Multipart upload**: FastAPI `UploadFile`, `await file.read()` → bytes → pass to command. Do NOT set Content-Type manually (Axios detects it)
- **Download endpoint**: returns `FileResponse(path=storage_path, filename=..., media_type=...)` — NOT JSON
- **IFileStorage port**: lives in `src/application/shared/file_storage.py` (shared, like IAiSummaryService)
- **Read models (stats/aggregates)**: use a frozen `@dataclass` in the handler file — NOT a domain entity. No ID, no mapper, no migration, no repo. `DashboardStats` es el ejemplo canónico
- **Cross-cutting queries**: agregar `find_by_tenant(tenant_id)` al repo cuando se necesita agregar sobre todo el tenant (evita N+1). Ejemplo: `IDeliverableRepository.find_by_tenant`, `IInvoiceRepository.find_by_tenant`

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
| `PATCH` | `/api/v1/users/me` | ✅ | 30/min | UpdateUserProfileHandler |
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
| `POST` | `/api/v1/organizations/{id}/conversations` | ✅ | 30/min | CreateConversationHandler |
| `POST` | `/api/v1/projects/{id}/conversations` | ✅ | 30/min | CreateConversationHandler |
| `GET` | `/api/v1/organizations/{id}/conversations` | ✅ | 60/min | ListOrgConversationsHandler |
| `GET` | `/api/v1/conversations/{id}` | ✅ | 60/min | GetConversationHandler |
| `POST` | `/api/v1/conversations/{id}/messages` | ✅ | 30/min | SendMessageHandler |
| `GET` | `/api/v1/conversations/{id}/messages` | ✅ | 60/min | ListMessagesHandler |
| `DELETE` | `/api/v1/messages/{id}` | ✅ | 30/min | DeleteMessageHandler |
| `POST` | `/api/v1/organizations/{id}/documents` | ✅ | 30/min | UploadDocumentHandler |
| `GET` | `/api/v1/organizations/{id}/documents` | ✅ | 60/min | ListDocumentsHandler |
| `POST` | `/api/v1/projects/{id}/documents` | ✅ | 30/min | UploadDocumentHandler |
| `GET` | `/api/v1/projects/{id}/documents` | ✅ | 60/min | ListDocumentsHandler |
| `DELETE` | `/api/v1/documents/{id}` | ✅ | 30/min | DeleteDocumentHandler |
| `GET` | `/api/v1/documents/{id}/download` | ✅ | 60/min | DownloadDocumentHandler |
| `GET` | `/api/v1/dashboard/stats` | ✅ | 30/min | GetDashboardStatsHandler |

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
| `UPLOAD_DIR` | `./uploads` | Local file storage directory |

## Backend Stack

Python 3.12 · FastAPI · Uvicorn · SQLAlchemy async (imperative mapping) · Alembic · pydantic-settings · bcrypt (no passlib) · PyJWT · slowapi · structlog · httpx · Resend · pytest + pytest-asyncio

## Frontend (monorepo — `/frontend`)

**Stack:** Next.js 16 (App Router) · Tailwind CSS 4 · shadcn/ui (base-ui) · TypeScript · Zustand · TanStack Query v5 · React Hook Form + Zod · Axios

**Workflow:** see `kairos-frontend-workflow.md` (gitignored, local reference only)

### Frontend Structure (Sprints 1-8 complete — build passing 2026-03-29)

**Sprint status:** S1 Auth ✅ · S2 Orgs ✅ · S3 Projects+Deliverables+AI ✅ · S4 Invoices+Stats ✅ · S5 Profile edit ✅ · S6 Chat ✅ · S7 Documents ✅ · S8 Dashboard+Invitations ✅ · S9 Seed+Fixes ✅

```
frontend/src/
├── app/
│   ├── layout.tsx, providers.tsx, globals.css
│   ├── (auth)/layout.tsx
│   │   ├── select-workspace/page.tsx    # Tenant lookup por slug
│   │   ├── login/page.tsx               # 2-step: tokens → getMe
│   │   └── register/page.tsx            # Con tenant_id
│   └── (dashboard)/layout.tsx           # AuthGuard + Sidebar
│       ├── page.tsx                     # Dashboard — stats cards + recientes ✅
│       ├── messages/page.tsx            # Chat / conversaciones ✅
│       ├── organizations/
│       │   ├── page.tsx                 # List orgs ✅
│       │   ├── new/page.tsx             # Create form ✅
│       │   └── [id]/
│       │       ├── page.tsx             # Detail: tabs members|invoices|chat|documents ✅
│       │       └── invoices/page.tsx    # Stats cards + tabla + crear + marcar pagada ✅
│       ├── projects/
│       │   ├── page.tsx                 # List projects ✅
│       │   ├── new/page.tsx             # Create form ✅
│       │   └── [id]/page.tsx            # Detail: tabs deliverables|chat|summary|documents ✅
│       └── settings/page.tsx            # Perfil editable: nombre + avatar_url ✅
├── components/
│   ├── layout/app-sidebar.tsx, header.tsx
│   ├── shared/auth-guard.tsx, status-badge.tsx, role-gate.tsx, confirm-dialog.tsx, empty-state.tsx
│   ├── ui/ (shadcn base-ui: button, card, input, label, select, form, textarea,
│   │        dialog, alert-dialog, dropdown-menu, sheet, sidebar, avatar, badge,
│   │        breadcrumb, separator, skeleton, tooltip, sonner, table)
│   ├── organizations/ (organization-card, organization-form, invite-member-dialog,
│   │                   change-role-dialog, member-table) ✅
│   ├── projects/ (project-card, project-form, project-summary) ✅
│   ├── deliverables/ (deliverable-card, deliverable-form, deliverable-list) ✅
│   ├── invoices/ (invoice-form, invoice-table) ✅
│   ├── chat/ (chat-panel, conversation-list, message-thread, message-input) ✅
│   ├── documents/ (document-upload-dialog, document-card, document-list) ✅
│   └── dashboard/ (stats-cards, deliverable-chart, invoice-chart, project-progress) ✅
├── lib/
│   ├── api/
│   │   ├── axios-instance.ts            # Interceptors, token mgmt, error envelope
│   │   ├── auth.api.ts                  # register, login, refresh, logout, getMe, updateProfile
│   │   ├── tenants.api.ts, organizations.api.ts
│   │   ├── projects.api.ts, deliverables.api.ts, invoices.api.ts
│   │   ├── conversations.api.ts, documents.api.ts
│   │   └── dashboard.api.ts             # GET /dashboard/stats ✅ (10 services total)
│   └── validators/ (auth, organization, project, deliverable, invoice schemas — Zod v4)
├── stores/auth.store.ts, ui.store.ts    # Zustand + _hasHydrated flag
├── hooks/ (use-auth, use-organizations, use-projects, use-deliverables, use-invoices,
│           use-conversations, use-documents, use-dashboard, use-mobile)
├── types/
│   ├── auth.types.ts                    # User {id,email,name,avatar_url,is_active}, UpdateProfileDto
│   ├── tenant, organization, project, deliverable, invoice, api types
│   ├── conversation.types.ts, document.types.ts, dashboard.types.ts
├── constants/ (routes, roles, query-keys, navigation)
└── middleware.ts                        # Auth guard (proxy)
```

### Frontend Design Rules

- **shadcn/ui v2 (base-ui)**: uses `render` prop, NOT `asChild` — e.g. `<SidebarMenuButton render={<Link href="/" />}>`
- **Auth 2-step flow**: Login → tokens only → GET /users/me → user profile
- **Register**: returns User only (no tokens) → redirect to /login
- **Zustand hydration**: `_hasHydrated` flag prevents SSR mismatch
- **Invoice amount**: always `string`, never `number`
- **Error envelope**: `{ error: { message } }` → `getApiErrorMessage()` helper
- **Refresh token rotation**: every refresh saves new token pair
- **Profile mutation**: `authApi.updateProfile()` → invalidate `queryKeys.users.me` on success
- **Document upload**: `multipart/form-data` via FormData — do NOT set Content-Type manually (Axios autodetects)
- **Document download**: `responseType: "blob"` → `URL.createObjectURL(blob)` → click a temp `<a>` element
- **Tabs pattern**: state local `useState<Tab>`, `border-b-2` custom buttons — NO shadcn Tabs. Para agregar un tab: extender el tipo union + el array de tabs + el bloque condicional
- **Recharts colores**: usar hex directos — `#4ade80` (green), `#f59e0b` (amber), `#ef4444` (red), `#a1a1aa` (muted). Recharts NO soporta CSS variables
- **`useSearchParams()` requiere Suspense**: en Next.js 16 cualquier página que lea query params debe envolver el componente en `<Suspense>` — ver `/accept-invitation/page.tsx` como referencia
- **`useAcceptInvitation`**: hook en `use-organizations.ts`. El API service `organizationsApi.acceptInvitation` existe desde S2

### Sprint History

| Sprint | Fecha | Descripción |
|--------|-------|-------------|
| S1 | — | Auth: login, register, select-workspace, token rotation |
| S2 | — | Orgs: crear, listar, detalle, miembros, invitaciones, roles |
| S3 | — | Projects + Deliverables + AI summary |
| S4 | 2026-03-23 | Invoices UI + Dashboard stats |
| S5 | 2026-03-25 | PATCH /users/me + settings editable + avatar_url |
| S6-backend | 2026-03-25 | Dominio Conversation + Message — 6 use cases, repos, SA mappers |
| S6-frontend | 2026-03-28 | Chat UI: /messages, chat-panel, conversation-list, message-thread, message-input, tabs en org+project |
| S7 | 2026-03-28 | Document Management — dominio Document, IFileStorage, LocalFileStorage, 4 handlers, 6 endpoints, 3 componentes UI |
| S8 | 2026-03-28 | Dashboard stats + Recharts (StatsCards, DeliverableChart, InvoiceChart, ProjectProgress) + página /accept-invitation |
| S9 | 2026-03-29 | Seed script demo (14 users-orgs-projects-deliverables-invoices-conversations), build fixes |

## Stitch MCP (Google)

**Servidor activo en Claude Code** — genera y gestiona UI con IA de Google.

```bash
# Ya configurado en ~/.claude.json — no requiere reinstalación
# API Key: X-Goog-Api-Key (no expira, no requiere OAuth)
# URL: https://stitch.googleapis.com/mcp
```

### Proyecto Kairos en Stitch

**Project ID:** `15698315690922955783`
**Design System:** "Kairos Dark Minimal" — Geist, dark mode, `#4ade80` green, `#0a0a0a` bg, `#111111` surface, round-8

| Screen | ID |
|--------|----|
| Freelancer Dashboard | `4ddc9c61378045c6b95df087d7f2dbce` |
| Client/Owner Dashboard | `ec963532bffc45ac92ae07d65b76a7f6` |
| Chat / Mensajería | `2e330ec7680841e6abf36200863209fc` |
| Project Detail + tabs | `d7a53dbd6ed645d7ab9fbed49b6367af` |
| Document Management | `db08e94813294c8694d6b63cfa55b4aa` |
| Settings & Profile | `0b1059ed4f674952a4226e7e5238b6f6` |
| Login | `7c4acb2e21db4cd6a13002954ed86e54` |
| Organization Detail | `9a90f9b591874fccb576a948ee4feb09` |
| Invitation Acceptance | `ba632be606ba40b196869f2588f61250` |

### Herramientas disponibles

| Tool | Descripción |
|------|-------------|
| `create_project` | Crea un nuevo proyecto de diseño UI |
| `list_projects` | Lista todos los proyectos activos |
| `list_screens` | Lista pantallas de un proyecto |
| `get_screen` | Detalles + HTML de una pantalla |
| `generate_screen_from_text` | Genera UI desde prompt (`GEMINI_3_1_PRO` recomendado) |
| `edit_screens` | Edita pantallas existentes |

### Uso en Kairos

- Obtener screen: `get_screen` con `name: "projects/15698315690922955783/screens/{id}"`
- Generar nueva pantalla: `generate_screen_from_text` con `projectId: "15698315690922955783"`
- Si Stitch responde "Unauthenticated" → la API key expiró → reconfigurar con `claude mcp add`

## Backend Development Workflow

1. Define domain in `src/domain/{aggregate}/`
2. Define use case in `src/application/{use_case}/`
3. Implement adapter in `src/infrastructure/persistence/sqlalchemy/`
4. Wire: TypeDecorators → `types.py`, mapper → `main.py` + `conftest.py`, repo → `unit_of_work.py`, factory → `container.py`, handler override → `conftest.py`
5. Create API route in `src/infrastructure/api/routers/`
6. Run migrations: `uv run alembic upgrade head`
7. Test: `uv run pytest`

## Seed Script

Demo data seeding via `scripts/seed.py` — populates DB with realistic domain data.

```bash
uv run python scripts/seed.py
```

**Creates:**
- 1 tenant: "Demo" (slug: `demo`)
- 2 users: Ana García (owner@kairos.dev) & Carlos López (dev@kairos.dev), both pwd `password123`
- 1 organization: "Agencia Creativa" (slug: agencia-creativa), owner Ana
- 2 projects: "Rediseño Web Q1", "App Mobile v2"
- 5 deliverables: 1 APPROVED, 1 PENDING, 1 CHANGES_REQUESTED, 2 PENDING (project 2)
- 3 invoices: 1 PAID ($2,500), 1 SENT ($4,000), 1 DRAFT ($1,500)
- 3 conversations: 1 org + 2 project, with realistic messages

Handlers invoked in FK-dependency order; all domain aggregates exercised.
