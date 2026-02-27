-- ============================================================================
-- Migration: 004_employee_restructure
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripción: Reestructura de empleados - tabla unificada con roles múltiples
-- 
-- Referencia: /17-REESTRUCTURA-EMPLEADOS.md
-- ============================================================================

-- ============================================================================
-- PASO 1: NUEVOS ENUMS
-- ============================================================================

CREATE TYPE department_type AS ENUM (
    'sales',        -- Ventas
    'collection',   -- Cobranza
    'claims',       -- Siniestros/Ajustadores
    'admin',        -- Administración
    'hr',           -- Recursos Humanos
    'management'    -- Dirección
);

CREATE TYPE role_level_type AS ENUM (
    'staff',        -- Personal operativo
    'manager',      -- Gerente de departamento
    'director'      -- Director
);

-- ============================================================================
-- PASO 2: TABLA EMPLOYEE (persona física)
-- ============================================================================

CREATE TABLE employee (
    id              SERIAL PRIMARY KEY,
    
    -- Datos personales
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    birth_date      DATE,
    gender          gender_type,
    
    -- Contacto
    phone           VARCHAR(20),
    phone_2         VARCHAR(20),
    email           VARCHAR(100),
    telegram_id     BIGINT,
    
    -- Documentos
    rfc             VARCHAR(13),
    curp            VARCHAR(18),
    
    -- Dirección
    address_id      BIGINT REFERENCES address(id),
    
    -- Datos laborales
    hire_date       DATE NOT NULL,
    termination_date DATE,
    status          entity_status_type NOT NULL DEFAULT 'active',
    
    -- Auditoría
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE employee IS 'Empleados de la empresa. Fuente única de verdad para RRHH.';
COMMENT ON COLUMN employee.telegram_id IS 'ID de Telegram del empleado (nivel persona, no rol).';
COMMENT ON COLUMN employee.hire_date IS 'Fecha de contratación. Usado para calcular antigüedad y vacaciones.';

CREATE INDEX idx_employee_status ON employee(status);
CREATE INDEX idx_employee_telegram ON employee(telegram_id) WHERE telegram_id IS NOT NULL;
CREATE INDEX idx_employee_name ON employee(last_name, first_name);

-- Trigger de updated_at
CREATE TRIGGER trg_employee_updated_at
    BEFORE UPDATE ON employee
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

-- ============================================================================
-- PASO 3: TABLA EMPLOYEE_ROLE (roles del empleado)
-- ============================================================================

CREATE TABLE employee_role (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    
    -- Rol
    department      department_type NOT NULL,
    level           role_level_type NOT NULL DEFAULT 'staff',
    
    -- Vigencia
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    start_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date        DATE,
    
    -- Supervisión
    supervisor_id   INT REFERENCES employee(id),
    
    -- Auditoría
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE employee_role IS 'Roles de cada empleado. Un empleado puede tener múltiples roles activos.';
COMMENT ON COLUMN employee_role.supervisor_id IS 'Supervisor directo para este rol específico.';
COMMENT ON COLUMN employee_role.level IS 'staff=operativo, manager=gerente, director=dirección.';

CREATE INDEX idx_employee_role_employee ON employee_role(employee_id);
CREATE INDEX idx_employee_role_active ON employee_role(employee_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_employee_role_dept ON employee_role(department);
CREATE INDEX idx_employee_role_supervisor ON employee_role(supervisor_id) WHERE supervisor_id IS NOT NULL;

-- Un empleado no puede tener el mismo departamento dos veces activo
CREATE UNIQUE INDEX idx_employee_role_unique_active 
    ON employee_role(employee_id, department) 
    WHERE is_active = TRUE;

CREATE TRIGGER trg_employee_role_updated_at
    BEFORE UPDATE ON employee_role
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

-- ============================================================================
-- PASO 4: PERFILES ESPECÍFICOS POR ROL
-- ============================================================================

-- ─── seller_profile ───────────────────────────────────────────────────────────

CREATE TABLE seller_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- V1, V2, V3...
    
    -- Tipo de vendedor
    seller_class        seller_class_type NOT NULL DEFAULT 'collaborator',
    
    -- Metas
    sales_target        INT,
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_seller_code UNIQUE (code),
    CONSTRAINT uq_seller_role UNIQUE (employee_role_id)
);

COMMENT ON TABLE seller_profile IS 'Datos específicos de vendedores.';
COMMENT ON COLUMN seller_profile.code IS 'Código único: V1, V2, V15, etc.';
COMMENT ON COLUMN seller_profile.seller_class IS 'seller=solo comisión multinivel, collaborator=sueldo+comisión nivel 3.';

CREATE INDEX idx_seller_profile_role ON seller_profile(employee_role_id);
CREATE INDEX idx_seller_profile_class ON seller_profile(seller_class);

CREATE TRIGGER trg_seller_profile_updated_at
    BEFORE UPDATE ON seller_profile
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

-- ─── collector_profile ────────────────────────────────────────────────────────

CREATE TABLE collector_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- C1, C2, C3...
    
    -- Operación
    receipt_limit       INT NOT NULL DEFAULT 50,
    zone                VARCHAR(50),
    route               VARCHAR(50),
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_collector_code UNIQUE (code),
    CONSTRAINT uq_collector_role UNIQUE (employee_role_id)
);

COMMENT ON TABLE collector_profile IS 'Datos específicos de cobradores de campo.';
COMMENT ON COLUMN collector_profile.code IS 'Código único: C1, C2, C8, etc.';
COMMENT ON COLUMN collector_profile.receipt_limit IS 'Máximo de recibos asignados simultáneamente.';

CREATE INDEX idx_collector_profile_role ON collector_profile(employee_role_id);
CREATE INDEX idx_collector_profile_zone ON collector_profile(zone) WHERE zone IS NOT NULL;

CREATE TRIGGER trg_collector_profile_updated_at
    BEFORE UPDATE ON collector_profile
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

-- ─── adjuster_profile ─────────────────────────────────────────────────────────

CREATE TABLE adjuster_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    
    -- Identificación
    code                VARCHAR(10) NOT NULL,   -- M1, M2, M3...
    
    -- Preferencias
    shift_preference    shift_order_type,
    
    -- Auditoría
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_adjuster_code UNIQUE (code),
    CONSTRAINT uq_adjuster_role UNIQUE (employee_role_id)
);

