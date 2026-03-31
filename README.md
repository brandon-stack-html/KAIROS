# 🚀 Kairos — Client Portal for Freelancers

> Un portal completo para freelancers. Gestiona organizaciones, proyectos, entregas, facturas y mensajería con clientes en un solo lugar.

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.12-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-RLS-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-201%20passing-4ade80?style=flat-square)](./tests)
[![Deploy](https://img.shields.io/badge/Deploy-CubePath-6366f1?style=flat-square)](https://cubepath.com)

---

## 🔗 Demo en vivo

> **URL:** http://45.90.237.238:3000

### 🧪 Credenciales de prueba

La demo incluye datos realistas precargados. Puedes probar la app con estas cuentas:

| Rol | Email | Contraseña | Workspace (slug) |
|-----|-------|-----------|-----------------|
| **Owner** (freelancer) | `owner@kairos.dev` | `password123` | `demo` |
| **Member** (cliente) | `dev@kairos.dev` | `password123` | `demo` |

> **Cómo entrar:** en la pantalla inicial escribe `demo` como workspace → luego inicia sesión con cualquiera de las cuentas.

**Datos de demo incluidos:**
- 1 organización: "Agencia Creativa"
- 2 proyectos: "Rediseño Web Q1" y "App Mobile v2"
- 5 entregas (APPROVED, PENDING, CHANGES_REQUESTED)
- 3 facturas ($2,500 pagada · $4,000 enviada · $1,500 borrador)
- 3 conversaciones con mensajes realistas
- Dashboard con estadísticas y gráficos

---

## 📦 Repositorio

[github.com/brandon-stack-html/KAIROS](https://github.com/brandon-stack-html/KAIROS)

---

## 📸 Capturas de pantalla

### Dashboard con estadísticas y gráficos en tiempo real

<img width="1085" height="1008" alt="Dashboard" src="https://github.com/user-attachments/assets/7a8368c2-a4b0-45e9-b4c6-9f135f42ba27" />

### Detalle de organización — Miembros, Facturas, Chat, Documentos

<img width="1108" height="944" alt="Organización" src="https://github.com/user-attachments/assets/41181476-6826-4b10-8673-f620036e8cb4" />

---

## 📝 Descripción del proyecto

**Kairos** resuelve el caos de gestionar múltiples clientes como freelancer. En lugar de Slack + Trello + PayPal + email, tienes todo en un portal unificado:

**Características principales:**

- **Organizaciones multi-tenant** — cada cliente tiene su workspace con roles (Owner/Admin/Member)
- **Proyectos y entregas** — envía trabajo, el cliente aprueba o pide cambios en 1 clic
- **Facturación integrada** — emite facturas, sigue el estado (Draft → Sent → Paid)
- **Mensajería contextual** — conversaciones separadas por organización y por proyecto
- **Resúmenes por IA** — genera reportes automáticos para clientes via OpenRouter
- **Gestión de documentos** — sube y comparte archivos (PDF, Word, Sheets, hasta 10 MB)
- **Dashboard visual** — estadísticas, gráficos Recharts, acceso rápido a todo
- **Autenticación robusta** — JWT con refresh token rotation automático

---

## 🛠️ Stack tecnológico

**Backend:** Python 3.12 · FastAPI · SQLAlchemy async · Alembic · PyJWT · bcrypt · slowapi · httpx · Resend

**Frontend:** Next.js 16 · React 19 · Tailwind CSS 4 · shadcn/ui · TypeScript · Zustand · TanStack Query v5 · Zod

**Base de datos:** PostgreSQL 15+ con Row-Level Security para aislamiento multi-tenant

**IA:** OpenRouter → `openai/gpt-4o-mini` para generación de resúmenes de proyectos

**Deploy:** CubePath — 2 servidores Nano (backend + frontend) + PostgreSQL managed

---

## ☁️ Cómo se utiliza CubePath

### Arquitectura desplegada

```
┌─────────────────────────────────┐
│           CubePath              │
│                                 │
│  ┌──────────┐  ┌─────────────┐  │
│  │ Frontend │  │   Backend   │  │
│  │  Nano    │  │    Nano     │  │
│  │  :3000   │  │    :8000    │  │
│  └──────────┘  └──────┬──────┘  │
│                       │         │
│              ┌────────▼──────┐  │
│              │  PostgreSQL   │  │
│              │   Managed     │  │
│              │   + RLS       │  │
│              └───────────────┘  │
└─────────────────────────────────┘
```

### Configuración de servidores

**Backend Nano** (Python 3.12)
```
Port: 8000
CMD: uv run uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000
Vars: DATABASE_URL, SECRET_KEY, OPENROUTER_API_KEY, ALLOWED_ORIGINS, EMAIL_PROVIDER
```

**Frontend Nano** (Node.js 20)
```
Port: 3000
CMD: npm run build && npm start
Vars: NEXT_PUBLIC_API_URL
```

**PostgreSQL managed**
```
Version: 15+
RLS habilitado para multi-tenancy
Backups automáticos diarios
SSL incluido
```

**Ventajas de CubePath para Kairos:**
- ✅ Orquestación sencilla de múltiples servicios
- ✅ PostgreSQL managed con RLS y backups automáticos
- ✅ SSL/TLS automático en todas las conexiones
- ✅ Variables de entorno por instancia (sin hardcoding de secrets)
- ✅ Escalabilidad vertical fácil para crecer con los clientes
- ✅ Health checks y auto-restart

---

## 🏗️ Arquitectura

Implementa **Clean Architecture + DDD + Hexagonal** garantizando separación de responsabilidades y cero dependencias externas en el dominio.

```
src/
├── domain/          # Lógica de negocio pura — ZERO dependencias externas
│   ├── user/        # User, Email, avatar_url
│   ├── organization/# Organization, Membership, Invitation, Role
│   ├── project/     # Project (ACTIVE/COMPLETED)
│   ├── deliverable/ # Deliverable (PENDING/APPROVED/CHANGES_REQUESTED)
│   ├── invoice/     # Invoice, Decimal amount (DRAFT/SENT/PAID)
│   ├── conversation/# Conversation (ORG|PROJECT type)
│   ├── message/     # Message (1-4000 chars)
│   └── document/    # Document (10MB max, 9 MIME types)
│
├── application/     # Casos de uso — orquestan dominio
│   └── 36 handlers  # Register, Login, Invite, Approve, Issue, Send...
│
└── infrastructure/  # Adaptadores — FastAPI, SQLAlchemy, JWT, email, IA
    ├── api/routers/
    ├── persistence/sqlalchemy/ (mappers, repos, TypeDecorators)
    └── services/ (AI, email, file storage)
```

**Regla de dependencia:** `infrastructure → application → domain`

---

## 🎯 Por qué destaca Kairos

### 1. Experiencia de usuario
- Diseño dark minimalista coherente (`#0a0a0a` + `#4ade80` green accent)
- 14 rutas funcionales con navegación fluida
- Feedback inmediato: toasts, loading states, confirmaciones
- Tabs contextuales por entidad (org: Miembros|Facturas|Chat|Docs)

### 2. Creatividad
- Resúmenes de proyectos generados por IA personalizados por cliente
- Sistema de roles granular con gates condicionales en la UI
- Mensajería contextual: conversaciones por org Y por proyecto (no mezcladas)
- Multi-tenancy real: JWT con `tid` claim + RLS a nivel de base de datos

### 3. Utilidad real
- Centraliza Slack + Trello + PayPal + email en 1 sola plataforma
- ROI inmediato para freelancers con múltiples clientes
- Auditable: historial completo de entregas, facturas y mensajes

### 4. Implementación técnica
- 201 tests pasando (dominio + application + infrastructure)
- Clean Architecture + DDD con 8 agregados
- TypeDecorators en SQLAlchemy para type safety completo
- Refresh token rotation automático sin fricción para el usuario
- Rate limiting por endpoint (slowapi)
- Error handling con envelope `{ error: { message } }` consistente

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Tests pasando | 201 ✅ |
| API endpoints | 36 |
| Rutas frontend | 14 |
| Dominios DDD | 8 agregados |
| Sprints completados | 9 (S1–S9) |
| Componentes React | 30+ |

---

## 🚀 Quick start local

### Backend

```bash
git clone https://github.com/brandon-stack-html/KAIROS.git
cd KAIROS
uv sync
uv run alembic upgrade head
uv run python scripts/seed.py   # carga datos de demo
uv run uvicorn src.infrastructure.api.main:app --reload
# http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
# crear frontend/.env.local con: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
# http://localhost:3000
```

### Variables de entorno relevantes

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Conexión PostgreSQL o SQLite para dev |
| `SECRET_KEY` | JWT signing key (≥ 32 chars en prod) |
| `OPENROUTER_API_KEY` | Para resúmenes por IA |
| `EMAIL_PROVIDER` | `console` (dev) o `resend` (prod) |
| `UPLOAD_DIR` | Directorio para documentos subidos |

---

## 👨‍💻 Autor

**Brandon Li** — brandonli777xd@gmail.com

---

## ✅ Confirmaciones

- [x] El proyecto está desplegado en CubePath: http://45.90.237.238:3000
- [x] El repositorio es público con README documentado
- [x] He leído y acepto las reglas de la hackatón

---

MIT License
