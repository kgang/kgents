# DEVELOP: Continuation from RESEARCH — Permanent K-gent Chatbot

## ATTACH

/hydrate

You are entering DEVELOP phase of the N-Phase Cycle (AD-005).

> *"Design compression: minimal specs that can regenerate code."*

---

## Context from RESEARCH

### Handles Created

| Artifact | Location | Status |
|----------|----------|--------|
| Research Notes | `plans/deployment/_research/kgent-chatbot-research-notes.md` | Complete |
| File Map | 30+ key classes with line references | Complete |
| Invariants | 5 laws documented | Complete |
| Blockers | 5 blockers with evidence | Surfaced |

### File Map (Key Locations)

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

### Invariants (Category Laws — Must Preserve)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Turn Immutability | `Turn` is frozen dataclass | Cannot mutate after creation |
| Identity | `TraceMonoid.append_mut(e)` preserves e.id | Event identity survives emission |
| Associativity | `(a >> b) >> c ≡ a >> (b >> c)` for Turn composition | Topological order preserved |
| Fire-and-Forget | `HolographicBuffer.reflect()` never awaits | Agent metabolism unblocked |
| Topological Order | `CausalCone.project_context()` respects happens-before | Causal history is valid |

### Blockers Surfaced (with Evidence)

| ID | Blocker | Evidence | Impact |
|----|---------|----------|--------|
| B1 | No streaming in dialogue | `soul.py:285-381` returns complete output | Cannot stream to WebSocket |
| B2 | LLM uses subprocess | `llm.py:124-154` awaits full response | No token-by-token streaming |
| B3 | Partial turn unclear | `turn.py:60` frozen=True | How to emit chunks? |
| B4 | Turn lacks serialization | No `.to_dict()` method | HolographicBuffer expects dict |
| B5 | Token budget ambiguous | `soul.py:79-95` BudgetConfig | Input vs output vs total? |

### Entropy Budget

- **Spent in RESEARCH**: ~0.04
- **Allocated for DEVELOP**: 0.10
- **Remaining after DEVELOP**: 0.61 (of 0.75 total)

---

## Your Mission

**Convert research into sharpened specs, APIs, and operable contracts.**

You are performing **design compression**: finding the minimal specification that can regenerate the implementation. The spec should be smaller than the impl (Generative principle).

### Step 1: Select Puppets

Choose the representation that makes the problem tractable:

| Concept | Puppet Candidates | Recommended |
|---------|-------------------|-------------|
| Chat turn | `Turn[T]` / `SoulEvent` / new `ChatTurn` | Extend `Turn[str]` |
| Streaming | `AsyncIterator[str]` / `FluxAgent` / callbacks | `AsyncIterator[str]` |
| Wire protocol | JSON / Protobuf / AGENTESE paths | JSON with AGENTESE handles |
| State machine | `PolyAgent[S,A,B]` / ad-hoc | `PolyAgent[ChatState, ChatInput, ChatOutput]` |

**Decision required**: Document which puppet for each concept and why.

### Step 2: Define Contracts

For each new component, specify:

1. **Inputs/Outputs** with types (no `Any` escapes)
2. **Laws** — Identity and Associativity assertions
3. **Error surfaces** — What can fail and how?
4. **Privacy/Ethics constraints** — What data is sensitive?
5. **HotData hooks** — Pre-computed fixtures for testing

### Step 3: Prototype in Spec

Draft examples and edge cases. This is NOT implementation—it's specification. The spec should be ~3x smaller than eventual implementation.

---

## Principles Alignment (from spec/principles.md)

### Primary Principles for DEVELOP

| Principle | Application |
|-----------|-------------|
| **Generative** | Spec is compression; delete impl and regenerate from spec |
| **Tasteful** | Only necessary primitives survive; say "no" to bloat |
| **Composable** | Contracts preserve identity/associativity; verify laws |

### Secondary Principles

| Principle | Application |
|-----------|-------------|
| **Ethical** | Chat content may be sensitive; no data hoarding |
| **Heterarchical** | Chat agent can be invoked OR streaming (dual mode) |
| **AGENTESE** | Map to handles: `self.soul.converse`, `time.chat.witness` |

### Meta-Principle: Accursed Share

Reserve 5-10% for exploration that may not directly serve the goal:
- What if we used AGENTESE paths instead of REST?
- What if Turn emission used the Sheaf pattern?
- Draw from `void.entropy.sip(0.05)` for these explorations.

---

## Blocker Resolutions

Design solutions for each blocker. Choose ONE option per blocker and document rationale.

### B1 — Streaming Dialogue

**Options**:

```python
# Option A: New streaming method on KgentSoul
async def dialogue_stream(
    self, message: str, mode: DialogueMode
) -> AsyncIterator[str]:
    """Stream tokens as they arrive. Emits SPEECH turn on complete."""

# Option B: Emit THOUGHT turns for partial content (existing pattern)
for chunk in chunks:
    trace.append_mut(Turn.create_turn(
        content=chunk, turn_type=TurnType.THOUGHT, ...
    ))
# Final SPEECH turn at end

# Option C: Use existing KgentFlux with SoulEvent stream (composition)
async for event in flux.start(input_events):
    yield event.payload.get("content", "")
```

**Decision Criteria**:
- Option A: New API surface (more tasteful if well-designed)
- Option B: Reuses existing Turn semantics (more composable)
- Option C: Leverages existing Flux infrastructure (most generative)

→ **CHOOSE ONE** and document: "Chose Option [X] because [rationale aligned with principles]"

### B2 — Streaming LLM Client

**Contract**:

```python
class LLMClient(Protocol):
    """Extended to support streaming."""

    async def generate(
        self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 4000
    ) -> LLMResponse:
        """Non-streaming generation (existing)."""
        ...

    async def generate_stream(
        self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 4000
    ) -> AsyncIterator[str]:
        """
        Stream tokens as they arrive.

        Laws:
        - Concatenating yielded strings ≡ generate().text (identity)
        - Order of yields is temporal (associativity preserved)

        Error surface:
        - Network errors: yield partial, then raise
        - Rate limits: raise RateLimitError with retry_after
        """
        ...
```

**Implementation hint**: Anthropic SDK `messages.stream()` with `async for` on `text_stream`.

### B3 — Partial Turn Emission

**Decision**:

The Turn is immutable by design. Streaming chunks are NOT turns—they are **ephemeral artifacts** that exist only in the wire protocol. The TraceMonoid only stores complete turns.

**Contract**:

```python
@dataclass(frozen=True)
class ChatChunk:
    """
    Ephemeral streaming artifact. NOT persisted to TraceMonoid.

    This is NOT a Turn. It exists only in the WebSocket wire.
    """
    content: str
    sequence: int
    final: bool
    correlation_id: str  # Links chunks to eventual Turn

# On stream completion:
final_turn = Turn.create_turn(
    content="".join(chunks),  # Full concatenated content
    source="kgent-soul",
    turn_type=TurnType.SPEECH,
    ...
)
trace.append_mut(final_turn)  # Only the complete turn is persisted
```

**Law**: `sum(chunk.content for chunk in chunks) == final_turn.content`

### B4 — Turn Serialization

**Contract**:

```python
# Add to Turn class (impl/claude/weave/turn.py)
def to_dict(self) -> dict[str, Any]:
    """
    Serialize Turn for HolographicBuffer.

    AGENTESE handle: self.turn.manifest → dict representation

    Law: Turn.from_dict(turn.to_dict()) ≡ turn (round-trip identity)
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
def from_dict(cls, data: dict[str, Any]) -> "Turn[str]":
    """Deserialize Turn. Inverse of to_dict()."""
    ...
```

### B5 — Token Budget Semantics

**Clarification**:

```python
@dataclass
class BudgetConfig:
    """
    Token budgets for K-gent responses.

    These are MAX OUTPUT TOKENS per response tier.
    Input tokens are governed by CausalCone (context window limits).

    The budget is the Accursed Share allocation:
    - DORMANT: No LLM call (template only)
    - WHISPER: Quick acknowledgment (~100 output tokens)
    - DIALOGUE: Full conversation (~4000 output tokens)
    - DEEP: Council of Ghosts (~8000 output tokens)

    Entropy cost: Each tier draws from session entropy budget.
    """
    dormant_max: int = 0       # Output tokens for DORMANT
    whisper_max: int = 100     # Output tokens for WHISPER
    dialogue_max: int = 4000   # Output tokens for DIALOGUE
    deep_max: int = 8000       # Output tokens for DEEP
```

---

## New Types (Spec Draft)

### ChatMessage (Input Schema)

```python
@dataclass(frozen=True)
class ChatMessage:
    """
    A chat message from user or system.

    NOT the same as Turn—this is the input format.
    Turns are the output format (what gets persisted).

    AGENTESE: world.chat.message → ChatMessage
    """
    role: Literal["user", "system"]
    content: str
    timestamp: float = field(default_factory=time.time)
    mode: DialogueMode = DialogueMode.REFLECT

    # Laws:
    # - content is non-empty (validation on creation)
    # - timestamp is monotonically increasing within session
```

### ChatEvent (Wire Schema)

```python
@dataclass(frozen=True)
class ChatEvent:
    """
    WebSocket wire format for chat.

    AGENTESE: time.chat.witness → Stream[ChatEvent]

    Event types:
    - "chunk": Streaming partial content
    - "message": Complete message (has turn_id)
    - "error": Error with recovery hint
    - "done": Stream termination
    """
    event_type: Literal["chunk", "message", "error", "done"]
    payload: dict[str, Any]
    sequence: int
    timestamp: float = field(default_factory=time.time)

    # Laws:
    # - sequence is monotonically increasing
    # - "done" is always final event
    # - "message" events have turn_id in payload
```