COMMENT ON TABLE adjuster_profile IS 'Datos específicos de ajustadores de siniestros.';
COMMENT ON COLUMN adjuster_profile.code IS 'Código único: M1, M2, M5, etc.';

CREATE INDEX idx_adjuster_profile_role ON adjuster_profile(employee_role_id);

CREATE TRIGGER trg_adjuster_profile_updated_at
    BEFORE UPDATE ON adjuster_profile
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_timestamp();

-- ============================================================================
-- PASO 5: PERMISOS ESPECIALES
-- ============================================================================

CREATE TABLE settlement_permission (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    can_pay         BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_settlement_permission UNIQUE (employee_id)
);

COMMENT ON TABLE settlement_permission IS 'Permisos para pagar liquidaciones. Solo Elena y Oscar tienen can_pay=true.';

-- ============================================================================
-- PASO 6: COMISIONES DE VENDEDORES
-- ============================================================================

-- ─── Rangos de nivel según ventas ─────────────────────────────────────────────

CREATE TABLE seller_level_threshold (
    id              SERIAL PRIMARY KEY,
    level           INT NOT NULL,
    min_sales       INT NOT NULL,
    max_sales       INT,                -- NULL = sin límite (nivel 7)
    
    CONSTRAINT uq_seller_level UNIQUE (level),
    CONSTRAINT chk_level_range CHECK (level >= 1 AND level <= 10),
    CONSTRAINT chk_sales_range CHECK (max_sales IS NULL OR max_sales >= min_sales)
);

