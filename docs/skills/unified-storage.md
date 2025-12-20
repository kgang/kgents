# Unified Storage Architecture

> *"One DB to rule them all, one schema to bind them."*

**Last Updated**: 2025-12-20

---

## Overview

kgents uses a **unified storage architecture** built on XDG-compliant paths and the `instance_db` module. This replaces the previous fragmented approach of multiple per-project databases.

### Key Insight

> The cortex is singular. Memory is global. Context is local.

- **Global state** lives in `~/.local/share/kgents/membrane.db`
- **Per-project config** lives in `.kgents/config.yaml`
- **No per-project databases** - all sessions, shapes, dreams unified in membrane.db

---

## Storage Locations

### XDG-Compliant (Canonical)

| Path | Purpose | Contents |
|------|---------|----------|
| `~/.config/kgents/` | Configuration | `infrastructure.yaml`, `telemetry.yaml` |
| `~/.local/share/kgents/` | Data | `membrane.db`, `telemetry.db`, `vectors.json`, `blobs/` |
| `~/.cache/kgents/` | Cache | Logs, temporary files |

### Per-Project

| Path | Purpose | Contents |
|------|---------|----------|
| `.kgents/config.yaml` | Project config | Defaults, registry path |
| `.kgents/catalog.json` | Agent registry | Registered agents for project |

### Legacy (Deprecated)

| Path | Status | Migration |
|------|--------|-----------|
| `~/.kgents/history.db` | **DEPRECATED** | Migrated to `membrane.db` cli_sessions table |
| `~/.kgents/kgents.db` | **REMOVED** | Was empty, deleted |
| `.kgents/history.db` | **DEPRECATED** | Config option ignored |

---

## membrane.db Schema

The unified database contains all persistent state:

```sql
-- Core tables (always present)
instances           -- Active kgent instances with heartbeat
shapes              -- Observed patterns (shapes in the membrane)
dreams              -- Consolidated insights
embedding_metadata  -- Vector model tracking
schema_version      -- Migration versioning

-- CLI session tables (unified from history.db)
cli_sessions        -- CLI sessions (repl, flow, script)
cli_session_events  -- Events within sessions
cli_session_agents  -- Agents spawned in sessions
cli_session_artifacts -- Outputs from sessions

-- Self-grow tables (prompt evolution)
self_grow_proposals     -- Proposed prompt changes
self_grow_nursery       -- Germinated proposals
self_grow_rollback_tokens -- Rollback capability
```

---

## Using the Storage

### Via StorageProvider (Recommended)

```python
from protocols.cli.instance_db import StorageProvider

async def main():
    storage = await StorageProvider.from_config()
    await storage.run_migrations()

    # Unified access to all stores
    await storage.relational.execute("SELECT * FROM shapes")
    results = await storage.vector.search(query_vec)
    await storage.blob.put("backups/today.bak", data)
    await storage.telemetry.append([event])

    await storage.close()
```

### Via CLISessionService (For CLI Sessions)

```python
from protocols.cli.instance_db import CLISessionService, create_cli_session_service

async def main():
    service = await create_cli_session_service()

    # Start session
    session = await service.start_session("interactive", "My REPL")

    # Log events
    await service.log_event(session.id, "command", "repl", "User ran check")

    # Record agents
    agent = await service.spawn_agent(session.id, "C-gent", "c-gent")
    await service.complete_agent(agent.id)

    # End session
    await service.end_session(session.id, state="completed")
```

---

## Migration from history.db

If you have data in the old `~/.kgents/history.db`, migrate it:

```bash
# Dry run first
cd impl/claude
uv run python -m protocols.cli.instance_db.migrate_history --dry-run

# Actual migration
uv run python -m protocols.cli.instance_db.migrate_history
```

The migration:
- Copies sessions → cli_sessions
- Copies events → cli_session_events
- Copies agents → cli_session_agents
- Copies artifacts → cli_session_artifacts

