# Unified Storage Protocol

> *"PostgreSQL is the cortex. Files are the skeleton. The cortex holds state. The skeleton holds structure."*

**Status**: Canonical | **Layer**: 0 (Persistence) | **Impl**: `impl/claude/services/storage/`

---

## Purpose

The Unified Storage Protocol defines how kgents manages all file-based storage across the system. It provides XDG-compliant directory management and separates concerns between database-backed state (PostgreSQL) and file-based structure (staging, exports, backups).

---

## Philosophy

### Storage Separation

```
PostgreSQL (Primary Store)
├── Relational data (crystals, marks, entities)
├── Vector embeddings (pgvector)
└── Transactional state

Files (Secondary Store)
├── Staging (uploads)
├── Exports (user downloads)
├── Backups (vector snapshots)
└── Static assets (cosmos K-Blocks)
```

**Core Principle**: PostgreSQL is the source of truth. Files are for human-readable artifacts and staging areas.

### XDG Compliance

kgents follows the XDG Base Directory Specification with user-friendly defaults:

```
~/.kgents/                      # Data (user-friendly default)
├── cosmos/                     # K-Block storage
├── uploads/                    # Sovereign staging area
├── vectors/                    # Vector export/backup
├── witness/                    # Witness marks (file backup)
├── exports/                    # User exports
├── sovereign/                  # Sovereign copies
└── tmp/                        # Temporary files

~/.config/kgents/               # Config
├── infrastructure.yaml         # Infrastructure config
└── profiles/                   # Named profiles

~/.cache/kgents/                # Cache
├── embeddings/                 # Cached embeddings
└── http/                       # HTTP cache

~/.local/state/kgents/          # State
└── logs/                       # Log files
```

**Design Decision**: We use `~/.kgents` instead of `~/.local/share/kgents` for better discoverability and user-friendliness. This is a CLI tool, not a GUI application, so user-visible paths are preferred.

---

## Architecture

### StorageProvider

Central abstraction for all file operations:

```python
from services.storage import get_storage_provider

provider = get_storage_provider()

# Access paths
uploads_dir = provider.paths.uploads
cosmos_dir = provider.paths.cosmos

# Ensure directories exist
provider.ensure_all_dirs()

# Validate paths
safe_path = provider.validate_path(some_path)

# Hash files
content_hash = provider.hash_file(file_path)
```

### Path Resolution

Environment variables provide override capability:

```bash
# Override data root (default: ~/.kgents)
export KGENTS_DATA_ROOT=/custom/path

# Override config root (default: ~/.config/kgents)
export KGENTS_CONFIG_ROOT=/custom/config

# Override cache root (default: ~/.cache/kgents)
export KGENTS_CACHE_ROOT=/custom/cache
```

---

## Storage Tiers

### Tier 0: PostgreSQL (Primary)

**Purpose**: All persistent state, relations, vectors

**What Lives Here**:
- Brain crystals (K-Blocks as relational entities)
- Witness marks (decision traces)
- User chat history
- Entity metadata
- Vector embeddings (pgvector)
- Morpheus dreams
- Agent state

**Access Pattern**: Via D-gent Universe and TableAdapters

```python
from agents.d.universe import get_universe

universe = get_universe()
crystals = await universe.all(Crystal)
```

**Lifecycle**: Persistent, ACID-compliant, backed up regularly

### Tier 1: Files (Secondary)

**Purpose**: Staging, exports, backups, human-readable artifacts

**What Lives Here**:
- `uploads/`: Sovereign staging area (pre-ingestion)
- `cosmos/`: K-Block file storage (for git integration)
- `exports/`: User-requested exports
- `vectors/`: Vector snapshots for backup
- `witness/`: Witness mark file backups (for auditing)
- `sovereign/`: Versioned sovereign copies

**Access Pattern**: Via StorageProvider

```python
from services.storage import get_storage_provider

provider = get_storage_provider()
uploads = provider.paths.uploads
```

**Lifecycle**: Ephemeral or user-managed

### Tier 2: Cache

**Purpose**: Non-essential, regenerable data

**What Lives Here**:
- `embeddings/`: Cached embedding computations
- `http/`: HTTP response cache

**Access Pattern**: Via StorageProvider

**Lifecycle**: Cleared on `kg cache clear` or periodically

---

## Directory Semantics

### cosmos/

K-Block file storage for git integration. Each K-Block exists as both:
1. PostgreSQL row (Crystal table) — source of truth
2. File on disk (cosmos/) — for git diffing, editing

**Sync Protocol**: Bidirectional
- File changes → ingest → PostgreSQL update
- PostgreSQL changes → export → file update

### uploads/

Sovereign staging area. Files here are **unmapped** — they exist but are not yet integrated.

**Integration Protocol**:
1. User drops file in uploads/
2. UI surfaces file with suggested layer (spec/impl/docs)
3. User confirms → triggers ingestion → moves to cosmos/ or integrates to PostgreSQL
4. Witness mark created

### exports/

User-requested exports (PDF, JSON, markdown bundles).

**Lifecycle**: User-managed. Periodically cleaned (30 days).

### vectors/

Vector snapshots for backup/portability. PostgreSQL pgvector is primary; this is fallback.

**Use Case**: Export vectors for:
- Backup before schema migration
- Offline analysis
- Vector store migration (pgvector → Qdrant)

### witness/

File-based backup of witness marks. PostgreSQL is primary; files are audit trail.

**Format**: JSONL (one mark per line)

### sovereign/

Versioned sovereign copies of ingested entities. See `spec/protocols/inbound-sovereignty.md`.

