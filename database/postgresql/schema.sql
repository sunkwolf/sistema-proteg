--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Debian 16.4-1.pgdg110+2)
-- Dumped by pg_dump version 16.4 (Debian 16.4-1.pgdg110+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: app_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.app_type_enum AS ENUM (
    'collector_app',
    'seller_app',
    'adjuster_app',
    'desktop'
);


--
-- Name: approval_request_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.approval_request_type AS ENUM (
    'policy_submission',
    'payment_submission'
);


--
-- Name: approval_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.approval_status_type AS ENUM (
    'pending',
    'approved',
    'rejected',
    'cancelled'
);


--
-- Name: card_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.card_status_type AS ENUM (
    'active',
    'paid_off',
    'cancelled',
    'recovery'
);


--
-- Name: coverage_category_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.coverage_category_type AS ENUM (
    'liability',
    'comprehensive',
    'platform'
);


--
-- Name: device_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.device_type_enum AS ENUM (
    'android',
    'ios',
    'web'
);


--
-- Name: endorsement_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.endorsement_status_type AS ENUM (
    'pending',
    'approved',
    'rejected',
    'applied'
);


--
-- Name: endorsement_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.endorsement_type_enum AS ENUM (
    'plate_change',
    'vehicle_change',
    'coverage_change',
    'contractor_change',
    'rights_transfer'
);


--
-- Name: entity_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.entity_status_type AS ENUM (
    'active',
    'inactive'
);


--
-- Name: gender_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.gender_type AS ENUM (
    'male',
    'female'
);


--
-- Name: incident_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.incident_type_enum AS ENUM (
    'collision',
    'theft',
    'total_loss',
    'vandalism',
    'natural_disaster',
    'other'
);


--
-- Name: marital_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.marital_status_type AS ENUM (
    'single',
    'married',
    'divorced',
    'widowed',
    'common_law'
);


--
-- Name: message_channel_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.message_channel_type AS ENUM (
    'whatsapp',
    'telegram',
    'sms',
    'email'
);


--
-- Name: message_delivery_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.message_delivery_status_type AS ENUM (
    'queued',
    'sent',
    'delivered',
    'read',
    'failed'
);


--
-- Name: message_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.message_type_enum AS ENUM (
    'reminder',
    'overdue'
);


--
-- Name: notification_period_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.notification_period_type AS ENUM (
    'renewal_15d',
    'renewal_3d',
    'expired_7d',
    'expired_30d'
);


--
-- Name: office_delivery_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.office_delivery_type AS ENUM (
    'pending',
    'delivered'
);


--
-- Name: payment_method_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_method_type AS ENUM (
    'cash',
    'deposit',
    'transfer',
    'crucero',
    'konfio',
    'terminal_banorte'
);


--
-- Name: payment_plan_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_plan_type AS ENUM (
    'cash',
    'cash_2_installments',
    'monthly_7',
    'quarterly_4',
    'semiannual_2',
    'monthly_12'
);


--
-- Name: preapproval_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.preapproval_status_type AS ENUM (
    'pending_approval',
    'approved',
    'rejected'
);


--
-- Name: payment_proposal_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_proposal_status_type AS ENUM (
    'active',
    'applied',
    'discarded'
);


--
-- Name: payment_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.payment_status_type AS ENUM (
    'pending',
    'paid',
    'late',
    'overdue',
    'cancelled'
);


--
-- Name: policy_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.policy_status_type AS ENUM (
    'active',
    'pending',
    'morosa',
    'pre_effective',
    'expired',
    'cancelled',
    'suspended',
    'no_status'
);


--
-- Name: promotion_discount_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.promotion_discount_type AS ENUM (
    'percentage',
    'fixed_amount',
    'free_months',
    'zero_down_payment'
);


--
-- Name: receipt_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.receipt_status_type AS ENUM (
    'unassigned',
    'assigned',
    'used',
    'delivered',
    'cancelled',
    'lost',
    'cancelled_undelivered'
);


--
-- Name: renewal_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.renewal_status_type AS ENUM (
    'pending',
    'completed',
    'rejected'
);


--
-- Name: responsibility_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.responsibility_type AS ENUM (
    'not_responsible',
    'at_fault',
    'shared'
);


--
-- Name: seller_class_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.seller_class_type AS ENUM (
    'seller',
    'collaborator'
);


--
-- Name: service_status_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.service_status_type AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'cancelled'
);


--
-- Name: service_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.service_type AS ENUM (
    'private',
    'commercial'
);


--
-- Name: shift_order_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.shift_order_type AS ENUM (
    'first',
    'second',
    'third',
    'rest'
);


--
-- Name: vehicle_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.vehicle_type_enum AS ENUM (
    'automobile',
    'truck',
    'suv',
    'motorcycle',
    'mototaxi'
);


