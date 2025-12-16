# V-gent Implementation Prompts

Ready-to-use prompts for implementing V-gent in phases.

---

## Prompt 1: Core Protocol & Memory Backend

```
Implement V-gent Phase 1: Core Protocol & Types

Context: V-gent is a new agent genus for vector operations. The spec is complete at spec/v-gents/*.md. Your job is to implement the reference implementation.

Read first:
1. spec/v-gents/core.md - VgentProtocol, types, mathematical properties
2. spec/v-gents/backends.md - Backend tier system
3. agents/d/protocol.py - Pattern to follow for protocol structure
4. agents/d/backends/memory.py - Pattern for memory backend

Create these files:

agents/v/__init__.py
- Export: VgentProtocol, Embedding, VectorEntry, SearchResult, DistanceMetric
- Export: MemoryVectorBackend, create_vgent

agents/v/types.py
- Embedding: vector (tuple), dimension, source, metadata
- VectorEntry: id, embedding, metadata
- SearchResult: id, similarity, distance, metadata
- DistanceMetric: Enum with COSINE, EUCLIDEAN, DOT_PRODUCT, MANHATTAN
- Implement similarity() method on DistanceMetric

agents/v/protocol.py
- VgentProtocol with @runtime_checkable
- 7 methods: add, add_batch, remove, clear, get, search, count
- Properties: dimension, metric
- BaseVgent with default implementations for exists()

agents/v/backends/__init__.py
- Export MemoryVectorBackend

agents/v/backends/memory.py
- MemoryVectorBackend implementing VgentProtocol
- In-memory dict storage
- Linear scan search with metric.similarity()
- Metadata filtering support

agents/v/_tests/conftest.py
- Fixtures: sample_embeddings, vgent_memory

agents/v/_tests/test_types.py
- Test Embedding creation, dimension validation
- Test DistanceMetric.similarity() for all metrics
- Test metric space laws: identity, symmetry, non-negativity

agents/v/_tests/test_memory.py
- Test add/get/remove/clear
- Test search with different limits, thresholds, filters
- Test batch operations
- Test count consistency

Success criteria:
- [ ] VgentProtocol is runtime_checkable
- [ ] MemoryVectorBackend passes protocol compliance
- [ ] All 4 distance metrics work correctly
- [ ] 25+ tests passing
- [ ] uv run pytest agents/v/ -v passes
```

---

## Prompt 2: D-gent Backend

```
Implement V-gent Phase 2: D-gent Backend

Context: V-gent Phase 1 is complete (Memory backend). Now add D-gent persistence.

Read first:
1. spec/v-gents/backends.md - DgentVectorBackend section
2. agents/v/protocol.py - VgentProtocol to implement
3. agents/d/protocol.py - DgentProtocol you'll depend on
4. agents/d/router.py - Pattern for graceful degradation

Create these files:

agents/v/backends/dgent.py
- DgentVectorBackend(dgent: DgentProtocol, dimension: int, namespace: str)
- Store vectors as Datum with serialized bytes
- Maintain in-memory index for search
- Implement load_index() to rebuild from D-gent on startup
- Serialize vectors with struct.pack (floats)

agents/v/_tests/test_dgent_backend.py
- Test with MemoryBackend D-gent
- Test persistence: add, reload, search finds vectors
- Test namespace isolation
- Test causal_parent support (optional)

Update agents/v/__init__.py:
- Export DgentVectorBackend

Key implementation details:
- Datum.id format: "vgent:{namespace}:{vector_id}"
- Datum.content: struct.pack("{n}f", *vector)
- Datum.metadata: include original metadata + dimension
- _index is dict[str, tuple[float, ...]] for fast search
- load_index() calls dgent.list() and deserializes

Success criteria:
- [ ] Vectors persist across DgentVectorBackend instances
- [ ] Index rebuilds correctly from D-gent
- [ ] Search works after reload
- [ ] 15+ new tests passing
```

---

## Prompt 3: Router & Environment Config

```
Implement V-gent Phase 3: VgentRouter

Context: V-gent has Memory and D-gent backends. Now add the router for automatic selection.

Read first:
1. spec/v-gents/backends.md - VgentRouter section
2. agents/d/router.py - Pattern to follow exactly
3. agents/v/backends/*.py - Backends to route between

Create these files:

agents/v/router.py
- VectorBackend enum: MEMORY, DGENT (later: POSTGRES, QDRANT)
- BackendStatus dataclass
- VgentRouter implementing VgentProtocol
- Selection order: env → preferred → fallback_chain → memory
- Environment variable: KGENTS_VGENT_BACKEND
- create_vgent() factory function

agents/v/_tests/test_router.py
- Test auto-selection (should pick DGENT if available)
- Test env override
- Test preferred backend
- Test fallback when preferred unavailable
- Test force_backend()
- Test status() returns all backend availability

Update agents/v/__init__.py:
- Export VgentRouter, VectorBackend, create_vgent
- create_vgent(dimension, namespace, preferred) → VgentRouter

Success criteria:
- [ ] Router implements full VgentProtocol
- [ ] Graceful fallback works
- [ ] Environment override works
- [ ] 12+ new tests passing
```

---

## Prompt 4: L-gent Integration

