-- SQL reference for categories and products tables (F-01: Browse catalogue)
-- Tables are created by SQLAlchemy; use seed.py to populate sample data.

CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS products (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(200) NOT NULL,
    description    TEXT,
    manufacturer   VARCHAR(100) NOT NULL,
    piece_count    INTEGER      NOT NULL,
    min_age        INTEGER,
    base_price     NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER      NOT NULL DEFAULT 0,
    image_url      VARCHAR(500),
    category_id    INTEGER REFERENCES categories(id)
);

CREATE INDEX IF NOT EXISTS ix_products_name         ON products (name);
CREATE INDEX IF NOT EXISTS ix_products_manufacturer ON products (manufacturer);
CREATE INDEX IF NOT EXISTS ix_products_category_id  ON products (category_id);
