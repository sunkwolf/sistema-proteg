-- ============================================================================
-- Migration: 003_add_settlements
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripcion: Tablas para liquidaciones de cobradores (comisiones y deducciones)
-- ============================================================================

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE settlement_status_type AS ENUM ('pending', 'paid');
CREATE TYPE settlement_method_type AS ENUM ('cash', 'transfer');
CREATE TYPE deduction_type AS ENUM ('fuel', 'loan', 'shortage', 'advance', 'other');
CREATE TYPE loan_status_type AS ENUM ('active', 'paid_off', 'cancelled');

-- ============================================================================
-- employee_loan — Préstamos a empleados (cobradores/vendedores)
-- ============================================================================

CREATE TABLE employee_loan (
    id                  SERIAL PRIMARY KEY,
    collector_id        INT REFERENCES collector(id) ON DELETE RESTRICT,
    seller_id           INT REFERENCES seller(id) ON DELETE RESTRICT,
    
    concept             VARCHAR(100) NOT NULL,          -- 'Préstamo moto', 'Adelanto', etc.
    total_amount        NUMERIC(12,2) NOT NULL,         -- Monto total del préstamo
    installment_amount  NUMERIC(12,2) NOT NULL,         -- Cuota quincenal
    total_installments  INT NOT NULL,                   -- Total de cuotas
    paid_installments   INT NOT NULL DEFAULT 0,         -- Cuotas pagadas
    remaining_balance   NUMERIC(12,2) NOT NULL,         -- Saldo pendiente
    
    status              loan_status_type NOT NULL DEFAULT 'active',
    start_date          DATE NOT NULL,
    end_date            DATE,                           -- Fecha estimada de término
    
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Solo uno de los dos debe tener valor
    CONSTRAINT chk_loan_employee CHECK (
        (collector_id IS NOT NULL AND seller_id IS NULL) OR
        (collector_id IS NULL AND seller_id IS NOT NULL)
    )
);

COMMENT ON TABLE employee_loan IS 'Préstamos y adelantos a cobradores/vendedores con pago quincenal';
COMMENT ON COLUMN employee_loan.concept IS 'Descripción del préstamo: moto, adelanto, uniforme, etc.';
COMMENT ON COLUMN employee_loan.installment_amount IS 'Monto de cada cuota quincenal';

CREATE INDEX idx_employee_loan_collector ON employee_loan(collector_id) WHERE collector_id IS NOT NULL;
CREATE INDEX idx_employee_loan_seller ON employee_loan(seller_id) WHERE seller_id IS NOT NULL;
CREATE INDEX idx_employee_loan_status ON employee_loan(status);

-- ============================================================================
-- settlement — Liquidaciones quincenales
-- ============================================================================

CREATE TABLE settlement (
    id                  SERIAL PRIMARY KEY,
    collector_id        INT NOT NULL REFERENCES collector(id) ON DELETE RESTRICT,
    
    -- Período
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    
    -- Comisiones (calculadas)
    commission_regular  NUMERIC(12,2) NOT NULL DEFAULT 0,   -- 10% cobranza normal
    commission_cash     NUMERIC(12,2) NOT NULL DEFAULT 0,   -- 5% pagos de contado
    commission_delivery NUMERIC(12,2) NOT NULL DEFAULT 0,   -- $50 x entrega
    total_commissions   NUMERIC(12,2) GENERATED ALWAYS AS (
        commission_regular + commission_cash + commission_delivery
    ) STORED,
    
    -- Deducciones
    deduction_fuel      NUMERIC(12,2) NOT NULL DEFAULT 0,   -- 50% gasolina
    deduction_loan      NUMERIC(12,2) NOT NULL DEFAULT 0,   -- Cuota préstamo
    deduction_shortage  NUMERIC(12,2) NOT NULL DEFAULT 0,   -- Faltantes de efectivo
    deduction_other     NUMERIC(12,2) NOT NULL DEFAULT 0,   -- Otras deducciones
    total_deductions    NUMERIC(12,2) GENERATED ALWAYS AS (
        deduction_fuel + deduction_loan + deduction_shortage + deduction_other
    ) STORED,
    
    -- Neto
    net_amount          NUMERIC(12,2) GENERATED ALWAYS AS (
        (commission_regular + commission_cash + commission_delivery) -
        (deduction_fuel + deduction_loan + deduction_shortage + deduction_other)
    ) STORED,
    
    -- Estado y pago
    status              settlement_status_type NOT NULL DEFAULT 'pending',
    payment_method      settlement_method_type,
    paid_at             TIMESTAMPTZ,
    paid_by             INT REFERENCES app_user(id),
    
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Un cobrador solo puede tener una liquidación por período
    CONSTRAINT uq_settlement_period UNIQUE (collector_id, period_start, period_end)
);

