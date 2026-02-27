-- ============================================================================
-- Migration: 006_create_app_user
-- Fecha: 2026-02-27
-- Autor: Claudy ✨
-- Descripción: Crear tabla de usuarios para la app
-- ============================================================================

CREATE TABLE IF NOT EXISTS app_user (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL UNIQUE REFERENCES employee(id) ON DELETE CASCADE,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_app_user_username ON app_user(username);

CREATE OR REPLACE TRIGGER trg_app_user_updated_at
    BEFORE UPDATE ON app_user
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();