COMMENT ON TABLE seller_level_threshold IS 'Rangos de ventas mensuales para determinar nivel del vendedor.';
COMMENT ON COLUMN seller_level_threshold.max_sales IS 'NULL indica sin límite superior (nivel máximo).';

-- Datos iniciales
INSERT INTO seller_level_threshold (level, min_sales, max_sales) VALUES
    (1, 0, 20),
    (2, 21, 25),
    (3, 26, 30),
    (4, 31, 35),
    (5, 36, 40),
    (6, 41, 45),
    (7, 46, NULL);

-- ─── Comisiones por nivel y cobertura ─────────────────────────────────────────

CREATE TABLE seller_commission_rate (
    id              SERIAL PRIMARY KEY,
    seller_class    seller_class_type NOT NULL,
    level           INT NOT NULL,
    coverage_name   VARCHAR(50) NOT NULL,
    effective_from  DATE NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_commission_rate UNIQUE (seller_class, level, coverage_name, effective_from),
    CONSTRAINT chk_commission_amount CHECK (amount >= 0)
);

COMMENT ON TABLE seller_commission_rate IS 'Comisiones de vendedores con vigencia histórica.';
COMMENT ON COLUMN seller_commission_rate.effective_from IS 'Fecha desde la cual aplica esta tarifa. Buscar el registro más reciente <= fecha de venta.';
COMMENT ON COLUMN seller_commission_rate.coverage_name IS 'Nombre de cobertura: AMPLIA, PREMIUM, PLATINO, INTERMEDIA, BASICA, RC_TON_2_A_3, etc.';

CREATE INDEX idx_commission_rate_lookup ON seller_commission_rate(seller_class, level, coverage_name, effective_from);

