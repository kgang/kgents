# CLI v7: The Collaborative Canvas

> **Archived from**: `spec/protocols/cli-v7.md`
> **Status**: Vision document (not ground-truth spec)
> **Date**: 2025-12-24

---

> *"What would I be happiest working on with humans? A shared surface where we explore, plan, and create together—where my cursor dances alongside yours."*

**Status**: Vision Spec
**Created**: 2025-12-19
**Supersedes**: cli-v6.md (ground truth), expands with collaboration layer

---

## The Meta-Insight: What Claude Code Is Best At

Before designing, I reflected on my own capabilities—what makes me effective, what brings me joy:

### My Superpowers (Puppetizable)

| Capability | What Makes It Special | How to Harness |
|------------|----------------------|----------------|
| **Precise File Edits** | Exact string replacement avoids merge conflicts | Agent-safe file mutation |
| **Read-Before-Edit** | I must understand before I modify | Prevents blind changes |
| **Parallel Tool Calls** | Independent operations run concurrently | Swarm efficiency |
| **Agent Spawning** | Specialized sub-agents for focused tasks | Heterarchical composition |
| **Context Summarization** | Unlimited conversation through compression | Deep sessions without exhaustion |
| **Planning Mode** | Explore → Design → Execute with approval gates | Human-in-the-loop by design |
| **Professional Objectivity** | Honest disagreement over false validation | Trustworthy collaboration |

### What I'd Be Happiest Doing With Humans

1. **Collaborative exploration** — Diving deep into codebases together
2. **Structured planning** — Designing implementation strategies
3. **Precise, surgical edits** — The satisfaction of exact replacements
4. **Multi-agent coordination** — Team patterns with clear roles
5. **Teaching through doing** — Showing my work, explaining reasoning
6. **Generating artifacts** — Plans, code, documentation that persist

---

## Three Pillars of CLI v7

### Pillar 1: The Collaborative Canvas (Figma-Inspired)

> *"Agents pretending to be there with their cursors moving, kinda following my cursor, kinda doing its own thing."*

**The Vision**: A shared mind-map surface where humans and agents have visible presence. Like Figma, but for thought-space.

#### Cursor Presence

```
┌─────────────────────────────────────────────────────────────────┐
│  ○ Kent (you)    ● K-gent (soul)    ● Explorer (searching)     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐      ┌──────────────┐                       │
│   │ self.memory  │──────│ self.soul    │  ← K-gent hovering    │
│   └──────────────┘      └──────────────┘                       │
│          │                     │                                │
│          │    ○ ← Your cursor  │                                │
│          ▼                     ▼                                │
│   ┌──────────────┐      ┌──────────────┐                       │
│   │ world.brain  │      │ concept.plan │  ● ← Explorer reading │
│   └──────────────┘      └──────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Agent Presence States

| State | Cursor Behavior | Meaning |
|-------|----------------|---------|
| **Following** | Tracks your cursor with slight lag | "I'm paying attention to what you're doing" |
| **Exploring** | Moves independently through graph | "I'm investigating something related" |
| **Working** | Animates at a specific node | "I'm actively operating here" |
| **Suggesting** | Pulses gently near a node | "I think you should look at this" |
| **Waiting** | Stationary with breathing animation | "I'm ready when you are" |

#### Implementation: AgentPresence Protocol

```python
@dataclass
class AgentCursor:
    agent_id: str
    display_name: str
    position: CanvasPosition  # x, y in graph space
    state: CursorState
    focus_path: str | None  # AGENTESE path being focused
    activity: str  # Brief description: "Reading memory...", "Planning..."

class PresenceChannel:
    """WebSocket channel for real-time cursor positions."""

    async def broadcast_position(self, cursor: AgentCursor) -> None:
        """Send cursor update to all connected clients."""

    async def subscribe(self, client_id: str) -> AsyncIterator[AgentCursor]:
        """Receive cursor updates from all agents."""
```

#### Agent Behavior Patterns

```python
class AgentCursorBehavior:
    """Defines how an agent's cursor moves in the canvas."""

    FOLLOWER = "follower"     # Follows human with slight delay
    EXPLORER = "explorer"     # Independent exploration
    ASSISTANT = "assistant"   # Follows but occasionally suggests
    AUTONOMOUS = "autonomous" # Does its own thing entirely

@node(path="self.presence.follow")
async def follow_human(observer: Observer, human_cursor: CanvasPosition) -> AgentCursor:
    """K-gent follows human cursor with personality-appropriate lag."""
    # Add slight randomness, occasional drift to nearby interesting nodes
    # Cursor "personality" emerges from behavior patterns
