# K-gent Chatbot: N-Phase Meta-Prompt

## ATTACH

/hydrate

---

## Phase Selector

**Execute Phase**: `PHASE=[RESEARCH|DEVELOP|STRATEGIZE|CROSS-SYNERGIZE|IMPLEMENT|QA|TEST]`

> Set the phase above, then follow that phase's instructions below.

---

## Project Overview

Permanent K-gent chatbot on Terrarium with real LLM calls (Claude Opus 4.5).

**Parallel Tracks**:
| Track | Purpose |
|-------|---------|
| A: Core Chatbot | Soul → Flux → WebSocket |
| B: Trace Monoid | Turn emission, CausalCone |
| C: Dashboard | Debugger screen |
| D: LLM Infrastructure | Streaming, token budget |

**Key Decisions** (from PLAN):
- Use Claude Opus 4.5 for real LLM calls (not mocks)
- WebSocket via Terrarium Mirror Protocol (`/perturb`, `/observe`)
- All turns emitted to TraceMonoid with dependency tracking
- Dashboard Debugger screen shows live chat trace
- D-gent substrate for persistence

---

## Shared Context

### File Map

```
impl/claude/weave/trace_monoid.py:94-107   — append_mut() for turn emission
impl/claude/weave/turn.py:60-191           — Turn[T] schema with TurnType enum
impl/claude/weave/causal_cone.py:77-115    — project_context() for LLM context
impl/claude/agents/k/soul.py:285-381       — KgentSoul.dialogue() (not streaming)
impl/claude/agents/k/flux.py:214-251       — KgentFlux.start() returns AsyncIterator
impl/claude/agents/k/llm.py:227-268        — create_llm_client() auto-detection
impl/claude/protocols/terrarium/gateway.py:272-382 — /perturb and /observe endpoints
impl/claude/protocols/terrarium/mirror.py:117-146  — HolographicBuffer.reflect(dict)
```

### Invariants (Category Laws)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Turn Immutability | `Turn` is frozen dataclass | Cannot mutate after creation |
| Identity | `TraceMonoid.append_mut(e)` preserves e.id | Event identity survives emission |
| Associativity | `(a >> b) >> c ≡ a >> (b >> c)` for Turn composition | Topological order preserved |
| Fire-and-Forget | `HolographicBuffer.reflect()` never awaits | Agent metabolism unblocked |
| Topological Order | `CausalCone.project_context()` respects happens-before | Causal history is valid |

### Blockers

| ID | Blocker | Evidence | Resolution |
|----|---------|----------|------------|
| B1 | No streaming in dialogue | `soul.py:285-381` returns complete | Option C: KgentFlux composition |
| B2 | LLM uses subprocess | `llm.py:124-154` awaits full response | Add `generate_stream()` |
| B3 | Partial turn unclear | `turn.py:60` frozen=True | Ephemeral `ChatChunk` (not Turn) |
| B4 | Turn lacks serialization | No `.to_dict()` method | Add `to_dict()`/`from_dict()` |
| B5 | Token budget ambiguous | `soul.py:79-95` BudgetConfig | Output tokens per tier |

### Implementation Components

| ID | Component | Location | Dependencies | Effort |
|----|-----------|----------|--------------|--------|
| C1 | `Turn.to_dict()/from_dict()` | `weave/turn.py` | None | S |
| C2 | `LLMClient.generate_stream()` | `agents/k/llm.py` | None | M |
| C3 | `KgentSoul.dialogue_stream()` | `agents/k/soul.py` | C2 | M |
| C4 | `KgentFlux.dialogue_stream()` | `agents/k/flux.py` | C3 | M |
| C5 | `ChatMessage` type | `agents/k/chat.py` | None | S |
| C6 | `ChatEvent` type | `agents/k/chat.py` | None | S |
| C7 | `ChatChunk` type | `agents/k/chat.py` | None | S |
| C8 | Gateway streaming endpoint | `protocols/terrarium/gateway.py` | C4, C6 | M |
| C9 | Pre-computed fixtures | `fixtures/chat/` | None | S |
| C10 | Integration tests | `_tests/` | C1-C8 | M |

### Waves (Execution Order)

| Wave | Components | Strategy |
|------|------------|----------|
| 1 (Foundation) | C1, C5-C7, C9 | Parallel, zero dependencies |
| 2 (Streaming Core) | C2 → C3 → C4 | Sequential chain |
| 3 (Integration) | C8, C10 | Parallel after Wave 2 |

### Checkpoints

| CP | Name | Criteria |
|----|------|----------|
| CP1 | Types ready | C1, C5-C7 compile |
| CP2 | LLM streams | C2 mock test passes |
| CP3 | Soul streams | C3 integration passes |
| CP4 | Flux streams | C4 e2e passes |
| CP5 | Gateway live | C8 accepts connection |
| CP6 | All tests pass | C10 green |

