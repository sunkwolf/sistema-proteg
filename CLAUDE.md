# CLAUDE.md - Reglas del Nuevo Proyecto CRM Protegrt

Este archivo se copiara al repositorio del nuevo proyecto cuando se cree.

---

## Stack Tecnologico

- **Backend**: FastAPI (Python 3.11+) con async/await
- **Frontend**: Next.js 14 + React + TypeScript + shadcn/ui + Tailwind CSS
- **Mobile**: React Native + Expo (TypeScript)
- **Base de datos**: PostgreSQL 16 + PostGIS
- **Cache/Queue**: Redis + Celery
- **Auth**: JWT RS256 access (15min) + UUID opaco refresh (7d web / 30d movil) con rotacion
- **WhatsApp**: Evolution API
- **Deploy**: Docker + EasyPanel en VPS
- **Backup**: pgBackRest a VPS secundario

## Arquitectura

**Monolito modular** — NO microservicios. Todo en un solo proyecto FastAPI organizado por modulos.

```
backend/
  app/
    modules/
      auth/          # Login, JWT, 2FA, sesiones
      employees/     # CRUD unificado (vendedor+cobrador+ajustador)
      clients/       # CRUD + PostGIS + verificacion WhatsApp
      vehicles/      # CRUD + claves (101-109)
      coverages/     # Tabla de precios RC, AMPLIA individual
      policies/      # CRUD + StatusUpdater + pendiente autorizacion
      payments/      # CRUD + maquina estados + contado a cuotas
      authorization/ # Panel unificado: pagos + polizas pendientes
      receipts/      # Batch, asignar, verificar, digitales
      collections/   # Tarjetas, movimientos, asignacion
      cancellations/ # C1-C5 + reactivacion
      renewals/      # Deteccion, notificacion, seguimiento
      incidents/     # Siniestros (vinculado a poliza)
      tow_services/  # Gruas (vinculado a poliza)
      endorsements/  # 5 tipos + costo auto + WhatsApp
      promotions/    # 4 tipos: %, fijo, meses gratis, $0 enganche
      notifications/ # WhatsApp + Telegram
      reports/       # Excel (sin export de clientes)
      dashboard/     # Por departamento + principal
      admin/         # Config, audit log, permisos
    core/
      database.py    # AsyncSession, engine
      security.py    # JWT RS256, hashing
      dependencies.py # Depends() comunes
      middleware.py   # Auth, CORS, rate limiting
    jobs/
      status_updater.py  # Celery: corre a medianoche
```

## Reglas Estrictas

### Base de Datos
- NUNCA SQL en la capa de vista/controlador. Todo pasa por repositories (patron Repository)
- SIEMPRE usar parametros ($1, $2) para queries. NUNCA f-strings con SQL
- SIEMPRE usar transacciones para operaciones que modifican multiples tablas
- Usar AsyncSession de SQLAlchemy para todas las operaciones
- PostGIS para direcciones de clientes (punto geografico)

### Seguridad
- NUNCA guardar secretos en codigo. Solo variables de entorno
- NUNCA exponer stacktraces en produccion. Loggear internamente, devolver error generico
- TODOS los endpoints requieren autenticacion excepto POST /auth/login y POST /auth/mobile/login
- JWT RS256 (NO HS256). Clave privada en el servidor, publica para verificar
- NO "remember me" / "recordar sesion". Las PCs se comparten
- Access token en memoria (JS), NUNCA en localStorage
- Refresh token: UUID opaco, hash SHA-256 almacenado en Redis (NUNCA el token en claro)
- Refresh token en cookie httpOnly + Secure + SameSite=Strict
- Hashing de passwords: Argon2id (bcrypt como fallback para passwords migrados)
- Verificar permisos en CADA endpoint con Depends(require_permission("modulo.accion"))
- Rate limiting en login: 5 intentos por usuario / 10 por IP en 15 minutos. Bloqueo cuenta a los 10 intentos por 30 min
- No permitir export CSV/Excel de lista de clientes (datos sensibles)
- RFC: validar formato estricto (12 o 13 chars, uppercase, alfanumerico, sin guiones)

### Empleados (Concepto Central)
- UN empleado puede ser vendedor Y cobrador Y ajustador simultaneamente
- Flags: es_vendedor, es_cobrador, es_ajustador en la tabla employee
- Un empleado puede pertenecer a MULTIPLES departamentos (tabla employee_department)
- es_gerente es per-departamento, no un rol global
- Permisos = rol_base UNION permisos_por_flags UNION overrides_individuales