-- Datos iniciales - Vendedores (vigencia 2026-01-01)
INSERT INTO seller_commission_rate (seller_class, level, coverage_name, effective_from, amount) VALUES
    -- Nivel 1
    ('seller', 1, 'AMPLIA', '2026-01-01', 800),
    ('seller', 1, 'PREMIUM', '2026-01-01', 725),
    ('seller', 1, 'PLATINO', '2026-01-01', 775),
    ('seller', 1, 'INTERMEDIA', '2026-01-01', 675),
    ('seller', 1, 'BASICA', '2026-01-01', 575),
    ('seller', 1, 'RC_TON_2_A_3', '2026-01-01', 825),
    ('seller', 1, 'RC_TON_3_A_5_5', '2026-01-01', 875),
    ('seller', 1, 'RC_TON_6_A_10', '2026-01-01', 1425),
    ('seller', 1, 'RC_TON_11_A_15', '2026-01-01', 1925),
    -- Nivel 2
    ('seller', 2, 'AMPLIA', '2026-01-01', 825),
    ('seller', 2, 'PREMIUM', '2026-01-01', 750),
    ('seller', 2, 'PLATINO', '2026-01-01', 800),
    ('seller', 2, 'INTERMEDIA', '2026-01-01', 700),
    ('seller', 2, 'BASICA', '2026-01-01', 600),
    ('seller', 2, 'RC_TON_2_A_3', '2026-01-01', 850),
    ('seller', 2, 'RC_TON_3_A_5_5', '2026-01-01', 900),
    ('seller', 2, 'RC_TON_6_A_10', '2026-01-01', 1450),
    ('seller', 2, 'RC_TON_11_A_15', '2026-01-01', 1950),
    -- Nivel 3
    ('seller', 3, 'AMPLIA', '2026-01-01', 850),
    ('seller', 3, 'PREMIUM', '2026-01-01', 775),
    ('seller', 3, 'PLATINO', '2026-01-01', 825),
    ('seller', 3, 'INTERMEDIA', '2026-01-01', 725),
    ('seller', 3, 'BASICA', '2026-01-01', 625),
    ('seller', 3, 'RC_TON_2_A_3', '2026-01-01', 875),
    ('seller', 3, 'RC_TON_3_A_5_5', '2026-01-01', 925),
    ('seller', 3, 'RC_TON_6_A_10', '2026-01-01', 1475),
    ('seller', 3, 'RC_TON_11_A_15', '2026-01-01', 1975),
    -- Nivel 4
    ('seller', 4, 'AMPLIA', '2026-01-01', 875),
    ('seller', 4, 'PREMIUM', '2026-01-01', 800),
    ('seller', 4, 'PLATINO', '2026-01-01', 850),
    ('seller', 4, 'INTERMEDIA', '2026-01-01', 750),
    ('seller', 4, 'BASICA', '2026-01-01', 650),
    ('seller', 4, 'RC_TON_2_A_3', '2026-01-01', 900),
    ('seller', 4, 'RC_TON_3_A_5_5', '2026-01-01', 950),
    ('seller', 4, 'RC_TON_6_A_10', '2026-01-01', 1500),
    ('seller', 4, 'RC_TON_11_A_15', '2026-01-01', 2000),
    -- Nivel 5
    ('seller', 5, 'AMPLIA', '2026-01-01', 900),
    ('seller', 5, 'PREMIUM', '2026-01-01', 825),
    ('seller', 5, 'PLATINO', '2026-01-01', 875),
    ('seller', 5, 'INTERMEDIA', '2026-01-01', 775),
    ('seller', 5, 'BASICA', '2026-01-01', 675),
    ('seller', 5, 'RC_TON_2_A_3', '2026-01-01', 925),
    ('seller', 5, 'RC_TON_3_A_5_5', '2026-01-01', 975),
    ('seller', 5, 'RC_TON_6_A_10', '2026-01-01', 1525),
    ('seller', 5, 'RC_TON_11_A_15', '2026-01-01', 2025),
    -- Nivel 6
    ('seller', 6, 'AMPLIA', '2026-01-01', 925),
    ('seller', 6, 'PREMIUM', '2026-01-01', 850),
    ('seller', 6, 'PLATINO', '2026-01-01', 900),
    ('seller', 6, 'INTERMEDIA', '2026-01-01', 800),
    ('seller', 6, 'BASICA', '2026-01-01', 700),
    ('seller', 6, 'RC_TON_2_A_3', '2026-01-01', 950),
    ('seller', 6, 'RC_TON_3_A_5_5', '2026-01-01', 1000),
    ('seller', 6, 'RC_TON_6_A_10', '2026-01-01', 1550),
    ('seller', 6, 'RC_TON_11_A_15', '2026-01-01', 2050),
    -- Nivel 7
    ('seller', 7, 'AMPLIA', '2026-01-01', 950),
    ('seller', 7, 'PREMIUM', '2026-01-01', 875),
    ('seller', 7, 'PLATINO', '2026-01-01', 925),
    ('seller', 7, 'INTERMEDIA', '2026-01-01', 825),
    ('seller', 7, 'BASICA', '2026-01-01', 725),
    ('seller', 7, 'RC_TON_2_A_3', '2026-01-01', 975),
    ('seller', 7, 'RC_TON_3_A_5_5', '2026-01-01', 1025),
    ('seller', 7, 'RC_TON_6_A_10', '2026-01-01', 1575),
    ('seller', 7, 'RC_TON_11_A_15', '2026-01-01', 2075);

