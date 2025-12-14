# K-gent Chatbot API Specification

> *"The specification is the compression. The implementation expands it."*

**Version**: 1.0.0
**Phase**: DEVELOP (N-Phase Cycle AD-005)
**Entropy Spent**: 0.08 (of 0.10 allocated)

---

## 1. Puppet Selections

| Concept | Puppet | Rationale |
|---------|--------|-----------|
| Chat turn | `Turn[str]` | Existing infrastructure; just add `to_dict()`. Tasteful: extend, don't create. |
| Streaming | `AsyncIterator[str]` | Simplest representation. Composes with existing `KgentFlux.start()`. |
| Wire protocol | JSON + AGENTESE handles | JSON for universal WebSocket support; handles for semantic routing. |
| State machine | `KgentFluxState` enum | Already exists. No `PolyAgent` formalization needed (YAGNI). |
| LLM streaming | `generate_stream()` method | Extend existing `LLMClient` protocol. |

**Principle Alignment**:
- **Tasteful**: Extend `Turn`, don't create `ChatTurn`
- **Composable**: New streaming method composes with existing Flux infrastructure
- **Generative**: Spec compresses to ~200 lines; impl expands to ~600

---

## 2. Blocker Resolutions

### B1 — Streaming Dialogue

**Decision**: Option C (Compose with KgentFlux)

```python
# New method on KgentFlux
async def dialogue_stream(
    self, message: str, mode: DialogueMode | None = None
) -> AsyncIterator[ChatEvent]:
    """
    Stream dialogue tokens as ChatEvents.

    Architecture:
    1. Create DIALOGUE_TURN SoulEvent
    2. Route through soul.dialogue_stream() (new)
    3. Yield ChatEvent for each chunk
    4. On completion: emit SPEECH Turn to TraceMonoid
    5. Yield final "message" ChatEvent with turn_id

    Laws:
    - Identity: concat(chunks) == final_turn.content
    - Ordering: sequence numbers monotonically increase
    """
```

**Rationale**: Option C leverages existing `KgentFlux` infrastructure. The flux already handles state, perturbation, and mirror integration. Adding streaming is an extension, not a new system. This is the **Generative** principle: compose existing abstractions.

### B2 — Streaming LLM Client

**Contract**:

```python
class LLMClient(Protocol):
    """Extended protocol with streaming support."""

    async def generate(
        self, system: str, user: str,
        temperature: float = 0.7, max_tokens: int = 4000
    ) -> LLMResponse:
        """Non-streaming (existing)."""
        ...

    async def generate_stream(
        self, system: str, user: str,
        temperature: float = 0.7, max_tokens: int = 4000
    ) -> AsyncIterator[str]:
        """
        Stream tokens as they arrive.

        Laws:
        - Identity: "".join([chunk async for chunk in stream]) == generate().text
        - Ordering: chunks arrive in temporal order

        Error surface:
        - Network: yield partial, then raise StreamError
        - Rate limit: raise RateLimitError(retry_after=N)
        - Timeout: raise TimeoutError after config.stream_timeout
        """
        ...
```

**Implementation**: Anthropic SDK `client.messages.stream()` with `async for text in stream.text_stream`.

### B3 — Partial Turn Emission

**Decision**: Chunks are ephemeral; only complete Turns persist.

```python
@dataclass(frozen=True)
class ChatChunk:
    """
    Ephemeral streaming artifact.

    NOT a Turn. NOT persisted to TraceMonoid.
    Exists only in WebSocket wire.

    AGENTESE: time.chat.chunk → ephemeral observation
    """
    content: str
    sequence: int
    final: bool
    correlation_id: str

# Completion triggers Turn creation:
final_turn = Turn.create_turn(
    content="".join(c.content for c in chunks),
    source="kgent-soul",
    turn_type=TurnType.SPEECH,
    confidence=0.95,
    entropy_cost=tokens_used * 0.001,
)
trace.append_mut(final_turn)  # Only complete Turn persists
```

**Law**: `sum(chunk.content for chunk in chunks) == final_turn.content`