---

## Cumulative State

### Handles Created

| Phase | Artifact | Location | Status |
|-------|----------|----------|--------|
| PLAN | Scope definition | `plans/deployment/permanent-kgent-chatbot.md` | Complete |
| RESEARCH | Research notes | `plans/deployment/_research/kgent-chatbot-research-notes.md` | Complete |
| DEVELOP | API spec | `plans/deployment/_specs/kgent-chatbot-api.md` | Complete |
| STRATEGIZE | Ordered backlog | [Shared Context above] | Complete |
| CROSS-SYNERGIZE | Synergy map | [Phase output] | Pending |

### Entropy Budget

| Phase | Allocated | Spent | Remaining |
|-------|-----------|-------|-----------|
| PLAN | 0.05 | 0.05 | 0.70 |
| RESEARCH | 0.05 | 0.04 | 0.66 |
| DEVELOP | 0.10 | 0.08 | 0.58 |
| STRATEGIZE | 0.05 | 0.05 | 0.53 |
| CROSS-SYNERGIZE | 0.10 | — | — |
| IMPLEMENT | 0.15 | — | — |
| QA | 0.05 | — | — |
| TEST | 0.08 | — | — |

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission

Map terrain to de-risk later phases. Discover prior art, invariants, blockers.

**Principles**: Curated (prevent redundant work), Composable (note contracts), Generative (compression opportunities)

### Actions

1. **Parallel reads** (essential files from File Map)
2. **Search for prior art**:
   - `class SoulEngine` — Soul engine location
   - `anthropic|claude-opus` — Existing LLM clients
   - `WebSocket|perturb|observe` — WebSocket handlers
3. **Surface blockers** with file:line evidence (B1-B5)
4. **Map existing tests**: `test_*kgent*.py`, `test_*trace*.py`

### Exit Criteria

- [ ] File map complete (30+ locations)
- [ ] Invariants documented (5+ laws)
- [ ] Blockers surfaced with evidence (5+)
- [ ] Research notes written
- [ ] Entropy spent: ≤0.05

### Deliverables

- `plans/deployment/_research/kgent-chatbot-research-notes.md`

### Continuation

On completion: `⟿[DEVELOP]` — Generate next phase prompt with researched handles.

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission

Design compression: minimal specs that regenerate code. Resolve blockers with design decisions.

**Principles**: Generative (spec < impl), Tasteful (necessary primitives only), Composable (laws verified)

### Actions

1. **Select puppets** (representations):
   | Concept | Puppet | Rationale |
   |---------|--------|-----------|
   | Chat turn | `Turn[str]` | Extend existing |
   | Streaming | `AsyncIterator[str]` | Simplest, composes |
   | Wire protocol | JSON + AGENTESE | Universal + semantic |
   | State machine | `KgentFluxState` | Already exists |

2. **Resolve blockers** (B1-B5) — see Shared Context for resolutions

3. **Define contracts** with laws:
   | Law | Type | Test |
   |-----|------|------|
   | Turn Round-Trip | Identity | `test_turn_roundtrip_identity` |
   | Stream Identity | Identity | `test_stream_content_identity` |
   | Sequence Monotonic | Order | `test_sequence_monotonic` |

4. **Draft type specs** (ChatMessage, ChatEvent, ChatChunk, ChatFluxConfig)

### Exit Criteria

- [ ] All 5 blockers have documented resolutions
- [ ] 7 laws defined with test names
- [ ] Type signatures complete (no `Any` escapes)
- [ ] Wire protocol versioned
- [ ] Entropy spent: ≤0.10

### Deliverables

- `plans/deployment/_specs/kgent-chatbot-api.md`

### Continuation

On completion: `⟿[STRATEGIZE]`

</details>

---

## Phase: STRATEGIZE

<details>
<summary>Expand if PHASE=STRATEGIZE</summary>

### Mission

Choose order of moves that maximizes leverage and resilience.

**Principles**: Heterarchical (order may change), Transparent Infrastructure (explicit interfaces), Composable (no orphans)

### Actions

1. **Build dependency graph** (see Components table)
2. **Identify parallel tracks**:
   | Track | Components | Interface |
   |-------|------------|-----------|
   | Foundation | C1, C5-C7, C9 | Type definitions |
   | Streaming Core | C2 → C3 → C4 | `AsyncIterator[str]` |
   | Gateway | C8 | WebSocket protocol |
   | Verification | C10 | Test contracts |

3. **Sequence waves** (see Waves table)
4. **Define checkpoints** (see Checkpoints table)
5. **Set metrics targets**:
   | Metric | Target | Alert |
   |--------|--------|-------|
   | First token latency | < 500ms | > 1s |
   | Stream completion | < 30s | > 45s |

### Exit Criteria

- [ ] Ordered backlog with dependencies
- [ ] Parallel tracks with interfaces
- [ ] Checkpoints defined
- [ ] Entropy spent: ≤0.05

