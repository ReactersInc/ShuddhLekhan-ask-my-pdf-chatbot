-- Create database tables for Ask My PDF Chatbot
-- Run this SQL in your Supabase SQL Editor: https://fkfmtxczjvrcfbswqdse.supabase.co
-- NOTE: These tables are already created - this is for reference only

-- =============================================================================
-- 1. USERS TABLE (Authentication)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
) TABLESPACE pg_default;

-- Index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users USING btree (email) TABLESPACE pg_default;

-- =============================================================================
-- 2. USER_FILES TABLE (PDF Uploads & Document Management)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.user_files (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NULL,
    file_type VARCHAR(50) DEFAULT 'pdf',
    upload_status VARCHAR(50) DEFAULT 'completed',
    summary_status VARCHAR(50) DEFAULT 'pending',
    summary_file_path VARCHAR(1000) NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT user_files_pkey PRIMARY KEY (id),
    CONSTRAINT user_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON public.user_files USING btree (user_id) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_user_files_uploaded_at ON public.user_files USING btree (uploaded_at) TABLESPACE pg_default;

-- =============================================================================
-- 3. PLAGIARISM_CHECKS TABLE (Plagiarism Detection)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.plagiarism_checks (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NULL,
    status VARCHAR(50) DEFAULT 'processing',
    chunks_file_path VARCHAR(1000) NULL,
    keywords_file_path VARCHAR(1000) NULL,
    similarity_score NUMERIC(5, 2) NULL,
    plagiarism_report JSONB NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT plagiarism_checks_pkey PRIMARY KEY (id),
    CONSTRAINT plagiarism_checks_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_user_id ON public.plagiarism_checks USING btree (user_id) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_uploaded_at ON public.plagiarism_checks USING btree (uploaded_at) TABLESPACE pg_default;

-- =============================================================================
-- 4. QA_SESSIONS TABLE (Chat Sessions for PDFs)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.qa_sessions (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    file_id UUID NULL,
    session_name VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT qa_sessions_pkey PRIMARY KEY (id),
    CONSTRAINT qa_sessions_file_id_fkey FOREIGN KEY (file_id) REFERENCES user_files (id) ON DELETE CASCADE,
    CONSTRAINT qa_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Index for faster user queries
CREATE INDEX IF NOT EXISTS idx_qa_sessions_user_id ON public.qa_sessions USING btree (user_id) TABLESPACE pg_default;

-- =============================================================================
-- 5. QA_MESSAGES TABLE (Chat Messages within Sessions)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.qa_messages (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    session_id UUID NULL,
    user_id UUID NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT qa_messages_pkey PRIMARY KEY (id),
    CONSTRAINT qa_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES qa_sessions (id) ON DELETE CASCADE,
    CONSTRAINT qa_messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- Index for faster session queries
CREATE INDEX IF NOT EXISTS idx_qa_messages_session_id ON public.qa_messages USING btree (session_id) TABLESPACE pg_default;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) CONFIGURATION
-- =============================================================================
-- Enable RLS for data protection
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE plagiarism_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies (allow service_role to manage all tables)
CREATE POLICY "Service role can manage users" ON users FOR ALL USING (true);
CREATE POLICY "Service role can manage user_files" ON user_files FOR ALL USING (true);
CREATE POLICY "Service role can manage plagiarism_checks" ON plagiarism_checks FOR ALL USING (true);
CREATE POLICY "Service role can manage qa_sessions" ON qa_sessions FOR ALL USING (true);
CREATE POLICY "Service role can manage qa_messages" ON qa_messages FOR ALL USING (true);

-- =============================================================================
-- SCHEMA SUMMARY
-- =============================================================================
/*
TABLE RELATIONSHIPS:
1. users (base table)
   ├── user_files (user's uploaded PDFs)
   ├── plagiarism_checks (user's plagiarism scans)
   └── qa_sessions (user's chat sessions)
       └── qa_messages (messages within sessions)

USER-SPECIFIC DATA FLOW:
- User logs in → gets user_id from JWT token
- All uploads → linked to user_id
- All queries → filtered by user_id
- User sees only their own files, chats, and plagiarism reports

FEATURES SUPPORTED:
✅ User authentication & management
✅ PDF upload & document management  
✅ Plagiarism detection with reports
✅ Q&A chat sessions with PDFs
✅ Message history within sessions
✅ User-specific data isolation
*/