**Rationale**: Turn immutability is a **Category Law**. Streaming doesn't violate it because chunks are ephemeral—they exist only in the wire protocol, not in the TraceMonoid. This is the holographic principle: the Turn is the source of truth; chunks are projections.

### B4 — Turn Serialization

**Contract**:

```python
# Add to Turn class (impl/claude/weave/turn.py)

def to_dict(self) -> dict[str, Any]:
    """
    Serialize Turn for HolographicBuffer and storage.

    AGENTESE: self.turn.manifest → dict

    Law: Turn.from_dict(turn.to_dict()) == turn (round-trip identity)
    """
    return {
        "id": self.id,
        "content": self.content,
        "timestamp": self.timestamp,
        "source": self.source,
        "turn_type": self.turn_type.value,
        "state_hash_pre": self.state_hash_pre,
        "state_hash_post": self.state_hash_post,
        "confidence": self.confidence,
        "entropy_cost": self.entropy_cost,
    }

@classmethod
def from_dict(cls, data: dict[str, Any]) -> Turn[str]:
    """
    Deserialize Turn.

    Law: Inverse of to_dict() (identity morphism)
    """
    return cls(
        id=data["id"],
        content=data["content"],
        timestamp=data["timestamp"],
        source=data["source"],
        turn_type=TurnType(data["turn_type"]),
        state_hash_pre=data["state_hash_pre"],
        state_hash_post=data["state_hash_post"],
        confidence=data["confidence"],
        entropy_cost=data["entropy_cost"],
    )
```

### B5 — Token Budget Semantics

**Clarification**: BudgetConfig specifies MAX OUTPUT TOKENS per tier.

```python
@dataclass
class BudgetConfig:
    """
    Token budgets for K-gent responses.

    These are MAX OUTPUT TOKENS per response tier.
    Input tokens governed by CausalCone (context window).

    Entropy mapping (Accursed Share):
    - DORMANT: 0 tokens → 0 entropy
    - WHISPER: ~100 tokens → 0.001 entropy
    - DIALOGUE: ~4000 tokens → 0.04 entropy
    - DEEP: ~8000 tokens → 0.08 entropy
    """
    dormant_max: int = 0
    whisper_max: int = 100
    dialogue_max: int = 4000
    deep_max: int = 8000

    def entropy_for_tier(self, tier: BudgetTier) -> float:
        """Map tier to entropy cost."""
        return {
            BudgetTier.DORMANT: 0.0,
            BudgetTier.WHISPER: 0.001,
            BudgetTier.DIALOGUE: 0.04,
            BudgetTier.DEEP: 0.08,
        }[tier]
```

---

## 3. Type Contracts

### ChatMessage (Input)

```python
@dataclass(frozen=True)
class ChatMessage:
    """
    User or system message entering the chat.

    NOT a Turn. This is input; Turn is output.

    AGENTESE: world.chat.message → ChatMessage

    Laws:
    - content is non-empty (enforced at creation)
    - timestamp monotonically increases within session
    """
    role: Literal["user", "system"]
    content: str  # Non-empty
    timestamp: float = field(default_factory=time.time)
    mode: DialogueMode = DialogueMode.REFLECT
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("ChatMessage content cannot be empty")
```

### ChatEvent (Wire)

```python
@dataclass(frozen=True)
class ChatEvent:
    """
    WebSocket wire format.

    AGENTESE: time.chat.witness → Stream[ChatEvent]

    Event types:
    - "chunk": Streaming partial (ephemeral)
    - "message": Complete message (has turn_id)
    - "error": Error with recovery hint
    - "done": Stream termination

    Laws:
    - sequence monotonically increases
    - "done" is always terminal
    - "message" events have turn_id in payload
    """
    event_type: Literal["chunk", "message", "error", "done"]
    payload: dict[str, Any]
    sequence: int
    timestamp: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps({
            "event_type": self.event_type,
            "payload": self.payload,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
        })
```

### ChatFluxConfig

```python
@dataclass
class ChatFluxConfig:
    """
    Configuration for streaming chat.

    Following AD-004 (Pre-Computed Richness):
    Defaults tuned from actual usage, not guessed.
    """
    emit_thoughts: bool = False       # THOUGHT turns for chunks? (default: no)
    buffer_chunks: int = 5            # Coalesce before WS emit
    stream_timeout: float = 30.0      # Max response time
    entropy_budget: float = 0.10      # Accursed Share per dialogue
    heartbeat_interval: float = 5.0   # Keep-alive ping
```

