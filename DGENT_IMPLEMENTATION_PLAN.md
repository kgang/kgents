# D-gent Implementation Plan
# Generated: 2025-12-08
# Context: Implementing D-gents (Data Agents) in impl/claude/agents using bootstrap

---

## Executive Summary

This plan details the implementation of D-gents (Data Agents) based on the comprehensive specification in `spec/d-gents/`. The implementation will follow the established kgents patterns (spec-first, composable, bootstrap-based) and integrate seamlessly with existing agent genera.

**Target**: `impl/claude/agents/d/` package with 6 D-gent types + Symbiont pattern
**Foundation**: Uses `impl/claude/bootstrap` for composability
**Integration**: Works with T-gents (testing), J-gents (entropy), B-gents (state)

---

## Part 1: Strategic Analysis

### 1.1 Critical D-gent Types (Priority Order)

Based on the ecosystem analysis, implement in this order:

**Priority 1 - Foundation (Essential)**
1. **VolatileAgent** - In-memory state (simplest, most immediate utility)
   - Rationale: Fastest to implement, needed for testing all others
   - Use cases: Conversational context, test fixtures (T-gents integration)
   - Dependencies: None

2. **Symbiont** - Fuses pure logic with stateful memory
   - Rationale: Core pattern that makes D-gents useful
   - Use cases: All stateful agents (B-gents, K-gent, future agents)
   - Dependencies: VolatileAgent (for testing)

**Priority 2 - Persistence (High Value)**
3. **PersistentAgent** - File-backed state
   - Rationale: Enables durability, critical for K-gent persona
   - Use cases: User profiles, agent knowledge bases, session continuity
   - Dependencies: VolatileAgent (composition pattern)

4. **LensAgent** - Focused state views
   - Rationale: Enables safe multi-agent coordination
   - Use cases: Shared state (multiple agents), access control
   - Dependencies: Any DataAgent (wraps existing D-gents)

**Priority 3 - Advanced (Future)**
5. **VectorAgent** - Semantic memory
   - Rationale: RAG integration, semantic search
   - Use cases: B-gents hypothesis retrieval, knowledge graphs
   - Dependencies: External (FAISS, embeddings)

6. **StreamAgent** - Event sourcing
   - Rationale: Audit trails, time-travel debugging
   - Use cases: T-gents history, J-gents promise tree replay
   - Dependencies: VolatileAgent or PersistentAgent (event store)

### 1.2 Bootstrap Integration Patterns

**Pattern 1: D-gents ARE NOT Bootstrap Agents**
- D-gents implement `DataAgent[S]` protocol, NOT `Agent[A, B]`
- Rationale: State management is orthogonal to transformation
- Bootstrap agents can *use* D-gents internally

**Pattern 2: Symbiont Wraps Bootstrap Agents**
```python
# Symbiont[I, O, S] implements Agent[I, O]
# Internally composes:
#   - Pure logic: (I, S) → (O, S)  [can be a bootstrap agent!]
#   - Memory: DataAgent[S]

symbiont = Symbiont(
    logic=lambda i, s: (transform(i, s), new_state(s)),
    memory=VolatileAgent(initial_state)
)
# symbiont is now a valid bootstrap Agent[I, O]
```

**Pattern 3: Fix + D-gents (Persistent Iteration)**
```python
# Fix iterates a function until convergence
# D-gent persists state AFTER Fix completes, not during

# WRONG: D-gent persists every iteration
fix_agent = Fix(
    func=lambda x: Symbiont(logic, dgent).invoke(x),  # ❌ Persists N times
    config=FixConfig(max_iterations=10)
)

# RIGHT: Persist after convergence
fix_agent = Fix(
    func=lambda x: pure_logic(x, volatile_state),  # ✅ Pure iterations
    config=FixConfig(max_iterations=10)
)
final_result = fix_agent.invoke(input)
await persistent_dgent.save(final_result)  # Persist once at end
```

### 1.3 Architectural Decisions

