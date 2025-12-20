# Continuation: Unified Storage Infrastructure Migration

**Created**: 2025-12-20
**Previous Session**: Unified storage refactor (schema consolidation, CLISessionService, migration utility)
**Status**: Phase 1 complete, Phases 2-4 pending

---

## Context for Continuation Agent

You are continuing a storage infrastructure unification project. The previous session:

1. Added CLI session tables to `membrane.db` (unified from deprecated `history.db`)
2. Created `CLISessionService` in `protocols/cli/instance_db/cli_session.py`
3. Deprecated `history_path` in `context.py` (backward compatible)
4. Created migration utility (`migrate_history.py`)
5. Documented in `docs/skills/unified-storage.md`

**Current State**:
- `~/.local/share/kgents/membrane.db` is the canonical data store (XDG-compliant)
- `~/.kgents/` still has active services using legacy paths (witness, ghost, prompt-history, etc.)
- `d-gent` spec and `metaphysical-fullstack.md` skill don't reflect the unified architecture

---

## Mission

Design and execute a **multi-stage strategy** to:

1. **Universalize** the local DB infrastructure under `StorageProvider`
2. **Update** the metaphysical fullstack skill to reflect unified persistence
3. **Update** the D-gent spec to codify the storage layer
4. **Complete** migration of all legacy `~/.kgents/` services to XDG structure

---

## Phase 1: Audit & Inventory (RESEARCH)

**Goal**: Understand all current storage touchpoints

### Tasks

1. **Grep for `~/.kgents` and `.kgents/` references**:
   ```bash
   grep -r "\.kgents" --include="*.py" | grep -v "__pycache__"
   ```

2. **Catalog each service's storage needs**:
   | Service | Current Path | Data Type | Migration Complexity |
   |---------|--------------|-----------|---------------------|
   | Witness | `~/.kgents/witness.*` | JSON, logs, PID | Medium |
   | Ghost | `~/.kgents/ghost/` | Session ghosts | Low |
   | Prompt History | `~/.kgents/prompt-history/` | JSON checkpoints | Medium |
   | Hypnagogia | `~/.kgents/hypnagogia/` | Dream state | Low |
   | Soul | `~/.kgents/soul/` | K-gent state | Medium |
   | Atelier | `~/.kgents/atelier/` | Design artifacts | Low |
   | Brain | `~/.kgents/brain/` | Neural state | Medium |

3. **Read current specs**:
   - `spec/agents/d-gent.md` (or create if missing)
   - `docs/skills/metaphysical-fullstack.md`
   - `protocols/cli/instance_db/__init__.py` (current exports)

---

## Phase 2: Architecture Design (PLAN)

**Goal**: Design the universal storage interface

### Principles

1. **Single Source of Truth**: All persistent state through `StorageProvider`
2. **XDG Compliance**: Config in `~/.config/kgents/`, data in `~/.local/share/kgents/`
3. **Interface Stability**: Services depend on interfaces, not implementations
4. **Graceful Degradation**: In-memory fallback when DB unavailable

### Proposed Architecture

```
StorageProvider (singleton)
├── relational: IRelationalStore      → membrane.db
│   ├── instances, shapes, dreams     (existing)
│   ├── cli_sessions, cli_events      (just added)
│   ├── witness_state                 (NEW)
│   ├── prompt_checkpoints            (NEW - migrate from JSON)
│   └── agent_state                   (NEW - soul, brain, etc.)
│
├── vector: IVectorStore              → vectors.json / sqlite-vec
├── blob: IBlobStore                  → blobs/ directory
│   ├── ghost_sessions/               (migrate from ~/.kgents/ghost/)
│   ├── hypnagogia_dreams/            (migrate)
│   └── atelier_artifacts/            (migrate)
│
└── telemetry: ITelemetryStore        → telemetry.db
```

### New Tables to Add

```sql
-- Witness daemon state
CREATE TABLE witness_state (
    id TEXT PRIMARY KEY,
    pid INTEGER,
    started_at TEXT,
    last_heartbeat TEXT,
    config TEXT,  -- JSON
    status TEXT
);

-- Prompt evolution checkpoints (migrate from JSON files)
CREATE TABLE prompt_checkpoints (
    id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    content TEXT NOT NULL,
    sections TEXT,  -- JSON array
    parent_id TEXT,
    created_at TEXT NOT NULL,
    metadata TEXT
);

-- Generic agent state (for soul, brain, etc.)
CREATE TABLE agent_state (
    agent_id TEXT PRIMARY KEY,
    genus TEXT NOT NULL,  -- "soul", "brain", "hypnagogia"
    state TEXT NOT NULL,  -- JSON
    version INTEGER DEFAULT 1,
    updated_at TEXT NOT NULL
);
```

---

## Phase 3: Service Migration (IMPLEMENT)

**Goal**: Migrate each service to use `StorageProvider`

### Migration Order (by risk/complexity)

1. **Ghost Writer** (Low risk, simple blobs)
   - Current: `~/.kgents/ghost/` directory with session files
   - Target: `StorageProvider.blob` with `ghost_sessions/` prefix
   - Files: `protocols/cli/devex/ghost_writer.py`