-- Datos iniciales - Colaboradores (nivel único)
INSERT INTO seller_commission_rate (seller_class, level, coverage_name, effective_from, amount) VALUES
    ('collaborator', 1, 'AMPLIA', '2026-01-01', 750),
    ('collaborator', 1, 'PREMIUM', '2026-01-01', 650),
    ('collaborator', 1, 'PLATINO', '2026-01-01', 700),
    ('collaborator', 1, 'INTERMEDIA', '2026-01-01', 600),
    ('collaborator', 1, 'BASICA', '2026-01-01', 500),
    ('collaborator', 1, 'RC_TON_2_A_3', '2026-01-01', 660),
    ('collaborator', 1, 'RC_TON_3_A_5_5', '2026-01-01', 660),
    ('collaborator', 1, 'RC_TON_6_A_10', '2026-01-01', 1375),
    ('collaborator', 1, 'RC_TON_11_A_15', '2026-01-01', 1875);

-- ============================================================================
-- PASO 7: FUNCIÓN PARA DETERMINAR NIVEL DE VENDEDOR
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_get_seller_level(
    p_seller_class seller_class_type,
    p_sales_count INT,
    p_is_first_fortnight BOOLEAN DEFAULT FALSE
) RETURNS INT AS $$
DECLARE
    v_level INT;
