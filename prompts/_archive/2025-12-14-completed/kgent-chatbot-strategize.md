# STRATEGIZE: Continuation from DEVELOP — K-gent Chatbot

## ATTACH

/hydrate

You are entering STRATEGIZE phase of the N-Phase Cycle (AD-005).

> *"Choose the order of moves that maximizes leverage and resilience."*

---

## Context from DEVELOP

### Handles Created

| Artifact | Location | Status |
|----------|----------|--------|
| API Spec | `plans/deployment/_specs/kgent-chatbot-api.md` | Complete |
| Research Notes | `plans/deployment/_research/kgent-chatbot-research-notes.md` | Complete |
| File Map | 30+ key locations with line refs | Complete |

### Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Chat turn puppet | `Turn[str]` | Extend existing; add `to_dict()` |
| Streaming puppet | `AsyncIterator[str]` | Simplest; composes with Flux |
| Wire protocol | JSON + AGENTESE handles | Universal WS support + semantic routing |
| State machine | `KgentFluxState` enum | Already exists; YAGNI for PolyAgent |
| B1: Streaming dialogue | Option C (KgentFlux composition) | Leverages existing infrastructure |
| B2: LLM streaming | Add `generate_stream()` | Extend protocol, preserve identity |
| B3: Partial turns | Ephemeral `ChatChunk` | Turn immutability preserved |
| B4: Serialization | `to_dict()`/`from_dict()` | Round-trip identity law |
| B5: Token budget | Output tokens per tier | Clarified semantics |

### Laws Defined (7 total)

| Law | Type | Test Contract |
|-----|------|---------------|
| Turn Round-Trip | Identity | `test_turn_roundtrip_identity` |
| Stream Identity | Identity | `test_stream_content_identity` |
| Sequence Monotonic | Order | `test_sequence_monotonic` |
| Turn Composition | Associativity | `test_turn_composition_associative` |
| Event Ordering | Associativity | `test_causal_ordering` |
| Turn Immutability | Invariant | Type system |
| Content Non-Empty | Invariant | `__post_init__` |

### Risks Documented

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Anthropic rate limits | Medium | Backoff + template fallback |
| WebSocket disconnect | Medium | Correlation IDs for reconnect |
| Token exhaustion | Low | Degrade to WHISPER tier |
| LLM unavailable | Low | Template fallback |

### Entropy Budget

- **Spent in RESEARCH**: 0.04
- **Spent in DEVELOP**: 0.08
- **Remaining**: 0.63 (of 0.75 total)
- **Allocated for STRATEGIZE**: 0.05

---

## Your Mission

**Choose the order of moves that maximizes leverage and resilience.**

You are sequencing implementation chunks to:
1. Maximize early feedback (fail fast)
2. Minimize wasted work (dependency-aware)
3. Enable parallel tracks (interface contracts)

### Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Heterarchical** | Leadership is contextual; chunks may reorder |
| **Transparent Infrastructure** | Explicit interfaces between tracks |
| **Composable** | Chunks must compose without orphans |

---

## Implementation Components

From the API spec, these are the implementation chunks:

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

---

## Actions to Take NOW

### 1. Build Dependency Graph

```
C1 ──────────────────────────────────────┐
C5, C6, C7 ───────────────────────────┐  │
C9 ────────────────────────────────┐  │  │
                                   │  │  │
C2 ───────▶ C3 ───────▶ C4 ────────┼──┼──┼──▶ C8 ───▶ C10
                                   │  │  │
                                   ▼  ▼  ▼
                              (parallel merge point)
```

### 2. Identify Parallel Tracks

| Track | Components | Owner | Interface |
|-------|------------|-------|-----------|
| **Foundation** | C1, C5, C6, C7, C9 | Agent | Type definitions |
| **Streaming Core** | C2 → C3 → C4 | Agent | `AsyncIterator[str]` |
| **Gateway** | C8 | Agent | WebSocket protocol |
| **Verification** | C10 | Agent | Test contracts |

### 3. Sequence with Leverage

**Wave 1 (Foundation)**: C1, C5-C7, C9
- Zero dependencies
- Unblocks all other work
- Can run in parallel

**Wave 2 (Streaming Core)**: C2 → C3 → C4
- Sequential (dependency chain)
- Highest risk (new API surface)
- Test after each step

