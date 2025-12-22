# K-Block Implementation Plan

> *"The K-Block is not where you edit a document. It's where you edit a possible world."*

**Spec**: `spec/protocols/k-block.md`
**Date**: 2025-12-22
**Estimated Complexity**: High (novel architecture, integrates with 4 existing systems)
**Dependencies**: FILE_OPERAD (implemented), Witness (implemented), DataBus (implemented), Interactive Text (planned)

---

## Overview

K-Block introduces **transactional hyperdimensional editing** — isolated editing universes with multiple coherent views that commit to an append-only cosmos. This plan outlines a phased implementation that builds the foundation first, then adds advanced capabilities.

### Key Innovations

1. **Monadic Isolation**: K-Block wraps FILE_OPERAD operations, preventing cosmic side effects until explicit commit
2. **Append-Only Cosmos**: Never overwrite — every save appends, enabling perfect time travel
3. **Hyperdimensional Views**: Prose/Graph/Code views sync bidirectionally within K-Block
4. **Witnessed Operations**: Every edit is traced, enabling replay and audit
5. **Entanglement**: Link K-Blocks for synchronized editing without breaking isolation
6. **Generative K-Blocks**: Specs can generate derived K-Blocks (types, tests, API stubs)

---

## Phase 0: Foundation (Sessions 1-2)

**Goal**: Core K-Block data structures, basic harness operations

### Session 1: Core Types

**Module**: `impl/claude/services/k_block/core/`

| File | Purpose |
|------|---------|
| `kblock.py` | `KBlock` dataclass with content, base, views, isolation state |
| `cosmos.py` | `Cosmos` with append-only log skeleton (in-memory first) |
| `harness.py` | `HARNESS_OPERAD` with create/save/discard |
| `polynomial.py` | `KBlockPolynomial` state machine |

**Deliverables**:
- [ ] `KBlock` dataclass with `id`, `path`, `content`, `base_content`, `isolation`
- [ ] `IsolationState` enum: PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED
- [ ] `Cosmos` with in-memory append log
- [ ] `FileOperadHarness` with `create()`, `save()`, `discard()`
- [ ] Basic tests for harness operations

**Verification**:
```python
# create_discard_identity law
block = await harness.create("test.md")
await harness.discard(block)
# Cosmos unchanged
```

### Session 2: Monad Laws + Polynomial

**Focus**: Verify monad laws, implement polynomial state machine

**Deliverables**:
- [ ] `bind` operation for K-Block monad
- [ ] Tests for left identity, right identity, associativity
- [ ] `KBlockPolynomial.directions()` for valid transitions
- [ ] State transition tests

**Verification**:
```python
# All three monad laws pass
def test_left_identity(): ...
def test_right_identity(): ...
def test_associativity(): ...
```

---

## Phase 1: Views + Sheaf (Sessions 3-5)

**Goal**: Hyperdimensional rendering with sheaf coherence

### Session 3: View Infrastructure

**Module**: `impl/claude/services/k_block/views/`

| File | Purpose |
|------|---------|
| `base.py` | `View` protocol, `ViewType` enum |
| `prose.py` | Markdown prose view |
| `registry.py` | View registry per K-Block |

**Deliverables**:
- [ ] `View` protocol with `render()`, `apply_delta()`, `tokens()`
- [ ] `ProseView` implementation (basic markdown rendering)
- [ ] `KBlock.views` dict management
- [ ] Single-view rendering tests

### Session 4: Graph + Code Views

**Deliverables**:
- [ ] `GraphView` — AST to DAG transformation
- [ ] `CodeView` — Type extraction to Python dataclasses
- [ ] View-specific delta types (`TextDelta`, `GraphDelta`, `CodeDelta`)
- [ ] Per-view rendering tests

### Session 5: Sheaf Gluing

**Module**: `impl/claude/services/k_block/core/sheaf.py`

**Deliverables**:
- [ ] `KBlockSheaf` with `compatible()`, `glue()`, `propagate()`
- [ ] `ViewSync` bidirectional synchronization
- [ ] Edit-in-one-view → all-views-update propagation
- [ ] Sheaf coherence tests

