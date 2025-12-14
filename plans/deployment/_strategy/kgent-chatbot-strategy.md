---
path: deployment/_strategy/kgent-chatbot-strategy
status: active
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [deployment/permanent-kgent-chatbot]
session_notes: |
  STRATEGIZE phase output. Ordered backlog with 3 waves, 4 tracks, 6 checkpoints.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.05
  spent: 0.04
  returned: 0.01
---

# STRATEGIZE: K-gent Chatbot Implementation Strategy

> *"Choose the order of moves that maximizes leverage and resilience."*

**Phase**: STRATEGIZE (N-Phase Cycle AD-005)
**Entropy Budget**: 0.05 | **Spent**: 0.04

---

## 1. Dependency Graph

```
                    ┌───────────────────────────────────────────────────┐
                    │                   WAVE 1                          │
                    │            (Foundation - Parallel)                │
                    └───────────────────────────────────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌───────┐               ┌───────────┐             ┌───────┐
│  C1   │               │  C5-C7    │             │  C9   │
│Turn   │               │  Chat     │             │Fixture│
│serde  │               │  Types    │             │  s    │
└───────┘               └───────────┘             └───────┘
    │                         │                         │
    └─────────────────────────┼─────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │     CHECKPOINT 1  │
                    │   "Types compile" │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────────────────────┐
                    │              WAVE 2               │
                    │       (Streaming Core - Serial)   │
                    └───────────────────────────────────┘
                              │
                              ▼
                          ┌───────┐
                          │  C2   │ LLMClient.generate_stream()
                          └───┬───┘
                              │ CHECKPOINT 2: "LLM streams"
                              ▼
                          ┌───────┐
                          │  C3   │ KgentSoul.dialogue_stream()
                          └───┬───┘
                              │ CHECKPOINT 3: "Soul streams"
                              ▼
                          ┌───────┐
                          │  C4   │ KgentFlux.dialogue_stream()
                          └───┬───┘
                              │ CHECKPOINT 4: "Flux streams"
                              │
                    ┌─────────▼─────────────────────────┐
                    │              WAVE 3               │
                    │     (Integration - Parallel)      │
                    └───────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                                   ▼
        ┌───────┐                           ┌───────┐
        │  C8   │ Gateway streaming         │  C10  │ Integration tests
        └───┬───┘ endpoint                  └───────┘
            │
            │ CHECKPOINT 5: "Gateway live"
            │
    ┌───────▼───────┐
    │  CHECKPOINT 6 │
    │ "All tests    │
    │    pass"      │
    └───────────────┘
            │
            ▼
    ┌───────────────┐
    │CROSS-SYNERGIZE│
    └───────────────┘
```

---

## 2. Ordered Backlog (10 Components)

### Wave 1: Foundation (Parallel - No Dependencies)

| ID | Component | Location | LOE | Owner | Interface |
|----|-----------|----------|-----|-------|-----------|
| C1 | `Turn.to_dict()/from_dict()` | `weave/turn.py:191+` | S | Agent | Identity morphism |
| C5 | `ChatMessage` type | `agents/k/chat.py` (new) | S | Agent | Input type |
| C6 | `ChatEvent` type | `agents/k/chat.py` | S | Agent | Wire format |
| C7 | `ChatChunk` type | `agents/k/chat.py` | S | Agent | Ephemeral streaming |
| C9 | Pre-computed fixtures | `fixtures/chat/` | S | Agent | `soul_dialogue.json` |

**Total LOE**: ~4 hours
**Parallelization**: All 5 run simultaneously

### Wave 2: Streaming Core (Serial - Dependency Chain)

| ID | Component | Location | LOE | Depends On |
|----|-----------|----------|-----|------------|
| C2 | `LLMClient.generate_stream()` | `agents/k/llm.py:71+` | M | C1 (for tests) |
| C3 | `KgentSoul.dialogue_stream()` | `agents/k/soul.py:381+` | M | C2 |
| C4 | `KgentFlux.dialogue_stream()` | `agents/k/flux.py:251+` | M | C3 |

**Total LOE**: ~6 hours
**Critical Path**: C2 → C3 → C4 (sequential)

### Wave 3: Integration (Parallel after Wave 2)

| ID | Component | Location | LOE | Depends On |
|----|-----------|----------|-----|------------|
| C8 | Gateway streaming endpoint | `protocols/terrarium/gateway.py:336+` | M | C4, C6 |
| C10 | Integration tests | `_tests/test_chat_integration.py` | M | C1-C9 |

**Total LOE**: ~4 hours
**Parallelization**: C8 and C10 can run in parallel

---

## 3. Parallel Tracks with Interfaces

### Track 1: Foundation (C1, C5-C7, C9)

**Purpose**: Type definitions and fixtures that unblock everything

**Interface Contract**:
```python
# weave/turn.py
class Turn(Event[T], Generic[T]):
    def to_dict(self) -> dict[str, Any]:
        """Serialize Turn for wire/storage. Law: round-trip identity."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Turn[str]:
        """Deserialize Turn. Law: from_dict(to_dict(t)) == t."""
        ...

# agents/k/chat.py
@dataclass(frozen=True)
class ChatMessage:
    """Input from user/system. NOT a Turn."""
    role: Literal["user", "system"]
    content: str
    correlation_id: str

@dataclass(frozen=True)
class ChatEvent:
    """Wire format for WebSocket. Event types: chunk, message, error, done."""
    event_type: Literal["chunk", "message", "error", "done"]
    payload: dict[str, Any]
    sequence: int

@dataclass(frozen=True)
class ChatChunk:
    """Ephemeral streaming artifact. NOT persisted."""
    content: str
    sequence: int
    final: bool
    correlation_id: str
```

