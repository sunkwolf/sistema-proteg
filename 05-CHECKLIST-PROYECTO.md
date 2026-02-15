# 05 - Checklist del Proyecto: Nuevo CRM Protegrt

**Ultima actualizacion:** 2026-02-14

---

## FASE 0: PREPARACION DE INFRAESTRUCTURA

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 0.1 | ~~Contratar VPS principal (EasyPanel)~~ | TERMINADA | Usuario | Ya tiene EasyPanel corriendo |
| 0.2 | Contratar VPS secundario (backups) | PENDIENTE | Usuario | Min 2 CPU, 2GB RAM, 200GB HDD. Solo para pgBackRest |
| 0.3 | ~~Instalar EasyPanel en VPS principal~~ | TERMINADA | Usuario | Ya instalado |
| 0.4 | ~~Registrar dominio~~ | TERMINADA | Usuario | Ya tiene dominio |
| 0.5 | Configurar DNS (subdominio api. y app.) | PENDIENTE | Usuario | A record: api.dominio.com, app.dominio.com → IP del VPS |
| 0.6 | Crear repositorio GitHub para nuevo proyecto | PENDIENTE | Usuario | Claude da instrucciones |
| 0.7 | Configurar WireGuard VPN en VPS | PENDIENTE | Claude + Usuario | Claude genera configs, usuario las aplica |
| 0.8 | ~~Instalar Evolution API para WhatsApp~~ | TERMINADA | Usuario | Ya la tiene corriendo |

## FASE 1: BASE DE DATOS Y BACKEND CORE

| # | Tarea | Estado | Responsable | Notas |
|---|-------|--------|-------------|-------|
| 1.1 | Ejecutar migracion de empleados en MySQL actual | PENDIENTE | Usuario | 4 scripts en database/migrations/ + guia |
| 1.2 | Verificar que la app actual funciona con empleados unificados | PENDIENTE | Usuario | Probar login, polizas, cobranza, siniestros |
| 1.3 | Disenar schema PostgreSQL final (DDL corregido) | PENDIENTE | Claude | Corregir: payment_method_type, payment_plan_type, prima_total, rfc, receipt_limit |
| 1.4 | Crear proyecto FastAPI (estructura de carpetas) | PENDIENTE | Claude | Monolito modular con 14 modulos |
| 1.5 | Implementar modulo de auth (JWT RS256) | PENDIENTE | Claude | Login, refresh, logout, 2FA, rate limiting |
| 1.6 | Implementar RBAC + permisos + middleware | PENDIENTE | Claude | Roles, permisos por modulo, overrides individuales |
| 1.7 | Implementar modulo empleados (CRUD unificado) | PENDIENTE | Claude | Multi-departamento, permission overrides |
| 1.8 | Implementar modulo clientes | PENDIENTE | Claude | CRUD + busqueda pg_trgm + PostGIS + verificacion WhatsApp |
| 1.9 | Implementar modulo vehiculos | PENDIENTE | Claude | CRUD + claves de vehiculo (101-109) |
| 1.10 | Implementar modulo coberturas | PENDIENTE | Claude | Tabla de precios RC + AMPLIA individual |
| 1.11 | Implementar modulo polizas | PENDIENTE | Claude | CRUD + StatusUpdater + pendiente de autorizacion |
| 1.12 | Implementar modulo pagos | PENDIENTE | Claude | CRUD + maquina de estados + contado a cuotas |
| 1.13 | Implementar panel de autorizacion | PENDIENTE | Claude | Unificado: propuestas de pago + polizas pendientes |
| 1.14 | Implementar modulo recibos | PENDIENTE | Claude | Batch, asignar, verificar, maquina de estados |
| 1.15 | Implementar modulo tarjetas/cobranza | PENDIENTE | Claude | Tarjetas, movimientos, asignacion |
| 1.16 | Implementar modulo cancelaciones | PENDIENTE | Claude | C1-C5 + reactivacion |
| 1.17 | Implementar modulo renovaciones | PENDIENTE | Claude | Deteccion, notificacion, seguimiento |
| 1.18 | Implementar modulo siniestros | PENDIENTE | Claude | Vinculado a poliza, no solo a cliente |
| 1.19 | Implementar modulo gruas | PENDIENTE | Claude | Vinculado a poliza |
| 1.20 | Implementar modulo endosos | PENDIENTE | Claude | 5 tipos + calculo de costo automatico + WhatsApp |
| 1.21 | Implementar modulo promociones | PENDIENTE | Claude | 4 tipos: %, fijo, meses gratis, $0 enganche |
| 1.22 | Implementar modulo cotizaciones (integracion) | PENDIENTE | Claude | Solo referencia externa, sin JOINs |
| 1.23 | Implementar modulo notificaciones | PENDIENTE | Claude | WhatsApp (Evolution API) + Telegram |
| 1.24 | Implementar modulo reportes | PENDIENTE | Claude | Excel via openpyxl, sin export de clientes |
| 1.25 | Implementar modulo dashboard | PENDIENTE | Claude | Dashboard por departamento + principal |
| 1.26 | Implementar modulo administracion | PENDIENTE | Claude | Empleados, roles, permisos, config, audit log |
| 1.27 | Implementar StatusUpdater (job diario) | PENDIENTE | Claude | Celery + Redis, corre a medianoche |
| 1.28 | Implementar sistema de backup pgBackRest | PENDIENTE | Claude | Full semanal + diff diario + WAL continuo al VPS 2 |
| 1.29 | Tests unitarios y de integracion backend | PENDIENTE | Claude | pytest + httpx async |

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

## TRABAJO YA REALIZADO

| # | Tarea | Estado | Notas |
|---|-------|--------|-------|
| P.1 | Crear CLAUDE.md del proyecto | TERMINADA | Documentacion para Claude Code |
| P.2 | Documentar logica de negocio completa (26 modulos) | TERMINADA | docs/INFORME_LOGICA_NEGOCIO.md |
| P.3 | Analizar MySQL actual (45+ tablas) | TERMINADA | docs/INFORME_ANALISIS_MYSQL.md |
| P.4 | Disenar schema PostgreSQL v1 (42 tablas) | TERMINADA | database/postgresql/schema.sql (tiene errores pendientes) |
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