---

## Deprecation Timeline

### 2025-12-20 (This Release)

- `history` section in `.kgents/config.yaml` **deprecated**
- Fields `history_enabled`, `history_path`, `history_retention` still parsed but **ignored**
- CLI session tracking now uses membrane.db via CLISessionService

### Future

- `~/.kgents/` directory contents will migrate to XDG paths
- Services currently using `~/.kgents/` (witness, ghost, etc.) will be updated
- `history.db.migrated` backup can be deleted after verification

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     KGENTS STORAGE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    StorageProvider                        │  │
│  │  (Unified access to all persistence)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│         │              │              │              │          │
│         ▼              ▼              ▼              ▼          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │Relational │  │  Vector   │  │   Blob    │  │ Telemetry │   │
│  │   Store   │  │   Store   │  │   Store   │  │   Store   │   │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │
│         │              │              │              │          │
│         ▼              ▼              ▼              ▼          │
│  membrane.db    vectors.json      blobs/       telemetry.db    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  ~/.local/share/kgents/  (XDG_DATA_HOME)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Learnings

### What Worked

1. **Interface abstraction** (`IRelationalStore`, `IVectorStore`, etc.) enables provider swapping
2. **XDG compliance** makes paths predictable and configurable
3. **Schema versioning** allows safe migrations
4. **WAL mode** for SQLite enables concurrent access

### Anti-Patterns Avoided

1. **Per-project databases** - Creates fragmentation, hard to query globally
2. **Multiple config locations** - Now just XDG + per-project
3. **Hardcoded paths** - All paths configurable via env vars

### Future Improvements

1. Move remaining `~/.kgents/` services to XDG (see Migration Roadmap below)
2. Add Alembic migrations for complex schema changes
3. Support PostgreSQL for team deployments

---

## Migration Roadmap: Legacy `~/.kgents/` Services

The following services still use legacy `~/.kgents/` paths and need migration to XDG structure.

### Priority 1: Active Services (Witness, Prompt)

| Service | Current Path | Target | Complexity |
|---------|--------------|--------|------------|
| **Witness Daemon** | `~/.kgents/witness.pid`, `~/.kgents/witness.log`, `~/.kgents/witness.json` | `~/.cache/kgents/witness.log` (logs), `membrane.db` (state) | Medium |
| **Prompt History** | `~/.kgents/prompt-history/` | `membrane.db` (prompt_checkpoints table) | Medium |
| **Telemetry Config** | `~/.kgents/telemetry.yaml` | `~/.config/kgents/telemetry.yaml` | Low |
| **Aliases** | `~/.kgents/aliases.yaml` | `~/.config/kgents/aliases.yaml` | Low |

### Priority 2: Agent State

| Service | Current Path | Target | Complexity |
|---------|--------------|--------|------------|
| **Soul (K-gent)** | `~/.kgents/soul/` | `membrane.db` (agent_state table, genus="soul") | Medium |
| **Hypnagogia** | `~/.kgents/hypnagogia/` | `membrane.db` (agent_state table, genus="hypnagogia") | Low |
| **Garden** | `~/.kgents/garden/` | `membrane.db` (agent_state table, genus="garden") | Low |
| **Audit** | `~/.kgents/audit/` | `~/.cache/kgents/audit.jsonl` (ephemeral logs) | Low |

### Priority 3: Blob Storage

| Service | Current Path | Target | Complexity |
|---------|--------------|--------|------------|
| **Ghost Cache** | `~/.kgents/ghost/` | `~/.local/share/kgents/blobs/ghost/` | Low |
| **Atelier Gallery** | `~/.kgents/atelier/gallery/` | `~/.local/share/kgents/blobs/atelier/gallery/` | Low |
| **Atelier Queue** | `~/.kgents/atelier/queue/` | `~/.local/share/kgents/blobs/atelier/queue/` | Low |
| **Traces** | `~/.kgents/traces/` | `~/.local/share/kgents/traces/` | Low |

