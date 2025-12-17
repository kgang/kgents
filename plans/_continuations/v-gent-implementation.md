# Continuation: V-gent Implementation

**Status**: Phase 7 COMPLETE (2025-12-16)

## Context

The V-gent (Vector Agents) specification has been completed:
- `spec/v-gents/core.md` — VgentProtocol, Embedding, SearchResult, DistanceMetric
- `spec/v-gents/backends.md` — Memory, D-gent, pgvector, Qdrant backends
- `spec/v-gents/integrations.md` — L-gent, M-gent, D-gent, K-gent integration
- `spec/v-gents/README.md` — Overview and philosophy

**Goal**: Implement V-gent as a dedicated agent genus, extract vector operations from L-gent/M-gent, and establish V-gent as shared infrastructure.

## Background Research

Before implementing, read these files to understand the current state:

### Specs (already done)
- `spec/v-gents/*.md` — The specification you're implementing

### Current Vector Implementation (to be refactored)
- `agents/l/vector_backend.py` — VectorBackend protocol, ChromaDBBackend, FAISSBackend
- `agents/l/vector_db.py` — DgentVectorBackend, VectorCatalog
- `agents/l/_tests/test_vector_backend.py` — Existing tests
- `agents/l/_tests/test_vector_db.py` — Existing tests

### Related Infrastructure
- `agents/d/protocol.py` — DgentProtocol (pattern to follow)
- `agents/d/router.py` — DgentRouter (pattern for VgentRouter)
- `agents/d/backends/` — Backend structure to mirror
- `agents/m/associative.py` — AssociativeMemory (will consume V-gent)

### Patterns
- `docs/skills/building-agent.md` — Agent creation patterns
- `docs/skills/test-patterns.md` — Testing conventions

## Implementation Phases

### Phase 1: Core Protocol & Types (Foundation) ✅ COMPLETE

**Created V-gent module structure:**

```
impl/claude/agents/v/
├── __init__.py           # Public exports
├── protocol.py           # VgentProtocol
├── types.py              # Embedding, VectorEntry, SearchResult, DistanceMetric
├── backends/
│   ├── __init__.py
│   ├── memory.py         # MemoryVectorBackend
│   └── dgent.py          # DgentVectorBackend
├── router.py             # VgentRouter
└── _tests/
    ├── __init__.py
    ├── conftest.py       # Fixtures
    ├── test_protocol.py  # Protocol compliance tests
    ├── test_memory.py    # Memory backend tests
    ├── test_dgent.py     # D-gent backend tests
    └── test_router.py    # Router tests
```

**Deliverables:**
1. `agents/v/types.py` — Embedding, VectorEntry, SearchResult, DistanceMetric
2. `agents/v/protocol.py` — VgentProtocol with 7 methods
3. `agents/v/backends/memory.py` — In-memory backend (Tier 0)
4. `agents/v/_tests/test_protocol.py` — Protocol compliance tests

**Success Criteria:**
- [x] VgentProtocol is runtime_checkable ✅
- [x] MemoryVectorBackend passes all protocol tests ✅
- [x] Distance metrics implement metric space laws ✅
- [x] 20+ tests passing ✅ (76 tests passing)

### Phase 2: D-gent Backend (Persistence) ✅ COMPLETE

**Implemented D-gent-backed persistence:**

**Deliverables:**
1. `agents/v/backends/dgent.py` — DgentVectorBackend ✅
2. `agents/v/_tests/test_dgent.py` — Persistence tests ✅ (44 tests)

**Key Features:**
- Vectors serialized to bytes (struct pack) for D-gent storage
- Metadata stored in Datum.metadata
- In-memory index rebuilt on startup via `load_index()`
- Namespace isolation for multiple vector stores

**Success Criteria:**
- [x] Vectors persist across restarts ✅
- [x] Index rebuilds correctly on load ✅
- [x] Search works with D-gent backends ✅
- [x] 15+ additional tests ✅ (44 tests)

### Phase 3: Router & Graceful Degradation ✅ COMPLETE (2025-12-16)

**Implemented VgentRouter with backend selection:**

**Deliverables:**
1. `agents/v/router.py` — VgentRouter with fallback chain ✅
2. `agents/v/_tests/test_router.py` — Router tests ✅ (43 tests)

**Key Features:**
- `VectorBackend` enum: MEMORY, DGENT, POSTGRES, QDRANT
- `BackendStatus` for availability checking
- Environment override via `KGENTS_VGENT_BACKEND`
- Fallback chain: [DGENT, MEMORY] by default
- D-gent injection support for testing
- Automatic index loading for D-gent backend
- `create_vgent()` factory function
- Concurrent access safety via asyncio.Lock

