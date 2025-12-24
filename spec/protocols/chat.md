# AGENTESE Chat Protocol: Conversational Affordances

**Status:** Specification v2.0
**Date:** 2025-12-24
**Principles:** Composable, Generative, Ethical, Joy-Inducing
**Dependencies:** AGENTESE v3, AD-015 (Proxy Handles), AD-012 (Aspect Projection)

---

## Epigraph

> *"A conversation is not an exchange of nouns. It is the meeting of two rates of change."*
>
> *"The Session is ground truth; the Working Context is a computed projection."*
>
> *"Chat is not a feature. Chat is an affordance that any node can expose."*

---

## Part I: Core Insight

### 1.1 Chat as Composable Affordance

Chat is not a separate system—it is a **composable affordance** that any AGENTESE node can expose. Just as `manifest` reveals state and `refine` enables dialectics, `chat` enables turn-based conversation with any entity that can converse.

```
Chat : Node × Observer → ChatSession
```

Where:
- `Node` is any AGENTESE node that exposes the `chat` affordance
- `Observer` is the user's umwelt
- `ChatSession` is a stateful coalgebra: `State → (Response × State)`

### 1.2 What This Enables

| Capability | Mechanism |
|------------|-----------|
| Chat with K-gent | `self.soul.chat.send[message="..."]` |
| Chat with Town citizen | `world.town.citizen.<name>.chat.send[message="..."]` |
| Chat with any agent | `world.agent.<id>.chat.send[message="..."]` |
| Collaborative chat | `self.flow.collaboration.post[message="..."]` |
| Research dialogue | `self.flow.research.converse[...]` |

---

## Part II: Categorical Foundation

### 2.1 ChatSession as Coalgebra

A chat session is a **coalgebra** over the state functor:

```
ChatCoalgebra = (S, step : S → (Response × State))
```

The session state `S` is a **product** of:
- **Context**: The rendered conversation window (computed projection)
- **Turns**: The complete history (ground truth)
- **Resources**: Remaining conversation budget

This gives us the **Session = Context × Turns × Resources** isomorphism.

### 2.2 Composition Laws

Chat sessions must satisfy these categorical laws:

| Law | Statement | Meaning |
|-----|-----------|---------|
| **Identity** | `chat(id_msg) = id_session` | Empty message preserves session |
| **Associativity** | `(turn_1 >> turn_2) >> turn_3 = turn_1 >> (turn_2 >> turn_3)` | Turn ordering is associative |
| **Naturality** | `WorkingContext(f . g) = WorkingContext(f) . WorkingContext(g)` | Context projection is functorial |

**Verification**: These laws are verified via property-based tests in `impl/claude/protocols/agentese/chat/_tests/test_laws.py`.

### 2.3 WorkingContext as Functor

The Working Context is a **functor** mapping Session state to LLM input:

```
WorkingContext : Session → ContextWindow
```

**Functor Laws**:

1. **Identity Law**: `WorkingContext(id) = id`
   - If session unchanged, context unchanged

2. **Composition Law**: `WorkingContext(f . g) = WorkingContext(f) . WorkingContext(g)`
   - Sequential updates compose correctly

**Implementation**: This functor applies:
- Context strategy (sliding/summarize/Galois)
- Token budget constraints
- System prompt injection
- Memory recall injection

See §5 for concrete strategies.

### 2.4 Composition with Other Nodes

Chat nodes compose via standard AGENTESE composition:

**Sequential Composition**:
```
chatty(X) >> chatty(Y) = multi_turn_dialogue(X, Y)
```
- Turn from X feeds into Y's context
- Combined session tracks both entities

**Parallel Composition**:
```
chatty(X) ‖ chatty(Y) = concurrent_chats(X, Y)
```
- Independent sessions with shared observer
- No cross-contamination of context

**Nested Composition**:
```
chatty(chatty(X)) = meta_conversation(X)
```
- Outer chat discusses inner chat's content
- Enables reflection on dialogue itself

---

## Part III: Path Grammar

### 3.1 Universal Chat Affordances

Any node exposing chat provides these standard affordances:

```
<node_path>.chat.*
├── send[message="..."]      # Send message, get response (MUTATION)
├── stream[message="..."]    # Streaming response (MUTATION, streaming=true)
├── history                  # Get turn history (PERCEPTION)
├── turn                     # Current turn number (PERCEPTION)
├── context                  # Current context window (PERCEPTION)
├── metrics                  # Token counts, latency (PERCEPTION)
├── reset                    # Clear session (MUTATION)
├── fork                     # Create branch session (GENERATION)
└── merge[session_id="..."]  # Merge sessions (COMPOSITION)
```

### 3.2 Concrete Path Examples

```
# Soul chat (K-gent)
self.soul.chat.send[message="What should I focus on today?"]
self.soul.chat.history
self.soul.chat.context

# Town citizen chat
world.town.citizen.elara.chat.send[message="Hello"]
world.town.citizen.marcus.chat.history

# Generic agent chat
world.agent.advisor-1.chat.send[message="Review this plan"]

# Session management
self.flow.chat.manifest           # Active chat sessions
self.flow.chat.sessions           # List all sessions
self.flow.chat.session[id="abc"]  # Access specific session
```

