# 11 - Modelos de Datos: Módulo Cobradores

**Fecha:** 2026-02-20
**Origen:** Sesión de diseño Fer + Claudy
**Estado:** En diseño ✏️
**Stack:** PostgreSQL 16 + PostGIS + SQLAlchemy (Alembic migrations)
**Convenciones:** snake_case, timestamps con timezone, soft delete donde aplique

---

## ÍNDICE

1. [Diagrama de Relaciones](#1-diagrama-de-relaciones)
2. [Tablas Nuevas](#2-tablas-nuevas)
3. [Modificaciones a Tablas Existentes](#3-modificaciones-a-tablas-existentes)
4. [Enums y Tipos](#4-enums-y-tipos)
5. [Índices y Performance](#5-índices-y-performance)
6. [Notas de Migración](#6-notas-de-migración)

---

## 1. DIAGRAMA DE RELACIONES

```
                    ┌──────────────┐
                    │   app_user   │ (existente, se extiende)
                    │──────────────│
                    │ id           │
                    │ role         │
                    │ + device_id  │
                    │ + fcm_token  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────────┐
              │            │                │
              ▼            ▼                ▼
     ┌────────────┐  ┌──────────┐   ┌─────────────┐
     │ collector  │  │ card     │   │ collection  │
     │ _assignment│  │(existente│   │ _proposal   │
     │            │  │ "tarjeta"│   │             │
     └─────┬──────┘  └────┬─────┘   └──────┬──────┘
           │               │                │
           │               │         ┌──────┴───────┐
           │               │         │              │
           ▼               ▼         ▼              ▼
     ┌──────────┐   ┌──────────┐ ┌────────┐ ┌───────────┐
     │  route   │   │  policy  │ │ visit  │ │  cash     │
     │  _plan   │   │(existente│ │ _notice│ │ _delivery │
     │          │   │)         │ │        │ │           │
     └────┬─────┘   └──────────┘ └────────┘ └───────────┘
          │
          ▼                        ┌──────────────┐
     ┌──────────┐                  │  collector   │
     │  route   │                  │  _debt       │
     │  _stop   │                  └──────────────┘
     └──────────┘
                                   ┌──────────────┐
     ┌──────────┐                  │  commission  │
     │collector │                  │  _rate       │
     │_location │                  └──────────────┘
     └──────────┘
                                   ┌──────────────┐
                                   │  notification│
                                   └──────────────┘

                                   ┌──────────────┐
                                   │  file_upload │
                                   └──────────────┘

                                   ┌──────────────┐
                                   │  device      │
                                   │  _session    │
                                   └──────────────┘
```

---

## 2. TABLAS NUEVAS

### 2.1 `collection_proposal` — Propuestas de cobro

La tabla central del módulo. Cada registro es un intento de cobro que requiere autorización.

```sql
CREATE TABLE collection_proposal (
    id                  SERIAL PRIMARY KEY,
    folio               INTEGER NOT NULL REFERENCES policy(folio),
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    payment_number      INTEGER NOT NULL,           -- Número de pago en el plan (1-7)
    
    -- Tipo de propuesta
    is_partial          BOOLEAN NOT NULL DEFAULT FALSE,
    partial_seq         INTEGER,                    -- 1, 2, 3... para abonos del mismo pago
    parent_proposal_id  INTEGER REFERENCES collection_proposal(id),  -- Si es reenvío de rechazada
    
    -- Datos del cobro
    amount              NUMERIC(12,2) NOT NULL,
    method              payment_method_enum NOT NULL,  -- efectivo, deposito, transferencia
    receipt_number      VARCHAR(20) NOT NULL,
    receipt_photo_id    INTEGER REFERENCES file_upload(id),
    
    -- Ubicación GPS
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    location_label      VARCHAR(200),               -- Geocodificación inversa (ej: "Tonalá, Jalisco")
    
    -- Estado y autorización
    status              proposal_status_enum NOT NULL DEFAULT 'pending',
    reviewed_by         INTEGER REFERENCES app_user(id),
    reviewed_at         TIMESTAMPTZ,
    rejection_reason    TEXT,
    
    -- Correcciones (si el gerente corrige y aprueba)
    corrected_fields    JSONB,                      -- {"amount": "1200.00", "receipt_number": "A00148"}
    correction_note     TEXT,
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_partial_seq CHECK (
        (is_partial = FALSE AND partial_seq IS NULL) OR
        (is_partial = TRUE AND partial_seq IS NOT NULL AND partial_seq > 0)
    ),
    CONSTRAINT chk_rejection_reason CHECK (
        (status != 'rejected') OR (rejection_reason IS NOT NULL AND rejection_reason != '')
    ),
    CONSTRAINT chk_amount_positive CHECK (amount > 0)
);

COMMENT ON TABLE collection_proposal IS 'Propuestas de cobro registradas por cobradores en campo, pendientes de autorización';
COMMENT ON COLUMN collection_proposal.partial_seq IS 'Secuencia del abono parcial. NULL si es cobro completo';
COMMENT ON COLUMN collection_proposal.corrected_fields IS 'JSON con campos corregidos por el gerente al usar CORREGIR Y APROBAR';
```

### 2.2 `visit_notice` — Avisos de visita

```sql
CREATE TABLE visit_notice (
    id                  SERIAL PRIMARY KEY,
    folio               INTEGER NOT NULL REFERENCES policy(folio),
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    payment_number      INTEGER NOT NULL,
    
    -- Motivo
    reason              visit_reason_enum NOT NULL,
    reason_detail       TEXT,                       -- Obligatorio si reason = 'other'
    
    -- Evidencia
    evidence_photo_id   INTEGER NOT NULL REFERENCES file_upload(id),
    
    -- Ubicación GPS
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_other_detail CHECK (
        reason != 'other' OR (reason_detail IS NOT NULL AND reason_detail != '')
    )
);

COMMENT ON TABLE visit_notice IS 'Avisos de visita cuando el cobrador acude pero no puede cobrar';
```

### 2.3 `cash_delivery` — Entregas de efectivo en oficina

```sql
CREATE TABLE cash_delivery (
    id                  SERIAL PRIMARY KEY,
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    
    -- Montos
    expected_amount     NUMERIC(12,2) NOT NULL,     -- Suma de propuestas aprobadas en efectivo
    received_amount     NUMERIC(12,2) NOT NULL,     -- Lo que se contó físicamente
    difference          NUMERIC(12,2) NOT NULL,     -- received - expected (negativo = deuda)
    
    -- Propuestas liquidadas
    proposal_ids        INTEGER[] NOT NULL,          -- Array de IDs de collection_proposal
    
    -- Quién confirmó
    confirmed_by        INTEGER NOT NULL REFERENCES app_user(id),
    confirmed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_self_confirm CHECK (collector_id != confirmed_by)
);

COMMENT ON TABLE cash_delivery IS 'Registro de entregas de efectivo del cobrador en oficina';
COMMENT ON COLUMN cash_delivery.difference IS 'Negativo = cobrador debe dinero. Positivo = cobrador entregó de más';
```

### 2.4 `collector_debt` — Deudas de cobradores

```sql
CREATE TABLE collector_debt (
    id                  SERIAL PRIMARY KEY,
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    cash_delivery_id    INTEGER REFERENCES cash_delivery(id),
    
    amount              NUMERIC(12,2) NOT NULL,
    description         TEXT NOT NULL,
    
    -- Resolución
    status              debt_status_enum NOT NULL DEFAULT 'pending',
    resolved_at         TIMESTAMPTZ,
    resolved_via        VARCHAR(50),                -- 'commission_deduction', 'cash_payment', 'forgiven'
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_amount_positive CHECK (amount > 0)
);

COMMENT ON TABLE collector_debt IS 'Deudas registradas a cobradores por diferencias de efectivo';
```

### 2.5 `collector_assignment` — Asignación de tarjetas a cobradores

```sql
CREATE TABLE collector_assignment (
    id                  SERIAL PRIMARY KEY,
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    folio               INTEGER NOT NULL REFERENCES policy(folio),
    
    assigned_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by         INTEGER REFERENCES app_user(id),
    unassigned_at       TIMESTAMPTZ,                -- NULL = activa
    
    CONSTRAINT uq_active_assignment UNIQUE (collector_id, folio)
);

COMMENT ON TABLE collector_assignment IS 'Qué pólizas/folios tiene asignados cada cobrador';
```

### 2.6 `route_plan` — Plan de ruta del día

```sql
CREATE TABLE route_plan (
    id                  SERIAL PRIMARY KEY,
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    date                DATE NOT NULL,
    
    -- Notificación WhatsApp
    notified_at         TIMESTAMPTZ,                -- NULL = no se ha notificado
    notified_count      INTEGER DEFAULT 0,          -- Cuántos clientes se notificaron
    
    -- Métricas
    total_stops         INTEGER NOT NULL DEFAULT 0,
    completed_stops     INTEGER NOT NULL DEFAULT 0,
    estimated_distance_km DOUBLE PRECISION,
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_collector_date UNIQUE (collector_id, date)
);

COMMENT ON TABLE route_plan IS 'Plan de ruta diario del cobrador';
```

### 2.7 `route_stop` — Paradas individuales de la ruta

```sql
CREATE TABLE route_stop (
    id                  SERIAL PRIMARY KEY,
    route_plan_id       INTEGER NOT NULL REFERENCES route_plan(id) ON DELETE CASCADE,
    folio               INTEGER NOT NULL REFERENCES policy(folio),
    
    stop_order          INTEGER NOT NULL,            -- Orden en la ruta (1, 2, 3...)
    status              route_stop_status_enum NOT NULL DEFAULT 'pending',
    
    -- Distancia calculada
    distance_from_prev_km DOUBLE PRECISION,
    
    -- Timestamps
    visited_at          TIMESTAMPTZ,                 -- Cuando se marcó como completada/skipped
    
    CONSTRAINT uq_route_stop UNIQUE (route_plan_id, folio)
);
```

### 2.8 `collector_location` — Tracking GPS pasivo

```sql
CREATE TABLE collector_location (
    id                  BIGSERIAL PRIMARY KEY,       -- BIGSERIAL porque puede crecer mucho
    collector_id        INTEGER NOT NULL REFERENCES app_user(id),
    
    lat                 DOUBLE PRECISION NOT NULL,
    lng                 DOUBLE PRECISION NOT NULL,
    accuracy_m          DOUBLE PRECISION,
    
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Particionado por mes para performance (tabla crece rápido)
-- Se implementa con herencia o particiones nativas PG 16
COMMENT ON TABLE collector_location IS 'Tracking GPS pasivo del cobrador durante ruta. Considerar particionado mensual';
```

### 2.9 `commission_rate` — Configuración de comisiones

```sql
CREATE TABLE commission_rate (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,       -- "Básico 10%", "Tiered Nivel 1", etc.
    mode                commission_mode_enum NOT NULL, -- 'flat', 'tiered'
    
    -- Modo flat
    flat_rate           NUMERIC(5,4),                -- 0.1000 = 10%
    
    -- Modo tiered (escalones en JSONB)
    tiers               JSONB,
    -- Ejemplo: [{"min": 0, "max": 10000, "rate": 0.08}, {"min": 10001, "max": null, "rate": 0.12}]
    
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from      DATE NOT NULL,
    effective_to        DATE,                        -- NULL = vigente indefinidamente
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE commission_rate IS 'Tablas de comisiones. Modo actual: flat 10%. Estructura flexible para escalar a tiered';
```

### 2.10 `notification` — Notificaciones in-app y push

```sql
CREATE TABLE notification (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES app_user(id),
    
    type                notification_type_enum NOT NULL,
    title               VARCHAR(200) NOT NULL,
    body                TEXT,
    
    -- Deep link
    action_url          VARCHAR(500),                -- Ruta interna de la app
    data                JSONB,                       -- Payload adicional (proposal_id, folio, etc.)
    
    -- Estado
    is_read             BOOLEAN NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMPTZ,
    
    -- Push
    push_sent           BOOLEAN NOT NULL DEFAULT FALSE,
    push_sent_at        TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.11 `device_session` — Dispositivos registrados

```sql
CREATE TABLE device_session (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES app_user(id),
    
    device_id           VARCHAR(200) NOT NULL,       -- ID único del dispositivo
    platform            VARCHAR(20) NOT NULL,        -- 'android', 'ios'
    fcm_token           TEXT,                        -- Firebase Cloud Messaging token
    
    -- Biometría
    biometric_enabled   BOOLEAN NOT NULL DEFAULT FALSE,
    biometric_token     TEXT,                        -- Hash para auth biométrica
    
    -- Metadata
    app_version         VARCHAR(20),
    last_active_at      TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_device UNIQUE (user_id, device_id)
);
```

### 2.12 `file_upload` — Archivos subidos (fotos de recibos, evidencias)

```sql
CREATE TABLE file_upload (
    id                  SERIAL PRIMARY KEY,
    
    uploaded_by         INTEGER NOT NULL REFERENCES app_user(id),
    
    filename            VARCHAR(500) NOT NULL,
    mime_type           VARCHAR(100) NOT NULL,
    size_bytes          INTEGER NOT NULL,
    storage_path        VARCHAR(1000) NOT NULL,      -- Ruta en disco o S3
    
    -- Contexto
    entity_type         VARCHAR(50),                 -- 'proposal_receipt', 'visit_evidence'
    entity_id           INTEGER,                     -- ID de la entidad relacionada
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE file_upload IS 'Registro de archivos subidos. Storage: local disk inicialmente, migrar a S3 cuando escale';
```

### 2.13 `receipt_sequence` — Secuencia de recibos digitales

```sql
CREATE TABLE receipt_sequence (
    id                  SERIAL PRIMARY KEY,
    prefix              CHAR(1) NOT NULL DEFAULT 'A',
    current_number      INTEGER NOT NULL DEFAULT 0,
    
    CONSTRAINT uq_prefix UNIQUE (prefix)
);

-- Función para generar el siguiente folio de recibo
CREATE OR REPLACE FUNCTION next_receipt_number()
RETURNS VARCHAR(6) AS $$
DECLARE
    next_num INTEGER;
    result VARCHAR(6);
BEGIN
    UPDATE receipt_sequence
    SET current_number = current_number + 1
    WHERE prefix = 'A'
    RETURNING current_number INTO next_num;
    
    result := 'A' || LPAD(next_num::TEXT, 5, '0');
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Seed inicial
INSERT INTO receipt_sequence (prefix, current_number) VALUES ('A', 0);

COMMENT ON TABLE receipt_sequence IS 'Numeración correlativa global de recibos digitales. Formato: A00001, A00002...';
```

### 2.14 `early_payment_discount` — Config de descuento por pronto pago

```sql
CREATE TABLE early_payment_discount (
    id                  SERIAL PRIMARY KEY,
    
    min_days_ahead      INTEGER NOT NULL DEFAULT 5,  -- Días de anticipación mínimos
    discount_percentage NUMERIC(5,4) NOT NULL,       -- 0.0500 = 5%
    applies_to_methods  payment_method_enum[] NOT NULL DEFAULT '{deposito,transferencia}',
    
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from      DATE NOT NULL,
    effective_to        DATE,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE early_payment_discount IS 'Configuración del descuento por pronto pago. Solo aplica a depósito/transferencia';
```

### 2.15 `cash_cap_config` — Config del tope de efectivo

```sql
CREATE TABLE cash_cap_config (
    id                  SERIAL PRIMARY KEY,
    
    cap_amount          NUMERIC(12,2) NOT NULL,      -- Ej: 5000.00
    warning_percentage  INTEGER NOT NULL DEFAULT 80,  -- Alerta al 80%
    block_at_cap        BOOLEAN NOT NULL DEFAULT FALSE, -- ¿Bloquear cobros al llegar?
    
    is_active           BOOLEAN NOT NULL DEFAULT FALSE, -- PENDIENTE aprobación Óscar/Elena
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE cash_cap_config IS 'Tope de efectivo acumulado. PENDIENTE de aprobación por dirección';
```

---

## 3. MODIFICACIONES A TABLAS EXISTENTES

### 3.1 `policy` (existente)

```sql
-- Agregar coordenadas para geocodificación
ALTER TABLE policy ADD COLUMN client_lat DOUBLE PRECISION;
ALTER TABLE policy ADD COLUMN client_lng DOUBLE PRECISION;
ALTER TABLE policy ADD COLUMN geocode_source VARCHAR(20);
-- 'nominatim' = batch ETL, 'collector_gps' = pasivo por cobrador, 'manual' = captura manual

-- Índice espacial (requiere PostGIS)
CREATE INDEX idx_policy_location ON policy USING GIST (
    ST_MakePoint(client_lng, client_lat)
) WHERE client_lat IS NOT NULL;
```

### 3.2 `payment` (existente)

```sql
-- Campos nuevos para soportar abonos parciales
ALTER TABLE payment ADD COLUMN is_partial BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE payment ADD COLUMN partial_seq INTEGER;
ALTER TABLE payment ADD COLUMN parent_payment_id INTEGER REFERENCES payment(id);

-- Referencia a la propuesta que originó este pago
ALTER TABLE payment ADD COLUMN proposal_id INTEGER REFERENCES collection_proposal(id);

-- Folio del recibo digital
ALTER TABLE payment ADD COLUMN receipt_number VARCHAR(20);

-- Descuento aplicado
ALTER TABLE payment ADD COLUMN discount_amount NUMERIC(12,2) DEFAULT 0;
ALTER TABLE payment ADD COLUMN discount_reason VARCHAR(100);
```

### 3.3 `app_user` (existente)

```sql
-- Campos para cobradores
ALTER TABLE app_user ADD COLUMN commission_rate_id INTEGER REFERENCES commission_rate(id);
ALTER TABLE app_user ADD COLUMN is_collector BOOLEAN NOT NULL DEFAULT FALSE;
```

---

## 4. ENUMS Y TIPOS

```sql
-- Métodos de pago
CREATE TYPE payment_method_enum AS ENUM (
    'efectivo',
    'deposito',
    'transferencia'
);

-- Estado de propuesta
CREATE TYPE proposal_status_enum AS ENUM (
    'pending',        -- Enviada por cobrador, esperando revisión
    'approved',       -- Aprobada por gerente
    'corrected',      -- Corregida y aprobada por gerente
    'rejected'        -- Rechazada por gerente
);

-- Motivo de aviso de visita
CREATE TYPE visit_reason_enum AS ENUM (
    'client_absent',      -- Cliente no estaba
    'no_cash',            -- No tenía efectivo
    'will_pay_later',     -- Pagará después
    'other'               -- Otro (requiere detalle)
);

-- Estado de parada de ruta
CREATE TYPE route_stop_status_enum AS ENUM (
    'pending',        -- Por visitar
    'next',           -- Siguiente en la ruta
    'completed',      -- Visitado (cobro o aviso registrado)
    'skipped'         -- Saltado por el cobrador
);

-- Modo de comisiones
CREATE TYPE commission_mode_enum AS ENUM (
    'flat',           -- Porcentaje fijo (actual: 10%)
    'tiered'          -- Escalonado por volumen
);

-- Estado de deuda
CREATE TYPE debt_status_enum AS ENUM (
    'pending',                -- Activa
    'deducted_from_commission', -- Descontada de comisión
    'paid_cash',              -- Pagada en efectivo
    'forgiven'                -- Perdonada
);

-- Tipos de notificación
CREATE TYPE notification_type_enum AS ENUM (
    'proposal_approved',
    'proposal_rejected',
    'proposal_corrected',
    'folio_assigned',
    'route_ready',
    'cash_warning',
    'cash_blocked',
    'proposal_pending',       -- Para gerente
    'cash_delivery',          -- Para gerente
    'debt_registered'         -- Para cobrador
);
```

---

## 5. ÍNDICES Y PERFORMANCE

```sql
-- ============================================
-- COLLECTION_PROPOSAL
-- ============================================

-- Búsqueda por cobrador + fecha (pantalla "Mis propuestas del día")
CREATE INDEX idx_proposal_collector_date
ON collection_proposal (collector_id, created_at DESC);

-- Búsqueda por estado (pantalla gerente "Propuestas pendientes")
CREATE INDEX idx_proposal_status
ON collection_proposal (status) WHERE status = 'pending';

-- Búsqueda por folio (evitar duplicados)
CREATE INDEX idx_proposal_folio_date
ON collection_proposal (folio, (created_at::DATE));

-- Receipt number único (validación de recibos duplicados)
CREATE UNIQUE INDEX idx_proposal_receipt_unique
ON collection_proposal (receipt_number)
WHERE status IN ('pending', 'approved', 'corrected');

-- ============================================
-- VISIT_NOTICE
-- ============================================
CREATE INDEX idx_visit_collector_date
ON visit_notice (collector_id, created_at DESC);

-- ============================================
-- CASH_DELIVERY
-- ============================================
CREATE INDEX idx_cash_delivery_collector
ON cash_delivery (collector_id, confirmed_at DESC);

-- ============================================
-- COLLECTOR_DEBT
-- ============================================
CREATE INDEX idx_debt_collector_status
ON collector_debt (collector_id, status) WHERE status = 'pending';

-- ============================================
-- NOTIFICATION
-- ============================================
CREATE INDEX idx_notification_user_unread
ON notification (user_id, created_at DESC) WHERE is_read = FALSE;

-- ============================================
-- COLLECTOR_LOCATION (tabla grande — índice mínimo)
-- ============================================
CREATE INDEX idx_location_collector_time
ON collector_location (collector_id, recorded_at DESC);

-- ============================================
-- COLLECTOR_ASSIGNMENT
-- ============================================
CREATE INDEX idx_assignment_collector_active
ON collector_assignment (collector_id) WHERE unassigned_at IS NULL;

-- ============================================
-- ROUTE
-- ============================================
CREATE INDEX idx_route_collector_date
ON route_plan (collector_id, date);
```

---

## 6. NOTAS DE MIGRACIÓN

### Orden de creación
Las migraciones deben ejecutarse en este orden por dependencias:

1. **Enums** (todos los CREATE TYPE)
2. **file_upload** (sin dependencias)
3. **receipt_sequence** (sin dependencias)
4. **Alteraciones a tablas existentes** (app_user, policy, payment)
5. **commission_rate** (referenciada por app_user)
6. **collection_proposal** (depende de policy, app_user, file_upload)
7. **visit_notice** (depende de policy, app_user, file_upload)
8. **cash_delivery** (depende de app_user)
9. **collector_debt** (depende de app_user, cash_delivery)
10. **collector_assignment** (depende de app_user, policy)
11. **route_plan** (depende de app_user)
12. **route_stop** (depende de route_plan, policy)
13. **collector_location** (depende de app_user)
14. **notification** (depende de app_user)
15. **device_session** (depende de app_user)
16. **cash_cap_config** (sin dependencias)
17. **early_payment_discount** (sin dependencias)
18. **Índices** (todos al final)

### Seed data

```sql
-- Comisión inicial: 10% flat
INSERT INTO commission_rate (name, mode, flat_rate, is_active, effective_from)
VALUES ('Básico 10%', 'flat', 0.1000, TRUE, '2026-01-01');

-- Tope de efectivo (inactivo por defecto — pendiente de aprobación)
INSERT INTO cash_cap_config (cap_amount, warning_percentage, block_at_cap, is_active)
VALUES (5000.00, 80, FALSE, FALSE);

-- Secuencia de recibos
INSERT INTO receipt_sequence (prefix, current_number) VALUES ('A', 0);
```

### Consideraciones

- **PostGIS:** Necesario para el índice espacial de geocodificación. Instalar extensión: `CREATE EXTENSION IF NOT EXISTS postgis;`
- **Particionado:** `collector_location` crecerá rápido (1 registro cada 5 min × N cobradores). Evaluar particionado mensual cuando supere 1M filas.
- **Backup:** Las tablas de propuestas y entregas de efectivo son críticas para auditoría. Incluir en backup diario.
- **Soft delete:** No se implementa en este módulo. Las propuestas rechazadas se mantienen en historial con su status, nunca se borran.

---

## APÉNDICE: RESUMEN DE TABLAS

| # | Tabla | Registros estimados/mes | Crítica |
|---|-------|------------------------|---------|
| 1 | `collection_proposal` | ~500-1000 | ⭐ Sí |
| 2 | `visit_notice` | ~200-400 | |
| 3 | `cash_delivery` | ~60-100 | ⭐ Sí |
| 4 | `collector_debt` | ~5-20 | |
| 5 | `collector_assignment` | ~200 (estática) | |
| 6 | `route_plan` | ~60-100 | |
| 7 | `route_stop` | ~600-1200 | |
| 8 | `collector_location` | ~10,000-50,000 | ⚠️ Grande |
| 9 | `commission_rate` | ~1-5 (config) | |
| 10 | `notification` | ~2000-5000 | |
| 11 | `device_session` | ~10-20 (estática) | |
| 12 | `file_upload` | ~500-1000 | |
| 13 | `receipt_sequence` | 1 (singleton) | |
| 14 | `early_payment_discount` | ~1-3 (config) | |
| 15 | `cash_cap_config` | 1 (singleton) | |

**Total: 15 tablas nuevas + 3 modificaciones a existentes**

---

*Documento generado en sesión Fer + Claudy — 2026-02-20*
*Siguiente paso: Definir las migraciones Alembic y comenzar implementación del backend*