**Success Criteria:**
- [x] Router selects best available backend ✅
- [x] Graceful fallback when preferred unavailable ✅
- [x] Environment override works ✅
- [x] 10+ router tests ✅ (43 tests)

**Total V-gent Tests: 163 passing**

### Phase 4: L-gent Integration (Refactor) ✅ COMPLETE (2025-12-16)

**Refactored L-gent to use V-gent:**

**Files Created:**
- `agents/l/vgent_adapter.py` — Two-way adapters for V-gent ↔ L-gent interop
- `agents/l/_tests/test_vgent_adapter.py` — 23 tests for adapter integration

**Files Modified:**
- `agents/l/vector_backend.py` → Added deprecation warnings
- `agents/l/vector_db.py` → Added `VectorCatalog.create_with_vgent()` factory
- `agents/l/__init__.py` → Export new adapter classes

**Key Changes:**
```python
# Two-way adapters
from agents.l.vgent_adapter import VgentToLgentAdapter, LgentToVgentAdapter

# V-gent → L-gent (for existing L-gent code)
vgent = MemoryVectorBackend(dimension=384)
lgent_backend = VgentToLgentAdapter(vgent)

# New: VectorCatalog with V-gent injection
catalog = await VectorCatalog.create_with_vgent(
    embedder=embedder,
    vgent=vgent,
)
```

**Exports Added:**
- `VgentToLgentAdapter` — Wrap V-gent for L-gent consumers
- `LgentToVgentAdapter` — Wrap L-gent for V-gent consumers
- `create_vgent_adapter` — Factory function
- `migrate_lgent_backend_to_vgent` — Migration helper (deprecated)

**Success Criteria:**
- [x] L-gent works with V-gent injection via `create_with_vgent()`
- [x] Backward compatibility via `VgentToLgentAdapter`
- [x] Deprecation warnings on `agents/l/vector_backend` imports
- [x] 23 adapter tests passing
- [x] 163 V-gent tests passing

**Note:** Legacy `DgentVectorBackend` in `vector_db.py` depends on non-existent
`agents.d.vector` module. This is deprecated in favor of V-gent integration.

### Phase 5: M-gent Integration (Refactor) ✅ COMPLETE (2025-12-16)

**Refactored M-gent AssociativeMemory to use V-gent:**

**Files Modified:**
- `agents/m/associative.py` → Added V-gent integration with backward compatibility
- `agents/m/_tests/conftest.py` → Added V-gent fixtures
- `agents/m/_tests/test_vgent_integration.py` → 15 new integration tests

**Key Changes:**
```python
# Backward compatible: Two modes
class AssociativeMemory:
    # Optional V-gent backend
    _vgent: VgentProtocol | None = None

    @classmethod
    async def create_with_vgent(cls, dgent, vgent, embedder=None):
        """Create V-gent-backed instance."""
        ...

    async def recall(self, cue, limit=5, threshold=0.5):
        if self._vgent is not None:
            return await self._recall_with_vgent(...)  # Efficient
        return await self._recall_linear(...)  # Original

# Usage (new V-gent mode)
from agents.v import MemoryVectorBackend
vgent = MemoryVectorBackend(dimension=64)
mgent = await AssociativeMemory.create_with_vgent(dgent, vgent)

# Usage (original mode - still works)
mgent = AssociativeMemory(dgent=dgent)
```

**Key Features:**
- `create_with_vgent()` factory for V-gent integration
- `has_vgent` property for introspection
- V-gent vectors added on `remember()`
- V-gent search used in `recall()` with lifecycle filtering
- Consolidation cleans COMPOSTING vectors from V-gent
- All original tests pass (backward compatibility)

**Success Criteria:**
- [x] AssociativeMemory uses V-gent for recall ✅
- [x] Memory lifecycle still managed by M-gent ✅
- [x] All M-gent tests pass ✅ (145 tests)
- [x] 15 new V-gent integration tests ✅

**Total V-gent Tests: 163 + 15 M-gent integration = 178 passing**

### Phase 6: External Backends (Optional)

**Add production-grade backends:**

**Deliverables:**
1. `agents/v/backends/pgvector.py` — PostgreSQL + pgvector
2. `agents/v/backends/qdrant.py` — Qdrant client
3. Integration tests (require external services)

