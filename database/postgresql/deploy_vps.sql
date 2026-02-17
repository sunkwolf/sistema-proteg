-- =============================================================================
-- SCRIPT DE DESPLIEGUE: protegrt_crm en VPS (EasyPanel)
-- Generado: 2026-02-17
-- Base: schema.sql v2.1 + correcciones B9 + tabla payment_preapproval
-- =============================================================================
--
-- INSTRUCCIONES:
-- 1. Conectar a protegrt_crm en el VPS via DBeaver o pgAdmin
-- 2. Ejecutar este script completo (F5 en DBeaver, o play en pgAdmin)
-- 3. Si PostGIS falla, ver notas al final
--
-- NOTA: Este script es idempotente para extensiones (IF NOT EXISTS)
--       pero NO para tablas (fallan si ya existen)
-- =============================================================================

BEGIN;

-- =============================================================================
-- EXTENSIONES
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;
COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';

-- =============================================================================
-- ENUM TYPES (32 tipos)
-- =============================================================================

CREATE TYPE public.app_type_enum AS ENUM (
    'collector_app', 'seller_app', 'adjuster_app', 'desktop'
);

CREATE TYPE public.approval_request_type AS ENUM (
    'policy_submission', 'payment_submission'
);

CREATE TYPE public.approval_status_type AS ENUM (
    'pending', 'approved', 'rejected', 'cancelled'
);

CREATE TYPE public.card_status_type AS ENUM (
    'active', 'paid_off', 'cancelled', 'recovery'
);

CREATE TYPE public.coverage_category_type AS ENUM (
    'liability', 'comprehensive', 'platform'
);

CREATE TYPE public.device_type_enum AS ENUM (
    'android', 'ios', 'web'
);

CREATE TYPE public.endorsement_status_type AS ENUM (
    'pending', 'approved', 'rejected', 'applied'
);

CREATE TYPE public.endorsement_type_enum AS ENUM (
    'plate_change', 'vehicle_change', 'coverage_change', 'contractor_change', 'rights_transfer'
);

CREATE TYPE public.entity_status_type AS ENUM (
    'active', 'inactive'
);

CREATE TYPE public.gender_type AS ENUM (
    'male', 'female'
);

CREATE TYPE public.incident_type_enum AS ENUM (
    'collision', 'theft', 'total_loss', 'vandalism', 'natural_disaster', 'other'
);

CREATE TYPE public.marital_status_type AS ENUM (
    'single', 'married', 'divorced', 'widowed', 'common_law'
);

CREATE TYPE public.message_channel_type AS ENUM (
    'whatsapp', 'telegram', 'sms', 'email'
);

CREATE TYPE public.message_delivery_status_type AS ENUM (
    'queued', 'sent', 'delivered', 'read', 'failed'
);

CREATE TYPE public.message_type_enum AS ENUM (
    'reminder', 'overdue'
);

CREATE TYPE public.notification_period_type AS ENUM (
    'renewal_15d', 'renewal_3d', 'expired_7d', 'expired_30d'
);

CREATE TYPE public.office_delivery_type AS ENUM (
    'pending', 'delivered'
);

CREATE TYPE public.payment_method_type AS ENUM (
    'cash', 'deposit', 'transfer', 'crucero', 'konfio', 'terminal_banorte'
);

CREATE TYPE public.payment_plan_type AS ENUM (
    'cash', 'cash_2_installments', 'monthly_7',
    'quarterly_4', 'semiannual_2', 'monthly_12'
);

CREATE TYPE public.payment_proposal_status_type AS ENUM (
    'active', 'applied', 'discarded'
);

CREATE TYPE public.payment_status_type AS ENUM (
    'pending', 'paid', 'late', 'overdue', 'cancelled'
);

CREATE TYPE public.policy_status_type AS ENUM (
    'active', 'pending', 'morosa', 'pre_effective', 'expired', 'cancelled', 'suspended', 'no_status'
);

CREATE TYPE public.preapproval_status_type AS ENUM (
    'pending_approval', 'approved', 'rejected'
);

CREATE TYPE public.promotion_discount_type AS ENUM (
    'percentage', 'fixed_amount', 'free_months', 'zero_down_payment'
);

CREATE TYPE public.receipt_status_type AS ENUM (
    'unassigned', 'assigned', 'used', 'delivered', 'cancelled', 'lost', 'cancelled_undelivered'
);

CREATE TYPE public.renewal_status_type AS ENUM (
    'pending', 'completed', 'rejected'
);

CREATE TYPE public.responsibility_type AS ENUM (
    'not_responsible', 'at_fault', 'shared'
);

CREATE TYPE public.seller_class_type AS ENUM (
    'seller', 'collaborator'
);

CREATE TYPE public.service_status_type AS ENUM (
    'pending', 'in_progress', 'completed', 'cancelled'
);

CREATE TYPE public.service_type AS ENUM (
    'private', 'commercial'
);

CREATE TYPE public.shift_order_type AS ENUM (
    'first', 'second', 'third', 'rest'
);

CREATE TYPE public.vehicle_type_enum AS ENUM (
    'automobile', 'truck', 'suv', 'motorcycle', 'mototaxi'
);

CREATE TYPE public.workshop_pass_type_enum AS ENUM (
    'repair', 'valuation_payment', 'open_repair_valuation', 'agreed_payment', 'agreement'
);

-- =============================================================================
-- TABLES (52 tablas)
-- =============================================================================

-- --- Tablas base (sin FK a otras tablas) ---

CREATE TABLE public.municipality (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL,
    state character varying(50) DEFAULT 'Tabasco'::character varying NOT NULL,
    zip_codes jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_municipality_name UNIQUE (name)
);
COMMENT ON TABLE public.municipality IS 'Catalogo de municipios (enfocado en Tabasco)';

