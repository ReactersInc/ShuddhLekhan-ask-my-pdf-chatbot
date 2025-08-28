-- Create database tables for authentication
-- Run this SQL in your Supabase SQL Editor: https://fkfmtxczjvrcfbswqdse.supabase.co

-- Users table (for authentication only)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Enable Row Level Security (RLS) for data protection
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS Policy (allow service_role to manage users)
CREATE POLICY "Service role can manage users" ON users
    FOR ALL USING (true); -- Service role bypasses RLS anyway
