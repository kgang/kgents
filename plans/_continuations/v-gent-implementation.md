# Continuation: V-gent Implementation

**Status**: Phase 1 COMPLETE (2025-12-16)

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
│   └── base.py           # BaseVgent (default implementations)
├── router.py             # VgentRouter
└── _tests/
    ├── __init__.py
    ├── conftest.py       # Fixtures
    ├── test_protocol.py  # Protocol compliance tests
    └── test_memory.py    # Memory backend tests
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

### Phase 2: D-gent Backend (Persistence)

**Add D-gent-backed persistence:**

**Deliverables:**
1. `agents/v/backends/dgent.py` — DgentVectorBackend
2. `agents/v/_tests/test_dgent_backend.py` — Persistence tests

**Key Implementation:**
```python
class DgentVectorBackend(BaseVgent):
    """
    Vectors stored as D-gent Datum with in-memory index.

    - Vectors serialized to bytes (struct pack)
    - Metadata in Datum.metadata
    - Index rebuilt on startup
    """

    def __init__(self, dgent: DgentProtocol, dimension: int, namespace: str = "vectors"):
        self.dgent = dgent
        self._dimension = dimension
        self._namespace = namespace
        self._index: dict[str, tuple[float, ...]] = {}

    async def _load_index(self) -> None:
        """Rebuild index from D-gent on startup."""
        ...
```

**Success Criteria:**
- [ ] Vectors persist across restarts
- [ ] Index rebuilds correctly on load
- [ ] Search works with D-gent JSONL/SQLite backends
- [ ] 15+ additional tests

### Phase 3: Router & Graceful Degradation

**Add VgentRouter with backend selection:**

**Deliverables:**
1. `agents/v/router.py` — VgentRouter with fallback chain
2. `agents/v/_tests/test_router.py` — Router tests

**Key Implementation:**
```python
class VgentRouter(BaseVgent):
    """
    Routes to best available backend.

    Selection: KGENTS_VGENT_BACKEND env → preferred → fallback chain
    Default chain: [DGENT, MEMORY]
    """

    async def _select_backend(self) -> VgentProtocol:
        # 1. Check env override
        # 2. Try preferred
        # 3. Fall through chain
        # 4. Last resort: memory
```

**Success Criteria:**
- [ ] Router selects best available backend
- [ ] Graceful fallback when preferred unavailable
- [ ] Environment override works
- [ ] 10+ router tests

### Phase 4: L-gent Integration (Refactor)

**Refactor L-gent to use V-gent:**

**Files to Modify:**
- `agents/l/vector_backend.py` → Deprecate, redirect to V-gent
- `agents/l/vector_db.py` → Use VgentProtocol instead of internal backend
- `agents/l/semantic.py` → Inject V-gent dependency

**Key Changes:**
```python
# Before: L-gent owns vector backend
class VectorCatalog:
    def __init__(self, embedder, catalog, vector_backend: VectorBackend):
        self.vector_backend = vector_backend  # L-gent's own type

# After: L-gent uses V-gent
class SemanticCatalog:
    def __init__(self, embedder, catalog, vgent: VgentProtocol):
        self.vgent = vgent  # V-gent protocol
```

**Migration Strategy:**
1. Add V-gent as optional dependency to L-gent
2. Create adapter: `LgentVectorBackendAdapter(VgentProtocol)`
3. Deprecate `agents/l/vector_backend.py` with warnings
4. Update tests to use V-gent

**Success Criteria:**
- [ ] L-gent works with V-gent injection
- [ ] Backward compatibility via adapter
- [ ] Deprecation warnings on old imports
- [ ] All L-gent tests pass

### Phase 5: M-gent Integration (Refactor)

**Refactor M-gent AssociativeMemory to use V-gent:**

**Files to Modify:**
- `agents/m/associative.py` → Inject V-gent for similarity search
- `agents/m/memory.py` → Keep Memory dataclass, remove embedded index

**Key Changes:**
```python
# Before: M-gent maintains its own index
class AssociativeMemory:
    _memories: dict[str, Memory]  # Includes embeddings inline

    async def recall(self, cue):
        # Linear scan of _memories
        for memory in self._memories.values():
            similarity = memory.similarity(cue_embedding)

# After: M-gent uses V-gent
class AssociativeMemory:
    def __init__(self, dgent: DgentProtocol, vgent: VgentProtocol, embedder):
        self.dgent = dgent
        self.vgent = vgent
        self.embedder = embedder

    async def recall(self, cue):
        query = await self.embedder.embed(cue)
        return await self.vgent.search(query, limit=limit)
```

**Success Criteria:**
- [ ] AssociativeMemory uses V-gent for recall
- [ ] Memory lifecycle still managed by M-gent
- [ ] All M-gent tests pass
- [ ] Performance comparable or better

### Phase 6: External Backends (Optional)

**Add production-grade backends:**

**Deliverables:**
1. `agents/v/backends/pgvector.py` — PostgreSQL + pgvector
2. `agents/v/backends/qdrant.py` — Qdrant client
3. Integration tests (require external services)

**These are optional** — the D-gent backend covers most use cases. Only implement if:
- User has Qdrant/pgvector in their stack
- Dataset exceeds D-gent's practical limits (>100K vectors)

### Phase 7: AGENTESE Paths

**Wire V-gent into AGENTESE:**

**Deliverables:**
1. `protocols/agentese/contexts/self_vector.py` — V-gent path handlers
2. Update `protocols/agentese/contexts/__init__.py`

**Paths to implement:**
```
self.vector.add[id, embedding]
self.vector.search[query]
self.vector.get[id]
self.vector.remove[id]
self.vector.count
self.vector.dimension
self.vector.metric
```

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

1. **Core**: VgentProtocol with Memory and D-gent backends
2. **Router**: VgentRouter with graceful degradation
3. **L-gent**: Refactored to use V-gent (backward compatible)
4. **M-gent**: Refactored to use V-gent
5. **Tests**: 80+ tests covering all phases
6. **Docs**: `docs/skills/vector-agent.md` with usage patterns

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