COMMENT ON TABLE settlement IS 'Liquidaciones quincenales de comisiones y deducciones para cobradores';
COMMENT ON COLUMN settlement.commission_regular IS '10% de cobros normales (abonos)';
COMMENT ON COLUMN settlement.commission_cash IS '5% de pagos de contado';
COMMENT ON COLUMN settlement.commission_delivery IS '$50 fijos por entrega de póliza/endoso';
COMMENT ON COLUMN settlement.deduction_fuel IS '50% del gasto de gasolina del período';
COMMENT ON COLUMN settlement.deduction_loan IS 'Cuota de préstamo descontada este período';
COMMENT ON COLUMN settlement.net_amount IS 'Monto neto a pagar (comisiones - deducciones)';

CREATE INDEX idx_settlement_collector ON settlement(collector_id);
CREATE INDEX idx_settlement_period ON settlement(period_start, period_end);
CREATE INDEX idx_settlement_status ON settlement(status);

-- ============================================================================
-- settlement_deduction — Detalle de deducciones manuales
-- ============================================================================

CREATE TABLE settlement_deduction (
    id              SERIAL PRIMARY KEY,
    settlement_id   INT NOT NULL REFERENCES settlement(id) ON DELETE CASCADE,
    
    deduction_type  deduction_type NOT NULL,
    concept         VARCHAR(255) NOT NULL,
    amount          NUMERIC(12,2) NOT NULL,
    
    -- Referencia opcional al préstamo si aplica
    loan_id         INT REFERENCES employee_loan(id),
    
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE settlement_deduction IS 'Detalle de cada deducción individual en una liquidación';
COMMENT ON COLUMN settlement_deduction.loan_id IS 'Referencia al préstamo si la deducción es cuota de préstamo';

CREATE INDEX idx_settlement_deduction_settlement ON settlement_deduction(settlement_id);

-- ============================================================================
-- settlement_payment — Pagos incluidos en una liquidación (para auditoría)
-- ============================================================================

CREATE TABLE settlement_payment (
    id              SERIAL PRIMARY KEY,
    settlement_id   INT NOT NULL REFERENCES settlement(id) ON DELETE CASCADE,
    payment_id      INT NOT NULL REFERENCES payment(id) ON DELETE RESTRICT,
    
    commission_type VARCHAR(20) NOT NULL,       -- 'regular', 'cash', 'delivery'
    amount_collected NUMERIC(12,2) NOT NULL,    -- Monto cobrado
    commission_amount NUMERIC(12,2) NOT NULL,   -- Comisión calculada
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Un pago solo puede estar en una liquidación
    CONSTRAINT uq_settlement_payment UNIQUE (payment_id)
);

COMMENT ON TABLE settlement_payment IS 'Relación de pagos incluidos en cada liquidación para trazabilidad';

CREATE INDEX idx_settlement_payment_settlement ON settlement_payment(settlement_id);
CREATE INDEX idx_settlement_payment_payment ON settlement_payment(payment_id);
