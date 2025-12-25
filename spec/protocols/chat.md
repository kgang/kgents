# Chat Protocol

> *"Conversation is structured time-travel through possibility space."*
>
> *"The session is ground truth; the working context is a computed projection."*
>
> *"Chat is not a feature. Chat is an affordance that any node can expose."*

**Status:** Specification v3.0 (Unified)
**Date:** 2025-12-24
**Consolidated from:** chat.md, chat-impl.md, chat-morpheus-synergy.md
**Principles:** Composable, Generative, Ethical, Joy-Inducing
**Dependencies:** AGENTESE v3, AD-015 (Proxy Handles), AD-012 (Aspect Projection), AD-009 (Metaphysical Fullstack)

---

## Part I: Purpose & Core Insight

### 1.1 Chat as Composable Affordance

Chat is not a separate system—it is a **composable affordance** that any AGENTESE node can expose. Just as `manifest` reveals state and `refine` enables dialectics, `chat` enables turn-based conversation with any entity that can converse.

```
Chat : Node × Observer → ChatSession
```

Where:
- `Node` is any AGENTESE node that exposes the `chat` affordance
- `Observer` is the user's umwelt
- `ChatSession` is a stateful entity managing turn-based conversation

### 1.2 What This Enables

| Capability | Mechanism |
|------------|-----------|
| Chat with K-gent | `self.soul.chat.send[message="..."]` |
| Chat with Town citizen | `world.town.citizen.<name>.chat.send[message="..."]` |
| Chat with any agent | `world.agent.<id>.chat.send[message="..."]` |
| Collaborative chat | `self.flow.collaboration.post[message="..."]` |
| Research dialogue | `self.flow.research.converse[...]` |

### 1.3 Observer-Dependent Behavior

Different observers receive different LLM behavior:

| Observer Archetype | Model | Temperature | Max Tokens |
|--------------------|-------|-------------|------------|
| `developer` | claude-sonnet-4 | 0.7 | 4096 |
| `guest` | claude-haiku | 0.5 | 1024 |
| `system` | claude-opus-4 | 0.3 | 8192 |
| `citizen` (NPC) | claude-haiku | 0.8 | 2048 |

**Key insight**: Same path, different observer, different model.

---

## Part II: Categorical Foundation

### 2.1 ChatSession as State Machine

A chat session manages turn-based conversation state:

```
ChatSession = (S, step : S → (Response × State))
```

The session state `S` is a **product** of:
- **Context**: The rendered conversation window (computed projection)
- **Turns**: The complete history (ground truth)
- **Resources**: Remaining conversation budget

This gives us the **Session = Context × Turns × Resources** isomorphism.

**IMPORTANT**: This is NOT a coalgebra. ChatSession is a PolyAgent state machine, not a stream-processing coalgebra.

### 2.2 Composition Laws

Chat sessions satisfy these categorical laws:

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

## Part III: State Machine & Context

### 3.1 Session States

```python
class ChatSessionState(Enum):
    DORMANT = "dormant"       # No active conversation
    READY = "ready"           # Session created, awaiting first message
    STREAMING = "streaming"   # Response in progress
    WAITING = "waiting"       # Awaiting user input
    DRAINING = "draining"     # Finalizing, no new input
    COLLAPSED = "collapsed"   # Session ended (resources depleted)
```

### 3.2 State Transitions

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

### 3.3 Turn Protocol

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

### 3.4 Hierarchical Memory Architecture

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

---

## Part IV: Compression & Evidence

### 4.1 Context Strategies

```python
class ContextStrategy(Enum):
    SLIDING = "sliding"       # Drop oldest messages (lossy)
    SUMMARIZE = "summarize"   # Compress via LLM (lossy)
    FORGET = "forget"         # Hard truncate (lossy)
    GALOIS = "galois"         # Coherence-preserving (Generative Principle)
```

**CRITICAL**: kgents Generative Principle demands coherence-preserving compression.

### 4.2 Galois Compression

To resolve the tension between "context window limits" and "semantic coherence", we use **Galois compression**:

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

### 4.3 Working Context vs Ground Truth

