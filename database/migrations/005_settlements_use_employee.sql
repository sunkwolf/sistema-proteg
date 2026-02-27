-- ============================================================================
-- Migration: 005_settlements_use_employee
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripción: Actualiza tablas de liquidaciones para usar estructura de empleados
-- 
-- DEPENDENCIAS: 
--   - 003_add_settlements.sql (crea tablas originales)
--   - 004_employee_restructure.sql (crea estructura de empleados)
--
-- EJECUTAR DESPUÉS DE: 004_employee_restructure.sql
-- ============================================================================

-- ============================================================================
-- PASO 1: AGREGAR ESTADO 'partial' AL ENUM
-- ============================================================================

ALTER TYPE settlement_status_type ADD VALUE 'partial' AFTER 'pending';

COMMENT ON TYPE settlement_status_type IS 'Estados de liquidación: pending=sin pagar, partial=pago parcial, paid=pagado completo';

-- ============================================================================
-- PASO 2: MODIFICAR employee_loan PARA USAR employee_id
-- ============================================================================

-- Agregar nueva columna
ALTER TABLE employee_loan ADD COLUMN employee_id INT REFERENCES employee(id) ON DELETE RESTRICT;

-- Nota: La migración de datos (copiar collector_id/seller_id → employee_id) 
-- se hace en el script ETL, no aquí.
-- Por ahora solo preparamos la estructura.

-- Crear índice para la nueva columna
CREATE INDEX idx_employee_loan_employee ON employee_loan(employee_id) WHERE employee_id IS NOT NULL;

-- Actualizar comentario
COMMENT ON TABLE employee_loan IS 'Préstamos y adelantos a empleados. Usa employee_id (nuevo) o collector_id/seller_id (legacy).';
COMMENT ON COLUMN employee_loan.employee_id IS 'FK a employee.id - usar este campo para nuevos registros.';

-- ============================================================================
-- PASO 3: MODIFICAR settlement PARA USAR employee_role_id
-- ============================================================================

-- Agregar nuevas columnas
ALTER TABLE settlement 
    ADD COLUMN employee_role_id INT REFERENCES employee_role(id) ON DELETE RESTRICT,
    ADD COLUMN amount_paid NUMERIC(12,2) NOT NULL DEFAULT 0;

-- Crear columna calculada para lo que falta por pagar
-- NOTA: PostgreSQL no permite ALTER para agregar generated columns, 
-- así que usamos un trigger o vista

-- Crear índice para la nueva columna
CREATE INDEX idx_settlement_employee_role ON settlement(employee_role_id) WHERE employee_role_id IS NOT NULL;

-- Actualizar constraint unique para incluir employee_role_id
-- (mantenemos el viejo para compatibilidad)
CREATE UNIQUE INDEX idx_settlement_period_employee_role 
    ON settlement(employee_role_id, period_start, period_end) 
    WHERE employee_role_id IS NOT NULL;

-- Actualizar comentarios
COMMENT ON COLUMN settlement.employee_role_id IS 'FK a employee_role.id (rol de cobrador). Usar este campo para nuevos registros.';
COMMENT ON COLUMN settlement.amount_paid IS 'Monto ya pagado. Para pagos parciales: amount_paid < net_amount.';

-- ============================================================================
-- PASO 4: FUNCIÓN PARA CALCULAR MONTO RESTANTE
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_settlement_remaining(p_settlement_id INT)
RETURNS NUMERIC(12,2) AS $$
DECLARE
    v_net NUMERIC(12,2);
    v_paid NUMERIC(12,2);
BEGIN
    SELECT net_amount, amount_paid 
    INTO v_net, v_paid
    FROM settlement 
    WHERE id = p_settlement_id;
    
    RETURN COALESCE(v_net, 0) - COALESCE(v_paid, 0);
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION fn_settlement_remaining IS 'Calcula el monto restante por pagar en una liquidación.';

-- ============================================================================
-- PASO 5: TRIGGER PARA ACTUALIZAR STATUS AUTOMÁTICAMENTE
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_settlement_update_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Si amount_paid cambió, actualizar status automáticamente
    IF NEW.amount_paid IS DISTINCT FROM OLD.amount_paid THEN
        IF NEW.amount_paid <= 0 THEN
            NEW.status := 'pending';
            NEW.paid_at := NULL;
        ELSIF NEW.amount_paid >= NEW.net_amount THEN
            NEW.status := 'paid';
            IF NEW.paid_at IS NULL THEN
                NEW.paid_at := NOW();
            END IF;
        ELSE
            NEW.status := 'partial';
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_settlement_auto_status
    BEFORE UPDATE ON settlement
    FOR EACH ROW
    EXECUTE FUNCTION fn_settlement_update_status();

COMMENT ON FUNCTION fn_settlement_update_status IS 'Actualiza automáticamente el status según amount_paid vs net_amount.';

-- ============================================================================
-- PASO 6: VISTA MEJORADA DE LIQUIDACIONES
-- ============================================================================

