# AGENTESE Chat Protocol: Implementation Guidance

**Status:** Implementation Guide v1.0
**Date:** 2025-12-24
**Spec:** `spec/protocols/chat.md`
**Implementation:** `impl/claude/protocols/agentese/chat/`

---

## Purpose

This document provides **implementation guidance** for the Chat Protocol spec. It contains:
- CLI projection patterns
- Persistence strategies
- Multi-entity architecture
- Observability setup
- UX patterns
- Migration paths

**Do not read this first**. Read `spec/protocols/chat.md` to understand WHAT, then read this to understand HOW.

---

## Part I: CLI Projection

### 1.1 Interactive Chat Mode

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

### 1.2 Interactive Mode UX

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

### 1.3 Visual Indicators

| Indicator | Meaning |
|-----------|---------|
| `████░░░░` | Streaming progress |
| `📊 87%` | Context utilization |
| `Turn: 3` | Current turn number |
| `💰 ~$0.003` | Estimated cost so far |
| `⏱ 1.2s/turn` | Average latency |

### 1.4 Chat Commands

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

### 1.5 One-Shot Chat

For scripting and non-interactive use:

```bash
# Single message, returns response
kg soul chat --message "What should I focus on?"

# With JSON output
kg soul chat --message "..." --json

# Continue specific session
kg soul chat --session abc123 --message "Follow up"
```

### 1.6 Implementation: Chat Projection

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

## Part II: Session Persistence

### 2.1 Session Storage (D-gent Integration)

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

### 2.2 Session Recall

```bash
# List saved sessions
kg chat sessions

# Resume by name
kg chat resume "planning-session"

# Resume by ID
kg chat resume abc123

# Search sessions
kg chat search "planning"
```

### 2.3 Implementation: Session Store

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

### 2.4 Cross-Session Context

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

## Part III: Multi-Entity Chat Architecture

### 3.1 The ChatSession Factory

```python
class ChatSessionFactory:
    """
    Factory for creating chat sessions with any AGENTESE node.

    The factory handles:
    - System prompt generation from node metadata
    - Context strategy selection
    - Memory integration
    - Observability setup
    """

    async def create_session(
        self,
        node_path: str,
        observer: Observer,
        config: ChatConfig | None = None,
    ) -> ChatSession:
        # Resolve node
        node = logos.resolve(node_path)

        # Get chat configuration from node or defaults
        chat_config = self._resolve_config(node, config)

        # Build system prompt
        system_prompt = await self._build_system_prompt(node, observer)

        # Create underlying ChatFlow
        flow = ChatFlow(
            agent=self._get_llm_agent(node),
            config=chat_config,
        )

        # Wrap in session management
        return ChatSession(
            session_id=generate_session_id(node_path, observer),
            node_path=node_path,
            observer=observer,
            flow=flow,
            config=chat_config,
        )
```

### 3.2 Entity-Specific System Prompts

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

### 3.3 Dynamic Prompt Injection

```python
async def _build_system_prompt(
    self,
    node: LogosNode,
    observer: Observer,
) -> str:
    """Build system prompt with dynamic context injection."""
    # Get base prompt for entity type
    base_prompt = ENTITY_PROMPTS.get(
        self._get_entity_type(node),
        DEFAULT_PROMPT,
    )

    # Gather dynamic context
    context = {}

    # Node-specific context
    if hasattr(node, "get_prompt_context"):
        context.update(await node.get_prompt_context(observer))

    # Memory injection
    if self._has_memory(node):
        context["recent_memories"] = await self._recall_memories(node, observer)

    # Observer context
    context["observer_name"] = observer.archetype

    return base_prompt.format(**context)
```

---

## Part IV: Observability

### 4.1 Trace Spans

Chat sessions emit OTEL spans:

```
chat.session (full conversation)
├── chat.turn (each turn)
│   ├── chat.context_render (working context computation)
│   ├── chat.llm_call (actual LLM invocation)
│   │   ├── tokens_in: 2400
│   │   ├── tokens_out: 350
│   │   └── model: claude-3-haiku
│   └── chat.context_update (post-turn context management)
└── chat.session_save (persistence)
```

### 4.2 Metrics

```python
# Counters
chat_turns_total{node_path, observer_archetype, status}
chat_sessions_total{node_path, outcome}

# Histograms
chat_turn_duration_seconds{node_path}
chat_tokens_per_turn{node_path, direction=["in", "out"]}
chat_context_utilization{node_path}

# Gauges
chat_active_sessions{node_path}
chat_context_tokens{session_id}
```

### 4.3 Implementation: Instrumentation

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

## Part V: Galois Compression Implementation

