# 05 - Checklist del Proyecto: Nuevo CRM Protegrt

**Ultima actualizacion:** 2026-02-15

---

## CONTEXTO: DOS SISTEMAS EN PARALELO

Este proyecto involucra **dos codebases separadas** que coexisten durante el desarrollo:

### Sistema Actual (MySQL) — Repo: `D:\pqtcreacion` (rama `claude`)
- Aplicacion web actual en produccion (Python/Flask + MySQL + Jinja2)
- Se le hicieron mejoras: refactorizacion MVC, unificacion de empleados, correccion de bugs
- Los scripts de migracion de empleados (`database/migrations/`) viven aqui
- Este sistema seguira en produccion hasta que el nuevo este listo para el corte

### Sistema Nuevo (PostgreSQL) — Repo: `D:\Claude\crm\nuevo-sistema` (rama `develop`)
- Codebase completamente nueva: FastAPI + Next.js + React Native
- Schema PostgreSQL v2.1 (1639 lineas, 49 tablas, 31 ENUMs)
- **Nota sobre seller/collector**: La unificacion a tabla `employee` con flags (`es_vendedor`,
  `es_cobrador`, `es_ajustador`) ya fue implementada (tarea 1.6c). La migracion Alembic
  `6524ad295e93` elimino las tablas `seller` y `collector`, migrando datos y FKs a `employee`.
  La BD ahora tiene 48 tablas (49 originales - seller - collector + employee + employee_department
  + employee_permission_override = 48 + 2 nuevas = 50 modelos, 48 tablas en BD).

### Flujo de migracion planeado
1. Unificar empleados en MySQL actual (tarea 1.1, la hace el usuario)
2. Verificar que el sistema actual funciona con empleados unificados (tarea 1.2)
3. Construir el nuevo sistema completo sobre PostgreSQL (Fase 1-3)
4. Migrar datos MySQL → PostgreSQL con scripts automatizados (Fase 4)
5. Desplegar nuevo sistema y hacer corte (Fase 5)

---

## REPOSITORIO Y TRACKING

- **Repo GitHub**: https://github.com/sunkwolf/sistema-proteg.git
- **Branches**: `main` (estable) / `develop` (desarrollo activo)
- **Tracking primario**: Notion (base de datos "Checklist del Proyecto")
- **Tracking secundario**: Este documento (para revisiones externas)
- **Docker**: `docker/docker-compose.yml` (dev) + `docker-compose.prod.yml` (prod)
  - Dev: puertos expuestos, sin auth en Redis/PG (solo local)
  - Prod: puertos cerrados, passwords por env vars, Redis con requirepass

---

## FASE 0: PREPARACION DE INFRAESTRUCTURA

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 0.1 | ~~Contratar VPS principal (EasyPanel)~~ | TERMINADA | Usuario | Ya tiene EasyPanel corriendo |
| 0.2 | Contratar VPS secundario (backups) | PENDIENTE | Usuario | Min 2 CPU, 2GB RAM, 200GB HDD. Solo para pgBackRest. No bloquea Fase 1 |
| 0.3 | ~~Instalar EasyPanel en VPS principal~~ | TERMINADA | Usuario | Ya instalado |
| 0.4 | ~~Registrar dominio~~ | TERMINADA | Usuario | Ya tiene dominio |
| 0.5 | Configurar DNS (subdominio api. y app.) | PENDIENTE | Usuario | No bloquea desarrollo. Se necesita para Fase 5 (deploy) |
| 0.6 | ~~Crear repositorio GitHub~~ | TERMINADA | Claude | https://github.com/sunkwolf/sistema-proteg.git |
| 0.7 | Configurar WireGuard VPN en VPS | PENDIENTE | Claude + Usuario | No bloquea desarrollo. Se necesita para Fase 5 |
| 0.8 | ~~Instalar Evolution API para WhatsApp~~ | TERMINADA | Usuario | Ya la tiene corriendo |
| 0.9 | ~~Crear proyecto FastAPI (estructura)~~ | TERMINADA | Claude | 148+ archivos, 21 modulos, monolito modular |
| 0.10 | ~~Docker Compose dev + prod~~ | TERMINADA | Claude | PG 16 + PgBouncer + Redis. Dev y prod separados |
| 0.11 | ~~Schema PostgreSQL v2.1~~ | TERMINADA | Claude | 1639 lineas, 49 tablas, 31 ENUMs, correcciones B8-B12 |
| 0.12 | ~~Git init + push a GitHub~~ | TERMINADA | Claude | Branches main + develop creados y pusheados |
| 0.13 | ~~Alembic config + baseline~~ | TERMINADA | Claude | Revision 1a3018309e6e. Schema cargado via DDL |
| 0.14 | ~~Docker levantado y verificado~~ | TERMINADA | Claude | PG:5433, PgBouncer:6432, Redis:6379 |