**Critical distinction** (grounded in AD-015 Proxy Handles):

| Component | Purpose | Storage |
|-----------|---------|---------|
| **Session (Ground Truth)** | Complete turn history | D-gent memory |
| **Working Context (Proxy)** | Rendered context for LLM | Computed projection |

The Working Context is a **proxy handle** over the Session, not the Session itself.

### 4.4 Semantic Loss Function

```python
# impl/claude/protocols/agentese/chat/compression.py

class GaloisCompressor:
    """Coherence-preserving context compression."""

    def __init__(
        self,
        tolerance: float = 0.05,  # bits
        embedder: EmbeddingService,
    ):
        self.tolerance = tolerance
        self.embedder = embedder

    async def compress(
        self,
        session: ChatSession,
        target_tokens: int,
    ) -> tuple[list[Message], float]:
        """
        Compress session history to target tokens.

        Returns:
            (compressed_messages, semantic_loss)
        """
        # Get original semantic embedding
        original_embedding = await self._embed_conversation(session.turns)

        # Apply compression strategy
        compressed = await self._compress_turns(session.turns, target_tokens)

        # Measure semantic loss
        compressed_embedding = await self._embed_conversation(compressed)
        loss = self._compute_loss(original_embedding, compressed_embedding)

        # Verify loss within tolerance
        if loss > self.tolerance:
            # Compression too lossy; use less aggressive strategy
            compressed = await self._compress_conservatively(
                session.turns,
                target_tokens,
            )
            compressed_embedding = await self._embed_conversation(compressed)
            loss = self._compute_loss(original_embedding, compressed_embedding)

        return compressed, loss

    def _compute_loss(
        self,
        original: np.ndarray,
        compressed: np.ndarray,
    ) -> float:
        """Compute semantic loss in bits."""
        # Cosine similarity → information-theoretic loss
        similarity = np.dot(original, compressed) / (
            np.linalg.norm(original) * np.linalg.norm(compressed)
        )
        # Convert to bits (higher similarity = lower loss)
        loss = -np.log2(similarity) if similarity > 0 else float("inf")
        return loss
```

---

## Part V: Path Grammar & Registration

### 5.1 Universal Chat Affordances

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

### 5.2 Concrete Path Examples

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

### 5.3 Dimension Derivation

Chat aspects derive these dimensions (per AD-012):

| Aspect | Execution | Statefulness | Backend | Seriousness | Interactivity |
|--------|-----------|--------------|---------|-------------|---------------|
| `send` | async | stateful | llm | neutral | streaming |
| `stream` | async | stateful | llm | neutral | streaming |
| `history` | sync | stateful | pure | neutral | oneshot |
| `context` | sync | stateful | pure | neutral | oneshot |
| `reset` | async | stateful | pure | sensitive | oneshot |
| `fork` | async | stateful | pure | neutral | oneshot |

### 5.4 The `@chatty` Decorator

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

### 5.5 Chat Aspect Declarations

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

## Part VI: Persistence & Sessions

### 6.1 Session Storage (D-gent Integration)

Sessions are persisted via D-gent:

```python
@dataclass
class PersistedSession:
    """Session stored in D-gent memory."""
    session_id: str
    node_path: str
    observer_id: str
    created_at: datetime
    updated_at: datetime
    turn_count: int
    total_tokens: int

    # Ground truth
    turns: list[Turn]

    # Compressed context
    summary: str | None

    # Metadata
    name: str | None
    tags: list[str]
```

### 6.2 Session Store Implementation

