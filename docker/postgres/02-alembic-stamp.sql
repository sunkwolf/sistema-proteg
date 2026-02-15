-- Alembic version stamp for fresh environments.
-- This file is loaded AFTER 01-schema.sql by docker-entrypoint-initdb.d.
-- It tells Alembic that all migrations up to HEAD have been applied
-- (since schema.sql already contains the full current schema).
--
-- IMPORTANT: Update this revision when adding new Alembic migrations.
-- Current head: 90e6fc3c4808 (add_unique_employee_user_id)

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

DELETE FROM alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('90e6fc3c4808');