### Pagos
- Solo el departamento de Cobranza puede EDITAR pagos
- Contado a Cuotas: integrado en modulo de pagos (no vista separada)
- Maquina de estados: pending → late → overdue → paid / cancelled
- Job diario a medianoche actualiza estados automaticamente

### Polizas
- Vinculadas a vehiculo + cliente + vendedor(empleado)
- Gruas y siniestros se vinculan a POLIZA, no solo a cliente
- StatusUpdater recalcula status basado en pagos
- Pueden quedar en "pendiente de autorizacion"

### Coberturas y Vehiculos
- Claves: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA, 107=MOTOCICLETA, 108=MOTO TAXI, 109=CAMION
- 102 no se usa
- AMPLIA SELECT solo elegible para claves 101, 103, 105
- AMPLIA se cotiza individualmente (precio 0.00 en tabla)

### Promociones
- 4 tipos: porcentaje, monto fijo, meses gratis, $0 enganche
- Condiciones en JSONB (flexible, no hardcoded)
- Fechas de vigencia configurables

### Cotizaciones
- Sistema SEPARADO. No hacer JOINs a tablas de cotizaciones
- Solo guardar quote_external_id como referencia

### Frontend
- shadcn/ui para componentes. No instalar otras librerias de UI
- Server Components por defecto, Client Components solo cuando se necesite interactividad
- Formularios con react-hook-form + zod para validacion
- Fetching con tanstack/react-query
- Tema oscuro no es prioridad (solo tema claro)

### Apps Moviles
- React Native + Expo (managed workflow)
- SecureStore para tokens (NO AsyncStorage)
- GPS tracking solo cuando la app esta en primer plano (ahorro de bateria)
- Modo offline basico: cache de datos criticos, cola de acciones pendientes

### Testing
- Backend: pytest + httpx (async) + factory_boy para fixtures
- Frontend: Vitest + Testing Library
- Minimo: tests para auth, pagos, StatusUpdater, migracion de datos

### Git
- Branch principal: main
- Branch de desarrollo: develop
- Feature branches: feature/nombre-modulo
- Commits en espanol, descriptivos
- No hacer push --force a main ni develop

## Documentacion de Referencia

Toda la planeacion esta en la carpeta `nuevo-sistema/` del proyecto actual (D:\pqtcreacion):
- 01-ARQUITECTURA.md — Stack, modulos, deployment
- 02-VISTAS-Y-PANTALLAS.md — Todas las vistas web y moviles
- 03-API-Y-LOGICA.md — 189+ endpoints, logica de negocio completa
- 04-SEGURIDAD-DESPLIEGUE-MIGRACION.md — OWASP, JWT, backup, migracion
- 05-CHECKLIST-PROYECTO.md — Estado de todas las tareas
- 06-CONSIDERACIONES-FINALES.md — Errores del schema, diferencias, riesgos
- 07-INSTRUCCIONES-USUARIO.md — Pasos que debe ejecutar el usuario

Documentacion del sistema actual en `docs/`:
- INFORME_LOGICA_NEGOCIO.md — 26 modulos de logica documentados
- INFORME_ANALISIS_MYSQL.md — Problemas del schema actual
- INFORME_OPTIMIZACION.md — 45 hallazgos y propuestas

## Decisiones Canonicas v1 (2026-02-15)

> **FUENTE DE VERDAD.** Todos los demas documentos (01-07) DEBEN alinearse con esta seccion.
> Si hay contradiccion entre un doc y esta seccion, ESTA SECCION GANA.

