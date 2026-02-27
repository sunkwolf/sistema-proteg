-- ============================================================================
-- Migration: 004_employee_restructure
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripción: Reestructura de empleados - tabla unificada con roles múltiples
-- ============================================================================

-- ============================================================================
-- PASO 1: TIPOS BASE Y ENUMS (Faltantes en la versión anterior)
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE entity_status_type AS ENUM ('active', 'inactive', 'suspended');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE department_type AS ENUM (
        'sales', 'collection', 'claims', 'admin', 'hr', 'management'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE role_level_type AS ENUM ('staff', 'manager', 'director');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE seller_class_type AS ENUM ('seller', 'collaborator');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE shift_order_type AS ENUM ('first', 'second', 'third', 'rest');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Función de timestamp (necesaria para los triggers)
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PASO 2: TABLA EMPLOYEE
-- ============================================================================

CREATE TABLE IF NOT EXISTS employee (
    id              SERIAL PRIMARY KEY,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    birth_date      DATE,
    gender          gender_type,
    phone           VARCHAR(20),
    phone_2         VARCHAR(20),
    email           VARCHAR(100),
    telegram_id     BIGINT,
    rfc             VARCHAR(13),
    curp            VARCHAR(18),
    address_id      BIGINT, -- Referencia opcional (tabla address no definida aquí)
    hire_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    termination_date DATE,
    status          entity_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_employee_status ON employee(status);
CREATE INDEX IF NOT EXISTS idx_employee_name ON employee(last_name, first_name);

CREATE OR REPLACE TRIGGER trg_employee_updated_at
    BEFORE UPDATE ON employee
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- ============================================================================
-- PASO 3: TABLA EMPLOYEE_ROLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS employee_role (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    department      department_type NOT NULL,
    level           role_level_type NOT NULL DEFAULT 'staff',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    start_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date        DATE,
    supervisor_id   INT REFERENCES employee(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_employee_role_employee ON employee_role(employee_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_employee_role_unique_active 
    ON employee_role(employee_id, department) WHERE is_active = TRUE;

CREATE OR REPLACE TRIGGER trg_employee_role_updated_at
    BEFORE UPDATE ON employee_role
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- ============================================================================
-- PASO 4: PERFILES ESPECÍFICOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS seller_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    code                VARCHAR(10) NOT NULL UNIQUE,
    seller_class        seller_class_type NOT NULL DEFAULT 'collaborator',
    sales_target        INT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_seller_role UNIQUE (employee_role_id)
);

CREATE TABLE IF NOT EXISTS collector_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    code                VARCHAR(10) NOT NULL UNIQUE,
    receipt_limit       INT NOT NULL DEFAULT 50,
    zone                VARCHAR(50),
    route               VARCHAR(50),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_collector_role UNIQUE (employee_role_id)
);

CREATE TABLE IF NOT EXISTS adjuster_profile (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id) ON DELETE CASCADE,
    code                VARCHAR(10) NOT NULL UNIQUE,
    shift_preference    shift_order_type,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_adjuster_role UNIQUE (employee_role_id)
);

-- ============================================================================
-- PASO 5: PERMISOS Y COMISIONES
-- ============================================================================

CREATE TABLE IF NOT EXISTS settlement_permission (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employee(id) ON DELETE CASCADE UNIQUE,
    can_pay         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS seller_level_threshold (
    id              SERIAL PRIMARY KEY,
    level           INT NOT NULL UNIQUE,
    min_sales       INT NOT NULL,
    max_sales       INT
);

INSERT INTO seller_level_threshold (level, min_sales, max_sales) VALUES
    (1, 0, 20), (2, 21, 25), (3, 26, 30), (4, 31, 35), (5, 36, 40), (6, 41, 45), (7, 46, NULL)
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS seller_commission_rate (
    id              SERIAL PRIMARY KEY,
    seller_class    seller_class_type NOT NULL,
    level           INT NOT NULL,
    coverage_name   VARCHAR(50) NOT NULL,
    effective_from  DATE NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_commission_rate UNIQUE (seller_class, level, coverage_name, effective_from)
);

-- ============================================================================
-- PASO 6: FUNCIONES Y VISTAS
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_get_seller_level(
    p_seller_class seller_class_type,
    p_sales_count INT,
    p_is_first_fortnight BOOLEAN DEFAULT FALSE
) RETURNS INT AS $$
DECLARE v_level INT;
BEGIN
    IF p_seller_class = 'collaborator' OR p_is_first_fortnight THEN RETURN 1; END IF;
    SELECT level INTO v_level FROM seller_level_threshold
    WHERE p_sales_count >= min_sales AND (max_sales IS NULL OR p_sales_count <= max_sales);
    RETURN COALESCE(v_level, 1);
END; $$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION fn_get_seller_commission(
    p_seller_class seller_class_type,
    p_level INT,
    p_coverage_name VARCHAR(50),
    p_sale_date DATE
) RETURNS NUMERIC(12,2) AS $$
DECLARE v_amount NUMERIC(12,2);
BEGIN
    SELECT amount INTO v_amount FROM seller_commission_rate
    WHERE seller_class = p_seller_class AND level = p_level AND coverage_name = p_coverage_name AND effective_from <= p_sale_date
    ORDER BY effective_from DESC LIMIT 1;
    RETURN COALESCE(v_amount, 0);
END; $$ LANGUAGE plpgsql STABLE;

-- Vistas de compatibilidad
CREATE OR REPLACE VIEW v_seller AS
SELECT sp.id, sp.code AS code_name, e.first_name || ' ' || e.last_name AS full_name, e.phone, e.status, sp.seller_class AS class, e.id AS employee_id, er.id AS employee_role_id
FROM seller_profile sp JOIN employee_role er ON sp.employee_role_id = er.id JOIN employee e ON er.employee_id = e.id;

CREATE OR REPLACE VIEW v_collector AS
SELECT cp.id, cp.code AS code_name, e.first_name || ' ' || e.last_name AS full_name, e.phone, cp.receipt_limit, e.status, e.id AS employee_id, er.id AS employee_role_id, cp.zone, cp.route
FROM collector_profile cp JOIN employee_role er ON cp.employee_role_id = er.id JOIN employee e ON er.employee_id = e.id;

CREATE OR REPLACE VIEW v_adjuster AS
SELECT ap.id, ap.code, e.first_name || ' ' || e.last_name AS name, e.phone, e.status, e.id AS employee_id, er.id AS employee_role_id, ap.shift_preference
FROM adjuster_profile ap JOIN employee_role er ON ap.employee_role_id = er.id JOIN employee e ON er.employee_id = e.id;