CREATE TABLE public.address (
    id SERIAL PRIMARY KEY,
    street character varying(200),
    exterior_number character varying(20),
    interior_number character varying(20),
    neighborhood character varying(100),
    zip_code character varying(10),
    municipality_id integer REFERENCES public.municipality(id),
    city character varying(100),
    state character varying(50) DEFAULT 'Tabasco'::character varying,
    full_address text,
    geom geometry(Point,4326),
    latitude numeric(10,7),
    longitude numeric(10,7),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.address IS 'Direcciones fisicas con geolocalizacion PostGIS';

CREATE TABLE public.department (
    id SERIAL PRIMARY KEY,
    name character varying(50) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_department_name UNIQUE (name)
);
COMMENT ON TABLE public.department IS 'Departamentos: Ventas, Cobranza, Siniestros, Admin';

CREATE TABLE public.role (
    id SERIAL PRIMARY KEY,
    name character varying(50) NOT NULL,
    description text,
    is_system boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_role_name UNIQUE (name)
);
COMMENT ON TABLE public.role IS 'Roles del sistema: admin, gerente_ventas, auxiliar, etc.';

CREATE TABLE public.permission (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_permission_name UNIQUE (name)
);
COMMENT ON TABLE public.permission IS '75+ permisos granulares: modulo.accion';

CREATE TABLE public.role_permission (
    role_id integer NOT NULL REFERENCES public.role(id) ON DELETE CASCADE,
    permission_id integer NOT NULL REFERENCES public.permission(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- --- Auth & Users ---

CREATE TABLE public.app_user (
    id SERIAL PRIMARY KEY,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_superuser boolean DEFAULT false NOT NULL,
    role_id integer REFERENCES public.role(id) ON DELETE SET NULL,
    department_id integer REFERENCES public.department(id) ON DELETE SET NULL,
    totp_secret character varying(64),
    totp_enabled boolean DEFAULT false NOT NULL,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    locked_until timestamp with time zone,
    last_login_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_user_username UNIQUE (username),
    CONSTRAINT uq_user_email UNIQUE (email)
);
COMMENT ON TABLE public.app_user IS 'Usuarios del sistema con auth JWT + 2FA';

CREATE TABLE public.session (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.app_user(id) ON DELETE CASCADE,
    token character varying(128) NOT NULL,
    refresh_token_hash character varying(128),
    ip_address character varying(45),
    user_agent text,
    is_active boolean DEFAULT true NOT NULL,
    app_type public.app_type_enum DEFAULT 'desktop'::public.app_type_enum NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_session_token UNIQUE (token)
);
COMMENT ON TABLE public.session IS 'Sesiones activas con refresh token hash';

CREATE TABLE public.device_session (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.app_user(id) ON DELETE CASCADE,
    device_id character varying(255) NOT NULL,
    device_name character varying(100),
    device_type public.device_type_enum NOT NULL,
    app_type public.app_type_enum NOT NULL,
    app_version character varying(20),
    os_version character varying(50),
    token character varying(255) NOT NULL,
    push_token character varying(255),
    is_active boolean DEFAULT true NOT NULL,
    last_location geometry(Point,4326),
    last_location_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_device_session_token UNIQUE (token)
);
COMMENT ON TABLE public.device_session IS 'Sesiones de dispositivos moviles con GPS';

-- --- Employees ---

CREATE TABLE public.employee (
    id SERIAL PRIMARY KEY,
    user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    code_name character varying(50) NOT NULL,
    full_name character varying(255) NOT NULL,
    phone character varying(20),
    telegram_id bigint,
    es_vendedor boolean DEFAULT false NOT NULL,
    es_cobrador boolean DEFAULT false NOT NULL,
    es_ajustador boolean DEFAULT false NOT NULL,
    seller_class public.seller_class_type,
    sales_target integer,
    receipt_limit integer DEFAULT 50 NOT NULL,
    hire_date date,
    termination_date date,
    curp character varying(18),
    rfc character varying(13),
    emergency_contact text,
    emergency_phone character varying(20),
    photo_url text,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_employee_code UNIQUE (code_name),
    CONSTRAINT uq_employee_user_id UNIQUE (user_id)
);
COMMENT ON TABLE public.employee IS 'Empleados: vendedor+cobrador+ajustador simultaneo';
COMMENT ON COLUMN public.employee.rfc IS 'RFC del empleado (12 moral, 13 fisica)';
COMMENT ON COLUMN public.employee.curp IS 'CURP del empleado (18 caracteres)';

CREATE TABLE public.employee_department (
    employee_id integer NOT NULL REFERENCES public.employee(id) ON DELETE CASCADE,
    department_id integer NOT NULL REFERENCES public.department(id) ON DELETE CASCADE,
    es_gerente boolean DEFAULT false NOT NULL,
    is_field_worker boolean DEFAULT false NOT NULL,
    assigned_at timestamp with time zone DEFAULT now() NOT NULL,
    PRIMARY KEY (employee_id, department_id)
);
COMMENT ON TABLE public.employee_department IS 'Relacion N:M empleado-departamento con flags gerente y campo/oficina';
COMMENT ON COLUMN public.employee_department.is_field_worker IS 'true=campo, false=oficina. Para gestion de vacaciones';

CREATE TABLE public.employee_permission_override (
    id SERIAL PRIMARY KEY,
    employee_id integer NOT NULL REFERENCES public.employee(id) ON DELETE CASCADE,
    permission_id integer NOT NULL REFERENCES public.permission(id) ON DELETE CASCADE,
    granted boolean DEFAULT true NOT NULL,
    granted_by integer REFERENCES public.app_user(id),
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_employee_permission UNIQUE (employee_id, permission_id)
);
COMMENT ON TABLE public.employee_permission_override IS 'Overrides individuales de permisos por empleado';

-- --- Clients ---

CREATE TABLE public.client (
    id SERIAL PRIMARY KEY,
    first_name character varying(100) NOT NULL,
    paternal_surname character varying(100) NOT NULL,
    maternal_surname character varying(100),
    phone_1 character varying(20),
    phone_2 character varying(20),
    email character varying(255),
    rfc character varying(13),
    gender public.gender_type,
    birth_date date,
    marital_status public.marital_status_type,
    address_id integer REFERENCES public.address(id),
    whatsapp_verified boolean DEFAULT false NOT NULL,
    whatsapp_phone character varying(20),
    occupation character varying(100),
    curp character varying(18),
    emergency_contact_name character varying(200),
    emergency_contact_phone character varying(20),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);
COMMENT ON TABLE public.client IS 'Clientes de la agencia con RFC y soft delete';
COMMENT ON COLUMN public.client.rfc IS 'RFC del cliente (12 chars persona moral, 13 chars persona fisica)';

-- --- Vehicles ---

CREATE TABLE public.vehicle (
    id SERIAL PRIMARY KEY,
    serial_number character varying(17) NOT NULL,
    plates character varying(15),
    brand character varying(50) NOT NULL,
    sub_brand character varying(50),
    model_year integer NOT NULL,
    color character varying(30),
    vehicle_type public.vehicle_type_enum,
    vehicle_key integer,
    service_type public.service_type,
    motor_number character varying(50),
    capacity integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_vehicle_serial UNIQUE (serial_number),
    CONSTRAINT chk_vehicle_key CHECK ((vehicle_key = ANY (ARRAY[101, 103, 105, 107, 108, 109]))),
    CONSTRAINT chk_model_year CHECK ((model_year >= 1900 AND model_year <= 2100))
);
COMMENT ON TABLE public.vehicle IS 'Vehiculos asegurados. Claves: 101=AUTO, 103=PICKUP, 105=CAMIONETA, 107=MOTO, 108=MOTOTAXI, 109=CAMION';

-- --- Coverages ---

CREATE TABLE public.coverage (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL,
    category public.coverage_category_type NOT NULL,
    vehicle_key integer NOT NULL,
    price numeric(12,2) DEFAULT 0.00 NOT NULL,
    commission_rate numeric(5,2),
    description text,
    benefits jsonb,
    exclusions jsonb,
    deductible_percentage numeric(5,2),
    sum_insured numeric(14,2),
    is_active boolean DEFAULT true NOT NULL,
    effective_from date,
    effective_until date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_coverage_price CHECK ((price >= (0)::numeric)),
    CONSTRAINT chk_coverage_vehicle_key CHECK ((vehicle_key = ANY (ARRAY[101, 103, 105, 107, 108, 109])))
);
COMMENT ON TABLE public.coverage IS 'Catalogo de coberturas por tipo de vehiculo. AMPLIA precio=0 (se cotiza individual)';

-- --- Policies ---

CREATE TABLE public.policy (
    id SERIAL PRIMARY KEY,
    folio character varying(50) NOT NULL,
    client_id integer NOT NULL REFERENCES public.client(id) ON DELETE RESTRICT,
    vehicle_id integer NOT NULL REFERENCES public.vehicle(id) ON DELETE RESTRICT,
    coverage_id integer NOT NULL REFERENCES public.coverage(id) ON DELETE RESTRICT,
    seller_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    renewal_folio character varying(50),
    effective_date date,
    expiration_date date,
    sale_date date,
    elaboration_date date,
    status public.policy_status_type DEFAULT 'active'::public.policy_status_type NOT NULL,
    payment_plan public.payment_plan_type,
    data_entry_user_id integer REFERENCES public.app_user(id),
    tow_services_available integer DEFAULT 0 NOT NULL,
    comments text,
    has_fraud_observation boolean DEFAULT false NOT NULL,
    has_payment_issues boolean DEFAULT false NOT NULL,
    payment_method public.payment_method_type,
    down_payment numeric(12,2),
    monthly_payment numeric(12,2),
    total_payments integer,
    paid_payments integer DEFAULT 0 NOT NULL,
    prima_neta numeric(12,2),
    prima_total numeric(12,2),
    derecho_poliza numeric(12,2),
    recargo numeric(12,2),
    iva numeric(12,2),
    quote_external_id character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_policy_folio UNIQUE (folio),
    CONSTRAINT chk_down_payment CHECK (((down_payment IS NULL) OR (down_payment >= (0)::numeric))),
    CONSTRAINT chk_monthly_payment CHECK (((monthly_payment IS NULL) OR (monthly_payment >= (0)::numeric))),
    CONSTRAINT chk_paid_payments CHECK ((paid_payments >= 0)),
    CONSTRAINT chk_prima_total CHECK (((prima_total IS NULL) OR (prima_total >= (0)::numeric)))
);
COMMENT ON TABLE public.policy IS 'Polizas de seguro vinculadas a vehiculo+cliente+vendedor';
COMMENT ON COLUMN public.policy.prima_total IS 'Costo total de la poliza (prima total)';
COMMENT ON COLUMN public.policy.quote_external_id IS 'Referencia al sistema de cotizaciones (NO hacer JOINs)';

-- --- Policy AMPLIA Detail ---

CREATE TABLE public.policy_amplia_detail (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE CASCADE,
    insured_value numeric(14,2) NOT NULL,
    deductible_percentage numeric(5,2) NOT NULL,
    annual_premium numeric(12,2) NOT NULL,
    theft_coverage boolean DEFAULT false NOT NULL,
    natural_disaster_coverage boolean DEFAULT false NOT NULL,
    agreed_value boolean DEFAULT false NOT NULL,
    eligible_no_responsible_incidents boolean DEFAULT true NOT NULL,
    eligible_no_fraud_observations boolean DEFAULT true NOT NULL,
    eligible_no_payment_issues boolean DEFAULT true NOT NULL,
    eligible_renewal_period_met boolean DEFAULT true NOT NULL,
    eligibility_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_amplia_policy UNIQUE (policy_id),
    CONSTRAINT chk_amplia_insured_value CHECK ((insured_value > (0)::numeric)),
    CONSTRAINT chk_amplia_deductible CHECK ((deductible_percentage >= (0)::numeric)),
    CONSTRAINT chk_amplia_premium CHECK ((annual_premium >= (0)::numeric))
);
COMMENT ON TABLE public.policy_amplia_detail IS 'Detalle AMPLIA/AMPLIA SELECT por poliza';

-- --- Payments ---

CREATE TABLE public.payment (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    payment_number integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    due_date date NOT NULL,
    paid_date date,
    status public.payment_status_type DEFAULT 'pending'::public.payment_status_type NOT NULL,
    payment_method public.payment_method_type,
    receipt_number character varying(50),
    collector_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    seller_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    reference character varying(100),
    surcharge numeric(12,2) DEFAULT 0.00 NOT NULL,
    discount numeric(12,2) DEFAULT 0.00 NOT NULL,
    total_paid numeric(12,2),
    office_delivery public.office_delivery_type DEFAULT 'pending'::public.office_delivery_type NOT NULL,
    office_delivery_date date,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_payment_amount CHECK ((amount > (0)::numeric)),
    CONSTRAINT chk_payment_surcharge CHECK ((surcharge >= (0)::numeric)),
    CONSTRAINT chk_payment_discount CHECK ((discount >= (0)::numeric))
);
COMMENT ON TABLE public.payment IS 'Pagos de polizas. Maquina de estados: pending->late->overdue->paid/cancelled';

CREATE TABLE public.payment_proposal (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    original_payment_id integer REFERENCES public.payment(id) ON DELETE RESTRICT,
    proposed_plan public.payment_plan_type NOT NULL,
    number_of_payments integer NOT NULL,
    amount_per_payment numeric(12,2) NOT NULL,
    first_due_date date NOT NULL,
    status public.payment_proposal_status_type DEFAULT 'active'::public.payment_proposal_status_type NOT NULL,
    reason text,
    collector_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    seller_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_proposal_amount CHECK ((amount_per_payment > (0)::numeric)),
    CONSTRAINT chk_proposal_payments CHECK ((number_of_payments > 0))
);
COMMENT ON TABLE public.payment_proposal IS 'Propuestas de cambio de plan de pago (contado a cuotas)';

-- --- Payment Pre-approval (NUEVO - App Cobrador) ---

CREATE TABLE public.payment_preapproval (
    id SERIAL PRIMARY KEY,
    policy_folio character varying(50) NOT NULL,
    collector_id integer NOT NULL REFERENCES public.employee(id) ON DELETE RESTRICT,
    amount numeric(12,2) NOT NULL,
    payment_method public.payment_method_type NOT NULL,
    collected_at timestamp with time zone NOT NULL,
    collector_notes text,
    receipt_photo_url text,
    status public.preapproval_status_type DEFAULT 'pending_approval'::public.preapproval_status_type NOT NULL,
    reviewed_by integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    reviewed_at timestamp with time zone,
    rejection_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_preapproval_amount CHECK ((amount > (0)::numeric))
);
COMMENT ON TABLE public.payment_preapproval IS 'Pre-aprobaciones de pago capturadas por cobradores en app movil';

-- --- Receipts ---

CREATE TABLE public.receipt (
    id SERIAL PRIMARY KEY,
    receipt_number character varying(50) NOT NULL,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    payment_id integer REFERENCES public.payment(id) ON DELETE SET NULL,
    collector_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    status public.receipt_status_type DEFAULT 'unassigned'::public.receipt_status_type NOT NULL,
    assigned_at timestamp with time zone,
    used_at timestamp with time zone,
    delivered_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    cancellation_reason text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_receipt_number UNIQUE (receipt_number)
);
COMMENT ON TABLE public.receipt IS 'Recibos de cobro fisicos y digitales';

CREATE TABLE public.receipt_loss_schedule (
    receipt_number character varying(50) PRIMARY KEY,
    collector_id integer NOT NULL,
    reported_at timestamp with time zone DEFAULT now() NOT NULL,
    reason text,
    resolved boolean DEFAULT false NOT NULL
);
COMMENT ON TABLE public.receipt_loss_schedule IS 'Registro de recibos reportados como perdidos';

-- --- Cards & Collections ---

CREATE TABLE public.card (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    card_number character varying(20),
    seller_id integer REFERENCES public.employee(id) ON DELETE SET NULL,
    current_holder integer,
    status public.card_status_type DEFAULT 'active'::public.card_status_type NOT NULL,
    total_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    paid_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    remaining_amount numeric(12,2) DEFAULT 0.00 NOT NULL,
    total_payments integer DEFAULT 0 NOT NULL,
    paid_payments integer DEFAULT 0 NOT NULL,
    next_due_date date,
    last_payment_date date,
    assigned_collector integer,
    assigned_at timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_card_amounts CHECK ((paid_amount >= (0)::numeric AND remaining_amount >= (0)::numeric))
);
COMMENT ON TABLE public.card IS 'Tarjetas de cobro vinculadas a polizas';

CREATE TABLE public.collection_assignment (
    id SERIAL PRIMARY KEY,
    card_id integer NOT NULL REFERENCES public.card(id) ON DELETE CASCADE,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    assigned_to integer NOT NULL,
    assigned_by integer,
    assigned_date date NOT NULL,
    returned_date date,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    collection_route character varying(100),
    priority integer DEFAULT 0 NOT NULL,
    visit_day character varying(20),
    visit_time character varying(20),
    collector_notes text,
    office_notes text,
    last_visit_date date,
    last_visit_result character varying(50),
    total_collected numeric(12,2) DEFAULT 0.00 NOT NULL,
    visits_made integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.collection_assignment IS 'Asignacion de tarjetas a cobradores con ruta';

CREATE TABLE public.visit_notice (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    card_id integer REFERENCES public.card(id) ON DELETE SET NULL,
    payment_id integer REFERENCES public.payment(id) ON DELETE SET NULL,
    visit_date date NOT NULL,
    visit_result character varying(50) NOT NULL,
    amount_collected numeric(12,2),
    collector_notes text,
    client_present boolean DEFAULT true NOT NULL,
    gps_latitude numeric(10,7),
    gps_longitude numeric(10,7),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_visit_amount CHECK (((amount_collected IS NULL) OR (amount_collected >= (0)::numeric)))
);
COMMENT ON TABLE public.visit_notice IS 'Avisos de visita del cobrador';

-- --- Cancellations ---

CREATE TABLE public.cancellation (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    cancellation_type character varying(10) NOT NULL,
    cancellation_date date NOT NULL,
    effective_date date,
    reason text NOT NULL,
    cancelled_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    refund_amount numeric(12,2),
    penalty_amount numeric(12,2),
    reactivation_eligible boolean DEFAULT false NOT NULL,
    reactivated boolean DEFAULT false NOT NULL,
    reactivation_date date,
    reactivation_conditions text,
    documents jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_cancellation_type CHECK ((cancellation_type = ANY (ARRAY['C1'::text, 'C2'::text, 'C3'::text, 'C4'::text, 'C5'::text]))),
    CONSTRAINT chk_cancel_refund CHECK (((refund_amount IS NULL) OR (refund_amount >= (0)::numeric)))
);
COMMENT ON TABLE public.cancellation IS 'Cancelaciones C1-C5 con opcion de reactivacion';

-- --- Endorsements & Renewals ---

CREATE TABLE public.endorsement (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    endorsement_type public.endorsement_type_enum NOT NULL,
    status public.endorsement_status_type DEFAULT 'pending'::public.endorsement_status_type NOT NULL,
    request_date date NOT NULL,
    effective_date date,
    change_details jsonb NOT NULL,
    previous_vehicle_id integer REFERENCES public.vehicle(id),
    new_contractor_id integer REFERENCES public.client(id),
    cost numeric(12,2),
    documents jsonb,
    requested_by_user_id integer,
    approved_by_user_id integer,
    whatsapp_notified boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_endorsement_cost CHECK (((cost IS NULL) OR (cost >= (0)::numeric)))
);
COMMENT ON TABLE public.endorsement IS '5 tipos de endoso: placas, vehiculo, cobertura, contratante, derechos';

CREATE TABLE public.renewal (
    id SERIAL PRIMARY KEY,
    old_policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    new_policy_id integer REFERENCES public.policy(id) ON DELETE SET NULL,
    status public.renewal_status_type DEFAULT 'pending'::public.renewal_status_type NOT NULL,
    detection_date date NOT NULL,
    renewal_date date,
    coverage_change text,
    price_change numeric(12,2),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.renewal IS 'Proceso de renovacion de polizas';

CREATE TABLE public.renewal_notification_log (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE CASCADE,
    notification_type public.notification_period_type NOT NULL,
    channel public.message_channel_type NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    delivered boolean DEFAULT false NOT NULL,
    response text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.renewal_notification_log IS 'Log de notificaciones de renovacion enviadas';

-- --- Incidents & Tow ---

CREATE TABLE public.adjuster (
    id SERIAL PRIMARY KEY,
    employee_id integer,
    code character varying(20) NOT NULL,
    name character varying(200) NOT NULL,
    phone character varying(20),
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    zone character varying(100),
    specialties jsonb,
    total_incidents integer DEFAULT 0 NOT NULL,
    avg_response_time_minutes integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_adjuster_code UNIQUE (code)
);
COMMENT ON TABLE public.adjuster IS 'Ajustadores de siniestros';

CREATE TABLE public.adjuster_shift (
    id SERIAL PRIMARY KEY,
    adjuster_id integer NOT NULL REFERENCES public.adjuster(id) ON DELETE CASCADE,
    shift_date date NOT NULL,
    shift_order public.shift_order_type NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    is_on_call boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_shift_date_adjuster UNIQUE (shift_date, adjuster_id)
);
COMMENT ON TABLE public.adjuster_shift IS 'Turnos de ajustadores: 1ro, 2do, 3ro, descanso';

CREATE TABLE public.incident (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    report_number character varying(50) NOT NULL,
    incident_type public.incident_type_enum NOT NULL,
    report_time timestamp with time zone NOT NULL,
    incident_date date,
    description text,
    requester_name character varying(200) NOT NULL,
    phone character varying(20),
    origin_address_id integer REFERENCES public.address(id) ON DELETE SET NULL,
    origin_description text,
    destination_description text,
    adjuster_id integer REFERENCES public.adjuster(id) ON DELETE RESTRICT,
    attended_by_user_id integer REFERENCES public.app_user(id),
    service_status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    responsibility public.responsibility_type,
    damage_description text,
    estimated_damage numeric(14,2),
    total_cost numeric(14,2),
    insurance_payout numeric(14,2),
    deductible_amount numeric(12,2),
    deductible_paid boolean DEFAULT false NOT NULL,
    third_party_name character varying(200),
    third_party_phone character varying(20),
    third_party_insurance character varying(100),
    third_party_policy character varying(50),
    police_report_number character varying(50),
    photos jsonb,
    documents jsonb,
    notes text,
    resolution text,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_incident_costs CHECK (((estimated_damage IS NULL) OR (estimated_damage >= (0)::numeric)))
);
COMMENT ON TABLE public.incident IS 'Siniestros vinculados a poliza';

CREATE TABLE public.incident_satisfaction_survey (
    id SERIAL PRIMARY KEY,
    incident_id integer NOT NULL REFERENCES public.incident(id) ON DELETE RESTRICT,
    overall_rating integer NOT NULL,
    adjuster_rating integer,
    response_time_rating integer,
    comments text,
    surveyed_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    surveyed_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_incident_survey UNIQUE (incident_id),
    CONSTRAINT chk_overall_rating CHECK ((overall_rating >= 1 AND overall_rating <= 5)),
    CONSTRAINT chk_adjuster_rating CHECK (((adjuster_rating IS NULL) OR (adjuster_rating >= 1 AND adjuster_rating <= 5))),
    CONSTRAINT chk_response_rating CHECK (((response_time_rating IS NULL) OR (response_time_rating >= 1 AND response_time_rating <= 5)))
);

CREATE TABLE public.tow_provider (
    id SERIAL PRIMARY KEY,
    name character varying(200) NOT NULL,
    phone character varying(20),
    contact_name character varying(200),
    address_id integer REFERENCES public.address(id) ON DELETE SET NULL,
    zone character varying(100),
    base_rate numeric(12,2),
    per_km_rate numeric(8,2),
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    rating numeric(3,2),
    total_services integer DEFAULT 0 NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.tow_provider IS 'Proveedores de servicio de grua';

CREATE TABLE public.tow_service (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    report_number character varying(50) NOT NULL,
    report_time timestamp with time zone NOT NULL,
    requester_name character varying(200) NOT NULL,
    phone character varying(20),
    origin_address_id integer REFERENCES public.address(id) ON DELETE SET NULL,
    origin_description text,
    destination_address_id integer REFERENCES public.address(id) ON DELETE SET NULL,
    destination_description text,
    distance_km numeric(8,2),
    tow_provider_id integer REFERENCES public.tow_provider(id) ON DELETE SET NULL,
    driver_name character varying(200),
    driver_phone character varying(20),
    unit_number character varying(20),
    attended_by_user_id integer REFERENCES public.app_user(id),
    service_status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    dispatch_time timestamp with time zone,
    arrival_time timestamp with time zone,
    completion_time timestamp with time zone,
    cost numeric(12,2),
    cost_covered_by_insurance numeric(12,2),
    cost_paid_by_client numeric(12,2),
    vehicle_condition_before text,
    vehicle_condition_after text,
    photos jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_tow_cost CHECK (((cost IS NULL) OR (cost >= (0)::numeric)))
);
COMMENT ON TABLE public.tow_service IS 'Servicios de grua vinculados a poliza';

CREATE TABLE public.tow_satisfaction_survey (
    id SERIAL PRIMARY KEY,
    tow_service_id integer NOT NULL REFERENCES public.tow_service(id) ON DELETE RESTRICT,
    overall_rating integer NOT NULL,
    driver_rating integer,
    response_time_rating integer,
    comments text,
    surveyed_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    surveyed_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_tow_survey UNIQUE (tow_service_id),
    CONSTRAINT chk_tow_overall_rating CHECK ((overall_rating >= 1 AND overall_rating <= 5)),
    CONSTRAINT chk_tow_driver_rating CHECK (((driver_rating IS NULL) OR (driver_rating >= 1 AND driver_rating <= 5))),
    CONSTRAINT chk_tow_response_rating CHECK (((response_time_rating IS NULL) OR (response_time_rating >= 1 AND response_time_rating <= 5)))
);

-- --- Medical & Workshop ---

CREATE TABLE public.hospital (
    id SERIAL PRIMARY KEY,
    name character varying(200) NOT NULL,
    phone character varying(20),
    address_id integer REFERENCES public.address(id),
    specialty character varying(100),
    emergency_available boolean DEFAULT false NOT NULL,
    contact_name character varying(200),
    agreement_active boolean DEFAULT false NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.medical_pass (
    id SERIAL PRIMARY KEY,
    incident_id integer NOT NULL REFERENCES public.incident(id) ON DELETE RESTRICT,
    hospital_id integer NOT NULL REFERENCES public.hospital(id) ON DELETE RESTRICT,
    pass_number character varying(50) NOT NULL,
    beneficiary_name character varying(200) NOT NULL,
    injury_description text,
    treatment_type character varying(100),
    estimated_cost numeric(12,2),
    actual_cost numeric(12,2),
    status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    authorized_by character varying(200),
    authorized_at timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_medical_costs CHECK (((estimated_cost IS NULL) OR (estimated_cost >= (0)::numeric)))
);

CREATE TABLE public.workshop (
    id SERIAL PRIMARY KEY,
    name character varying(200) NOT NULL,
    phone character varying(20),
    address_id integer REFERENCES public.address(id),
    specialty character varying(100),
    contact_name character varying(200),
    agreement_active boolean DEFAULT false NOT NULL,
    rating numeric(3,2),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.workshop_pass (
    id SERIAL PRIMARY KEY,
    incident_id integer NOT NULL REFERENCES public.incident(id) ON DELETE RESTRICT,
    workshop_id integer NOT NULL REFERENCES public.workshop(id) ON DELETE RESTRICT,
    pass_number character varying(50) NOT NULL,
    beneficiary_name character varying(100),
    pass_type public.workshop_pass_type_enum NOT NULL,
    vehicle_damages text,
    observations text,
    cost numeric(12,2),
    status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_workshop_cost CHECK (((cost IS NULL) OR (cost >= (0)::numeric)))
);
COMMENT ON TABLE public.workshop_pass IS 'Pases de taller emitidos en siniestros';

-- --- Promotions ---

CREATE TABLE public.promotion (
    id SERIAL PRIMARY KEY,
    name character varying(100) NOT NULL,
    description text,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    max_applications integer,
    current_applications integer DEFAULT 0 NOT NULL,
    conditions jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.promotion IS 'Promociones con fechas de vigencia';

CREATE TABLE public.promotion_rule (
    id SERIAL PRIMARY KEY,
    promotion_id integer NOT NULL REFERENCES public.promotion(id) ON DELETE CASCADE,
    discount_type public.promotion_discount_type NOT NULL,
    discount_value numeric(12,2) NOT NULL,
    applies_to_coverage_category public.coverage_category_type,
    applies_to_vehicle_key integer,
    applies_to_payment_plan public.payment_plan_type,
    min_policy_count integer,
    min_payment_amount numeric(12,2),
    conditions jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_rule_discount CHECK ((discount_value > (0)::numeric)),
    CONSTRAINT chk_rule_vehicle_key CHECK (((applies_to_vehicle_key IS NULL) OR (applies_to_vehicle_key = ANY (ARRAY[101, 103, 105, 107, 108, 109]))))
);

CREATE TABLE public.promotion_application (
    id SERIAL PRIMARY KEY,
    promotion_id integer NOT NULL REFERENCES public.promotion(id) ON DELETE RESTRICT,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE RESTRICT,
    promotion_rule_id integer NOT NULL REFERENCES public.promotion_rule(id) ON DELETE RESTRICT,
    applied_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    applied_at timestamp with time zone DEFAULT now() NOT NULL,
    discount_amount numeric(12,2) NOT NULL,
    free_months integer,
    zero_down_payment boolean DEFAULT false NOT NULL,
    original_amount numeric(12,2),
    final_amount numeric(12,2),
    referrer_policy_id integer REFERENCES public.policy(id) ON DELETE SET NULL,
    referrer_discount numeric(12,2),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_promo_application UNIQUE (promotion_id, policy_id, promotion_rule_id),
    CONSTRAINT chk_promo_discount CHECK ((discount_amount >= (0)::numeric))
);

CREATE TABLE public.commission_rate (
    id SERIAL PRIMARY KEY,
    role character varying(30) NOT NULL,
    level character varying(30) NOT NULL,
    coverage_id integer NOT NULL REFERENCES public.coverage(id) ON DELETE RESTRICT,
    rate_percentage numeric(5,2) NOT NULL,
    fixed_amount numeric(12,2),
    effective_from date,
    effective_until date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT uq_commission UNIQUE (role, level, coverage_id),
    CONSTRAINT chk_commission_rate CHECK ((rate_percentage >= (0)::numeric AND rate_percentage <= (100)::numeric))
);
COMMENT ON TABLE public.commission_rate IS 'Tabla de comisiones por rol, nivel y cobertura';

-- --- Notifications ---

CREATE TABLE public.sent_message (
    id SERIAL PRIMARY KEY,
    phone character varying(20) NOT NULL,
    message_type public.message_type_enum NOT NULL,
    channel public.message_channel_type DEFAULT 'whatsapp'::public.message_channel_type NOT NULL,
    content text NOT NULL,
    template_name character varying(100),
    template_params jsonb,
    policy_id integer REFERENCES public.policy(id) ON DELETE SET NULL,
    sent_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    external_message_id character varying(100),
    delivery_status public.message_delivery_status_type DEFAULT 'queued'::public.message_delivery_status_type NOT NULL,
    delivered_at timestamp with time zone,
    read_at timestamp with time zone,
    error_message text,
    retry_count integer DEFAULT 0 NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.sent_message IS 'Log de mensajes enviados: WhatsApp, Telegram, SMS, email';

CREATE TABLE public.policy_notification (
    id SERIAL PRIMARY KEY,
    policy_id integer NOT NULL REFERENCES public.policy(id) ON DELETE CASCADE,
    seller_id integer NOT NULL REFERENCES public.employee(id) ON DELETE CASCADE,
    notification_type character varying(50) NOT NULL,
    message text NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL,
    read_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.policy_notification IS 'Notificaciones internas por poliza a vendedores';

-- --- Audit & Logging ---

CREATE TABLE public.execution_log (
    id SERIAL PRIMARY KEY,
    job_name character varying(100) NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    status character varying(20) DEFAULT 'running'::character varying NOT NULL,
    records_processed integer DEFAULT 0 NOT NULL,
    records_updated integer DEFAULT 0 NOT NULL,
    records_failed integer DEFAULT 0 NOT NULL,
    error_details jsonb,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.execution_log IS 'Log de ejecucion de jobs (StatusUpdater, etc.)';

CREATE TABLE public.approval_request (
    id SERIAL PRIMARY KEY,
    request_type public.approval_request_type NOT NULL,
    reference_id integer NOT NULL,
    reference_type character varying(50) NOT NULL,
    submitted_by_user_id integer NOT NULL REFERENCES public.app_user(id) ON DELETE RESTRICT,
    submitted_from_device_id integer REFERENCES public.device_session(id) ON DELETE SET NULL,
    status public.approval_status_type DEFAULT 'pending'::public.approval_status_type NOT NULL,
    request_data jsonb NOT NULL,
    reviewed_by_user_id integer REFERENCES public.app_user(id) ON DELETE SET NULL,
    reviewed_at timestamp with time zone,
    review_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.approval_request IS 'Panel unificado de autorizacion: pagos + polizas';

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    table_name character varying(50) NOT NULL,
    record_id integer NOT NULL,
    action character varying(10) NOT NULL,
    old_data jsonb,
    new_data jsonb,
    changed_by integer,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    ip_address character varying(45)
) PARTITION BY RANGE (changed_at);
COMMENT ON TABLE public.audit_log IS 'Audit log particionado por anio';

CREATE SEQUENCE public.audit_log_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);

CREATE TABLE public.audit_log_2026 PARTITION OF public.audit_log
    FOR VALUES FROM ('2026-01-01 00:00:00-06') TO ('2027-01-01 00:00:00-06');

CREATE TABLE public.mobile_action_log (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.app_user(id) ON DELETE CASCADE,
    device_session_id integer REFERENCES public.device_session(id) ON DELETE CASCADE,
    action character varying(100) NOT NULL,
    module character varying(50) NOT NULL,
    reference_id integer,
    reference_type character varying(50),
    request_data jsonb,
    response_status integer,
    ip_address character varying(45),
    gps_latitude numeric(10,7),
    gps_longitude numeric(10,7),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
COMMENT ON TABLE public.mobile_action_log IS 'Log de acciones desde apps moviles';

-- --- Report sequences ---

CREATE TABLE public.report_number_sequence (
    prefix character varying(10) NOT NULL,
    date_part character varying(10) NOT NULL,
    last_number integer DEFAULT 0 NOT NULL,
    PRIMARY KEY (prefix),
    CONSTRAINT uq_report_seq UNIQUE (prefix, date_part)
);

-- --- Alembic version tracking ---

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL,
    PRIMARY KEY (version_num)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Audit
CREATE INDEX idx_audit_log_changed_at ON ONLY public.audit_log USING btree (changed_at);
CREATE INDEX idx_audit_log_table_record ON ONLY public.audit_log USING btree (table_name, record_id);

-- Address (PostGIS)
CREATE INDEX idx_address_geom ON public.address USING gist (geom);
CREATE INDEX idx_address_municipality ON public.address USING btree (municipality_id);

-- Adjuster
CREATE INDEX idx_adjuster_status ON public.adjuster USING btree (status);

-- Approval
CREATE INDEX idx_approval_request_status ON public.approval_request USING btree (status);
CREATE INDEX idx_approval_request_submitted_by ON public.approval_request USING btree (submitted_by_user_id);

-- Cancellation
CREATE INDEX idx_cancellation_date ON public.cancellation USING btree (cancellation_date);
CREATE INDEX idx_cancellation_policy ON public.cancellation USING btree (policy_id);
CREATE INDEX idx_cancellation_user ON public.cancellation USING btree (cancelled_by_user_id);

-- Card
CREATE INDEX idx_card_holder ON public.card USING btree (current_holder);
CREATE INDEX idx_card_policy ON public.card USING btree (policy_id);
CREATE INDEX idx_card_seller ON public.card USING btree (seller_id);
CREATE INDEX idx_card_status ON public.card USING btree (status);

-- Client
CREATE INDEX idx_client_deleted ON public.client USING btree (deleted_at);
CREATE INDEX idx_client_name ON public.client USING btree (paternal_surname, first_name) WHERE (deleted_at IS NULL);
CREATE INDEX idx_client_name_trgm ON public.client USING gin (((((((first_name)::text || ' '::text) || (paternal_surname)::text) || ' '::text) || (COALESCE(maternal_surname, ''::character varying))::text)) public.gin_trgm_ops) WHERE (deleted_at IS NULL);
CREATE INDEX idx_client_phone ON public.client USING btree (phone_1) WHERE (deleted_at IS NULL);

-- Collection
CREATE INDEX idx_collection_assignment_assigned ON public.collection_assignment USING btree (assigned_to);
CREATE INDEX idx_collection_assignment_card ON public.collection_assignment USING btree (card_id);
CREATE INDEX idx_collection_assignment_policy ON public.collection_assignment USING btree (policy_id);

-- Coverage
CREATE INDEX idx_coverage_active ON public.coverage USING btree (is_active) WHERE (is_active = true);
CREATE INDEX idx_coverage_name ON public.coverage USING btree (name);
CREATE INDEX idx_coverage_vehicle_key ON public.coverage USING btree (vehicle_key);

-- Device session
CREATE INDEX idx_device_session_active ON public.device_session USING btree (is_active, user_id) WHERE (is_active = true);
CREATE INDEX idx_device_session_device ON public.device_session USING btree (device_id);
CREATE INDEX idx_device_session_user ON public.device_session USING btree (user_id);

-- Employee
CREATE INDEX idx_employee_status ON public.employee USING btree (status);
CREATE INDEX idx_employee_user ON public.employee USING btree (user_id);

-- Endorsement
CREATE INDEX idx_endorsement_details ON public.endorsement USING gin (change_details);
CREATE INDEX idx_endorsement_policy ON public.endorsement USING btree (policy_id);
CREATE INDEX idx_endorsement_status ON public.endorsement USING btree (status);

-- Incident
CREATE INDEX idx_incident_adjuster ON public.incident USING btree (adjuster_id);
CREATE INDEX idx_incident_policy ON public.incident USING btree (policy_id);
CREATE INDEX idx_incident_report_number ON public.incident USING btree (report_number);
CREATE INDEX idx_incident_report_time ON public.incident USING btree (report_time);
CREATE INDEX idx_incident_search ON public.incident USING gin (((((((report_number)::text || ' '::text) || (requester_name)::text) || ' '::text) || (COALESCE(phone, ''::character varying))::text)) public.gin_trgm_ops);
CREATE INDEX idx_incident_status ON public.incident USING btree (service_status);

-- Medical pass
CREATE INDEX idx_medical_pass_hospital ON public.medical_pass USING btree (hospital_id);
CREATE INDEX idx_medical_pass_incident ON public.medical_pass USING btree (incident_id);

-- Mobile action log
CREATE INDEX idx_mobile_action_log_created ON public.mobile_action_log USING btree (created_at);
CREATE INDEX idx_mobile_action_log_device ON public.mobile_action_log USING btree (device_session_id);
CREATE INDEX idx_mobile_action_log_user ON public.mobile_action_log USING btree (user_id);

-- Payment
CREATE INDEX idx_payment_collector ON public.payment USING btree (collector_id);
CREATE INDEX idx_payment_due_date ON public.payment USING btree (due_date);
CREATE INDEX idx_payment_late ON public.payment USING btree (policy_id, due_date) WHERE (status = 'late'::public.payment_status_type);
CREATE INDEX idx_payment_overdue ON public.payment USING btree (policy_id, due_date) WHERE (status = 'overdue'::public.payment_status_type);
CREATE INDEX idx_payment_pending ON public.payment USING btree (policy_id, due_date) WHERE (status = 'pending'::public.payment_status_type);
CREATE INDEX idx_payment_policy ON public.payment USING btree (policy_id);
CREATE INDEX idx_payment_policy_status_due ON public.payment USING btree (policy_id, status, due_date);
CREATE INDEX idx_payment_proposal_original ON public.payment_proposal USING btree (original_payment_id);
CREATE INDEX idx_payment_proposal_policy ON public.payment_proposal USING btree (policy_id);
CREATE INDEX idx_payment_receipt ON public.payment USING btree (receipt_number);
CREATE INDEX idx_payment_seller ON public.payment USING btree (seller_id);
CREATE INDEX idx_payment_status ON public.payment USING btree (status);

-- Payment preapproval
CREATE INDEX idx_preapproval_collector ON public.payment_preapproval USING btree (collector_id);
CREATE INDEX idx_preapproval_status ON public.payment_preapproval USING btree (status);
CREATE INDEX idx_preapproval_created ON public.payment_preapproval USING btree (created_at);

-- Policy
CREATE INDEX idx_policy_active ON public.policy USING btree (folio) WHERE (status = 'active'::public.policy_status_type);
CREATE INDEX idx_policy_client ON public.policy USING btree (client_id);
CREATE INDEX idx_policy_coverage ON public.policy USING btree (coverage_id);
CREATE INDEX idx_policy_elaboration ON public.policy USING btree (elaboration_date);
CREATE INDEX idx_policy_expiration ON public.policy USING btree (expiration_date);
CREATE INDEX idx_policy_folio ON public.policy USING btree (folio);
CREATE INDEX idx_policy_fraud ON public.policy USING btree (has_fraud_observation, has_payment_issues) WHERE ((has_fraud_observation = true) OR (has_payment_issues = true));
CREATE INDEX idx_policy_morosa ON public.policy USING btree (folio, client_id) WHERE (status = 'morosa'::public.policy_status_type);
CREATE INDEX idx_policy_pending ON public.policy USING btree (folio) WHERE (status = 'pending'::public.policy_status_type);
CREATE INDEX idx_policy_pre_effective ON public.policy USING btree (folio, effective_date) WHERE (status = 'pre_effective'::public.policy_status_type);
CREATE INDEX idx_policy_renewal ON public.policy USING btree (renewal_folio);
CREATE INDEX idx_policy_seller ON public.policy USING btree (seller_id);
CREATE INDEX idx_policy_status ON public.policy USING btree (status);
CREATE INDEX idx_policy_vehicle ON public.policy USING btree (vehicle_id);

-- Policy AMPLIA detail
CREATE INDEX idx_amplia_eligibility ON public.policy_amplia_detail USING btree (eligible_no_responsible_incidents, eligible_no_fraud_observations, eligible_no_payment_issues, eligible_renewal_period_met);

-- Policy notification
CREATE INDEX idx_policy_notif_policy ON public.policy_notification USING btree (policy_id, notification_type);
CREATE INDEX idx_policy_notif_seller ON public.policy_notification USING btree (seller_id);

-- Promotion
CREATE INDEX idx_promo_app_policy ON public.promotion_application USING btree (policy_id);
CREATE INDEX idx_promo_app_promotion ON public.promotion_application USING btree (promotion_id);
CREATE INDEX idx_promo_app_referrer ON public.promotion_application USING btree (referrer_policy_id) WHERE (referrer_policy_id IS NOT NULL);
CREATE INDEX idx_promo_rule_promotion ON public.promotion_rule USING btree (promotion_id);
CREATE INDEX idx_promo_rule_type ON public.promotion_rule USING btree (discount_type);
CREATE INDEX idx_promotion_dates ON public.promotion USING btree (start_date, end_date);
CREATE INDEX idx_promotion_status ON public.promotion USING btree (status);

-- Receipt
CREATE INDEX idx_receipt_collector ON public.receipt USING btree (collector_id);
CREATE INDEX idx_receipt_number ON public.receipt USING btree (receipt_number);
CREATE INDEX idx_receipt_payment ON public.receipt USING btree (payment_id);
CREATE INDEX idx_receipt_status ON public.receipt USING btree (status);

-- Renewal
CREATE INDEX idx_renewal_new ON public.renewal USING btree (new_policy_id);
CREATE INDEX idx_renewal_notif_policy ON public.renewal_notification_log USING btree (policy_id);
CREATE INDEX idx_renewal_old ON public.renewal USING btree (old_policy_id);

-- Sent message
CREATE INDEX idx_sent_msg_date ON public.sent_message USING btree (sent_at);
CREATE INDEX idx_sent_msg_delivery ON public.sent_message USING btree (delivery_status) WHERE (delivery_status = ANY (ARRAY['queued'::public.message_delivery_status_type, 'sent'::public.message_delivery_status_type]));
CREATE INDEX idx_sent_msg_failed ON public.sent_message USING btree (retry_count) WHERE (delivery_status = 'failed'::public.message_delivery_status_type);
CREATE INDEX idx_sent_msg_phone ON public.sent_message USING btree (phone, sent_at);
CREATE INDEX idx_sent_msg_policy ON public.sent_message USING btree (policy_id, message_type);

-- Session
CREATE INDEX idx_session_expires ON public.session USING btree (expires_at) WHERE (is_active = true);
CREATE INDEX idx_session_user ON public.session USING btree (user_id);

-- Shift
CREATE INDEX idx_shift_date ON public.adjuster_shift USING btree (shift_date);

-- Tow
CREATE INDEX idx_tow_policy ON public.tow_service USING btree (policy_id);
CREATE INDEX idx_tow_provider_fk ON public.tow_service USING btree (tow_provider_id);
CREATE INDEX idx_tow_provider_status ON public.tow_provider USING btree (status);
CREATE INDEX idx_tow_report_time ON public.tow_service USING btree (report_time);
CREATE INDEX idx_tow_search ON public.tow_service USING gin (((((report_number)::text || ' '::text) || (requester_name)::text)) public.gin_trgm_ops);
CREATE INDEX idx_tow_status ON public.tow_service USING btree (service_status);

-- User
CREATE INDEX idx_user_active ON public.app_user USING btree (is_active) WHERE (is_active = true);

-- Vehicle
CREATE INDEX idx_vehicle_plates ON public.vehicle USING btree (plates);
CREATE INDEX idx_vehicle_serial ON public.vehicle USING btree (serial_number);

-- Visit
CREATE INDEX idx_visit_card ON public.visit_notice USING btree (card_id);
CREATE INDEX idx_visit_policy ON public.visit_notice USING btree (policy_id);

-- Workshop
CREATE INDEX idx_workshop_pass_incident ON public.workshop_pass USING btree (incident_id);
CREATE INDEX idx_workshop_pass_workshop ON public.workshop_pass USING btree (workshop_id);

COMMIT;

-- =============================================================================
-- VERIFICACION
-- =============================================================================
-- Ejecuta esto despues para confirmar que todo se creo bien:
--
-- SELECT count(*) AS total_tablas FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
--
-- Resultado esperado: 52 tablas (51 originales + 1 particion audit_log_2026 + payment_preapproval)
--
-- SELECT typname, array_length(enumsortorder_array, 1) as valores
-- FROM (
--   SELECT t.typname, array_agg(e.enumsortorder) as enumsortorder_array
--   FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid
--   GROUP BY t.typname
-- ) sub ORDER BY typname;
-- =============================================================================