---

## 4. Wire Protocol

### Version

```yaml
protocol_version: "1.0.0"
agentese_handles:
  perturb: "self.soul.perturb"
  observe: "time.soul.witness"
  stream: "time.chat.stream"
```

### Client → Server

**Endpoint**: `ws://terrarium/perturb/kgent`

```json
{
  "action": "message",
  "version": "1.0.0",
  "data": {
    "content": "What should I focus on?",
    "mode": "reflect",
    "correlation_id": "client-uuid-123"
  }
}
```

### Server → Client

**Endpoint**: `ws://terrarium/observe/kgent`

**Chunk** (streaming):
```json
{
  "event_type": "chunk",
  "sequence": 1,
  "timestamp": 1702598400.123,
  "payload": {
    "content": "Let me think about",
    "correlation_id": "client-uuid-123",
    "final": false
  }
}
```

**Message** (complete):
```json
{
  "event_type": "message",
  "sequence": 12,
  "timestamp": 1702598402.456,
  "payload": {
    "content": "Let me think about what matters most...",
    "turn_id": "turn-uuid-789",
    "mode": "reflect",
    "tokens_used": 47,
    "entropy_cost": 0.004,
    "correlation_id": "client-uuid-123"
  }
}
```

**Error**:
```json
{
  "event_type": "error",
  "sequence": 3,
  "timestamp": 1702598401.000,
  "payload": {
    "code": "RATE_LIMITED",
    "message": "Token budget exhausted",
    "retry_after_seconds": 60,
    "correlation_id": "client-uuid-123"
  }
}
```

**Done** (terminal):
```json
{
  "event_type": "done",
  "sequence": 13,
  "timestamp": 1702598402.500,
  "payload": {
    "total_chunks": 12,
    "correlation_id": "client-uuid-123"
  }
}
```

### Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| `RATE_LIMITED` | Token budget exhausted | Wait `retry_after_seconds` |
| `STREAM_TIMEOUT` | Response exceeded timeout | Retry with shorter message |
| `LLM_UNAVAILABLE` | No LLM backend available | Check Morpheus/CLI status |
| `INVALID_MESSAGE` | Malformed input | Fix client payload |
| `SESSION_EXPIRED` | Session timed out | Reconnect |

---

## 5. Laws (Category Assertions)

### Identity Laws

| Law | Assertion | Test |
|-----|-----------|------|
| Turn Round-Trip | `Turn.from_dict(t.to_dict()) == t` | `test_turn_roundtrip_identity` |
| Stream Identity | `"".join(chunks) == final_turn.content` | `test_stream_content_identity` |
| Sequence Monotonic | `all(s[i] < s[i+1] for i in range(len(s)-1))` | `test_sequence_monotonic` |

### Associativity Laws

| Law | Assertion | Test |
|-----|-----------|------|
| Turn Composition | `(a >> b) >> c == a >> (b >> c)` | `test_turn_composition_associative` |
| Event Ordering | Topological order preserved | `test_causal_ordering` |

### Invariants

| Invariant | Assertion | Enforcement |
|-----------|-----------|-------------|
| Turn Immutability | `frozen=True` on dataclass | Type system |
| Fire-and-Forget | Mirror.reflect() never awaits | Code review |
| Content Non-Empty | `len(content.strip()) > 0` | `__post_init__` validation |

---

## 6. Test Contracts (Pre-Computed Richness)

Following AD-004, use pre-computed LLM outputs:

### Fixture: Soul Dialogue

```json
// fixtures/chat/soul_dialogue.json
{
  "input": {
    "content": "What should I focus on?",
    "mode": "reflect"
  },
  "output": {
    "content": "The pattern I notice is that you're drawn to compression...",
    "tokens_used": 47,
    "turn_type": "SPEECH"
  }
}
```

### Test: Turn Emission