**Verification**:
```python
def test_view_coherence():
    block = await harness.create("spec.md")
    block.content = "# Type\n- field: string"

    # Edit in prose
    block.views["prose"].edit(delta)

    # Graph and code views reflect change
    assert "field" in block.views["graph"].nodes
    assert "field" in block.views["code"].fields
```

---

## Phase 2: Cosmos Persistence (Sessions 6-7)

**Goal**: Append-only log with persistence and time travel

### Session 6: Append-Only Log

**Module**: `impl/claude/services/k_block/persistence/`

| File | Purpose |
|------|---------|
| `log.py` | `AppendOnlyLog` with JSON persistence |
| `index.py` | `SemanticIndex` for path → version lookup |

**Deliverables**:
- [ ] `AppendOnlyLog.append()`, `get()`, `walk_back()`
- [ ] JSON serialization to `~/.kgents/cosmos/`
- [ ] `SemanticIndex` for efficient path lookup
- [ ] Persistence tests (write, reload, verify)

### Session 7: Time Travel

**Deliverables**:
- [ ] `Cosmos.history(path)` — all versions of a path
- [ ] `Cosmos.travel(version)` — view cosmos at historical state
- [ ] `Cosmos.diff(v1, v2)` — delta between versions
- [ ] CLI: `kg cosmos history <path>`, `kg cosmos travel <version>`
- [ ] Time travel tests

**Verification**:
```python
def test_time_travel():
    # Create and edit
    block = await harness.create("test.md")
    block.content = "v1"
    v1 = await harness.save(block)

    block.content = "v2"
    v2 = await harness.save(block)

    # Travel back
    old_cosmos = await cosmos.travel(v1)
    assert await old_cosmos.read("test.md") == "v1"

    # Current cosmos still at v2
    assert await cosmos.read("test.md") == "v2"
```

---

## Phase 3: Witness Integration (Sessions 8-9)

**Goal**: Every K-Block operation witnessed and replayable

### Session 8: Operation Witnessing

**Module**: `impl/claude/services/k_block/witness/`

| File | Purpose |
|------|---------|
| `trace.py` | `KBlockWitness` integration |
| `marks.py` | Mark types for K-Block operations |

**Deliverables**:
- [ ] `WitnessedKBlock` wrapper
- [ ] Mark on: create, edit, save, discard, checkpoint
- [ ] Reasoning capture for saves
- [ ] Witness query: `kg witness show --kblock <id>`

### Session 9: Session Replay

**Module**: `impl/claude/services/k_block/witness/replay.py`

**Deliverables**:
- [ ] `replay_session(block_id, from_witness)` — reconstruct state
- [ ] CLI: `kg kblock replay <block_id>`
- [ ] Replay verification tests

**Verification**:
```python
def test_replay():
    # Edit session
    block = await harness.create("test.md")
    block.content = "edit1"
    block.content = "edit2"
    block.content = "edit3"
    first_mark = block.witness_marks[0]

    # Replay from first mark
    replayed = await replay_session(block.id, first_mark)
    assert replayed.content == "edit3"
```

---

## Phase 4: Checkpoints + Fork/Merge (Sessions 10-12)

**Goal**: Temporal operations and parallel universes

### Session 10: Checkpoints

**Deliverables**:
- [ ] `harness.checkpoint(block, name)` — create named restore point
- [ ] `harness.rewind(block, checkpoint_id)` — restore to checkpoint
- [ ] Checkpoint stored in K-Block state (not cosmos)
- [ ] CLI: `kg kblock checkpoint <name>`, `kg kblock rewind <name>`
- [ ] Checkpoint tests

### Session 11: Fork

**Deliverables**:
- [ ] `harness.fork(block)` → `(KBlock, KBlock)`
- [ ] Both K-Blocks have same base, independent content
- [ ] Fork law: `merge(fork(kb)) ≡ kb`
- [ ] CLI: `kg kblock fork`

### Session 12: Merge

