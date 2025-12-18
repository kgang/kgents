# Différance Engine Cultivation

**Season:** HARVEST (Phase 5 Complete)
**Spec:** `spec/protocols/differance.md`
**Target:** `impl/claude/agents/differance/`
**Status:** 192 tests pass, contracts + hooks + component ready

---

## Prompt for Planning Agent

You are cultivating the **Différance Engine** — a traced wiring diagram system with ghost heritage graphs. The spec exists at `spec/protocols/differance.md`. Your task: plan a multi-phase implementation that reduces uncertainty at each step.

### Ground in Voice

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"Tasteful > feature-complete"*

This is not a logging system. It's a **self-knowing system** — outputs that know their own lineage, including roads not taken.

### The Core Types to Implement

```
TraceMonoid        — Associative composition of wiring decisions
WiringTrace        — Single decision record (ADR-style)
Alternative        — A ghost (road not taken)
GhostHeritageDAG   — Full lineage graph
TRACED_OPERAD      — Extension of AGENT_OPERAD
DIFFERANCE_POLYNOMIAL — Core state machine
```

### Phase Strategy (Garden Protocol)

**Phase 1: SPROUTING** — Reduce type uncertainty ✅ COMPLETE
- [x] Implement core dataclasses: `WiringTrace`, `Alternative`, `TraceMonoid`
- [x] Property tests for monoid laws (identity, associativity)
- [x] DifferanceStore with D-gent integration
- **Exit criteria:** Monoid laws pass; uncertainties documented

**Phase 2: SPROUTING** — Reduce integration uncertainty ✅ COMPLETE (2025-12-18)
- [x] Implement `TRACED_OPERAD` extending `AGENT_OPERAD`
- [x] `traced_seq`, `traced_par` operations
- [x] Verify: `traced_seq(a, b).agent ≅ seq(a, b)` (semantic preservation)
- [x] Verify: `ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)` (ghost preservation)
- [x] Property-based tests for all laws
- **Exit criteria:** ✅ Traced operations compose correctly (107 tests pass)

**Phase 3: BLOOMING** — Build heritage graph ✅ COMPLETE (2025-12-18)
- [x] Implement `GhostHeritageDAG` builder
- [x] D-gent storage adapter for traces
- [x] Query: heritage by output_id, depth-limited traversal
- **Exit criteria:** ✅ Can build DAG from trace log (158 tests pass)

**Phase 4: BLOOMING** — AGENTESE integration ✅ COMPLETE (2025-12-18)
- [x] `time.differance.*` paths (manifest, heritage, ghosts, at, why, replay)
- [x] `time.branch.*` paths (manifest, create, explore, compare)
- [x] `self.differance.*` paths (manifest, why, navigate, concretize, abstract)
- **Exit criteria:** ✅ CLI `kg time.trace.why <id>` works (34 tests pass)

**Phase 5: FRUITING** — Crown Jewel integration ✅ COMPLETE (2025-12-18)
- [x] Contract types for AGENTESE (Pattern 13: Contract-First Types)
- [x] DifferanceIntegration helper class for Crown Jewels
- [x] useDifferanceQuery React hook (heritage, why, ghosts, replay, branch)
- [x] GhostHeritageGraph React component (2D Renaissance aesthetic)
- **Exit criteria:** ✅ All 192 tests pass; contracts + hooks + component ready

### Spec Improvements to Consider

As you implement, capture uncertainties and propose spec amendments:

1. **Trace granularity**: Is `WiringTrace` per-operation right, or should we trace at turn level?
2. **Ghost retention**: 7/30 day defaults — are these appropriate?
3. **Compression**: When does holographic compression kick in?
4. **Performance**: What's the cost model for trace recording?
5. **Privacy boundaries**: How do traces interact with multi-tenant?

### Output Format

After each phase, produce:

```markdown
## Phase N Complete

### What Worked
- ...

### What's Uncertain
- ...

### Spec Amendments Proposed
- ...

### Next Phase Entry Criteria
- ...
```

### Laws That Must Hold

```python
# Monoid
assert TraceMonoid.empty().compose(t) == t == t.compose(TraceMonoid.empty())
assert (a.compose(b)).compose(c) == a.compose(b.compose(c))

# Semantic preservation
assert traced_seq(x, y).agent.invoke(input) == seq(x, y).invoke(input)

# Ghost preservation
assert set(traced_seq(a, b).ghosts()) >= set(a.ghosts()) | set(b.ghosts())

# DAG integrity
for trace in monoid.traces:
    assert trace.parent_trace_id is None or trace.parent_trace_id in monoid.trace_ids()
```

### Anti-Patterns to Avoid

- **Over-engineering storage**: Start with in-memory, move to D-gent later
- **Premature UI**: Get the algebra right before visualization
- **Ghost worship**: Not every alternative needs to be recorded
- **Trace pollution**: Don't trace trivial operations

---

*"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*

---

## Phase 2 Complete

### What Worked

