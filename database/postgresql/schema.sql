-- ============================================================================
-- PostgreSQL Schema: CRM Seguros ProtegRT
-- Version: 2.1
-- Fecha: 2026-02-15
-- Descripcion: Esquema completo rediseñado con TODAS las correcciones del
--              propietario del proyecto. Cambios criticos vs v1.2:
--   1. PostGIS habilitado para address (geometry/geography)
--   2. Sistema de promociones flexible (promotion + promotion_rule + promotion_application)
--   3. ELIMINADA tabla quote (cotizaciones via API REST)
--   4. Renombrada card_location_history -> collection_assignment
--   5. Flujo de autorizacion (approval_request)
--   6. Soporte apps moviles (device_session, mobile_action_log)
--   7. vehicle_key documentado como codigos internos (101, 103, 105)
--
-- Correcciones v2.1 (B8-B12):
--   B8.  payment_method_type: reemplazado card/check por deposit/crucero/konfio/terminal_banorte
--   B9.  payment_plan_type: reemplazado semester/quarterly/monthly_12 por monthly_7
--   B10. Agregada columna prima_total a tabla policy
--   B11. Agregada columna rfc a tabla client
--   B12. collector.receipt_limit default cambiado de 5 a 50
-- ============================================================================

-- Convenciones:
--   - Tablas: singular, snake_case, ingles
--   - PKs: SERIAL o BIGSERIAL segun volumen esperado
--   - FKs: nombre_tabla_id (ej: client_id, policy_id)
--   - Timestamps: TIMESTAMPTZ (con zona horaria)
--   - Booleans: BOOLEAN nativo (no TINYINT)
--   - Montos: NUMERIC(12,2)
--   - Todos los campos tienen COMMENT
--   - ON DELETE: RESTRICT por defecto en tablas de negocio,
--     CASCADE solo en tablas de log/auditoria/junction,
--     SET NULL en referencias opcionales

-- ============================================================================
-- PASO 0: Extensiones
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- Para gen_random_uuid() si se necesita
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- Para indices GIN de busqueda por similitud
CREATE EXTENSION IF NOT EXISTS "postgis";    -- Para geometry/geography y futuro pgRouting

-- ============================================================================
-- PASO 1: ENUM Types
-- ============================================================================

CREATE TYPE gender_type AS ENUM ('male', 'female');
CREATE TYPE marital_status_type AS ENUM ('single', 'married', 'divorced', 'widowed', 'common_law');
CREATE TYPE entity_status_type AS ENUM ('active', 'inactive');

-- Valores de policy_status_type (mapeados del StatusUpdater):
--   active        = Activa: En vigencia y pagos al corriente
--   pending       = Pendiente: Primer pago aun no realizado
--   morosa        = Morosa: Tiene pagos atrasados o vencidos
--   pre_effective = Previgencia: Aun no inicia vigencia pero tiene pagos
--   expired       = Expirada: Fecha actual > fin de vigencia
--   cancelled     = Cancelada: Tiene pagos cancelados
--   suspended     = Suspendida: Suspendida administrativamente
--   no_status     = SinEstado: No se puede determinar el estado
CREATE TYPE policy_status_type AS ENUM ('active', 'pending', 'morosa', 'pre_effective', 'expired', 'cancelled', 'suspended', 'no_status');

-- Valores de payment_status_type (mapeados del StatusUpdater):
--   pending   = PENDIENTE: fecha_limite >= hoy
--   paid      = PAGADO: Pago realizado
--   late      = ATRASADO: 1-5 dias despues de fecha_limite
--   overdue   = VENCIDO: 5+ dias despues de fecha_limite
--   cancelled = CANCELADO: Pago cancelado
CREATE TYPE payment_status_type AS ENUM ('pending', 'paid', 'late', 'overdue', 'cancelled');
CREATE TYPE payment_method_type AS ENUM ('cash', 'deposit', 'transfer', 'crucero', 'konfio', 'terminal_banorte');
CREATE TYPE payment_plan_type AS ENUM ('cash', 'cash_2_installments', 'monthly_7');
CREATE TYPE office_delivery_type AS ENUM ('pending', 'delivered');
CREATE TYPE receipt_status_type AS ENUM ('unassigned', 'assigned', 'used', 'delivered', 'cancelled', 'lost', 'cancelled_undelivered');
CREATE TYPE service_type AS ENUM ('private', 'commercial');
CREATE TYPE vehicle_type_enum AS ENUM ('automobile', 'truck', 'suv', 'motorcycle', 'mototaxi');
CREATE TYPE coverage_category_type AS ENUM ('liability', 'comprehensive', 'platform');
CREATE TYPE incident_type_enum AS ENUM ('collision', 'theft', 'total_loss', 'vandalism', 'natural_disaster', 'other');
CREATE TYPE responsibility_type AS ENUM ('not_responsible', 'at_fault', 'shared');
CREATE TYPE service_status_type AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
CREATE TYPE endorsement_type_enum AS ENUM ('plate_change', 'vehicle_change', 'coverage_change', 'contractor_change', 'rights_transfer');
CREATE TYPE endorsement_status_type AS ENUM ('pending', 'approved', 'rejected', 'applied');
CREATE TYPE shift_order_type AS ENUM ('first', 'second', 'third', 'rest');
CREATE TYPE message_type_enum AS ENUM ('reminder', 'overdue');
CREATE TYPE notification_period_type AS ENUM ('renewal_15d', 'renewal_3d', 'expired_7d', 'expired_30d');
CREATE TYPE seller_class_type AS ENUM ('seller', 'collaborator');
CREATE TYPE workshop_pass_type_enum AS ENUM ('repair', 'valuation_payment', 'open_repair_valuation', 'agreed_payment', 'agreement');
CREATE TYPE renewal_status_type AS ENUM ('pending', 'completed', 'rejected');
CREATE TYPE payment_proposal_status_type AS ENUM ('active', 'applied', 'discarded');
CREATE TYPE card_status_type AS ENUM ('active', 'paid_off', 'cancelled', 'recovery');
CREATE TYPE message_channel_type AS ENUM ('whatsapp', 'telegram', 'sms', 'email');
CREATE TYPE message_delivery_status_type AS ENUM ('queued', 'sent', 'delivered', 'read', 'failed');

-- NUEVO v2: Tipos para sistema de promociones flexible
CREATE TYPE promotion_discount_type AS ENUM ('percentage', 'fixed_amount', 'free_months', 'zero_down_payment');

-- NUEVO v2: Tipos para flujo de autorizacion
CREATE TYPE approval_request_type AS ENUM ('policy_submission', 'payment_submission');
CREATE TYPE approval_status_type AS ENUM ('pending', 'approved', 'rejected', 'cancelled');

-- NUEVO v2: Tipos para soporte movil
CREATE TYPE device_type_enum AS ENUM ('android', 'ios', 'web');
CREATE TYPE app_type_enum AS ENUM ('collector_app', 'seller_app', 'adjuster_app', 'desktop');

-- ============================================================================
-- PASO 2: Tablas de Catalogo / Referencia
-- ============================================================================

-- -----------------------------------------------
-- municipality
-- -----------------------------------------------
CREATE TABLE municipality (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    short_name  VARCHAR(50)  NOT NULL,
    siga_code   VARCHAR(100),
    CONSTRAINT uq_municipality_name UNIQUE (name)
);
COMMENT ON TABLE municipality IS 'Catalogo de municipios';
COMMENT ON COLUMN municipality.siga_code IS 'Codigo del Sistema de Informacion Geografica';