**Deliverables**:
- [ ] `harness.merge(kb1, kb2)` → `KBlock`
- [ ] Three-way merge using base
- [ ] Conflict detection → `IsolationState.CONFLICTING`
- [ ] Conflict markers in content
- [ ] CLI: `kg kblock merge <id1> <id2>`
- [ ] Merge tests (clean merge, conflict)

---

## Phase 5: Entanglement (Sessions 13-15)

**Goal**: Linked K-Blocks for synchronized editing

### Session 13: Entanglement Core

**Module**: `impl/claude/services/k_block/entanglement/`

**Deliverables**:
- [ ] `EntangledPair` dataclass
- [ ] `SyncRule` for defining propagation patterns
- [ ] `harness.entangle(kb1, kb2, rules)` → `EntangledPair`
- [ ] Basic entanglement tests

### Session 14: Change Propagation

**Deliverables**:
- [ ] `propagate_if_matches(delta, target, rules)`
- [ ] Bidirectional watchers setup
- [ ] Transform functions for rule-based propagation
- [ ] Propagation tests

### Session 15: Disentanglement + Save

**Deliverables**:
- [ ] `harness.disentangle(pair)` → `(KBlock, KBlock)`
- [ ] Atomic save of entangled pair (both or neither)
- [ ] CLI: `kg kblock entangle <id1> <id2>`, `kg kblock disentangle`
- [ ] Entanglement symmetry law tests

---

## Phase 6: Generators (Sessions 16-18)

**Goal**: Specs generate derived K-Blocks

### Session 16: Generator Framework

**Module**: `impl/claude/services/k_block/generators/`

**Deliverables**:
- [ ] `Generator` protocol
- [ ] `GenerativeKBlock` subclass
- [ ] `should_run()` pattern matching
- [ ] Generator registration

### Session 17: Built-in Generators

**Deliverables**:
- [ ] `TypeGen` — `## Types` section → Python dataclasses
- [ ] `TestGen` — `## Verification` section → pytest stubs
- [ ] Generator tests

### Session 18: Generator UX

**Deliverables**:
- [ ] Generated K-Blocks shown after spec save
- [ ] Review/Save/Discard workflow
- [ ] CLI: `kg kblock generate <id>`, `kg kblock generators`
- [ ] Integration tests

---

## Phase 7: Web UI (Sessions 19-22)

**Goal**: Full K-Block editing experience in web UI

### Session 19: Editor Component

**Module**: `impl/claude/web/src/components/kblock/`

**Deliverables**:
- [ ] `KBlockEditor.tsx` — main editing surface
- [ ] `useKBlock.ts` — state management hook
- [ ] Basic prose editing with isolation indicator

### Session 20: View Tabs

**Deliverables**:
- [ ] `ViewTabs.tsx` — tab bar for view switching
- [ ] `ProseView.tsx`, `GraphView.tsx`, `CodeView.tsx` components
- [ ] View state synchronization via hook

### Session 21: Isolation + Actions

**Deliverables**:
- [ ] `IsolationIndicator.tsx` — badge showing K-Block state
- [ ] `HarnessActions.tsx` — Save/Discard/Fork/Merge buttons
- [ ] Staleness warning banner
- [ ] Conflict resolution UI

### Session 22: Entanglement UI

**Deliverables**:
- [ ] `EntanglementPanel.tsx` — show linked K-Blocks
- [ ] Split view for entangled editing
- [ ] Entangle/disentangle buttons
- [ ] E2E tests

---

## Phase 8: AGENTESE Integration (Session 23)

**Goal**: Full AGENTESE exposure under `self.kblock.*`

**Deliverables**:
- [ ] `KBlockNode` registered at `self.kblock`
- [ ] All aspects: create, save, discard, fork, merge, checkpoint, rewind, entangle, manifest, history
- [ ] Dependency injection setup
- [ ] AGENTESE invocation tests

---

## Phase 9: Polish + Documentation (Sessions 24-25)

### Session 24: Performance + Edge Cases

**Deliverables**:
- [ ] Large document performance (>10K lines)
- [ ] Many checkpoints performance
- [ ] Deep cosmos history performance
- [ ] Error handling for all edge cases

### Session 25: Documentation