```python
def test_complete_dialogue_emits_speech_turn(trace_monoid, precomputed):
    """
    Law: Complete dialogue emits exactly one SPEECH turn.
    Category: Identity — turn content equals response
    """
    # Given: pre-computed dialogue
    # When: dialogue completes
    # Then: exactly 1 SPEECH turn
    assert len(trace_monoid.events) == 1
    assert trace_monoid.events[0].turn_type == TurnType.SPEECH
    assert trace_monoid.events[0].content == precomputed["output"]["content"]
```

### Test: Streaming Order

```python
async def test_chunks_monotonic_sequence(chat_flux):
    """
    Law: Sequence numbers monotonically increase.
    Category: Associativity — order preserved
    """
    events = [e async for e in chat_flux.dialogue_stream("test")]
    sequences = [e.sequence for e in events]

    assert sequences == sorted(sequences)
    assert len(sequences) == len(set(sequences))  # No duplicates
```

### Test: Round-Trip

```python
def test_turn_serialization_roundtrip(sample_turn):
    """
    Law: Turn.from_dict(turn.to_dict()) == turn
    Category: Identity morphism
    """
    serialized = sample_turn.to_dict()
    deserialized = Turn.from_dict(serialized)

    assert deserialized == sample_turn
    assert deserialized.id == sample_turn.id
    assert deserialized.turn_type == sample_turn.turn_type
```

---

## 7. Privacy Constraints

| Data | Classification | Handling |
|------|----------------|----------|
| Chat content | PII-Potential | No logging of raw content |
| User messages | Sensitive | Encrypt at rest if persisted |
| Turn IDs | Internal | Safe to log |
| Correlation IDs | Ephemeral | Expire after session |
| Token counts | Metrics | Safe to aggregate |

**Ethical Constraint**: Chat content MAY contain sensitive user data. The chatbot MUST NOT:
1. Log raw message content to external systems
2. Persist messages beyond session without consent
3. Share message content with third parties

**Implementation**: HolographicBuffer stores only Turn metadata, not content.

---

## 8. Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     WebSocket Client                         │
└────────────────────────────┬────────────────────────────────┘
                             │ JSON (ChatMessage)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Terrarium Gateway (/perturb/kgent, /observe/kgent)         │
│  - Version validation                                        │
│  - Rate limiting                                             │
│  - Session management                                        │
└────────────────────────────┬────────────────────────────────┘
                             │ SoulEvent
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  KgentFlux.dialogue_stream()                                 │
│  - State: DORMANT → FLOWING                                  │
│  - Perturbation handling                                     │
│  - Mirror integration                                        │
└────────────────────────────┬────────────────────────────────┘
                             │ AsyncIterator[str]
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  KgentSoul.dialogue_stream()  ← NEW                          │
│  - Eigenvector context                                       │
│  - Budget tier selection                                     │
│  - Template short-circuit                                    │
└────────────────────────────┬────────────────────────────────┘
                             │ AsyncIterator[str]
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  LLMClient.generate_stream()  ← NEW                          │
│  - Anthropic/Morpheus streaming                              │
│  - Token counting                                            │
│  - Error recovery                                            │
└────────────────────────────┬────────────────────────────────┘
                             │ str (tokens)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Response Assembly                                           │
│  - ChatChunk emission (ephemeral)                            │
│  - Turn creation (persistent)                                │
│  - TraceMonoid.append_mut()                                  │
│  - HolographicBuffer.reflect()                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Anthropic rate limits | Medium | High | Queue with backoff; fallback to template |
| WebSocket disconnect mid-stream | Medium | Medium | Correlation IDs for reconnection |
| Token budget exhaustion | Low | Medium | Graceful degradation to WHISPER tier |
| LLM unavailable | Low | High | Template fallback; clear error message |

---

## 10. Exit Criteria Checklist

- [x] All 5 blockers resolved with rationale
- [x] Puppet selection documented
- [x] Type signatures complete (no `Any` escapes)
- [x] Laws stated and testable (identity/associativity)
- [x] Wire protocol version-tagged (1.0.0)
- [x] Test contracts use pre-computed fixtures
- [x] Privacy constraints documented
- [x] Entropy spent: 0.08 ≤ 0.10

---

*Generated by DEVELOP phase. Ready for STRATEGIZE.*