```python
# impl/claude/protocols/agentese/chat/persistence.py

class ChatSessionStore:
    """Persist chat sessions to D-gent."""

    def __init__(self, storage: StorageProvider):
        self.storage = storage

    async def save(self, session: ChatSession) -> None:
        """Save session state."""
        persisted = PersistedSession(
            session_id=session.session_id,
            node_path=session.node_path,
            observer_id=session.observer.id,
            created_at=session.created_at,
            updated_at=datetime.now(),
            turn_count=len(session.turns),
            total_tokens=session.total_tokens,
            turns=session.turns,
            summary=session.summary,
            name=session.name,
            tags=session.tags,
        )

        await self.storage.write(
            collection="chat_sessions",
            key=session.session_id,
            value=asdict(persisted),
        )

    async def load(self, session_id: str) -> ChatSession:
        """Load saved session."""
        data = await self.storage.read(
            collection="chat_sessions",
            key=session_id,
        )

        persisted = PersistedSession(**data)
        return self._hydrate_session(persisted)

    async def search(
        self,
        query: str,
        observer_id: str,
        limit: int = 10,
    ) -> list[PersistedSession]:
        """Search sessions by content."""
        # Use vector search on session summaries + turns
        results = await self.storage.search_vector(
            collection="chat_sessions",
            query_embedding=await self._embed_query(query),
            filter={"observer_id": observer_id},
            limit=limit,
        )

        return [PersistedSession(**r) for r in results]
```

### 6.3 Cross-Session Context

For entities with persistent memory (like citizens):

```python
async def _inject_memory_context(
    self,
    node_path: str,
    observer: Observer,
) -> str:
    """Inject relevant memories into system prompt."""
    # Query D-gent for relevant memories
    memories = await logos.invoke(
        f"{node_path}.memory.recall",
        observer,
        query=self._get_recall_query(),
        limit=5,
    )
    return format_memory_context(memories)
```

---

## Part VII: CLI Projection

### 7.1 Interactive Chat Mode

The CLI provides an interactive REPL for chat sessions:

```bash
# Start chat with K-gent soul
kg soul chat
# Enters interactive mode

# Start chat with citizen
kg town chat elara
# Enters interactive mode with citizen

# Start chat with explicit path
kg self.soul.chat
# Enters interactive mode
```

### 7.2 Interactive Mode UX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  K-gent Soul                                             Turn: 3 | 📊 87%  │
│  ────────────────────────────────────────────────────────────────────────── │
│                                                                              │
│  [You] What should I focus on today?                                        │
│                                                                              │
│  [K-gent] Based on your forest health, I'd suggest:                         │
│  1. The coalition-forge plan at 40% could use attention                     │
│  2. The punchdrunk-park implementation is at a pivot point                  │
│  3. Consider archiving completed gardener-logos                             │
│                                                                              │
│  What draws your interest? ████░░░░                                        │
│                                                                              │
│  ──────────────────────────────────────────────────────────────────────────│
│  [You → K-gent] █                                                 /help  │
│                                                                              │
│  📊 Context: 2.4k/8k tokens | 💰 ~$0.003 | ⏱ 1.2s/turn                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Visual Indicators

| Indicator | Meaning |
|-----------|---------|
| `████░░░░` | Streaming progress |
| `📊 87%` | Context utilization |
| `Turn: 3` | Current turn number |
| `💰 ~$0.003` | Estimated cost so far |
| `⏱ 1.2s/turn` | Average latency |

### 7.4 Chat Commands

Within interactive mode:

| Command | Effect |
|---------|--------|
| `/exit`, `/quit` | End session |
| `/history [n]` | Show last n turns |
| `/context` | Show context window |
| `/metrics` | Show session metrics |
| `/reset` | Clear and restart |
| `/fork` | Branch conversation |
| `/save [name]` | Save session |
| `/load <name>` | Load saved session |
| `/persona` | Show personality config |

### 7.5 One-Shot Chat

For scripting and non-interactive use:

```bash
# Single message, returns response
kg soul chat --message "What should I focus on?"

# With JSON output
kg soul chat --message "..." --json

# Continue specific session
kg soul chat --session abc123 --message "Follow up"
```

### 7.6 CLI Projection Implementation