**Deliverables**:
- [ ] Skills doc: `docs/skills/k-block-patterns.md`
- [ ] Update CLAUDE.md with K-Block section
- [ ] Update `docs/systems-reference.md`
- [ ] Spec refinements based on implementation learnings

---

## Test Strategy

### Law Verification (T-gent Type III)

```python
# Monad laws
test_left_identity()
test_right_identity()
test_associativity()

# Harness laws
test_create_discard_identity()
test_save_idempotence()
test_fork_merge_identity()
test_checkpoint_rewind_identity()
test_entangle_symmetry()
```

### Property-Based Testing (T-gent Type IV)

```python
@given(st.text(), st.lists(st.text()))
def test_arbitrary_edits_maintain_coherence(initial, edits):
    block = harness.create_sync("test.md", initial)
    for edit in edits:
        block.content = edit
    # Views always coherent
    assert block.sheaf.verify_coherence()
```

### Integration Testing

```python
def test_full_workflow():
    # Create
    block = await harness.create("spec.md")

    # Edit with checkpoints
    block.content = "v1"
    cp1 = await harness.checkpoint(block, "v1")
    block.content = "v2"

    # Fork
    left, right = await harness.fork(block)
    left.content = "left"
    right.content = "right"

    # Merge
    merged = await harness.merge(left, right)

    # Save
    result = await harness.save(merged)

    # Verify cosmos
    assert await cosmos.read("spec.md") == merged.content
```

---

## Risk Mitigation

### Risk: View Sync Complexity

**Mitigation**: Start with prose-only (Session 3), add views incrementally. Each view has its own delta type, reducing coupling.

### Risk: Merge Conflicts

**Mitigation**: Use proven three-way merge algorithm. Conflict markers follow Git convention (familiar to users). AI-assisted merge is future enhancement.

### Risk: Performance at Scale

**Mitigation**: Lazy view rendering (don't compute all views until needed). Append-only log with indices (not full scan). Checkpoint pruning strategy.

### Risk: Entanglement Complexity

**Mitigation**: Defer entanglement to Phase 5. Core K-Block value (isolation) works without it. Entanglement is enhancement, not requirement.

---

## Success Criteria

### Phase 0-2 (MVP)

- [ ] K-Block create/edit/save/discard works
- [ ] Prose view renders correctly
- [ ] Monad laws verified
- [ ] Basic persistence to cosmos

### Phase 3-4 (Core)

- [ ] All operations witnessed
- [ ] Checkpoints and rewind work
- [ ] Fork and merge work
- [ ] Time travel through cosmos history

### Phase 5-6 (Advanced)

- [ ] Entanglement synchronizes edits
- [ ] Generators produce derived K-Blocks
- [ ] User reviews generated content before save

### Phase 7-9 (Complete)

- [ ] Full web UI with all views
- [ ] AGENTESE integration complete
- [ ] Documentation updated
- [ ] Performance acceptable (< 100ms for common operations)

---

## Timeline Estimate

| Phase | Sessions | Focus | Est. Effort |
|-------|----------|-------|-------------|
| 0 | 1-2 | Foundation | 1 day |
| 1 | 3-5 | Views + Sheaf | 2 days |
| 2 | 6-7 | Cosmos Persistence | 1 day |
| 3 | 8-9 | Witness Integration | 1 day |
| 4 | 10-12 | Checkpoints + Fork/Merge | 2 days |
| 5 | 13-15 | Entanglement | 2 days |
| 6 | 16-18 | Generators | 2 days |
| 7 | 19-22 | Web UI | 2 days |
| 8 | 23 | AGENTESE | 0.5 day |
| 9 | 24-25 | Polish | 1 day |

**Total**: ~14.5 days (25 sessions)

---

## Next Steps

1. **Immediate**: Review spec and plan, identify any gaps
2. **Session 1**: Implement core types (`kblock.py`, `cosmos.py`, `harness.py`)
3. **Session 2**: Verify monad laws, implement polynomial

---

*"The K-Block is not where you edit a document. It's where you edit a possible world."*

*Plan drafted: 2025-12-22*
