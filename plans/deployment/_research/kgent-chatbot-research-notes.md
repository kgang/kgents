---
path: plans/deployment/_research/kgent-chatbot-research-notes
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# RESEARCH Notes: K-gent Chatbot

**Date**: 2025-12-13
**Entropy Spent**: ~0.04
**Status**: Complete

## File Map with Key Classes

### Core Infrastructure (HIGH Priority)

| File | Class/Function | Purpose | Lines |
|------|----------------|---------|-------|
| `impl/claude/weave/trace_monoid.py` | `TraceMonoid[T]` | Concurrent history with dependency graph | 1-329 |
| `impl/claude/weave/trace_monoid.py` | `append_mut()` | Mutating append with dependencies | 94-107 |
| `impl/claude/weave/trace_monoid.py` | `linearize_subset()` | Project causal cone to list | 156-216 |
| `impl/claude/weave/turn.py` | `Turn[T]` | Extends Event with turn type + state hashes | 60-191 |
| `impl/claude/weave/turn.py` | `TurnType` | SPEECH, ACTION, THOUGHT, YIELD, SILENCE | 37-57 |
| `impl/claude/weave/causal_cone.py` | `CausalCone` | Perspective functor for context projection | 39-193 |
| `impl/claude/weave/causal_cone.py` | `project_context()` | Return minimal causal history for agent | 77-115 |

### K-gent Soul (HIGH Priority)

| File | Class/Function | Purpose | Lines |
|------|----------------|---------|-------|
| `impl/claude/agents/k/soul.py` | `KgentSoul` | Middleware of Consciousness | 189-877 |
| `impl/claude/agents/k/soul.py` | `dialogue()` | Budget-aware dialogue with templates/LLM | 285-381 |
| `impl/claude/agents/k/soul.py` | `BudgetTier` | DORMANT, WHISPER, DIALOGUE, DEEP | 69-76 |
| `impl/claude/agents/k/soul.py` | `BudgetConfig` | Token limits per tier | 78-95 |
| `impl/claude/agents/k/flux.py` | `KgentFlux` | K-gent as Flux stream agent | 100-843 |
| `impl/claude/agents/k/flux.py` | `start()` | Returns AsyncIterator[SoulEvent] | 214-251 |
| `impl/claude/agents/k/flux.py` | `_emit_output()` | Emit to output stream + mirror | 737-754 |

### LLM Infrastructure (HIGH Priority)

| File | Class/Function | Purpose | Lines |
|------|----------------|---------|-------|
| `impl/claude/agents/k/llm.py` | `LLMClient` | Protocol for LLM clients | 60-71 |
| `impl/claude/agents/k/llm.py` | `ClaudeLLMClient` | Uses claude CLI subprocess | 89-154 |
| `impl/claude/agents/k/llm.py` | `create_llm_client()` | Auto-detect best backend | 227-268 |
| `impl/claude/agents/k/llm.py` | `morpheus_available()` | Check for Morpheus Gateway | 214-224 |

### Terrarium Gateway (MEDIUM Priority)

| File | Class/Function | Purpose | Lines |
|------|----------------|---------|-------|
| `impl/claude/protocols/terrarium/gateway.py` | `Terrarium` | FastAPI WebSocket gateway | 68-505 |
| `impl/claude/protocols/terrarium/gateway.py` | `/perturb/{agent_id}` | WebSocket for injection | 272-336 |
| `impl/claude/protocols/terrarium/gateway.py` | `/observe/{agent_id}` | WebSocket for broadcast | 338-382 |
| `impl/claude/protocols/terrarium/gateway.py` | `register_agent()` | Register FluxAgent with mirror | 386-433 |
| `impl/claude/protocols/terrarium/mirror.py` | `HolographicBuffer` | Fire-and-forget broadcast | 45-308 |
| `impl/claude/protocols/terrarium/mirror.py` | `reflect()` | Emit event to mirrors | 117-146 |
| `impl/claude/protocols/terrarium/mirror.py` | `attach_mirror()` | Connect WebSocket observer | 186-210 |

### Dashboard/Debugger (MEDIUM Priority)

| File | Class/Function | Purpose | Lines |
|------|----------------|---------|-------|
| `impl/claude/agents/i/screens/debugger_screen.py` | `DebuggerScreen` | LOD 2 forensic view | 191-773 |
| `impl/claude/agents/i/screens/debugger_screen.py` | `_build_turns_from_weave()` | Map weave events to Turn objects | 389-415 |

## Invariants Found (Laws/Contracts)

### TraceMonoid Laws
1. `append_mut()` is **synchronous** (not async) — file:94-107
2. Events have `id`, `content`, `timestamp`, `source` — from Event base class
3. `linearize_subset()` produces **topological order** — file:156-216

### Turn Laws
1. Turn extends Event (IS-A relationship) — file:61
2. `TurnType` is closed enum: SPEECH, ACTION, THOUGHT, YIELD, SILENCE — file:37-57
3. Confidence clamped to [0.0, 1.0] — file:132
4. Entropy cost non-negative — file:133

### CausalCone Laws
1. `project_context()` returns minimal causal history — file:77-115
2. Agent sees: own events + transitive dependencies — file:97
3. Linearization is topological sort — file:114-115