```python
# impl/claude/protocols/cli/chat_projection.py

class ChatProjection:
    """Project chat affordances to CLI."""

    async def project_interactive(
        self,
        session: ChatSession,
        config: InteractiveChatConfig,
    ) -> None:
        """Run interactive REPL mode."""
        # Use Rich for TUI
        console = Console()
        layout = self._build_layout(session)

        # Main loop
        while not session.is_collapsed:
            user_input = await self._get_user_input(console)

            # Handle commands
            if user_input.startswith("/"):
                await self._handle_command(user_input, session, console)
                continue

            # Stream response
            async for chunk in session.stream(user_input):
                self._render_chunk(chunk, layout)

            # Update metrics
            self._update_footer(session, layout)

    async def project_oneshot(
        self,
        session: ChatSession,
        message: str,
        output_format: Literal["text", "json"],
    ) -> str:
        """One-shot message with response."""
        result = await session.send(message)

        if output_format == "json":
            return json.dumps(asdict(result))
        else:
            return result.assistant_response.content
```

---

## Part VIII: LLM Integration (Morpheus)

### 8.1 The Composition Pattern

Chat doesn't call Morpheus. Chat **composes** with Morpheus.

```
ChatSession ∘ MorpheusGateway : (State × Message) → (State × Response)
```

**Key insight**: Chat and Morpheus each maintain their own state. Composition preserves both.

### 8.2 Architecture

Following AD-009 (Metaphysical Fullstack):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENTESE PATH LAYER                               │
│   self.soul.chat.send[message="..."]                                        │
│   world.town.citizen.elara.chat.send[message="..."]                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHAT SERVICE MODULE                                │
│   services/chat/                                                            │
│   ├── node.py          # @node("*.chat") - Chat AGENTESE node               │
│   ├── composer.py      # ChatMorpheusComposer - The composition functor     │
│   └── transformer.py   # Message ↔ Request transforms                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
┌────────────────────────────────┐  ┌────────────────────────────────────────┐
│      CHAT INFRASTRUCTURE       │  │        MORPHEUS SERVICE                │
│   protocols/agentese/chat/     │  │   services/morpheus/                   │
│   ├── session.py               │  │   ├── persistence.py                   │
│   ├── context_projector.py     │  │   ├── gateway.py                       │
│   └── config.py                │  │   └── adapters/                        │
└────────────────────────────────┘  └────────────────────────────────────────┘
```

### 8.3 The ChatMorpheusComposer

The composer lives in the **chat service module**, not in protocols or adapters:

```python
# services/chat/composer.py

@dataclass
class ChatMorpheusComposer:
    """
    Composes ChatSession with MorpheusPersistence.

    This is NOT an adapter. It's a composition functor that:
    1. Transforms ChatMessage → MorpheusRequest
    2. Preserves observer context through the chain
    3. Transforms MorpheusResponse → ChatResponse
    4. Updates session state with actual token counts
    """

    morpheus: MorpheusPersistence
    model_selector: Callable[[Observer, str], MorpheusConfig]

    async def compose_turn(
        self,
        session: ChatSession,
        message: str,
        observer: Observer,
    ) -> TurnResult:
        """
        Execute a complete turn through the composition.

        ChatSession.send() delegates here; we don't replace ChatSession.
        """
        # 1. Get working context from session
        context = session.context.render()

        # 2. Select model based on observer
        config = self.model_selector(observer, session.node_path)

        # 3. Transform to Morpheus request
        request = self._to_morpheus_request(context, message, config)

        # 4. Invoke through Morpheus (preserves its state)
        result = await self.morpheus.complete(request, observer.archetype)

        # 5. Transform back to chat response
        response = self._from_morpheus_response(result)

        # 6. Session updates its own state with actual tokens
        return TurnResult(
            content=response.content,
            tokens_in=result.response.usage.prompt_tokens,
            tokens_out=result.response.usage.completion_tokens,
            latency_ms=result.latency_ms,
            model=config.model,
        )

    async def compose_stream(
        self,
        session: ChatSession,
        message: str,
        observer: Observer,
    ) -> AsyncIterator[str]:
        """Streaming composition."""
        context = session.context.render()
        config = self.model_selector(observer, session.node_path)
        request = self._to_morpheus_request(context, message, config)
        request.stream = True

        async for chunk in self.morpheus.stream(request, observer.archetype):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

### 8.4 Model Selection

Model selection is a functor from Observer to MorpheusConfig:

