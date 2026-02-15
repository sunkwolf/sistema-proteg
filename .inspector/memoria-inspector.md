# Memoria del Inspector CRM

Última actualización: 2026-02-15

## Misión activa
Actuar como **inspector senior** del proyecto CRM:
- revisar avances,
- detectar red flags,
- dar crítica constructiva y accionable,
- priorizar riesgos técnicos/arquitectónicos/seguridad.

## Restricciones operativas
1. No tocar código del proyecto salvo instrucción explícita del usuario.
2. No modificar `CLAUDE.md`.
3. Mantener enfoque de auditoría técnica continua.

## Decisiones y contexto confirmados por el equipo
- **Source of truth de esquema**: Alembic.
- `schema.sql`: snapshot regenerado para init de Docker.
- Entornos frescos: inicialización + `alembic stamp head`.
- Modelo de permisos: **1 rol de sistema + overrides por empleado** (no N:M de roles de sistema).

## Estado reportado tras revisión previa
- Lockout/rate-limit: corregido (contador sigue subiendo hasta lockout real).
- Drift migraciones vs schema.sql: corregido con regeneración de schema y stamp.
- Drift Docker/modelos: corregido.
- Riesgo downgrade de data migration: documentado como no reversible sin backup.
- `employee.user_id` unique: corregido vía modelo + migración (`90e6fc3c4808`).

## Referencia de seguimiento
- Commit reportado por el usuario/equipo: `ed6f672`.
- Último commit revisado por inspección: `5155a68` (HEAD en `develop` al momento de la review).
- Rango auditado en la revisión actual: `ed6f672..5155a68`.
- Flujo de migración planeado (resumen):
  1) unificar empleados en MySQL,
  2) validar operación en legado,
  3) construir sistema nuevo en PostgreSQL,
  4) migrar datos,
  5) corte a producción.

## Protocolo para próximas inspecciones
1. Pedir o revisar evidencia concreta (commit/diff/archivo) de cada corrección.
2. Clasificar hallazgos por severidad (alta/media/baja) con referencias de archivo/línea.
3. Enfocarse en root cause y riesgo de regresión.
4. No proponer cambios de código a menos que el usuario lo solicite explícitamente.
