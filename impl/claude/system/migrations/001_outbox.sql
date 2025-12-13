-- Outbox Table Migration for CDC (Change Data Capture)
--
-- This table implements the Transactional Outbox Pattern:
-- 1. Application writes to target table AND outbox in same transaction
-- 2. Synapse polls outbox for unprocessed events
-- 3. After syncing to derived views (Qdrant), events are marked processed
--
-- Categorical Role: The outbox is the observable interface for the CDC Functor.
-- It transforms Postgres row mutations into ChangeEvents for the Synapse.
--
-- Reference: https://microservices.io/patterns/data/transactional-outbox.html

-- ===========================================================================
-- Outbox Table
-- ===========================================================================

CREATE TABLE IF NOT EXISTS outbox (
    id BIGSERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,           -- INSERT, UPDATE, DELETE
    table_name TEXT NOT NULL,           -- Source table name
    row_id TEXT NOT NULL,               -- Primary key of affected row
    payload JSONB NOT NULL,             -- Row data (NEW for insert/update, OLD for delete)
    processed BOOLEAN DEFAULT FALSE,    -- Has this event been synced?
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ            -- When was it processed?
);

-- Index for efficient polling: unprocessed events in order
CREATE INDEX IF NOT EXISTS idx_outbox_unprocessed
    ON outbox(created_at)
    WHERE NOT processed;

-- Index for cleanup: find old processed events
CREATE INDEX IF NOT EXISTS idx_outbox_processed
    ON outbox(processed_at)
    WHERE processed;

-- Comment describing the table's role
COMMENT ON TABLE outbox IS 'Transactional outbox for CDC - enables eventual consistency between Postgres and derived views';

-- ===========================================================================
-- Generic Trigger Function
-- ===========================================================================

CREATE OR REPLACE FUNCTION outbox_trigger() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO outbox (event_type, table_name, row_id, payload)
    VALUES (
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id::TEXT, OLD.id::TEXT),
        CASE TG_OP
            WHEN 'DELETE' THEN row_to_json(OLD)
            ELSE row_to_json(NEW)
        END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION outbox_trigger() IS 'Generic trigger function to populate outbox on row changes';

-- ===========================================================================
-- Example: Attach to memories table
-- ===========================================================================
-- To enable CDC on a table, create a trigger like:
--
-- CREATE TRIGGER memories_outbox_trigger
--     AFTER INSERT OR UPDATE OR DELETE ON memories
--     FOR EACH ROW EXECUTE FUNCTION outbox_trigger();
--
-- This ensures every change to memories is captured in the outbox,
-- and the Synapse will eventually sync it to Qdrant.

-- ===========================================================================
-- Cleanup Function (Optional)
-- ===========================================================================

CREATE OR REPLACE FUNCTION outbox_cleanup(retention_days INTEGER DEFAULT 7) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM outbox
    WHERE processed = TRUE
    AND processed_at < NOW() - (retention_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION outbox_cleanup(INTEGER) IS 'Remove old processed events to prevent unbounded growth';

-- ===========================================================================
-- Monitoring View
-- ===========================================================================

CREATE OR REPLACE VIEW outbox_stats AS
SELECT
    COUNT(*) FILTER (WHERE NOT processed) AS pending_events,
    COUNT(*) FILTER (WHERE processed) AS processed_events,
    MAX(created_at) FILTER (WHERE NOT processed) AS oldest_pending,
    AVG(EXTRACT(EPOCH FROM (processed_at - created_at)) * 1000) FILTER (WHERE processed) AS avg_processing_lag_ms
FROM outbox;

COMMENT ON VIEW outbox_stats IS 'Statistics for monitoring outbox health and CDC lag';
