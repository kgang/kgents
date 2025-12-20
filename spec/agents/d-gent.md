# D-gent: The Data Agent (Persistence Layer)

> *"The cortex is singular. Memory is global. Context is local."*

## Status

**Version**: 1.0
**Status**: Canonical
**Implementation**: `impl/claude/protocols/cli/instance_db/`
**Tests**: `test_storage.py`, `test_lifecycle.py`, `test_cli_session.py`

---

## Overview

D-gent owns all persistence for kgents. It is the **Layer 0** of the Metaphysical Fullstack (AD-009)—the foundation upon which services build. Other agents request storage via D-gent interfaces; D-gent manages migrations, backups, and recovery.

**Key Insight**: D-gent is infrastructure, not a Crown Jewel. It provides the categorical primitives that services compose.

---

## The Storage Polynomial

```python
STORAGE_POLYNOMIAL = PolyAgent[StorageState, StorageOp, StorageResult](
    positions=frozenset({
        StorageState.IDLE,
        StorageState.READING,
        StorageState.WRITING,
        StorageState.MIGRATING,
        StorageState.RECOVERING,
    }),
    directions=lambda s: VALID_OPS[s],
    transition=storage_transition,
)
```

**State Machine**:
```
IDLE --[read]--> READING --[done]--> IDLE
IDLE --[write]--> WRITING --[done]--> IDLE
IDLE --[migrate]--> MIGRATING --[done]--> IDLE
IDLE --[error]--> RECOVERING --[recovered]--> IDLE
```

---

## XDG Compliance

D-gent follows the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html):

| Purpose | Path | Environment Variable |
|---------|------|----------------------|
| **Configuration** | `~/.config/kgents/` | `XDG_CONFIG_HOME` |
| **Data** | `~/.local/share/kgents/` | `XDG_DATA_HOME` |
| **Cache** | `~/.cache/kgents/` | `XDG_CACHE_HOME` |

**Per-Project** (non-XDG):
- `.kgents/config.yaml` — Project-specific configuration
- `.kgents/catalog.json` — Agent registry for project

---

## Storage Providers

The `StorageProvider` unifies access to all persistence backends:

```python
@dataclass
class StorageProvider:
    relational: IRelationalStore    # → membrane.db
    vector: IVectorStore            # → vectors.json / sqlite-vec
    blob: IBlobStore                # → blobs/ directory
    telemetry: ITelemetryStore      # → telemetry.db
```

### Interfaces

```python
class IRelationalStore(Protocol):
    async def execute(self, query: str, params: dict | None = None) -> None: ...
    async def fetch_all(self, query: str, params: dict | None = None) -> list[dict]: ...
    async def fetch_one(self, query: str, params: dict | None = None) -> dict | None: ...
    async def close(self) -> None: ...

class IVectorStore(Protocol):
    async def add(self, id: str, vector: list[float], metadata: dict | None = None) -> None: ...
    async def search(self, query: list[float], k: int = 10) -> list[SearchResult]: ...
    async def close(self) -> None: ...

class IBlobStore(Protocol):
    async def put(self, key: str, data: bytes) -> None: ...
    async def get(self, key: str) -> bytes | None: ...
    async def delete(self, key: str) -> bool: ...
    async def close(self) -> None: ...

class ITelemetryStore(Protocol):
    async def append(self, events: list[TelemetryEvent]) -> None: ...
    async def query(self, span_id: str | None = None, limit: int = 100) -> list[TelemetryEvent]: ...
    async def close(self) -> None: ...
```

---

## membrane.db Schema

The unified database (`~/.local/share/kgents/membrane.db`) contains all persistent state:

### Core Tables

| Table | Purpose |
|-------|---------|
| `instances` | Active kgent instances with heartbeat |
| `shapes` | Observed patterns (shapes in the membrane) |
| `dreams` | Consolidated insights |
| `embedding_metadata` | Vector model tracking |
| `schema_version` | Migration versioning |

### CLI Session Tables

| Table | Purpose |
|-------|---------|
| `cli_sessions` | CLI sessions (repl, flow, script) |
| `cli_session_events` | Events within sessions |
| `cli_session_agents` | Agents spawned in sessions |
| `cli_session_artifacts` | Outputs from sessions |

### Self-Grow Tables

| Table | Purpose |
|-------|---------|
| `self_grow_proposals` | Proposed prompt changes |
| `self_grow_nursery` | Germinated proposals |
| `self_grow_rollback_tokens` | Rollback capability |