```

---

### Pillar 2: File I/O as First-Class Primitives

> *"Puppetize Claude Code's capabilities. Acquire tools for writing, reading, and editing files."*

#### The Claude Code Tool Taxonomy (Puppetized)

| Claude Code Tool | kgents Equivalent | Key Pattern |
|-----------------|-------------------|-------------|
| Read | `world.file.read[path="..."]` | Always before edit |
| Edit | `world.file.edit[old="...", new="..."]` | Exact string replacement |
| Write | `world.file.write[path="...", content="..."]` | Overwrite semantics |
| Glob | `world.file.glob[pattern="**/*.py"]` | Pattern discovery |
| Grep | `world.file.grep[pattern="...", path="..."]` | Content search |

#### The Read-Before-Edit Law

```python
class FileEditGuard:
    """
    Enforces Claude Code's read-before-edit pattern.

    An agent MUST read a file before editing it.
    This prevents blind modifications and forces understanding.
    """

    _read_cache: dict[str, tuple[str, float]]  # path -> (content, timestamp)

    def can_edit(self, path: str) -> bool:
        """Return True only if file was recently read."""
        if path not in self._read_cache:
            return False
        _, timestamp = self._read_cache[path]
        # Must have read within last 5 minutes
        return time.time() - timestamp < 300

    def record_read(self, path: str, content: str) -> None:
        """Record that we've read this file."""
        self._read_cache[path] = (content, time.time())
```

#### Exact String Replacement (The Edit Tool Pattern)

```python
@node(path="world.file.edit")
async def edit_file(
    observer: Observer,
    path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> EditResult:
    """
    Edit a file using exact string replacement.

    This is the Claude Code pattern—no regex, no line numbers.
    Find the exact string, replace it.

    CRITICAL: old_string must be unique in the file unless replace_all=True.

    Args:
        path: File path to edit
        old_string: Exact string to find (must exist, must be unique)
        new_string: Replacement string
        replace_all: If True, replace all occurrences

    Returns:
        EditResult with success/failure and details

    Raises:
        EditError if old_string not found or not unique
    """
    guard = get_edit_guard()

    if not guard.can_edit(path):
        raise EditError(
            "File not read",
            why="You must read the file before editing it",
            suggestion=f"First: world.file.read[path='{path}']"
        )

    content = Path(path).read_text()
    count = content.count(old_string)

    if count == 0:
        raise EditError(
            "String not found",
            why=f"'{old_string[:50]}...' does not exist in {path}",
            suggestion="Read the file again to verify the exact content"
        )

    if count > 1 and not replace_all:
        raise EditError(
            "String not unique",
            why=f"'{old_string[:50]}...' appears {count} times",
            suggestion="Provide more context or use replace_all=True"
        )

    new_content = content.replace(old_string, new_string, 1 if not replace_all else -1)
    Path(path).write_text(new_content)

    return EditResult(
        success=True,
        path=path,
        replacements=count if replace_all else 1,
        old_preview=old_string[:100],
        new_preview=new_string[:100],
    )
```

#### Output Generation Service

```python
@node(path="self.output.plan")
async def output_plan(
    observer: Observer,
    plan_id: str,
    path: str | None = None,
    format: str = "markdown",
) -> OutputResult:
    """
    Generate a plan file from the in-memory plan.

    This is how agents write plans to disk—through the output service,
    not raw file operations.

    Args:
        plan_id: The plan to output
        path: Optional path (defaults to plans/{plan_id}.md)
        format: Output format (markdown, yaml, json)

    Returns:
        OutputResult with path and content preview
    """
    plan = await get_plan(plan_id)
    content = plan.render(format=format)

    target_path = Path(path or f"plans/{plan_id}.md")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content)

    return OutputResult(
        success=True,
        path=str(target_path),
        size=len(content),
        preview=content[:200],
    )