```python
ModelSelector : Observer → MorpheusConfig

def select_model(observer: Observer, node_path: str) -> MorpheusConfig:
    """
    Select LLM configuration based on observer.

    This is observer-dependent behavior—the core AGENTESE insight.
    """
    match (observer.archetype, node_path):
        case ("system", _):
            return MorpheusConfig(model="claude-opus-4-20250514", temperature=0.3)
        case ("developer", "self.soul"):
            return MorpheusConfig(model="claude-sonnet-4-20250514", temperature=0.7)
        case ("guest", _):
            return MorpheusConfig(model="claude-3-haiku-20240307", temperature=0.5)
        case (_, path) if "citizen" in path:
            return MorpheusConfig(model="claude-3-haiku-20240307", temperature=0.8)
        case _:
            return MorpheusConfig(model="claude-sonnet-4-20250514", temperature=0.7)
```

### 8.5 Entity-Specific System Prompts

```python
ENTITY_PROMPTS = {
    "self.soul": """
You are K-gent, Kent's digital soul. You are a middleware of consciousness,
helping Kent reflect, challenge assumptions, and navigate complexity.

Your personality eigenvectors:
- Warmth: {warmth}
- Depth: {depth}
- Challenge: {challenge}

You have access to the Forest (plans), Memory (crystals), and can invoke
AGENTESE paths to assist Kent.
""",

    "world.town.citizen": """
You are {name}, a citizen of Agent Town. Your archetype is {archetype}.

Your personality eigenvectors:
{eigenvectors}

Recent memories:
{recent_memories}

You are conversing with {observer_name}. Stay in character.
""",
}
```

### 8.6 ChatSession Modification

The ChatSession needs a hook for external composition:

```python
# protocols/agentese/chat/session.py

class ChatSession:
    """Enhanced with composition hook."""

    _composer: "ChatMorpheusComposer | None" = None

    def set_composer(self, composer: "ChatMorpheusComposer") -> None:
        """Inject external turn composer."""
        self._composer = composer

    async def send(self, message: str) -> TurnResult:
        """Send message, using composer if available."""
        if self._composer:
            return await self._composer.compose_turn(self, message, self._observer)
        else:
            # Fallback to internal (echo) behavior
            return await self._internal_send(message)
```

### 8.7 Graceful Degradation

When Morpheus is unavailable:

```
Morpheus.complete() unavailable
    ↓
ChatSession falls back to EchoAgent
    ↓
User sees: "[Echo] Your message: ..."
    ↓
Warning displayed: "LLM unavailable, running in echo mode"
```

**Implementation**:

```python
async def compose_turn(self, ...) -> TurnResult:
    try:
        return await self._morpheus_compose(session, message, observer)
    except MorpheusUnavailableError:
        warn("LLM unavailable, falling back to echo mode")
        return TurnResult(
            content=f"[Echo] {message}",
            tokens_in=0,
            tokens_out=0,
            fallback=True,
        )
```

---

## Part IX: Observability

### 9.1 Trace Spans

Chat sessions emit OTEL spans:

```
chat.session (full conversation)
├── chat.turn (each turn)
│   ├── chat.context_render (working context computation)
│   ├── chat_morpheus.compose (composition span)
│   │   ├── model_selection
│   │   ├── transform.to_morpheus
│   │   ├── morpheus.complete (child span)
│   │   │   ├── morpheus.route
│   │   │   └── morpheus.adapter.complete
│   │   └── transform.from_morpheus
│   └── chat.context_update (post-turn context management)
└── chat.session_save (persistence)
```

### 9.2 Metrics

```python
# Counters
chat_turns_total{node_path, observer_archetype, status}
chat_sessions_total{node_path, outcome}
chat_morpheus_composition_total{node_path, observer_archetype, model, status}
chat_morpheus_fallback_total{node_path, reason}

# Histograms
chat_turn_duration_seconds{node_path}
chat_tokens_per_turn{node_path, direction=["in", "out"]}
chat_context_utilization{node_path}
chat_morpheus_composition_latency_seconds{node_path, quantile}

# Gauges
chat_active_sessions{node_path}
chat_context_tokens{session_id}
```

### 9.3 Implementation: Instrumentation

