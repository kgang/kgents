-- Onboarding Sessions Table Migration
--
-- This table stores onboarding sessions for the Genesis FTUE flow.
-- Sessions persist across server restarts and are cleaned up after 24h of inactivity.
--
-- Philosophy:
--   "The act of declaring, capturing, and auditing your decisions is itself
--    a radical act of self-transformation."
--
-- Reference: plans/zero-seed-genesis-grand-strategy.md §6.2 (FTUE)

-- ===========================================================================
-- Onboarding Sessions Table
-- ===========================================================================

CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    current_step VARCHAR(32) NOT NULL DEFAULT 'started',
    completed BOOLEAN NOT NULL DEFAULT false,
    completed_at TIMESTAMP WITH TIME ZONE,
    first_kblock_id VARCHAR(64),
    first_declaration TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for querying by user
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_id
    ON onboarding_sessions(user_id);

-- Index for cleanup queries (incomplete sessions)
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_cleanup
    ON onboarding_sessions(created_at)
    WHERE NOT completed;

-- Index for completion status queries
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_completed
    ON onboarding_sessions(completed, completed_at);

-- Comment describing the table's role
COMMENT ON TABLE onboarding_sessions IS 'First Time User Experience (FTUE) onboarding sessions - persist across server restarts, auto-cleanup after 24h';

-- ===========================================================================
-- Cleanup Function
-- ===========================================================================

CREATE OR REPLACE FUNCTION cleanup_onboarding_sessions(retention_hours INTEGER DEFAULT 24) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
    cutoff_time TIMESTAMP WITH TIME ZONE;
BEGIN
    cutoff_time := NOW() - (retention_hours || ' hours')::INTERVAL;

    DELETE FROM onboarding_sessions
    WHERE completed = FALSE
    AND created_at < cutoff_time;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_onboarding_sessions(INTEGER) IS 'Remove old incomplete onboarding sessions to prevent database bloat';

-- ===========================================================================
-- Usage Examples
-- ===========================================================================

-- Clean up abandoned sessions older than 24 hours:
-- SELECT cleanup_onboarding_sessions(24);

-- Check for abandoned sessions:
-- SELECT COUNT(*) FROM onboarding_sessions
-- WHERE NOT completed AND created_at < NOW() - INTERVAL '24 hours';

-- View recent onboarding activity:
-- SELECT id, user_id, current_step, completed, created_at
-- FROM onboarding_sessions
-- ORDER BY created_at DESC LIMIT 10;