## FASE 1: BASE DE DATOS Y BACKEND CORE

### Commits realizados en develop:
1. `178324b` — Commit inicial: estructura del proyecto CRM Protegrt
2. `2ebaec3` — feat: agregar modelos SQLAlchemy para las 49 tablas del schema v2.1
3. `f3b9977` — feat: implementar autenticacion JWT RS256 completa
4. `e3542b7` — fix: corregir 3 bugs detectados en code review
5. `4839909` — feat: seed RBAC - 5 departamentos, 7 roles, 75 permisos granulares
6. `57ebce1` — feat: unificar seller/collector en tabla employee unificada
7. `df73991` — feat: modulo empleados CRUD + migracion tablas audit
8. `ed6f672` — fix: correcciones code review + modulo clientes CRUD
9. `3079aa2` — docs: actualizar checklist con tareas 1.7 y 1.8a terminadas
10. `5a13939` — feat: modulos vehiculos y coberturas CRUD completos
11. `4fed4dc` — feat: modulo polizas CRUD con generacion automatica de pagos
12. `7b166a0` — feat: modulo pagos CRUD + abonos parciales + revertir
13. `adb4ac7` — feat: modulo autorizacion - propuestas de pago + aprobaciones genericas
14. `91ce232` — feat: modulo recibos CRUD + memoria inspector
15. `3f117b5` — feat: modulo tarjetas/cobranza CRUD + avisos de visita
16. `d8a8fb1` — feat: modulo cancelaciones C1-C5 + reactivacion
17. `e731d64` — feat: modulo renovaciones - deteccion, CRUD, completar/rechazar
18. `082c602` — feat: modulo siniestros CRUD + pases medicos/taller + encuesta + guardias
19. `578fa61` — feat: modulo gruas CRUD + proveedores + encuesta satisfaccion
20. `5155a68` — feat: modulo endosos CRUD + aprobar/rechazar/aplicar + calculo costo
21. `44df845` — feat: modulo promociones CRUD + reglas + aplicar/simular descuentos
22. `355717b` — feat: modulo cotizaciones - proxy API externa validate/approve
23. `f512074` — feat: modulo notificaciones WhatsApp + Telegram + historial + stats
24. `30ac5bc` — feat: modulo reportes Excel (7 endpoints)
25. `4d71167` — fix: corregir 9 bugs encontrados por code review
26. `00a5216` — feat: modulo dashboard (general, ventas, cobranza, siniestros)

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 1.1 | Ejecutar migracion de empleados en MySQL actual | PENDIENTE | Usuario | 4 scripts en `D:\pqtcreacion\database\migrations\`. No bloquea Fase 1 del nuevo sistema |
| 1.2 | Verificar que la app actual funciona con empleados unificados | PENDIENTE | Usuario | Probar login, polizas, cobranza, siniestros en sistema actual |
| 1.3 | ~~Disenar schema PostgreSQL final (DDL corregido)~~ | TERMINADA | Claude | v2.1 con 49 tablas, 31 ENUMs, correcciones B8-B12 aplicadas |
| 1.4 | ~~Crear proyecto FastAPI (estructura de carpetas)~~ | TERMINADA | Claude | Monolito modular con 21 modulos |
| 1.4b | ~~Configurar Alembic + primera migracion~~ | TERMINADA | Claude | Baseline stamp sobre DDL existente |
| 1.4c | ~~Modelos SQLAlchemy para 49 tablas~~ | TERMINADA | Claude | Validados: 49 tablas coinciden con schema.sql |
| 1.5a | ~~Implementar JWT RS256 (access + refresh tokens)~~ | TERMINADA | Claude | RSA 2048-bit, access 15min, refresh UUID opaco con rotacion |
| 1.5b | ~~Implementar endpoints login/refresh/logout~~ | TERMINADA | Claude | POST /login, POST /refresh, POST /logout, GET /me |
| 1.5c | ~~Implementar rate limiting en login~~ | TERMINADA | Claude | 5/usuario, 10/IP en 15min. Lockout a 10 intentos por 30min |
| 1.5d | Implementar 2FA (TOTP) | PENDIENTE | Claude | pyotp. Puede hacerse despues del MVP |
| 1.6a | ~~Definir roles y permisos granulares en BD~~ | TERMINADA | Claude | 5 deptos, 7 roles, 75 permisos, 170 mappings. Script idempotente |
| 1.6b | ~~Implementar middleware require_permission~~ | TERMINADA | Claude | Factory en dependencies.py que consulta role_permission en BD |
| 1.6c | ~~Implementar multi-rol y override de permisos~~ | TERMINADA | Claude | Tabla employee unificada, migracion Alembic, permission overrides en dependencies.py |
| 1.7 | ~~Implementar modulo empleados (CRUD unificado)~~ | TERMINADA | Claude | 13 endpoints, schemas+repo+service+router. Departments M:N, permission overrides |
| 1.8a | ~~Implementar modulo clientes - CRUD basico~~ | TERMINADA | Claude | 5 endpoints, soft-delete, PostGIS, validacion RFC. Sin export |
| 1.8b | Implementar busqueda de clientes con pg_trgm | PENDIENTE | Claude | Extension pg_trgm para busqueda por similitud |
| 1.8c | Implementar PostGIS para direcciones de clientes | PENDIENTE | Claude | GeoAlchemy2. Busqueda por cercania |
| 1.8d | Implementar verificacion WhatsApp de clientes | PENDIENTE | Claude | Via Evolution API. No obligatorio |
| 1.9 | ~~Implementar modulo vehiculos~~ | TERMINADA | Claude | 6 endpoints: CRUD + busqueda por serie/placas. Validacion claves 101-109, mapeo tipo, cilindraje motos |
| 1.10 | ~~Implementar modulo coberturas~~ | TERMINADA | Claude | 6 endpoints: CRUD + busqueda + esquemas de pago. AMPLIA solo 101/103/105, logica cilindraje motos |
| 1.11a | ~~Implementar modulo polizas - CRUD y calculo de pagos~~ | TERMINADA | Claude | 6 endpoints: CRUD + folio lookup + cambiar vendedor. Auto-genera pagos y tarjeta |
| 1.11b | Implementar maquina de estados de polizas | TERMINADA | Claude | StatusUpdater + update_single_policy_status on-demand. Commit 29 |
| 1.11c | Implementar pendiente de autorizacion de polizas | TERMINADA | Claude | ApprovalRequest auto al crear poliza, approve→active, reject→cancelled. Commit 30 |
| 1.12a | ~~Implementar modulo pagos - CRUD y edicion~~ | TERMINADA | Claude | 8 endpoints: CRUD + abono parcial + revertir + marcar problema. Validaciones fecha/delivery |
| 1.12b | Implementar maquina de estados de pagos | TERMINADA | Claude | StatusUpdater batch + recalculo on-demand en PaymentService. Commit 29 |
| 1.12c | Implementar contado a cuotas en pagos | TERMINADA | Claude | POST /payments/convert-to-installments. Commit 29 |
| 1.12d | ~~Implementar propuestas de pago (cobradores campo)~~ | TERMINADA | Claude | Cubierto por modulo autorizacion. Propuestas CRUD + aprobar/rechazar/cancelar |
| 1.13 | ~~Implementar panel de autorizacion unificado~~ | TERMINADA | Claude | 9 endpoints /authorization/*. Propuestas de pago + solicitudes genericas de aprobacion |
| 1.14a | ~~Implementar modulo recibos - batch y asignacion~~ | TERMINADA | Claude | 9 endpoints: batch, assign, verify, cancel, mark-lost, list, by-collector, by-number, by-id |
| 1.14b | ~~Implementar verificacion y estados de recibos~~ | TERMINADA | Claude | Maquina de estados completa + deteccion recibos saltados + loss schedule |
| 1.15 | ~~Implementar modulo tarjetas/cobranza~~ | TERMINADA | Claude | 8 endpoints: tarjetas CRUD + reasignar + historial + avisos de visita. PostGIS pendiente |
| 1.16 | ~~Implementar modulo cancelaciones~~ | TERMINADA | Claude | 5 endpoints: CRUD + undo (admin) + notify. Cascada a pagos/tarjeta. Codigos C1-C5 |
| 1.17 | ~~Implementar modulo renovaciones~~ | TERMINADA | Claude | 7 endpoints: list, pending, create, get, complete, reject, notifications. Deteccion polizas por vencer |
| 1.18 | ~~Implementar modulo siniestros~~ | TERMINADA | Claude | 13 endpoints: CRUD + pases medicos/taller + encuesta satisfaccion + guardias ajustadores |
| 1.19 | ~~Implementar modulo gruas~~ | TERMINADA | Claude | 9 endpoints: CRUD servicios + proveedores CRUD + encuesta satisfaccion |
| 1.20 | ~~Implementar modulo endosos~~ | TERMINADA | Claude | 8 endpoints: CRUD + aprobar/rechazar/aplicar + calculo costo. 5 tipos, JSONB change_details |
| 1.21 | ~~Implementar modulo promociones~~ | TERMINADA | Claude | 12 endpoints: CRUD promos + CRUD reglas + aplicar/simular + listar aplicaciones. 4 tipos descuento |
| 1.22 | ~~Implementar modulo cotizaciones (integracion)~~ | TERMINADA | Claude | 2 endpoints proxy: validate + approve. httpx a API externa. Sin JOINs |
| 1.23a | ~~Implementar modulo notificaciones - WhatsApp~~ | TERMINADA | Claude | Evolution API client + send-overdue + send-reminders. Queue pattern con SentMessage |
| 1.23b | ~~Implementar modulo notificaciones - Telegram~~ | TERMINADA | Claude | Bot API client para alertas. Integrado con modulo notificaciones |
| 1.24 | ~~Implementar modulo reportes~~ | TERMINADA | Claude | 7 endpoints Excel con openpyxl. SIN export de clientes. Commit `30ac5bc` |
| 1.25 | ~~Implementar modulo dashboard~~ | TERMINADA | Claude | 4 endpoints: general, ventas, cobranza, siniestros. KPIs, alertas, actividad |
| 1.26 | ~~Implementar modulo administracion~~ | TERMINADA | Claude | 9 endpoints: audit log, roles CRUD, permisos, departamentos, system info |
| 1.27 | Implementar StatusUpdater (job diario Celery) | TERMINADA | Claude | Core logic + Celery task + Beat scheduler + trigger manual POST /admin/status-update. Commit 28 |
| 1.28 | Implementar sistema de backup pgBackRest | PENDIENTE | Claude | Full semanal + diff diario + WAL continuo |
| 1.29 | Tests unitarios e integracion backend | PENDIENTE | Claude | pytest + httpx async + factory_boy |

### Bugs corregidos por code review (2026-02-15):
- **Anti-bruteforce**: Lockout a 10 intentos era inalcanzable porque rate-limit cortaba a 5 sin incrementar contador. Corregido: ahora son checks independientes.
- **Permisos duplicados**: Existia un `permissions.py` stub viejo ademas del `dependencies.py` real. Eliminado el duplicado.
- **Alembic env.py**: No importaba `app.models`, asi que autogenerate no descubria los 49 modelos. Corregido.

## FASE 2: FRONTEND WEB

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 2.1 | Crear proyecto Next.js 14 + TypeScript + shadcn/ui | PENDIENTE | Claude | Estructura de carpetas, tema, layouts |
| 2.2 | Implementar login + auth context | PENDIENTE | Claude | JWT en memoria, refresh via cookie, sin remember me |
| 2.3 | Implementar layout principal + sidebar + navegacion | PENDIENTE | Claude | Sidebar con modulos segun permisos del usuario |
| 2.4 | Implementar dashboard principal | PENDIENTE | Claude | Widgets por departamento |
| 2.5 | Implementar modulo clientes (frontend) | PENDIENTE | Claude | Tabla, busqueda, formulario, sin export |
| 2.6 | Implementar modulo polizas (frontend) | PENDIENTE | Claude | Formulario wizard, vehiculo, coberturas |
| 2.7 | Implementar modulo pagos (frontend) | PENDIENTE | Claude | Edicion, abonos, contado a cuotas |
| 2.8 | Implementar panel de autorizacion (frontend) | PENDIENTE | Claude | Pagos + polizas pendientes |
| 2.9 | Implementar modulo recibos (frontend) | PENDIENTE | Claude | Batch, asignacion, verificacion |
| 2.10 | Implementar modulo tarjetas/cobranza (frontend) | PENDIENTE | Claude | 3 propuestas de diseno pendientes de decision |
| 2.11 | Implementar modulo empleados (frontend) | PENDIENTE | Claude | Formulario con 4 tabs |
| 2.12 | Implementar modulo cancelaciones (frontend) | PENDIENTE | Claude | |
| 2.13 | Implementar modulo renovaciones (frontend) | PENDIENTE | Claude | |
| 2.14 | Implementar modulo siniestros (frontend) | PENDIENTE | Claude | |
| 2.15 | Implementar modulo gruas (frontend) | PENDIENTE | Claude | |
| 2.16 | Implementar modulo endosos (frontend) | PENDIENTE | Claude | |
| 2.17 | Implementar modulo reportes (frontend) | PENDIENTE | Claude | |
| 2.18 | Implementar modulo administracion (frontend) | PENDIENTE | Claude | |
| 2.19 | Tests frontend | PENDIENTE | Claude | Vitest + Testing Library |

## FASE 3: APPS MOVILES

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 3.1 | Crear proyecto React Native + Expo | PENDIENTE | Claude | Monorepo o 3 apps separadas? Decidir |
| 3.2 | App Cobrador: login + ruta del dia | PENDIENTE | Claude | GPS tracking, pagos pendientes |
| 3.3 | App Cobrador: registrar cobro (propuesta) | PENDIENTE | Claude | Foto evidencia, geolocalizacion |
| 3.4 | App Cobrador: recibos asignados | PENDIENTE | Claude | Ver, usar, reportar extravio |
| 3.5 | App Cobrador: depositos pendientes | PENDIENTE | Claude | Dinero recaudado, alertas de deposito |
| 3.6 | App Vendedor: crear poliza | PENDIENTE | Claude | Formulario simplificado |
| 3.7 | App Vendedor: cotizar | PENDIENTE | Claude | Integracion con cotizaciones |
| 3.8 | App Vendedor: mis polizas + renovaciones | PENDIENTE | Claude | |
| 3.9 | App Ajustador: siniestros asignados | PENDIENTE | Claude | |
| 3.10 | App Ajustador: servicios de grua | PENDIENTE | Claude | |
| 3.11 | App Ajustador: guardia del dia | PENDIENTE | Claude | |
| 3.12 | Tests apps moviles | PENDIENTE | Claude | |

## FASE 4: MIGRACION DE DATOS

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 4.1 | Desarrollar scripts de migracion MySQL → PostgreSQL | PENDIENTE | Claude | 9 fases segun doc 04 |
| 4.2 | Ejecutar migracion en entorno de prueba | PENDIENTE | Claude + Usuario | Verificar integridad |
| 4.3 | Validar datos migrados (queries de verificacion) | PENDIENTE | Usuario | Claude da las queries |
| 4.4 | Ejecutar migracion en produccion | PENDIENTE | Usuario | Ventana de mantenimiento |
| 4.5 | Verificar sistema nuevo con datos reales | PENDIENTE | Usuario | |

## FASE 5: DESPLIEGUE Y CORTE

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 5.1 | Desplegar backend en EasyPanel (Docker) | PENDIENTE | Claude + Usuario | Claude genera Dockerfile y configs |
| 5.2 | Desplegar frontend en EasyPanel | PENDIENTE | Claude + Usuario | |
| 5.3 | Configurar SSL/TLS (Let's Encrypt) | PENDIENTE | EasyPanel | Automatico en EasyPanel |
| 5.4 | Configurar backup automatico pgBackRest | PENDIENTE | Claude + Usuario | |
| 5.5 | Pruebas de usuario final (UAT) | PENDIENTE | Usuario + equipo | 1-2 semanas |
| 5.6 | Corte: apagar sistema viejo, activar nuevo | PENDIENTE | Usuario | Fin de semana preferiblemente |
| 5.7 | Publicar apps moviles (APK/TestFlight) | PENDIENTE | Usuario | Claude genera builds |

## TRABAJO YA REALIZADO (pre-proyecto)

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| P.1 | Crear CLAUDE.md del proyecto | TERMINADA | Documentacion para Claude Code |
| P.2 | Documentar logica de negocio completa (26 modulos) | TERMINADA | docs/INFORME_LOGICA_NEGOCIO.md |
| P.3 | Analizar MySQL actual (45+ tablas) | TERMINADA | docs/INFORME_ANALISIS_MYSQL.md |
| P.4 | Disenar schema PostgreSQL v1 (42 tablas) | TERMINADA | database/postgresql/schema.sql |
| P.5 | Documentar hallazgos de optimizacion (45 findings) | TERMINADA | docs/INFORME_OPTIMIZACION.md |
| P.6 | Refactorizar codigo actual (55+ archivos) | TERMINADA | Separacion View→Controller→Service→DAO |
| P.7 | Planear arquitectura nuevo sistema | TERMINADA | nuevo-sistema/01-ARQUITECTURA.md |
| P.8 | Planear vistas y pantallas (25+5+3 apps) | TERMINADA | nuevo-sistema/02-VISTAS-Y-PANTALLAS.md |
| P.9 | Planear API REST (189 endpoints, 24 modulos) | TERMINADA | nuevo-sistema/03-API-Y-LOGICA.md |
| P.10 | Planear seguridad, despliegue, migracion | TERMINADA | nuevo-sistema/04-SEGURIDAD-DESPLIEGUE-MIGRACION.md |
| P.11 | Traer unificacion de empleados a rama claude | TERMINADA | Model, DAO, Service, Controller, View, Form, Migrations |
| P.12 | Corregir bugs del sistema actual | TERMINADA | Indentation, SyntaxWarning, vehicle keys, fotos |
| P.13 | Incorporar feedback del usuario en docs 01-04 | TERMINADA | Roles, multi-rol, VPN, empleados, etc. |

---

## DECISIONES PENDIENTES

| # | Decision | Opciones | Notas |
|---|----------|----------|-------|
| D.1 | Diseno de tarjetas/cobranza | 3 propuestas en doc 02 | Elegir una antes de Fase 2.10 |
| D.2 | Apps moviles: monorepo o separadas | Monorepo (shared code) vs 3 repos | Decidir antes de Fase 3 |
| D.3 | ~~Prioridad de apps moviles~~ | **App Cobrador primero** | DECIDIDO |
| D.4 | ~~Dominio del sistema~~ | Ya tiene dominio | DECIDIDO |
| D.5 | ~~Proveedor VPS~~ | Ya tiene VPS con EasyPanel | DECIDIDO |

---

## NOTAS PARA EL REVIEWER

### Arquitectura de seguridad (auth)
- **JWT RS256**: Clave privada firma tokens (15 min), clave publica verifica. Keys en `backend/keys/` (gitignored)
- **Refresh token**: UUID opaco, hash SHA-256 en Redis. Rotacion obligatoria. Revocacion por familia
- **Cookie**: httpOnly + Secure + SameSite=Strict, scoped a `/api/v1/auth`
- **Rate limiting**: 5 intentos/usuario + 10/IP en 15 min (ventana). Lockout: 10 intentos → 30 min bloqueo
- **Passwords**: Argon2id (time=3, mem=64MB). bcrypt como fallback para passwords migrados con auto-rehash
- **Permisos**: `require_permission("modulo.accion")` como Depends() en cada endpoint. Consulta tabla `role_permission` en BD

### Separacion dev/prod (Docker)
- `docker-compose.yml`: Solo para desarrollo local. Redis sin auth, puertos expuestos. NUNCA usar en VPS
- `docker-compose.prod.yml`: Redis con requirepass, puertos cerrados, passwords por env vars. Para EasyPanel
- CSP header se agregara cuando el frontend se integre (irrelevante para API pura)

### Sobre el schema employee (unificado)
Las tablas `seller` y `collector` fueron eliminadas y reemplazadas por `employee` (con flags `es_vendedor`,
`es_cobrador`, `es_ajustador`) + `employee_department` (M:N con `es_gerente` per-depto) + `employee_permission_override`.
La migracion Alembic `6524ad295e93` se encargo de migrar datos y actualizar los 8 FKs en 6 tablas.
El sistema de permisos en `dependencies.py` resuelve: overrides > role_permissions.