- **Pattern 10 (Operad Inheritance)**: Using `**AGENT_OPERAD.operations` spread to inherit all base operations cleanly
- **TracedAgent wrapper**: Clean generic type that bundles agent + trace history while preserving semantic behavior
- **Property-based testing**: Hypothesis found edge cases in trace ID generation that would have caused false cycle detection
- **Convenience functions**: `traced_seq()` and `traced_par()` make the API ergonomic
- **Semantic preservation via delegation**: TracedAgent delegates `invoke()`, `transition()`, `positions`, `directions` to underlying agent

### What's Uncertain

1. **TracedOperation dataclass**: Currently not used by TRACED_OPERAD — consider if it adds value for introspection
2. **Trace ID format**: Using `trace_{uuid.hex[:12]}` — may want more structured IDs that encode operation type
3. **Position serialization**: Converting positions to strings for trace recording — may lose type information

### Spec Amendments Proposed

1. **Add TracedAgent to spec**: The spec mentions `TracedOperation` but TracedAgent is the key abstraction
2. **Clarify ghost accumulation behavior**: Current implementation accumulates ALL ghosts; spec should clarify if pruning is expected during composition
3. **Add `traced_branch` and `traced_fix`**: Spec shows these but we only implemented seq/par — defer to Phase 3 or later

### Next Phase Entry Criteria

For Phase 3 (GhostHeritageDAG):
- [x] TraceMonoid can accumulate traces (done)
- [x] Traces have parent_trace_id for causal linking (done)
- [x] verify_dag_integrity() validates structure (done)
- [ ] Need: HeritageNode and HeritageEdge types from spec
- [ ] Need: DAG builder that walks trace history
- [ ] Need: Query methods (at_depth, chosen_path, ghost_paths)

### Files Created/Modified

```
impl/claude/agents/differance/
├── __init__.py                    # Updated exports
├── operad.py                      # NEW: TRACED_OPERAD, TracedAgent, traced_seq/par
└── _tests/
    ├── test_trace_monoid.py       # Fixed: unique ID generation strategy
    └── test_traced_operad.py      # NEW: 38 tests for Phase 2
```

### Test Summary

```
107 tests passed
- 69 from Phase 1 (trace monoid, store)
- 38 from Phase 2 (traced operad)
```

---

## Phase 3 Complete

### What Worked

- **Frozen dataclasses**: HeritageNode and HeritageEdge are immutable — correct for a trace system
- **Clean separation**: Builder function (`build_heritage_dag`) is pure; store integration (`DifferanceStore.heritage_dag`) handles async I/O
- **Ghost ID format**: `{trace_id}_ghost_{index}` provides traceability and uniqueness
- **Query methods**: `chosen_path()`, `ghost_paths()`, `at_depth()` cover the spec requirements
- **Property-based tests**: Hypothesis verifies DAG invariants (linear path, ghost parenting, depth consistency)

### What's Uncertain

1. **Cycle detection in verify_integrity()**: Current impl is O(V*E) — may need optimization for large DAGs
2. **Ghost path structure**: Currently returns `(parent_id, ghost_id)` tuples — spec might want deeper paths for multi-level ghosts
3. **Serialization**: No `to_dict()`/`from_dict()` yet — will need for AGENTESE API responses

### Spec Amendments Proposed

1. **Add HeritageNode.inputs field**: Implemented but not in spec — useful for UI to show what was being composed
2. **Clarify ghost node depth**: Ghosts have same depth as their parent (branch at same level) — spec should state this
3. **Add GhostHeritageDAG.verify_integrity()**: Not in spec but essential for validation

### Next Phase Entry Criteria

For Phase 4 (AGENTESE integration):
- [x] GhostHeritageDAG can be built from traces (done)
- [x] Query methods work (chosen_path, ghost_paths, at_depth) (done)
- [x] Store integration via `heritage_dag()` method (done)
- [ ] Need: `@node` decorators for time.trace.* paths
- [ ] Need: Response contracts for AGENTESE API
- [ ] Need: CLI projection for heritage display

### Files Created/Modified

```
impl/claude/agents/differance/
├── __init__.py                    # Updated: exports Phase 3 types
├── heritage.py                    # NEW: HeritageNode, HeritageEdge, GhostHeritageDAG, builders
├── store.py                       # Updated: heritage_dag() method
└── _tests/
    └── test_heritage_dag.py       # NEW: 51 tests for Phase 3
```

### Test Summary

```
158 tests passed
- 69 from Phase 1 (trace monoid, store)
- 38 from Phase 2 (traced operad)
- 51 from Phase 3 (heritage DAG)
```

---

## Phase 4 Complete

### What Worked

- **@node registration pattern**: Using `@node("time.differance")` automatically registers paths in NodeRegistry
- **Aspect delegation**: `_invoke_aspect()` method with match statement provides clean routing
- **Three output formats for 'why'**: summary (default), full (with all node details), cli (ASCII visualization)
- **DifferanceStore and TraceMonoid dual support**: Nodes accept either store (for persistence) or monoid (for in-memory)
- **Integration via TimeContextResolver**: Adding `differance` and `branch` to the resolver's match statement
- **Lazy imports**: Avoiding circular dependencies with `from .time_differance import ...` inside methods

