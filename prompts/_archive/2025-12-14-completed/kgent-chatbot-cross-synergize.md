# CROSS-SYNERGIZE: Continuation from STRATEGIZE — K-gent Chatbot

## ATTACH

/hydrate

You are entering CROSS-SYNERGIZE phase of the N-Phase Cycle (AD-005).

> *"The whole is greater than the sum of its parts — but only if the parts compose."*

---

## Context from STRATEGIZE

### Ordered Backlog

| Wave | Components | Status |
|------|------------|--------|
| Wave 1 (Foundation) | C1, C5-C7, C9 | Ready for parallel execution |
| Wave 2 (Streaming Core) | C2 → C3 → C4 | Sequential dependency chain |
| Wave 3 (Integration) | C8, C10 | Parallel after Wave 2 |

### Parallel Tracks

| Track | Purpose | Interface |
|-------|---------|-----------|
| Foundation | Types + fixtures | `Turn.to_dict()`, `ChatMessage`, `ChatEvent`, `ChatChunk` |
| Streaming Core | LLM → Soul → Flux | `AsyncIterator[str]` → `AsyncIterator[ChatEvent]` |
| Gateway | WebSocket endpoint | `/chat/kgent` |
| Verification | Law tests | 7 laws (identity, associativity, invariants) |

### Checkpoints

| CP | Name | Criteria |
|----|------|----------|
| CP1 | Types ready | C1, C5-C7 compile |
| CP2 | LLM streams | C2 mock test passes |
| CP3 | Soul streams | C3 integration passes |
| CP4 | Flux streams | C4 e2e passes |
| CP5 | Gateway live | C8 accepts connection |
| CP6 | All tests pass | C10 green |

### Entropy Budget

- **Spent through STRATEGIZE**: 0.17 (of 0.75 total)
- **Remaining**: 0.58
- **Allocated for CROSS-SYNERGIZE**: 0.10

---

## Your Mission

**Discover unexpected compositions and synergies.**

Cross-synergize looks for compositions that:
1. Reduce implementation work (reuse existing infrastructure)
2. Strengthen existing systems (new consumers for existing APIs)
3. Unblock parallel work (interface contracts enable independence)
4. Surface hidden dependencies (what else needs these types?)

---

## Actions to Take NOW

### 1. Type-Level Compositions

Search for existing types that Chat types might unify with:

| New Type | Potential Unification | Investigation |
|----------|----------------------|---------------|
| `ChatMessage` | `SoulEvent`? | Check if `SoulEvent` already has role/content |
| `ChatEvent` | `MirrorEvent`? | Check if `HolographicBuffer.reflect()` format matches |
| `ChatChunk` | Existing streaming? | Check if Flux already has chunk concept |
| `Turn.to_dict()` | `Event.to_dict()`? | Should serialization be on base Event? |

**Run**:
```bash
grep -r "class.*Event" impl/claude --include="*.py" | head -20
grep -r "to_dict\|from_dict" impl/claude --include="*.py"
```

### 2. Runtime Compositions

Check if streaming can reuse existing Flux patterns:

| Component | Existing Pattern | Reuse Opportunity |
|-----------|------------------|-------------------|
| `generate_stream()` | `KgentFlux.start()` returns `AsyncIterator[SoulEvent]` | Compose? |
| `dialogue_stream()` | `SoulDialogueOutput` | Extend with stream variant? |
| Gateway streaming | `/observe/{agent_id}` | Reuse mirror broadcast? |

**Check**: Does `KgentFlux._emit_output()` (line 737-754) already do what we need?

### 3. Test Compositions

Can existing fixtures be extended rather than creating new ones?

| New Fixture | Existing Location | Extension |
|-------------|-------------------|-----------|
| `soul_dialogue.json` | `fixtures/` | Any existing LLM fixtures? |
| Integration tests | `test_kgent_flux.py` | Add streaming tests there? |
| Law tests | `test_trace_*.py` | Extend existing law framework? |

### 4. Cross-Plan Synergies

Check for compositions with active plans:

