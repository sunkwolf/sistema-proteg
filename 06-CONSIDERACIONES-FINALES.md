# 06 - Consideraciones Finales

**Proyecto:** Nuevo CRM Protegrt
**Fecha:** 2026-02-14

---

## 1. ERRORES CONOCIDOS EN EL SCHEMA POSTGRESQL

El schema en `database/postgresql/schema.sql` tiene 5 errores que deben corregirse antes de usarlo:

| # | Error | Correccion |
|---|-------|-----------|
| B8 | `payment_method_type` ENUM tiene `cash, transfer, card, check` | Debe ser: `cash, deposit, transfer, crucero, konfio, terminal_banorte` |
| B9 | `payment_plan_type` tiene `monthly_12` | Debe ser `monthly_7` (las polizas son de 7 pagos, no 12) |
| B10 | Tabla `policy` no tiene campo `prima_total` | Agregar `prima_total NUMERIC(12,2)` — es el costo total de la poliza |
| B11 | Tabla `client` no tiene campo `rfc` | Agregar `rfc VARCHAR(13)` — identificacion fiscal |
| B12 | `collector.receipt_limit` default es 5 | Debe ser 50 (default real en produccion) |

## 2. DIFERENCIAS CLAVE ENTRE SISTEMA ACTUAL Y NUEVO

| Aspecto | Sistema Actual | Sistema Nuevo |
|---------|---------------|---------------|
| Arquitectura | Desktop (PyQt5) en LAN | Web (Next.js) + Apps moviles (React Native) |
| Base de datos | MySQL/MariaDB (mal disenada) | PostgreSQL + PostGIS |
| Acceso | Solo en oficina via LAN | Internet con VPN/geofencing |
| Empleados | 4 tablas separadas | 1 tabla unificada con flags |
| Recibos | Fisicos (papel) | Digitales (WhatsApp) + fisicos en transicion |
| Cobranza | Manual, sin GPS | GPS tracking, rutas inteligentes |
| Notificaciones | Telegram | WhatsApp (Evolution API) + Telegram |
| Reportes | Excel via openpyxl local | Excel generado por API, sin export de clientes |
| Autorizaciones | Flujo informal | Panel unificado: pagos + polizas pendientes |
| Promociones | Hardcoded "mayo" | Flexible: 4 tipos, reglas JSONB, fechas configurables |
| Backups | Ninguno automatizado | pgBackRest a otro VPS (full semanal + diff diario + WAL) |

## 3. COSAS QUE NO SE MIGRAN

- **Cotizaciones**: Se quedan en su sistema separado. Solo se guarda `quote_external_id` como referencia
- **Tabla `recibos` vieja**: Reemplazada por `recibos_new` hace tiempo
- **Tabla `vdia`**: Obsoleta, no se usa en codigo
- **Historial de sesiones antiguas**: Se puede migrar parcialmente si se quiere, pero no es critico
- **Promocion de mayo hardcoded**: Se reemplaza por sistema flexible de promociones

## 4. ORDEN RECOMENDADO DE DESARROLLO

Estimaciones realistas alineadas con el roadmap detallado en doc 01:

```
Fase 0 (Infraestructura)              → 2-3 semanas
Fase 1 (Auth + Clientes + Polizas)    → 4-6 semanas
Fase 2 (Pagos + Recibos + Autorizacion) → 4-6 semanas
Fase 3 (Cobranza + App Cobradores)    → 4-6 semanas
Fase 4 (Siniestros + Gruas + Endosos) → 4-6 semanas (paralelo con Fase 3)
Fase 5 (Notificaciones + Mensajeria)  → 3-4 semanas
Fase 6 (App Vendedores + Renovaciones) → 3-4 semanas
Fase 7 (App Ajustadores)              → 2-3 semanas
Fase 8 (Migracion + Go-Live)          → 2-3 semanas
Total estimado: ~25-30 semanas
```

**Modulos que se pueden desarrollar en paralelo:**
- Backend + Frontend del mismo modulo (cuando la API esta lista, empezar el frontend)
- Apps moviles se pueden empezar cuando la API de auth y los endpoints necesarios esten listos
- El sistema actual sigue funcionando mientras se construye el nuevo

## 5. RIESGOS Y MITIGACIONES

| Riesgo | Impacto | Mitigacion |
|--------|---------|-----------|
| Datos corruptos en migracion | Alto | Backup antes, queries de verificacion, entorno de prueba |
| Perdida de datos por falta de backup | Critico | pgBackRest configurado desde dia 1 |
| Usuarios no adoptan nuevo sistema | Medio | Capacitacion, periodo de transicion con ambos sistemas |
| WhatsApp API bloqueada | Medio | Fallback a Telegram existente |
| VPS caido | Alto | Monitoreo con UptimeRobot, backup en VPS 2 puede restaurar |
| Contexto de Claude se compacta | Medio | Documentacion exhaustiva en CLAUDE.md y estos docs |

## 6. SOBRE AMPLIA SELECT

Recordatorio critico para el desarrollo:
- AMPLIA SELECT solo es elegible para claves de vehiculo 101 (AUTOMOVIL), 103 (PICK UP) y 105 (CAMIONETA)
- AMPLIA se cotiza individualmente (precio 0.00 en tabla de coberturas)
- Las claves de vehiculo son: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA, 107=MOTOCICLETA, 108=MOTO TAXI, 109=CAMION
- La clave 102 no se usa actualmente

## 7. SOBRE LA UNIFICACION DE EMPLEADOS

La migracion de empleados (scripts 001-004 en `database/migrations/`) debe ejecutarse EN EL SISTEMA ACTUAL (MySQL) ANTES de iniciar la migracion a PostgreSQL. Esto asegura que cuando hagamos el gran salto MySQL→PostgreSQL, la tabla `empleados` ya este unificada y sea mas facil de mapear.

**Orden obligatorio:**
1. Backup completo de MySQL
2. Ejecutar 001_schema.sql (crea tablas nuevas)
3. Ejecutar 002_data.sql (migra datos, remapea FKs)
4. Verificar que la app actual funciona
5. Ejecutar 003_cleanup.sql (elimina tablas viejas)
6. Ejecutar 004_roles_permisos.sql (roles, departamentos, permisos)
7. Desplegar codigo con los archivos nuevos (empleado model/dao/service/controller/view)

## 8. FLUJO "PENDIENTE DE AUTORIZACION"

Este es un concepto CENTRAL del nuevo sistema que aplica a:
- **Polizas**: Una poliza nueva puede quedar en "pendiente de autorizacion" hasta que un gerente la apruebe
- **Pagos**: Un cobrador en campo registra un cobro como "propuesta" que debe ser aprobada por cobranza

Ambos flujos se unifican en un solo "Panel de Autorizacion" donde los gerentes ven todo lo pendiente.