### Priority 4: Infrastructure (Lower Priority)

| Service | Current Path | Target | Notes |
|---------|--------------|--------|-------|
| **D-gent Data** | `~/.kgents/data/` | `~/.local/share/kgents/data/` | Backend storage |
| **I-gent State** | `~/.kgents/i-gent-state.json` | `membrane.db` (agent_state) | UI state |
| **L-gent Vectors** | `.kgents/vectors.json` | Uses per-project `.kgents/` (keep as-is) | Per-project |
| **Embeddings Cache** | `.kgents/embeddings_cache.json` | Uses per-project `.kgents/` (keep as-is) | Per-project |

### Per-Project Paths (Keep As-Is)

These paths are intentionally per-project and should remain:

| Path | Purpose |
|------|---------|
| `.kgents/config.yaml` | Project configuration |
| `.kgents/catalog.json` | Agent registry |
| `.kgents/ghost/` | Project-specific ghost files |
| `.kgents/flows/` | Flow definitions |
| `.kgents/shortcuts.yaml` | Project shortcuts |
| `.kgents/cortex.db` | Legacy project DB (being deprecated) |

### Migration Pattern

Each migration follows the same pattern:

```python
from protocols.cli.instance_db import StorageProvider, XDGPaths

async def migrate_service(service_name: str) -> None:
    paths = XDGPaths.resolve()
    legacy_path = Path.home() / ".kgents" / service_name

    if not legacy_path.exists():
        return  # Nothing to migrate

    storage = await StorageProvider.from_config()

    # Service-specific migration logic
    if service_name == "witness":
        # Migrate state to membrane.db
        state = json.loads((legacy_path / "witness.json").read_text())
        await storage.relational.execute(
            "INSERT OR REPLACE INTO witness_state ...",
            {"state": json.dumps(state)}
        )
        # Move logs to cache
        shutil.move(legacy_path / "witness.log", paths.cache / "witness.log")

    # Mark as migrated
    legacy_path.rename(f"{legacy_path}.migrated")

    await storage.close()
```

### New Tables Needed

```sql
-- Add to membrane.db migrations:

-- Generic agent state table
CREATE TABLE IF NOT EXISTS agent_state (
    agent_id TEXT PRIMARY KEY,
    genus TEXT NOT NULL,  -- "soul", "hypnagogia", "garden", "i-gent"
    state TEXT NOT NULL,  -- JSON
    version INTEGER DEFAULT 1,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_state_genus ON agent_state(genus);

-- Witness daemon state
CREATE TABLE IF NOT EXISTS witness_state (
    id TEXT PRIMARY KEY,
    pid INTEGER,
    started_at TEXT,
    last_heartbeat TEXT,
    config TEXT,  -- JSON
    status TEXT
);

-- Prompt evolution checkpoints (for prompt-history migration)
CREATE TABLE IF NOT EXISTS prompt_checkpoints (
    id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    content TEXT NOT NULL,
    sections TEXT,  -- JSON array
    parent_id TEXT,
    created_at TEXT NOT NULL,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_prompt_checkpoints_hash ON prompt_checkpoints(content_hash);
```

---

## Quick Reference

```bash
# View membrane.db tables
sqlite3 ~/.local/share/kgents/membrane.db ".tables"

# Check sessions
sqlite3 ~/.local/share/kgents/membrane.db "SELECT id, name, state FROM cli_sessions LIMIT 5"

# Check schema version
sqlite3 ~/.local/share/kgents/membrane.db "SELECT * FROM schema_version"
```

---

## Cross-References

- `spec/agents/d-gent.md` — D-gent persistence layer specification
- `docs/skills/metaphysical-fullstack.md` — Layer 1 (Persistence) in the fullstack
- `protocols/cli/instance_db/` — Implementation

---

*This is a skill document. See `docs/skills/` for the full skills library.*
