-- Initialization script for PostgreSQL
-- Creates extensions useful for text search and UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