**These are optional** — the D-gent backend covers most use cases. Only implement if:
- User has Qdrant/pgvector in their stack
- Dataset exceeds D-gent's practical limits (>100K vectors)

### Phase 7: AGENTESE Paths ✅ COMPLETE (2025-12-16)

**Wired V-gent into AGENTESE:**

**Files Created:**
- `protocols/agentese/contexts/self_vector.py` — VectorNode with 11 affordances
- `protocols/agentese/contexts/_tests/test_self_vector.py` — 36 tests

**Files Modified:**
- `protocols/agentese/contexts/self_.py` → Added VectorNode import, SELF_AFFORDANCES["vector"], resolve case, factory param
- `protocols/agentese/contexts/__init__.py` → Added VectorNode exports, vgent param to create_context_resolvers()

**Paths Implemented:**
```
self.vector.manifest         # View vector state
self.vector.add[id, embedding, metadata]  # Insert vector
self.vector.add_batch[entries]            # Bulk insert
self.vector.search[query, limit, filters, threshold]  # Similarity search
self.vector.get[id]          # Retrieve by ID
self.vector.remove[id]       # Delete by ID
self.vector.clear            # Remove all
self.vector.count            # Get total count
self.vector.exists[id]       # Check existence
self.vector.dimension        # Get vector dimension
self.vector.metric           # Get distance metric
self.vector.status           # Overall status
```

**Key Features:**
- V-gent integration via factory: `create_self_resolver(vgent=vgent)`
- Graceful fallback: works without V-gent using in-memory dict
- Full cosine similarity implementation in fallback mode
- Metadata filtering in search
- Threshold filtering in search

**Success Criteria:**
- [x] VectorNode implements all 11 affordances ✅
- [x] Resolution works via `self.vector.*` path ✅
- [x] Fallback mode works without V-gent ✅
- [x] V-gent integration works when available ✅
- [x] 36 tests passing ✅

**Total V-gent + AGENTESE Tests: 163 + 36 = 199 passing**

## Testing Strategy

### Unit Tests (per phase)
- Protocol compliance: Does backend implement all methods?
- Metric space laws: Identity, symmetry, triangle inequality
- Edge cases: Empty index, duplicate IDs, dimension mismatch

### Integration Tests
- V + D: Vectors persist via D-gent projection lattice
- V + L: L-gent search works with V-gent backend
- V + M: M-gent recall works with V-gent backend

### Property-Based Tests (optional)
- Search results are sorted by similarity
- Add/remove are idempotent
- Count is consistent with add/remove

## Acceptance Criteria

The implementation is complete when:

1. **Core**: VgentProtocol with Memory and D-gent backends ✅
2. **Router**: VgentRouter with graceful degradation ✅
3. **L-gent**: Refactored to use V-gent (backward compatible) ✅
4. **M-gent**: Refactored to use V-gent ✅
5. **Tests**: 199 tests covering all phases ✅ (163 V-gent + 36 AGENTESE)
6. **AGENTESE**: self.vector.* paths wired ✅
7. **Docs**: `docs/skills/vector-agent.md` with usage patterns (TODO)

## Non-Goals (This Phase)

- GPU-accelerated search (future)
- Distributed V-gent (future)
- Custom distance metrics beyond the 4 standard ones
- Automatic embedding generation (embedder is external)

## Commands

```bash
# Run V-gent tests
cd impl/claude && uv run pytest agents/v/ -v

# Run integration tests
cd impl/claude && uv run pytest agents/l/_tests/test_vector*.py agents/m/_tests/test_associative.py -v

# Type check
cd impl/claude && uv run mypy agents/v/
```

## Prompt for Claude Code

```
Implement V-gent Phase 1: Core Protocol & Types

Read the spec first:
- spec/v-gents/core.md
- spec/v-gents/backends.md

Create the module structure:
- agents/v/__init__.py
- agents/v/types.py (Embedding, VectorEntry, SearchResult, DistanceMetric)
- agents/v/protocol.py (VgentProtocol, BaseVgent)
- agents/v/backends/__init__.py
- agents/v/backends/memory.py (MemoryVectorBackend)
- agents/v/_tests/conftest.py
- agents/v/_tests/test_protocol.py
- agents/v/_tests/test_memory.py

Follow patterns from:
- agents/d/protocol.py (protocol structure)
- agents/d/backends/memory.py (memory backend pattern)
- docs/skills/test-patterns.md (testing conventions)

Success: 20+ tests passing, MemoryVectorBackend implements VgentProtocol.
```
