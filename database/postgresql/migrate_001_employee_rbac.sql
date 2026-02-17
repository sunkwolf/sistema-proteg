-- =============================================================================
-- MIGRACION 001: Campos employee + is_field_worker + RBAC simplificado
-- Fecha: 2026-02-17
-- Ejecutar en: VPS PostgreSQL (protegrt_crm) via DBeaver o pgAdmin
-- =============================================================================
-- NOTA: La tabla employee en el VPS fue desplegada con first_name/paternal_surname/
-- maternal_surname, pero el modelo SQLAlchemy usa full_name. Esta migracion
-- corrige eso y agrega los campos nuevos.
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. CORREGIR employee: reemplazar first_name/paternal_surname/maternal_surname → full_name
-- =============================================================================

-- No hay datos, podemos simplemente DROP + ADD
ALTER TABLE public.employee DROP COLUMN IF EXISTS first_name;
ALTER TABLE public.employee DROP COLUMN IF EXISTS paternal_surname;
ALTER TABLE public.employee DROP COLUMN IF EXISTS maternal_surname;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS full_name character varying(255) NOT NULL DEFAULT '';

-- Quitar el default despues de agregar (solo era para el ALTER)
ALTER TABLE public.employee ALTER COLUMN full_name DROP DEFAULT;

-- =============================================================================
-- 2. AGREGAR campos que faltan en employee (telegram_id y sales_target no estan en VPS)
-- =============================================================================

ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS telegram_id bigint;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS sales_target integer;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS hire_date date;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS termination_date date;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS curp character varying(18);
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS rfc character varying(13);
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS emergency_contact text;
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS emergency_phone character varying(20);
ALTER TABLE public.employee ADD COLUMN IF NOT EXISTS photo_url text;

-- Comentarios
COMMENT ON COLUMN public.employee.telegram_id IS 'Telegram ID para notificaciones';
COMMENT ON COLUMN public.employee.hire_date IS 'Fecha de ingreso a la empresa';
COMMENT ON COLUMN public.employee.termination_date IS 'Fecha de baja';
COMMENT ON COLUMN public.employee.curp IS 'CURP del empleado (18 caracteres)';
COMMENT ON COLUMN public.employee.rfc IS 'RFC del empleado (12 moral, 13 fisica)';
COMMENT ON COLUMN public.employee.emergency_contact IS 'Nombre del contacto de emergencia';
COMMENT ON COLUMN public.employee.emergency_phone IS 'Telefono del contacto de emergencia';
COMMENT ON COLUMN public.employee.photo_url IS 'URL de la foto del empleado';

-- =============================================================================
-- 3. AGREGAR is_field_worker a employee_department
-- =============================================================================

ALTER TABLE public.employee_department
    ADD COLUMN IF NOT EXISTS is_field_worker boolean DEFAULT false NOT NULL;

COMMENT ON COLUMN public.employee_department.is_field_worker
    IS 'true=campo (cobrador/vendedor de calle), false=oficina. Para gestion de vacaciones';

-- =============================================================================
-- 4. LIMPIAR roles y permisos viejos (si existen)
-- =============================================================================

-- Borrar mappings primero (FK), luego permisos y roles
DELETE FROM public.role_permission;
DELETE FROM public.permission;
DELETE FROM public.role;
DELETE FROM public.department;

-- =============================================================================
-- 5. INSERTAR 4 departamentos
-- =============================================================================

INSERT INTO public.department (name, description) VALUES
    ('Administracion', 'Administracion general, RH, gestion del sistema'),
    ('Ventas', 'Venta de polizas y renovaciones'),
    ('Cobranza', 'Cobranza, recaudacion, tarjetas y recibos'),
    ('Siniestros', 'Atencion de siniestros, gruas y ajuste');

-- =============================================================================
-- 6. INSERTAR 4 roles
-- =============================================================================