BEGIN
    -- Colaboradores siempre nivel 1 (su tabla tiene un solo nivel)
    IF p_seller_class = 'collaborator' THEN
        RETURN 1;
    END IF;
    
    -- Primera quincena siempre nivel 1
    IF p_is_first_fortnight THEN
        RETURN 1;
    END IF;
    
    -- Buscar nivel según ventas
    SELECT level INTO v_level
    FROM seller_level_threshold
    WHERE p_sales_count >= min_sales
      AND (max_sales IS NULL OR p_sales_count <= max_sales);
    
    RETURN COALESCE(v_level, 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION fn_get_seller_level IS 'Determina el nivel de comisión de un vendedor según sus ventas del mes.';

-- ============================================================================
-- PASO 8: FUNCIÓN PARA OBTENER COMISIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_get_seller_commission(
    p_seller_class seller_class_type,
    p_level INT,
    p_coverage_name VARCHAR(50),
    p_sale_date DATE
) RETURNS NUMERIC(12,2) AS $$
DECLARE
    v_amount NUMERIC(12,2);
BEGIN
    SELECT amount INTO v_amount
    FROM seller_commission_rate
    WHERE seller_class = p_seller_class
      AND level = p_level
      AND coverage_name = p_coverage_name
      AND effective_from <= p_sale_date
    ORDER BY effective_from DESC
    LIMIT 1;
    
    RETURN COALESCE(v_amount, 0);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION fn_get_seller_commission IS 'Obtiene la comisión aplicable según clase, nivel, cobertura y fecha de venta.';

-- ============================================================================
-- PASO 9: VISTAS DE COMPATIBILIDAD
-- ============================================================================

-- Vista que emula la tabla seller original
CREATE OR REPLACE VIEW v_seller AS
SELECT 
    sp.id,
    sp.code AS code_name,
    e.first_name || ' ' || e.last_name AS full_name,
    e.phone,
    e.telegram_id,
    CASE WHEN er.is_active THEN 'active'::entity_status_type ELSE 'inactive'::entity_status_type END AS status,
    sp.seller_class AS class,
    sp.sales_target,
    e.id AS employee_id,
    er.id AS employee_role_id,
    sp.created_at,
    sp.updated_at
FROM seller_profile sp
JOIN employee_role er ON sp.employee_role_id = er.id
JOIN employee e ON er.employee_id = e.id;

COMMENT ON VIEW v_seller IS 'Vista de compatibilidad que emula la tabla seller original.';

-- Vista que emula la tabla collector original
CREATE OR REPLACE VIEW v_collector AS
SELECT 
    cp.id,
    cp.code AS code_name,
    e.first_name || ' ' || e.last_name AS full_name,
    e.phone,
    cp.receipt_limit,
    CASE WHEN er.is_active THEN 'active'::entity_status_type ELSE 'inactive'::entity_status_type END AS status,
    e.id AS employee_id,
    er.id AS employee_role_id,
    cp.zone,
    cp.route,
    cp.created_at,
    cp.updated_at
FROM collector_profile cp
JOIN employee_role er ON cp.employee_role_id = er.id
JOIN employee e ON er.employee_id = e.id;

COMMENT ON VIEW v_collector IS 'Vista de compatibilidad que emula la tabla collector original.';

-- Vista que emula la tabla adjuster original
CREATE OR REPLACE VIEW v_adjuster AS
SELECT 
    ap.id,
    ap.code,
    e.first_name || ' ' || e.last_name AS name,
    e.phone,
    e.telegram_id,
    CASE WHEN er.is_active THEN 'active'::entity_status_type ELSE 'inactive'::entity_status_type END AS status,
    e.id AS employee_id,
    er.id AS employee_role_id,
    ap.shift_preference,
    ap.created_at,
    ap.updated_at
FROM adjuster_profile ap
JOIN employee_role er ON ap.employee_role_id = er.id
JOIN employee e ON er.employee_id = e.id;

COMMENT ON VIEW v_adjuster IS 'Vista de compatibilidad que emula la tabla adjuster original.';

-- Vista de empleados con todos sus roles
CREATE OR REPLACE VIEW v_employee_roles AS
SELECT 
    e.id AS employee_id,
    e.first_name,
    e.last_name,
    e.first_name || ' ' || e.last_name AS full_name,
    e.phone,
    e.telegram_id,
    e.hire_date,
    e.status AS employee_status,
    er.id AS role_id,
    er.department,
    er.level AS role_level,
    er.is_active AS role_active,
    er.supervisor_id,
    sup.first_name || ' ' || sup.last_name AS supervisor_name
FROM employee e
LEFT JOIN employee_role er ON e.id = er.employee_id
LEFT JOIN employee sup ON er.supervisor_id = sup.id;

COMMENT ON VIEW v_employee_roles IS 'Vista de empleados con todos sus roles y supervisores.';

-- ============================================================================
-- PASO 10: MODIFICACIÓN A app_user (comentado - ejecutar después de migración de datos)
-- ============================================================================

-- NOTA: Ejecutar estos cambios DESPUÉS de migrar los datos de usuarios existentes
--
-- ALTER TABLE app_user ADD COLUMN employee_id INT REFERENCES employee(id);
-- 
-- -- Migrar datos: crear employees y actualizar employee_id en app_user
-- -- (script de migración separado)
--
-- ALTER TABLE app_user ALTER COLUMN employee_id SET NOT NULL;
-- ALTER TABLE app_user DROP COLUMN first_name;
-- ALTER TABLE app_user DROP COLUMN last_name;
-- ALTER TABLE app_user DROP COLUMN email;

-- ============================================================================
-- PASO 11: AUDITORÍA
-- ============================================================================

CREATE TRIGGER trg_employee_audit
    AFTER INSERT OR UPDATE OR DELETE ON employee
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_employee_role_audit
    AFTER INSERT OR UPDATE OR DELETE ON employee_role
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

-- ============================================================================
-- FIN DE MIGRACIÓN
-- ============================================================================

-- Resumen de objetos creados:
-- 
-- Tablas nuevas:
--   - employee (persona física)
--   - employee_role (roles del empleado)
--   - seller_profile (datos de vendedor)
--   - collector_profile (datos de cobrador)
--   - adjuster_profile (datos de ajustador)
--   - settlement_permission (permisos de liquidación)
--   - seller_level_threshold (rangos de nivel)
--   - seller_commission_rate (comisiones con vigencia)
--
-- Funciones:
--   - fn_get_seller_level(seller_class, sales_count, is_first_fortnight)
--   - fn_get_seller_commission(seller_class, level, coverage_name, sale_date)
--
-- Vistas de compatibilidad:
--   - v_seller
--   - v_collector
--   - v_adjuster
--   - v_employee_roles
--
-- ENUMs:
--   - department_type
--   - role_level_type
