-- FTUE Axiom Tracking Columns Migration
--
-- Adds columns to track FTUE (First Time User Experience) axiom completion.
--
-- FTUE Axioms (from spec/protocols/ftue-axioms.md):
--   - F1: Identity Seed (first K-Block) - tracked as first_kblock_id
--   - F2: Connection Pattern (first edge) - tracked as f2_edge_id
--   - F3: Judgment Experience (first judgment) - tracked as f3_judgment_id
--   - FG: Growth Witness (witnessed emergence) - tracked as fg_witness_id
--
-- Philosophy:
--   "Onboarding is not a feature - it is axiom discovery."
--
-- Reference: spec/protocols/ftue-axioms.md

-- ===========================================================================
-- Add FTUE Axiom Tracking Columns
-- ===========================================================================

-- F1: Identity Seed completion timestamp (first_kblock_id already exists)
ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS f1_completed_at TIMESTAMP WITH TIME ZONE;

-- F2: Connection Pattern (first edge)
ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS f2_edge_id VARCHAR(64);

ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS f2_completed_at TIMESTAMP WITH TIME ZONE;

-- F3: Judgment Experience (first judgment)
ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS f3_judgment_id VARCHAR(64);

ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS f3_completed_at TIMESTAMP WITH TIME ZONE;

-- FG: Growth Witness (witnessed emergence)
ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS fg_witness_id VARCHAR(64);

ALTER TABLE onboarding_sessions
    ADD COLUMN IF NOT EXISTS fg_completed_at TIMESTAMP WITH TIME ZONE;

-- ===========================================================================
-- Add Indexes for FTUE Status Queries
-- ===========================================================================

-- Index for checking FTUE completion status
CREATE INDEX IF NOT EXISTS idx_onboarding_ftue_completion
    ON onboarding_sessions(first_kblock_id, f2_edge_id, f3_judgment_id, fg_witness_id)
    WHERE NOT completed;

-- ===========================================================================
-- Update Table Comment
-- ===========================================================================

COMMENT ON TABLE onboarding_sessions IS 'FTUE onboarding sessions with axiom tracking (F1: Identity, F2: Connection, F3: Judgment, FG: Growth)';

-- ===========================================================================
-- Column Comments
-- ===========================================================================

COMMENT ON COLUMN onboarding_sessions.f1_completed_at IS 'F1: When Identity Seed (first K-Block) axiom was completed';
COMMENT ON COLUMN onboarding_sessions.f2_edge_id IS 'F2: ID of first edge created (Connection Pattern)';
COMMENT ON COLUMN onboarding_sessions.f2_completed_at IS 'F2: When Connection Pattern axiom was completed';
COMMENT ON COLUMN onboarding_sessions.f3_judgment_id IS 'F3: ID of first judgment (Judgment Experience)';
COMMENT ON COLUMN onboarding_sessions.f3_completed_at IS 'F3: When Judgment Experience axiom was completed';
COMMENT ON COLUMN onboarding_sessions.fg_witness_id IS 'FG: ID of emergence witness mark (Growth Witness)';
COMMENT ON COLUMN onboarding_sessions.fg_completed_at IS 'FG: When Growth Witness axiom was completed';

-- ===========================================================================
-- Usage Examples
-- ===========================================================================

-- Check FTUE axiom completion status for a session:
-- SELECT
--     id,
--     first_kblock_id IS NOT NULL AS f1_complete,
--     f2_edge_id IS NOT NULL AS f2_complete,
--     f3_judgment_id IS NOT NULL AS f3_complete,
--     fg_witness_id IS NOT NULL AS fg_complete,
--     (first_kblock_id IS NOT NULL AND
--      f2_edge_id IS NOT NULL AND
--      f3_judgment_id IS NOT NULL AND
--      fg_witness_id IS NOT NULL) AS all_complete
-- FROM onboarding_sessions
-- WHERE id = 'session_id_here';

-- Find sessions that have completed F1 but not F2:
-- SELECT * FROM onboarding_sessions
-- WHERE first_kblock_id IS NOT NULL
-- AND f2_edge_id IS NULL;