**Structure**:
```
sovereign/
└── spec/protocols/k-block.md/
    ├── v1/
    │   ├── content.md
    │   └── meta.json
    ├── v2/
    │   ├── content.md
    │   └── meta.json
    └── current -> v2/
```

### categorical/

Categorical reasoning study data (Phase 1 validation).

**Contents**:
- `categorical_phase1_problems.json` — Problem set for monad/sheaf studies
- `phase1b_results_*.json` — Correlation study results

**Migration**: Files previously in `impl/claude/data/` moved to `~/.kgents/categorical/`

---

## D-gent Integration

D-gent (the data agent) handles **Datum** persistence for its own backends:

```python
from agents.d import DgentRouter

router = DgentRouter()
# Auto-selects best backend: Postgres > SQLite > JSONL > Memory
# SQLite/JSONL use ~/.kgents/data/ (handled internally by D-gent)
```

**Key Insight**: D-gent backends (SQLite, JSONL) **already handle XDG paths** internally. You don't need to use StorageProvider for D-gent operations.

**StorageProvider is for**:
- Higher-level services (uploads, exports, backups)
- Explicit file operations (not Datum-based)
- Directory management

---

## Usage Patterns

### Service Initialization

```python
from services.storage import get_storage_provider

async def on_startup():
    provider = get_storage_provider()
    provider.ensure_all_dirs()  # Create all standard directories
```

### Upload Handling

```python
from services.storage import get_uploads_dir

uploads_dir = get_uploads_dir()
for file in uploads_dir.iterdir():
    # Process upload
    ...
```

### Export Generation

```python
from services.storage import get_exports_dir

exports_dir = get_exports_dir()
export_path = exports_dir / f"export-{timestamp}.pdf"
export_path.write_bytes(pdf_bytes)
```

### Sovereign Storage

```python
from services.sovereign import SovereignStore

store = SovereignStore()  # Uses ~/.kgents/sovereign by default
await store.store_version(
    path="spec/protocols/k-block.md",
    content=content_bytes,
    ingest_mark="mark-abc123",
)
```

---

## Migration from Legacy Paths

### Old Pattern (Avoid)

```python
# ❌ Hardcoded project-local paths
Path.cwd() / "data" / "uploads"
Path.cwd() / ".kgents" / "sovereign"

# ❌ Scattered path logic
home = Path.home()
data_dir = home / ".kgents" / "data"
```

### New Pattern (Use)

```python
# ✅ Unified StorageProvider
from services.storage import get_storage_provider

provider = get_storage_provider()
uploads = provider.paths.uploads
sovereign_root = provider.paths.data_root / "sovereign"

# ✅ Convenience functions
from services.storage import get_uploads_dir, get_cosmos_dir

uploads = get_uploads_dir()
cosmos = get_cosmos_dir()
```

### Migration Checklist

1. **Replace hardcoded paths**: Use `get_storage_provider().paths.*`
2. **Update service constructors**: Accept `Path | None` and default to StorageProvider
3. **Ensure directories**: Call `provider.ensure_all_dirs()` in startup
4. **Update tests**: Use `reset_storage_provider()` in fixtures
5. **Update docs**: Reference `spec/protocols/storage-unified.md`
6. **Move data files**: Migrate from `impl/claude/data/` to `~/.kgents/<category>/`

### Project-Specific vs User-Specific Paths

**User-Specific (XDG)**:
- `~/.kgents/` — User data (uploads, exports, sovereign copies)
- `~/.config/kgents/` — User config (infrastructure.yaml)
- `~/.cache/kgents/` — User cache (embeddings, HTTP)

**Project-Specific (Version-Controlled)**:
- `.kgents/ghost/` — Project-specific CI signals, git status, test flinches
  - Intentionally local to project, not XDG-compliant
  - Contains project state that should not be shared across projects
  - Example: test_flinches.jsonl, ci_signals.jsonl

**Gotcha**: Don't migrate project-local `.kgents/ghost/` to XDG! It's correct as-is.

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `KGENTS_DATA_ROOT` | Data directory root | `~/.kgents` |
| `KGENTS_CONFIG_ROOT` | Config directory root | `~/.config/kgents` |
| `KGENTS_CACHE_ROOT` | Cache directory root | `~/.cache/kgents` |
| `KGENTS_DATABASE_URL` | PostgreSQL connection | *(required for Postgres)* |
| `XDG_CONFIG_HOME` | XDG config base | `~/.config` |
| `XDG_CACHE_HOME` | XDG cache base | `~/.cache` |

---

## Anti-Patterns

```python
# ❌ Using files for primary state
crystal_file = cosmos_dir / "crystal.json"
crystal_file.write_text(json.dumps(crystal_data))

# ✅ Use PostgreSQL for state
await universe.insert(crystal)

# ❌ Bypassing StorageProvider
uploads = Path.home() / ".kgents" / "uploads"

# ✅ Use StorageProvider
uploads = get_uploads_dir()

# ❌ Hardcoded data directories in services
class MyService:
    def __init__(self):
        self.data_dir = Path.cwd() / "data" / "myservice"

# ✅ Accept optional path, default to StorageProvider
from services.storage import get_kgents_data_root

class MyService:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or (get_kgents_data_root() / "myservice")
```

---

## Cross-References

- **Agent**: `spec/agents/d-gent.md` (D-gent persistence layer)
- **Protocol**: `spec/protocols/inbound-sovereignty.md` (Sovereign copies)
- **Skill**: `docs/skills/unified-storage.md` (Usage patterns)
- **Implementation**: `impl/claude/services/storage/provider.py`
- **Bootstrap**: `impl/claude/infra/ground.py` (XDG path resolution)

---

*"One root. Many branches. All paths coherent."*
