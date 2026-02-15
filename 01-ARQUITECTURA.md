# 01 - ARQUITECTURA DEL NUEVO SISTEMA CRM SEGUROS PROTEGRT

**Fecha:** 2026-02-14
**Autor:** Agente Arquitecto
**Version:** 1.0
**Estado:** Propuesta inicial

> **NOTA:** Las decisiones tecnicas canonicas estan en `CLAUDE.md` seccion "Decisiones Canonicas v1".
> En caso de contradiccion entre este documento y CLAUDE.md, CLAUDE.md prevalece.

---

## INDICE

1. [Stack Tecnologico Recomendado](#1-stack-tecnologico-recomendado)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Base de Datos](#3-base-de-datos)
4. [Autenticacion y Autorizacion](#4-autenticacion-y-autorizacion)
5. [Despliegue en EasyPanel](#5-despliegue-en-easypanel)
6. [Roadmap de Implementacion](#6-roadmap-de-implementacion)

---

## 1. STACK TECNOLOGICO RECOMENDADO

### 1.1 Evaluacion comparativa

| Criterio | FastAPI (Python) | NestJS (Node/TS) | Django REST | Veredicto |
|----------|-----------------|-------------------|-------------|-----------|
| Velocidad de desarrollo | Alta (tipado, async nativo) | Media-Alta (decoradores, modular) | Alta (baterias incluidas) | FastAPI |
| Rendimiento async | Excelente (uvicorn+ASGI) | Excelente (event loop nativo) | Medio (requiere ASGI) | Empate FastAPI/NestJS |
| Ecosistema Python (equipo actual) | Curva 0 (ya conocen Python) | Curva media (TypeScript nuevo) | Curva 0 | FastAPI |
| Documentacion API auto | OpenAPI nativo con Swagger/ReDoc | Swagger via plugin | DRF Spectacular | FastAPI |
| ORM / query builder | SQLAlchemy 2.0 (maduro, async) | Prisma/TypeORM | Django ORM | SQLAlchemy gana |
| Validacion de datos | Pydantic v2 (incluido) | class-validator + class-transformer | Serializers | Pydantic gana |
| PostGIS / GIS | GeoAlchemy2 (maduro) | PostGIS via raw SQL o Prisma | GeoDjango (excelente) | FastAPI con GeoAlchemy2 |
| WebSockets | Nativo en Starlette | Nativo en NestJS | Django Channels | Empate |
| Comunidad / soporte | Enorme, creciente | Grande | Muy grande | Todos bien |

| Criterio | React + Next.js | Vue 3 + Nuxt 3 | Angular | Veredicto |
|----------|----------------|----------------|---------|-----------|
| Curva de aprendizaje | Media | Baja-Media | Alta | Vue para equipo nuevo |
| Ecosistema de componentes | El mayor (shadcn/ui, Radix) | Bueno (PrimeVue, Vuetify) | Material (Angular Material) | React |
| SSR / SSG | Next.js (maduro) | Nuxt 3 (maduro) | Universal (complejo) | Empate Next/Nuxt |
| TypeScript | Nativo | Nativo | Obligatorio | Todos |
| Productividad para CRM/admin | Alta con shadcn + TanStack | Alta con PrimeVue | Alta con Material | React por ecosistema admin |

| Criterio | Flutter | React Native | PWA | Veredicto |
|----------|---------|-------------|-----|-----------|
| Base de codigo compartida | 100% (Dart) | 95% (JS/TS) | 100% (web) | Flutter |
| Rendimiento | Nativo (compilado) | Near-native (bridge) | Web (limitado) | Flutter |
| Offline / GPS / camara | Excelente | Bueno | Limitado | Flutter |
| Push notifications | FCM nativo | FCM via plugin | Web Push (limitado en iOS) | Flutter/RN |
| Reutilizacion con web | Ninguna (Dart) | Alta (mismo lenguaje) | Total | PWA/RN |
| Publicacion en stores | Si | Si | Opcional | Flutter/RN |
| Requisitos del proyecto | GPS, camara, offline, push | GPS, camara, offline, push | Solo basico | Flutter o RN |
| Equipo actual sabe | -- | -- | -- | Curva nueva para ambos |

### 1.2 Stack seleccionado

```
BACKEND:     FastAPI (Python 3.11+)
             SQLAlchemy 2.0 + GeoAlchemy2 (async)
             Pydantic v2
             Alembic (migraciones)
             Celery + Redis (tareas en background)
             uvicorn (servidor ASGI)

FRONTEND:    Next.js 14+ (React + TypeScript)
             shadcn/ui + Tailwind CSS
             TanStack Query (data fetching)
             TanStack Table (tablas de datos)
             Zustand (estado global ligero)
             Socket.IO client (notificaciones real-time)

MOVIL:       React Native + Expo
             (comparte TypeScript y logica con frontend web)
             React Native Maps (cobradores, ajustadores)
             Expo Camera (fotos de recibos/siniestros)
             Expo Location (GPS tracking)

BASE DATOS:  PostgreSQL 16 + PostGIS 3.4
             PgBouncer (connection pooling)
             Redis 7 (cache, sesiones, cola de tareas)

INFRA:       Docker + Docker Compose
             EasyPanel (orquestacion)
             Traefik (reverse proxy, SSL automatico)
             GitHub Actions (CI/CD)
```

### 1.3 Justificacion de decisiones clave

**FastAPI sobre Django REST Framework:**
- El equipo ya programa en Python; la curva de aprendizaje es minima.
- async nativo permite manejar WebSockets, notificaciones y llamadas a APIs externas (WhatsApp, Telegram, Cotizaciones) sin bloquear.
- Pydantic v2 genera documentacion OpenAPI automaticamente -- los endpoints quedan auto-documentados para el equipo de movil.
- SQLAlchemy 2.0 async con GeoAlchemy2 da soporte PostGIS maduro.
- El proyecto actual ya usa un patron similar (Services + DAOs). FastAPI con inyeccion de dependencias lo formaliza mejor.

**Next.js sobre Nuxt/Angular:**
- React tiene el mayor ecosistema de componentes para aplicaciones tipo CRM/admin (shadcn/ui, TanStack Table para tablas con 10,000+ filas, Recharts para dashboards).
- Next.js con App Router y Server Components permite renderizado hibrido, util para el dashboard y reportes.
- TypeScript compartido con React Native reduce duplicacion de tipos y logica.

**React Native sobre Flutter:**
- La decision principal es que React Native comparte TypeScript, tipos Pydantic->Zod, y logica de validacion con Next.js. El equipo aprende un solo lenguaje para frontend + movil.
- Expo simplifica enormemente el build, push notifications, y OTA updates (critical para actualizar la app de cobradores sin pasar por Play Store).
- Si el equipo tuviera experiencia en Dart, Flutter seria superior en rendimiento puro. Pero la productividad de un solo lenguaje (TS) pesa mas para un equipo pequeno.

**React Native sobre PWA:**
- Las apps de cobradores y ajustadores requieren GPS en background, camara de alta calidad para fotos de siniestros, push notifications confiables, y eventual modo offline. Las PWA son insuficientes para estas necesidades, particularmente en iOS donde las limitaciones de Service Workers son significativas.

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Tipo de arquitectura: Monolito Modular

Para un equipo pequeno, microservicios es over-engineering. Se elige un **monolito modular** que se puede descomponer en el futuro si crece. Cada modulo tiene fronteras claras y dependencias explicitas.

**Ventajas frente a microservicios:**
- Un solo repositorio, un solo deploy, un solo proceso
- Sin overhead de red entre servicios
- Transacciones ACID simples (sin sagas/2PC)
- Debugging y logging centralizado
- Un solo equipo puede mantenerlo

**Ventajas frente a monolito clasico:**
- Modulos con interfaces explicitas (no se importa cualquier cosa desde cualquier lugar)
- Cada modulo tiene su propio router, service, repository, schemas
- Se puede extraer un modulo a microservicio si crece (ej: notificaciones)
- Tests por modulo sin dependencias cruzadas

### 2.2 Diagrama de componentes

```
                         INTERNET
                            |
                     +------v------+
                     |   Traefik   |  <-- SSL/TLS termination
                     | (EasyPanel) |  <-- Rate limiting
                     +------+------+  <-- CORS
                            |
              +-------------+-------------+
              |                           |
     +--------v--------+       +---------v---------+
     |   FastAPI App    |       |    Next.js App    |
     |   (Backend)      |       |    (Frontend)     |
     |   :8000          |       |    :3000          |
     +--------+---------+       +-------------------+
              |
     +--------v--------+
     |     Modulos      |
     |  +------------+  |
     |  | auth       |  |  -- JWT, sesiones, permisos
     |  | clients    |  |  -- CRUD clientes
     |  | policies   |  |  -- Polizas, coberturas, status
     |  | payments   |  |  -- Pagos, propuestas, recibos
     |  | collections|  |  -- Cobranza, tarjetas, rutas
     |  | incidents  |  |  -- Siniestros, ajustadores
     |  | tow        |  |  -- Gruas, proveedores
     |  | endorsemnts|  |  -- Endosos
     |  | renewals   |  |  -- Renovaciones
     |  | promotions |  |  -- Promociones flexibles
     |  | notificatns|  |  -- WhatsApp, Telegram, Push
     |  | reports    |  |  -- Reportes, Excel, PDF
     |  | dashboard  |  |  -- Estadisticas, graficos
     |  | hr         |  |  -- Vacaciones, permisos, horarios, quejas
     |  +------------+  |
     +--------+---------+
              |
    +---------+----------+-----------+
    |         |          |           |
+---v---+ +--v----+ +---v----+ +----v-----+
|  PG   | |PgBounc| | Redis  | | Celery   |
|+PostGS| |  er   | | :6379  | | Workers  |
| :5432 | | :6432 | |        | |          |
+-------+ +-------+ +--------+ +----------+
                                     |
                          +----------+----------+
                          |          |          |
                     WhatsApp    Telegram   Push
                     (Evolution) (Bot API)  (FCM)

    OTRO VPS (backup):
    +--------------+
    | PG Standby   |  <-- WAL streaming
    | pgBackRest   |  <-- Backups completos
    +--------------+
```

### 2.3 Comunicacion entre componentes

| Comunicacion | Protocolo | Uso |
|-------------|-----------|-----|
| Frontend <-> Backend | REST (HTTPS) | CRUD, operaciones normales |
| Frontend <-> Backend | WebSocket (Socket.IO) | Notificaciones real-time: pago aprobado, nueva propuesta, siniestro reportado |
| App movil <-> Backend | REST (HTTPS) | Misma API que web |
| App movil <-> Backend | Push Notifications (FCM) | Alertas cuando la app esta cerrada |
| Backend -> WhatsApp | REST (Evolution API) | Mensajes de cobranza, recordatorios, confirmaciones de pago |
| Backend -> Telegram | REST (Bot API) | Alertas de siniestros, guardias, renovaciones |
| Backend -> Cotizaciones | REST (API interna) | Validar/aprobar cotizaciones |
| Backend -> Celery/Redis | Broker (Redis) | Tareas asincronas: StatusUpdater, reportes, mensajes masivos |
| Backend -> PostgreSQL | TCP via PgBouncer | Datos persistentes |
| Backend -> Redis | TCP | Cache, rate limiting, sesiones de refresh token |

### 2.4 Estructura de carpetas del proyecto

```
nuevo-sistema/
|
|-- backend/                          # FastAPI (monolito modular)
|   |-- alembic/                      # Migraciones de BD
|   |   |-- versions/
|   |   |-- env.py
|   |-- app/
|   |   |-- core/                     # Nucleo compartido
|   |   |   |-- config.py             # Settings (pydantic-settings, env vars)
|   |   |   |-- database.py           # Engine SQLAlchemy async + session factory
|   |   |   |-- security.py           # JWT, Argon2id (bcrypt como fallback para passwords migrados), dependencias de auth
|   |   |   |-- dependencies.py       # Dependencias comunes (get_db, get_current_user)
|   |   |   |-- exceptions.py         # Excepciones custom + handlers
|   |   |   |-- permissions.py        # RBAC engine
|   |   |   |-- events.py             # Event bus interno (para desacoplar modulos)
|   |   |
|   |   |-- modules/                  # Modulos de negocio
|   |   |   |-- auth/
|   |   |   |   |-- router.py         # POST /login, POST /refresh, POST /logout
|   |   |   |   |-- service.py        # Logica de autenticacion
|   |   |   |   |-- repository.py     # Acceso a app_user, session, device_session
|   |   |   |   |-- schemas.py        # LoginRequest, TokenResponse, etc.
|   |   |   |   |-- dependencies.py   # get_current_user, require_permission
|   |   |   |
|   |   |   |-- clients/
|   |   |   |   |-- router.py         # CRUD /clients
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- policies/
|   |   |   |   |-- router.py         # CRUD /policies, status updater
|   |   |   |   |-- service.py        # Creacion con pagos, status machine
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- status_updater.py # Logica de actualizacion de estados
|   |   |   |
|   |   |   |-- payments/
|   |   |   |   |-- router.py         # CRUD /payments, /proposals
|   |   |   |   |-- service.py        # Logica de pagos, abonos, restructuracion
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- proposal_service.py # Flujo de autorizacion
|   |   |   |
|   |   |   |-- collections/
|   |   |   |   |-- router.py         # /cards, /assignments, /affinity
|   |   |   |   |-- service.py        # Tarjetas, asignaciones, algoritmo afinidad
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- affinity.py       # Algoritmo de mejor ubicacion
|   |   |   |
|   |   |   |-- receipts/
|   |   |   |   |-- router.py         # /receipts, lotes, asignacion, verificacion
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- incidents/
|   |   |   |   |-- router.py         # /incidents, /adjusters, /shifts
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- tow/
|   |   |   |   |-- router.py         # /tow-services, /providers
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- endorsements/
|   |   |   |   |-- router.py         # /endorsements
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- renewals/
|   |   |   |   |-- router.py         # /renewals
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- promotions/
|   |   |   |   |-- router.py         # /promotions, /promotion-rules
|   |   |   |   |-- service.py        # Aplicacion flexible de promociones
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |   |-- engine.py         # Motor de evaluacion de reglas
|   |   |   |
|   |   |   |-- notifications/
|   |   |   |   |-- router.py         # /notifications (historial, config)
|   |   |   |   |-- service.py        # Orquestador de canales
|   |   |   |   |-- channels/
|   |   |   |   |   |-- whatsapp.py   # Evolution API client
|   |   |   |   |   |-- telegram.py   # Telegram Bot API client
|   |   |   |   |   |-- push.py       # FCM client
|   |   |   |   |-- templates.py      # Plantillas de mensajes
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- reports/
|   |   |   |   |-- router.py         # /reports (Excel, PDF)
|   |   |   |   |-- generators/
|   |   |   |   |   |-- renewals.py
|   |   |   |   |   |-- payments.py
|   |   |   |   |   |-- collections.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- dashboard/
|   |   |   |   |-- router.py         # /dashboard/stats
|   |   |   |   |-- service.py        # Estadisticas (usa vistas materializadas)
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- coverages/
|   |   |   |   |-- router.py         # /coverages (catalogo, precios)
|   |   |   |   |-- service.py
|   |   |   |   |-- repository.py
|   |   |   |   |-- schemas.py
|   |   |   |
|   |   |   |-- hr/
|   |   |       |-- router.py         # /hr (vacaciones, permisos, horario, quejas)
|   |   |       |-- service.py
|   |   |       |-- repository.py
|   |   |       |-- schemas.py
|   |   |
|   |   |-- models/                   # SQLAlchemy models (shared across modules)
|   |   |   |-- base.py               # Base declarativa, mixins (timestamps, soft delete)
|   |   |   |-- client.py
|   |   |   |-- policy.py
|   |   |   |-- payment.py
|   |   |   |-- receipt.py
|   |   |   |-- card.py
|   |   |   |-- incident.py
|   |   |   |-- tow_service.py
|   |   |   |-- ...                   # Un archivo por tabla principal
|   |   |
|   |   |-- tasks/                    # Celery tasks
|   |   |   |-- status_updater.py     # Actualizacion nocturna de estados
|   |   |   |-- messaging.py          # Envio masivo de mensajes (morosos, recordatorios)
|   |   |   |-- reports.py            # Generacion de reportes pesados
|   |   |   |-- backups.py            # Monitoreo de backups
|   |   |   |-- scheduler.py          # Tareas programadas (celery beat)
|   |   |
|   |   |-- websocket/                # WebSocket handlers
|   |   |   |-- manager.py            # Connection manager
|   |   |   |-- events.py             # Eventos real-time
|   |   |
|   |   |-- main.py                   # App factory, include routers, middleware
|   |
|   |-- tests/
|   |   |-- conftest.py               # Fixtures: DB test, client HTTP, factories
|   |   |-- factories/                # factory_boy factories
|   |   |-- unit/                     # Tests unitarios por modulo
|   |   |   |-- test_status_updater.py
|   |   |   |-- test_payment_calculations.py
|   |   |   |-- test_affinity_algorithm.py
|   |   |   |-- test_promotion_engine.py
|   |   |-- integration/              # Tests con DB real (testcontainers)
|   |   |   |-- test_auth_flow.py
|   |   |   |-- test_policy_lifecycle.py
|   |   |   |-- test_approval_workflow.py
|   |
|   |-- Dockerfile
|   |-- pyproject.toml                # Dependencias (uv o poetry)
|   |-- alembic.ini
|
|-- frontend/                         # Next.js (web admin)
|   |-- src/
|   |   |-- app/                      # App Router (Next.js 14+)
|   |   |   |-- (auth)/               # Layout de login (sin sidebar)
|   |   |   |   |-- login/page.tsx
|   |   |   |-- (dashboard)/          # Layout principal (con sidebar)
|   |   |   |   |-- page.tsx          # Dashboard principal
|   |   |   |   |-- clients/
|   |   |   |   |-- policies/
|   |   |   |   |-- payments/
|   |   |   |   |-- collections/
|   |   |   |   |-- incidents/
|   |   |   |   |-- tow-services/
|   |   |   |   |-- endorsements/
|   |   |   |   |-- renewals/
|   |   |   |   |-- promotions/
|   |   |   |   |-- reports/
|   |   |   |   |-- admin/            # Usuarios, roles, config
|   |   |   |   |-- hr/               # Recursos Humanos (panel personal + gestion)
|   |   |-- components/
|   |   |   |-- ui/                   # shadcn/ui (Button, Dialog, Table, etc.)
|   |   |   |-- layout/              # Sidebar, Header, Breadcrumb
|   |   |   |-- data-tables/         # Tablas reutilizables con TanStack
|   |   |   |-- forms/               # Formularios reutilizables
|   |   |   |-- charts/              # Graficos del dashboard
|   |   |-- lib/
|   |   |   |-- api.ts               # Cliente API (fetch wrapper con auth)
|   |   |   |-- auth.ts              # Manejo de tokens, refresh
|   |   |   |-- socket.ts            # Socket.IO client
|   |   |   |-- utils.ts
|   |   |-- hooks/                    # Custom hooks
|   |   |-- types/                    # TypeScript types (generados desde OpenAPI)
|   |   |-- stores/                   # Zustand stores
|   |
|   |-- Dockerfile
|   |-- package.json
|   |-- tailwind.config.ts
|   |-- next.config.js
|
|-- mobile/                           # React Native + Expo
|   |-- apps/
|   |   |-- collector/                # App cobradores
|   |   |   |-- app/                  # Expo Router
|   |   |   |   |-- (tabs)/
|   |   |   |   |   |-- route.tsx     # Ruta de cobranza (mapa)
|   |   |   |   |   |-- proposals.tsx # Mis propuestas
|   |   |   |   |   |-- receipts.tsx  # Recibos asignados
|   |   |   |   |-- collect/[id].tsx  # Registrar cobro
|   |   |
|   |   |-- seller/                   # App vendedores
|   |   |   |-- app/
|   |   |   |   |-- (tabs)/
|   |   |   |   |   |-- policies.tsx  # Mis polizas
|   |   |   |   |   |-- quotes.tsx    # Cotizaciones
|   |   |   |   |   |-- renewals.tsx  # Renovaciones pendientes
|   |   |   |   |-- new-policy.tsx    # Crear poliza
|   |   |
|   |   |-- adjuster/                 # App ajustadores
|   |       |-- app/
|   |           |-- (tabs)/
|   |           |   |-- incidents.tsx  # Siniestros asignados
|   |           |   |-- shift.tsx      # Mi turno
|   |           |-- incident/[id].tsx  # Detalle siniestro + fotos
|   |
|   |-- packages/
|   |   |-- shared/                   # Codigo compartido entre apps
|   |   |   |-- api/                  # Cliente API compartido
|   |   |   |-- types/                # Tipos TypeScript compartidos
|   |   |   |-- components/           # Componentes UI compartidos
|   |   |   |-- hooks/                # Hooks compartidos (auth, location)
|   |
|   |-- Dockerfile                    # Solo para builds (no runtime)
|   |-- package.json
|
|-- docker/
|   |-- docker-compose.yml            # Orquestacion local
|   |-- docker-compose.prod.yml       # Override de produccion
|   |-- postgres/
|   |   |-- postgresql.conf           # Configuracion custom
|   |   |-- pg_hba.conf
|   |-- pgbouncer/
|   |   |-- pgbouncer.ini
|   |-- redis/
|   |   |-- redis.conf
|   |-- traefik/
|       |-- traefik.yml
|       |-- dynamic/
|
|-- database/
|   |-- postgresql/
|   |   |-- schema.sql                # Schema completo (ya existente)
|   |   |-- seed.sql                  # Datos iniciales (coberturas, roles, permisos)
|   |-- migrations/
|       |-- migrate_mysql_to_pg.py    # Script de migracion
|
|-- docs/                             # Documentacion
|   |-- api/                          # OpenAPI spec exportada
|   |-- architecture/                 # Diagramas (este documento)
|
|-- .github/
|   |-- workflows/
|       |-- ci.yml                    # Lint, tests, build
|       |-- deploy.yml                # Deploy a EasyPanel
|
|-- .env.example
|-- README.md
```

### 2.5 Patron de capas en el backend

Cada modulo sigue estrictamente estas capas:

```
Router (endpoint HTTP)
  |
  v
Service (logica de negocio)
  |
  v
Repository (acceso a datos)
  |
  v
SQLAlchemy Model (ORM)
  |
  v
PostgreSQL
```

**Reglas estrictas:**

| Capa | Puede importar | NO puede importar |
|------|---------------|-------------------|
| **Router** | Service, Schemas, Dependencies (FastAPI) | Repository, Models, SQLAlchemy session |
| **Service** | Repository, Schemas, otros Services, Event bus | Router, FastAPI Request/Response, session directa |
| **Repository** | Models, SQLAlchemy session (inyectada) | Service, Router, Schemas de request |
| **Schemas** | Nada (Pydantic puro) | Cualquier otra capa |
| **Models** | SQLAlchemy Base | Cualquier otra capa |

**Ejemplo de flujo: Crear una poliza**

```python
# router.py
@router.post("/policies", response_model=PolicyResponse)
async def create_policy(
    data: PolicyCreateRequest,
    service: PolicyService = Depends(get_policy_service),
    current_user: User = Depends(require_permission("policies.create")),
):
    return await service.create_policy(data, current_user)

# service.py
class PolicyService:
    def __init__(self, repo: PolicyRepository, payment_svc: PaymentService, ...):
        ...

    async def create_policy(self, data: PolicyCreateRequest, user: User) -> PolicyResponse:
        # 1. Validar datos de negocio
        # 2. Crear poliza via repository
        # 3. Crear pagos segun forma de pago
        # 4. Crear tarjeta
        # 5. Emitir evento "policy_created" (para notificaciones)
        ...

# repository.py
class PolicyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, policy: Policy) -> Policy:
        self.session.add(policy)
        await self.session.flush()
        return policy
```

### 2.6 Event bus interno (desacoplamiento entre modulos)

Para evitar dependencias circulares entre modulos (ej: al crear un pago, se necesita actualizar status de poliza, enviar WhatsApp, sincronizar recibo), se usa un event bus interno simple:

```python
# core/events.py
class EventBus:
    _handlers: dict[str, list[Callable]] = {}

    @classmethod
    def subscribe(cls, event_name: str, handler: Callable):
        cls._handlers.setdefault(event_name, []).append(handler)

    @classmethod
    async def publish(cls, event_name: str, data: dict):
        for handler in cls._handlers.get(event_name, []):
            await handler(data)

# En payments/service.py:
await EventBus.publish("payment_completed", {
    "policy_id": policy_id,
    "payment_id": payment_id,
    "receipt_number": receipt_number
})

# En notifications/service.py (suscriptor):
@EventBus.subscribe("payment_completed")
async def on_payment_completed(data):
    await send_whatsapp_confirmation(data["policy_id"])

# En policies/status_updater.py (suscriptor):
@EventBus.subscribe("payment_completed")
async def on_payment_completed(data):
    await recalculate_policy_status(data["policy_id"])
```

Para tareas pesadas (reportes, mensajes masivos), el handler envia la tarea a Celery en lugar de ejecutarla inline.

### 2.7 WebSockets para notificaciones real-time

```
Eventos real-time (via Socket.IO):
|
|-- "proposal:new"         -> Oficina ve nueva propuesta de cobro
|-- "proposal:approved"    -> Cobrador ve que su propuesta fue aprobada
|-- "proposal:rejected"    -> Cobrador ve que fue rechazada (con motivo)
|-- "policy:status_change" -> Dashboard actualiza status de poliza
|-- "incident:new"         -> Grupo de ajustadores ve nuevo siniestro
|-- "payment:completed"    -> Dashboard actualiza
|-- "notification:sent"    -> Log de notificaciones actualiza
```

Los WebSockets se autentican con el mismo JWT. El servidor mantiene un mapa de user_id -> connections para dirigir mensajes. Redis Pub/Sub se usa como backend de Socket.IO para escalar a multiples workers.

---

## 3. BASE DE DATOS

### 3.1 PostgreSQL + PostGIS en EasyPanel

**Configuracion recomendada para el VPS:**

```ini
# postgresql.conf (optimizado para VPS 4-8GB RAM)
shared_buffers = 2GB              # 25% de RAM
effective_cache_size = 6GB        # 75% de RAM
work_mem = 64MB                   # Para sorts y joins
maintenance_work_mem = 512MB      # Para VACUUM, CREATE INDEX
wal_buffers = 64MB
max_connections = 200             # PgBouncer limita las reales
max_wal_size = 2GB
min_wal_size = 512MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1            # SSD
effective_io_concurrency = 200    # SSD

# WAL para replicacion y PITR
wal_level = replica
archive_mode = on
archive_command = 'pgbackrest --stanza=protegrt archive-push %p'
max_wal_senders = 5

# Logging
log_min_duration_statement = 500  # Log queries > 500ms
log_checkpoints = on
log_lock_waits = on
```

### 3.2 Connection pooling con PgBouncer

```ini
# pgbouncer.ini
[databases]
protegrt = host=postgres port=5432 dbname=protegrt_db

[pgbouncer]
pool_mode = transaction          # Libera conexion al final de cada transaccion
max_client_conn = 400            # Conexiones de clientes (apps)
default_pool_size = 25           # Conexiones reales a PostgreSQL
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
server_check_query = SELECT 1
server_check_delay = 30
max_db_connections = 50
```

**FastAPI conecta a PgBouncer (puerto 6432), NO directamente a PostgreSQL (5432).** Esto permite manejar cientos de conexiones de apps moviles y web sin saturar PostgreSQL.

### 3.3 Estrategia de backup automatico

**Herramienta: pgBackRest** (superior a pg_dump para bases > 1GB, soporta incremental, paralelo, y WAL archiving).

```
ARQUITECTURA DE BACKUP:

  VPS Principal (EasyPanel)          VPS Backup (otro datacenter)
  +----------------------+           +------------------------+
  | PostgreSQL 16        |   WAL     | pgBackRest Repository  |
  | + PostGIS            | --------> | /var/lib/pgbackrest/   |
  | + pgBackRest agent   |  stream   | + WAL archive          |
  +----------------------+           | + Full backups         |
                                     | + Diff backups         |
                                     | + PITR capability      |
                                     +------------------------+
```

**Configuracion pgBackRest:**

```ini
# /etc/pgbackrest/pgbackrest.conf (VPS principal)
[global]
repo1-host=backup-vps.example.com
repo1-host-user=pgbackrest
repo1-path=/var/lib/pgbackrest
repo1-retention-full=4            # Mantener 4 backups completos
repo1-retention-diff=14           # Mantener 14 diferenciales
repo1-cipher-type=aes-256-cbc     # Cifrado en transito y reposo
repo1-cipher-pass=<clave-segura>
process-max=2                     # Paralelismo

[protegrt]
pg1-path=/var/lib/postgresql/16/main
pg1-port=5432
```

**Programacion de backups:**

| Tipo | Frecuencia | Retencion | Tamano estimado | Comando |
|------|-----------|-----------|-----------------|---------|
| Full backup | Domingo 02:00 | 4 semanas | ~500MB-2GB | `pgbackrest --stanza=protegrt backup --type=full` |
| Differential | Lun-Sab 02:00 | 14 dias | ~50-200MB | `pgbackrest --stanza=protegrt backup --type=diff` |
| WAL archive | Continuo | 14 dias | ~10-50MB/hora | Automatico via `archive_command` |

**Point-in-Time Recovery (PITR):**

```bash
# Restaurar al estado exacto de ayer a las 15:30
pgbackrest --stanza=protegrt \
  --type=time \
  --target="2026-02-13 15:30:00-06" \
  restore
```

### 3.4 Monitoreo de backups

**Script de verificacion diaria** (cron a las 08:00):

```bash
#!/bin/bash
# check_backup_status.sh

# Verificar que el ultimo backup fue exitoso
LAST_BACKUP=$(pgbackrest --stanza=protegrt info --output=json | jq -r '.[0].backup[-1]')
STATUS=$(echo $LAST_BACKUP | jq -r '.status')
AGE_HOURS=$(( ($(date +%s) - $(date -d "$(echo $LAST_BACKUP | jq -r '.timestamp.stop')" +%s)) / 3600 ))

if [ "$STATUS" != "ok" ] || [ $AGE_HOURS -gt 26 ]; then
  # Alertar via Telegram al administrador
  curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d "chat_id=${ADMIN_CHAT_ID}" \
    -d "text=ALERTA: Backup de BD fallo o tiene mas de 26 horas. Status: ${STATUS}, Edad: ${AGE_HOURS}h"
fi

# Verificar integridad del ultimo backup
pgbackrest --stanza=protegrt verify 2>&1 | tail -1
```

**Alertas configuradas:**
- Backup fallo o tarda mas de 26 horas -> Telegram al admin
- WAL archive gap detectado -> Telegram al admin
- Disco de backup > 80% -> Telegram al admin
- Test de restauracion mensual (automatizado en VPS temporal)

### 3.5 Correcciones pendientes al schema.sql

El informe de optimizacion identifico 3 issues ALTOS no corregidos en el schema:

| Issue | Problema | Correccion necesaria |
|-------|----------|---------------------|
| B8 | `payment_method_type` incompleto | Cambiar a: `cash, deposit, transfer, crucero, konfio, terminal_banorte` |
| B9 | `payment_plan_type` con valores incorrectos | Cambiar a: `cash, cash_2_installments, monthly_7` (eliminar semester, quarterly, monthly_12) |
| B10 | `policy` falta campo `prima_total` | Agregar `prima_total NUMERIC(12,2)` a tabla `policy` |
| B11 | `client` falta campo `rfc` | Agregar `rfc VARCHAR(13)` a tabla `client` |
| B12 | `collector.receipt_limit` default 5 | Cambiar default a 50 |

Estas correcciones deben aplicarse en el primer migration de Alembic antes de cualquier carga de datos.

---

## 4. AUTENTICACION Y AUTORIZACION

### 4.1 Arquitectura de tokens

> **IMPORTANTE:** TODO acceso al sistema requiere autenticacion. No existe acceso anonimo ni modo
> "solo lectura" sin login. Tampoco se implementa "Recordar usuario/contrasena" porque multiples
> personas usan las mismas PCs en la oficina.

```
LOGIN:
  Client -> POST /api/v1/auth/login {username, password}
  Server -> Verifica restriccion de acceso (VPN o geofencing, ver seccion 4.6)
         -> Verifica password hash (Argon2id)
         -> Genera:
            - Access Token (JWT, 15 min, en response body)
            - Refresh Token (opaque UUID, 7 dias, en httpOnly cookie)
         -> Almacena Refresh Token en Redis (key: token, value: user_id + device_id)
         -> Registra sesion en DB (session o device_session)
  Client <- {access_token, expires_in: 900, user: {...}}

REFRESH:
  Client -> POST /api/v1/auth/refresh (cookie con refresh_token)
  Server -> Busca refresh_token en Redis
         -> Si existe y no expirado:
            - Genera nuevo Access Token
            - Rota Refresh Token (nuevo UUID, invalida el anterior)
         -> Si no existe: 401 (sesion expirada)
  Client <- {access_token, expires_in: 900}

LOGOUT:
  Client -> POST /api/v1/auth/logout (cookie con refresh_token)
  Server -> Elimina refresh_token de Redis
         -> Marca sesion como inactiva en DB
  Client <- 204 No Content
```

### 4.2 Estructura del Access Token (JWT)

```json
{
  "sub": "42",                          // user_id
  "username": "juan.perez",
  "roles": ["gerente", "vendedor"],     // Un usuario puede tener MULTIPLES roles
  "departments": ["ventas", "cobranza"],// Departamentos asociados
  "permissions": ["payments.*", "collections.*", "policies.read", "renewals.*"],
  "device_id": "abc-123",              // null para web
  "iat": 1739520000,
  "exp": 1739520900                     // 15 minutos
}
```

**Configuracion JWT:**
- Algoritmo: RS256 (par de claves publica/privada, no HS256 con secret compartido)
- Access Token TTL: 15 minutos
- Refresh Token TTL: 7 dias (web), 30 dias (app movil)
- Rotacion de refresh tokens: siempre (cada uso genera uno nuevo)
- Blacklist: no necesaria con TTL corto + rotacion

### 4.3 RBAC mejorado

> **NOTA IMPORTANTE:** Un empleado puede tener MULTIPLES roles simultaneamente. Ejemplos reales:
> - El dev es admin + ajustador + vendedor
> - El director general es vendedor + ajustador
> - Todos los vendedores son tambien cobradores (pueden recibir dinero en ventas y cobrar a sus clientes)
> - Los ajustadores tambien cobran pagos atrasados de menos de 5 dias o dinero de contraparte para taller
>
> El sistema de roles debe modelarse como una relacion muchos-a-muchos (usuario <-> roles).
> Los permisos efectivos de un usuario son la UNION de los permisos de todos sus roles.
>
> **NOTA:** NO implementar acceso granular configurable ahora, solo preparar el terreno con la estructura
> de permisos. La configuracion fina se hara cuando el sistema este en uso.

**Areas comunes a TODOS los roles:**

| Area | Acceso |
|------|--------|
| Gruas | Crear, editar, ver |
| Siniestros | Crear, editar, ver |
| Clientes | READ ONLY (solo lectura para todos excepto admin) |
| Polizas | READ ONLY (solo lectura para todos excepto admin) |
| Guardias de ajustadores | READ ONLY (solo lectura para todos) |
| Recursos Humanos (panel personal) | Cada usuario accede a SU propio panel: vacaciones, permisos sin goce de sueldo, horario, quejas/sugerencias a jefe directo o director |

**Roles predefinidos:**

| Rol | Descripcion | Permisos clave |
|-----|------------|----------------|
| `admin` | Acceso total (solo 2 usuarios: director general y el dev) | `*` |
| `gerente` | Gerente de area (antes "supervisor") | Areas comunes + TODOS los apartados de su area (admin, ventas, cobranza, RRHH). Accede a dashboards de su departamento, reportes, y gestion de personal. |
| `auxiliar` | Auxiliar de oficina (antes "capturista") | Areas comunes + ALGUNOS apartados de su departamento. **CONFIGURABLE por admin** ya que hay varios auxiliares que hacen cosas diferentes. |
| `cobrador` | Cobrador de campo | Areas comunes + acceso a su cartera (cuentas asignadas), ver pagos dados/pendientes, fechas, cobertura de poliza, datos del vehiculo, dinero recolectado/pendiente por entregar, gestionar rutas. |
| `vendedor` | Vendedor de campo (TODOS los vendedores son tambien cobradores) | Areas comunes + buscar sus propios clientes, renovaciones, editar renovaciones, ver dinero por entregar, generar nuevas polizas. Pueden recibir dinero en ventas y cobrar a sus clientes. |
| `ajustador` | Ajustador de campo | Areas comunes + informacion completa de siniestros asignados. Tambien cobran pagos atrasados <5 dias y dinero de contraparte para taller. |

**Permisos granulares (patron recurso.accion):**

```
# Formato: modulo.accion

# --- Areas comunes (TODOS los roles) ---
tow.create               # Crear servicios de grua
tow.edit                 # Editar servicios de grua
tow.read                 # Ver servicios de grua
incidents.create          # Crear siniestros
incidents.edit            # Editar siniestros
incidents.read            # Ver siniestros

# --- Areas comunes READ ONLY ---
clients.read             # Ver clientes (todos)
policies.read            # Ver polizas (todos)
shifts.read              # Ver guardias de ajustadores (todos)

# --- Recursos Humanos (panel personal) ---
hr.my_vacations          # Solicitar/ver mis vacaciones
hr.my_permits            # Solicitar/ver mis permisos sin goce
hr.my_schedule           # Ver mi horario
hr.my_complaints         # Enviar quejas/sugerencias a jefe directo o director

# --- Permisos de rol especificos ---
policies.create          # Crear polizas (vendedor, gerente, admin)
policies.read_own        # Solo polizas del vendedor actual (vendedor)
policies.edit            # Editar polizas (gerente, admin)
policies.cancel          # Cancelar polizas (gerente, admin)
policies.change_seller   # Cambiar vendedor de poliza (gerente, admin)

clients.create           # Crear clientes (vendedor, gerente, admin)
clients.edit             # Editar clientes (gerente, admin)

payments.read            # Ver situacion de pagos (TODOS pueden ver, solo cobranza edita)
payments.edit            # Editar pagos (solo area de cobranza)
payments.revert          # Revertir un pago (gerente cobranza, admin)

proposals.create         # Crear propuesta de cobro (cobrador, vendedor)
proposals.read_own       # Ver mis propuestas (cobrador, vendedor)
proposals.approve        # Aprobar propuestas (gerente cobranza, admin)
proposals.reject         # Rechazar propuestas (gerente cobranza, admin)

collections.read         # Ver asignaciones de cobranza (gerente)
collections.read_own     # Solo mis asignaciones (cobrador)
collections.assign       # Reasignar tarjetas (gerente, admin)
collections.routes       # Gestionar rutas (cobrador, gerente)

receipts.assign          # Asignar recibos a cobradores (gerente, admin)
receipts.cancel          # Cancelar recibos con reversion (gerente, admin)

incidents.read_assigned  # Solo siniestros asignados a mi (ajustador)
incidents.update_own     # Actualizar mis siniestros (ajustador)

renewals.read_own        # Ver mis renovaciones (vendedor)
renewals.edit            # Editar renovaciones (vendedor, gerente)

hr.manage                # Gestionar RRHH del departamento (gerente)
hr.admin                 # Gestionar RRHH global (admin)

reports.*                # Generar reportes (gerente, admin)
admin.*                  # Gestion de usuarios, roles, config (solo admin)
```

### 4.4 Sesiones por dispositivo

Cada login genera una sesion independiente vinculada al dispositivo:

```
Usuario "Juan Perez" puede tener sesiones simultaneas:
  - Web (Chrome, oficina)       -> session table
  - App Cobrador (Android)      -> device_session table
  - App Cobrador (tablet)       -> device_session table

Cada sesion tiene su propio refresh token.
Cerrar sesion en un dispositivo NO afecta las demas.
El admin puede ver y revocar sesiones individuales.
```

### 4.5 2FA opcional

Implementacion con TOTP (Google Authenticator / Authy):

```
Activacion:
  1. Usuario accede a /settings/security
  2. Backend genera secret TOTP (pyotp)
  3. Frontend muestra QR code
  4. Usuario escanea con app authenticator
  5. Usuario ingresa codigo de 6 digitos para verificar
  6. Backend almacena secret cifrado en app_user.totp_secret

Login con 2FA:
  1. POST /auth/login -> si user.totp_enabled: retorna {requires_2fa: true, temp_token: "..."}
  2. POST /auth/verify-2fa {temp_token, totp_code} -> valida codigo -> retorna access + refresh tokens
```

Recomendacion: Obligatorio para roles `admin` y `gerente`. Opcional para el resto.

### 4.6 Restriccion de acceso: VPN o geofencing

El sistema NO debe ser accesible desde cualquier lugar sin restriccion. Se implementara uno de dos mecanismos (VPN es la opcion preferida):

**Opcion A: VPN (preferida)**

```
ARQUITECTURA VPN:
  VPS (EasyPanel)
    |
    +-- WireGuard / OpenVPN server
    |     |-- Solo acepta conexiones de IPs de VPN
    |     |-- Empleados instalan cliente VPN en sus dispositivos
    |     |-- El backend verifica que la IP de origen pertenece al rango VPN
    |
    +-- Firewall (iptables/nftables)
          |-- Puerto 443 (HTTPS): solo acepta desde rango VPN
          |-- Excepcion: apps moviles via VPN tambien
```

- Configurar servidor VPN (WireGuard preferido por rendimiento) directamente en el VPS
- Los empleados se conectan via VPN desde sus dispositivos (PC oficina, apps moviles)
- El backend rechaza conexiones que no vengan del rango de IPs de la VPN
- **Admins EXENTOS:** los usuarios con rol `admin` pueden acceder desde cualquier IP

**Opcion B: Geofencing + horario (fallback si VPN no es viable)**

```
RESTRICCION POR UBICACION Y HORARIO:
  En cada request:
    1. Obtener coordenadas GPS del dispositivo (navegador o app movil)
    2. Verificar que el usuario esta dentro del radio permitido
       (ej: 500m de la oficina para web, 50km para apps moviles en campo)
    3. Verificar que la hora actual esta dentro del horario laboral del usuario
    4. Si no cumple -> 403 Forbidden con mensaje descriptivo

  Excepciones:
    - Admins: sin restriccion de ubicacion ni horario
    - Permisos especiales temporales: un admin puede conceder acceso
      fuera de horario/ubicacion a un usuario especifico por un periodo definido
      (ej: "Juan puede acceder desde casa el sabado de 9am a 2pm")
```

- GPS del navegador + horario laboral configurado por usuario
- Radio de geofencing configurable por tipo de dispositivo
- Opcion de conceder permisos especiales temporales por admin
- **Admins EXENTOS:** los usuarios con rol `admin` pueden acceder sin restriccion de ubicacion ni horario

---

## 5. DESPLIEGUE EN EASYPANEL

### 5.1 Contenedores Docker

```yaml
# docker-compose.prod.yml (simplificado - EasyPanel lo orquesta)

services:
  # --- Base de datos ---
  postgres:
    image: postgis/postgis:16-3.4
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
    environment:
      POSTGRES_DB: protegrt_db
      POSTGRES_USER: protegrt
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          memory: 4G

  pgbouncer:
    image: edoburu/pgbouncer:1.22
    volumes:
      - ./docker/pgbouncer/pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini
    ports:
      - "6432:6432"
    depends_on:
      - postgres

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # --- Backend ---
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://protegrt:${DB_PASSWORD}@pgbouncer:6432/protegrt_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_PRIVATE_KEY_PATH: /run/secrets/jwt_private_key
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
      WHATSAPP_API_URL: ${WHATSAPP_API_URL}
      WHATSAPP_API_KEY: ${WHATSAPP_API_KEY}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      QUOTES_API_URL: ${QUOTES_API_URL}
      QUOTES_API_KEY: ${QUOTES_API_KEY}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - pgbouncer
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G

  # --- Celery worker ---
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks worker -l info -c 4
    environment:
      DATABASE_URL: postgresql+asyncpg://protegrt:${DB_PASSWORD}@pgbouncer:6432/protegrt_db
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - pgbouncer
      - redis
    deploy:
      resources:
        limits:
          memory: 1G

  # --- Celery beat (scheduler) ---
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.tasks beat -l info --schedule=/tmp/celerybeat-schedule
    environment:
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
    deploy:
      replicas: 1

  # --- Frontend ---
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: https://api.protegrt.com
      NEXT_PUBLIC_WS_URL: wss://api.protegrt.com
    ports:
      - "3000:3000"
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
```

### 5.2 Reverse proxy y SSL

EasyPanel usa Traefik internamente. Configuracion de dominios:

| Dominio | Servicio | Puerto |
|---------|----------|--------|
| `app.protegrt.com` | frontend (Next.js) | 3000 |
| `api.protegrt.com` | backend (FastAPI) | 8000 |
| `api.protegrt.com/ws` | WebSocket (Socket.IO) | 8000 |
| `archivos.protegrt.com` | protegrt-files (ya existente) | -- |
| `cotizaciones.protegrt.com` | cotizaciones API (ya existente) | -- |

**SSL:** Traefik en EasyPanel obtiene certificados Let's Encrypt automaticamente. No requiere configuracion manual.

**Headers de seguridad** (configurados en Traefik):
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0
Content-Security-Policy: default-src 'self'; script-src 'self'; connect-src 'self' wss://api.protegrt.com
Referrer-Policy: strict-origin-when-cross-origin
```

### 5.3 Variables de entorno para secrets

**NUNCA en codigo.** Todo en variables de entorno de EasyPanel:

```
# Base de datos
DB_PASSWORD=<generado-aleatorio-32-chars>
REDIS_PASSWORD=<generado-aleatorio-32-chars>

# JWT (par de claves RSA, generadas una vez)
JWT_PRIVATE_KEY=<contenido-PEM-base64>
JWT_PUBLIC_KEY=<contenido-PEM-base64>

# APIs externas
WHATSAPP_API_URL=https://evolution-api.protegrt.com
WHATSAPP_API_KEY=<rotada-periodicamente>
WHATSAPP_INSTANCE=protegrt

TELEGRAM_BOT_TOKEN=<token-del-bot>
TELEGRAM_SINIESTROS_GROUP_ID=-1002128363151
TELEGRAM_GERENTE_VENTAS_ID=7802431635

QUOTES_API_URL=https://cotizaciones.protegrt.com
QUOTES_API_KEY=<clave-api>

FILES_API_URL=https://archivos.protegrt.com
FILES_API_KEY=<clave-api>

# Backups
BACKUP_VPS_HOST=<ip-vps-backup>
BACKUP_VPS_SSH_KEY=<clave-ssh-base64>
PGBACKREST_CIPHER_PASS=<clave-cifrado-backups>

# Aplicacion
ENVIRONMENT=production
CORS_ORIGINS=https://app.protegrt.com
```

### 5.4 CI/CD desde GitHub

```yaml
# .github/workflows/deploy.yml
name: Deploy to EasyPanel

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install backend dependencies
        run: cd backend && pip install -e ".[test]"

      - name: Run linter (ruff)
        run: cd backend && ruff check .

      - name: Run type checker (mypy)
        run: cd backend && mypy app/

      - name: Run backend tests
        run: cd backend && pytest tests/ -v --cov=app --cov-report=term-missing
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"

      - name: Install frontend dependencies
        run: cd frontend && npm ci

      - name: Run frontend linter
        run: cd frontend && npm run lint

      - name: Run frontend type check
        run: cd frontend && npm run type-check

      - name: Build frontend
        run: cd frontend && npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to EasyPanel
        uses: easypanel-io/deploy@v1
        with:
          easypanel-url: ${{ secrets.EASYPANEL_URL }}
          app-name: protegrt-crm
          token: ${{ secrets.EASYPANEL_TOKEN }}
```

**Reglas de CI/CD:**
- Todo push a `main` dispara deploy automatico
- PR a `main` requiere: tests verdes, linter limpio, type-check limpio
- Branch `develop` para desarrollo diario
- Tags `v*` para releases

### 5.5 Monitoreo y alertas

| Herramienta | Proposito | Como |
|-------------|-----------|------|
| **Sentry** | Errores de aplicacion (backend + frontend) | SDK en FastAPI y Next.js. Alertas a Telegram. |
| **Uptime Kuma** | Monitoreo de disponibilidad | Contenedor en EasyPanel. Chequea cada 60s: api.protegrt.com, app.protegrt.com, PostgreSQL. Alerta via Telegram si cae. |
| **pg_stat_statements** | Queries lentas | Extension PostgreSQL. Dashboard en Grafana o consulta directa. |
| **Celery Flower** | Monitoreo de tareas async | Contenedor en EasyPanel. UI web para ver tareas en cola, fallidas, tiempos. |
| **Docker healthchecks** | Salud de contenedores | Cada contenedor tiene HEALTHCHECK en Dockerfile. EasyPanel reinicia si falla. |
| **Logs centralizados** | Debugging | JSON structured logging -> stdout -> EasyPanel log viewer. Opcionalmente Loki + Grafana. |
| **pgBackRest verify** | Integridad de backups | Cron diario. Alerta via Telegram si falla. |

---

## 6. ROADMAP DE IMPLEMENTACION

### 6.1 Principio rector

**No recrear todo a la vez.** El sistema actual funciona. La migracion debe ser incremental, con cada fase produciendo valor usable.

### 6.2 Fases

```
Fase 0: Infraestructura y Base          [2-3 semanas]
  |
  v
Fase 1: Auth + Clientes + Polizas      [4-6 semanas]
  |
  v
Fase 2: Pagos + Recibos + Autorizacion [4-6 semanas]
  |
  v
Fase 3: Cobranza + App Cobradores      [4-6 semanas]
  |
  v
Fase 4: Siniestros + Gruas + Endosos   [4-6 semanas]
  |
  v
Fase 5: Notificaciones + Mensajeria    [3-4 semanas]
  |
  v
Fase 6: App Vendedores + Renovaciones  [3-4 semanas]
  |
  v
Fase 7: App Ajustadores                [2-3 semanas]
  |
  v
Fase 8: Migracion de Datos + Go-Live   [2-3 semanas]
```

---

### FASE 0: Infraestructura y Base (2-3 semanas)

**Objetivo:** Tener el esqueleto del proyecto funcionando end-to-end.

**Entregables:**
1. Repositorio Git con estructura de carpetas completa
2. Docker Compose para desarrollo local (PostgreSQL + PostGIS + PgBouncer + Redis)
3. Backend FastAPI: proyecto base con core/ (config, database, security, exceptions)
4. Alembic configurado con primera migracion (tablas base: municipality, address, department, role, permission, app_user)
5. Frontend Next.js: proyecto base con layout, tema, login page placeholder
6. CI/CD: GitHub Actions con lint + type-check + build
7. EasyPanel: servicios creados (PostgreSQL, Redis, backend, frontend)
8. pgBackRest configurado y primer backup completo exitoso
9. Sentry y Uptime Kuma configurados

**Dependencias:** Ninguna (es la base de todo).

**Por que primero:** Sin infraestructura no hay donde construir. Esta fase elimina toda la incertidumbre tecnica de deploy.

---

### FASE 1: Auth + Clientes + Polizas (4-6 semanas)

**Objetivo:** El core del sistema funcional: login, ver clientes, crear y consultar polizas.

**Entregables Backend:**
1. Modulo `auth`: Login, JWT RS256, refresh tokens, sesiones, middleware de permisos
2. Modulo `clients`: CRUD completo con busqueda por nombre (pg_trgm), paginacion
3. Modulo `policies`: CRUD, creacion con calculo automatico de pagos, maquina de estados
4. Modulo `coverages`: Catalogo de coberturas con precios, busqueda por criterios
5. StatusUpdater: Reimplementado como Celery task con tests completos
6. Migracion Alembic de todas las tablas de Fase 1

**Entregables Frontend:**
1. Login funcional con manejo de tokens
2. Layout principal: sidebar, header, breadcrumb
3. Listado de clientes con busqueda y filtros
4. Formulario de cliente (crear/editar)
5. Listado de polizas con filtros por status, vendedor, cobertura
6. Formulario de poliza con seleccion de cobertura, calculo de pagos, vista previa
7. Detalle de poliza con timeline de pagos

**Tests prioritarios:** StatusUpdater (P0), calculo de montos de pago (P0), auth flow (P0).

**Dependencias:** Fase 0 completa.

**Por que primero:** Polizas es el nucleo del negocio. Sin polizas y clientes, nada mas tiene sentido. Ademas, valida toda la arquitectura end-to-end.

---

### FASE 2: Pagos + Recibos + Flujo de Autorizacion (4-6 semanas)

**Objetivo:** Gestion completa de pagos y el flujo "pendiente de autorizacion".

**Entregables Backend:**
1. Modulo `payments`: CRUD, edicion con validaciones completas (8 meses max, 30 dias diff), reversion, abonos parciales
2. Modulo `receipts`: Registro de lotes, asignacion a cobradores, verificacion, ciclo de vida completo, extravios programados
3. `proposal_service`: Flujo de autorizacion (pending -> under_review -> approved -> applied / rejected)
4. Restructuracion contado-a-cuotas
5. Modulo `promotions`: Sistema flexible con reglas, aplicacion a pagos, reversion

**Entregables Frontend:**
1. Tabla de pagos por poliza con edicion inline
2. Dialogo de edicion de pago con todas las validaciones
3. Gestion de recibos: lotes, asignacion, busqueda, cancelacion
4. Panel de "Pendientes de Autorizacion" con: lista de propuestas, aprobar/rechazar, detalle
5. Dashboard de promociones activas, crear/editar reglas

**Tests prioritarios:** Calculo de pagos (P0), flujo de autorizacion (P1), ciclo de recibos (P2).

**Dependencias:** Fase 1 completa.

---

### FASE 3: Cobranza + App Cobradores (4-6 semanas)

**Objetivo:** Sistema de cobranza web y app movil para cobradores.

**Entregables Backend:**
1. Modulo `collections`: Tarjetas, asignaciones, algoritmo de afinidad reimplementado con tests
2. Endpoints para app movil: ruta de cobranza, clientes cercanos (PostGIS), registrar cobro con GPS + foto
3. WebSockets: notificaciones de propuestas aprobadas/rechazadas

**Entregables Frontend:**
1. Dashboard de cobranza: tarjetas por cobrador, reasignacion drag-and-drop
2. Vista de cobrador: recibos asignados, polizas a cobrar, estadisticas
3. Mapa de calor de cobranza (PostGIS)

**Entregables App Movil (React Native):**
1. App Cobradores v1.0:
   - Login y sesion por dispositivo
   - Lista de polizas a cobrar (mis asignaciones)
   - Mapa con ruta de cobranza (React Native Maps + PostGIS)
   - Registrar cobro: seleccionar poliza, escanear/ingresar recibo, monto, metodo, foto
   - Envio como propuesta (pendiente de autorizacion)
   - Notificaciones push de aprobacion/rechazo
   - Historial de mis cobros

**Tests prioritarios:** Algoritmo de afinidad (P2), PostGIS queries (P2).

**Dependencias:** Fase 2 completa.

---

### FASE 4: Siniestros + Gruas + Endosos (4-6 semanas)

**Objetivo:** Gestion completa de siniestros, gruas y endosos.

**Entregables Backend:**
1. Modulo `incidents`: CRUD siniestros, ajustadores, guardias, pases medicos y de taller
2. Modulo `tow`: CRUD gruas, proveedores, validacion de elegibilidad
3. Modulo `endorsements`: Los 5 tipos de endoso con validaciones
4. Encuestas de satisfaccion
5. Validacion de elegibilidad para grua (reglas por cobertura, status pago)

**Entregables Frontend:**
1. Registro de siniestro con formulario paso-a-paso
2. Listado y detalle de siniestros con filtros
3. Registro de servicio de grua
4. Gestion de ajustadores y guardias (calendario)
5. Gestion de endosos por poliza
6. Proveedores de grua con mapa (PostGIS)

**Tests prioritarios:** Elegibilidad de grua (P3), validacion de endosos (P3).

**Dependencias:** Fase 1 completa (requiere polizas). Puede hacerse en paralelo con Fase 3 si hay recursos.

---

### FASE 5: Notificaciones + Mensajeria (3-4 semanas)

**Objetivo:** Sistema unificado de notificaciones multi-canal.

**Entregables Backend:**
1. Modulo `notifications` con adaptadores para: WhatsApp (Evolution API), Telegram (Bot API), Push (FCM), Email (futuro)
2. Motor de mensajes a morosos con reglas de frecuencia reimplementadas
3. Motor de recordatorios de pago
4. Cola de mensajes con reintentos (Celery + Redis)
5. Plantillas de mensajes configurables
6. Historial de mensajes con tracking de entrega

**Entregables Frontend:**
1. Panel de mensajeria: envio manual/automatico, filtros, preview
2. Configuracion de plantillas de mensajes
3. Historial de mensajes enviados con status de entrega
4. Dashboard de efectividad de mensajeria

**Dependencias:** Fase 2 completa (requiere pagos para morosos/recordatorios).

---

### FASE 6: App Vendedores + Renovaciones (3-4 semanas)

**Objetivo:** App movil para vendedores y gestion de renovaciones.

**Entregables Backend:**
1. Modulo `renewals`: Reporte de renovaciones, calculo de elegibilidad, notificaciones
2. Endpoints movil para vendedores: crear cotizacion, crear poliza, mis polizas, renovaciones pendientes

**Entregables App Movil:**
1. App Vendedores v1.0:
   - Login
   - Mis polizas (listado, detalle)
   - Crear poliza desde app (como propuesta, pendiente de autorizacion)
   - Cotizaciones (enlace al sistema de cotizaciones)
   - Renovaciones pendientes con notificaciones

**Entregables Frontend:**
1. Reporte de renovaciones (Excel exportable)
2. Dashboard de renovaciones por vendedor

**Dependencias:** Fase 1 y Fase 5 (notificaciones).

---

### FASE 7: App Ajustadores (2-3 semanas)

**Objetivo:** App movil para ajustadores.

**Entregables App Movil:**
1. App Ajustadores v1.0:
   - Login
   - Siniestros asignados (listado)
   - Detalle de siniestro con datos del cliente y poliza
   - Subir fotos del siniestro/vehiculo
   - Actualizar status del siniestro
   - Mi turno de guardia actual
   - Notificaciones push de nuevos siniestros

**Dependencias:** Fase 4 completa (requiere siniestros).

---

### FASE 8: Migracion de Datos + Go-Live (2-3 semanas)

**Objetivo:** Migrar datos de MySQL a PostgreSQL y poner en produccion.

**Entregables:**
1. Script de migracion MySQL -> PostgreSQL probado y verificado
2. Plan de migracion con downtime minimo:
   - Viernes noche: Congelar sistema actual (solo lectura)
   - Sabado: Ejecutar migracion completa
   - Sabado/Domingo: Verificacion exhaustiva de datos
   - Lunes: Go-live con nuevo sistema
3. Rollback plan documentado (volver a MySQL si hay problemas criticos)
4. Periodo de transicion (1-2 semanas): ambos sistemas corriendo en paralelo para comparar
5. Capacitacion del equipo en el nuevo sistema

**Dependencias:** Todas las fases anteriores completas.

---

### 6.3 Resumen visual del roadmap

```
Semana:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
         |--------|
         Fase 0: Infraestructura
                  |----------------|
                  Fase 1: Auth + Polizas + Clientes
                                    |----------------|
                                    Fase 2: Pagos + Recibos + Autorizacion
                                                      |----------------|
                                                      Fase 3: Cobranza + App Cobradores
                                                      |----------------|
                                                      Fase 4: Siniestros (paralelo si hay recursos)
                                                                        |-----------|
                                                                        Fase 5: Notificaciones
                                                                                     |-----------|
                                                                                     Fase 6: App Vendedores
                                                                                               |--------|
                                                                                               Fase 7: App Ajustadores
                                                                                                        |--------|
                                                                                                        Fase 8: Migracion
```

### 6.4 Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Migracion de datos con perdida | Media | Critico | Script de migracion con verificacion automatica. Backup antes de migrar. Periodo de sistemas paralelos. |
| Performance de PostGIS en VPS limitado | Baja | Alto | Indices GiST correctos. PgBouncer. Cache en Redis. Monitoring desde Fase 0. |
| Apps moviles rechazadas por App Store | Media | Medio | Comenzar con APK directo (Android). iOS usa TestFlight. EAS Build de Expo simplifica. |
| Equipo no adopta nuevo sistema | Media | Critico | Involucrar al equipo desde Fase 1. Capacitacion continua. UI familiar al sistema actual. |
| Celery/Redis cae y tareas se pierden | Baja | Alto | Redis con persistencia (AOF). Celery con `acks_late=True`. Monitoreo con Flower. |
| Backup falla sin detectarse | Media | Critico | Verificacion diaria automatizada con alerta Telegram. Test de restauracion mensual. |

---

## APENDICE A: Decisiones Descartadas

| Opcion | Razon de descarte |
|--------|-------------------|
| Microservicios desde el inicio | Over-engineering para equipo pequeno. Monolito modular permite descomponer despues. |
| GraphQL en lugar de REST | Mayor complejidad sin beneficio claro para este tipo de CRM. REST + OpenAPI es mas simple y mejor documentado. |
| PWA en lugar de React Native | GPS background, camara, push confiable, y offline requieren apps nativas. PWA no alcanza. |
| MongoDB en lugar de PostgreSQL | Datos relacionales (polizas-pagos-clientes) requieren ACID y JOINs. PostgreSQL con JSONB da flexibilidad sin sacrificar integridad. |
| Django en lugar de FastAPI | Django es excelente pero su ORM async es inmaduro. FastAPI + SQLAlchemy 2.0 async es superior para APIs con WebSockets. |
| Flutter en lugar de React Native | Si solo se hicieran apps moviles, Flutter seria mejor. Pero compartir TypeScript con Next.js y validaciones es mas productivo para un equipo pequeno. |
| Supabase / Firebase | Vendor lock-in. El equipo necesita control total de la BD (PostGIS, pgBackRest, triggers custom). |

---

## APENDICE B: Comparativa con Sistema Actual

| Aspecto | Sistema Actual (PyQt5) | Sistema Nuevo |
|---------|----------------------|---------------|
| Plataforma | Desktop (Windows) | Web + Mobile (cualquier dispositivo) |
| Base de datos | MySQL 5.7, LAN | PostgreSQL 16 + PostGIS, Internet |
| Arquitectura | Monolito con capas rotas | Monolito modular con capas estrictas |
| Autenticacion | JWT HS256, verify_exp=False, secret hardcoded | JWT RS256, 15min TTL, refresh tokens, 2FA |
| Seguridad | Credenciales en git, SQL injection parcial | Env vars, parameterized queries, CORS, rate limiting |
| Tests | 0% cobertura | 75% unitarios, 20% integracion, 5% E2E |
| CI/CD | git pull manual (start.bat) | GitHub Actions automatico |
| Backups | -- | pgBackRest con PITR, backup a otro VPS |
| Notificaciones | WhatsApp/Telegram sincronico | Multi-canal async con cola y reintentos |
| Geolocalizacion | -- | PostGIS, rutas de cobranza, clientes cercanos |
| Apps moviles | -- | React Native (cobradores, vendedores, ajustadores) |
| Promociones | Solo porcentaje | Reglas flexibles: %, monto fijo, meses gratis, $0 enganche |
| Autorizacion de pagos | pagos_temporales basico | Workflow completo con niveles, auditoria, GPS, foto |
| Monitoreo | -- | Sentry, Uptime Kuma, Celery Flower, pg_stat_statements |
| Escalabilidad | 1 maquina | Docker containers, horizontal scaling |

---

**Fin del documento de arquitectura.**