### 3.3 Dimension Derivation

Chat aspects derive these dimensions (per AD-012):

| Aspect | Execution | Statefulness | Backend | Seriousness | Interactivity |
|--------|-----------|--------------|---------|-------------|---------------|
| `send` | async | stateful | llm | neutral | streaming |
| `stream` | async | stateful | llm | neutral | streaming |
| `history` | sync | stateful | pure | neutral | oneshot |
| `context` | sync | stateful | pure | neutral | oneshot |
| `reset` | async | stateful | pure | sensitive | oneshot |
| `fork` | async | stateful | pure | neutral | oneshot |

---

## Part IV: State Machine

### 4.1 Session States

```python
class ChatSessionState(Enum):
    DORMANT = "dormant"       # No active conversation
    READY = "ready"           # Session created, awaiting first message
    STREAMING = "streaming"   # Response in progress
    WAITING = "waiting"       # Awaiting user input
    DRAINING = "draining"     # Finalizing, no new input
    COLLAPSED = "collapsed"   # Session ended (resources depleted)
```

### 4.2 State Transitions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CHAT SESSION STATE MACHINE                            │
│                                                                              │
│                        ┌──────────────┐                                     │
│                        │   DORMANT    │                                     │
│                        └──────────────┘                                     │
│                               │                                              │
│                          create_session                                      │
│                               ▼                                              │
│                        ┌──────────────┐                                     │
│                        │    READY     │                                     │
│                        └──────────────┘                                     │
│                               │                                              │
│                          send_message                                        │
│                               ▼                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   WAITING    │◄───│  STREAMING   │───►│  DRAINING    │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘                  │
│          │                   │                   │                           │
│     send_message        interrupt          complete                          │
│          │                   │                   │                           │
│          └───────────────────┼───────────────────┘                           │
│                              ▼                                               │
│                       ┌──────────────┐                                      │
│                       │  COLLAPSED   │ (resources = 0 or max_turns)         │
│                       └──────────────┘                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Turn Protocol

Each turn follows this atomic protocol:

```python
@dataclass
class Turn:
    """A complete conversation turn."""
    turn_number: int
    user_message: Message
    assistant_response: Message
    started_at: datetime
    completed_at: datetime
    tokens_in: int
    tokens_out: int
    context_before: int  # Context size before this turn
    context_after: int   # Context size after (may differ due to compression)
    metadata: dict[str, Any]
```

The turn is **atomic**—it either completes fully or rolls back.

---

## Part V: Context Management

### 5.1 Hierarchical Memory Architecture

Following the **Sheaf pattern** (AD-006), context exists at three resolutions:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HIERARCHICAL CONTEXT ARCHITECTURE                       │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       SHORT-TERM (Working Context)                      │ │
│  │  • Recent turns verbatim                                                │ │
│  │  • Current token budget (configurable, default 8000)                    │ │
│  │  • Compression strategy applied                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                              compression                                     │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      MEDIUM-TERM (Session Summary)                      │ │
│  │  • Compressed summaries of earlier conversation                         │ │
│  │  • Key facts extracted                                                  │ │
│  │  • Updated on context overflow                                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                              crystallize                                     │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       LONG-TERM (D-gent Memory)                         │ │
│  │  • Persisted conversation crystals                                      │ │
│  │  • Semantic embeddings for recall                                       │ │
│  │  • Entity-specific memory (per citizen, per session)                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Context Strategies

```python
class ContextStrategy(Enum):
    SLIDING = "sliding"       # Drop oldest messages (lossy)
    SUMMARIZE = "summarize"   # Compress via LLM (lossy)
    FORGET = "forget"         # Hard truncate (lossy)
    GALOIS = "galois"         # Coherence-preserving (Generative Principle)
```

**CRITICAL**: kgents Generative Principle demands coherence-preserving compression.

### 5.3 Galois Compression (NEW)

To resolve the tension between "context window limits" and "semantic coherence", we introduce **Galois compression**:

```
L(compressed) ≤ L(original) + tolerance
```

Where `L` is the **semantic loss function**:
- Measures information loss during compression
- Tolerance is configurable (default: 0.05 bits)

**Implementation**: Uses Galois connection between full history and compressed context:

```
compress : Session → ContextWindow
expand   : ContextWindow → Session

Property: expand(compress(s)) ⊆ s  (retrieves subset of original)
```

**Verification**: Property-based tests ensure compression doesn't violate coherence.

See `impl/claude/protocols/agentese/chat/context.py` for implementation.

### 5.4 Working Context vs Ground Truth

**Critical distinction** (grounded in AD-015 Proxy Handles):

| Component | Purpose | Storage |
|-----------|---------|---------|
| **Session (Ground Truth)** | Complete turn history | D-gent memory |
| **Working Context (Proxy)** | Rendered context for LLM | Computed projection |