### KgentFlux Laws
1. DORMANT → direct invoke(), FLOWING → perturbation injection — file:294-329
2. Mirror reflection is fire-and-forget — file:750-754
3. `SoulEvent` is the wire format — throughout

### HolographicBuffer Laws
1. `reflect()` never awaits clients — file:117-146
2. Slow clients don't slow agent — design principle
3. Late joiners receive history (The Ghost) — file:186-210

## Blockers with Evidence

### B1: No streaming support in KgentSoul.dialogue()

**Evidence**: `impl/claude/agents/k/soul.py:285-381`
```python
async def dialogue(self, message: str, ...) -> SoulDialogueOutput:
    # Returns complete output, not AsyncIterator[str]
    output = await self._agent.invoke(input_data)
    return SoulDialogueOutput(...)
```

**Resolution Path**:
- Add streaming variant `dialogue_stream()` returning `AsyncIterator[str]`
- Or emit partial turns to TraceMonoid as THOUGHT events

### B2: ClaudeLLMClient uses subprocess, not Anthropic API streaming

**Evidence**: `impl/claude/agents/k/llm.py:124-154`
```python
async def generate(...) -> LLMResponse:
    text, metadata = await self._runtime.raw_completion(context)
    return LLMResponse(text=text, ...)  # Waits for complete response
```

**Resolution Path**:
- For streaming, need direct Anthropic API client with `stream=True`
- MorpheusLLMClient may already support this (check `runtime/morpheus.py`)

### B3: Turn emission schema needs clarification

**Evidence**: `impl/claude/weave/turn.py:93-134`
```python
@classmethod
def create_turn(cls, content: T, source: str, turn_type: TurnType, ...) -> Turn[T]:
```

**Question**: How to emit partial turns (streaming chunks)?
- Current `Turn` is immutable (`frozen=True`) — file:60
- Need either: (a) emit complete turns with THOUGHT type, or (b) new `PartialTurn` type

### B4: HolographicBuffer expects dict, not Turn

**Evidence**: `impl/claude/protocols/terrarium/mirror.py:117-146`
```python
async def reflect(self, event: dict[str, Any]) -> None:
    # ...
    payload = json.dumps(event)
```

**Question**: Does Turn have `.to_dict()` or do we need adapter?
**Evidence**: Turn is a dataclass, has no `.to_dict()` — need to add or use `dataclasses.asdict()`

### B5: Token budget enforcement in LLM generation

**Evidence**: `impl/claude/agents/k/soul.py:79-95`
```python
@dataclass
class BudgetConfig:
    dormant_max: int = 0
    whisper_max: int = 100
    dialogue_max: int = 4000
    deep_max: int = 8000
```

**Question**: Are these INPUT tokens, OUTPUT tokens, or total?
**Resolution**: Need clarification or use Anthropic's `max_tokens` parameter for output

## Prior Art Summary

### Existing LLM Integration
- `ClaudeLLMClient` uses `claude -p` CLI subprocess — mature, works
- `MorpheusLLMClient` for cluster-native — check if supports streaming
- 17 files reference `anthropic|claude-opus` — existing patterns

### Existing WebSocket/Terrarium
- `Terrarium` gateway with `/perturb` and `/observe` — mature
- `HolographicBuffer` for broadcast — fire-and-forget, robust
- 238 files reference WebSocket/perturb/observe — well-integrated

### Existing Test Infrastructure
- `test_kgent_flux.py` — K-gent flux tests
- `test_trace_monoid.py`, `test_trace_hardening.py` — trace tests
- `test_terrarium_tui.py`, `test_terrarium_source.py` — terrarium tests

### Token Budget/Rate Limiting
- 68 files reference `token.*budget|rate.*limit`
- `BudgetConfig` in K-gent soul — existing pattern
- `entropy_budget` in KgentFluxConfig — decay model

## Questions for DEVELOP

### API Design
1. Should chatbot have its own endpoint or reuse `/perturb/{agent_id}`?
2. What is the Turn content schema for chat messages?
3. Should streaming use Server-Sent Events or WebSocket frames?

### Contract Clarifications
1. Token budget: input vs output vs total?
2. Turn ID generation: UUID or sequential?
3. Causal cone: include all agent turns or just dependencies?

### Type Compatibility
1. `Turn[T]` generic: what concrete type for chat content?
2. `SoulEvent` vs `Turn`: when to use which?
3. Need `Turn.to_dict()` for HolographicBuffer compatibility?

## Summary

### What Exists (Can Reuse)
- TraceMonoid with dependency tracking
- CausalCone for context projection
- KgentFlux for stream processing
- KgentSoul for dialogue
- Terrarium gateway with WebSocket
- HolographicBuffer for broadcast
- LLMClient abstraction

### What Needs Building
- Streaming dialogue (AsyncIterator)
- Turn → dict adapter for mirror
- Chat-specific SoulEvent types
- Token budget enforcement in generation
- Dashboard chat panel (or reuse DebuggerScreen)

### Recommended Architecture
```
Browser → /perturb/kgent → KgentFlux.inject() → KgentSoul.dialogue()
                                ↓
                         Turn to TraceMonoid
                                ↓
                         HolographicBuffer.reflect()
                                ↓
                         /observe/kgent → Browser
```

---

*"The map is not the territory, but without the map we wander."*