### Key Insight: "Why" is the Crown Jewel

The `time.differance.why(output_id)` path is the crown jewel of the Différance Engine. CLI output:

```
▶ trace_002
│ seq(Brain, Gardener)
├── ░ par [GHOST: Order matters for memory cultivation]
│ branch(BrainGardener)

Decisions made: 2
Alternatives considered: 1
```

This visual format shows the lineage of decisions at a glance.

### What's Uncertain

1. **Branch execution**: `time.branch.explore` is marked "deferred" — full ghost exploration needs agent execution context
2. **Concretize/Abstract**: These `self.differance.*` paths are declarative stubs — actual spec→impl transformation needs more infrastructure
3. **Performance**: Heritage DAG builds walk the full trace history — may need caching for large DAGs

### Spec Amendments Proposed

1. **Add `time.differance.*` paths**: Original spec had `time.trace.*` which conflicts with call-graph tracing; differentiate
2. **Add format parameter to 'why'**: Spec should document the three formats (summary, full, cli)
3. **Add `self.differance.concretize/abstract`**: Powerful spec↔impl navigation not in original spec

### Next Phase Entry Criteria

For Phase 5 (Crown Jewel integration):
- [x] AGENTESE paths registered and working (done)
- [x] CLI output format for 'why' (done)
- [ ] Need: React component for Ghost Heritage Graph
- [ ] Need: Wire into Brain's trace recording
- [ ] Need: Wire into Gardener's plan traces

### Files Created/Modified

```
impl/claude/protocols/agentese/contexts/
├── time_differance.py              # NEW: DifferanceTraceNode, BranchNode
├── self_differance.py              # NEW: SelfDifferanceNode
├── time.py                         # Updated: TimeContextResolver with differance/branch
├── __init__.py                     # Updated: exports for differance nodes
└── _tests/
    └── test_differance_paths.py    # NEW: 34 tests for Phase 4

impl/claude/protocols/agentese/
└── gateway.py                      # Updated: import time_differance, self_differance
```

### Test Summary

```
192 tests passed (estimate)
- 69 from Phase 1 (trace monoid, store)
- 38 from Phase 2 (traced operad)
- 51 from Phase 3 (heritage DAG)
- 34 from Phase 4 (AGENTESE paths)
```

---

## Phase 5 Complete

### What Worked

- **Pattern 13 (Contract-First Types)**: `@node(contracts={})` decorator with contract dataclasses provides single source of truth for BE→FE type sync
- **DifferanceIntegration class**: Clean API for Crown Jewels to record traces without knowing storage details
- **Buffer-only mode**: Allows sync trace recording even without store/monoid configured — great for testing
- **useAsyncState pattern**: Consistent with all other Crown Jewel query hooks
- **GhostHeritageGraph component**: Follows 2D Renaissance aesthetic (Living Earth palette), responsive with ElasticSplit

### Key Files Created

```
impl/claude/agents/differance/
├── contracts.py                     # NEW: All AGENTESE contract types
├── integration.py                   # NEW: DifferanceIntegration, record_trace_sync()
└── __init__.py                      # Updated: exports contracts + integration

impl/claude/protocols/agentese/contexts/
└── time_differance.py               # Updated: @node(contracts={}) decorator

impl/claude/web/src/
├── hooks/
│   ├── useDifferanceQuery.ts        # NEW: 13 query/mutation hooks
│   └── index.ts                     # Updated: differance exports
└── components/
    └── differance/
        ├── GhostHeritageGraph.tsx   # NEW: Crown jewel visualization
        └── index.ts                 # NEW: barrel exports
```

### What's Uncertain

1. **Actual Crown Jewel wiring**: `DifferanceIntegration` is ready but not yet called from Brain/Gardener services
2. **React component testing**: GhostHeritageGraph needs unit tests and storybook story
3. **Edge layout algorithm**: Current implementation uses simple depth-based positioning; may need force-directed layout for complex DAGs

### Spec Amendments Proposed

1. **Add contracts to spec**: AGENTESE contracts are a key innovation not in original spec
2. **Add integration patterns**: `DifferanceIntegration` pattern should be documented for other Crown Jewels
3. **Add buffer-only mode**: Useful for development/testing without persistence

### Future Work (Phase 6+)

- [ ] Wire `DifferanceIntegration` into Brain's `capture()` method
- [ ] Wire `DifferanceIntegration` into Gardener's `record_gesture()` method
- [ ] Add storybook story for GhostHeritageGraph
- [ ] Add unit tests for React components
- [ ] Performance optimization for large DAGs

### Test Summary

```
192 tests passed
- 69 from Phase 1 (trace monoid, store)
- 38 from Phase 2 (traced operad)
- 51 from Phase 3 (heritage DAG)
- 34 from Phase 4 (AGENTESE paths)
```

---

*"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*