```
Implement V-gent Phase 4: L-gent Integration

Context: V-gent is complete. Now refactor L-gent to use V-gent instead of embedded vectors.

Read first:
1. spec/v-gents/integrations.md - V×L section
2. agents/l/vector_backend.py - Current implementation to refactor
3. agents/l/vector_db.py - VectorCatalog that uses vector_backend
4. agents/l/semantic.py - SemanticBrain that may need updates

Strategy: Backward-compatible refactor
1. Keep old VectorBackend protocol in agents/l/vector_backend.py (deprecated)
2. Create adapter that wraps VgentProtocol as VectorBackend
3. Update VectorCatalog to accept either
4. Add deprecation warnings

Changes:

agents/l/vector_backend.py
- Add deprecation warning at module level
- Keep existing code for backward compatibility

agents/l/vgent_adapter.py (NEW)
- VgentAdapter(vgent: VgentProtocol) implements old VectorBackend
- Translates between protocols

agents/l/vector_db.py
- Update VectorCatalog.__init__ to accept vgent: VgentProtocol | None
- If vgent provided, use directly
- If vector_backend provided (old style), emit deprecation warning
- Update search() to use vgent.search()

agents/l/_tests/test_vector_db.py
- Add tests using VgentProtocol
- Keep old tests working

Success criteria:
- [ ] VectorCatalog works with V-gent injection
- [ ] Old code still works (with deprecation warning)
- [ ] All existing L-gent tests pass
- [ ] 5+ new integration tests
```

---

## Prompt 5: M-gent Integration

```
Implement V-gent Phase 5: M-gent Integration

Context: V-gent and L-gent integration complete. Now refactor M-gent AssociativeMemory.

Read first:
1. spec/v-gents/integrations.md - V×M section
2. agents/m/associative.py - Current AssociativeMemory
3. agents/m/memory.py - Memory dataclass
4. agents/m/protocol.py - MgentProtocol

Strategy: Add V-gent as optional dependency

Changes:

agents/m/associative.py
- Update __init__ to accept optional vgent: VgentProtocol
- If vgent provided, delegate recall to vgent.search()
- If not provided, use existing linear scan (backward compat)
- Update remember() to also add to vgent if available
- Update forget() to also remove from vgent if available

agents/m/_tests/test_associative.py
- Add tests with V-gent injection
- Test recall uses vgent.search
- Test remember adds to vgent
- Test forget removes from vgent
- Keep existing tests working

Optional: Update agents/m/__init__.py exports

Success criteria:
- [ ] AssociativeMemory works with V-gent
- [ ] Old code still works without V-gent
- [ ] All existing M-gent tests pass
- [ ] 8+ new integration tests
- [ ] Performance comparable or better
```

---

## Prompt 6: AGENTESE Paths

```
Implement V-gent Phase 6: AGENTESE Integration

Context: V-gent is fully implemented. Now wire it into AGENTESE.

Read first:
1. spec/v-gents/core.md - AGENTESE paths section
2. protocols/agentese/contexts/self_.py - Pattern for self.* paths
3. protocols/agentese/contexts/self_memory.py - Similar integration
4. protocols/agentese/wiring.py - How paths get wired

Create:

protocols/agentese/contexts/self_vector.py
- register_vector_paths(logos: Logos, vgent: VgentProtocol)
- Paths:
  - self.vector.add[id, embedding, metadata?]
  - self.vector.search[query, limit?, threshold?, filters?]
  - self.vector.get[id]
  - self.vector.remove[id]
  - self.vector.count
  - self.vector.dimension
  - self.vector.metric
  - self.vector.clear

protocols/agentese/_tests/test_vector_paths.py
- Test each path with mock vgent
- Test parameter parsing

Update protocols/agentese/contexts/__init__.py
- Export register_vector_paths

Success criteria:
- [ ] All 8 paths work
- [ ] Parameters parse correctly
- [ ] 10+ tests passing
```

---

## Prompt 7: Documentation & Skills

```
Complete V-gent Phase 7: Documentation

Context: V-gent implementation is complete. Document it.

Create:

docs/skills/vector-agent.md
- When to use V-gent
- Quick start example
- Backend selection guide
- Integration patterns (with L-gent, M-gent)
- Embedder options
- Testing patterns

Update docs/systems-reference.md
- Add V-gent section with components table
- Add import patterns
- Add example code

Update CLAUDE.md (if taxonomy section exists)
- Add V-gent to agent taxonomy table

Success criteria:
- [ ] Skills doc covers common use cases
- [ ] Systems reference includes V-gent
- [ ] Examples are copy-paste runnable
```

---

## Full Implementation Prompt (All Phases)

For a single session that does everything:

```
Implement V-gent: Vector Agents for Semantic Search

The V-gent specification is complete at spec/v-gents/*.md. Implement the full reference implementation.

Phase 1: Core (agents/v/types.py, protocol.py, backends/memory.py)
Phase 2: D-gent Backend (agents/v/backends/dgent.py)
Phase 3: Router (agents/v/router.py)
Phase 4: L-gent Integration (refactor agents/l/vector_db.py)
Phase 5: M-gent Integration (refactor agents/m/associative.py)
Phase 6: AGENTESE (protocols/agentese/contexts/self_vector.py)
Phase 7: Documentation (docs/skills/vector-agent.md)

Follow patterns from:
- agents/d/ (D-gent structure)
- docs/skills/test-patterns.md

Success: 80+ tests, all integrations working, documented.
```
