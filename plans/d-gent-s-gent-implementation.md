---
path: plans/d-gent-s-gent-implementation
status: active
progress: 50
last_touched: 2025-12-17
touched_by: claude-opus-4
blocking: []
enables:
  - crown-jewel integration (Brain, Town typed state)
  - flux-state composition
session_notes: |
  2025-12-17: Plan created from spec extraction completion
  2025-12-17: Phase 1 COMPLETE - S-gent core implementation:
    - agents/s/ package created
    - StateBackend[S] protocol
    - StateFunctor with lift(), lift_logic(), unlift()
    - StatefulAgent with state threading
    - MemoryStateBackend, DataAgentBackend, DgentStateBackend adapters
    - Registered in FunctorRegistry ("State")
    - 33 tests passing + functor law verification
    - Symbiont updated with S-gent docs
    - Exported from agents package
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  IMPLEMENT: in_progress  # Phase 1 done, Phase 2-3 pending
  TEST: complete  # For Phase 1
  REFLECT: pending
entropy:
  planned: 0.4
  spent: 0.20
  returned: 0.0
---

# D-gent + S-gent Implementation

> Implementing dual-track architecture (D-gent) and StateFunctor (S-gent) from specs.

## Context

**Specs** (completed in `d-gent-s-gent-spec-extraction`):
- `spec/d-gents/dual-track.md` — Agent Memory + Application State
- `spec/s-gents/README.md` — S-gent overview
- `spec/s-gents/state-functor.md` — StateFunctor spec
- `spec/s-gents/composition.md` — Flux ∘ State patterns
- `spec/s-gents/laws.md` — Functor laws

**Gap**: Symbiont exists but no proper StateFunctor or TableAdapter.

**Design Decisions**:
- S-gent in new `agents/s/` package (separate genus)
- New `StateBackend[S]` protocol (principled, minimal: `load/save` only)
- Symbiont updated to use new interface (breaking change OK)
- Adapters for migration from `DataAgent`

---

## Phases

### Phase 1: Core S-gent (P0)

Create `agents/s/` package with StateFunctor following Flux patterns.

**Files to create**:
```
impl/claude/agents/s/
├── __init__.py
├── protocol.py           # StateBackend[S] protocol
├── state_functor.py      # StateFunctor, StatefulAgent
├── config.py             # StateConfig
├── adapters.py           # DataAgentBackend, DgentStateBackend
└── _tests/
    ├── test_state_functor.py
    └── test_state_functor_laws.py
```

**Key implementation**:
- `StateBackend[S]` protocol (minimal: `load/save` only)
- `StateFunctor(UniversalFunctor)` with `lift()`, `lift_logic()`, `unlift()`
- `StatefulAgent(Agent)` with state load → invoke → save cycle
- Auto-register with FunctorRegistry
- Adapters for `DataAgent` and `DgentProtocol` migration
- Update Symbiont to use `StateBackend[S]`

### Phase 2: TableAdapter (P1)

Bridge Alembic tables to DgentProtocol.

**Files to create**:
```
impl/claude/agents/d/adapters/
├── __init__.py
└── table_adapter.py      # TableAdapter(BaseDgent)
```

**Key implementation**:
- `TableAdapter[T]` wraps SQLAlchemy model
- Implements `put/get/delete/list/causal_chain`
- `StateFunctor.from_table_adapter()` factory

### Phase 3: Flux Composition (P2)

Enable `Flux ∘ State` for streaming stateful agents.

**Key implementation**:
- `StateFunctor.compose_flux()` returns composed lift function
- Tests for state threading through stream events

---

## Critical Files

| Action | File |
|--------|------|
| Create | `impl/claude/agents/s/__init__.py` |
| Create | `impl/claude/agents/s/protocol.py` |
| Create | `impl/claude/agents/s/state_functor.py` |
| Create | `impl/claude/agents/s/config.py` |
| Create | `impl/claude/agents/s/adapters.py` |
| Create | `impl/claude/agents/s/_tests/*.py` |
| Create | `impl/claude/agents/d/adapters/table_adapter.py` |
| Modify | `impl/claude/agents/d/__init__.py` (exports) |
| Modify | `impl/claude/agents/d/symbiont.py` (use StateBackend) |
| Modify | `impl/claude/agents/__init__.py` (export s) |

---

## Success Criteria

- [ ] StateFunctor passes identity law
- [ ] StateFunctor passes composition law
- [ ] State persists across invocations
- [ ] Symbiont unchanged behavior (backward compat)
- [ ] TableAdapter implements DgentProtocol
- [ ] Flux ∘ State composition works
- [ ] Registered in FunctorRegistry
- [ ] All existing tests pass

---

## Estimated Effort

| Phase | Time |
|-------|------|
| Phase 1 | 2-3 hours |
| Phase 2 | 1-2 hours |
| Phase 3 | 30 min |

---

*"State threads through computation like a river. D-gent is the riverbed. S-gent is the flow."*