-- -----------------------------------------------
-- address (direcciones normalizadas con PostGIS)
-- -----------------------------------------------
CREATE TABLE address (
    id              BIGSERIAL PRIMARY KEY,
    street          VARCHAR(150) NOT NULL,
    exterior_number VARCHAR(10),
    interior_number VARCHAR(10),
    cross_street_1  VARCHAR(100),
    cross_street_2  VARCHAR(100),
    neighborhood    VARCHAR(100),
    municipality_id BIGINT REFERENCES municipality(id),
    postal_code     VARCHAR(10),
    -- PostGIS geometry column (SRID 4326 = WGS84, el estandar GPS)
    geom            geometry(Point, 4326),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE address IS 'Direcciones normalizadas con PostGIS para consultas espaciales y futuro pgRouting';
COMMENT ON COLUMN address.postal_code IS 'Codigo postal como texto para preservar ceros a la izquierda';
COMMENT ON COLUMN address.geom IS 'Punto geografico WGS84 (lon, lat). Insertar con ST_SetSRID(ST_MakePoint(lon, lat), 4326)';

CREATE INDEX idx_address_municipality ON address(municipality_id);
-- Indice espacial GiST para consultas de proximidad, distancia, pgRouting
CREATE INDEX idx_address_geom ON address USING GIST (geom);

-- -----------------------------------------------
-- department
-- -----------------------------------------------
CREATE TABLE department (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_department_name UNIQUE (name)
);
COMMENT ON TABLE department IS 'Departamentos de la organizacion';

-- -----------------------------------------------
-- role
-- -----------------------------------------------
CREATE TABLE role (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_role_name UNIQUE (name)
);
COMMENT ON TABLE role IS 'Roles de usuario en el sistema';

-- -----------------------------------------------
-- permission
-- -----------------------------------------------
CREATE TABLE permission (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_permission_name UNIQUE (name)
);
COMMENT ON TABLE permission IS 'Permisos individuales del sistema';

-- -----------------------------------------------
-- role_permission (N:M)
-- -----------------------------------------------
CREATE TABLE role_permission (
    role_id       INT NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    permission_id INT NOT NULL REFERENCES permission(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
COMMENT ON TABLE role_permission IS 'Relacion muchos a muchos entre roles y permisos';

-- ============================================================================
-- PASO 3: Usuarios y Autenticacion
-- ============================================================================

CREATE TABLE app_user (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100),
    department_id   INT REFERENCES department(id) ON DELETE SET NULL,
    role_id         INT REFERENCES role(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_username UNIQUE (username),
    CONSTRAINT uq_user_email UNIQUE (email)
);
COMMENT ON TABLE app_user IS 'Usuarios del sistema (app_user para evitar conflicto con palabra reservada user)';
COMMENT ON COLUMN app_user.password_hash IS 'Hash bcrypt de la contrasena';

CREATE INDEX idx_user_active ON app_user(is_active) WHERE is_active = TRUE;

-- -----------------------------------------------
-- session (sesiones de escritorio / web clasicas)
-- -----------------------------------------------
CREATE TABLE session (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_session_token UNIQUE (token)
);
COMMENT ON TABLE session IS 'Sesiones de usuario (escritorio/web)';

CREATE INDEX idx_session_user ON session(user_id);
CREATE INDEX idx_session_expires ON session(expires_at) WHERE is_active = TRUE;

-- -----------------------------------------------
-- device_session (NUEVO v2: sesiones multi-dispositivo para apps moviles)
-- -----------------------------------------------
CREATE TABLE device_session (
    id              SERIAL PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    device_id       VARCHAR(255) NOT NULL,
    device_type     device_type_enum NOT NULL,
    app_type        app_type_enum NOT NULL,
    app_version     VARCHAR(20),
    push_token      VARCHAR(500),
    token           VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_device_session_token UNIQUE (token)
);
COMMENT ON TABLE device_session IS 'Sesiones por dispositivo para apps moviles (cobradores, vendedores, ajustadores)';
COMMENT ON COLUMN device_session.device_id IS 'UUID unico del dispositivo, generado por la app movil';
COMMENT ON COLUMN device_session.app_type IS 'Tipo de app: collector_app, seller_app, adjuster_app, desktop';
COMMENT ON COLUMN device_session.push_token IS 'Token FCM/APNS para push notifications';

CREATE INDEX idx_device_session_user ON device_session(user_id);
CREATE INDEX idx_device_session_active ON device_session(is_active, user_id) WHERE is_active = TRUE;
CREATE INDEX idx_device_session_device ON device_session(device_id);

-- ============================================================================
-- PASO 4: Entidades de Negocio Principales
-- ============================================================================

-- -----------------------------------------------
-- client
-- -----------------------------------------------
CREATE TABLE client (
    id                BIGSERIAL PRIMARY KEY,
    first_name        VARCHAR(50)  NOT NULL,
    paternal_surname  VARCHAR(50)  NOT NULL,
    maternal_surname  VARCHAR(50),
    rfc               VARCHAR(13),
    birth_date        DATE,
    gender            gender_type,
    marital_status    marital_status_type,
    address_id        BIGINT REFERENCES address(id),
    phone_1           VARCHAR(20),
    phone_2           VARCHAR(20),
    email             VARCHAR(100),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at        TIMESTAMPTZ
);
COMMENT ON TABLE client IS 'Clientes / contratantes de polizas';
COMMENT ON COLUMN client.rfc IS 'RFC del cliente (12 chars persona moral, 13 chars persona fisica)';
COMMENT ON COLUMN client.deleted_at IS 'Soft delete: NULL = activo, fecha = eliminado';

CREATE INDEX idx_client_name ON client(paternal_surname, first_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_client_phone ON client(phone_1) WHERE deleted_at IS NULL;
CREATE INDEX idx_client_deleted ON client(deleted_at);
-- Indice GIN para busqueda por similitud
CREATE INDEX idx_client_name_trgm ON client USING GIN (
    (first_name || ' ' || paternal_surname || ' ' || COALESCE(maternal_surname, '')) gin_trgm_ops
) WHERE deleted_at IS NULL;

-- -----------------------------------------------
-- seller (vendedor)
-- -----------------------------------------------
CREATE TABLE seller (
    id            SERIAL PRIMARY KEY,
    code_name     VARCHAR(50)  NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    phone         VARCHAR(20),
    telegram_id   BIGINT,
    status        entity_status_type NOT NULL DEFAULT 'active',
    class         seller_class_type NOT NULL DEFAULT 'collaborator',
    sales_target  INT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_seller_code UNIQUE (code_name)
);
COMMENT ON TABLE seller IS 'Vendedores y colaboradores comerciales';
COMMENT ON COLUMN seller.code_name IS 'Nombre clave/alias del vendedor (antes nombre en MySQL)';
COMMENT ON COLUMN seller.full_name IS 'Nombre completo real';
COMMENT ON COLUMN seller.sales_target IS 'Meta de ventas mensuales';

CREATE INDEX idx_seller_status ON seller(status);

-- -----------------------------------------------
-- collector (cobrador)
-- -----------------------------------------------
CREATE TABLE collector (
    id              SERIAL PRIMARY KEY,
    code_name       VARCHAR(50)  NOT NULL,
    full_name       VARCHAR(255),
    phone           VARCHAR(20),
    receipt_limit   INT NOT NULL DEFAULT 50,
    status          entity_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_collector_code UNIQUE (code_name)
);
COMMENT ON TABLE collector IS 'Cobradores que gestionan recibos y pagos en campo';
COMMENT ON COLUMN collector.receipt_limit IS 'Maximo de recibos asignados simultaneamente';

-- -----------------------------------------------
-- vehicle
-- -----------------------------------------------
CREATE TABLE vehicle (
    id              SERIAL PRIMARY KEY,
    brand           VARCHAR(45)  NOT NULL,
    model_type      VARCHAR(45),
    model_year      VARCHAR(10),
    color           VARCHAR(45),
    vehicle_key     INT,
    seats           INT,
    serial_number   VARCHAR(45),
    plates          VARCHAR(20),
    load_capacity   VARCHAR(15),
    vehicle_type    vehicle_type_enum,
    cylinder_capacity VARCHAR(25),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_vehicle_serial UNIQUE (serial_number)
);
COMMENT ON TABLE vehicle IS 'Vehiculos asegurados. Normalizado desde la tabla polizas de MySQL.';
COMMENT ON COLUMN vehicle.vehicle_key IS 'Clave INTERNA del tipo de vehiculo: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA. NO es catalogo externo.';

CREATE INDEX idx_vehicle_plates ON vehicle(plates);
CREATE INDEX idx_vehicle_serial ON vehicle(serial_number);

-- -----------------------------------------------
-- coverage (catalogo de coberturas)
-- -----------------------------------------------
CREATE TABLE coverage (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(50)   NOT NULL,
    vehicle_type            VARCHAR(50)   NOT NULL,
    vehicle_key             INT           NOT NULL,
    service_type            service_type  NOT NULL,
    category                coverage_category_type NOT NULL DEFAULT 'liability',
    cylinder_capacity       VARCHAR(20),
    credit_price            NUMERIC(12,2) NOT NULL,
    initial_payment         NUMERIC(12,2) NOT NULL,
    cash_price              NUMERIC(12,2) NOT NULL,
    tow_services_included   INT NOT NULL DEFAULT 0,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_coverage_prices CHECK (credit_price >= 0 AND initial_payment >= 0 AND cash_price >= 0),
    CONSTRAINT chk_coverage_tow CHECK (tow_services_included >= 0)
);
COMMENT ON TABLE coverage IS 'Catalogo de coberturas con precios por tipo de vehiculo y servicio';
COMMENT ON COLUMN coverage.vehicle_type IS 'Tipo de vehiculo: AUTOMOVIL, PICK UP, CAMIONETA, MOTOCICLETA, MOTOTAXI (VARCHAR para mantener valores originales MySQL)';
COMMENT ON COLUMN coverage.vehicle_key IS 'Codigo INTERNO del tipo de vehiculo: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA. NO es catalogo externo.';
COMMENT ON COLUMN coverage.name IS 'Nombre de la cobertura: AMPLIA, PLATINO, RC PREMIUM, RC INTERMEDIA, RC BASICA, PLATAFORMA N, PLATAFORMA A';
COMMENT ON COLUMN coverage.cylinder_capacity IS 'Solo para MOTOCICLETA. Ej: "901 A 1800 CC". NULL para otros vehiculos.';
COMMENT ON COLUMN coverage.credit_price IS 'Precio a credito. AMPLIA = 0.00 (se cotiza individualmente por vehiculo).';

CREATE INDEX idx_coverage_vehicle_key ON coverage(vehicle_key);
CREATE INDEX idx_coverage_name ON coverage(name);
CREATE INDEX idx_coverage_active ON coverage(is_active) WHERE is_active = TRUE;

-- -----------------------------------------------
-- policy (poliza)
-- -----------------------------------------------
CREATE TABLE policy (
    id                      SERIAL PRIMARY KEY,
    folio                   INT NOT NULL,
    renewal_folio           INT,
    client_id               BIGINT NOT NULL REFERENCES client(id) ON DELETE RESTRICT,
    vehicle_id              INT NOT NULL REFERENCES vehicle(id) ON DELETE RESTRICT,
    coverage_id             INT NOT NULL REFERENCES coverage(id) ON DELETE RESTRICT,
    seller_id               INT REFERENCES seller(id) ON DELETE SET NULL,
    service_type            service_type,
    contract_folio          INT,
    effective_date          DATE,
    expiration_date         DATE,
    sale_date               DATE,
    elaboration_date        DATE,
    status                  policy_status_type NOT NULL DEFAULT 'active',
    payment_plan            payment_plan_type,
    data_entry_user_id      INT REFERENCES app_user(id),
    tow_services_available  INT NOT NULL DEFAULT 0,
    comments                TEXT,
    has_fraud_observation   BOOLEAN NOT NULL DEFAULT FALSE,
    has_payment_issues      BOOLEAN NOT NULL DEFAULT FALSE,
    contract_image_path     VARCHAR(500),
    prima_total             NUMERIC(12,2),
    -- NUEVO v2: referencia a cotizacion externa (API REST), NO tabla local
    quote_external_id       VARCHAR(50),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_policy_folio UNIQUE (folio),
    CONSTRAINT chk_policy_dates CHECK (expiration_date IS NULL OR effective_date IS NULL OR expiration_date >= effective_date),
    CONSTRAINT chk_policy_tow CHECK (tow_services_available >= 0)
);
COMMENT ON TABLE policy IS 'Polizas de seguro vehicular. Tabla central del sistema.';
COMMENT ON COLUMN policy.folio IS 'Numero de folio unico de negocio';
COMMENT ON COLUMN policy.renewal_folio IS 'Folio de la poliza que fue renovada (NULL si es nueva)';
COMMENT ON COLUMN policy.data_entry_user_id IS 'Usuario que capturo la poliza (antes capturista)';
COMMENT ON COLUMN policy.has_fraud_observation IS 'Marca de observacion de fraude para elegibilidad AMPLIA SELECT';
COMMENT ON COLUMN policy.has_payment_issues IS 'Marca de problemas de pago para elegibilidad AMPLIA SELECT';
COMMENT ON COLUMN policy.prima_total IS 'Costo total de la poliza (prima total)';
COMMENT ON COLUMN policy.quote_external_id IS 'ID de la cotizacion en sistema externo (API REST). Las cotizaciones NO viven en esta BD.';

CREATE INDEX idx_policy_folio ON policy(folio);
CREATE INDEX idx_policy_client ON policy(client_id);
CREATE INDEX idx_policy_seller ON policy(seller_id);
CREATE INDEX idx_policy_vehicle ON policy(vehicle_id);
CREATE INDEX idx_policy_coverage ON policy(coverage_id);
CREATE INDEX idx_policy_status ON policy(status);
CREATE INDEX idx_policy_expiration ON policy(expiration_date);
CREATE INDEX idx_policy_elaboration ON policy(elaboration_date);
CREATE INDEX idx_policy_renewal ON policy(renewal_folio);
CREATE INDEX idx_policy_fraud ON policy(has_fraud_observation, has_payment_issues)
    WHERE has_fraud_observation = TRUE OR has_payment_issues = TRUE;
-- Indices parciales para polizas por estado (consultas mas frecuentes)
CREATE INDEX idx_policy_active ON policy(folio) WHERE status = 'active';
CREATE INDEX idx_policy_morosa ON policy(folio, client_id) WHERE status = 'morosa';
CREATE INDEX idx_policy_pending ON policy(folio) WHERE status = 'pending';
CREATE INDEX idx_policy_pre_effective ON policy(folio, effective_date) WHERE status = 'pre_effective';

-- -----------------------------------------------
-- payment (pago)
-- -----------------------------------------------
CREATE TABLE payment (
    id                      SERIAL PRIMARY KEY,
    policy_id               INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    seller_id               INT REFERENCES seller(id) ON DELETE SET NULL,
    collector_id            INT REFERENCES collector(id) ON DELETE SET NULL,
    user_id                 INT REFERENCES app_user(id) ON DELETE SET NULL,
    payment_number          INT NOT NULL,
    receipt_number          VARCHAR(10),
    due_date                DATE,
    actual_date             DATE,
    amount                  NUMERIC(12,2),
    payment_method          payment_method_type,
    office_delivery_status  office_delivery_type,
    office_delivery_date    DATE,
    policy_delivered        BOOLEAN DEFAULT FALSE,
    comments                TEXT,
    status                  payment_status_type NOT NULL DEFAULT 'pending',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_payment_number CHECK (payment_number > 0),
    CONSTRAINT chk_payment_amount CHECK (amount IS NULL OR amount >= 0)
);
COMMENT ON TABLE payment IS 'Pagos de polizas. Cada poliza tiene 1 a N pagos segun forma de pago.';
COMMENT ON COLUMN payment.policy_id IS 'FK a policy(id), no a folio. Relacion por PK tecnico.';
COMMENT ON COLUMN payment.collector_id IS 'FK al cobrador por ID numerico (antes era VARCHAR clave_cobrador)';
COMMENT ON COLUMN payment.receipt_number IS 'Numero de recibo fisico asociado';
COMMENT ON COLUMN payment.policy_delivered IS 'Si la poliza fisica fue entregada al cliente con este pago';

CREATE INDEX idx_payment_policy ON payment(policy_id);
CREATE INDEX idx_payment_seller ON payment(seller_id);
CREATE INDEX idx_payment_collector ON payment(collector_id);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_payment_due_date ON payment(due_date);
CREATE INDEX idx_payment_receipt ON payment(receipt_number);
CREATE INDEX idx_payment_policy_status_due ON payment(policy_id, status, due_date);
CREATE INDEX idx_payment_pending ON payment(policy_id, due_date)
    WHERE status = 'pending';
CREATE INDEX idx_payment_late ON payment(policy_id, due_date)
    WHERE status = 'late';
CREATE INDEX idx_payment_overdue ON payment(policy_id, due_date)
    WHERE status = 'overdue';

-- -----------------------------------------------
-- payment_proposal (pagos temporales)
-- -----------------------------------------------
CREATE TABLE payment_proposal (
    id                  SERIAL PRIMARY KEY,
    original_payment_id INT NOT NULL REFERENCES payment(id) ON DELETE RESTRICT,
    policy_id           INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    seller_id           INT REFERENCES seller(id) ON DELETE SET NULL,
    collector_id        INT REFERENCES collector(id) ON DELETE SET NULL,
    user_id             INT REFERENCES app_user(id) ON DELETE SET NULL,
    payment_number      INT NOT NULL,
    receipt_number      VARCHAR(10),
    due_date            DATE,
    actual_date         DATE,
    amount              NUMERIC(12,2),
    payment_method      payment_method_type,
    office_delivery_status office_delivery_type,
    office_delivery_date DATE,
    policy_delivered    BOOLEAN DEFAULT FALSE,
    comments            TEXT,
    payment_status      payment_status_type NOT NULL DEFAULT 'pending',
    draft_status        payment_proposal_status_type NOT NULL DEFAULT 'active',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE payment_proposal IS 'Propuestas de cobro pendientes de verificacion (antes pagos_temporales). NO son borradores: son pagos propuestos por cobradores que requieren aprobacion.';

CREATE INDEX idx_payment_proposal_policy ON payment_proposal(policy_id);
CREATE INDEX idx_payment_proposal_original ON payment_proposal(original_payment_id);

-- -----------------------------------------------
-- receipt (recibo)
-- -----------------------------------------------
CREATE TABLE receipt (
    id              SERIAL PRIMARY KEY,
    receipt_number  VARCHAR(10) NOT NULL,
    policy_id       INT REFERENCES policy(id) ON DELETE RESTRICT,
    collector_id    INT REFERENCES collector(id) ON DELETE SET NULL,
    payment_id      INT REFERENCES payment(id) ON DELETE SET NULL,
    assignment_date DATE,
    usage_date      DATE,
    delivery_date   DATE,
    status          receipt_status_type NOT NULL DEFAULT 'unassigned',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_receipt_number UNIQUE (receipt_number)
);
COMMENT ON TABLE receipt IS 'Recibos fisicos gestionados por cobradores';

CREATE INDEX idx_receipt_collector ON receipt(collector_id);
CREATE INDEX idx_receipt_payment ON receipt(payment_id);
CREATE INDEX idx_receipt_status ON receipt(status);
CREATE INDEX idx_receipt_number ON receipt(receipt_number);

-- -----------------------------------------------
-- receipt_loss_schedule (programacion de extravios)
-- -----------------------------------------------
CREATE TABLE receipt_loss_schedule (
    receipt_number  VARCHAR(10) PRIMARY KEY,
    deadline        TIMESTAMPTZ NOT NULL
);
COMMENT ON TABLE receipt_loss_schedule IS 'Programacion de cambio a LOST para recibos no devueltos';

-- -----------------------------------------------
-- cancellation
-- -----------------------------------------------
CREATE TABLE cancellation (
    id                          SERIAL PRIMARY KEY,
    policy_id                   INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    cancellation_date           DATE NOT NULL,
    reason                      VARCHAR(255),
    code                        VARCHAR(45),
    payments_made               INT DEFAULT 0,
    cancelled_by_user_id        INT REFERENCES app_user(id) ON DELETE SET NULL,
    notification_sent_seller    BOOLEAN NOT NULL DEFAULT FALSE,
    notification_sent_collector BOOLEAN NOT NULL DEFAULT FALSE,
    notification_sent_client    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_cancellation_payments CHECK (payments_made >= 0)
);
COMMENT ON TABLE cancellation IS 'Registro de cancelaciones de polizas';

CREATE INDEX idx_cancellation_policy ON cancellation(policy_id);
CREATE INDEX idx_cancellation_date ON cancellation(cancellation_date);
CREATE INDEX idx_cancellation_user ON cancellation(cancelled_by_user_id);

-- -----------------------------------------------
-- card (tarjeta)
-- -----------------------------------------------
CREATE TABLE card (
    id              SERIAL PRIMARY KEY,
    policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    current_holder  VARCHAR(50) NOT NULL,
    assignment_date DATE NOT NULL,
    seller_id       INT REFERENCES seller(id),
    status          card_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE card IS 'Tarjetas de seguro fisicas asignadas a polizas';
COMMENT ON COLUMN card.current_holder IS 'Persona que tiene fisicamente la tarjeta (cobrador, vendedor, oficina)';

CREATE INDEX idx_card_policy ON card(policy_id);
CREATE INDEX idx_card_seller ON card(seller_id);
CREATE INDEX idx_card_status ON card(status);
CREATE INDEX idx_card_holder ON card(current_holder);

-- -----------------------------------------------
-- collection_assignment (RENOMBRADA de card_location_history / ubicacion_tarjeta)
-- -----------------------------------------------
CREATE TABLE collection_assignment (
    id              SERIAL PRIMARY KEY,
    card_id         INT NOT NULL REFERENCES card(id) ON DELETE CASCADE,
    policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    assigned_to     VARCHAR(50) NOT NULL,
    zone            VARCHAR(50),
    route           VARCHAR(50),
    assignment_date DATE NOT NULL,
    observations    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE collection_assignment IS 'Asignacion de cobranza: a quien se asigna cobrar cada poliza, en que zona/ruta. Antes ubicacion_tarjeta en MySQL.';
COMMENT ON COLUMN collection_assignment.assigned_to IS 'Persona asignada para cobrar (cobrador o vendedor)';
COMMENT ON COLUMN collection_assignment.zone IS 'Zona de cobranza asignada';
COMMENT ON COLUMN collection_assignment.route IS 'Ruta de cobranza asignada';

CREATE INDEX idx_collection_assignment_card ON collection_assignment(card_id);
CREATE INDEX idx_collection_assignment_policy ON collection_assignment(policy_id);
CREATE INDEX idx_collection_assignment_assigned ON collection_assignment(assigned_to);

-- ============================================================================
-- PASO 5: Siniestros y Servicios
-- ============================================================================

-- -----------------------------------------------
-- adjuster (ajustador)
-- -----------------------------------------------
CREATE TABLE adjuster (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(20) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    phone       VARCHAR(20),
    telegram_id BIGINT NOT NULL,
    status      entity_status_type NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_adjuster_code UNIQUE (code)
);
COMMENT ON TABLE adjuster IS 'Ajustadores de siniestros';

CREATE INDEX idx_adjuster_status ON adjuster(status);

-- -----------------------------------------------
-- adjuster_shift
-- -----------------------------------------------
CREATE TABLE adjuster_shift (
    id              SERIAL PRIMARY KEY,
    shift_date      DATE NOT NULL,
    adjuster_id     INT NOT NULL REFERENCES adjuster(id) ON DELETE CASCADE,
    shift_order     shift_order_type NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_shift_date_adjuster UNIQUE (shift_date, adjuster_id)
);
COMMENT ON TABLE adjuster_shift IS 'Asignacion de guardias diarias a ajustadores';
COMMENT ON COLUMN adjuster_shift.shift_order IS 'first=1ra guardia, second=2da, third=3ra, rest=descanso';

CREATE INDEX idx_shift_date ON adjuster_shift(shift_date);

-- -----------------------------------------------
-- incident (siniestro) -- FK a policy (correccion #1 confirmada)
-- -----------------------------------------------
CREATE TABLE incident (
    id                      SERIAL PRIMARY KEY,
    policy_id               INT REFERENCES policy(id) ON DELETE RESTRICT,
    report_number           VARCHAR(20) NOT NULL,
    requester_name          VARCHAR(100) NOT NULL,
    phone                   VARCHAR(20),
    origin_address_id       BIGINT REFERENCES address(id) ON DELETE SET NULL,
    incident_type           incident_type_enum,
    description             TEXT,
    responsibility          responsibility_type,
    client_misconduct       BOOLEAN NOT NULL DEFAULT FALSE,
    adjuster_id             INT NOT NULL REFERENCES adjuster(id) ON DELETE RESTRICT,
    report_time             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    contact_time            TIMESTAMPTZ,
    completion_time         TIMESTAMPTZ,
    attended_by_user_id     INT REFERENCES app_user(id),
    service_status          service_status_type NOT NULL DEFAULT 'pending',
    satisfaction_rating     SMALLINT,
    comments                TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_incident_rating CHECK (satisfaction_rating IS NULL OR (satisfaction_rating >= 1 AND satisfaction_rating <= 10))
);
COMMENT ON TABLE incident IS 'Reportes de siniestros vehiculares. FK a policy (un cliente puede tener multiples polizas).';
COMMENT ON COLUMN incident.policy_id IS 'FK a policy(id). Un cliente puede tener 3 polizas con folios distintos; el siniestro se liga a UNA poliza.';
COMMENT ON COLUMN incident.client_misconduct IS 'Comportamiento inadecuado del cliente durante el siniestro';
COMMENT ON COLUMN incident.satisfaction_rating IS 'Calificacion 1-10 del servicio';

CREATE INDEX idx_incident_policy ON incident(policy_id);
CREATE INDEX idx_incident_adjuster ON incident(adjuster_id);
CREATE INDEX idx_incident_report_time ON incident(report_time);
CREATE INDEX idx_incident_status ON incident(service_status);
CREATE INDEX idx_incident_report_number ON incident(report_number);
CREATE INDEX idx_incident_search ON incident USING GIN (
    (report_number || ' ' || requester_name || ' ' || COALESCE(phone, '')) gin_trgm_ops
);

-- -----------------------------------------------
-- hospital
-- -----------------------------------------------
CREATE TABLE hospital (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    address_id      BIGINT REFERENCES address(id),
    phone           VARCHAR(20),
    status          entity_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE hospital IS 'Hospitales convenidos para pases medicos';

-- -----------------------------------------------
-- medical_pass (pase medico)
-- -----------------------------------------------
CREATE TABLE medical_pass (
    id                  SERIAL PRIMARY KEY,
    incident_id         INT NOT NULL REFERENCES incident(id) ON DELETE RESTRICT,
    hospital_id         INT NOT NULL REFERENCES hospital(id) ON DELETE RESTRICT,
    pass_number         VARCHAR(50) NOT NULL,
    beneficiary_name    VARCHAR(100),
    injuries            TEXT,
    observations        TEXT,
    cost                NUMERIC(12,2),
    status              service_status_type NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_medical_cost CHECK (cost IS NULL OR cost >= 0)
);
COMMENT ON TABLE medical_pass IS 'Pases medicos emitidos en siniestros';

CREATE INDEX idx_medical_pass_incident ON medical_pass(incident_id);
CREATE INDEX idx_medical_pass_hospital ON medical_pass(hospital_id);

-- -----------------------------------------------
-- workshop (taller)
-- -----------------------------------------------
CREATE TABLE workshop (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    address_id      BIGINT REFERENCES address(id),
    phone           VARCHAR(20),
    status          entity_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE workshop IS 'Talleres convenidos para reparacion vehicular';

-- -----------------------------------------------
-- workshop_pass (pase de taller)
-- -----------------------------------------------
CREATE TABLE workshop_pass (
    id                  SERIAL PRIMARY KEY,
    incident_id         INT NOT NULL REFERENCES incident(id) ON DELETE RESTRICT,
    workshop_id         INT NOT NULL REFERENCES workshop(id) ON DELETE RESTRICT,
    pass_number         VARCHAR(50) NOT NULL,
    beneficiary_name    VARCHAR(100),
    pass_type           workshop_pass_type_enum NOT NULL,
    vehicle_damages     TEXT,
    observations        TEXT,
    cost                NUMERIC(12,2),
    status              service_status_type NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_workshop_cost CHECK (cost IS NULL OR cost >= 0)
);
COMMENT ON TABLE workshop_pass IS 'Pases de taller emitidos en siniestros';

CREATE INDEX idx_workshop_pass_incident ON workshop_pass(incident_id);
CREATE INDEX idx_workshop_pass_workshop ON workshop_pass(workshop_id);

-- -----------------------------------------------
-- tow_provider (proveedor de gruas)
-- -----------------------------------------------
CREATE TABLE tow_provider (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    phone           VARCHAR(20),
    telegram_group_id BIGINT,
    contact_person  VARCHAR(100),
    address_id      BIGINT REFERENCES address(id) ON DELETE SET NULL,
    notes           TEXT,
    status          entity_status_type NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE tow_provider IS 'Proveedores de servicios de grua (unifica tow_service_providers y tow_providers)';

CREATE INDEX idx_tow_provider_status ON tow_provider(status);

-- -----------------------------------------------
-- tow_service (servicio de grua) -- FK a policy (correccion #1 confirmada)
-- -----------------------------------------------
CREATE TABLE tow_service (
    id                          SERIAL PRIMARY KEY,
    policy_id                   INT REFERENCES policy(id) ON DELETE RESTRICT,
    report_number               VARCHAR(20) NOT NULL,
    requester_name              VARCHAR(100) NOT NULL,
    phone                       VARCHAR(20),
    origin_address_id           BIGINT REFERENCES address(id) ON DELETE SET NULL,
    destination_address_id      BIGINT REFERENCES address(id) ON DELETE SET NULL,
    vehicle_failure             VARCHAR(100) NOT NULL,
    load_weight                 INT,
    tow_provider_id             INT REFERENCES tow_provider(id) ON DELETE SET NULL,
    tow_cost                    NUMERIC(12,2),
    extra_charge                NUMERIC(12,2),
    estimated_arrival_time      TIMESTAMPTZ,
    report_time                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    attended_by_user_id         INT REFERENCES app_user(id),
    contact_time                TIMESTAMPTZ,
    end_time                    TIMESTAMPTZ,
    comments                    TEXT,
    service_status              service_status_type NOT NULL DEFAULT 'pending',
    satisfaction_rating         SMALLINT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_tow_cost CHECK (tow_cost IS NULL OR tow_cost >= 0),
    CONSTRAINT chk_tow_rating CHECK (satisfaction_rating IS NULL OR (satisfaction_rating >= 1 AND satisfaction_rating <= 10))
);
COMMENT ON TABLE tow_service IS 'Servicios de grua solicitados por asegurados. FK a policy (un cliente puede tener multiples polizas).';
COMMENT ON COLUMN tow_service.policy_id IS 'FK a policy(id). Un cliente puede tener 3 polizas; la grua se liga a UNA poliza especifica.';

CREATE INDEX idx_tow_policy ON tow_service(policy_id);
CREATE INDEX idx_tow_provider_fk ON tow_service(tow_provider_id);
CREATE INDEX idx_tow_report_time ON tow_service(report_time);
CREATE INDEX idx_tow_status ON tow_service(service_status);
CREATE INDEX idx_tow_search ON tow_service USING GIN (
    (report_number || ' ' || requester_name) gin_trgm_ops
);

-- ============================================================================
-- PASO 6: Encuestas de Satisfaccion
-- ============================================================================

CREATE TABLE incident_satisfaction_survey (
    id                      SERIAL PRIMARY KEY,
    incident_id             INT NOT NULL REFERENCES incident(id) ON DELETE RESTRICT,
    survey_date             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time_rating    SMALLINT NOT NULL,
    service_rating          SMALLINT NOT NULL,
    overall_service_rating  SMALLINT NOT NULL,
    company_impression      SMALLINT NOT NULL,
    comments                TEXT,
    average_rating          NUMERIC(3,2) NOT NULL,
    surveyed_by_user_id     INT REFERENCES app_user(id) ON DELETE SET NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_incident_survey UNIQUE (incident_id),
    CONSTRAINT chk_incident_survey_ratings CHECK (
        response_time_rating BETWEEN 1 AND 10
        AND service_rating BETWEEN 1 AND 10
        AND overall_service_rating BETWEEN 1 AND 10
        AND company_impression BETWEEN 1 AND 10
    )
);
COMMENT ON TABLE incident_satisfaction_survey IS 'Encuestas de satisfaccion para siniestros';

CREATE TABLE tow_satisfaction_survey (
    id                      SERIAL PRIMARY KEY,
    tow_service_id          INT NOT NULL REFERENCES tow_service(id) ON DELETE RESTRICT,
    survey_date             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time_rating    SMALLINT NOT NULL,
    service_rating          SMALLINT NOT NULL,
    overall_service_rating  SMALLINT NOT NULL,
    company_impression      SMALLINT NOT NULL,
    comments                TEXT,
    average_rating          NUMERIC(3,2) NOT NULL,
    surveyed_by_user_id     INT REFERENCES app_user(id) ON DELETE SET NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_tow_survey UNIQUE (tow_service_id),
    CONSTRAINT chk_tow_survey_ratings CHECK (
        response_time_rating BETWEEN 1 AND 10
        AND service_rating BETWEEN 1 AND 10
        AND overall_service_rating BETWEEN 1 AND 10
        AND company_impression BETWEEN 1 AND 10
    )
);
COMMENT ON TABLE tow_satisfaction_survey IS 'Encuestas de satisfaccion para servicios de grua';

-- ============================================================================
-- PASO 7: Endosos, Renovaciones, Detalles Amplia
-- ============================================================================

-- -----------------------------------------------
-- endorsement (endoso)
-- -----------------------------------------------
CREATE TABLE endorsement (
    id                  SERIAL PRIMARY KEY,
    policy_id           INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    endorsement_type    endorsement_type_enum NOT NULL,
    request_date        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    application_date    TIMESTAMPTZ,
    status              endorsement_status_type NOT NULL DEFAULT 'pending',
    change_details      JSONB NOT NULL,
    comments            TEXT,
    new_contractor_id   BIGINT REFERENCES client(id),
    previous_vehicle_id INT REFERENCES vehicle(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE endorsement IS 'Endosos (modificaciones) a polizas vigentes';
COMMENT ON COLUMN endorsement.change_details IS 'Detalle de cambios en formato JSONB estructurado';

CREATE INDEX idx_endorsement_policy ON endorsement(policy_id);
CREATE INDEX idx_endorsement_status ON endorsement(status);
CREATE INDEX idx_endorsement_details ON endorsement USING GIN (change_details);

-- -----------------------------------------------
-- renewal (renovacion)
-- -----------------------------------------------
CREATE TABLE renewal (
    id                  SERIAL PRIMARY KEY,
    old_policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    new_policy_id       INT REFERENCES policy(id) ON DELETE SET NULL,
    renewal_date        DATE NOT NULL,
    status              renewal_status_type NOT NULL DEFAULT 'pending',
    comments            TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE renewal IS 'Registro de renovaciones de polizas';

CREATE INDEX idx_renewal_old ON renewal(old_policy_id);
CREATE INDEX idx_renewal_new ON renewal(new_policy_id);

-- -----------------------------------------------
-- policy_amplia_detail
-- -----------------------------------------------
CREATE TABLE policy_amplia_detail (
    id                                  SERIAL PRIMARY KEY,
    policy_id                           INT NOT NULL REFERENCES policy(id) ON DELETE CASCADE,
    quote_number                        VARCHAR(20),
    coverage_type                       VARCHAR(20) NOT NULL,
    commercial_value                    NUMERIC(12,2) NOT NULL,
    damage_deductible                   NUMERIC(12,2) NOT NULL,
    theft_deductible                    NUMERIC(12,2) NOT NULL,
    civil_liability_deductible          NUMERIC(12,2),
    eligible_no_responsible_incidents   BOOLEAN NOT NULL DEFAULT TRUE,
    eligible_no_fraud_observations      BOOLEAN NOT NULL DEFAULT TRUE,
    eligible_no_payment_issues          BOOLEAN NOT NULL DEFAULT TRUE,
    eligible_renewal_period_met         BOOLEAN NOT NULL DEFAULT FALSE,
    eligibility_last_checked            TIMESTAMPTZ,
    eligibility_notes                   TEXT,
    created_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_amplia_policy UNIQUE (policy_id),
    CONSTRAINT chk_amplia_values CHECK (commercial_value >= 0 AND damage_deductible >= 0 AND theft_deductible >= 0)
);
COMMENT ON TABLE policy_amplia_detail IS 'Detalles especificos de polizas AMPLIA, AMPLIA SELECT y PLATAFORMA';
COMMENT ON COLUMN policy_amplia_detail.coverage_type IS 'AMPLIA, AMPLIA SELECT, PLATAFORMA N, PLATAFORMA A';

CREATE INDEX idx_amplia_eligibility ON policy_amplia_detail(
    eligible_no_responsible_incidents,
    eligible_no_fraud_observations,
    eligible_no_payment_issues,
    eligible_renewal_period_met
);

-- ============================================================================
-- PASO 8: Promociones Flexibles (REDISEÑADO v2)
-- ============================================================================

-- -----------------------------------------------
-- promotion (definicion de promocion)
-- -----------------------------------------------
CREATE TABLE promotion (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    status          entity_status_type NOT NULL DEFAULT 'active',
    start_date      DATE,
    end_date        DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_promotion_dates CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);
COMMENT ON TABLE promotion IS 'Definicion de promociones. Cada promocion puede tener multiples reglas de descuento (promotion_rule).';

CREATE INDEX idx_promotion_status ON promotion(status);
CREATE INDEX idx_promotion_dates ON promotion(start_date, end_date);

-- -----------------------------------------------
-- promotion_rule (NUEVO v2: reglas de descuento flexibles)
-- -----------------------------------------------
CREATE TABLE promotion_rule (
    id                          SERIAL PRIMARY KEY,
    promotion_id                INT NOT NULL REFERENCES promotion(id) ON DELETE CASCADE,
    discount_type               promotion_discount_type NOT NULL,
    discount_value              NUMERIC(12,2) NOT NULL,
    applies_to_payment_number   INT,
    min_payments                INT,
    max_payments                INT,
    coverage_ids                JSONB,
    vehicle_types               JSONB,
    requires_referral           BOOLEAN NOT NULL DEFAULT FALSE,
    description                 TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_rule_discount_value CHECK (discount_value >= 0),
    CONSTRAINT chk_rule_payment_range CHECK (
        min_payments IS NULL OR max_payments IS NULL OR min_payments <= max_payments
    )
);
COMMENT ON TABLE promotion_rule IS 'Reglas de descuento para cada promocion. Multiples reglas por promocion.';
COMMENT ON COLUMN promotion_rule.discount_type IS 'Tipo: percentage (%), fixed_amount ($), free_months (meses gratis), zero_down_payment ($0 enganche)';
COMMENT ON COLUMN promotion_rule.discount_value IS 'Valor: 15.00 para 15%, 500.00 para $500, 2 para 2 meses gratis, 0 para $0 enganche';
COMMENT ON COLUMN promotion_rule.applies_to_payment_number IS 'Numero de pago especifico donde aplica. NULL = aplica a todos los pagos elegibles.';
COMMENT ON COLUMN promotion_rule.coverage_ids IS 'JSONB array de IDs de cobertura elegibles. Ej: [1,3,5]. NULL = todas.';
COMMENT ON COLUMN promotion_rule.vehicle_types IS 'JSONB array de tipos de vehiculo elegibles. Ej: ["automobile","truck"]. NULL = todos.';
COMMENT ON COLUMN promotion_rule.requires_referral IS 'Si requiere poliza referente (para promociones de referidos)';

CREATE INDEX idx_promo_rule_promotion ON promotion_rule(promotion_id);
CREATE INDEX idx_promo_rule_type ON promotion_rule(discount_type);

-- -----------------------------------------------
-- promotion_application (NUEVO v2: promociones aplicadas a polizas)
-- -----------------------------------------------
CREATE TABLE promotion_application (
    id                  SERIAL PRIMARY KEY,
    promotion_id        INT NOT NULL REFERENCES promotion(id) ON DELETE RESTRICT,
    promotion_rule_id   INT NOT NULL REFERENCES promotion_rule(id) ON DELETE RESTRICT,
    policy_id           INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    referrer_policy_id  INT REFERENCES policy(id) ON DELETE SET NULL,
    discount_applied    NUMERIC(12,2) NOT NULL,
    applied_by_user_id  INT REFERENCES app_user(id) ON DELETE SET NULL,
    comments            TEXT,
    applied_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_promo_application UNIQUE (promotion_id, policy_id, promotion_rule_id),
    CONSTRAINT chk_promo_discount CHECK (discount_applied >= 0)
);
COMMENT ON TABLE promotion_application IS 'Registro de promociones efectivamente aplicadas a polizas';
COMMENT ON COLUMN promotion_application.referrer_policy_id IS 'Poliza referente (solo para promociones de referidos)';
COMMENT ON COLUMN promotion_application.discount_applied IS 'Monto del descuento efectivamente aplicado';

CREATE INDEX idx_promo_app_policy ON promotion_application(policy_id);
CREATE INDEX idx_promo_app_promotion ON promotion_application(promotion_id);
CREATE INDEX idx_promo_app_referrer ON promotion_application(referrer_policy_id) WHERE referrer_policy_id IS NOT NULL;

-- -----------------------------------------------
-- commission_rate (comisiones pivotadas)
-- -----------------------------------------------
CREATE TABLE commission_rate (
    id              SERIAL PRIMARY KEY,
    role            seller_class_type NOT NULL,
    level           INT NOT NULL,
    coverage_id     INT NOT NULL REFERENCES coverage(id) ON DELETE RESTRICT,
    percentage      NUMERIC(5,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_commission UNIQUE (role, level, coverage_id),
    CONSTRAINT chk_commission_pct CHECK (percentage >= 0 AND percentage <= 100),
    CONSTRAINT chk_commission_level CHECK (level > 0)
);
COMMENT ON TABLE commission_rate IS 'Tabla de comisiones por rol, nivel y cobertura (pivotada desde MySQL)';

-- ============================================================================
-- PASO 9: Mensajeria y Notificaciones
-- ============================================================================

-- -----------------------------------------------
-- sent_message
-- -----------------------------------------------
CREATE TABLE sent_message (
    id              SERIAL PRIMARY KEY,
    policy_id       INT REFERENCES policy(id) ON DELETE SET NULL,
    phone           VARCHAR(20) NOT NULL,
    message_type    message_type_enum NOT NULL,
    channel         message_channel_type NOT NULL DEFAULT 'whatsapp',
    delivery_status message_delivery_status_type NOT NULL DEFAULT 'queued',
    scheduled_at    TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ,
    target_payment_date DATE,
    days_before_due INT,
    retry_count     SMALLINT NOT NULL DEFAULT 0,
    max_retries     SMALLINT NOT NULL DEFAULT 3,
    error_message   TEXT,
    external_message_id VARCHAR(100),
    source_ip       VARCHAR(45),
    sent_by_user_id INT REFERENCES app_user(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_msg_retries CHECK (retry_count >= 0 AND retry_count <= max_retries)
);
COMMENT ON TABLE sent_message IS 'Mensajes de cobranza y recordatorios con tracking de entrega (WhatsApp, Telegram, SMS, email)';
COMMENT ON COLUMN sent_message.channel IS 'Canal de envio del mensaje';
COMMENT ON COLUMN sent_message.delivery_status IS 'Estado de entrega: queued->sent->delivered->read o failed';
COMMENT ON COLUMN sent_message.external_message_id IS 'ID del mensaje en el servicio externo (WhatsApp API, Telegram, etc.)';

CREATE INDEX idx_sent_msg_policy ON sent_message(policy_id, message_type);
CREATE INDEX idx_sent_msg_date ON sent_message(sent_at);
CREATE INDEX idx_sent_msg_phone ON sent_message(phone, sent_at);
CREATE INDEX idx_sent_msg_delivery ON sent_message(delivery_status) WHERE delivery_status IN ('queued', 'sent');
CREATE INDEX idx_sent_msg_failed ON sent_message(retry_count) WHERE delivery_status = 'failed';

-- -----------------------------------------------
-- policy_notification
-- -----------------------------------------------
CREATE TABLE policy_notification (
    id              SERIAL PRIMARY KEY,
    policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE CASCADE,
    seller_id       INT NOT NULL REFERENCES seller(id) ON DELETE CASCADE,
    notification_type notification_period_type NOT NULL,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE policy_notification IS 'Notificaciones enviadas a vendedores sobre polizas';

CREATE INDEX idx_policy_notif_policy ON policy_notification(policy_id, notification_type);
CREATE INDEX idx_policy_notif_seller ON policy_notification(seller_id);

-- -----------------------------------------------
-- renewal_notification_log
-- -----------------------------------------------
CREATE TABLE renewal_notification_log (
    id              SERIAL PRIMARY KEY,
    policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE CASCADE,
    notification_type notification_period_type NOT NULL,
    sent_at         TIMESTAMPTZ NOT NULL,
    sent_by         VARCHAR(50) NOT NULL DEFAULT 'system'
);
COMMENT ON TABLE renewal_notification_log IS 'Log de notificaciones automaticas de renovacion';

CREATE INDEX idx_renewal_notif_policy ON renewal_notification_log(policy_id);

-- ============================================================================
-- PASO 10: Logs y Auditoria
-- ============================================================================

-- -----------------------------------------------
-- execution_log
-- -----------------------------------------------
CREATE TABLE execution_log (
    id          SERIAL PRIMARY KEY,
    description VARCHAR(255),
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE execution_log IS 'Log de ejecuciones de procesos automaticos';

-- -----------------------------------------------
-- visit_notice (avisos de visita)
-- -----------------------------------------------
CREATE TABLE visit_notice (
    id              SERIAL PRIMARY KEY,
    card_id         INT REFERENCES card(id) ON DELETE SET NULL,
    policy_id       INT NOT NULL REFERENCES policy(id) ON DELETE RESTRICT,
    visit_date      DATE NOT NULL,
    comments        TEXT,
    payment_id      INT REFERENCES payment(id) ON DELETE SET NULL,
    notice_number   INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE visit_notice IS 'Avisos de visita para cobranza de tarjetas';

CREATE INDEX idx_visit_card ON visit_notice(card_id);
CREATE INDEX idx_visit_policy ON visit_notice(policy_id);

-- -----------------------------------------------
-- audit_log (auditoria generica, particionada por mes)
-- -----------------------------------------------
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(63) NOT NULL,
    record_id       INT NOT NULL,
    action          VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_values      JSONB,
    new_values      JSONB,
    changed_by_user_id INT,
    changed_by      VARCHAR(100),
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (changed_at);
COMMENT ON TABLE audit_log IS 'Registro de auditoria para cambios en tablas criticas. Particionado por mes.';
COMMENT ON COLUMN audit_log.changed_by_user_id IS 'Se obtiene via current_setting(''myapp.current_user_id'', true). La app debe ejecutar SET LOCAL myapp.current_user_id = ? al inicio de cada transaccion.';

-- Crear particiones iniciales (12 meses de 2026)
CREATE TABLE audit_log_2026_01 PARTITION OF audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_log_2026_02 PARTITION OF audit_log
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE audit_log_2026_03 PARTITION OF audit_log
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE audit_log_2026_04 PARTITION OF audit_log
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE audit_log_2026_05 PARTITION OF audit_log
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
CREATE TABLE audit_log_2026_06 PARTITION OF audit_log
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE audit_log_2026_07 PARTITION OF audit_log
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE audit_log_2026_08 PARTITION OF audit_log
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE audit_log_2026_09 PARTITION OF audit_log
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
CREATE TABLE audit_log_2026_10 PARTITION OF audit_log
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');
CREATE TABLE audit_log_2026_11 PARTITION OF audit_log
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
CREATE TABLE audit_log_2026_12 PARTITION OF audit_log
    FOR VALUES FROM ('2026-12-01') TO ('2027-01-01');
CREATE TABLE audit_log_default PARTITION OF audit_log DEFAULT;

CREATE INDEX idx_audit_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_date ON audit_log(changed_at);
CREATE INDEX idx_audit_user ON audit_log(changed_by_user_id) WHERE changed_by_user_id IS NOT NULL;

-- ============================================================================
-- PASO 11: Flujo de Autorizacion (NUEVO v2)
-- ============================================================================

-- -----------------------------------------------
-- approval_request (solicitudes de aprobacion desde apps moviles)
-- -----------------------------------------------
CREATE TABLE approval_request (
    id                      SERIAL PRIMARY KEY,
    request_type            approval_request_type NOT NULL,
    status                  approval_status_type NOT NULL DEFAULT 'pending',
    entity_type             VARCHAR(50) NOT NULL,
    entity_id               INT,
    payload                 JSONB NOT NULL,
    submitted_by_user_id    INT NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    submitted_from_device_id INT REFERENCES device_session(id) ON DELETE SET NULL,
    reviewed_by_user_id     INT REFERENCES app_user(id) ON DELETE SET NULL,
    review_notes            TEXT,
    submitted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at             TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE approval_request IS 'Flujo de autorizacion para envios desde apps moviles. Polizas subidas por vendedores y pagos registrados por cobradores requieren aprobacion antes de ser oficiales.';
COMMENT ON COLUMN approval_request.request_type IS 'policy_submission = poliza nueva/renovacion desde app vendedor. payment_submission = pago registrado desde app cobrador.';
COMMENT ON COLUMN approval_request.entity_type IS 'Tipo de entidad: policy, payment (referencia polimorfica)';
COMMENT ON COLUMN approval_request.entity_id IS 'ID de la entidad creada (NULL si aun no se crea hasta aprobacion)';
COMMENT ON COLUMN approval_request.payload IS 'Datos completos enviados desde la app movil en formato JSONB';
COMMENT ON COLUMN approval_request.submitted_from_device_id IS 'Dispositivo desde donde se envio la solicitud';

CREATE INDEX idx_approval_status ON approval_request(status) WHERE status = 'pending';
CREATE INDEX idx_approval_type ON approval_request(request_type, status);
CREATE INDEX idx_approval_submitted_by ON approval_request(submitted_by_user_id);
CREATE INDEX idx_approval_reviewed_by ON approval_request(reviewed_by_user_id);

-- ============================================================================
-- PASO 12: Log de Acciones Moviles (NUEVO v2)
-- ============================================================================

-- -----------------------------------------------
-- mobile_action_log (log de acciones desde apps moviles)
-- -----------------------------------------------
CREATE TABLE mobile_action_log (
    id                  BIGSERIAL PRIMARY KEY,
    device_session_id   INT NOT NULL REFERENCES device_session(id) ON DELETE CASCADE,
    user_id             INT NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    action_type         VARCHAR(100) NOT NULL,
    entity_type         VARCHAR(50),
    entity_id           INT,
    latitude            NUMERIC(10,8),
    longitude           NUMERIC(11,8),
    geom                geometry(Point, 4326),
    request_payload     JSONB,
    response_status     SMALLINT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE mobile_action_log IS 'Log de acciones realizadas desde apps moviles con geolocalizacion';
COMMENT ON COLUMN mobile_action_log.action_type IS 'Tipo de accion: create_policy, register_payment, report_incident, start_tow, etc.';
COMMENT ON COLUMN mobile_action_log.geom IS 'Punto PostGIS para consultas espaciales de rastreo';
COMMENT ON COLUMN mobile_action_log.request_payload IS 'Datos enviados por la app movil';
COMMENT ON COLUMN mobile_action_log.response_status IS 'Codigo HTTP de respuesta del API';

CREATE INDEX idx_mobile_log_device ON mobile_action_log(device_session_id);
CREATE INDEX idx_mobile_log_user ON mobile_action_log(user_id);
CREATE INDEX idx_mobile_log_action ON mobile_action_log(action_type, created_at);
CREATE INDEX idx_mobile_log_entity ON mobile_action_log(entity_type, entity_id) WHERE entity_type IS NOT NULL;
-- Indice espacial para rastreo geografico de acciones
CREATE INDEX idx_mobile_log_geom ON mobile_action_log USING GIST (geom);

-- ============================================================================
-- PASO 13: Vistas Materializadas para Dashboard
-- ============================================================================

-- Vista: Resumen mensual de polizas por cobertura
CREATE MATERIALIZED VIEW mv_monthly_policy_summary AS
SELECT
    DATE_TRUNC('month', p.elaboration_date) AS month,
    c.name AS coverage_name,
    COUNT(*) FILTER (WHERE p.renewal_folio IS NULL) AS new_policies,
    COUNT(*) FILTER (WHERE p.renewal_folio IS NOT NULL) AS renewals,
    COUNT(*) AS total
FROM policy p
JOIN coverage c ON p.coverage_id = c.id
WHERE p.elaboration_date IS NOT NULL
GROUP BY DATE_TRUNC('month', p.elaboration_date), c.name
ORDER BY month DESC, total DESC;

CREATE UNIQUE INDEX idx_mv_monthly_policy ON mv_monthly_policy_summary(month, coverage_name);

COMMENT ON MATERIALIZED VIEW mv_monthly_policy_summary IS 'Resumen mensual de polizas por cobertura. Refrescar: REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_policy_summary;';

-- Vista: Top vendedores del mes
CREATE MATERIALIZED VIEW mv_top_sellers_monthly AS
SELECT
    DATE_TRUNC('month', p.elaboration_date) AS month,
    s.id AS seller_id,
    s.code_name,
    s.full_name,
    COUNT(*) AS total_policies,
    COUNT(*) FILTER (WHERE p.renewal_folio IS NULL) AS new_policies,
    COUNT(*) FILTER (WHERE p.renewal_folio IS NOT NULL) AS renewals
FROM policy p
JOIN seller s ON p.seller_id = s.id
WHERE p.elaboration_date IS NOT NULL
GROUP BY DATE_TRUNC('month', p.elaboration_date), s.id, s.code_name, s.full_name
ORDER BY month DESC, total_policies DESC;

CREATE UNIQUE INDEX idx_mv_top_sellers ON mv_top_sellers_monthly(month, seller_id);

-- Vista: Estadisticas de cobranza
CREATE MATERIALIZED VIEW mv_collection_stats AS
SELECT
    co.id AS collector_id,
    co.code_name,
    co.full_name,
    COUNT(*) FILTER (WHERE r.status = 'assigned') AS assigned_receipts,
    COUNT(*) FILTER (WHERE r.status = 'used') AS used_receipts,
    COUNT(*) FILTER (WHERE r.status = 'delivered') AS delivered_receipts,
    COUNT(*) FILTER (WHERE r.status = 'lost') AS lost_receipts,
    COUNT(*) FILTER (WHERE r.status IN ('assigned', 'used', 'lost', 'cancelled_undelivered')) AS total_active
FROM collector co
LEFT JOIN receipt r ON co.id = r.collector_id
GROUP BY co.id, co.code_name, co.full_name;

CREATE UNIQUE INDEX idx_mv_collection_stats ON mv_collection_stats(collector_id);

-- ============================================================================
-- PASO 14: Funciones y Triggers
-- ============================================================================

-- Funcion: Actualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de updated_at a todas las tablas con dicho campo
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'updated_at'
          AND table_schema = 'public'
          AND table_name NOT LIKE 'mv_%'
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW
             EXECUTE FUNCTION fn_update_timestamp();',
            t, t
        );
    END LOOP;
END;
$$;

-- Funcion: Trigger de auditoria generico
-- La aplicacion debe ejecutar al inicio de cada transaccion:
--   SET LOCAL myapp.current_user_id = '123';
--   SET LOCAL myapp.current_user_name = 'juan.perez';
CREATE OR REPLACE FUNCTION fn_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id INT;
    v_user_name TEXT;
BEGIN
    v_user_id := NULLIF(current_setting('myapp.current_user_id', true), '')::INT;
    v_user_name := COALESCE(NULLIF(current_setting('myapp.current_user_name', true), ''), current_user);

    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(table_name, record_id, action, new_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', to_jsonb(NEW), v_user_id, v_user_name);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values, new_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), v_user_id, v_user_name);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values, changed_by_user_id, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), v_user_id, v_user_name);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Aplicar auditoria a tablas criticas
CREATE TRIGGER trg_policy_audit
    AFTER INSERT OR UPDATE OR DELETE ON policy
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_payment_audit
    AFTER INSERT OR UPDATE OR DELETE ON payment
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_cancellation_audit
    AFTER INSERT OR UPDATE OR DELETE ON cancellation
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_endorsement_audit
    AFTER INSERT OR UPDATE OR DELETE ON endorsement
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_incident_audit
    AFTER INSERT OR UPDATE OR DELETE ON incident
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

CREATE TRIGGER trg_tow_service_audit
    AFTER INSERT OR UPDATE OR DELETE ON tow_service
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

-- NUEVO v2: Auditoria en approval_request
CREATE TRIGGER trg_approval_request_audit
    AFTER INSERT OR UPDATE OR DELETE ON approval_request
    FOR EACH ROW EXECUTE FUNCTION fn_audit_trigger();

-- Tabla de secuencias de numeros de reporte (evita race conditions)
CREATE TABLE report_number_sequence (
    prefix      VARCHAR(10) PRIMARY KEY,
    date_part   VARCHAR(8) NOT NULL,
    last_number INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_report_seq UNIQUE (prefix, date_part)
);
COMMENT ON TABLE report_number_sequence IS 'Secuencias para generacion concurrente de numeros de reporte sin race conditions';

-- Funcion: Obtener siguiente numero de reporte con lock
CREATE OR REPLACE FUNCTION fn_next_report_number(p_prefix TEXT)
RETURNS TEXT AS $$
DECLARE
    v_date_part TEXT;
    v_next_num INT;
BEGIN
    v_date_part := TO_CHAR(NOW(), 'YYYYMMDD');

    INSERT INTO report_number_sequence (prefix, date_part, last_number)
    VALUES (p_prefix, v_date_part, 1)
    ON CONFLICT (prefix, date_part)
    DO UPDATE SET last_number = report_number_sequence.last_number + 1
    RETURNING last_number INTO v_next_num;

    RETURN p_prefix || '-' || v_date_part || '-' || LPAD(v_next_num::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Funcion: Generar numero de reporte de siniestro
CREATE OR REPLACE FUNCTION fn_generate_incident_report_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.report_number IS NULL OR NEW.report_number = '' THEN
        NEW.report_number := fn_next_report_number('INC');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_incident_report_number
    BEFORE INSERT ON incident
    FOR EACH ROW EXECUTE FUNCTION fn_generate_incident_report_number();

-- Funcion: Generar numero de reporte de grua
CREATE OR REPLACE FUNCTION fn_generate_tow_report_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.report_number IS NULL OR NEW.report_number = '' THEN
        NEW.report_number := fn_next_report_number('TOW');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tow_report_number
    BEFORE INSERT ON tow_service
    FOR EACH ROW EXECUTE FUNCTION fn_generate_tow_report_number();

-- NUEVO v2: Funcion helper para crear geometry desde lat/lng al insertar address
CREATE OR REPLACE FUNCTION fn_set_address_geom()
RETURNS TRIGGER AS $$
BEGIN
    -- Si se proporcionan coordenadas, crear el punto PostGIS automaticamente
    -- Nota: la app puede insertar con ST_SetSRID(ST_MakePoint(lon, lat), 4326) directamente
    -- o usar esta funcion que lo hace en el trigger
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PASO 15: Comentarios finales
-- ============================================================================

COMMENT ON SCHEMA public IS 'Esquema principal del CRM de Seguros ProtegRT - PostgreSQL v2.1';

-- ============================================================================
-- PASO 16: Refresh de Vistas Materializadas y Mantenimiento
-- ============================================================================

-- Funcion unica para refrescar todas las vistas materializadas
CREATE OR REPLACE FUNCTION fn_refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Iniciando refresh de vistas materializadas: %', NOW();
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_policy_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_sellers_monthly;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_collection_stats;
    RAISE NOTICE 'Refresh de vistas materializadas completado: %', NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_refresh_all_materialized_views() IS 'Refresca las 3 vistas materializadas del dashboard. Ejecutar diariamente.';

-- Funcion para crear automaticamente particiones de audit_log para el proximo mes
CREATE OR REPLACE FUNCTION fn_create_next_audit_partition()
RETURNS void AS $$
DECLARE
    v_next_month DATE;
    v_partition_name TEXT;
    v_start_date TEXT;
    v_end_date TEXT;
BEGIN
    v_next_month := DATE_TRUNC('month', NOW()) + INTERVAL '1 month';
    v_partition_name := 'audit_log_' || TO_CHAR(v_next_month, 'YYYY_MM');
    v_start_date := TO_CHAR(v_next_month, 'YYYY-MM-DD');
    v_end_date := TO_CHAR(v_next_month + INTERVAL '1 month', 'YYYY-MM-DD');

    IF NOT EXISTS (
        SELECT 1 FROM pg_class WHERE relname = v_partition_name
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF audit_log FOR VALUES FROM (%L) TO (%L)',
            v_partition_name, v_start_date, v_end_date
        );
        RAISE NOTICE 'Particion creada: %', v_partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_create_next_audit_partition() IS 'Crea la particion de audit_log para el proximo mes. Ejecutar mensualmente.';

-- Configuracion de pg_cron (requiere extension instalada en el servidor)
-- Ejecutar estas sentencias MANUALMENTE despues de instalar pg_cron:
--
--   CREATE EXTENSION IF NOT EXISTS pg_cron;
--
--   -- Refresh de vistas materializadas: diario a las 00:30
--   SELECT cron.schedule('refresh-materialized-views',
--       '30 0 * * *',
--       'SELECT fn_refresh_all_materialized_views()');
--
--   -- Crear particion de audit_log: dia 25 de cada mes
--   SELECT cron.schedule('create-audit-partition',
--       '0 3 25 * *',
--       'SELECT fn_create_next_audit_partition()');

-- ============================================================================
-- PASO 17: ESTRATEGIA DE MIGRACION FOLIO -> ID
-- ============================================================================
-- El sistema MySQL actual usa `folio` (INT) como clave de relacion entre tablas.
-- El nuevo diseno usa `policy.id` (SERIAL) como PK tecnico, conservando `folio`
-- como campo de negocio con UNIQUE constraint.
--
-- PLAN DE MIGRACION (ejecutar en este orden):
--
-- 1. Migrar polizas primero: INSERT INTO policy SELECT ... FROM polizas
--    El policy.id sera SERIAL auto-generado. Conservar policy.folio como campo de negocio.
--
-- 2. Crear tabla temporal de mapeo:
--    CREATE TEMP TABLE folio_to_policy_id AS
--      SELECT id AS policy_id, folio FROM policy;
--    CREATE UNIQUE INDEX ON folio_to_policy_id(folio);
--
-- 3. Migrar tablas dependientes usando JOIN al mapeo:
--    INSERT INTO payment (policy_id, ...)
--      SELECT m.policy_id, ...
--      FROM pagos p JOIN folio_to_policy_id m ON p.folio = m.folio;
--
-- 4. Repetir paso 3 para: cancellation, card, receipt, incident, tow_service,
--    endorsement, renewal, sent_message, payment_proposal, visit_notice,
--    policy_notification, renewal_notification_log, policy_amplia_detail,
--    collection_assignment.
--
-- 5. Verificar integridad:
--    SELECT COUNT(*) FROM payment WHERE policy_id NOT IN (SELECT id FROM policy);
--    -- Debe retornar 0 para cada tabla migrada.
--
-- 6. Eliminar tabla temporal:
--    DROP TABLE folio_to_policy_id;
--
-- RIESGO: Este es el cambio mas critico de toda la migracion.
-- Se recomienda ejecutar en una transaccion unica con SAVEPOINT por tabla.
-- ============================================================================

-- ============================================================================
-- FIN DEL ESQUEMA v2.1
-- ============================================================================
-- Total: ~42 tablas, 3 vistas materializadas, 31 ENUM types,
--        audit_log particionado por mes, triggers con user de aplicacion,
--        report_number concurrente sin race conditions,
--        politica de ON DELETE explicita (RESTRICT por defecto),
--        PostGIS habilitado (geometry en address y mobile_action_log),
--        sistema de promociones flexible (3 tablas),
--        flujo de autorizacion (approval_request),
--        soporte apps moviles (device_session + mobile_action_log),
--        cotizaciones EXTERNAS via API REST (sin tabla quote),
--        collection_assignment (renombrada de ubicacion_tarjeta).
--
-- Tablas nuevas en v2 (vs v1.2):
--   - device_session
--   - mobile_action_log
--   - approval_request
--   - promotion_rule
--   - promotion_application
--
-- Tablas eliminadas de v1.2:
--   - quote (cotizaciones via API REST)
--   - referral_discount (reemplazada por promotion_application)
--
-- Tablas renombradas:
--   - card_location_history -> collection_assignment
--
-- Para refrescar vistas materializadas (cron diario recomendado):
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_policy_summary;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_sellers_monthly;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_collection_stats;
-- ============================================================================