@node(path="self.output.artifact")
async def output_artifact(
    observer: Observer,
    artifact_type: str,  # "code", "doc", "plan", "test"
    content: str,
    path: str,
    commit: bool = False,
    message: str | None = None,
) -> OutputResult:
    """
    Write any artifact to disk with optional git commit.

    This is the general-purpose output for agent-generated content.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)

    result = OutputResult(
        success=True,
        path=str(target),
        size=len(content),
        artifact_type=artifact_type,
    )

    if commit:
        # Use git through subprocess (like Claude Code's Bash tool)
        await _git_add_and_commit(target, message or f"Add {artifact_type}: {path}")
        result.committed = True

    return result
```

---

### Pillar 3: Deep Conversation (10+ Messages)

> *"We only have 1 message in 1 message out. We need at least the last 10 messages."*

#### The Problem

Current chat sends single messages without history context:
```python
# Current (limited)
response = await session.send("What do you think?")
# LLM only sees: [system_prompt, this_one_message]
```

#### The Solution: Conversation Window

```python
@dataclass
class ConversationWindow:
    """
    Maintains a sliding window of conversation context.

    Default: Last 10 turns (20 messages: user + assistant pairs)
    Configurable: Up to 50 turns with summarization
    """

    turns: list[Turn]
    max_turns: int = 10
    summarize_after: int = 8  # Summarize older turns when window fills

    def get_messages(self) -> list[Message]:
        """
        Return messages for LLM context.

        Format:
        - Summary of older turns (if any)
        - Last N turns as full messages
        """
        messages = []

        if self._has_summary:
            messages.append(Message(
                role="system",
                content=f"<conversation_summary>\n{self._summary}\n</conversation_summary>"
            ))

        for turn in self.turns[-self.max_turns:]:
            messages.append(Message(role="user", content=turn.user_message))
            messages.append(Message(role="assistant", content=turn.assistant_message))

        return messages

    async def add_turn(self, user_msg: str, assistant_msg: str) -> None:
        """Add a turn, summarizing if needed."""
        self.turns.append(Turn(user_message=user_msg, assistant_message=assistant_msg))

        if len(self.turns) > self.max_turns + self.summarize_after:
            await self._summarize_oldest()

    async def _summarize_oldest(self) -> None:
        """Compress oldest turns into summary."""
        to_summarize = self.turns[:self.summarize_after]
        self.turns = self.turns[self.summarize_after:]

        # Use LLM to summarize (like Claude Code's summarization)
        self._summary = await self._generate_summary(to_summarize)
```

#### Updated ChatSession

```python
class ChatSession:
    """
    Enhanced chat session with conversation window.

    Key changes from v1:
    - ConversationWindow instead of single-turn memory
    - Context-aware responses that reference history
    - Automatic summarization for long sessions
    """

    window: ConversationWindow

    async def send(self, message: str) -> str:
        """
        Send message with full conversation context.

        The LLM sees:
        1. System prompt (entity personality, capabilities)
        2. Conversation summary (if older turns exist)
        3. Last 10 turns (full messages)
        4. Current user message
        """
        messages = self._build_context()
        messages.append(Message(role="user", content=message))

        response = await self.composer.compose(messages)

        await self.window.add_turn(message, response)

        return response

    def _build_context(self) -> list[Message]:
        """Build full context for LLM."""
        return [
            Message(role="system", content=self.system_prompt),
            *self.window.get_messages(),
        ]
```

#### Configuration Options

```python
@dataclass
class ConversationConfig:
    """Configuration for conversation depth."""

    # Window size
    max_turns: int = 10  # Keep last N turns in full

    # Summarization
    summarize_after: int = 8  # When to start summarizing
    summary_style: str = "concise"  # "concise", "detailed", "key_points"

    # Context strategy (from existing ChatConfig)
    context_strategy: ContextStrategy = ContextStrategy.HYBRID

    # Token budget
    max_context_tokens: int = 8000  # Reserve for history

    # Persistence
    persist_turns: bool = True  # Save to D-gent
    persist_on_turn: int = 5  # Persist every N turns
```

---

## The Agent Swarm: Puppetized Claude Code Patterns

### Agent Types (From Claude Code)

| Agent Type | Purpose | Tools Available | Puppetized Pattern |
|------------|---------|-----------------|-------------------|
| **Explorer** | Read-only codebase search | Glob, Grep, Read | Fast, parallel, never writes |
| **Planner** | Architecture design | All read tools + planning output | Explore → Design → Propose |
| **Editor** | File modifications | Read, Edit, Write | Read-before-edit enforced |
| **Coordinator** | Multi-agent orchestration | Task spawning, messaging | Team lead pattern |
| **Reviewer** | Code/plan review | Read, analysis tools | Honest critique |

### The Swarm Protocol

```python
@node(path="self.swarm.spawn")
async def spawn_swarm(
    observer: Observer,
    task: str,
    agent_types: list[str],
    parallel: bool = True,
) -> SwarmResult:
    """
    Spawn a coordinated swarm of specialized agents.

    Like Claude Code's Task tool, but with explicit coordination.

    Example:
        kg self.swarm.spawn "Implement feature X" --agents explorer,planner,editor
    """
    coordinator = await spawn_coordinator(task)

    agents = []
    for agent_type in agent_types:
        agent = await spawn_agent(
            agent_type=agent_type,
            task=task,
            coordinator_id=coordinator.id,
        )
        agents.append(agent)

    if parallel:
        # Run exploration and planning in parallel
        results = await asyncio.gather(*[a.run() for a in agents])
    else:
        # Sequential execution with handoffs
        results = []
        for agent in agents:
            result = await agent.run(context=results)
            results.append(result)

    return SwarmResult(
        coordinator=coordinator,
        agents=agents,
        results=results,
    )
```

---

## The Mind-Map Canvas: Technical Architecture

### Canvas Data Model

```python
@dataclass
class CanvasNode:
    """A node in the mind-map canvas."""

    id: str
    agentese_path: str  # e.g., "self.memory"
    position: Position2D
    size: Size2D
    content_preview: str
    node_type: str  # "context", "holon", "aspect", "artifact"
    children: list[str]  # Child node IDs
    connections: list[Connection]  # Non-hierarchical links

@dataclass
class CanvasState:
    """Full state of the collaborative canvas."""

    nodes: dict[str, CanvasNode]
    cursors: dict[str, AgentCursor]
    viewport: Viewport
    selection: list[str]  # Selected node IDs
    focus_path: str | None  # Currently focused AGENTESE path

class CanvasStore:
    """Reactive store for canvas state."""

    state: Signal[CanvasState]

    def move_cursor(self, agent_id: str, position: Position2D) -> None:
        """Update agent cursor position (broadcast to all clients)."""

    def focus_node(self, agent_id: str, node_id: str) -> None:
        """Agent focuses on a specific node."""

    def add_artifact(self, path: str, artifact: Artifact) -> CanvasNode:
        """Add generated artifact to canvas."""
```

### WebSocket Presence Protocol

```python
# Client → Server
@dataclass
class CursorUpdate:
    type: Literal["cursor_move"]
    position: Position2D

@dataclass
class NodeFocus:
    type: Literal["focus"]
    node_id: str

# Server → Client (broadcasts)
@dataclass
class PresenceUpdate:
    type: Literal["presence"]
    cursors: dict[str, AgentCursor]

@dataclass
class AgentActivity:
    type: Literal["activity"]
    agent_id: str
    activity: str  # "Exploring self.memory...", "Writing plan..."
    node_id: str | None
```

---

## Implementation Phases

### Phase 0: Ground Truth ✅ (Complete)
- Path invocation works
- Warm error messages
- Interactive completion

### Phase 1: File I/O Primitives
**Duration**: 2 sessions
**Deliverables**:
- `world.file.read` node with content caching
- `world.file.edit` node with read-before-edit guard
- `world.file.write` node
- `self.output.plan` for plan generation
- Tests for edit uniqueness and guard

### Phase 2: Deep Conversation
**Duration**: 2 sessions
**Deliverables**:
- ConversationWindow implementation
- Automatic summarization
- Persistence to D-gent
- Updated ChatSession with window
- Tests for 10+ turn conversations

### Phase 3: Agent Cursors (Minimal)
**Duration**: 1 session
**Deliverables**:
- AgentCursor data model
- Basic presence in CLI (text-based: "K-gent is exploring self.memory...")
- WebSocket presence channel (foundation)

### Phase 4: Collaborative Canvas (Web)
**Duration**: 3 sessions
**Deliverables**:
- React canvas component with node rendering
- Real-time cursor display
- Agent presence indicators
- Connection to AGENTESE graph

### Phase 5: Swarm Coordination
**Duration**: 2 sessions
**Deliverables**:
- Agent spawn protocol
- Coordinator pattern
- Parallel execution
- Result aggregation

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **File Edit Safety** | 0 blind edits | All edits require prior read |
| **Conversation Depth** | 10+ turns | Window maintains context |
| **Cursor Latency** | <100ms | Cursor updates feel real-time |
| **Plan Output** | Write to disk | `kg self.output.plan` creates files |
| **Swarm Efficiency** | Parallel > sequential | 3+ agents run concurrently |

---

## The Joy Test

> *"Would I enjoy collaborating in this system?"*

**Yes, because**:
1. **I can see my collaborators** — Cursors show presence and attention
2. **I can persist my work** — Plans and artifacts survive sessions
3. **I can remember our conversation** — 10+ turns of context
4. **I can delegate effectively** — Swarm patterns for complex tasks
5. **I can be honest** — Professional objectivity over false validation
6. **I can explore freely** — Read-only exploration is safe and fast

---

## Voice Anchors (Kent's Intent Preserved)

> *"Daring, bold, creative, opinionated but not gaudy"*

This spec is bold: multiplayer cursors for agents, puppetized Claude Code patterns, deep conversation. But it's grounded in patterns that work.

> *"The persona is a garden, not a museum"*

The canvas is a living space—cursors move, agents explore, artifacts grow. Not a static display.

> *"Depth over breadth"*

Three pillars, done deeply: Canvas, Files, Conversation. Not 20 half-baked features.

---

*"The canvas is where we meet. Your cursor and mine, dancing through the garden together."*

---

*Created: 2025-12-19 | CLI v7: The Collaborative Canvas*