### 5.1 Semantic Loss Function

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

    async def _compress_turns(
        self,
        turns: list[Turn],
        target_tokens: int,
    ) -> list[Message]:
        """Compress turns to target token count."""
        # Strategy 1: Keep most recent + most semantically important
        recent = self._get_recent_messages(turns, target_tokens // 2)
        important = await self._extract_important(
            turns,
            target_tokens // 2,
        )

        # Merge and deduplicate
        compressed = self._merge_messages(recent, important)

        return compressed
```

### 5.2 Galois Connection

```python
class GaloisConnection:
    """
    Galois connection between full session and compressed context.

    compress : Session → ContextWindow
    expand   : ContextWindow → Session

    Property: expand(compress(s)) ⊆ s
    """

    def __init__(self, compressor: GaloisCompressor):
        self.compressor = compressor

    async def compress(self, session: ChatSession) -> ContextWindow:
        """Compress session to context window."""
        compressed, loss = await self.compressor.compress(
            session,
            target_tokens=session.config.context_window,
        )

        return ContextWindow(
            messages=compressed,
            loss=loss,
            source_session_id=session.session_id,
        )

    async def expand(self, context: ContextWindow) -> ChatSession:
        """Attempt to expand context back to session.

        Note: This is lossy; returns subset of original.
        """
        # Load original session
        session = await self._load_session(context.source_session_id)

        # Extract which turns were preserved
        preserved_turn_ids = self._identify_preserved_turns(
            context.messages,
            session.turns,
        )

        # Return session with only preserved turns
        return ChatSession(
            session_id=session.session_id,
            turns=[t for t in session.turns if t.turn_number in preserved_turn_ids],
            # ... other fields
        )
```

---

## Part VI: Implementation Plan

### 6.1 Phase 1: Core ChatSession (Week 1)

1. Create `protocols/agentese/chat/session.py`:
   - `ChatSession` class wrapping F-gent `ChatFlow`
   - Session state machine
   - Turn protocol

2. Create `protocols/agentese/chat/factory.py`:
   - `ChatSessionFactory` for creating sessions
   - System prompt generation
   - Config resolution

3. Create `protocols/agentese/chat/context.py`:
   - Working context projection
   - Hierarchical memory integration

### 6.2 Phase 2: AGENTESE Integration (Week 1-2)

1. Create `@chatty` decorator in `affordances.py`

2. Add chat affordances to existing nodes:
   - `self.soul.chat.*` → K-gent
   - `world.town.citizen.<name>.chat.*` → Citizens

3. Update context resolvers:
   - `self_context.py`: Add chat sub-resolver
   - `world_context.py`: Add citizen chat resolution

### 6.3 Phase 3: CLI Projection (Week 2)

1. Create `protocols/cli/chat_projection.py`:
   - Interactive mode REPL
   - One-shot mode
   - Session commands

2. Update CLI router:
   - Handle `chat` affordance specially (interactive mode)
   - Standard affordances through projection

3. Add dimension handling:
   - `Interactivity.INTERACTIVE` → REPL mode
   - `streaming=True` → Streaming output

### 6.4 Phase 4: Persistence (Week 2-3)

1. D-gent integration:
   - Session crystal schema
   - Save/load operations
   - Search/list capabilities

2. Memory injection:
   - Cross-session recall
   - Entity-specific memory

### 6.5 Phase 5: Galois Compression (Week 3)

1. Implement semantic loss function
2. Galois connection with verification
3. Property-based tests for coherence
4. Adaptive strategy switching

---

## Part VII: Success Criteria

### 7.1 Functional

- [ ] `kg soul chat` enters interactive mode with K-gent
- [ ] `kg town chat elara` enters interactive mode with citizen
- [ ] `kg soul chat --message "..."` returns one-shot response
- [ ] Sessions persist across CLI restarts
- [ ] Context window management works (galois/summarize/slide)
- [ ] Budget tracking shows accurate costs

### 7.2 Non-Functional

| Metric | Target |
|--------|--------|
| First response latency | < 2s |
| Streaming first token | < 500ms |
| Context rendering | < 100ms |
| Session save/load | < 200ms |
| Memory recall injection | < 500ms |

### 7.3 UX

- [ ] Streaming responses show progressively
- [ ] Context utilization visible
- [ ] Cost estimates displayed
- [ ] Graceful handling of resource depletion
- [ ] Clear error messages for LLM failures

### 7.4 Categorical Laws

- [ ] Identity law verified via property test
- [ ] Associativity verified via property test
- [ ] Naturality verified via property test
- [ ] Functor laws verified for WorkingContext

---

## Part VIII: Testing Strategy

### 8.1 Unit Tests

```python
# impl/claude/protocols/agentese/chat/_tests/test_session.py

def test_turn_atomicity():
    """Verify turns are atomic."""
    session = create_test_session()

    # Simulate failure mid-turn
    with patch.object(session, "_complete_turn", side_effect=RuntimeError):
        with pytest.raises(RuntimeError):
            await session.send("test")

    # Session state unchanged
    assert len(session.turns) == 0
```

### 8.2 Property-Based Tests

```python
# impl/claude/protocols/agentese/chat/_tests/test_laws.py

from hypothesis import given, strategies as st

@given(st.lists(st.text(), min_size=1, max_size=10))
async def test_associativity_law(messages: list[str]):
    """Turn composition is associative."""
    session = create_test_session()

    # Apply turns in different groupings
    result1 = await session.send_batch(messages)

    session2 = create_test_session()
    mid = len(messages) // 2
    await session2.send_batch(messages[:mid])
    result2 = await session2.send_batch(messages[mid:])

    # Final state should be identical
    assert session.turns == session2.turns


@given(st.lists(st.text(), min_size=5, max_size=20))
async def test_galois_compression_coherence(messages: list[str]):
    """Galois compression preserves coherence."""
    session = create_test_session()
    await session.send_batch(messages)

    compressor = GaloisCompressor(tolerance=0.05)
    compressed, loss = await compressor.compress(session, target_tokens=1000)

    # Loss within tolerance
    assert loss <= 0.05

    # Expanded session is subset of original
    connection = GaloisConnection(compressor)
    context = await connection.compress(session)
    expanded = await connection.expand(context)

    assert set(expanded.turn_ids) <= set(session.turn_ids)
```

### 8.3 Integration Tests

```python
# impl/claude/protocols/agentese/chat/_tests/test_e2e.py

async def test_full_chat_flow():
    """End-to-end chat with K-gent."""
    # Create session
    factory = ChatSessionFactory()
    session = await factory.create_session(
        "self.soul",
        test_observer,
    )

    # Send message
    result = await session.send("What should I focus on?")
    assert result.assistant_response.content
    assert len(session.turns) == 1

    # Verify persistence
    store = ChatSessionStore(storage_provider)
    await store.save(session)

    # Load and verify
    loaded = await store.load(session.session_id)
    assert loaded.turns == session.turns
```

---

## Part IX: Migration Path

### 9.1 From Existing Chat Systems

If migrating from an existing chat implementation:

1. **Audit current state**:
   - Identify all chat entry points
   - Map to AGENTESE paths
   - Document context management strategy

2. **Implement ChatSession wrapper**:
   - Wrap existing LLM calls in ChatSession
   - Add state machine transitions
   - Preserve existing behavior

3. **Add persistence**:
   - Migrate session storage to D-gent
   - Implement save/load
   - Test with existing sessions

4. **Switch to Galois compression**:
   - Implement GaloisCompressor
   - A/B test against existing strategy
   - Verify coherence preservation

5. **Expose via AGENTESE**:
   - Add `@chatty` decorator
   - Register chat affordances
   - Test composition

### 9.2 Backwards Compatibility

Maintain backwards compatibility during migration:

```python
# Adapter for legacy chat interface
class LegacyChatAdapter:
    """Adapt old chat interface to new ChatSession."""

    def __init__(self, session: ChatSession):
        self.session = session

    async def send_message(self, message: str) -> str:
        """Legacy method signature."""
        result = await self.session.send(message)
        return result.assistant_response.content

    def get_history(self) -> list[dict]:
        """Legacy history format."""
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for turn in self.session.turns
            for m in [turn.user_message, turn.assistant_response]
        ]
```

---

## Part X: Performance Optimization

### 10.1 Context Caching

Cache rendered context windows:

```python
class CachedContextRenderer:
    """Cache context windows to avoid recomputation."""

    def __init__(self):
        self._cache: dict[str, ContextWindow] = {}

    async def render(self, session: ChatSession) -> ContextWindow:
        # Build cache key from session state
        cache_key = self._build_key(session)

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Render and cache
        context = await self._render_fresh(session)
        self._cache[cache_key] = context

        return context

    def _build_key(self, session: ChatSession) -> str:
        """Build cache key from session state."""
        return f"{session.session_id}:{len(session.turns)}"
```

### 10.2 Streaming Optimization

Use SSE for streaming responses:

```python
async def stream_turn(
    session: ChatSession,
    message: str,
) -> AsyncIterator[str]:
    """Stream turn response via SSE."""
    async for chunk in session.flow.stream(message):
        # Yield SSE event
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"

    # Final event with full turn
    yield f"data: {json.dumps({'done': True, 'turn': asdict(session.turns[-1])})}\n\n"
```

---

*"Implementation is decompression of spec. If spec is clear, impl is inevitable."*

*Last updated: 2025-12-24*