---

## Usage Pattern

### Via StorageProvider (Recommended)

```python
from protocols.cli.instance_db import StorageProvider

async def example():
    storage = await StorageProvider.from_config()
    await storage.run_migrations()

    # Unified access to all stores
    await storage.relational.execute("INSERT INTO shapes ...")
    results = await storage.vector.search(query_vec)
    await storage.blob.put("backups/today.bak", data)
    await storage.telemetry.append([event])

    await storage.close()
```

### Via Specific Services

```python
from protocols.cli.instance_db import CLISessionService, create_cli_session_service

async def cli_example():
    service = await create_cli_session_service()
    session = await service.start_session("interactive", "My REPL")
    await service.log_event(session.id, "command", "repl", "User ran check")
    await service.end_session(session.id, state="completed")
```

---

## Graceful Degradation

D-gent follows the Graceful Degradation principle (spec/principles.md):

| Condition | Behavior |
|-----------|----------|
| DB unavailable | In-memory fallback, warns on restart |
| Migration fails | Roll back to previous schema |
| Config parse error | Use XDG defaults |
| Env var unset | Use XDG defaults (non-strict mode) |

```python
# In-memory fallback
storage = await StorageProvider.create_minimal()
```

---

## Migration Strategy

### From Legacy Paths

Legacy `~/.kgents/` paths are being migrated to XDG structure:

| Legacy | Target | Status |
|--------|--------|--------|
| `~/.kgents/history.db` | `membrane.db` (cli_sessions) | COMPLETE |
| `~/.kgents/witness.*` | `membrane.db` + `~/.cache/kgents/` | PLANNED |
| `~/.kgents/ghost/` | `~/.local/share/kgents/blobs/ghost/` | PLANNED |
| `~/.kgents/prompt-history/` | `membrane.db` (prompt_checkpoints) | PLANNED |
| `~/.kgents/hypnagogia/` | `membrane.db` (agent_state) | PLANNED |
| `~/.kgents/soul/` | `membrane.db` (agent_state) | PLANNED |
| `~/.kgents/atelier/` | `~/.local/share/kgents/blobs/atelier/` | PLANNED |

### Migration Pattern

```python
# Each service follows the same pattern:
# 1. Read from legacy if exists
# 2. Write to new location
# 3. Mark legacy as migrated
# 4. Warn on next access of legacy path

def migrate_service(service_name: str) -> None:
    legacy = Path.home() / ".kgents" / service_name
    if legacy.exists():
        # Migrate...
        legacy.rename(f"{legacy}.migrated")
```

---

## Anti-Patterns

```python
# ❌ Hardcoded paths
state_path = Path.home() / ".kgents" / "state.json"

# ✅ XDG-compliant via StorageProvider
storage = await StorageProvider.from_config()
await storage.relational.execute("INSERT INTO agent_state ...")

# ❌ Multiple databases per project
project_db = project / ".kgents" / "cortex.db"

# ✅ Single global database with project_hash
await storage.relational.execute(
    "INSERT INTO shapes (project_hash, ...) VALUES (:hash, ...)",
    {"hash": project_hash}
)

# ❌ Direct file I/O for state
Path("~/.kgents/soul/state.json").write_text(json.dumps(state))

# ✅ StorageProvider interfaces
await storage.relational.execute(
    "INSERT OR REPLACE INTO agent_state (agent_id, genus, state) VALUES (:id, :genus, :state)",
    {"id": "soul", "genus": "k-gent", "state": json.dumps(state)}
)
```

---

## Principles Alignment

| Principle | How D-gent Embodies It |
|-----------|------------------------|
| **Tasteful** | One canonical DB, not scattered files |
| **Composable** | Interfaces enable provider swapping |
| **Generative** | Schema from spec, migrations derived |
| **Graceful Degradation** | In-memory fallback always works |
| **Transparent Infrastructure** | First-run messages tell user where data lives |

---

## Cross-References

- **Skill**: `docs/skills/unified-storage.md`
- **Skill**: `docs/skills/metaphysical-fullstack.md` (Layer 0)
- **Implementation**: `impl/claude/protocols/cli/instance_db/`
- **Principles**: `spec/principles.md` §Graceful Degradation, §Transparent Infrastructure

---

*"Every agent that persists does so through D-gent. D-gent is the ground upon which memory stands."*