--
-- Name: workshop_pass_type_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.workshop_pass_type_enum AS ENUM (
    'repair',
    'valuation_payment',
    'open_repair_valuation',
    'agreed_payment',
    'agreement'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: address; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.address (
    id bigint NOT NULL,
    street character varying(150) NOT NULL,
    exterior_number character varying(10),
    interior_number character varying(10),
    cross_street_1 character varying(100),
    cross_street_2 character varying(100),
    neighborhood character varying(100),
    municipality_id bigint,
    postal_code character varying(10),
    geom public.geometry(Point,4326),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE address; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.address IS 'Direcciones normalizadas con PostGIS para consultas espaciales y futuro pgRouting';


--
-- Name: COLUMN address.postal_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.address.postal_code IS 'Codigo postal como texto para preservar ceros a la izquierda';


--
-- Name: COLUMN address.geom; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.address.geom IS 'Punto geografico WGS84 (lon, lat). Insertar con ST_SetSRID(ST_MakePoint(lon, lat), 4326)';


--
-- Name: address_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.address_id_seq OWNED BY public.address.id;


--
-- Name: adjuster; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.adjuster (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    phone character varying(20),
    telegram_id bigint NOT NULL,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE adjuster; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.adjuster IS 'Ajustadores de siniestros';


--
-- Name: adjuster_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.adjuster_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: adjuster_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.adjuster_id_seq OWNED BY public.adjuster.id;


--
-- Name: adjuster_shift; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.adjuster_shift (
    id integer NOT NULL,
    shift_date date NOT NULL,
    adjuster_id integer NOT NULL,
    shift_order public.shift_order_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE adjuster_shift; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.adjuster_shift IS 'Asignacion de guardias diarias a ajustadores';


--
-- Name: COLUMN adjuster_shift.shift_order; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.adjuster_shift.shift_order IS 'first=1ra guardia, second=2da, third=3ra, rest=descanso';


--
-- Name: adjuster_shift_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.adjuster_shift_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: adjuster_shift_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.adjuster_shift_id_seq OWNED BY public.adjuster_shift.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: app_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.app_user (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(100),
    department_id integer,
    role_id integer,
    is_active boolean DEFAULT true NOT NULL,
    last_login_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE app_user; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.app_user IS 'Usuarios del sistema (app_user para evitar conflicto con palabra reservada user)';


--
-- Name: COLUMN app_user.password_hash; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.app_user.password_hash IS 'Hash bcrypt de la contrasena';


--
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.app_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- Name: approval_request; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.approval_request (
    id integer NOT NULL,
    request_type public.approval_request_type NOT NULL,
    status public.approval_status_type DEFAULT 'pending'::public.approval_status_type NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer,
    payload jsonb NOT NULL,
    submitted_by_user_id integer NOT NULL,
    submitted_from_device_id integer,
    reviewed_by_user_id integer,
    review_notes text,
    submitted_at timestamp with time zone DEFAULT now() NOT NULL,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: approval_request_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.approval_request_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: approval_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.approval_request_id_seq OWNED BY public.approval_request.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log (
    id bigint NOT NULL,
    table_name character varying(63) NOT NULL,
    record_id integer NOT NULL,
    action character varying(10) NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_by_user_id integer,
    changed_by character varying(100),
    changed_at timestamp with time zone DEFAULT now() NOT NULL
)
PARTITION BY RANGE (changed_at);


--
-- Name: audit_log_2026; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_log_2026 (
    id bigint NOT NULL,
    table_name character varying(63) NOT NULL,
    record_id integer NOT NULL,
    action character varying(10) NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_by_user_id integer,
    changed_by character varying(100),
    changed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.audit_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.audit_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: cancellation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cancellation (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    cancellation_date date NOT NULL,
    reason character varying(255),
    code character varying(45),
    payments_made integer DEFAULT 0,
    cancelled_by_user_id integer,
    notification_sent_seller boolean DEFAULT false NOT NULL,
    notification_sent_collector boolean DEFAULT false NOT NULL,
    notification_sent_client boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_cancellation_payments CHECK ((payments_made >= 0))
);


--
-- Name: TABLE cancellation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.cancellation IS 'Registro de cancelaciones de polizas';


--
-- Name: cancellation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cancellation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cancellation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cancellation_id_seq OWNED BY public.cancellation.id;


--
-- Name: card; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.card (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    current_holder character varying(50) NOT NULL,
    assignment_date date NOT NULL,
    seller_id integer,
    status public.card_status_type DEFAULT 'active'::public.card_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE card; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.card IS 'Tarjetas de seguro fisicas asignadas a polizas';


--
-- Name: COLUMN card.current_holder; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.card.current_holder IS 'Persona que tiene fisicamente la tarjeta (cobrador, vendedor, oficina)';


--
-- Name: card_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.card_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: card_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.card_id_seq OWNED BY public.card.id;


--
-- Name: client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client (
    id bigint NOT NULL,
    first_name character varying(50) NOT NULL,
    paternal_surname character varying(50) NOT NULL,
    maternal_surname character varying(50),
    rfc character varying(13),
    birth_date date,
    gender public.gender_type,
    marital_status public.marital_status_type,
    address_id bigint,
    phone_1 character varying(20),
    phone_2 character varying(20),
    email character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: TABLE client; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.client IS 'Clientes / contratantes de polizas';


--
-- Name: COLUMN client.rfc; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.client.rfc IS 'RFC del cliente (12 chars persona moral, 13 chars persona fisica)';


--
-- Name: COLUMN client.deleted_at; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.client.deleted_at IS 'Soft delete: NULL = activo, fecha = eliminado';


--
-- Name: client_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.client_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.client_id_seq OWNED BY public.client.id;


--
-- Name: collection_assignment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collection_assignment (
    id integer NOT NULL,
    card_id integer NOT NULL,
    policy_id integer NOT NULL,
    assigned_to character varying(50) NOT NULL,
    zone character varying(50),
    route character varying(50),
    assignment_date date NOT NULL,
    observations text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE collection_assignment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.collection_assignment IS 'Asignacion de cobranza: a quien se asigna cobrar cada poliza, en que zona/ruta. Antes ubicacion_tarjeta en MySQL.';


--
-- Name: COLUMN collection_assignment.assigned_to; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.collection_assignment.assigned_to IS 'Persona asignada para cobrar (cobrador o vendedor)';


--
-- Name: COLUMN collection_assignment.zone; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.collection_assignment.zone IS 'Zona de cobranza asignada';


--
-- Name: COLUMN collection_assignment.route; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.collection_assignment.route IS 'Ruta de cobranza asignada';


--
-- Name: collection_assignment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.collection_assignment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: collection_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.collection_assignment_id_seq OWNED BY public.collection_assignment.id;


--
-- Name: commission_rate; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commission_rate (
    id integer NOT NULL,
    role public.seller_class_type NOT NULL,
    level integer NOT NULL,
    coverage_id integer NOT NULL,
    percentage numeric(5,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_commission_level CHECK ((level > 0)),
    CONSTRAINT chk_commission_pct CHECK (((percentage >= (0)::numeric) AND (percentage <= (100)::numeric)))
);


--
-- Name: TABLE commission_rate; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.commission_rate IS 'Tabla de comisiones por rol, nivel y cobertura (pivotada desde MySQL)';


--
-- Name: commission_rate_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.commission_rate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: commission_rate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.commission_rate_id_seq OWNED BY public.commission_rate.id;


--
-- Name: coverage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.coverage (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    vehicle_type character varying(50) NOT NULL,
    vehicle_key integer NOT NULL,
    service_type public.service_type NOT NULL,
    category public.coverage_category_type DEFAULT 'liability'::public.coverage_category_type NOT NULL,
    cylinder_capacity character varying(20),
    credit_price numeric(12,2) NOT NULL,
    initial_payment numeric(12,2) NOT NULL,
    cash_price numeric(12,2) NOT NULL,
    tow_services_included integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_coverage_prices CHECK (((credit_price >= (0)::numeric) AND (initial_payment >= (0)::numeric) AND (cash_price >= (0)::numeric))),
    CONSTRAINT chk_coverage_tow CHECK ((tow_services_included >= 0))
);


--
-- Name: TABLE coverage; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.coverage IS 'Catalogo de coberturas con precios por tipo de vehiculo y servicio';


--
-- Name: COLUMN coverage.name; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.coverage.name IS 'Nombre de la cobertura: AMPLIA, PLATINO, RC PREMIUM, RC INTERMEDIA, RC BASICA, PLATAFORMA N, PLATAFORMA A';


--
-- Name: COLUMN coverage.vehicle_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.coverage.vehicle_type IS 'Tipo de vehiculo: AUTOMOVIL, PICK UP, CAMIONETA, MOTOCICLETA, MOTOTAXI (VARCHAR para mantener valores originales MySQL)';


--
-- Name: COLUMN coverage.vehicle_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.coverage.vehicle_key IS 'Codigo INTERNO del tipo de vehiculo: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA. NO es catalogo externo.';


--
-- Name: COLUMN coverage.cylinder_capacity; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.coverage.cylinder_capacity IS 'Solo para MOTOCICLETA. Ej: "901 A 1800 CC". NULL para otros vehiculos.';


--
-- Name: COLUMN coverage.credit_price; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.coverage.credit_price IS 'Precio a credito. AMPLIA = 0.00 (se cotiza individualmente por vehiculo).';


--
-- Name: coverage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.coverage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: coverage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.coverage_id_seq OWNED BY public.coverage.id;


--
-- Name: department; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.department (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE department; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.department IS 'Departamentos de la organizacion';


--
-- Name: department_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.department_id_seq OWNED BY public.department.id;


--
-- Name: device_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.device_session (
    id integer NOT NULL,
    user_id integer NOT NULL,
    device_id character varying(255) NOT NULL,
    device_type public.device_type_enum NOT NULL,
    app_type public.app_type_enum NOT NULL,
    app_version character varying(20),
    push_token character varying(500),
    token character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE device_session; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.device_session IS 'Sesiones por dispositivo para apps moviles (cobradores, vendedores, ajustadores)';


--
-- Name: COLUMN device_session.device_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_session.device_id IS 'UUID unico del dispositivo, generado por la app movil';


--
-- Name: COLUMN device_session.app_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_session.app_type IS 'Tipo de app: collector_app, seller_app, adjuster_app, desktop';


--
-- Name: COLUMN device_session.push_token; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.device_session.push_token IS 'Token FCM/APNS para push notifications';


--
-- Name: device_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.device_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: device_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.device_session_id_seq OWNED BY public.device_session.id;


--
-- Name: employee; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee (
    id integer NOT NULL,
    user_id integer,
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
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: employee_department; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_department (
    employee_id integer NOT NULL,
    department_id integer NOT NULL,
    es_gerente boolean DEFAULT false NOT NULL,
    is_field_worker boolean DEFAULT false NOT NULL
);


--
-- Name: employee_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_id_seq OWNED BY public.employee.id;


--
-- Name: employee_permission_override; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_permission_override (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    permission_id integer NOT NULL,
    granted boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: employee_permission_override_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employee_permission_override_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employee_permission_override_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employee_permission_override_id_seq OWNED BY public.employee_permission_override.id;


--
-- Name: endorsement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.endorsement (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    endorsement_type public.endorsement_type_enum NOT NULL,
    request_date timestamp with time zone DEFAULT now() NOT NULL,
    application_date timestamp with time zone,
    status public.endorsement_status_type DEFAULT 'pending'::public.endorsement_status_type NOT NULL,
    change_details jsonb NOT NULL,
    comments text,
    new_contractor_id bigint,
    previous_vehicle_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE endorsement; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.endorsement IS 'Endosos (modificaciones) a polizas vigentes';


--
-- Name: COLUMN endorsement.change_details; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.endorsement.change_details IS 'Detalle de cambios en formato JSONB estructurado';


--
-- Name: endorsement_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.endorsement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: endorsement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.endorsement_id_seq OWNED BY public.endorsement.id;


--
-- Name: execution_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.execution_log (
    id integer NOT NULL,
    description character varying(255),
    executed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE execution_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.execution_log IS 'Log de ejecuciones de procesos automaticos';


--
-- Name: execution_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.execution_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: execution_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.execution_log_id_seq OWNED BY public.execution_log.id;


--
-- Name: hospital; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    address_id bigint,
    phone character varying(20),
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE hospital; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.hospital IS 'Hospitales convenidos para pases medicos';


--
-- Name: hospital_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hospital_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hospital_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hospital_id_seq OWNED BY public.hospital.id;


--
-- Name: incident; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident (
    id integer NOT NULL,
    policy_id integer,
    report_number character varying(20) NOT NULL,
    requester_name character varying(100) NOT NULL,
    phone character varying(20),
    origin_address_id bigint,
    incident_type public.incident_type_enum,
    description text,
    responsibility public.responsibility_type,
    client_misconduct boolean DEFAULT false NOT NULL,
    adjuster_id integer NOT NULL,
    report_time timestamp with time zone DEFAULT now() NOT NULL,
    contact_time timestamp with time zone,
    completion_time timestamp with time zone,
    attended_by_user_id integer,
    service_status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    satisfaction_rating smallint,
    comments text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_incident_rating CHECK (((satisfaction_rating IS NULL) OR ((satisfaction_rating >= 1) AND (satisfaction_rating <= 10))))
);


--
-- Name: TABLE incident; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.incident IS 'Reportes de siniestros vehiculares. FK a policy (un cliente puede tener multiples polizas).';


--
-- Name: COLUMN incident.policy_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.incident.policy_id IS 'FK a policy(id). Un cliente puede tener 3 polizas con folios distintos; el siniestro se liga a UNA poliza.';


--
-- Name: COLUMN incident.client_misconduct; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.incident.client_misconduct IS 'Comportamiento inadecuado del cliente durante el siniestro';


--
-- Name: COLUMN incident.satisfaction_rating; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.incident.satisfaction_rating IS 'Calificacion 1-10 del servicio';


--
-- Name: incident_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.incident_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: incident_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.incident_id_seq OWNED BY public.incident.id;


--
-- Name: incident_satisfaction_survey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_satisfaction_survey (
    id integer NOT NULL,
    incident_id integer NOT NULL,
    survey_date timestamp with time zone DEFAULT now() NOT NULL,
    response_time_rating smallint NOT NULL,
    service_rating smallint NOT NULL,
    overall_service_rating smallint NOT NULL,
    company_impression smallint NOT NULL,
    comments text,
    average_rating numeric(3,2) NOT NULL,
    surveyed_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_incident_survey_ratings CHECK ((((response_time_rating >= 1) AND (response_time_rating <= 10)) AND ((service_rating >= 1) AND (service_rating <= 10)) AND ((overall_service_rating >= 1) AND (overall_service_rating <= 10)) AND ((company_impression >= 1) AND (company_impression <= 10))))
);


--
-- Name: TABLE incident_satisfaction_survey; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.incident_satisfaction_survey IS 'Encuestas de satisfaccion para siniestros';


--
-- Name: incident_satisfaction_survey_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.incident_satisfaction_survey_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: incident_satisfaction_survey_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.incident_satisfaction_survey_id_seq OWNED BY public.incident_satisfaction_survey.id;


--
-- Name: medical_pass; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.medical_pass (
    id integer NOT NULL,
    incident_id integer NOT NULL,
    hospital_id integer NOT NULL,
    pass_number character varying(50) NOT NULL,
    beneficiary_name character varying(100),
    injuries text,
    observations text,
    cost numeric(12,2),
    status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_medical_cost CHECK (((cost IS NULL) OR (cost >= (0)::numeric)))
);


--
-- Name: TABLE medical_pass; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.medical_pass IS 'Pases medicos emitidos en siniestros';


--
-- Name: medical_pass_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.medical_pass_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: medical_pass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.medical_pass_id_seq OWNED BY public.medical_pass.id;


--
-- Name: mobile_action_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mobile_action_log (
    id bigint NOT NULL,
    device_session_id integer NOT NULL,
    user_id integer NOT NULL,
    action_type character varying(100) NOT NULL,
    entity_type character varying(50),
    entity_id integer,
    latitude numeric(10,8),
    longitude numeric(11,8),
    request_payload jsonb,
    response_status smallint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    geom public.geometry(Point,4326)
);


--
-- Name: mobile_action_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mobile_action_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mobile_action_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mobile_action_log_id_seq OWNED BY public.mobile_action_log.id;


--
-- Name: municipality; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.municipality (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    short_name character varying(50) NOT NULL,
    siga_code character varying(100)
);


--
-- Name: TABLE municipality; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.municipality IS 'Catalogo de municipios';


--
-- Name: COLUMN municipality.siga_code; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.municipality.siga_code IS 'Codigo del Sistema de Informacion Geografica';


--
-- Name: municipality_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.municipality_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: municipality_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.municipality_id_seq OWNED BY public.municipality.id;


--
-- Name: payment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    seller_id integer,
    collector_id integer,
    user_id integer,
    payment_number integer NOT NULL,
    receipt_number character varying(10),
    due_date date,
    actual_date date,
    amount numeric(12,2),
    payment_method public.payment_method_type,
    office_delivery_status public.office_delivery_type,
    office_delivery_date date,
    policy_delivered boolean DEFAULT false,
    comments text,
    status public.payment_status_type DEFAULT 'pending'::public.payment_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_payment_amount CHECK (((amount IS NULL) OR (amount >= (0)::numeric))),
    CONSTRAINT chk_payment_number CHECK ((payment_number > 0))
);


--
-- Name: TABLE payment; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.payment IS 'Pagos de polizas. Cada poliza tiene 1 a N pagos segun forma de pago.';


--
-- Name: COLUMN payment.policy_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.payment.policy_id IS 'FK a policy(id), no a folio. Relacion por PK tecnico.';


--
-- Name: COLUMN payment.collector_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.payment.collector_id IS 'FK al cobrador por ID numerico (antes era VARCHAR clave_cobrador)';


--
-- Name: COLUMN payment.receipt_number; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.payment.receipt_number IS 'Numero de recibo fisico asociado';


--
-- Name: COLUMN payment.policy_delivered; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.payment.policy_delivered IS 'Si la poliza fisica fue entregada al cliente con este pago';


--
-- Name: payment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_id_seq OWNED BY public.payment.id;


--
-- Name: payment_proposal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_proposal (
    id integer NOT NULL,
    original_payment_id integer NOT NULL,
    policy_id integer NOT NULL,
    seller_id integer,
    collector_id integer,
    user_id integer,
    payment_number integer NOT NULL,
    receipt_number character varying(10),
    due_date date,
    actual_date date,
    amount numeric(12,2),
    payment_method public.payment_method_type,
    office_delivery_status public.office_delivery_type,
    office_delivery_date date,
    policy_delivered boolean DEFAULT false,
    comments text,
    payment_status public.payment_status_type DEFAULT 'pending'::public.payment_status_type NOT NULL,
    draft_status public.payment_proposal_status_type DEFAULT 'active'::public.payment_proposal_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE payment_proposal; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.payment_proposal IS 'Propuestas de cobro pendientes de verificacion (antes pagos_temporales). NO son borradores: son pagos propuestos por cobradores que requieren aprobacion.';


--
-- Name: payment_proposal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_proposal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_proposal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_proposal_id_seq OWNED BY public.payment_proposal.id;


--
-- Name: payment_preapproval; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_preapproval (
    id integer NOT NULL,
    policy_folio character varying(50) NOT NULL,
    collector_id integer NOT NULL,
    amount numeric(12,2) NOT NULL,
    payment_method public.payment_method_type NOT NULL,
    collected_at timestamp with time zone NOT NULL,
    collector_notes text,
    receipt_photo_url text,
    status public.preapproval_status_type DEFAULT 'pending_approval'::public.preapproval_status_type NOT NULL,
    reviewed_by integer,
    reviewed_at timestamp with time zone,
    rejection_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_preapproval_amount CHECK ((amount > (0)::numeric))
);


--
-- Name: TABLE payment_preapproval; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.payment_preapproval IS 'Pre-aprobaciones de pago capturadas por cobradores en app movil';


--
-- Name: payment_preapproval_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_preapproval_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_preapproval_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_preapproval_id_seq OWNED BY public.payment_preapproval.id;


--
-- Name: permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permission (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE permission; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.permission IS 'Permisos individuales del sistema';


--
-- Name: permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.permission_id_seq OWNED BY public.permission.id;


--
-- Name: policy; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.policy (
    id integer NOT NULL,
    folio integer NOT NULL,
    renewal_folio integer,
    client_id bigint NOT NULL,
    vehicle_id integer NOT NULL,
    coverage_id integer NOT NULL,
    seller_id integer,
    service_type public.service_type,
    contract_folio integer,
    effective_date date,
    expiration_date date,
    sale_date date,
    elaboration_date date,
    status public.policy_status_type DEFAULT 'active'::public.policy_status_type NOT NULL,
    payment_plan public.payment_plan_type,
    data_entry_user_id integer,
    tow_services_available integer DEFAULT 0 NOT NULL,
    comments text,
    has_fraud_observation boolean DEFAULT false NOT NULL,
    has_payment_issues boolean DEFAULT false NOT NULL,
    contract_image_path character varying(500),
    prima_total numeric(12,2),
    quote_external_id character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_policy_dates CHECK (((expiration_date IS NULL) OR (effective_date IS NULL) OR (expiration_date >= effective_date))),
    CONSTRAINT chk_policy_tow CHECK ((tow_services_available >= 0))
);


--
-- Name: TABLE policy; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.policy IS 'Polizas de seguro vehicular. Tabla central del sistema.';


--
-- Name: COLUMN policy.folio; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.folio IS 'Numero de folio unico de negocio';


--
-- Name: COLUMN policy.renewal_folio; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.renewal_folio IS 'Folio de la poliza que fue renovada (NULL si es nueva)';


--
-- Name: COLUMN policy.data_entry_user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.data_entry_user_id IS 'Usuario que capturo la poliza (antes capturista)';


--
-- Name: COLUMN policy.has_fraud_observation; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.has_fraud_observation IS 'Marca de observacion de fraude para elegibilidad AMPLIA SELECT';


--
-- Name: COLUMN policy.has_payment_issues; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.has_payment_issues IS 'Marca de problemas de pago para elegibilidad AMPLIA SELECT';


--
-- Name: COLUMN policy.prima_total; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.prima_total IS 'Costo total de la poliza (prima total)';


--
-- Name: COLUMN policy.quote_external_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy.quote_external_id IS 'ID de la cotizacion en sistema externo (API REST). Las cotizaciones NO viven en esta BD.';


--
-- Name: policy_amplia_detail; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.policy_amplia_detail (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    quote_number character varying(20),
    coverage_type character varying(20) NOT NULL,
    commercial_value numeric(12,2) NOT NULL,
    damage_deductible numeric(12,2) NOT NULL,
    theft_deductible numeric(12,2) NOT NULL,
    civil_liability_deductible numeric(12,2),
    eligible_no_responsible_incidents boolean DEFAULT true NOT NULL,
    eligible_no_fraud_observations boolean DEFAULT true NOT NULL,
    eligible_no_payment_issues boolean DEFAULT true NOT NULL,
    eligible_renewal_period_met boolean DEFAULT false NOT NULL,
    eligibility_last_checked timestamp with time zone,
    eligibility_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_amplia_values CHECK (((commercial_value >= (0)::numeric) AND (damage_deductible >= (0)::numeric) AND (theft_deductible >= (0)::numeric)))
);


--
-- Name: TABLE policy_amplia_detail; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.policy_amplia_detail IS 'Detalles especificos de polizas AMPLIA, AMPLIA SELECT y PLATAFORMA';


--
-- Name: COLUMN policy_amplia_detail.coverage_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.policy_amplia_detail.coverage_type IS 'AMPLIA, AMPLIA SELECT, PLATAFORMA N, PLATAFORMA A';


--
-- Name: policy_amplia_detail_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.policy_amplia_detail_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: policy_amplia_detail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.policy_amplia_detail_id_seq OWNED BY public.policy_amplia_detail.id;


--
-- Name: policy_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.policy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: policy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.policy_id_seq OWNED BY public.policy.id;


--
-- Name: policy_notification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.policy_notification (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    seller_id integer NOT NULL,
    notification_type public.notification_period_type NOT NULL,
    sent_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE policy_notification; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.policy_notification IS 'Notificaciones enviadas a vendedores sobre polizas';


--
-- Name: policy_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.policy_notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: policy_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.policy_notification_id_seq OWNED BY public.policy_notification.id;


--
-- Name: promotion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promotion (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    start_date date,
    end_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_promotion_dates CHECK (((end_date IS NULL) OR (start_date IS NULL) OR (end_date >= start_date)))
);


--
-- Name: TABLE promotion; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.promotion IS 'Definicion de promociones. Cada promocion puede tener multiples reglas de descuento (promotion_rule).';


--
-- Name: promotion_application; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promotion_application (
    id integer NOT NULL,
    promotion_id integer NOT NULL,
    promotion_rule_id integer NOT NULL,
    policy_id integer NOT NULL,
    referrer_policy_id integer,
    discount_applied numeric(12,2) NOT NULL,
    applied_by_user_id integer,
    comments text,
    applied_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_promo_discount CHECK ((discount_applied >= (0)::numeric))
);


--
-- Name: TABLE promotion_application; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.promotion_application IS 'Registro de promociones efectivamente aplicadas a polizas';


--
-- Name: COLUMN promotion_application.referrer_policy_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_application.referrer_policy_id IS 'Poliza referente (solo para promociones de referidos)';


--
-- Name: COLUMN promotion_application.discount_applied; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_application.discount_applied IS 'Monto del descuento efectivamente aplicado';


--
-- Name: promotion_application_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.promotion_application_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: promotion_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.promotion_application_id_seq OWNED BY public.promotion_application.id;


--
-- Name: promotion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.promotion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: promotion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.promotion_id_seq OWNED BY public.promotion.id;


--
-- Name: promotion_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promotion_rule (
    id integer NOT NULL,
    promotion_id integer NOT NULL,
    discount_type public.promotion_discount_type NOT NULL,
    discount_value numeric(12,2) NOT NULL,
    applies_to_payment_number integer,
    min_payments integer,
    max_payments integer,
    coverage_ids jsonb,
    vehicle_types jsonb,
    requires_referral boolean DEFAULT false NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_rule_discount_value CHECK ((discount_value >= (0)::numeric)),
    CONSTRAINT chk_rule_payment_range CHECK (((min_payments IS NULL) OR (max_payments IS NULL) OR (min_payments <= max_payments)))
);


--
-- Name: TABLE promotion_rule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.promotion_rule IS 'Reglas de descuento para cada promocion. Multiples reglas por promocion.';


--
-- Name: COLUMN promotion_rule.discount_type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.discount_type IS 'Tipo: percentage (%), fixed_amount ($), free_months (meses gratis), zero_down_payment ($0 enganche)';


--
-- Name: COLUMN promotion_rule.discount_value; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.discount_value IS 'Valor: 15.00 para 15%, 500.00 para $500, 2 para 2 meses gratis, 0 para $0 enganche';


--
-- Name: COLUMN promotion_rule.applies_to_payment_number; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.applies_to_payment_number IS 'Numero de pago especifico donde aplica. NULL = aplica a todos los pagos elegibles.';


--
-- Name: COLUMN promotion_rule.coverage_ids; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.coverage_ids IS 'JSONB array de IDs de cobertura elegibles. Ej: [1,3,5]. NULL = todas.';


--
-- Name: COLUMN promotion_rule.vehicle_types; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.vehicle_types IS 'JSONB array de tipos de vehiculo elegibles. Ej: ["automobile","truck"]. NULL = todos.';


--
-- Name: COLUMN promotion_rule.requires_referral; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.promotion_rule.requires_referral IS 'Si requiere poliza referente (para promociones de referidos)';


--
-- Name: promotion_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.promotion_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: promotion_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.promotion_rule_id_seq OWNED BY public.promotion_rule.id;


--
-- Name: receipt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.receipt (
    id integer NOT NULL,
    receipt_number character varying(10) NOT NULL,
    policy_id integer,
    collector_id integer,
    payment_id integer,
    assignment_date date,
    usage_date date,
    delivery_date date,
    status public.receipt_status_type DEFAULT 'unassigned'::public.receipt_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE receipt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.receipt IS 'Recibos fisicos gestionados por cobradores';


--
-- Name: receipt_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.receipt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: receipt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.receipt_id_seq OWNED BY public.receipt.id;


--
-- Name: receipt_loss_schedule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.receipt_loss_schedule (
    receipt_number character varying(10) NOT NULL,
    deadline timestamp with time zone NOT NULL
);


--
-- Name: TABLE receipt_loss_schedule; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.receipt_loss_schedule IS 'Programacion de cambio a LOST para recibos no devueltos';


--
-- Name: renewal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.renewal (
    id integer NOT NULL,
    old_policy_id integer NOT NULL,
    new_policy_id integer,
    renewal_date date NOT NULL,
    status public.renewal_status_type DEFAULT 'pending'::public.renewal_status_type NOT NULL,
    comments text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE renewal; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.renewal IS 'Registro de renovaciones de polizas';


--
-- Name: renewal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.renewal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: renewal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.renewal_id_seq OWNED BY public.renewal.id;


--
-- Name: renewal_notification_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.renewal_notification_log (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    notification_type public.notification_period_type NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    sent_by character varying(50) DEFAULT 'system'::character varying NOT NULL
);


--
-- Name: TABLE renewal_notification_log; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.renewal_notification_log IS 'Log de notificaciones automaticas de renovacion';


--
-- Name: renewal_notification_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.renewal_notification_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: renewal_notification_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.renewal_notification_log_id_seq OWNED BY public.renewal_notification_log.id;


--
-- Name: report_number_sequence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.report_number_sequence (
    prefix character varying(10) NOT NULL,
    date_part character varying(8) NOT NULL,
    last_number integer DEFAULT 0 NOT NULL
);


--
-- Name: role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE role; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.role IS 'Roles de usuario en el sistema';


--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: role_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_permission (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: TABLE role_permission; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.role_permission IS 'Relacion muchos a muchos entre roles y permisos';


--
-- Name: sent_message; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sent_message (
    id integer NOT NULL,
    policy_id integer,
    phone character varying(20) NOT NULL,
    message_type public.message_type_enum NOT NULL,
    channel public.message_channel_type DEFAULT 'whatsapp'::public.message_channel_type NOT NULL,
    delivery_status public.message_delivery_status_type DEFAULT 'queued'::public.message_delivery_status_type NOT NULL,
    scheduled_at timestamp with time zone,
    sent_at timestamp with time zone,
    delivered_at timestamp with time zone,
    target_payment_date date,
    days_before_due integer,
    retry_count smallint DEFAULT 0 NOT NULL,
    max_retries smallint DEFAULT 3 NOT NULL,
    error_message text,
    external_message_id character varying(100),
    source_ip character varying(45),
    sent_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_msg_retries CHECK (((retry_count >= 0) AND (retry_count <= max_retries)))
);


--
-- Name: TABLE sent_message; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.sent_message IS 'Mensajes de cobranza y recordatorios con tracking de entrega (WhatsApp, Telegram, SMS, email)';


--
-- Name: COLUMN sent_message.channel; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sent_message.channel IS 'Canal de envio del mensaje';


--
-- Name: COLUMN sent_message.delivery_status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sent_message.delivery_status IS 'Estado de entrega: queued->sent->delivered->read o failed';


--
-- Name: COLUMN sent_message.external_message_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.sent_message.external_message_id IS 'ID del mensaje en el servicio externo (WhatsApp API, Telegram, etc.)';


--
-- Name: sent_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sent_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sent_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sent_message_id_seq OWNED BY public.sent_message.id;


--
-- Name: session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.session (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE session; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.session IS 'Sesiones de usuario (escritorio/web)';


--
-- Name: session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.session_id_seq OWNED BY public.session.id;


--
-- Name: tow_provider; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tow_provider (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    phone character varying(20),
    telegram_group_id bigint,
    contact_person character varying(100),
    address_id bigint,
    notes text,
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE tow_provider; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tow_provider IS 'Proveedores de servicios de grua (unifica tow_service_providers y tow_providers)';


--
-- Name: tow_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tow_provider_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tow_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tow_provider_id_seq OWNED BY public.tow_provider.id;


--
-- Name: tow_satisfaction_survey; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tow_satisfaction_survey (
    id integer NOT NULL,
    tow_service_id integer NOT NULL,
    survey_date timestamp with time zone DEFAULT now() NOT NULL,
    response_time_rating smallint NOT NULL,
    service_rating smallint NOT NULL,
    overall_service_rating smallint NOT NULL,
    company_impression smallint NOT NULL,
    comments text,
    average_rating numeric(3,2) NOT NULL,
    surveyed_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_tow_survey_ratings CHECK ((((response_time_rating >= 1) AND (response_time_rating <= 10)) AND ((service_rating >= 1) AND (service_rating <= 10)) AND ((overall_service_rating >= 1) AND (overall_service_rating <= 10)) AND ((company_impression >= 1) AND (company_impression <= 10))))
);


--
-- Name: TABLE tow_satisfaction_survey; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tow_satisfaction_survey IS 'Encuestas de satisfaccion para servicios de grua';


--
-- Name: tow_satisfaction_survey_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tow_satisfaction_survey_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tow_satisfaction_survey_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tow_satisfaction_survey_id_seq OWNED BY public.tow_satisfaction_survey.id;


--
-- Name: tow_service; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tow_service (
    id integer NOT NULL,
    policy_id integer,
    report_number character varying(20) NOT NULL,
    requester_name character varying(100) NOT NULL,
    phone character varying(20),
    origin_address_id bigint,
    destination_address_id bigint,
    vehicle_failure character varying(100) NOT NULL,
    load_weight integer,
    tow_provider_id integer,
    tow_cost numeric(12,2),
    extra_charge numeric(12,2),
    estimated_arrival_time timestamp with time zone,
    report_time timestamp with time zone DEFAULT now() NOT NULL,
    attended_by_user_id integer,
    contact_time timestamp with time zone,
    end_time timestamp with time zone,
    comments text,
    service_status public.service_status_type DEFAULT 'pending'::public.service_status_type NOT NULL,
    satisfaction_rating smallint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_tow_cost CHECK (((tow_cost IS NULL) OR (tow_cost >= (0)::numeric))),
    CONSTRAINT chk_tow_rating CHECK (((satisfaction_rating IS NULL) OR ((satisfaction_rating >= 1) AND (satisfaction_rating <= 10))))
);


--
-- Name: TABLE tow_service; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.tow_service IS 'Servicios de grua solicitados por asegurados. FK a policy (un cliente puede tener multiples polizas).';


--
-- Name: COLUMN tow_service.policy_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.tow_service.policy_id IS 'FK a policy(id). Un cliente puede tener 3 polizas; la grua se liga a UNA poliza especifica.';


--
-- Name: tow_service_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tow_service_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tow_service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tow_service_id_seq OWNED BY public.tow_service.id;


--
-- Name: vehicle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle (
    id integer NOT NULL,
    brand character varying(45) NOT NULL,
    model_type character varying(45),
    model_year character varying(10),
    color character varying(45),
    vehicle_key integer,
    seats integer,
    serial_number character varying(45),
    plates character varying(20),
    load_capacity character varying(15),
    vehicle_type public.vehicle_type_enum,
    cylinder_capacity character varying(25),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE vehicle; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.vehicle IS 'Vehiculos asegurados. Normalizado desde la tabla polizas de MySQL.';


--
-- Name: COLUMN vehicle.vehicle_key; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.vehicle.vehicle_key IS 'Clave INTERNA del tipo de vehiculo: 101=AUTOMOVIL, 103=PICK UP, 105=CAMIONETA. NO es catalogo externo.';


--
-- Name: vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vehicle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vehicle_id_seq OWNED BY public.vehicle.id;


--
-- Name: visit_notice; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.visit_notice (
    id integer NOT NULL,
    card_id integer,
    policy_id integer NOT NULL,
    visit_date date NOT NULL,
    comments text,
    payment_id integer,
    notice_number integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE visit_notice; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.visit_notice IS 'Avisos de visita para cobranza de tarjetas';


--
-- Name: visit_notice_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.visit_notice_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: visit_notice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.visit_notice_id_seq OWNED BY public.visit_notice.id;


--
-- Name: workshop; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workshop (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    address_id bigint,
    phone character varying(20),
    status public.entity_status_type DEFAULT 'active'::public.entity_status_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE workshop; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.workshop IS 'Talleres convenidos para reparacion vehicular';


--
-- Name: workshop_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.workshop_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: workshop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.workshop_id_seq OWNED BY public.workshop.id;


--
-- Name: workshop_pass; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workshop_pass (
    id integer NOT NULL,
    incident_id integer NOT NULL,
    workshop_id integer NOT NULL,
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


--
-- Name: TABLE workshop_pass; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.workshop_pass IS 'Pases de taller emitidos en siniestros';


--
-- Name: workshop_pass_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.workshop_pass_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: workshop_pass_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.workshop_pass_id_seq OWNED BY public.workshop_pass.id;


--
-- Name: audit_log_2026; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log ATTACH PARTITION public.audit_log_2026 FOR VALUES FROM ('2026-01-01 00:00:00-06') TO ('2027-01-01 00:00:00-06');


--
-- Name: address id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.address ALTER COLUMN id SET DEFAULT nextval('public.address_id_seq'::regclass);


--
-- Name: adjuster id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster ALTER COLUMN id SET DEFAULT nextval('public.adjuster_id_seq'::regclass);


--
-- Name: adjuster_shift id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster_shift ALTER COLUMN id SET DEFAULT nextval('public.adjuster_shift_id_seq'::regclass);


--
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- Name: approval_request id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_request ALTER COLUMN id SET DEFAULT nextval('public.approval_request_id_seq'::regclass);


--
-- Name: cancellation id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cancellation ALTER COLUMN id SET DEFAULT nextval('public.cancellation_id_seq'::regclass);


--
-- Name: card id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.card ALTER COLUMN id SET DEFAULT nextval('public.card_id_seq'::regclass);


--
-- Name: client id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client ALTER COLUMN id SET DEFAULT nextval('public.client_id_seq'::regclass);


--
-- Name: collection_assignment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collection_assignment ALTER COLUMN id SET DEFAULT nextval('public.collection_assignment_id_seq'::regclass);


--
-- Name: commission_rate id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_rate ALTER COLUMN id SET DEFAULT nextval('public.commission_rate_id_seq'::regclass);


--
-- Name: coverage id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coverage ALTER COLUMN id SET DEFAULT nextval('public.coverage_id_seq'::regclass);


--
-- Name: department id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department ALTER COLUMN id SET DEFAULT nextval('public.department_id_seq'::regclass);


--
-- Name: device_session id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_session ALTER COLUMN id SET DEFAULT nextval('public.device_session_id_seq'::regclass);


--
-- Name: employee id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee ALTER COLUMN id SET DEFAULT nextval('public.employee_id_seq'::regclass);


--
-- Name: employee_permission_override id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_permission_override ALTER COLUMN id SET DEFAULT nextval('public.employee_permission_override_id_seq'::regclass);


--
-- Name: endorsement id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endorsement ALTER COLUMN id SET DEFAULT nextval('public.endorsement_id_seq'::regclass);


--
-- Name: execution_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.execution_log ALTER COLUMN id SET DEFAULT nextval('public.execution_log_id_seq'::regclass);


--
-- Name: hospital id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital ALTER COLUMN id SET DEFAULT nextval('public.hospital_id_seq'::regclass);


--
-- Name: incident id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident ALTER COLUMN id SET DEFAULT nextval('public.incident_id_seq'::regclass);


--
-- Name: incident_satisfaction_survey id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_satisfaction_survey ALTER COLUMN id SET DEFAULT nextval('public.incident_satisfaction_survey_id_seq'::regclass);


--
-- Name: medical_pass id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_pass ALTER COLUMN id SET DEFAULT nextval('public.medical_pass_id_seq'::regclass);


--
-- Name: mobile_action_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mobile_action_log ALTER COLUMN id SET DEFAULT nextval('public.mobile_action_log_id_seq'::regclass);


--
-- Name: municipality id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipality ALTER COLUMN id SET DEFAULT nextval('public.municipality_id_seq'::regclass);


--
-- Name: payment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public.payment_id_seq'::regclass);


--
-- Name: payment_proposal id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal ALTER COLUMN id SET DEFAULT nextval('public.payment_proposal_id_seq'::regclass);


--
-- Name: payment_preapproval id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_preapproval ALTER COLUMN id SET DEFAULT nextval('public.payment_preapproval_id_seq'::regclass);


--
-- Name: permission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permission ALTER COLUMN id SET DEFAULT nextval('public.permission_id_seq'::regclass);


--
-- Name: policy id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy ALTER COLUMN id SET DEFAULT nextval('public.policy_id_seq'::regclass);


--
-- Name: policy_amplia_detail id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_amplia_detail ALTER COLUMN id SET DEFAULT nextval('public.policy_amplia_detail_id_seq'::regclass);


--
-- Name: policy_notification id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_notification ALTER COLUMN id SET DEFAULT nextval('public.policy_notification_id_seq'::regclass);


--
-- Name: promotion id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion ALTER COLUMN id SET DEFAULT nextval('public.promotion_id_seq'::regclass);


--
-- Name: promotion_application id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application ALTER COLUMN id SET DEFAULT nextval('public.promotion_application_id_seq'::regclass);


--
-- Name: promotion_rule id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_rule ALTER COLUMN id SET DEFAULT nextval('public.promotion_rule_id_seq'::regclass);


--
-- Name: receipt id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt ALTER COLUMN id SET DEFAULT nextval('public.receipt_id_seq'::regclass);


--
-- Name: renewal id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal ALTER COLUMN id SET DEFAULT nextval('public.renewal_id_seq'::regclass);


--
-- Name: renewal_notification_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal_notification_log ALTER COLUMN id SET DEFAULT nextval('public.renewal_notification_log_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: sent_message id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sent_message ALTER COLUMN id SET DEFAULT nextval('public.sent_message_id_seq'::regclass);


--
-- Name: session id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session ALTER COLUMN id SET DEFAULT nextval('public.session_id_seq'::regclass);


--
-- Name: tow_provider id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_provider ALTER COLUMN id SET DEFAULT nextval('public.tow_provider_id_seq'::regclass);


--
-- Name: tow_satisfaction_survey id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_satisfaction_survey ALTER COLUMN id SET DEFAULT nextval('public.tow_satisfaction_survey_id_seq'::regclass);


--
-- Name: tow_service id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service ALTER COLUMN id SET DEFAULT nextval('public.tow_service_id_seq'::regclass);


--
-- Name: vehicle id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN id SET DEFAULT nextval('public.vehicle_id_seq'::regclass);


--
-- Name: visit_notice id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visit_notice ALTER COLUMN id SET DEFAULT nextval('public.visit_notice_id_seq'::regclass);


--
-- Name: workshop id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop ALTER COLUMN id SET DEFAULT nextval('public.workshop_id_seq'::regclass);


--
-- Name: workshop_pass id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop_pass ALTER COLUMN id SET DEFAULT nextval('public.workshop_pass_id_seq'::regclass);


--
-- Name: address address_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_pkey PRIMARY KEY (id);


--
-- Name: adjuster adjuster_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster
    ADD CONSTRAINT adjuster_pkey PRIMARY KEY (id);


--
-- Name: adjuster_shift adjuster_shift_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster_shift
    ADD CONSTRAINT adjuster_shift_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: approval_request approval_request_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_request
    ADD CONSTRAINT approval_request_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id, changed_at);


--
-- Name: audit_log_2026 audit_log_2026_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_log_2026
    ADD CONSTRAINT audit_log_2026_pkey PRIMARY KEY (id, changed_at);


--
-- Name: cancellation cancellation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cancellation
    ADD CONSTRAINT cancellation_pkey PRIMARY KEY (id);


--
-- Name: card card_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.card
    ADD CONSTRAINT card_pkey PRIMARY KEY (id);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: collection_assignment collection_assignment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collection_assignment
    ADD CONSTRAINT collection_assignment_pkey PRIMARY KEY (id);


--
-- Name: commission_rate commission_rate_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_rate
    ADD CONSTRAINT commission_rate_pkey PRIMARY KEY (id);


--
-- Name: coverage coverage_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coverage
    ADD CONSTRAINT coverage_pkey PRIMARY KEY (id);


--
-- Name: department department_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT department_pkey PRIMARY KEY (id);


--
-- Name: device_session device_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_session
    ADD CONSTRAINT device_session_pkey PRIMARY KEY (id);


--
-- Name: employee_department employee_department_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_department
    ADD CONSTRAINT employee_department_pkey PRIMARY KEY (employee_id, department_id);


--
-- Name: employee_permission_override employee_permission_override_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_permission_override
    ADD CONSTRAINT employee_permission_override_pkey PRIMARY KEY (id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: endorsement endorsement_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endorsement
    ADD CONSTRAINT endorsement_pkey PRIMARY KEY (id);


--
-- Name: execution_log execution_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.execution_log
    ADD CONSTRAINT execution_log_pkey PRIMARY KEY (id);


--
-- Name: hospital hospital_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital
    ADD CONSTRAINT hospital_pkey PRIMARY KEY (id);


--
-- Name: incident incident_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident
    ADD CONSTRAINT incident_pkey PRIMARY KEY (id);


--
-- Name: incident_satisfaction_survey incident_satisfaction_survey_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_satisfaction_survey
    ADD CONSTRAINT incident_satisfaction_survey_pkey PRIMARY KEY (id);


--
-- Name: medical_pass medical_pass_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_pass
    ADD CONSTRAINT medical_pass_pkey PRIMARY KEY (id);


--
-- Name: mobile_action_log mobile_action_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mobile_action_log
    ADD CONSTRAINT mobile_action_log_pkey PRIMARY KEY (id);


--
-- Name: municipality municipality_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipality
    ADD CONSTRAINT municipality_pkey PRIMARY KEY (id);


--
-- Name: payment payment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_pkey PRIMARY KEY (id);


--
-- Name: payment_proposal payment_proposal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_pkey PRIMARY KEY (id);


--
-- Name: payment_preapproval payment_preapproval_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_preapproval
    ADD CONSTRAINT payment_preapproval_pkey PRIMARY KEY (id);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);


--
-- Name: policy_amplia_detail policy_amplia_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_amplia_detail
    ADD CONSTRAINT policy_amplia_detail_pkey PRIMARY KEY (id);


--
-- Name: policy_notification policy_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_notification
    ADD CONSTRAINT policy_notification_pkey PRIMARY KEY (id);


--
-- Name: policy policy_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_pkey PRIMARY KEY (id);


--
-- Name: promotion_application promotion_application_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_pkey PRIMARY KEY (id);


--
-- Name: promotion promotion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion
    ADD CONSTRAINT promotion_pkey PRIMARY KEY (id);


--
-- Name: promotion_rule promotion_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_rule
    ADD CONSTRAINT promotion_rule_pkey PRIMARY KEY (id);


--
-- Name: receipt_loss_schedule receipt_loss_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt_loss_schedule
    ADD CONSTRAINT receipt_loss_schedule_pkey PRIMARY KEY (receipt_number);


--
-- Name: receipt receipt_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt
    ADD CONSTRAINT receipt_pkey PRIMARY KEY (id);


--
-- Name: renewal_notification_log renewal_notification_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal_notification_log
    ADD CONSTRAINT renewal_notification_log_pkey PRIMARY KEY (id);


--
-- Name: renewal renewal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal
    ADD CONSTRAINT renewal_pkey PRIMARY KEY (id);


--
-- Name: report_number_sequence report_number_sequence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_number_sequence
    ADD CONSTRAINT report_number_sequence_pkey PRIMARY KEY (prefix);


--
-- Name: role_permission role_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: sent_message sent_message_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sent_message
    ADD CONSTRAINT sent_message_pkey PRIMARY KEY (id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: tow_provider tow_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_provider
    ADD CONSTRAINT tow_provider_pkey PRIMARY KEY (id);


--
-- Name: tow_satisfaction_survey tow_satisfaction_survey_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_satisfaction_survey
    ADD CONSTRAINT tow_satisfaction_survey_pkey PRIMARY KEY (id);


--
-- Name: tow_service tow_service_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_pkey PRIMARY KEY (id);


--
-- Name: adjuster uq_adjuster_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster
    ADD CONSTRAINT uq_adjuster_code UNIQUE (code);


--
-- Name: policy_amplia_detail uq_amplia_policy; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_amplia_detail
    ADD CONSTRAINT uq_amplia_policy UNIQUE (policy_id);


--
-- Name: commission_rate uq_commission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_rate
    ADD CONSTRAINT uq_commission UNIQUE (role, level, coverage_id);


--
-- Name: department uq_department_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department
    ADD CONSTRAINT uq_department_name UNIQUE (name);


--
-- Name: device_session uq_device_session_token; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_session
    ADD CONSTRAINT uq_device_session_token UNIQUE (token);


--
-- Name: employee uq_employee_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT uq_employee_code UNIQUE (code_name);


--
-- Name: employee_permission_override uq_employee_permission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_permission_override
    ADD CONSTRAINT uq_employee_permission UNIQUE (employee_id, permission_id);


--
-- Name: employee uq_employee_user_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT uq_employee_user_id UNIQUE (user_id);


--
-- Name: incident_satisfaction_survey uq_incident_survey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_satisfaction_survey
    ADD CONSTRAINT uq_incident_survey UNIQUE (incident_id);


--
-- Name: municipality uq_municipality_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipality
    ADD CONSTRAINT uq_municipality_name UNIQUE (name);


--
-- Name: permission uq_permission_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT uq_permission_name UNIQUE (name);


--
-- Name: policy uq_policy_folio; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT uq_policy_folio UNIQUE (folio);


--
-- Name: promotion_application uq_promo_application; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT uq_promo_application UNIQUE (promotion_id, policy_id, promotion_rule_id);


--
-- Name: receipt uq_receipt_number; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt
    ADD CONSTRAINT uq_receipt_number UNIQUE (receipt_number);


--
-- Name: report_number_sequence uq_report_seq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.report_number_sequence
    ADD CONSTRAINT uq_report_seq UNIQUE (prefix, date_part);


--
-- Name: role uq_role_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT uq_role_name UNIQUE (name);


--
-- Name: session uq_session_token; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT uq_session_token UNIQUE (token);


--
-- Name: adjuster_shift uq_shift_date_adjuster; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster_shift
    ADD CONSTRAINT uq_shift_date_adjuster UNIQUE (shift_date, adjuster_id);


--
-- Name: tow_satisfaction_survey uq_tow_survey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_satisfaction_survey
    ADD CONSTRAINT uq_tow_survey UNIQUE (tow_service_id);


--
-- Name: app_user uq_user_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT uq_user_email UNIQUE (email);


--
-- Name: app_user uq_user_username; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT uq_user_username UNIQUE (username);


--
-- Name: vehicle uq_vehicle_serial; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT uq_vehicle_serial UNIQUE (serial_number);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: visit_notice visit_notice_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visit_notice
    ADD CONSTRAINT visit_notice_pkey PRIMARY KEY (id);


--
-- Name: workshop_pass workshop_pass_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop_pass
    ADD CONSTRAINT workshop_pass_pkey PRIMARY KEY (id);


--
-- Name: workshop workshop_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop
    ADD CONSTRAINT workshop_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_log_changed_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_changed_at ON ONLY public.audit_log USING btree (changed_at);


--
-- Name: audit_log_2026_changed_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2026_changed_at_idx ON public.audit_log_2026 USING btree (changed_at);


--
-- Name: idx_audit_log_table_record; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_log_table_record ON ONLY public.audit_log USING btree (table_name, record_id);


--
-- Name: audit_log_2026_table_name_record_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX audit_log_2026_table_name_record_id_idx ON public.audit_log_2026 USING btree (table_name, record_id);


--
-- Name: idx_address_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_address_geom ON public.address USING gist (geom);


--
-- Name: idx_address_municipality; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_address_municipality ON public.address USING btree (municipality_id);


--
-- Name: idx_adjuster_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_adjuster_status ON public.adjuster USING btree (status);


--
-- Name: idx_amplia_eligibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_amplia_eligibility ON public.policy_amplia_detail USING btree (eligible_no_responsible_incidents, eligible_no_fraud_observations, eligible_no_payment_issues, eligible_renewal_period_met);


--
-- Name: idx_approval_request_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_approval_request_status ON public.approval_request USING btree (status);


--
-- Name: idx_approval_request_submitted_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_approval_request_submitted_by ON public.approval_request USING btree (submitted_by_user_id);


--
-- Name: idx_cancellation_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cancellation_date ON public.cancellation USING btree (cancellation_date);


--
-- Name: idx_cancellation_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cancellation_policy ON public.cancellation USING btree (policy_id);


--
-- Name: idx_cancellation_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cancellation_user ON public.cancellation USING btree (cancelled_by_user_id);


--
-- Name: idx_card_holder; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_card_holder ON public.card USING btree (current_holder);


--
-- Name: idx_card_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_card_policy ON public.card USING btree (policy_id);


--
-- Name: idx_card_seller; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_card_seller ON public.card USING btree (seller_id);


--
-- Name: idx_card_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_card_status ON public.card USING btree (status);


--
-- Name: idx_client_deleted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_deleted ON public.client USING btree (deleted_at);


--
-- Name: idx_client_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_name ON public.client USING btree (paternal_surname, first_name) WHERE (deleted_at IS NULL);


--
-- Name: idx_client_name_trgm; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_name_trgm ON public.client USING gin (((((((first_name)::text || ' '::text) || (paternal_surname)::text) || ' '::text) || (COALESCE(maternal_surname, ''::character varying))::text)) public.gin_trgm_ops) WHERE (deleted_at IS NULL);


--
-- Name: idx_client_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_client_phone ON public.client USING btree (phone_1) WHERE (deleted_at IS NULL);


--
-- Name: idx_collection_assignment_assigned; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_collection_assignment_assigned ON public.collection_assignment USING btree (assigned_to);


--
-- Name: idx_collection_assignment_card; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_collection_assignment_card ON public.collection_assignment USING btree (card_id);


--
-- Name: idx_collection_assignment_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_collection_assignment_policy ON public.collection_assignment USING btree (policy_id);


--
-- Name: idx_coverage_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_coverage_active ON public.coverage USING btree (is_active) WHERE (is_active = true);


--
-- Name: idx_coverage_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_coverage_name ON public.coverage USING btree (name);


--
-- Name: idx_coverage_vehicle_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_coverage_vehicle_key ON public.coverage USING btree (vehicle_key);


--
-- Name: idx_device_session_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_session_active ON public.device_session USING btree (is_active, user_id) WHERE (is_active = true);


--
-- Name: idx_device_session_device; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_session_device ON public.device_session USING btree (device_id);


--
-- Name: idx_device_session_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_device_session_user ON public.device_session USING btree (user_id);


--
-- Name: idx_employee_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_employee_status ON public.employee USING btree (status);


--
-- Name: idx_employee_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_employee_user ON public.employee USING btree (user_id);


--
-- Name: idx_endorsement_details; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_endorsement_details ON public.endorsement USING gin (change_details);


--
-- Name: idx_endorsement_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_endorsement_policy ON public.endorsement USING btree (policy_id);


--
-- Name: idx_endorsement_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_endorsement_status ON public.endorsement USING btree (status);


--
-- Name: idx_incident_adjuster; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_adjuster ON public.incident USING btree (adjuster_id);


--
-- Name: idx_incident_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_policy ON public.incident USING btree (policy_id);


--
-- Name: idx_incident_report_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_report_number ON public.incident USING btree (report_number);


--
-- Name: idx_incident_report_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_report_time ON public.incident USING btree (report_time);


--
-- Name: idx_incident_search; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_search ON public.incident USING gin (((((((report_number)::text || ' '::text) || (requester_name)::text) || ' '::text) || (COALESCE(phone, ''::character varying))::text)) public.gin_trgm_ops);


--
-- Name: idx_incident_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_status ON public.incident USING btree (service_status);


--
-- Name: idx_medical_pass_hospital; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_medical_pass_hospital ON public.medical_pass USING btree (hospital_id);


--
-- Name: idx_medical_pass_incident; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_medical_pass_incident ON public.medical_pass USING btree (incident_id);


--
-- Name: idx_mobile_action_log_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mobile_action_log_created ON public.mobile_action_log USING btree (created_at);


--
-- Name: idx_mobile_action_log_device; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mobile_action_log_device ON public.mobile_action_log USING btree (device_session_id);


--
-- Name: idx_mobile_action_log_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mobile_action_log_user ON public.mobile_action_log USING btree (user_id);


--
-- Name: idx_payment_collector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_collector ON public.payment USING btree (collector_id);


--
-- Name: idx_payment_due_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_due_date ON public.payment USING btree (due_date);


--
-- Name: idx_payment_late; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_late ON public.payment USING btree (policy_id, due_date) WHERE (status = 'late'::public.payment_status_type);


--
-- Name: idx_payment_overdue; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_overdue ON public.payment USING btree (policy_id, due_date) WHERE (status = 'overdue'::public.payment_status_type);


--
-- Name: idx_payment_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_pending ON public.payment USING btree (policy_id, due_date) WHERE (status = 'pending'::public.payment_status_type);


--
-- Name: idx_payment_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_policy ON public.payment USING btree (policy_id);


--
-- Name: idx_payment_policy_status_due; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_policy_status_due ON public.payment USING btree (policy_id, status, due_date);


--
-- Name: idx_payment_proposal_original; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_proposal_original ON public.payment_proposal USING btree (original_payment_id);


--
-- Name: idx_payment_proposal_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_proposal_policy ON public.payment_proposal USING btree (policy_id);


--
-- Name: idx_preapproval_collector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_preapproval_collector ON public.payment_preapproval USING btree (collector_id);


--
-- Name: idx_preapproval_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_preapproval_status ON public.payment_preapproval USING btree (status);


--
-- Name: idx_preapproval_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_preapproval_created ON public.payment_preapproval USING btree (created_at);


--
-- Name: idx_payment_receipt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_receipt ON public.payment USING btree (receipt_number);


--
-- Name: idx_payment_seller; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_seller ON public.payment USING btree (seller_id);


--
-- Name: idx_payment_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_status ON public.payment USING btree (status);


--
-- Name: idx_policy_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_active ON public.policy USING btree (folio) WHERE (status = 'active'::public.policy_status_type);


--
-- Name: idx_policy_client; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_client ON public.policy USING btree (client_id);


--
-- Name: idx_policy_coverage; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_coverage ON public.policy USING btree (coverage_id);


--
-- Name: idx_policy_elaboration; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_elaboration ON public.policy USING btree (elaboration_date);


--
-- Name: idx_policy_expiration; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_expiration ON public.policy USING btree (expiration_date);


--
-- Name: idx_policy_folio; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_folio ON public.policy USING btree (folio);


--
-- Name: idx_policy_fraud; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_fraud ON public.policy USING btree (has_fraud_observation, has_payment_issues) WHERE ((has_fraud_observation = true) OR (has_payment_issues = true));


--
-- Name: idx_policy_morosa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_morosa ON public.policy USING btree (folio, client_id) WHERE (status = 'morosa'::public.policy_status_type);


--
-- Name: idx_policy_notif_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_notif_policy ON public.policy_notification USING btree (policy_id, notification_type);


--
-- Name: idx_policy_notif_seller; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_notif_seller ON public.policy_notification USING btree (seller_id);


--
-- Name: idx_policy_pending; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_pending ON public.policy USING btree (folio) WHERE (status = 'pending'::public.policy_status_type);


--
-- Name: idx_policy_pre_effective; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_pre_effective ON public.policy USING btree (folio, effective_date) WHERE (status = 'pre_effective'::public.policy_status_type);


--
-- Name: idx_policy_renewal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_renewal ON public.policy USING btree (renewal_folio);


--
-- Name: idx_policy_seller; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_seller ON public.policy USING btree (seller_id);


--
-- Name: idx_policy_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_status ON public.policy USING btree (status);


--
-- Name: idx_policy_vehicle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_vehicle ON public.policy USING btree (vehicle_id);


--
-- Name: idx_promo_app_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promo_app_policy ON public.promotion_application USING btree (policy_id);


--
-- Name: idx_promo_app_promotion; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promo_app_promotion ON public.promotion_application USING btree (promotion_id);


--
-- Name: idx_promo_app_referrer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promo_app_referrer ON public.promotion_application USING btree (referrer_policy_id) WHERE (referrer_policy_id IS NOT NULL);


--
-- Name: idx_promo_rule_promotion; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promo_rule_promotion ON public.promotion_rule USING btree (promotion_id);


--
-- Name: idx_promo_rule_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promo_rule_type ON public.promotion_rule USING btree (discount_type);


--
-- Name: idx_promotion_dates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promotion_dates ON public.promotion USING btree (start_date, end_date);


--
-- Name: idx_promotion_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_promotion_status ON public.promotion USING btree (status);


--
-- Name: idx_receipt_collector; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_receipt_collector ON public.receipt USING btree (collector_id);


--
-- Name: idx_receipt_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_receipt_number ON public.receipt USING btree (receipt_number);


--
-- Name: idx_receipt_payment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_receipt_payment ON public.receipt USING btree (payment_id);


--
-- Name: idx_receipt_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_receipt_status ON public.receipt USING btree (status);


--
-- Name: idx_renewal_new; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_renewal_new ON public.renewal USING btree (new_policy_id);


--
-- Name: idx_renewal_notif_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_renewal_notif_policy ON public.renewal_notification_log USING btree (policy_id);


--
-- Name: idx_renewal_old; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_renewal_old ON public.renewal USING btree (old_policy_id);


--
-- Name: idx_sent_msg_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sent_msg_date ON public.sent_message USING btree (sent_at);


--
-- Name: idx_sent_msg_delivery; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sent_msg_delivery ON public.sent_message USING btree (delivery_status) WHERE (delivery_status = ANY (ARRAY['queued'::public.message_delivery_status_type, 'sent'::public.message_delivery_status_type]));


--
-- Name: idx_sent_msg_failed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sent_msg_failed ON public.sent_message USING btree (retry_count) WHERE (delivery_status = 'failed'::public.message_delivery_status_type);


--
-- Name: idx_sent_msg_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sent_msg_phone ON public.sent_message USING btree (phone, sent_at);


--
-- Name: idx_sent_msg_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sent_msg_policy ON public.sent_message USING btree (policy_id, message_type);


--
-- Name: idx_session_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_session_expires ON public.session USING btree (expires_at) WHERE (is_active = true);


--
-- Name: idx_session_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_session_user ON public.session USING btree (user_id);


--
-- Name: idx_shift_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_shift_date ON public.adjuster_shift USING btree (shift_date);


--
-- Name: idx_tow_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_policy ON public.tow_service USING btree (policy_id);


--
-- Name: idx_tow_provider_fk; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_provider_fk ON public.tow_service USING btree (tow_provider_id);


--
-- Name: idx_tow_provider_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_provider_status ON public.tow_provider USING btree (status);


--
-- Name: idx_tow_report_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_report_time ON public.tow_service USING btree (report_time);


--
-- Name: idx_tow_search; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_search ON public.tow_service USING gin (((((report_number)::text || ' '::text) || (requester_name)::text)) public.gin_trgm_ops);


--
-- Name: idx_tow_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tow_status ON public.tow_service USING btree (service_status);


--
-- Name: idx_user_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_active ON public.app_user USING btree (is_active) WHERE (is_active = true);


--
-- Name: idx_vehicle_plates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_plates ON public.vehicle USING btree (plates);


--
-- Name: idx_vehicle_serial; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_serial ON public.vehicle USING btree (serial_number);


--
-- Name: idx_visit_card; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_visit_card ON public.visit_notice USING btree (card_id);


--
-- Name: idx_visit_policy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_visit_policy ON public.visit_notice USING btree (policy_id);


--
-- Name: idx_workshop_pass_incident; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workshop_pass_incident ON public.workshop_pass USING btree (incident_id);


--
-- Name: idx_workshop_pass_workshop; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workshop_pass_workshop ON public.workshop_pass USING btree (workshop_id);


--
-- Name: audit_log_2026_changed_at_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_log_changed_at ATTACH PARTITION public.audit_log_2026_changed_at_idx;


--
-- Name: audit_log_2026_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.audit_log_pkey ATTACH PARTITION public.audit_log_2026_pkey;


--
-- Name: audit_log_2026_table_name_record_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_audit_log_table_record ATTACH PARTITION public.audit_log_2026_table_name_record_id_idx;


--
-- Name: address address_municipality_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.address
    ADD CONSTRAINT address_municipality_id_fkey FOREIGN KEY (municipality_id) REFERENCES public.municipality(id);


--
-- Name: adjuster_shift adjuster_shift_adjuster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.adjuster_shift
    ADD CONSTRAINT adjuster_shift_adjuster_id_fkey FOREIGN KEY (adjuster_id) REFERENCES public.adjuster(id) ON DELETE CASCADE;


--
-- Name: app_user app_user_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE SET NULL;


--
-- Name: app_user app_user_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE SET NULL;


--
-- Name: approval_request approval_request_reviewed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_request
    ADD CONSTRAINT approval_request_reviewed_by_user_id_fkey FOREIGN KEY (reviewed_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: approval_request approval_request_submitted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_request
    ADD CONSTRAINT approval_request_submitted_by_user_id_fkey FOREIGN KEY (submitted_by_user_id) REFERENCES public.app_user(id) ON DELETE RESTRICT;


--
-- Name: approval_request approval_request_submitted_from_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_request
    ADD CONSTRAINT approval_request_submitted_from_device_id_fkey FOREIGN KEY (submitted_from_device_id) REFERENCES public.device_session(id) ON DELETE SET NULL;


--
-- Name: cancellation cancellation_cancelled_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cancellation
    ADD CONSTRAINT cancellation_cancelled_by_user_id_fkey FOREIGN KEY (cancelled_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: cancellation cancellation_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cancellation
    ADD CONSTRAINT cancellation_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: card card_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.card
    ADD CONSTRAINT card_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: card card_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.card
    ADD CONSTRAINT card_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: client client_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(id);


--
-- Name: collection_assignment collection_assignment_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collection_assignment
    ADD CONSTRAINT collection_assignment_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.card(id) ON DELETE CASCADE;


--
-- Name: collection_assignment collection_assignment_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collection_assignment
    ADD CONSTRAINT collection_assignment_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: commission_rate commission_rate_coverage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_rate
    ADD CONSTRAINT commission_rate_coverage_id_fkey FOREIGN KEY (coverage_id) REFERENCES public.coverage(id) ON DELETE RESTRICT;


--
-- Name: device_session device_session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.device_session
    ADD CONSTRAINT device_session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- Name: employee_department employee_department_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_department
    ADD CONSTRAINT employee_department_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.department(id) ON DELETE CASCADE;


--
-- Name: employee_department employee_department_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_department
    ADD CONSTRAINT employee_department_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: employee_permission_override employee_permission_override_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_permission_override
    ADD CONSTRAINT employee_permission_override_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: employee_permission_override employee_permission_override_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_permission_override
    ADD CONSTRAINT employee_permission_override_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: employee employee_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: endorsement endorsement_new_contractor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endorsement
    ADD CONSTRAINT endorsement_new_contractor_id_fkey FOREIGN KEY (new_contractor_id) REFERENCES public.client(id);


--
-- Name: endorsement endorsement_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endorsement
    ADD CONSTRAINT endorsement_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: endorsement endorsement_previous_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.endorsement
    ADD CONSTRAINT endorsement_previous_vehicle_id_fkey FOREIGN KEY (previous_vehicle_id) REFERENCES public.vehicle(id);


--
-- Name: hospital hospital_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital
    ADD CONSTRAINT hospital_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(id);


--
-- Name: incident incident_adjuster_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident
    ADD CONSTRAINT incident_adjuster_id_fkey FOREIGN KEY (adjuster_id) REFERENCES public.adjuster(id) ON DELETE RESTRICT;


--
-- Name: incident incident_attended_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident
    ADD CONSTRAINT incident_attended_by_user_id_fkey FOREIGN KEY (attended_by_user_id) REFERENCES public.app_user(id);


--
-- Name: incident incident_origin_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident
    ADD CONSTRAINT incident_origin_address_id_fkey FOREIGN KEY (origin_address_id) REFERENCES public.address(id) ON DELETE SET NULL;


--
-- Name: incident incident_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident
    ADD CONSTRAINT incident_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: incident_satisfaction_survey incident_satisfaction_survey_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_satisfaction_survey
    ADD CONSTRAINT incident_satisfaction_survey_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incident(id) ON DELETE RESTRICT;


--
-- Name: incident_satisfaction_survey incident_satisfaction_survey_surveyed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_satisfaction_survey
    ADD CONSTRAINT incident_satisfaction_survey_surveyed_by_user_id_fkey FOREIGN KEY (surveyed_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: medical_pass medical_pass_hospital_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_pass
    ADD CONSTRAINT medical_pass_hospital_id_fkey FOREIGN KEY (hospital_id) REFERENCES public.hospital(id) ON DELETE RESTRICT;


--
-- Name: medical_pass medical_pass_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.medical_pass
    ADD CONSTRAINT medical_pass_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incident(id) ON DELETE RESTRICT;


--
-- Name: mobile_action_log mobile_action_log_device_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mobile_action_log
    ADD CONSTRAINT mobile_action_log_device_session_id_fkey FOREIGN KEY (device_session_id) REFERENCES public.device_session(id) ON DELETE CASCADE;


--
-- Name: mobile_action_log mobile_action_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mobile_action_log
    ADD CONSTRAINT mobile_action_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- Name: payment payment_collector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_collector_id_fkey FOREIGN KEY (collector_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: payment payment_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: payment_proposal payment_proposal_collector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_collector_id_fkey FOREIGN KEY (collector_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: payment_proposal payment_proposal_original_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_original_payment_id_fkey FOREIGN KEY (original_payment_id) REFERENCES public.payment(id) ON DELETE RESTRICT;


--
-- Name: payment_proposal payment_proposal_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: payment_proposal payment_proposal_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: payment_proposal payment_proposal_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_proposal
    ADD CONSTRAINT payment_proposal_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: payment_preapproval payment_preapproval_collector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_preapproval
    ADD CONSTRAINT payment_preapproval_collector_id_fkey FOREIGN KEY (collector_id) REFERENCES public.employee(id) ON DELETE RESTRICT;


--
-- Name: payment_preapproval payment_preapproval_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_preapproval
    ADD CONSTRAINT payment_preapproval_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: payment payment_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: payment payment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: policy_amplia_detail policy_amplia_detail_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_amplia_detail
    ADD CONSTRAINT policy_amplia_detail_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE CASCADE;


--
-- Name: policy policy_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.client(id) ON DELETE RESTRICT;


--
-- Name: policy policy_coverage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_coverage_id_fkey FOREIGN KEY (coverage_id) REFERENCES public.coverage(id) ON DELETE RESTRICT;


--
-- Name: policy policy_data_entry_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_data_entry_user_id_fkey FOREIGN KEY (data_entry_user_id) REFERENCES public.app_user(id);


--
-- Name: policy_notification policy_notification_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_notification
    ADD CONSTRAINT policy_notification_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE CASCADE;


--
-- Name: policy_notification policy_notification_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_notification
    ADD CONSTRAINT policy_notification_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: policy policy_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: policy policy_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy
    ADD CONSTRAINT policy_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id) ON DELETE RESTRICT;


--
-- Name: promotion_application promotion_application_applied_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_applied_by_user_id_fkey FOREIGN KEY (applied_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: promotion_application promotion_application_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: promotion_application promotion_application_promotion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_promotion_id_fkey FOREIGN KEY (promotion_id) REFERENCES public.promotion(id) ON DELETE RESTRICT;


--
-- Name: promotion_application promotion_application_promotion_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_promotion_rule_id_fkey FOREIGN KEY (promotion_rule_id) REFERENCES public.promotion_rule(id) ON DELETE RESTRICT;


--
-- Name: promotion_application promotion_application_referrer_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_application
    ADD CONSTRAINT promotion_application_referrer_policy_id_fkey FOREIGN KEY (referrer_policy_id) REFERENCES public.policy(id) ON DELETE SET NULL;


--
-- Name: promotion_rule promotion_rule_promotion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.promotion_rule
    ADD CONSTRAINT promotion_rule_promotion_id_fkey FOREIGN KEY (promotion_id) REFERENCES public.promotion(id) ON DELETE CASCADE;


--
-- Name: receipt receipt_collector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt
    ADD CONSTRAINT receipt_collector_id_fkey FOREIGN KEY (collector_id) REFERENCES public.employee(id) ON DELETE SET NULL;


--
-- Name: receipt receipt_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt
    ADD CONSTRAINT receipt_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payment(id) ON DELETE SET NULL;


--
-- Name: receipt receipt_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.receipt
    ADD CONSTRAINT receipt_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: renewal renewal_new_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal
    ADD CONSTRAINT renewal_new_policy_id_fkey FOREIGN KEY (new_policy_id) REFERENCES public.policy(id) ON DELETE SET NULL;


--
-- Name: renewal_notification_log renewal_notification_log_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal_notification_log
    ADD CONSTRAINT renewal_notification_log_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE CASCADE;


--
-- Name: renewal renewal_old_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.renewal
    ADD CONSTRAINT renewal_old_policy_id_fkey FOREIGN KEY (old_policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: role_permission role_permission_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: role_permission role_permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: sent_message sent_message_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sent_message
    ADD CONSTRAINT sent_message_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE SET NULL;


--
-- Name: sent_message sent_message_sent_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sent_message
    ADD CONSTRAINT sent_message_sent_by_user_id_fkey FOREIGN KEY (sent_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: session session_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.app_user(id) ON DELETE CASCADE;


--
-- Name: tow_provider tow_provider_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_provider
    ADD CONSTRAINT tow_provider_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(id) ON DELETE SET NULL;


--
-- Name: tow_satisfaction_survey tow_satisfaction_survey_surveyed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_satisfaction_survey
    ADD CONSTRAINT tow_satisfaction_survey_surveyed_by_user_id_fkey FOREIGN KEY (surveyed_by_user_id) REFERENCES public.app_user(id) ON DELETE SET NULL;


--
-- Name: tow_satisfaction_survey tow_satisfaction_survey_tow_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_satisfaction_survey
    ADD CONSTRAINT tow_satisfaction_survey_tow_service_id_fkey FOREIGN KEY (tow_service_id) REFERENCES public.tow_service(id) ON DELETE RESTRICT;


--
-- Name: tow_service tow_service_attended_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_attended_by_user_id_fkey FOREIGN KEY (attended_by_user_id) REFERENCES public.app_user(id);


--
-- Name: tow_service tow_service_destination_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_destination_address_id_fkey FOREIGN KEY (destination_address_id) REFERENCES public.address(id) ON DELETE SET NULL;


--
-- Name: tow_service tow_service_origin_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_origin_address_id_fkey FOREIGN KEY (origin_address_id) REFERENCES public.address(id) ON DELETE SET NULL;


--
-- Name: tow_service tow_service_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: tow_service tow_service_tow_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tow_service
    ADD CONSTRAINT tow_service_tow_provider_id_fkey FOREIGN KEY (tow_provider_id) REFERENCES public.tow_provider(id) ON DELETE SET NULL;


--
-- Name: visit_notice visit_notice_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visit_notice
    ADD CONSTRAINT visit_notice_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.card(id) ON DELETE SET NULL;


--
-- Name: visit_notice visit_notice_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visit_notice
    ADD CONSTRAINT visit_notice_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.payment(id) ON DELETE SET NULL;


--
-- Name: visit_notice visit_notice_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visit_notice
    ADD CONSTRAINT visit_notice_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.policy(id) ON DELETE RESTRICT;


--
-- Name: workshop workshop_address_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop
    ADD CONSTRAINT workshop_address_id_fkey FOREIGN KEY (address_id) REFERENCES public.address(id);


--
-- Name: workshop_pass workshop_pass_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop_pass
    ADD CONSTRAINT workshop_pass_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incident(id) ON DELETE RESTRICT;


--
-- Name: workshop_pass workshop_pass_workshop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workshop_pass
    ADD CONSTRAINT workshop_pass_workshop_id_fkey FOREIGN KEY (workshop_id) REFERENCES public.workshop(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