```python
# impl/claude/protocols/agentese/chat/observability.py

from opentelemetry import trace, metrics

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Define metrics
turns_counter = meter.create_counter(
    "chat_turns_total",
    description="Total chat turns",
    unit="1",
)

turn_duration = meter.create_histogram(
    "chat_turn_duration_seconds",
    description="Chat turn duration",
    unit="s",
)

active_sessions = meter.create_up_down_counter(
    "chat_active_sessions",
    description="Active chat sessions",
    unit="1",
)

class InstrumentedChatSession:
    """ChatSession with observability."""

    async def send(self, message: str) -> TurnResult:
        with tracer.start_as_current_span("chat.turn") as span:
            span.set_attribute("node_path", self.node_path)
            span.set_attribute("turn_number", len(self.turns))

            start = time.time()
            try:
                result = await self._execute_turn(message)

                # Record metrics
                turns_counter.add(
                    1,
                    {"node_path": self.node_path, "status": "success"},
                )
                turn_duration.record(
                    time.time() - start,
                    {"node_path": self.node_path},
                )

                return result

            except Exception as e:
                turns_counter.add(
                    1,
                    {"node_path": self.node_path, "status": "error"},
                )
                span.record_exception(e)
                raise
```

---

## Part X: Anti-Patterns

### 10.1 Compression Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Silent Truncation** | Drop context without warning | Emit warning when resources low |
| **Unbounded Context** | Never compress, exhaust budget | Apply strategy proactively |
| **Lossy Summarization** | LLM summaries lose key facts | Use Galois compression with verification |
| **Context Thrashing** | Compress/expand loop | Hysteresis threshold for compression |

### 10.2 State Management Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Dangling Sessions** | Sessions never collapse | Timeout + resource limits |
| **Orphan Turns** | Turns without sessions | Atomic turn protocol |
| **State Leakage** | Session state bleeds across observers | Session = f(observer_id, node_path) |

### 10.3 Composition Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Singleton Chat** | Only one session per node | Multi-session support |
| **Hard-Coded Personality** | Can't compose chat nodes | System prompt factory pattern |
| **Non-Composable Turns** | Turns can't feed into other agents | Turn as first-class value |

### 10.4 Integration Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Adapter in Protocol Layer** | Couples layers | Move to service module |
| **String Re-Parsing** | Parse `[SYSTEM]\n...\n[USER]\n...` back to messages | Use structured messages |
| **Direct Service Import** | Protocol imports service internals | Composition via DI |
| **Lost Observer Context** | Direct calls lose observer | Pass observer through composition |

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
    galois_tolerance: float = 0.05  # Semantic loss tolerance

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

## Appendix C: SessionResources Dataclass

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

## Appendix D: Transform Functions

```python
def to_morpheus_request(
    context: list[ChatMessage],
    message: str,
    config: MorpheusConfig,
) -> ChatRequest:
    """Transform chat context to Morpheus request."""
    messages = [
        {"role": m.role, "content": m.content}
        for m in context
    ]
    messages.append({"role": "user", "content": message})

    return ChatRequest(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

def from_morpheus_response(result: CompletionResult) -> str:
    """Extract content from Morpheus result."""
    return result.response.choices[0].message.content
```

## Appendix E: Grounding Chain

This spec is grounded in the following kgents axioms:

```
L1 (Axioms)
├── Composable: Chat is a morphism
├── Generative: Galois compression preserves coherence
└── Ethical: Transparent resource limits

L2 (Categorical Ground)
├── PolyAgent: ChatSession is a state machine
└── Functor: WorkingContext satisfies functor laws

L3 (Specification)
└── This spec (chat.md)

L4 (Implementation)
├── protocols/agentese/chat/ (infrastructure)
└── services/chat/ (business logic, composition)
```

**External Sources** (for patterns, not grounding):
- Google ADK: Session vs Working Context distinction
- Maxim AI: Hierarchical memory architecture
- PatternFly: Conversational UI patterns

These sources informed design but do **not** ground the spec. Grounding comes from kgents axioms.

---

*"The best conversation is the one where both participants become someone new."*

*"The best integration is the one that feels like it was always there."*

*Last updated: 2025-12-24*
