-- SQL migration: Initial schema for Policy-Constrained LLM Agent Workspace System
-- Wave 1 Task 4 - Database Schema

-- Create ENUM types for status fields
CREATE TYPE session_status AS ENUM ('active', 'completed', 'failed');
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE execution_plan_status AS ENUM ('pending', 'approved', 'rejected', 'executing', 'completed', 'failed');
CREATE TYPE tool_call_status AS ENUM ('pending', 'running', 'success', 'failed');

-- Table: sessions
-- Stores agent session metadata and workspace context
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status session_status NOT NULL DEFAULT 'active',
    workspace_path VARCHAR(1024) NOT NULL
);

-- Table: messages
-- Stores conversation history within sessions
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: execution_plans
-- Stores LLM-generated execution plans for policy validation
CREATE TABLE execution_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    plan_json JSONB NOT NULL,
    status execution_plan_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Table: tool_calls
-- Stores individual tool execution records
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_plan_id UUID NOT NULL REFERENCES execution_plans(id) ON DELETE CASCADE,
    step_id VARCHAR(255) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    arguments JSONB NOT NULL,
    result JSONB,
    status tool_call_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Table: artifacts
-- Stores file artifacts created during agent sessions
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    file_path VARCHAR(1024) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: audit_logs
-- Stores policy and security-related audit entries
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: recipes
-- Stores reusable plan templates for common tasks
CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    plan_template JSONB NOT NULL,
    parameters JSONB NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    usage_count INTEGER NOT NULL DEFAULT 0
);

-- Create indexes for optimal query performance

-- sessions: Filter by user and time range
CREATE INDEX idx_sessions_user_created ON sessions(user_id, created_at);

-- messages: Get messages for a session in chronological order
CREATE INDEX idx_messages_session_created ON messages(session_id, created_at);

-- execution_plans: Track plan status per session
CREATE INDEX idx_execution_plans_session_status ON execution_plans(session_id, status);

-- tool_calls: Get tool calls for an execution plan by status
CREATE INDEX idx_tool_calls_plan_status ON tool_calls(execution_plan_id, status);

-- audit_logs: Search by user and time, or session and time
CREATE INDEX idx_audit_logs_user_created ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_logs_session_created ON audit_logs(session_id, created_at);

-- Additional helpful indexes
CREATE INDEX idx_artifacts_session_created ON artifacts(session_id, created_at);
CREATE INDEX idx_artifacts_file_path ON artifacts(file_path);