| # | Tema | Decision Final | Justificacion |
|---|------|---------------|---------------|
| DC-1 | Refresh token | UUID opaco, hash SHA-256 en Redis. TTL: 7d web, 30d movil. Rotacion siempre. Revocacion por familia | Mas simple que JWT, revocacion instantanea, no expone datos en cookie |
| DC-2 | Hashing passwords | Argon2id (time=3, memory=64MB, parallelism=4). bcrypt solo como fallback para passwords migrados | Resistente a GPU y side-channel |
| DC-3 | Workers/cola | Celery + Redis (NO ARQ) | Ecosistema maduro, Flower para monitoreo, compatible con beat scheduler |
| DC-4 | RFC | VARCHAR(13). Validar: 12 (moral) o 13 (fisica) chars, uppercase, alfanumerico, sin guiones | Formato fiscal mexicano estandar |
| DC-5 | XSS Header | `X-XSS-Protection: 0` + CSP robusto | El header XSS esta deprecated, CSP es el estandar moderno |
| DC-6 | Rate limiting login | 5 intentos/usuario + 10/IP en 15 min. Bloqueo cuenta: 10 intentos -> 30 min. Alerta Telegram: 5 fallidos | Defensa en capas |
| DC-7 | Namespace endpoints autorizacion | `/authorization/*` (payments, policies, requests) | Un solo namespace, sin fragmentacion |
| DC-8 | Cronograma | ~25-30 semanas (8 fases). Ver roadmap detallado en doc 01 seccion 6 | Estimacion realista con fases paralelas |
| DC-9 | Export clientes | PROHIBIDO exportar lista de clientes a CSV/Excel/PDF. Todas las demas tablas si pueden exportar | Datos sensibles, politica de seguridad |
| DC-10 | Empleados | Tabla unificada `employee` con flags (es_vendedor, es_cobrador, es_ajustador). NO tablas separadas | Multi-rol simultaneo, simplifica FK |

## Versiones y Documentacion

- **NUNCA usar versiones antiguas** de frameworks o librerias. Siempre usar las versiones mas recientes y estables
- **context7 MCP**: Cuando necesites contexto actualizado sobre una tecnologia (FastAPI, Next.js, SQLAlchemy, React Native, etc.), usa el MCP `context7` para consultar la documentacion vigente. No asumas APIs o patrones de versiones anteriores
- Antes de escribir codigo que dependa de una API especifica de un framework, verifica con context7 que la API sigue vigente en la version actual

## Plan Maestro y Estrategia de Coexistencia (2026-02-17)

> **FUENTE DE VERDAD para la estrategia**: `memory/PLAN_MAESTRO_MIGRACION.md` en el repo pqtcreacion

- **Desktop (pqtcreacion)** sigue corriendo con MySQL. NO se apaga.
- **nuevo-sistema** corre en VPS con PostgreSQL como backend para apps moviles
- **ETL gradual** sincroniza MySQL → PostgreSQL (primero solo datos del cobrador)
- **Pre-aprobacion de pagos**: cobrador captura en app → PostgreSQL → oficina aprueba en desktop → MySQL
- **Modulo nuevo**: `payment_preapproval` (tabla + 3 endpoints: POST crear, GET listar, PUT aprobar/rechazar)
- **Fases en Notion**: Fase 0-5 + Fase Desktop (integracion pre-aprobaciones en pqtcreacion)
- **Orden de ejecucion**: Fase 0 (infra) → Fase 1 (corregir schema) → Fase 5 (deploy API) → Fase 4 (ETL) → Fase Desktop → Fase 3 (App Cobrador)

### Planes de pago REALES (B9 corregido)
- **RC**: cash, cash_2_installments, monthly_7
- **AMPLIA / AMPLIA SELECT**: cash, cash_2_installments, quarterly_4, semiannual_2, monthly_12
- ENUM `payment_plan_type` debe tener los 6 valores
- Validacion por cobertura en el servicio

### Metodos de pago (B8 - PENDIENTE confirmacion)
- Esperando confirmacion del usuario con gerente de cobranza
- Candidatos: cash, deposit, transfer, tarjeta, crucero, konfio, terminal_banorte

## Tracking del Proyecto

- **Notion**: Base de datos "Checklist del Proyecto" dentro de "Nuevo Sistema CRM Seguros Protegrt"
- **Notion data source ID**: `3c423189-ff2c-4f9e-b554-1db4f8b6ee62`
- **Checklist local**: `05-CHECKLIST-PROYECTO.md` (para el inspector externo)
- **REGLA OBLIGATORIA**: Al trabajar en cualquier tarea, SIEMPRE actualizar **AMBOS** (Notion Y 05-CHECKLIST):
  - Iniciar tarea → Estado: EN PROCESO
  - Completar → Estado: TERMINADA
  - Bloqueada → Estado: BLOQUEADA (con nota del motivo)
  - Tarea nueva descubierta → Crearla en Notion Y en 05-CHECKLIST con fase, prioridad y responsable
  - NUNCA omitir la actualizacion de Notion NI del checklist
  - NUNCA dejar que Notion y 05-CHECKLIST se desincronicen