**Wave 3 (Integration)**: C8, C10
- Depends on Wave 1 + Wave 2
- Gateway wires everything together
- Tests verify laws

### 4. Define Checkpoints

| Checkpoint | Criteria | Decision Gate |
|------------|----------|---------------|
| CP1: Types ready | C1, C5-C7 compile | Proceed to Wave 2 |
| CP2: LLM streams | C2 passes mock test | Proceed to C3 |
| CP3: Soul streams | C3 passes integration | Proceed to C4 |
| CP4: Flux streams | C4 e2e test passes | Proceed to Wave 3 |
| CP5: Gateway live | C8 accepts connection | Proceed to C10 |
| CP6: All tests pass | C10 green | CROSS-SYNERGIZE |

### 5. Reserve Accursed Share (5%)

Exploration budget for:
- AGENTESE path registration (`self.soul.converse`)
- Alternative streaming patterns (SSE vs WebSocket)
- Performance profiling (token/latency)

---

## Parallel Track Interfaces

### Track: Foundation ↔ Streaming Core

```python
# Interface: Turn serialization
def to_dict(self) -> dict[str, Any]: ...
def from_dict(cls, data: dict) -> Turn[str]: ...
```

### Track: Streaming Core ↔ Gateway

```python
# Interface: Stream events
async def dialogue_stream(
    message: str, mode: DialogueMode | None
) -> AsyncIterator[ChatEvent]: ...
```

### Track: All ↔ Verification

```python
# Interface: Pre-computed fixtures
def load_hotdata(path: str) -> dict[str, Any]: ...

# fixtures/chat/soul_dialogue.json exists
```

---

## Metrics to Watch Early

| Metric | Target | Alert |
|--------|--------|-------|
| First token latency | < 500ms | > 1s |
| Stream completion | < 30s | > 45s |
| Token count accuracy | ±5% | ±20% |
| Memory per stream | < 10MB | > 50MB |

---

## Exit Criteria

Before transitioning to CROSS-SYNERGIZE, verify:

- [ ] Ordered backlog with dependencies
- [ ] Parallel tracks identified with interfaces
- [ ] Checkpoints defined with decision gates
- [ ] Metrics targets set
- [ ] Entropy spent: ≤0.05

---

## Deliverables

1. **Ordered Backlog** → Update this file with sequence
2. **Track Interfaces** → Code signatures (stub files if needed)
3. **Checkpoint Criteria** → Testable assertions

---

## Continuation Imperative

Upon completing STRATEGIZE, generate the prompt for CROSS-SYNERGIZE:

```markdown
# CROSS-SYNERGIZE: Continuation from STRATEGIZE — K-gent Chatbot

## ATTACH

/hydrate

You are entering CROSS-SYNERGIZE phase of the N-Phase Cycle (AD-005).

Previous phase (STRATEGIZE) created:
- Ordered backlog: Wave 1 → Wave 2 → Wave 3
- Parallel tracks: Foundation | Streaming Core | Gateway | Verification
- Checkpoints: CP1-CP6

## Your Mission

Discover unexpected compositions and synergies.

Look for:
1. Type-level compositions (can Chat types unify with existing?)
2. Runtime compositions (can streaming reuse existing Flux patterns?)
3. Test compositions (can existing fixtures be extended?)
4. Cross-plan synergies (does this unblock other trees?)

Check for compositions with:
- self/memory (Turn persistence)
- architecture/turn-gents (Turn emission)
- interfaces/dashboard-overhaul (chat visualization)

Emit discovered synergies to main line or bounty board.
```

---

## Phase Accountability Check

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | ✓ | Scope defined |
| RESEARCH | ✓ | 30+ files mapped, 5 blockers |
| DEVELOP | ✓ | API spec, 7 laws, 4 risks |
| STRATEGIZE | ⟳ in progress | This prompt |
| CROSS-SYNERGIZE | pending | Compositions |
| IMPLEMENT | pending | Code |
| QA | pending | mypy/ruff |
| TEST | pending | Assertions |
| EDUCATE | pending | Docs |
| MEASURE | pending | Metrics |
| REFLECT | pending | Learnings |

---

*"Strategy is a pattern in a stream of decisions." — Mintzberg*