The Working Context is a **proxy handle** over the Session, not the Session itself.

### 5.5 Functor Composition

Context strategies compose via functor composition:

```
WorkingContext(GALOIS) . WorkingContext(SLIDING) = WorkingContext(GALOIS_SLIDING)
```

This enables **adaptive strategies** that switch based on session state.

---

## Part VI: Registration

### 6.1 The `@chatty` Decorator

Nodes expose chat capability via a composable decorator:

```python
@chatty(
    context_window=8000,
    context_strategy="galois",
    system_prompt_factory=None,  # Factory for personality-based prompts
    persist_history=True,
    memory_key=None,  # Auto-derived from node path
)
@logos.node("world.town.citizen")
class CitizenNode:
    """A town citizen that can converse."""
    ...
```

### 6.2 Chat Aspect Declarations

```python
@aspect(
    category=AspectCategory.MUTATION,
    effects=[
        Effect.CALLS("llm"),
        Effect.WRITES("chat_session"),
        Effect.CHARGES("tokens"),
    ],
    help="Send a message and receive a response",
    examples=["self.soul.chat.send[message='Hello']"],
    budget_estimate="medium",
    streaming=True,
)
async def send(self, observer: Observer, message: str) -> TurnResult:
    """Send a message through the chat session."""
    ...
```

---

## Part VII: Anti-Patterns

### 7.1 Compression Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Silent Truncation** | Drop context without warning | Emit warning when resources low |
| **Unbounded Context** | Never compress, exhaust budget | Apply strategy proactively |
| **Lossy Summarization** | LLM summaries lose key facts | Use Galois compression with verification |
| **Context Thrashing** | Compress/expand loop | Hysteresis threshold for compression |

### 7.2 State Management Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Dangling Sessions** | Sessions never collapse | Timeout + resource limits |
| **Orphan Turns** | Turns without sessions | Atomic turn protocol |
| **State Leakage** | Session state bleeds across observers | Session = f(observer_id, node_path) |

### 7.3 Composition Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Singleton Chat** | Only one session per node | Multi-session support |
| **Hard-Coded Personality** | Can't compose chat nodes | System prompt factory pattern |
| **Non-Composable Turns** | Turns can't feed into other agents | Turn as first-class value |

---

## Appendix A: Message Schema

```python
@dataclass
class Message:
    """A single message in the conversation."""
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens: int = 0  # Computed if not provided
    metadata: dict[str, Any] = field(default_factory=dict)
```

## Appendix B: Configuration Reference

```python
@dataclass
class ChatConfig:
    """Chat session configuration."""
    # Context management
    context_window: int = 8000
    context_strategy: Literal["sliding", "summarize", "forget", "galois"] = "galois"
    summarization_threshold: float = 0.8
    galois_tolerance: float = 0.05  # NEW: semantic loss tolerance

    # Turn limits
    turn_timeout: float = 60.0
    max_turns: int | None = None

    # System prompt
    system_prompt: str | None = None
    system_prompt_position: Literal["prepend", "inject"] = "prepend"

    # Interruption handling
    interruption_strategy: Literal["complete", "abort", "merge"] = "complete"

    # Persistence
    persist_history: bool = True
    memory_key: str | None = None

    # Memory injection
    inject_memories: bool = True
    memory_recall_limit: int = 5

    # Resources (renamed from Entropy)
    resource_budget: float = 1.0
    resource_decay_per_turn: float = 0.02
```

## Appendix C: Grounding Chain

This spec is grounded in the following kgents axioms:

```
L1 (Axioms)
├── Composable: Chat is a morphism
├── Generative: Galois compression preserves coherence
└── Ethical: Transparent resource limits

L2 (Categorical Ground)
├── PolyAgent: ChatSession is a coalgebra
└── Functor: WorkingContext satisfies functor laws

L3 (Specification)
└── This spec (chat.md)

L4 (Implementation)
└── impl/claude/protocols/agentese/chat/
```

**External Sources** (for patterns, not grounding):
- Google ADK: Session vs Working Context distinction
- Maxim AI: Hierarchical memory architecture
- PatternFly: Conversational UI patterns

These sources informed design but do **not** ground the spec. Grounding comes from kgents axioms.

---

## Appendix D: SessionResources Dataclass

Replaces ambiguous "entropy" with explicit resource tracking:

```python
@dataclass
class SessionResources:
    """Explicit session resource tracking."""
    token_budget_remaining: int      # Tokens left in context window
    turn_count: int                  # Current turn number
    max_turns: int | None            # Hard limit on turns
    estimated_cost_usd: float        # Running cost estimate
    time_elapsed: timedelta          # Session duration

    @property
    def is_depleted(self) -> bool:
        """Check if session has run out of resources."""
        if self.max_turns and self.turn_count >= self.max_turns:
            return True
        if self.token_budget_remaining <= 0:
            return True
        return False
```

---

*"The best conversation is the one where both participants become someone new."*

*Last updated: 2025-12-24*