2. **Prompt History** (Medium, has existing users)
   - Current: `~/.kgents/prompt-history/` JSON files
   - Target: `prompt_checkpoints` table in membrane.db
   - Files: `protocols/prompt/rollback/registry.py`

3. **Witness Daemon** (Medium, active service)
   - Current: `~/.kgents/witness.*` files
   - Target: `witness_state` table + logs to `~/.cache/kgents/witness.log`
   - Files: `services/witness/*.py`

4. **Soul/Brain/Hypnagogia** (Medium, agent state)
   - Current: Various `~/.kgents/` subdirectories
   - Target: `agent_state` table with genus differentiation
   - Files: Respective agent implementations

5. **Telemetry Config** (Low, just config)
   - Current: `~/.kgents/telemetry.yaml`
   - Target: `~/.config/kgents/telemetry.yaml`
   - Files: `protocols/agentese/telemetry_config.py`

### Migration Pattern

For each service:

```python
# Before (legacy)
state_path = Path.home() / ".kgents" / "service" / "state.json"
state = json.loads(state_path.read_text())

# After (unified)
from protocols.cli.instance_db import StorageProvider

storage = await StorageProvider.from_config()
state = await storage.relational.fetch_one(
    "SELECT state FROM agent_state WHERE agent_id = :id",
    {"id": "service"}
)
```

---

## Phase 4: Spec & Skill Updates (DOCUMENT)

**Goal**: Update specs to reflect the unified architecture

### D-gent Spec Updates

The D-gent (Data Agent) spec should codify:

1. **Storage Layer Responsibilities**
   - D-gent owns all persistence
   - Other agents request storage via D-gent interfaces
   - D-gent manages migrations, backups, recovery

2. **Interface Contracts**
   ```python
   class DGent(Protocol):
       async def store(self, key: str, value: Any, namespace: str) -> None: ...
       async def retrieve(self, key: str, namespace: str) -> Any: ...
       async def query(self, predicate: Callable, namespace: str) -> list[Any]: ...
   ```

3. **XDG Compliance**
   - Config: `XDG_CONFIG_HOME/kgents/` (default: `~/.config/kgents/`)
   - Data: `XDG_DATA_HOME/kgents/` (default: `~/.local/share/kgents/`)
   - Cache: `XDG_CACHE_HOME/kgents/` (default: `~/.cache/kgents/`)

### Metaphysical Fullstack Skill Updates

Add Layer 0 (Persistence) to the stack:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  0. PERSISTENCE LAYER     StorageProvider: membrane.db, vectors, blobs     │  ← NEW
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 5: Cleanup & Verification (COMPLETE)

**Goal**: Remove legacy paths, verify migration

### Cleanup Tasks

1. **Remove deprecated code paths**:
   - Delete `history_path` references after deprecation period
   - Remove `~/.kgents/history.db.migrated` backup
   - Clean up empty `~/.kgents/` subdirectories

2. **Add migration verification**:
   ```bash
   # Verify no code still references legacy paths
   grep -r "\.kgents/" --include="*.py" | grep -v "XDG\|deprecated\|migrated"
   ```

3. **Update tests**:
   - Add integration tests for `StorageProvider` with all services
   - Ensure in-memory fallback works for all storage types

4. **Documentation sweep**:
   - Update all `docs/skills/` that mention storage
   - Update `CLAUDE.md` if needed
   - Ensure `spec/agents/d-gent.md` is complete

---

## Files to Read First

Before starting, read these to understand current state:

1. `docs/skills/unified-storage.md` - Just created, explains current architecture
2. `protocols/cli/instance_db/storage.py` - StorageProvider implementation
3. `protocols/cli/instance_db/cli_session.py` - Example of new unified pattern
4. `docs/skills/metaphysical-fullstack.md` - Current skill to update
5. `spec/agents/d-gent.md` - D-gent spec (may not exist yet)

---

## Success Criteria

The migration is complete when:

1. ✅ All services use `StorageProvider` for persistence
2. ✅ No production code references `~/.kgents/` directly
3. ✅ `~/.kgents/` can be deleted without breaking anything
4. ✅ D-gent spec defines the persistence layer contract
5. ✅ Metaphysical fullstack includes Layer 0 (Persistence)
6. ✅ All tests pass with XDG-compliant paths
7. ✅ Migration utilities exist for any remaining legacy data

---

## Anti-Patterns to Avoid

1. **Don't break active services** - Each migration should be atomic and reversible
2. **Don't remove backward compatibility too early** - Deprecate first, remove later
3. **Don't hardcode paths** - Always use `XDGPaths.resolve()` or env vars
4. **Don't duplicate storage** - One service, one storage location

---

## Estimated Effort

| Phase | Effort | Notes |
|-------|--------|-------|
| Phase 1: Audit | 1 hour | Research, no code changes |
| Phase 2: Design | 1-2 hours | Architecture decisions |
| Phase 3: Migrate | 4-6 hours | Most of the work |
| Phase 4: Document | 1-2 hours | Spec and skill updates |
| Phase 5: Cleanup | 1 hour | Verification and removal |

**Total**: ~8-12 hours across multiple sessions

---

*This continuation plan was generated after the initial unified storage refactor session on 2025-12-20.*
