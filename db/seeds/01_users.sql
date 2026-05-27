-- SQL reference for the users table (F-04: Registration and Login)
-- The actual table is created by SQLAlchemy (Base.metadata.create_all).
-- This file is provided as a human-readable schema reference.
--
-- To seed the admin account use: docker compose exec backend python seed.py

-- users: stores both regular users and admins (distinguished by the role column)
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    role          VARCHAR(10)  NOT NULL DEFAULT 'user', -- 'user' | 'admin'
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