CREATE OR REPLACE VIEW v_settlement AS
SELECT 
    s.id,
    s.period_start,
    s.period_end,
    
    -- Empleado (nuevo)
    er.id AS employee_role_id,
    e.id AS employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    cp.code AS collector_code,
    
    -- Legacy (para compatibilidad)
    s.collector_id,
    
    -- Comisiones
    s.commission_regular,
    s.commission_cash,
    s.commission_delivery,
    s.total_commissions,
    
    -- Deducciones
    s.deduction_fuel,
    s.deduction_loan,
    s.deduction_shortage,
    s.deduction_other,
    s.total_deductions,
    
    -- Montos
    s.net_amount,
    s.amount_paid,
    s.net_amount - s.amount_paid AS amount_remaining,
    
    -- Estado
    s.status,
    s.payment_method,
    s.paid_at,
    s.paid_by,
    
    -- Auditoría
    s.notes,
    s.created_at,
    s.updated_at
FROM settlement s
LEFT JOIN employee_role er ON s.employee_role_id = er.id
LEFT JOIN employee e ON er.employee_id = e.id
LEFT JOIN collector_profile cp ON er.id = cp.employee_role_id;

COMMENT ON VIEW v_settlement IS 'Vista de liquidaciones con datos de empleado resueltos.';

-- ============================================================================
-- PASO 7: VISTA DE PREVIEW DE LIQUIDACIÓN (para la app)
-- ============================================================================

CREATE OR REPLACE VIEW v_settlement_preview AS
SELECT 
    er.id AS employee_role_id,
    e.id AS employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    cp.code AS collector_code,
    cp.zone,
    
    -- Último período liquidado
    (SELECT MAX(period_end) FROM settlement WHERE employee_role_id = er.id) AS last_settlement_date,
    
    -- Préstamos activos
    (SELECT COUNT(*) FROM employee_loan WHERE employee_id = e.id AND status = 'active') AS active_loans,
    (SELECT COALESCE(SUM(installment_amount), 0) FROM employee_loan WHERE employee_id = e.id AND status = 'active') AS total_loan_installment
    
FROM employee_role er
JOIN employee e ON er.employee_id = e.id
JOIN collector_profile cp ON er.id = cp.employee_role_id
WHERE er.department = 'collection'
  AND er.is_active = TRUE;

COMMENT ON VIEW v_settlement_preview IS 'Vista para mostrar cobradores disponibles para liquidar.';

-- ============================================================================
-- PASO 8: FUNCIÓN PARA REGISTRAR PAGO DE LIQUIDACIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_pay_settlement(
    p_settlement_id INT,
    p_amount NUMERIC(12,2),
    p_method settlement_method_type,
    p_paid_by INT
) RETURNS settlement AS $$
DECLARE
    v_settlement settlement;
BEGIN
    UPDATE settlement
    SET amount_paid = amount_paid + p_amount,
        payment_method = p_method,
        paid_by = p_paid_by
    WHERE id = p_settlement_id
    RETURNING * INTO v_settlement;
    
    RETURN v_settlement;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_pay_settlement IS 'Registra un pago (parcial o total) en una liquidación.';

-- ============================================================================
-- PASO 9: AUDITORÍA
-- ============================================================================

-- El trigger de auditoría ya existe para settlement (003), 
-- pero agregamos para employee_loan si no existe

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_employee_loan_audit'
    ) THEN
        CREATE TRIGGER trg_employee_loan_audit
            AFTER INSERT OR UPDATE OR DELETE ON employee_loan
            FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();
    END IF;
END;
$$;

-- ============================================================================
-- NOTAS DE MIGRACIÓN DE DATOS
-- ============================================================================

-- Para migrar datos existentes de collector_id → employee_role_id:
--
-- 1. Primero ejecutar ETL que crea employees y employee_roles desde collectors
--
-- 2. Luego actualizar settlements:
--    UPDATE settlement s
--    SET employee_role_id = (
--        SELECT cp.employee_role_id 
--        FROM collector_profile cp
--        JOIN employee_role er ON cp.employee_role_id = er.id
--        JOIN v_collector vc ON vc.id = s.collector_id
--        WHERE cp.code = vc.code_name
--    )
--    WHERE employee_role_id IS NULL;
--
-- 3. Similar para employee_loan
--
-- 4. Una vez migrados todos los datos, se pueden dropear las columnas legacy:
--    ALTER TABLE settlement DROP COLUMN collector_id;
--    ALTER TABLE employee_loan DROP COLUMN collector_id;
--    ALTER TABLE employee_loan DROP COLUMN seller_id;

-- ============================================================================
-- FIN DE MIGRACIÓN
-- ============================================================================

-- Resumen de cambios:
--
-- ENUMs modificados:
--   - settlement_status_type: agregado 'partial'
--
-- Columnas agregadas:
--   - employee_loan.employee_id
--   - settlement.employee_role_id
--   - settlement.amount_paid
--
-- Funciones nuevas:
--   - fn_settlement_remaining(settlement_id)
--   - fn_settlement_update_status() [trigger]
--   - fn_pay_settlement(settlement_id, amount, method, paid_by)
--
-- Vistas nuevas:
--   - v_settlement (liquidaciones con datos de empleado)
--   - v_settlement_preview (cobradores disponibles para liquidar)
--
-- Triggers nuevos:
--   - trg_settlement_auto_status (actualiza status según amount_paid)