### ChatFluxConfig

```python
@dataclass
class ChatFluxConfig:
    """
    Configuration for chat streaming.

    Following Pre-Computed Richness principle (AD-004):
    Default values are tuned from actual usage, not guessed.
    """
    emit_thoughts: bool = False      # Emit THOUGHT turns for chunks?
    buffer_chunks: int = 5           # Coalesce N chunks before WebSocket emit
    stream_timeout: float = 30.0     # Max seconds for stream response
    entropy_budget: float = 0.10     # Accursed Share per dialogue
```

---

## WebSocket Wire Protocol

### Version

```yaml
protocol_version: "1.0.0"
agentese_handles:
  perturb: "self.soul.perturb"
  observe: "time.soul.witness"
```

### Client → Server (/perturb/kgent)

```json
{
  "action": "message",
  "version": "1.0.0",
  "data": {
    "content": "What should I focus on?",
    "mode": "reflect",
    "correlation_id": "uuid-from-client"
  }
}
```

### Server → Client (/observe/kgent)

**Chunk event** (streaming):
```json
{
  "event_type": "chunk",
  "sequence": 1,
  "payload": {
    "content": "Let me think about",
    "correlation_id": "uuid-from-client",
    "final": false
  }
}
```

**Message event** (complete):
```json
{
  "event_type": "message",
  "sequence": 5,
  "payload": {
    "content": "Let me think about what matters most...",
    "turn_id": "uuid-turn-id",
    "mode": "reflect",
    "tokens_used": 47,
    "correlation_id": "uuid-from-client"
  }
}
```

**Error event**:
```json
{
  "event_type": "error",
  "sequence": 2,
  "payload": {
    "code": "RATE_LIMITED",
    "message": "Token budget exhausted",
    "retry_after_seconds": 60,
    "correlation_id": "uuid-from-client"
  }
}
```

---

## Test Contracts (Pre-Computed Richness)

Following AD-004, test fixtures use pre-computed LLM outputs, not mocks:

### Fixture: Pre-Computed Chat Responses

```python
# fixtures/chat/soul_dialogue.json (generated once by LLM)
{
  "input": {"content": "What should I focus on?", "mode": "reflect"},
  "output": {
    "content": "The pattern I notice is...",
    "tokens_used": 47,
    "turn_type": "SPEECH"
  }
}

# In tests:
@pytest.fixture
def precomputed_dialogue():
    return load_hotdata("fixtures/chat/soul_dialogue.json")
```

### Contract: Turn Emission

```python
def test_turn_emitted_on_complete_response(trace_monoid, precomputed_dialogue):
    """
    Law: Complete dialogue emits exactly one SPEECH turn.

    Category: Identity — the turn content equals concatenated chunks
    """
    # Given: pre-computed dialogue
    # When: dialogue completes
    # Then: exactly 1 SPEECH turn in monoid
    # And: turn.content == expected_content
    assert len(trace_monoid.events) == 1
    assert trace_monoid.events[0].turn_type == TurnType.SPEECH
    assert trace_monoid.events[0].content == precomputed_dialogue["output"]["content"]
```

### Contract: Streaming Order

```python
def test_chunks_preserve_order(chat_flux):
    """
    Law: Chunk sequence numbers are monotonically increasing.

    Category: Associativity — order of composition preserved
    """
    events = []
    async for event in chat_flux.stream_dialogue("test"):
        events.append(event)

    sequences = [e.sequence for e in events]
    assert sequences == sorted(sequences)  # Monotonic
```

### Contract: Round-Trip Serialization

```python
def test_turn_roundtrip_identity(sample_turn):
    """
    Law: Turn.from_dict(turn.to_dict()) ≡ turn

    Category: Identity morphism for serialization
    """
    serialized = sample_turn.to_dict()
    deserialized = Turn.from_dict(serialized)
    assert deserialized == sample_turn
```

---

## Recursive Hologram

Apply a micro PLAN→RESEARCH→DEVELOP cycle to this spec:

### Micro-PLAN
- **Goal**: Spec for K-gent chatbot with streaming
- **Scope**: Types, protocols, laws

### Micro-RESEARCH
- Does existing `SoulEvent` already handle chat? → Partially
- Can we extend rather than create? → Yes, extend Turn with to_dict()

### Micro-DEVELOP
- Smallest generative grammar: `ChatMessage → ChatFlux → Turn → ChatEvent`
- This pipeline compresses the entire feature

---

## Potential Branches (Surfaced During DEVELOP)

