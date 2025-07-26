-- Initialize Co-Intelligence GenAI Universe Database
-- This script runs when PostgreSQL container starts

-- Create database if it doesn't exist (handled by Docker environment)
-- The database is created automatically by POSTGRES_DB environment variable

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Note: The users table will be created by Alembic migrations
-- This script just sets up the database environment
