-- Required for §6.2: UUID primary keys via gen_random_uuid().
-- Runs once on first container start (Postgres docker-entrypoint-initdb.d hook).
CREATE EXTENSION IF NOT EXISTS pgcrypto;