### Track 2: Streaming Core (C2 → C3 → C4)

**Purpose**: LLM streaming from Anthropic API through Soul to Flux

**Interface Contract**:
```python
# agents/k/llm.py - Extend LLMClient protocol
class LLMClient(Protocol):
    async def generate_stream(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> AsyncIterator[str]:
        """Stream tokens. Law: join(chunks) == generate().text."""
        ...

# agents/k/soul.py - New method
class KgentSoul:
    async def dialogue_stream(
        self,
        message: str,
        mode: DialogueMode | None = None,
    ) -> AsyncIterator[str]:
        """Stream dialogue tokens. Uses eigenvector context."""
        ...

# agents/k/flux.py - New method
class KgentFlux:
    async def dialogue_stream(
        self,
        message: str,
        mode: DialogueMode | None = None,
    ) -> AsyncIterator[ChatEvent]:
        """Stream ChatEvents. Emits final Turn to TraceMonoid."""
        ...
```

### Track 3: Gateway (C8)

**Purpose**: WebSocket endpoint that connects browser to KgentFlux

**Interface Contract**:
```python
# protocols/terrarium/gateway.py
@app.websocket("/chat/kgent")
async def chat_kgent_stream(websocket: WebSocket) -> None:
    """
    WebSocket chat endpoint.

    Client → Server: ChatMessage (JSON)
    Server → Client: ChatEvent stream (JSON per line)

    Protocol version: 1.0.0
    """
    ...
```

### Track 4: Verification (C10)

**Purpose**: Integration tests that verify laws hold end-to-end

**Interface Contract**:
```python
# Tests verify these laws:
def test_turn_roundtrip_identity():
    """Turn.from_dict(t.to_dict()) == t"""

async def test_stream_content_identity():
    """''.join(chunks) == final_turn.content"""

async def test_sequence_monotonic():
    """all(s[i] < s[i+1] for events)"""

async def test_turn_composition_associative():
    """(a >> b) >> c == a >> (b >> c)"""

async def test_causal_ordering():
    """User turn precedes agent turn in TraceMonoid"""
```

---

## 4. Checkpoints with Decision Gates

| CP | Name | Criteria | Decision Gate |
|----|------|----------|---------------|
| CP1 | Types ready | C1, C5-C7 compile; mypy passes | Proceed to Wave 2 |
| CP2 | LLM streams | C2 mock test passes; tokens flow | Proceed to C3 |
| CP3 | Soul streams | C3 integration test; eigenvectors applied | Proceed to C4 |
| CP4 | Flux streams | C4 e2e test; ChatEvents emit correctly | Proceed to Wave 3 |
| CP5 | Gateway live | C8 accepts WS connection; echoes events | Proceed to C10 |
| CP6 | All tests pass | C10 green; all 7 laws verified | CROSS-SYNERGIZE |

**Decision Protocol**:
- If checkpoint fails: Fix before proceeding (no parallel workarounds)
- If blocked >2 hours: Escalate to research (may need spec revision)

---

## 5. Metrics Targets

| Metric | Target | Alert | Measurement |
|--------|--------|-------|-------------|
| First token latency | < 500ms | > 1s | Timer from request to first chunk |
| Stream completion | < 30s | > 45s | Timer from request to done event |
| Token count accuracy | ±5% | ±20% | Compare Anthropic reported vs counted |
| Memory per stream | < 10MB | > 50MB | RSS delta during stream |
| Test count delta | +25 | < 20 | pytest --collect-only count |
| Law assertions | 7/7 pass | < 7 | Dedicated law tests |

---

## 6. Accursed Share (5% Budget)

Reserved exploration for:

1. **AGENTESE path registration**: `self.soul.converse` → semantic routing
2. **Alternative streaming**: SSE fallback if WebSocket problematic
3. **Performance profiling**: Token/latency tradeoffs with buffer_chunks config
4. **Unexpected compositions**: Chat types unifying with existing Trace events

**Entropy**: 0.03 reserved (0.01 returned to void if unused)

---

## 7. Risk Mitigation Checkpoints

| Risk | Checkpoint | Mitigation if Hit |
|------|------------|-------------------|
| Anthropic rate limits | CP2 | Implement exponential backoff; fallback to template |
| WebSocket disconnect | CP5 | Add correlation_id for reconnect; replay from sequence |
| Token exhaustion | CP4 | Graceful degrade to WHISPER tier |
| LLM unavailable | CP2 | Template fallback; surface clear error |

---

## 8. Exit Criteria (STRATEGIZE Complete)

- [x] Ordered backlog with dependencies (10 components, 3 waves)
- [x] Parallel tracks identified with interfaces (4 tracks)
- [x] Checkpoints defined with decision gates (6 checkpoints)
- [x] Metrics targets set (6 metrics)
- [x] Entropy spent: 0.04 ≤ 0.05

---

## 9. Continuation: CROSS-SYNERGIZE Prompt

See: `prompts/kgent-chatbot-cross-synergize.md`

---

*"Strategy without tactics is the slowest route to victory. Tactics without strategy is the noise before defeat." — Sun Tzu*
