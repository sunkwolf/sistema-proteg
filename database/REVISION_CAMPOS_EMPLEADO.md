# Revision de Campos: Empleados y Roles — DECIDIDO

**Fecha de revision:** 2026-02-17
**Estado:** TODAS LAS DECISIONES TOMADAS

---

## RESUMEN DE DECISIONES

| # | Pregunta | Decision |
|---|----------|----------|
| 1 | Email en employee? | NO — usar el de app_user. Se recrean todos los accesos |
| 2 | Telegram ID? | SI — agregado a employee |
| 3 | Hire/termination date? | SI — agregados |
| 4 | Sales target? | SI — ya existia en modelo |
| 5 | Adjuster code? | NO — se usa code_name ("M1", "M7") |
| 6 | Campos personales? | SI: curp, rfc, emergency_contact, emergency_phone, photo_url |
| 7 | Departamentos adicionales? | NO — 4 deptos: Administracion (incluye RH), Ventas, Cobranza, Siniestros |
| 8 | Roles? | 4 roles: admin, gerente, oficina, campo (eliminados invitado y roles granulares) |
| 9 | Recepcionista? | Rol "oficina" en depto Administracion |
| 10 | Dueno? | Rol "admin". El dueno es el hermano del usuario |

## CAMPOS AGREGADOS A employee

| Campo | Tipo | Para que |
|-------|------|----------|
| telegram_id | BIGINT | Notificaciones Telegram |
| sales_target | INTEGER | Meta de polizas (vendedores) |
| hire_date | DATE | Fecha de ingreso |
| termination_date | DATE | Fecha de baja |
| curp | VARCHAR(18) | Tramites legales |
| rfc | VARCHAR(13) | Facturacion comisiones |
| emergency_contact | TEXT | Nombre contacto emergencia |
| emergency_phone | VARCHAR(20) | Telefono emergencia |
| photo_url | TEXT | Foto del empleado |

## CAMPO AGREGADO A employee_department

| Campo | Tipo | Para que |
|-------|------|----------|
| is_field_worker | BOOLEAN DEFAULT false | Distinguir campo vs oficina para gestion de vacaciones |

## ROLES Y PERMISOS (simplificado)

**Principio: "Todos ven, pocos editan"**

4 roles, 13 permisos. Todo lo NO listado como permiso es accesible para cualquier usuario.

### Roles
| Rol | Quien | Permisos especiales |
|-----|-------|---------------------|
| admin | Dueno + sistemas | 13/13 (todos) |
| gerente | Gerentes de departamento | 10/13 |
| oficina | Auxiliares de oficina | 4/13 |
| campo | App movil (vendedores, cobradores, ajustadores) | 0/13 |

### 13 Permisos
| # | Permiso | admin | gerente | oficina | Nota |
|---|---------|:-----:|:-------:|:-------:|------|
| 1 | system.config | x | | | |
| 2 | users.manage | x | | | |
| 3 | roles.manage | x | | | |
| 4 | audit.view | x | x | | Gerente ve las de su personal |
| 5 | employees.manage | x | x | | |
| 6 | payments.approve | x | x | | Gerente de ventas aprueba |
| 7 | payments.modify | x | x | | Solo depto Cobranza |
| 8 | cancellations.execute | x | x | | Solo gerente Cobranza |
| 9 | policies.approve | x | x | x | Auxiliar admin revisa y aprueba |
| 10 | endorsements.approve | x | x | x | Solo depto Administracion |
| 11 | promotions.manage | x | x | x | Solo depto Cobranza |
| 12 | receipts.batch | x | x | x | Solo personal Cobranza |
| 13 | cards.assign | x | x | | Gerente Cobranza asigna |

### Departamentos
| # | Departamento | Descripcion |
|---|-------------|-------------|
| 1 | Administracion | Admin general + RH |
| 2 | Ventas | Venta de polizas |
| 3 | Cobranza | Cobranza y recaudacion |
| 4 | Siniestros | Siniestros y gruas |

## ARCHIVOS MODIFICADOS

- `backend/app/models/business.py` — Employee + EmployeeDepartment
- `backend/app/scripts/seed_rbac.py` — Reescrito: 4 deptos, 4 roles, 13 permisos
- `database/postgresql/schema.sql` — DDL canonico actualizado
- `database/postgresql/deploy_vps.sql` — Script deploy actualizado
- `database/postgresql/migrate_001_employee_rbac.sql` — ALTER TABLE para VPS existente