| Plan | Progress | Potential Synergy |
|------|----------|-------------------|
| `self/memory` | 75% | Turn persistence → GhostCache? |
| `architecture/turn-gents` | 100% | Turn emission → existing infrastructure |
| `interfaces/dashboard-overhaul` | 0% | Chat visualization → DebuggerScreen? |
| `void/entropy` | 100% | Entropy tithe → existing void protocol |

**Action**: Read each plan's interface section; identify shared types.

---

## Synergy Detection Protocol

For each potential synergy, answer:

1. **Does it reduce work?** (Less code to write)
2. **Does it strengthen existing?** (More consumers = more robust)
3. **Does it introduce coupling?** (Bad if changes ripple)
4. **Is the interface stable?** (Changing = bad synergy)

### Emit Synergies

| Synergy ID | Components | Type | Emit To |
|------------|------------|------|---------|
| S1 | ? | Type unification | Main line |
| S2 | ? | Runtime reuse | Main line |
| S3 | ? | Test extension | Main line |
| S4 | ? | Cross-plan | Bounty board |

---

## Specific Investigation: Memory Substrate

The `self/memory` plan (75% complete) has `GhostCache` for Turn persistence.

**Questions**:
1. Can `Turn.to_dict()` (C1) feed directly into GhostCache?
2. Does GhostCache already have serialization we can reuse?
3. Can chat history use memory substrate for persistence?

**Read**: `impl/claude/protocols/agentese/contexts/self_.py` (memory paths)

---

## Specific Investigation: HolographicBuffer

The `HolographicBuffer.reflect()` expects `dict[str, Any]`.

**Questions**:
1. Can `ChatEvent.to_json()` → `dict` feed directly to `reflect()`?
2. Does `/observe/kgent` already broadcast SoulEvents? Can we add ChatEvents?
3. Is there event type discrimination in mirror protocol?

**Read**: `impl/claude/protocols/terrarium/mirror.py:117-146`

---

## Deliverables

1. **Synergy Report** → List of discovered compositions with rationale
2. **Interface Updates** → Any changes to Track interfaces from synergies
3. **Bounty Board Entries** → Future work discovered but not in scope
4. **Updated Backlog** → Components modified based on synergies

---

## Exit Criteria

Before transitioning to IMPLEMENT, verify:

- [ ] All 4 synergy domains investigated (type, runtime, test, cross-plan)
- [ ] Synergies documented with rationale
- [ ] Interface contracts updated if synergies change them
- [ ] No orphaned components (everything composes)
- [ ] Entropy spent: ≤0.10

---

## Continuation Imperative

Upon completing CROSS-SYNERGIZE, generate the prompt for IMPLEMENT:

```markdown
# IMPLEMENT: Continuation from CROSS-SYNERGIZE — K-gent Chatbot

## ATTACH

/hydrate

You are entering IMPLEMENT phase of the N-Phase Cycle (AD-005).

Previous phases created:
- Ordered backlog: Wave 1 → Wave 2 → Wave 3 (10 components)
- Parallel tracks: Foundation | Streaming Core | Gateway | Verification
- Checkpoints: CP1-CP6
- Synergies: [list discovered synergies]

## Your Mission

Execute Wave 1 (Foundation) in parallel:
- C1: Turn.to_dict()/from_dict()
- C5-C7: ChatMessage, ChatEvent, ChatChunk
- C9: Pre-computed fixtures

Write production code. Tests come in TEST phase.
Checkpoint CP1: All types compile, mypy passes.
```

---

## Phase Accountability Check

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | complete | Scope defined |
| RESEARCH | complete | 30+ files mapped, 5 blockers |
| DEVELOP | complete | API spec, 7 laws, 4 risks |
| STRATEGIZE | complete | 3 waves, 4 tracks, 6 checkpoints |
| CROSS-SYNERGIZE | in progress | This prompt |
| IMPLEMENT | pending | Code |
| QA | pending | mypy/ruff |
| TEST | pending | Assertions |
| EDUCATE | pending | Docs |
| MEASURE | pending | Metrics |
| REFLECT | pending | Learnings |

---

*"Synergy is not magic. It is the careful alignment of interfaces."*