| Branch | Impact | Classification | Action |
|--------|--------|----------------|--------|
| AGENTESE path for chat (`self.soul.converse`) | MED | Parallel | Bounty |
| PolyAgent formalization for chat states | LOW | Deferred | Bounty |
| Pre-computed fixture generation script | MED | Parallel | Bounty |

→ Main line continues to STRATEGIZE. Branches emitted to `plans/_bounty.md`.

---

## Exit Criteria

Before transitioning to STRATEGIZE, verify:

- [ ] All 5 blockers have documented resolutions with rationale
- [ ] Puppet selection documented (which representation for each concept)
- [ ] Type signatures complete (no `Any` escapes)
- [ ] Laws stated and testable (identity/associativity for each contract)
- [ ] Wire protocol is version-tagged
- [ ] Test contracts use pre-computed fixtures (AD-004)
- [ ] Privacy constraints documented (sensitive data handling)
- [ ] Entropy spent: ≤0.10

---

## Deliverables

1. **API Spec** → `plans/deployment/_specs/kgent-chatbot-api.md`
2. **Blocker Resolutions** → Inline in spec with rationale
3. **Test Contracts** → Spec for fixtures and law assertions
4. **Branches Emitted** → `plans/_bounty.md` (if any)

---

## Continuation Imperative

Upon completing DEVELOP, generate the prompt for STRATEGIZE using this structure:

---

### Generated Prompt: STRATEGIZE after DEVELOP

```markdown
# STRATEGIZE: Continuation from DEVELOP — K-gent Chatbot

## ATTACH

/hydrate

You are entering STRATEGIZE phase of the N-Phase Cycle (AD-005).

Previous phase (DEVELOP) created these handles:
- API Spec: plans/deployment/_specs/kgent-chatbot-api.md
- Laws defined: ${laws_count} (identity/associativity assertions)
- Risks documented: ${risks_noted}
- Blocker resolutions: 5/5 complete

Design decisions made:
- Puppet: ${puppet_choices}
- Streaming: ${streaming_approach}
- Serialization: Turn.to_dict() with round-trip law

Blockers resolved for sequencing:
- ${resolved_blockers}

Branches emitted:
- ${branches_emitted or "None"}

## Your Mission

Choose the order of moves that maximizes leverage and resilience. You are:
- Prioritizing chunks by impact/effort and dependency graph
- Identifying parallel tracks with clear interfaces
- Defining checkpoints and decision gates

**Principles Alignment** (from spec/principles.md):
- **Heterarchical**: Leadership is contextual; no fixed order
- **Transparent Infrastructure**: Communication is explicit
- **Composable**: Chunks must compose without orphans

## Actions to Take NOW

1. Prioritize by leverage:
   - Impact/effort matrix for each component
   - Dependency graph (what blocks what)
   - Reserve Accursed Share buffer (5%)

2. Parallelize safely:
   - Identify independent tracks (e.g., LLM client vs. Turn serialization)
   - Define interfaces between tracks
   - Assign ownership (human/agent)

3. Define signals:
   - Checkpoints for progress
   - Metrics to watch early (latency, token usage)
   - Decision gates for CROSS-SYNERGIZE

4. Run oblique lookback:
   - Execute lookback-revision.md on strategy
   - Surface frame errors before locking order

## Exit Criteria

- Ordered backlog with owners, dependencies, and checkpoints
- Parallel tracks identified with interfaces
- Ready to discover compositions in CROSS-SYNERGIZE

## Continuation Imperative

Upon completing STRATEGIZE, generate the prompt for CROSS-SYNERGIZE using the same structure. The form is the function.
```

---

## Template Variables (Fill Before Generating)

| Variable | Source |
|----------|--------|
| `${laws_count}` | Count of identity/associativity laws defined |
| `${risks_noted}` | Risks documented during DEVELOP |
| `${puppet_choices}` | Puppets selected for each concept |
| `${streaming_approach}` | Which streaming option chosen (A/B/C) |
| `${resolved_blockers}` | Summary of B1-B5 resolutions |
| `${branches_emitted}` | Branches from Potential Branches table |

---

## Phase Accountability Check

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | ✓ (prior) | Scope defined in creativity session |
| RESEARCH | ✓ | 30+ files mapped, 5 blockers surfaced |
| DEVELOP | ⟳ in progress | This prompt |
| STRATEGIZE | pending | Ordered backlog |
| CROSS-SYNERGIZE | pending | Compositions discovered |
| IMPLEMENT | pending | Code written |
| QA | pending | mypy/ruff clean |
| TEST | pending | Assertions pass |
| EDUCATE | pending | User-facing docs |
| MEASURE | pending | Metrics captured |
| REFLECT | pending | Learnings extracted |

---

*"The specification is the compression. The implementation expands it."*