### Continuation

On completion: `⟿[CROSS-SYNERGIZE]`

</details>

---

## Phase: CROSS-SYNERGIZE

<details>
<summary>Expand if PHASE=CROSS-SYNERGIZE</summary>

### Mission

Discover unexpected compositions and synergies.

**Goal**: Reduce work, strengthen existing systems, enable parallel execution.

### Actions

1. **Type-level compositions**:
   - `ChatMessage` ↔ `SoulEvent`?
   - `ChatEvent` ↔ `MirrorEvent`?
   - `Turn.to_dict()` ↔ `Event.to_dict()`?

2. **Runtime compositions**:
   - `generate_stream()` ↔ `KgentFlux.start()`?
   - Gateway streaming ↔ `/observe/{agent_id}`?

3. **Test compositions**:
   - Extend existing fixtures?
   - Add streaming tests to `test_kgent_flux.py`?

4. **Cross-plan synergies**:
   | Plan | Synergy |
   |------|---------|
   | `self/memory` | Turn persistence → GhostCache? |
   | `interfaces/dashboard-overhaul` | Chat → DebuggerScreen? |
   | `void/entropy` | Entropy tithe → existing protocol? |

### Synergy Detection Protocol

For each synergy: Does it reduce work? Strengthen existing? Introduce coupling? Is interface stable?

### Exit Criteria

- [ ] All 4 domains investigated
- [ ] Synergies documented with rationale
- [ ] Interfaces updated if needed
- [ ] Entropy spent: ≤0.10

### Continuation

On completion: `⟿[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission

Write production code per the ordered backlog.

### Actions

Execute waves in order:

**Wave 1 (Foundation)** — Parallel:
- C1: `Turn.to_dict()/from_dict()` in `weave/turn.py`
- C5-C7: `ChatMessage`, `ChatEvent`, `ChatChunk` in `agents/k/chat.py`
- C9: Pre-computed fixtures in `fixtures/chat/`

**Wave 2 (Streaming Core)** — Sequential:
- C2: `LLMClient.generate_stream()` in `agents/k/llm.py`
- C3: `KgentSoul.dialogue_stream()` in `agents/k/soul.py`
- C4: `KgentFlux.dialogue_stream()` in `agents/k/flux.py`

**Wave 3 (Integration)** — Parallel:
- C8: Gateway streaming endpoint
- C10: Integration tests (stubs for TEST phase)

### Checkpoint Gates

- CP1 after Wave 1: Types compile
- CP2-CP4 after each C2/C3/C4
- CP5 after C8

### Exit Criteria

- [ ] All components implemented
- [ ] Each checkpoint passed
- [ ] Code compiles (no syntax errors)
- [ ] Entropy spent: ≤0.15

### Continuation

On completion: `⟿[QA]`

</details>

---

## Phase: QA

<details>
<summary>Expand if PHASE=QA</summary>

### Mission

Static analysis: mypy, ruff clean.

### Actions

1. Run `uv run mypy impl/claude/agents/k/ impl/claude/weave/`
2. Run `uv run ruff check impl/claude/agents/k/ impl/claude/weave/`
3. Fix all errors (type errors, lint violations)
4. Verify no `Any` escapes in new code

### Exit Criteria

- [ ] mypy passes with no errors
- [ ] ruff passes with no errors
- [ ] Entropy spent: ≤0.05

### Continuation

On completion: `⟿[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission

Verify laws with assertions.

### Actions

1. Implement test contracts from DEVELOP:
   - `test_turn_roundtrip_identity`
   - `test_stream_content_identity`
   - `test_sequence_monotonic`
   - `test_turn_composition_associative`
   - `test_causal_ordering`

2. Use pre-computed fixtures (AD-004 Pre-Computed Richness)

3. Run full test suite: `uv run pytest impl/claude/agents/k/_tests/`

### Exit Criteria

- [ ] All 7 law tests implemented
- [ ] All tests pass (green)
- [ ] CP6 verified
- [ ] Entropy spent: ≤0.08

### Continuation

On completion: `⟿[REFLECT]` or return to RESEARCH for next feature.

</details>

---

## Phase Accountability

| Phase | Status |
|-------|--------|
| PLAN | ✓ complete |
| RESEARCH | ✓ complete |
| DEVELOP | ✓ complete |
| STRATEGIZE | ✓ complete |
| CROSS-SYNERGIZE | in progress |
| IMPLEMENT | pending |
| QA | pending |
| TEST | pending |
| REFLECT | pending |

---

## Accursed Share (5%)

Reserved exploration budget:
- AGENTESE path registration (`self.soul.converse`)
- Alternative streaming patterns (SSE vs WebSocket)
- Meta-prompt pattern for other N-Phase cycles

---

*"Compression is understanding." — spec/principles.md*
