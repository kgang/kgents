# AGENTESE Chat Protocol: Conversational Affordances

**Status:** Specification v1.0
**Date:** 2025-12-17
**Dependencies:** AGENTESE v3, F-gent Flow, CLI Isomorphic Migration

---

## Epigraph

> *"A conversation is not an exchange of nouns. It is the meeting of two rates of change."*
>
> *"The Session is ground truth; the Working Context is a computed projection."* — Google ADK
>
> *"Chat is not a feature. Chat is an affordance that any node can expose."*

---

## Part I: Design Philosophy

### 1.1 The Core Insight

Chat is not a separate system—it is a **composable affordance** that any AGENTESE node can expose. Just as `manifest` reveals state and `refine` enables dialectics, `chat` enables turn-based conversation with any entity that can converse.

```
Chat : Node × Observer → ChatSession
```

Where:
- `Node` is any AGENTESE node that exposes the `chat` affordance
- `Observer` is the user's umwelt
- `ChatSession` is a stateful coalgebra: `State → (Response × State)`

### 1.2 Categorical Foundation

A chat session is a **coalgebra** over the state functor:

```
ChatCoalgebra = (S, step : S → (Response × S))
```

The session state `S` is a **product** of:
- **Context**: The rendered conversation window
- **Turns**: The complete history (ground truth)
- **Entropy**: Remaining conversation budget

This gives us the **Session = Context × Turns × Entropy** isomorphism.

### 1.3 What This Enables

| Capability | Mechanism |
|------------|-----------|
| Chat with K-gent | `self.soul.chat.send[message="..."]` |
| Chat with Town citizen | `world.town.citizen.<name>.chat.send[message="..."]` |
| Chat with any agent | `world.agent.<id>.chat.send[message="..."]` |
| Collaborative chat | `self.flow.collaboration.post[message="..."]` |
| Research dialogue | `self.flow.research.converse[...]` |

---

## Part II: Path Grammar

### 2.1 Universal Chat Affordances

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

### 2.2 Concrete Path Examples

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

### 2.3 Session Identification

Sessions are identified by:
```
session_id = hash(observer.id, node_path, created_at)
```

Sessions can be:
- **Ephemeral**: Live only during CLI session
- **Persistent**: Saved to D-gent memory
- **Named**: User-assigned names for recall

---

## Part III: The ChatSession State Machine

### 3.1 Session States (F-gent Flow Integration)

```python
class ChatSessionState(Enum):
    DORMANT = "dormant"       # No active conversation
    READY = "ready"           # Session created, awaiting first message
    STREAMING = "streaming"   # Response in progress
    WAITING = "waiting"       # Awaiting user input
    DRAINING = "draining"     # Finalizing, no new input
    COLLAPSED = "collapsed"   # Session ended (entropy depleted)
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
│                       │  COLLAPSED   │ (entropy = 0 or max_turns)           │
│                       └──────────────┘                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 The Turn Protocol

Each turn follows this protocol:

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

## Part IV: Context Window Management

### 4.1 The Hierarchical Memory Architecture

Following best practices from [Google ADK](https://google.github.io/adk-docs/sessions/) and [Maxim AI](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HIERARCHICAL CONTEXT ARCHITECTURE                       │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       SHORT-TERM (Working Context)                      │ │
│  │  • Recent turns verbatim                                                │ │
│  │  • Current token budget (configurable, default 8000)                    │ │
│  │  • Sliding or summarizing strategy                                      │ │
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

### 4.2 Context Strategies

```python
class ContextStrategy(Enum):
    SLIDING = "sliding"       # Drop oldest messages
    SUMMARIZE = "summarize"   # Compress via LLM
    FORGET = "forget"         # Hard truncate, no memory
    HYBRID = "hybrid"         # Sliding + periodic summary
```

### 4.3 Working Context vs Ground Truth

**Critical distinction** (from [Google ADK](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)):

| Component | Purpose | Storage |
|-----------|---------|---------|
| **Session (Ground Truth)** | Complete turn history | D-gent memory |
| **Working Context (View)** | Rendered context for LLM | Computed projection |

The Working Context is a **functor** over the Session:

```
WorkingContext : Session → ContextWindow
```

This functor applies:
1. Context strategy (sliding/summarize)
2. Token budget constraints
3. System prompt injection
4. Memory recall injection

---

## Part V: AGENTESE Registration

### 5.1 The `@chatty` Decorator

Nodes expose chat capability via a composable decorator:

```python
@chatty(
    context_window=8000,
    context_strategy="summarize",
    system_prompt_factory=None,  # Factory for personality-based prompts
    persist_history=True,
    memory_key=None,  # Auto-derived from node path
)
@logos.node("world.town.citizen")
class CitizenNode:
    """A town citizen that can converse."""

    # Existing aspects...

    # Chat affordances are auto-generated by @chatty:
    # - self.chat.send
    # - self.chat.history
    # - etc.
```

### 5.2 Chat Aspect Declarations

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

### 5.3 Dimension Derivation for Chat

Chat aspects derive these dimensions:

| Aspect | Execution | Statefulness | Backend | Seriousness | Interactivity |
|--------|-----------|--------------|---------|-------------|---------------|
| `send` | async | stateful | llm | neutral | streaming |
| `stream` | async | stateful | llm | neutral | streaming |
| `history` | sync | stateful | pure | neutral | oneshot |
| `context` | sync | stateful | pure | neutral | oneshot |
| `reset` | async | stateful | pure | sensitive | oneshot |
| `fork` | async | stateful | pure | neutral | oneshot |

---

## Part VI: CLI Projection

### 6.1 Interactive Chat Mode

The CLI provides an interactive REPL for chat sessions:

```bash
# Start chat with K-gent soul
kg soul chat
# → Enters interactive mode