**Decision 1: Async-First Design**
- All D-gent methods are `async` (load, save, history)
- Rationale: I/O is inherently async, composition with other agents requires it
- Trade-off: More complex testing, but matches ecosystem (LLMAgent is async)
- **Recommendation**: Use `async/await` throughout

**Decision 2: Pure Logic in Symbiont**
- Symbiont logic function can be sync or async
- Rationale: Logic purity is about (input, state) → (output, new_state) determinism
- Implementation:
  ```python
  # Detect if logic is async and adapt
  if asyncio.iscoroutinefunction(self.logic):
      output, new_state = await self.logic(input_data, current_state)
  else:
      output, new_state = self.logic(input_data, current_state)
  ```
- **Recommendation**: Support both, prefer sync for testability

**Decision 3: Error Handling Strategy**
- Use `runtime.base.Result[T]` (Success/Error) for D-gent operations
- Rationale: Matches existing kgents error handling (Issue #6)
- State errors:
  - `StateNotFoundError` → retry with default initialization
  - `StateCorruptionError` → log + fallback to safe state
  - `StateSerializationError` → permanent failure (fix schema)
- **Recommendation**: Wrap load/save in try/except, return Result types

**Decision 4: Lens Law Enforcement**
- Lenses are tested with T-gents PropertyAgent
- Three laws: GetPut, PutGet, PutPut (see spec/d-gents/lenses.md)
- Implementation: Provide `verify_lens_laws()` test helper
- **Recommendation**: Lenses are correctness-critical, property test all of them

---

## Part 2: Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Deliverable 1.1: DataAgent Protocol**
- File: `impl/claude/agents/d/protocol.py`
- Content:
  ```python
  from typing import TypeVar, Protocol, List
  from abc import abstractmethod

  S = TypeVar("S")

  class DataAgent(Protocol[S]):
      @abstractmethod
      async def load(self) -> S: ...

      @abstractmethod
      async def save(self, state: S) -> None: ...

      @abstractmethod
      async def history(self, limit: int | None = None) -> List[S]: ...
  ```
- Tests: Protocol compliance checker (T-gent)

**Deliverable 1.2: VolatileAgent**
- File: `impl/claude/agents/d/volatile.py`
- Implementation: In-memory state with bounded history
- Key features:
  - `copy.deepcopy` for isolation (prevent reference sharing)
  - Configurable `max_history` (entropy-aware)
  - O(1) load, O(1) save (just memory operations)
- Tests:
  - Round-trip integrity (save → load preserves state)
  - Isolation (mutations don't affect loaded copies)
  - History ordering (newest first)

**Deliverable 1.3: Symbiont Pattern**
- File: `impl/claude/agents/d/symbiont.py`
- Implementation: Fuses `logic: (I, S) → (O, S)` with `memory: DataAgent[S]`
- Key features:
  - Implements `Agent[I, O]` (composable with bootstrap)
  - Detects sync vs async logic functions
  - State threading: load → compute → save → return
- Tests:
  - Pure logic testability (unit test logic without I/O)
  - State persistence (memory survives invocations)
  - Composition (symbiont >> symbiont chains correctly)

**Deliverable 1.4: Package Structure**
```
impl/claude/agents/d/
├── __init__.py          # Public API exports
├── protocol.py          # DataAgent protocol
├── volatile.py          # VolatileAgent
├── symbiont.py          # Symbiont pattern
├── errors.py            # State* exceptions
└── _tests/
    ├── test_protocol.py
    ├── test_volatile.py
    └── test_symbiont.py
```

**Success Criteria Phase 1:**
- ✅ All tests pass (pytest)
- ✅ T-gents integration (SpyAgent records state changes)
- ✅ Example: Conversational chatbot with VolatileAgent + Symbiont

---

### Phase 2: Persistence (Week 2)

**Deliverable 2.1: PersistentAgent**
- File: `impl/claude/agents/d/persistent.py`
- Implementation: File-backed state with atomic writes
- Key features:
  - JSON serialization (dataclasses + primitives)
  - Atomic writes (temp file + rename)
  - JSONL history (append-only)
  - Crash recovery (survives process restart)
- Tests:
  - Round-trip with dataclasses
  - Concurrent writes (file locking?)
  - Crash recovery (delete object, recreate, load succeeds)

**Deliverable 2.2: Lens Infrastructure**
- File: `impl/claude/agents/d/lens.py`
- Implementation: Lens[S, A] with get/set + composition
- Key features:
  - Lens laws verification (T-gent PropertyAgent)
  - Composability (`lens1 >> lens2`)
  - Helpers: `key_lens()`, `field_lens()`, `index_lens()`
- Tests:
  - Three laws (GetPut, PutGet, PutPut) - property-based
  - Composition (nested state access)
  - Type safety (mypy checks)

**Deliverable 2.3: LensAgent**
- File: `impl/claude/agents/d/lens_agent.py`
- Implementation: D-gent that wraps parent + lens
- Key features:
  - Delegates to parent for persistence
  - Projects state through lens
  - Composable (lenses compose, agents compose)
- Tests:
  - Focused access (agent sees only sub-state)
  - Multi-agent coordination (shared parent, different lenses)
  - Lens law preservation (agent operations respect laws)

**Deliverable 2.4: Integration Examples**
- File: `examples/d-gents/` (new directory)
- Examples:
  1. `chatbot_memory.py` - Persistent conversation history
  2. `multi_agent_blackboard.py` - Shared state via lenses
  3. `k_gent_persona.py` - K-gent personality storage

**Success Criteria Phase 2:**
- ✅ PersistentAgent survives restart (integration test)
- ✅ Lenses pass all property tests (lens laws verified)
- ✅ K-gent uses PersistentAgent for personality continuity

---

### Phase 3: Advanced Types (Week 3)

**Deliverable 3.1: CachedAgent (Composition Pattern)**
- File: `impl/claude/agents/d/cached.py`
- Implementation: Volatile cache + Persistent backend
- Pattern: Layered D-gents
  ```python
  cached = CachedAgent(
      cache=VolatileAgent(initial),
      backend=PersistentAgent(path, schema)
  )
  # Reads from cache, writes to both
  ```
- Tests:
  - Cache hit performance (< 1ms)
  - Write-through (both updated)
  - Cache miss fallback (loads from backend)

**Deliverable 3.2: VectorAgent (Optional - Future)**
- File: `impl/claude/agents/d/vector.py`
- Implementation: FAISS-backed semantic search
- Depends: `faiss-cpu`, embedding model
- Use case: B-gents hypothesis retrieval
- **Defer if time-constrained** (not blocking for other agents)

**Deliverable 3.3: StreamAgent (Optional - Future)**
- File: `impl/claude/agents/d/stream.py`
- Implementation: Event sourcing pattern
- Use case: J-gents promise tree replay, audit logs
- **Defer if time-constrained** (complex, fewer immediate use cases)

**Deliverable 3.4: Documentation**
- File: `impl/claude/agents/d/README.md`
- Content:
  - Quick start guide
  - D-gent type comparison table
  - Integration patterns (with Bootstrap, T-gents, J-gents)
  - Common pitfalls and anti-patterns

**Success Criteria Phase 3:**
- ✅ CachedAgent demonstrates composition pattern
- ✅ Documentation is clear and complete
- ✅ All examples run without errors

---

### Phase 4: Ecosystem Integration (Week 4)

**Deliverable 4.1: T-gents Integration**
- Update: `impl/claude/agents/t/spy.py`
- Enhancement: SpyAgent as a D-gent (records to VolatileAgent)
  ```python
  class SpyAgent:
      def __init__(self, label: str):
          self.memory = VolatileAgent[List[Any]](initial=[])

      async def invoke(self, input):
          history = await self.memory.load()
          history.append(input)
          await self.memory.save(history)
          return input  # Identity with side effect
  ```
- Benefit: SpyAgent history is queryable via D-gent interface

**Deliverable 4.2: J-gents Integration**
- Update: `impl/claude/agents/j/` (entropy budgets)
- Enhancement: Add `EntropyConstrainedAgent` wrapper
  ```python
  dgent = EntropyConstrainedAgent(
      backend=PersistentAgent(...),
      budget=0.5,  # At depth 2 in promise tree
      max_size_bytes=500_000
  )
  # Raises StateError if state exceeds budget
  ```
- Benefit: J-gents can enforce state size limits

**Deliverable 4.3: B-gents Integration**
- Update: `impl/claude/agents/b/robin.py`
- Enhancement: Robin uses D-gent for hypothesis history
  ```python
  class RobinAgent:
      def __init__(self, ...):
          self.hypothesis_memory = PersistentAgent[List[Hypothesis]](
              path="robin_hypotheses.json",
              schema=List[Hypothesis]
          )
  ```
- Benefit: Robin remembers past hypotheses across sessions

**Deliverable 4.4: Bootstrap Integration Example**
- File: `examples/d-gents/bootstrap_stateful.py`
- Example: Stateful Fix with D-gent persistence
  ```python
  # Iterate with Fix, persist result with D-gent
  def refine(code: str, state: RefinementState) -> tuple[str, RefinementState]:
      # Pure logic
      improved = improve_code(code)
      new_state = state.with_iteration(state.iteration + 1)
      return improved, new_state

  # Volatile during Fix iterations
  volatile_state = VolatileAgent(RefinementState(iteration=0))
  fix_agent = Fix(...)

  # Persist final result
  final = fix_agent.invoke(initial_code)
  await persistent_dgent.save(final)
  ```

**Success Criteria Phase 4:**
- ✅ SpyAgent refactored to use D-gent
- ✅ J-gents entropy enforcement works
- ✅ Robin demonstrates persistent memory
- ✅ Bootstrap + D-gent example is clear

---

## Part 3: Testing Strategy

### 3.1 Unit Tests (Per D-gent Type)

**Test Categories:**
1. **Protocol Compliance**
   - All D-gents implement DataAgent[S]
   - load() returns correct type
   - save() persists correctly
   - history() orders newest-first

2. **Isomorphism (Round-Trip)**
   ```python
   async def test_round_trip(dgent, sample_state):
       await dgent.save(sample_state)
       loaded = await dgent.load()
       assert loaded == sample_state
   ```

3. **Isolation**
   ```python
   async def test_isolation(dgent):
       await dgent.save({"value": 1})
       state1 = await dgent.load()
       state1["value"] = 2  # Mutate
       state2 = await dgent.load()
       assert state2["value"] == 1  # Not affected
   ```

4. **History Semantics**
   ```python
   async def test_history_ordering(dgent):
       await dgent.save(1)
       await dgent.save(2)
       await dgent.save(3)
       history = await dgent.history(limit=3)
       assert history == [2, 1]  # Newest first, current excluded
   ```

### 3.2 Integration Tests (Cross-Genus)

**Test 1: D-gent + T-gent (SpyAgent)**
```python
async def test_spy_with_dgent():
    spy = SpyAgent(label="test")
    pipeline = Generator() >> spy >> Validator()
    await pipeline.invoke(input)

    # Query spy's memory
    history = await spy.memory.history()
    assert len(history) > 0
```

**Test 2: D-gent + Symbiont + Bootstrap**
```python
async def test_symbiont_composition():
    dgent = VolatileAgent(ConversationState())
    logic = lambda inp, state: (transform(inp), update(state))
    symbiont = Symbiont(logic, dgent)

    # Symbiont is an Agent - compose with ID
    pipeline = ID >> symbiont >> ID
    result = await pipeline.invoke("Hello")
    assert result is not None
```

**Test 3: D-gent + J-gent (Entropy)**
```python
async def test_entropy_constraint():
    dgent = EntropyConstrainedAgent(
        backend=VolatileAgent({}),
        budget=0.1,  # Very small
        max_size_bytes=100
    )

    large_state = {"data": "x" * 1000}
    with pytest.raises(StateError, match="too large"):
        await dgent.save(large_state)
```

### 3.3 Property-Based Tests (Lens Laws)

Using T-gent PropertyAgent:

```python
from agents.t import PropertyAgent

def test_lens_laws():
    lens = key_lens("user")

    # Property 1: GetPut
    def get_put_law(state: dict) -> bool:
        return lens.set(state, lens.get(state)) == state

    # Property 2: PutGet
    def put_get_law(state: dict, value: Any) -> bool:
        return lens.get(lens.set(state, value)) == value

    # Property 3: PutPut
    def put_put_law(state: dict, a: Any, b: Any) -> bool:
        return lens.set(lens.set(state, a), b) == lens.set(state, b)

    # Run property tests
    agent = PropertyAgent(property=get_put_law, ...)
    result = agent.test()
    assert result.passed
```

---

## Part 4: File Structure

### Final Package Layout

```
impl/claude/agents/d/
├── __init__.py                 # Public API
├── protocol.py                 # DataAgent[S] protocol
├── errors.py                   # StateError hierarchy
│
├── volatile.py                 # VolatileAgent (in-memory)
├── persistent.py               # PersistentAgent (file-backed)
├── symbiont.py                 # Symbiont pattern
│
├── lens.py                     # Lens[S, A] infrastructure
├── lens_agent.py               # LensAgent (focused views)
│
├── cached.py                   # CachedAgent (composition)
├── entropy.py                  # EntropyConstrainedAgent (J-gents)
│
├── vector.py                   # VectorAgent (optional/future)
├── stream.py                   # StreamAgent (optional/future)
│
├── helpers.py                  # Lens factories, test utilities
├── README.md                   # Usage guide
│
└── _tests/
    ├── test_protocol.py
    ├── test_volatile.py
    ├── test_persistent.py
    ├── test_symbiont.py
    ├── test_lens.py
    ├── test_lens_agent.py
    ├── test_cached.py
    ├── test_entropy.py
    └── test_integration.py     # Cross-genus tests
```

**Total Estimated LOC**: ~2,500-3,000 lines
- Core D-gents: ~1,200 lines
- Symbiont + Lens: ~600 lines
- Tests: ~1,000 lines
- Examples + Docs: ~500 lines

---

## Part 5: Success Metrics

### 5.1 Completeness

- [ ] All 6 D-gent types specified in spec implemented (or deferred with rationale)
- [ ] DataAgent protocol fully specified
- [ ] Symbiont pattern working with sync and async logic
- [ ] Lens laws verified with property tests

### 5.2 Integration

- [ ] SpyAgent (T-gent) refactored to use D-gent
- [ ] J-gents can use EntropyConstrainedAgent
- [ ] B-gents Robin uses PersistentAgent for memory
- [ ] K-gent can persist personality via D-gent

### 5.3 Quality

- [ ] Test coverage > 90% (pytest --cov)
- [ ] All lens laws pass property tests
- [ ] No mypy errors (type safety)
- [ ] Documentation complete (README + examples)

### 5.4 Performance

- [ ] VolatileAgent: load < 1μs, save < 1μs
- [ ] PersistentAgent: load < 10ms, save < 10ms (small state)
- [ ] CachedAgent: cache hit < 1ms, cache miss < 20ms
- [ ] No memory leaks (history bounded, deepcopy used correctly)

---

## Part 6: Risks and Mitigations

### Risk 1: Async Complexity
- **Risk**: async/await adds testing complexity
- **Mitigation**: Use `pytest-asyncio`, provide sync wrappers for testing
- **Fallback**: Implement sync versions first, add async later

### Risk 2: Lens Law Violations
- **Risk**: Hand-written lenses may violate laws
- **Mitigation**: Property-based testing catches violations early
- **Fallback**: Provide only verified lens factories, not raw Lens constructor

### Risk 3: State Serialization Edge Cases
- **Risk**: Complex types (functions, closures) can't serialize
- **Mitigation**: Document supported types, validate in save()
- **Fallback**: Provide custom serializers for common patterns

### Risk 4: Performance Degradation
- **Risk**: deepcopy on every load() may be slow for large state
- **Mitigation**: Benchmark and optimize (structural sharing, copy-on-write)
- **Fallback**: Add `zero_copy=True` flag with safety warnings

### Risk 5: Scope Creep
- **Risk**: Implementing VectorAgent, StreamAgent adds weeks
- **Mitigation**: Phase 3 is explicitly optional, defer if needed
- **Fallback**: Ship core D-gents (Volatile, Persistent, Symbiont, Lens) first

---

## Part 7: Timeline

### Week 1: Foundation
- Days 1-2: Protocol + VolatileAgent + tests
- Days 3-4: Symbiont pattern + tests
- Day 5: Integration examples, buffer time

### Week 2: Persistence
- Days 1-2: PersistentAgent + tests
- Days 3-4: Lens + LensAgent + property tests
- Day 5: Integration with K-gent, examples

### Week 3: Advanced & Polish
- Days 1-2: CachedAgent + EntropyConstrainedAgent
- Days 3-4: Documentation, examples, README
- Day 5: Code review, refactoring

### Week 4: Integration & Testing
- Days 1-2: T-gents integration (SpyAgent)
- Days 3-4: J-gents, B-gents integration
- Day 5: Final testing, benchmarking, release

**Total**: 4 weeks to full D-gent ecosystem

---

## Part 8: Next Steps

### Immediate Actions
1. Create `impl/claude/agents/d/` directory
2. Copy protocol.py from spec (adapt to Python)
3. Implement VolatileAgent (simplest first)
4. Write tests using pytest-asyncio
5. Implement Symbiont pattern

### Review Checkpoints
- End of Week 1: Protocol + Volatile + Symbiont working
- End of Week 2: Persistent + Lens working
- End of Week 3: Advanced types + docs complete
- End of Week 4: Full integration validated

### Documentation Updates
- Update `HYDRATE.md` with D-gent implementation progress
- Add `impl/claude/agents/d/README.md` with usage guide
- Create `examples/d-gents/` with 3-5 examples
- Update main `README.md` to mention D-gents

---

## Part 9: Open Questions

### Question 1: Transactional D-gents?
- Should we implement `TransactionalDataAgent` protocol?
- Use case: Multi-step state updates that must be atomic
- Decision: Defer to Phase 3+ (advanced feature)

### Question 2: Observable D-gents?
- Should we implement observer pattern for state changes?
- Use case: Reactive agents that respond to state changes
- Decision: Defer to Phase 3+ (complex, fewer use cases)

### Question 3: Schema Migration?
- How to handle state schema evolution?
- Use case: Update dataclass shape, old state files exist
- Decision: Document manual migration pattern, defer auto-migration

### Question 4: Concurrency Safety?
- File locking for PersistentAgent?
- Use case: Multiple processes writing to same file
- Decision: Document single-writer assumption, add locking in Phase 3+

---

## Conclusion

This plan provides a complete roadmap for implementing D-gents in `impl/claude/agents/d/` following the kgents philosophy:

✅ **Specification-First**: Implements `spec/d-gents/` faithfully
✅ **Composable**: D-gents compose with Bootstrap agents via Symbiont
✅ **Tasteful**: Focus on essential types (Volatile, Persistent, Lens, Symbiont)
✅ **Curated**: Each D-gent type has clear, non-overlapping purpose
✅ **Ethical**: Transparent state management, inspectable, rollback-capable
✅ **Joyful**: Endosymbiosis metaphor, elegant lens laws
✅ **Generative**: Can regenerate from specs + bootstrap

**Estimated Effort**: 4 weeks full-time (120-160 hours)
**Risk Level**: Medium (async complexity, lens laws)
**Impact**: High (enables stateful agents across all genera)

---

**Next Session**: Start with Phase 1, Deliverable 1.1 (DataAgent protocol)
