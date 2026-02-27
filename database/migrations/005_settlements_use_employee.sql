-- ============================================================================
-- Migration: 005_settlements_use_employee
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripción: Ajustar liquidaciones para usar la nueva estructura de empleados
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE settlement_status AS ENUM ('pending', 'partial', 'paid', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE settlement_method AS ENUM ('cash', 'transfer', 'check', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE deduction_type AS ENUM ('fuel', 'loan', 'shortage', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS settlement (
    id                  SERIAL PRIMARY KEY,
    employee_role_id    INT NOT NULL REFERENCES employee_role(id),
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    total_collected     NUMERIC(12,2) NOT NULL DEFAULT 0,
    commission_amount   NUMERIC(12,2) NOT NULL DEFAULT 0,
    deduction_amount    NUMERIC(12,2) NOT NULL DEFAULT 0,
    net_amount          NUMERIC(12,2) NOT NULL DEFAULT 0,
    amount_paid         NUMERIC(12,2) NOT NULL DEFAULT 0,
    status              settlement_status NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settlement_deduction (
    id              SERIAL PRIMARY KEY,
    settlement_id   INT NOT NULL REFERENCES settlement(id) ON DELETE CASCADE,
    type            deduction_type NOT NULL,
    concept         VARCHAR(100) NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settlement_payment (
    id              SERIAL PRIMARY KEY,
    settlement_id   INT NOT NULL REFERENCES settlement(id) ON DELETE CASCADE,
    amount          NUMERIC(12,2) NOT NULL,
    method          settlement_method NOT NULL DEFAULT 'cash',
    reference       VARCHAR(100),
    paid_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      INT REFERENCES employee(id)
);