# Start chat with citizen
kg town chat elara
# → Enters interactive mode with citizen

# Start chat with explicit path
kg self.soul.chat
# → Enters interactive mode
```

### 6.2 Interactive Mode UX

Following [best practices](https://www.patternfly.org/patternfly-ai/conversation-design/) for conversational UI:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🧠 K-gent Soul                                          Turn: 3 │ 📊 87%  │
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
│  📊 Context: 2.4k/8k tokens │ 💰 ~$0.003 │ ⏱ 1.2s/turn                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Visual Indicators

| Indicator | Meaning |
|-----------|---------|
| `████░░░░` | Streaming progress |
| `📊 87%` | Context utilization |
| `Turn: 3` | Current turn number |
| `💰 ~$0.003` | Estimated cost so far |
| `⏱ 1.2s/turn` | Average latency |

### 6.4 Chat Commands

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

### 6.5 One-Shot Chat

For scripting and non-interactive use:

```bash
# Single message, returns response
kg soul chat --message "What should I focus on?"

# With JSON output
kg soul chat --message "..." --json

# Continue specific session
kg soul chat --session abc123 --message "Follow up"
```

---

## Part VII: Session Persistence

### 7.1 Session Storage (D-gent Integration)

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

### 7.2 Session Recall

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

### 7.3 Cross-Session Context

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

## Part VIII: Multi-Entity Chat Architecture

### 8.1 The ChatSession Factory

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

### 8.2 Entity-Specific System Prompts

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

### 8.3 Dynamic Prompt Injection

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

## Part IX: Observability

### 9.1 Trace Spans

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

### 9.2 Metrics

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

### 9.3 Budget Tracking

```python
@dataclass
class SessionBudget:
    """Track conversation costs."""
    tokens_in_total: int = 0
    tokens_out_total: int = 0
    estimated_cost_usd: float = 0.0

    def record_turn(self, turn: Turn, model: str) -> None:
        self.tokens_in_total += turn.tokens_in
        self.tokens_out_total += turn.tokens_out
        self.estimated_cost_usd += estimate_cost(
            model, turn.tokens_in, turn.tokens_out
        )
```

---

## Part X: Implementation Plan

### 10.1 Phase 1: Core ChatSession (Week 1)

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

### 10.2 Phase 2: AGENTESE Integration (Week 1-2)

1. Create `@chatty` decorator in `affordances.py`

2. Add chat affordances to existing nodes:
   - `self.soul.chat.*` → K-gent
   - `world.town.citizen.<name>.chat.*` → Citizens

3. Update context resolvers:
   - `self_context.py`: Add chat sub-resolver
   - `world_context.py`: Add citizen chat resolution

### 10.3 Phase 3: CLI Projection (Week 2)

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

### 10.4 Phase 4: Persistence (Week 2-3)

1. D-gent integration:
   - Session crystal schema
   - Save/load operations
   - Search/list capabilities

2. Memory injection:
   - Cross-session recall
   - Entity-specific memory

---

## Part XI: Success Criteria

### 11.1 Functional

- [ ] `kg soul chat` enters interactive mode with K-gent
- [ ] `kg town chat elara` enters interactive mode with citizen
- [ ] `kg soul chat --message "..."` returns one-shot response
- [ ] Sessions persist across CLI restarts
- [ ] Context window management works (summarize/slide)
- [ ] Budget tracking shows accurate costs

### 11.2 Non-Functional

| Metric | Target |
|--------|--------|
| First response latency | < 2s |
| Streaming first token | < 500ms |
| Context rendering | < 100ms |
| Session save/load | < 200ms |
| Memory recall injection | < 500ms |

### 11.3 UX

- [ ] Streaming responses show progressively
- [ ] Context utilization visible
- [ ] Cost estimates displayed
- [ ] Graceful handling of entropy depletion
- [ ] Clear error messages for LLM failures

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
    context_strategy: Literal["sliding", "summarize", "forget", "hybrid"] = "summarize"
    summarization_threshold: float = 0.8

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

    # Entropy
    entropy_budget: float = 1.0
    entropy_decay_per_turn: float = 0.02
```

## Appendix C: Sources

Design patterns and best practices synthesized from:

- [Google Agent Development Kit - Sessions](https://google.github.io/adk-docs/sessions/)
- [Google ADK - Multi-Agent Framework](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)
- [Maxim AI - Context Window Management](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)
- [PatternFly - Conversation Design](https://www.patternfly.org/patternfly-ai/conversation-design/)
- [Smashing Magazine - AI Interface Patterns](https://www.smashingmagazine.com/2025/07/design-patterns-ai-interfaces/)
- [WillowTree - Conversational AI Best Practices](https://www.willowtreeapps.com/insights/willowtrees-7-ux-ui-rules-for-designing-a-conversational-ai-assistant)
- [Strands Agents - Session Management](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/)
- [Strands Agents - Conversation Management](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/conversation-management/)

---

*"The best conversation is the one where both participants become someone new."*

*Last updated: 2025-12-17*
