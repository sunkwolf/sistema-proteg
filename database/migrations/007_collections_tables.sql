-- ============================================================================
-- Migration 007: Collections Module Tables
-- Fecha: 2026-03-02
-- Autores: Claudy + Fer
--
-- Crea las tablas necesarias para el módulo de cobranza.
-- Rollback: instrucciones al final del archivo.
-- ============================================================================

BEGIN;

-- PASO 1: ENUM Types (solo los que no existen)
DO $$ BEGIN CREATE TYPE gender_type AS ENUM ('male', 'female'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE marital_status_type AS ENUM ('single', 'married', 'divorced', 'widowed', 'common_law'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE entity_status_type AS ENUM ('active', 'inactive'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE policy_status_type AS ENUM ('active', 'pending', 'morosa', 'pre_effective', 'expired', 'cancelled', 'suspended', 'no_status'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE payment_status_type AS ENUM ('pending', 'paid', 'late', 'overdue', 'cancelled'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE payment_method_type AS ENUM ('cash', 'deposit', 'transfer', 'crucero', 'konfio', 'terminal_banorte'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE payment_plan_type AS ENUM ('cash', 'cash_2_installments', 'monthly_7'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE office_delivery_type AS ENUM ('pending', 'delivered'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE receipt_status_type AS ENUM ('unassigned', 'assigned', 'used', 'delivered', 'cancelled', 'lost', 'cancelled_undelivered'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE service_type AS ENUM ('private', 'commercial'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE vehicle_type_enum AS ENUM ('automobile', 'truck', 'suv', 'motorcycle', 'mototaxi'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE coverage_category_type AS ENUM ('liability', 'comprehensive', 'platform'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE seller_class_type AS ENUM ('seller', 'collaborator'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE payment_proposal_status_type AS ENUM ('active', 'applied', 'discarded'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE card_status_type AS ENUM ('active', 'paid_off', 'cancelled', 'recovery'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE approval_request_type AS ENUM ('policy_submission', 'payment_submission'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE approval_status_type AS ENUM ('pending', 'approved', 'rejected', 'cancelled'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE device_type_enum AS ENUM ('android', 'ios', 'web'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE app_type_enum AS ENUM ('collector_app', 'seller_app', 'adjuster_app', 'desktop'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- PASO 2: Extensiones
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- PASO 3: Catálogos
CREATE TABLE IF NOT EXISTS municipality (
    id BIGSERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL,
    short_name VARCHAR(50) NOT NULL, siga_code VARCHAR(100),
    CONSTRAINT uq_municipality_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS address (
    id BIGSERIAL PRIMARY KEY, street VARCHAR(150) NOT NULL,
    exterior_number VARCHAR(10), interior_number VARCHAR(10),
    cross_street_1 VARCHAR(100), cross_street_2 VARCHAR(100),
    neighborhood VARCHAR(100), municipality_id BIGINT REFERENCES municipality(id),
    postal_code VARCHAR(10), geom geometry(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_address_municipality ON address(municipality_id);
CREATE INDEX IF NOT EXISTS idx_address_geom ON address USING GIST (geom);

-- PASO 4: Entidades de negocio
CREATE TABLE IF NOT EXISTS client (
    id BIGSERIAL PRIMARY KEY, first_name VARCHAR(50) NOT NULL,
    paternal_surname VARCHAR(50) NOT NULL, maternal_surname VARCHAR(50),
    rfc VARCHAR(13), birth_date DATE, gender gender_type,
    marital_status marital_status_type, address_id BIGINT REFERENCES address(id),
    phone_1 VARCHAR(20), phone_2 VARCHAR(20), email VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_client_name ON client(paternal_surname, first_name) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_client_phone ON client(phone_1) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS seller (
    id SERIAL PRIMARY KEY, code_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(255) NOT NULL, phone VARCHAR(20), telegram_id BIGINT,
    status entity_status_type NOT NULL DEFAULT 'active',
    class seller_class_type NOT NULL DEFAULT 'collaborator', sales_target INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_seller_code UNIQUE (code_name)
);

CREATE TABLE IF NOT EXISTS collector (
    id SERIAL PRIMARY KEY, code_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(255), phone VARCHAR(20),
    receipt_limit INT NOT NULL DEFAULT 50,
    status entity_status_type NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_collector_code UNIQUE (code_name)
);

CREATE TABLE IF NOT EXISTS vehicle (
    id SERIAL PRIMARY KEY, brand VARCHAR(45) NOT NULL,
    model_type VARCHAR(45), model_year VARCHAR(10), color VARCHAR(45),
    vehicle_key INT, seats INT, serial_number VARCHAR(45),
    plates VARCHAR(20), load_capacity VARCHAR(15),
    vehicle_type vehicle_type_enum, cylinder_capacity VARCHAR(25),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_vehicle_serial UNIQUE (serial_number)
);
CREATE INDEX IF NOT EXISTS idx_vehicle_plates ON vehicle(plates);

CREATE TABLE IF NOT EXISTS coverage (
    id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL, vehicle_key INT NOT NULL,
    service_type service_type NOT NULL,
    category coverage_category_type NOT NULL DEFAULT 'liability',
    cylinder_capacity VARCHAR(20), credit_price NUMERIC(12,2) NOT NULL,
    initial_payment NUMERIC(12,2) NOT NULL, cash_price NUMERIC(12,2) NOT NULL,
    tow_services_included INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PASO 5: Tablas principales de cobranza
CREATE TABLE IF NOT EXISTS policy (
    id SERIAL PRIMARY KEY, folio INT NOT NULL,
    renewal_folio INT, client_id BIGINT NOT NULL REFERENCES client(id) ON DELETE RESTRICT,
    vehicle_id INT NOT NULL REFERENCES vehicle(id) ON DELETE RESTRICT,
    coverage_id INT NOT NULL REFERENCES coverage(id) ON DELETE RESTRICT,
    seller_id INT REFERENCES seller(id) ON DELETE SET NULL,
    service_type service_type, contract_folio INT,
    effective_date DATE, expiration_date DATE, sale_date DATE, elaboration_date DATE,
    status policy_status_type NOT NULL DEFAULT 'active',
    payment_plan payment_plan_type,
    data_entry_user_id INT REFERENCES app_user(id),
    tow_services_available INT NOT NULL DEFAULT 0, comments TEXT,
    has_fraud_observation BOOLEAN NOT NULL DEFAULT FALSE,
    has_payment_issues BOOLEAN NOT NULL DEFAULT FALSE,
    contract_image_path VARCHAR(500), prima_total NUMERIC(12,2),
    quote_external_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_policy_folio UNIQUE (folio),
    CONSTRAINT chk_policy_tow CHECK (tow_services_available >= 0)
);
CREATE INDEX IF NOT EXISTS idx_policy_folio ON policy(folio);
CREATE INDEX IF NOT EXISTS idx_policy_client ON policy(client_id);
CREATE INDEX IF NOT EXISTS idx_policy_seller ON policy(seller_id);
CREATE INDEX IF NOT EXISTS idx_policy_status ON policy(status);

CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    seller_id INT REFERENCES seller(id) ON DELETE SET NULL,
    collector_id INT REFERENCES collector(id) ON DELETE SET NULL,
    user_id INT REFERENCES app_user(id) ON DELETE SET NULL,
    payment_number INT NOT NULL, receipt_number VARCHAR(10),
    due_date DATE, actual_date DATE, amount NUMERIC(12,2),
    payment_method payment_method_type,
    office_delivery_status office_delivery_type,
    office_delivery_date DATE, policy_delivered BOOLEAN DEFAULT FALSE,
    comments TEXT, status payment_status_type NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_payment_number CHECK (payment_number > 0),
    CONSTRAINT chk_payment_amount CHECK (amount IS NULL OR amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_payment_policy ON payment(policy_id);
CREATE INDEX IF NOT EXISTS idx_payment_collector ON payment(collector_id);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(status);
CREATE INDEX IF NOT EXISTS idx_payment_due_date ON payment(due_date);

CREATE TABLE IF NOT EXISTS payment_proposal (
    id SERIAL PRIMARY KEY,
    original_payment_id INT NOT NULL REFERENCES payment(id) ON DELETE RESTRICT,
    policy_id INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    seller_id INT REFERENCES seller(id) ON DELETE SET NULL,
    collector_id INT REFERENCES collector(id) ON DELETE SET NULL,
    user_id INT REFERENCES app_user(id) ON DELETE SET NULL,
    payment_number INT NOT NULL, receipt_number VARCHAR(10),
    due_date DATE, actual_date DATE, amount NUMERIC(12,2),
    payment_method payment_method_type,
    office_delivery_status office_delivery_type,
    office_delivery_date DATE, policy_delivered BOOLEAN DEFAULT FALSE,
    comments TEXT, payment_status payment_status_type NOT NULL DEFAULT 'pending',
    draft_status payment_proposal_status_type NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS receipt (
    id SERIAL PRIMARY KEY, receipt_number VARCHAR(10) NOT NULL,
    policy_id INT REFERENCES policy(id) ON DELETE RESTRICT,
    collector_id INT REFERENCES collector(id) ON DELETE SET NULL,
    payment_id INT REFERENCES payment(id) ON DELETE SET NULL,
    assignment_date DATE, usage_date DATE, delivery_date DATE,
    status receipt_status_type NOT NULL DEFAULT 'unassigned',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_receipt_number UNIQUE (receipt_number)
);
CREATE INDEX IF NOT EXISTS idx_receipt_collector ON receipt(collector_id);

CREATE TABLE IF NOT EXISTS card (
    id SERIAL PRIMARY KEY,
    policy_id INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    current_holder VARCHAR(50) NOT NULL, assignment_date DATE NOT NULL,
    seller_id INT REFERENCES seller(id),
    status card_status_type NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_card_policy ON card(policy_id);
CREATE INDEX IF NOT EXISTS idx_card_status ON card(status);
CREATE INDEX IF NOT EXISTS idx_card_holder ON card(current_holder);

CREATE TABLE IF NOT EXISTS collection_assignment (
    id SERIAL PRIMARY KEY,
    card_id INT NOT NULL REFERENCES card(id) ON DELETE CASCADE,
    policy_id INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    assigned_to VARCHAR(50) NOT NULL, zone VARCHAR(50), route VARCHAR(50),
    assignment_date DATE NOT NULL, observations TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_collection_assignment_card ON collection_assignment(card_id);

CREATE TABLE IF NOT EXISTS visit_notice (
    id SERIAL PRIMARY KEY,
    card_id INT REFERENCES card(id) ON DELETE SET NULL,
    policy_id INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    visit_date DATE NOT NULL, comments TEXT,
    payment_id INT REFERENCES payment(id) ON DELETE SET NULL,
    notice_number INT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_visit_policy ON visit_notice(policy_id);

-- PASO 6: Sesiones móviles y autorización
CREATE TABLE IF NOT EXISTS device_session (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL, device_type device_type_enum NOT NULL,
    app_type app_type_enum NOT NULL, app_version VARCHAR(20),
    push_token VARCHAR(500), token VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_device_session_token UNIQUE (token)
);

CREATE TABLE IF NOT EXISTS approval_request (
    id SERIAL PRIMARY KEY,
    request_type approval_request_type NOT NULL,
    status approval_status_type NOT NULL DEFAULT 'pending',
    entity_type VARCHAR(50) NOT NULL, entity_id INT,
    payload JSONB NOT NULL,
    submitted_by_user_id INT NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    submitted_from_device_id INT REFERENCES device_session(id) ON DELETE SET NULL,
    reviewed_by_user_id INT REFERENCES app_user(id) ON DELETE SET NULL,
    review_notes TEXT, submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_approval_status ON approval_request(status) WHERE status = 'pending';

-- PASO 7: Auditoría (particionada)
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL NOT NULL, table_name VARCHAR(63) NOT NULL,
    record_id INT NOT NULL, action VARCHAR(10) NOT NULL,
    old_values JSONB, new_values JSONB,
    changed_by_user_id INT, changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), PRIMARY KEY (id, changed_at)
) PARTITION BY RANGE (changed_at);

DO $$
DECLARE m INT; start_d TEXT; end_d TEXT; pname TEXT;
BEGIN
    FOR m IN 1..12 LOOP
        pname := 'audit_log_2026_' || LPAD(m::TEXT, 2, '0');
        start_d := '2026-' || LPAD(m::TEXT, 2, '0') || '-01';
        IF m = 12 THEN end_d := '2027-01-01';
        ELSE end_d := '2026-' || LPAD((m+1)::TEXT, 2, '0') || '-01'; END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = pname) THEN
            EXECUTE format('CREATE TABLE %I PARTITION OF audit_log FOR VALUES FROM (%L) TO (%L)', pname, start_d, end_d);
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'audit_log_default') THEN
        EXECUTE 'CREATE TABLE audit_log_default PARTITION OF audit_log DEFAULT';
    END IF;
END $$;

-- PASO 8: Funciones y Triggers
CREATE OR REPLACE FUNCTION fn_update_timestamp() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

DO $$
DECLARE t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY['client','seller','collector','vehicle','coverage','policy','payment','payment_proposal','receipt','card','device_session','approval_request']) LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_' || t || '_updated_at') THEN
            EXECUTE format('CREATE TRIGGER trg_%s_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();', t, t);
        END IF;
    END LOOP;
END $$;

CREATE OR REPLACE FUNCTION fn_audit_trigger() RETURNS TRIGGER AS $$
DECLARE v_user_id INT; v_user_name TEXT;
BEGIN
    v_user_id := NULLIF(current_setting('myapp.current_user_id', true), '')::INT;
    v_user_name := COALESCE(NULLIF(current_setting('myapp.current_user_name', true), ''), current_user);
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(table_name, record_id, action, new_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), v_user_id, v_user_name); RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values, new_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), v_user_id, v_user_name); RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), v_user_id, v_user_name); RETURN OLD;
    END IF; RETURN NULL;
END; $$ LANGUAGE plpgsql;

DO $$
DECLARE t TEXT;
BEGIN
    FOR t IN SELECT unnest(ARRAY['policy','payment','approval_request']) LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_' || t || '_audit') THEN
            EXECUTE format('CREATE TRIGGER trg_%s_audit AFTER INSERT OR UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();', t, t);
        END IF;
    END LOOP;
END $$;

COMMIT;

-- ROLLBACK (emergencia):
-- DROP TABLE IF EXISTS approval_request, device_session, visit_notice, collection_assignment, card, receipt, payment_proposal, payment, policy, coverage, vehicle, collector, seller, client, address, municipality, audit_log CASCADE;