INSERT INTO public.role (name, description) VALUES
    ('admin', 'Acceso total al sistema. Configuracion, usuarios, auditoria'),
    ('gerente', 'Gerente de departamento. Aprobaciones, reportes, supervision de personal'),
    ('oficina', 'Personal de oficina. Ve todo, captura datos, aprueba polizas'),
    ('campo', 'Personal de campo (app movil). Ve solo lo asignado, captura con aprobacion');

-- =============================================================================
-- 7. INSERTAR 13 permisos
-- =============================================================================

INSERT INTO public.permission (name, description) VALUES
    -- Admin-only (3)
    ('system.config', 'Configurar parametros del sistema y backups'),
    ('users.manage', 'Crear/editar usuarios, resetear passwords, asignar roles'),
    ('roles.manage', 'Crear/editar roles y asignar permisos'),
    -- Admin + Gerente (5)
    ('audit.view', 'Ver bitacora de auditoria del personal'),
    ('employees.manage', 'Alta, baja y edicion de empleados'),
    ('payments.approve', 'Aprobar pagos capturados (gerente de ventas aprueba)'),
    ('payments.modify', 'Modificar pagos existentes (solo depto Cobranza)'),
    ('cancellations.execute', 'Cancelar polizas C1-C5 (solo gerente Cobranza o admin)'),
    -- Admin + Gerente + Oficina (4)
    ('policies.approve', 'Aprobar polizas capturadas por vendedor de campo'),
    ('endorsements.approve', 'Aprobar endosos (solo depto Administracion)'),
    ('promotions.manage', 'Crear y editar promociones (solo depto Cobranza o superior)'),
    ('receipts.batch', 'Crear lotes de recibos y asignacion (solo personal Cobranza)'),
    -- Admin + Gerente only (1)
    ('cards.assign', 'Asignar tarjetas de cobro a cobradores (gerente Cobranza)');

-- =============================================================================
-- 8. INSERTAR role_permission mappings
-- =============================================================================

-- Admin: ALL 13
INSERT INTO public.role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM public.role r
CROSS JOIN public.permission p
WHERE r.name = 'admin';

-- Gerente: 10 permisos
INSERT INTO public.role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM public.role r
CROSS JOIN public.permission p
WHERE r.name = 'gerente'
  AND p.name IN (
    'audit.view', 'employees.manage',
    'payments.approve', 'payments.modify', 'cancellations.execute',
    'policies.approve', 'endorsements.approve', 'promotions.manage',
    'receipts.batch', 'cards.assign'
  );

-- Oficina: 4 permisos
INSERT INTO public.role_permission (role_id, permission_id)
SELECT r.id, p.id
FROM public.role r
CROSS JOIN public.permission p
WHERE r.name = 'oficina'
  AND p.name IN (
    'policies.approve', 'endorsements.approve',
    'promotions.manage', 'receipts.batch'
  );

-- Campo: 0 permisos (no inserts needed)

-- =============================================================================
-- VERIFICACION
-- =============================================================================

DO $$
DECLARE
    dept_count integer;
    role_count integer;
    perm_count integer;
    mapping_count integer;
BEGIN
    SELECT count(*) INTO dept_count FROM public.department;
    SELECT count(*) INTO role_count FROM public.role;
    SELECT count(*) INTO perm_count FROM public.permission;
    SELECT count(*) INTO mapping_count FROM public.role_permission;

    RAISE NOTICE '=== Migracion 001 completada ===';
    RAISE NOTICE 'Departamentos: %', dept_count;
    RAISE NOTICE 'Roles: %', role_count;
    RAISE NOTICE 'Permisos: %', perm_count;
    RAISE NOTICE 'Mappings role_permission: %', mapping_count;

    -- Validaciones
    ASSERT dept_count = 4, 'Esperados 4 departamentos, encontrados ' || dept_count;
    ASSERT role_count = 4, 'Esperados 4 roles, encontrados ' || role_count;
    ASSERT perm_count = 13, 'Esperados 13 permisos, encontrados ' || perm_count;
    ASSERT mapping_count = 27, 'Esperados 27 mappings (13+10+4+0), encontrados ' || mapping_count;
END $$;

COMMIT;
