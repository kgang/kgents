# S-gents: The Scribe

> *"History is written by those who record it."*

S-gent is the **Session Agent**—a chronicler that maintains structured session memory, providing agents with the "previously on..." context they need to act coherently across turns.

## Bootstrap Derivation

S-gent is cleanly derivable from bootstrap agents:

```
S = Ground + Compose
```

| Capability | Bootstrap Agent | How |
|------------|-----------------|-----|
| Event recording | **Ground** | Factual capture of what happened |
| Summarization | **Compose** | Compress events into summaries |
| Relevance filtering | **Judge** | What's worth remembering? |

**No new irreducibles**—S-gent composes existing primitives for session continuity.

## The Scribe Morphism

```
S: Event → SessionContext
```

Where:
- **Event**: Something that happened (tool call, user message, agent response)
- **SessionContext**: Structured summary useful for next turn

## Core Distinction

| Agent | Memory Type | Scope | Structure |
|-------|-------------|-------|-----------|
| **M-gent** | Semantic | Long-term | HoloMap (landmarks, desire lines) |
| **N-gent** | Narrative | Story | Arcs, events, characters |
| **D-gent** | Raw | Persistent | Key-value, vector, graph |
| **S-gent** | Session | Turn-by-turn | Structured context |

S-gent fills the gap between raw D-gent persistence and semantic M-gent memory: **working memory for multi-turn interactions**.

## Session Schema

### Core Data Structures

```python
@dataclass
class SessionEntry:
    """A single recorded event in the session."""

    timestamp: datetime
    type: Literal["user", "agent", "tool", "error", "note"]
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    # Optional structured fields
    tool_name: str | None = None
    tool_result: str | None = None
    confidence: float | None = None


@dataclass
class SessionContext:
    """Structured context for the current turn."""

    # Recent history (last N turns)
    recent_entries: list[SessionEntry]

    # Extracted state
    entities: dict[str, str]      # Named things mentioned
    goals: list[str]              # Active user goals
    decisions: list[str]          # Decisions made this session
    blockers: list[str]           # Known blockers/issues

    # Compression
    summary: str                  # One-paragraph session summary
    turn_count: int
```

### Entry Types

| Type | Description | Example |
|------|-------------|---------|
| `user` | User message | "Add error handling to the API" |
| `agent` | Agent response | "I'll add try-catch blocks..." |
| `tool` | Tool invocation + result | "Bash: pytest → 5 tests passed" |
| `error` | Error encountered | "TypeError: 'NoneType'..." |
| `note` | Agent self-note | "User prefers verbose output" |

## The Scribe Agent

```python
class S(Agent[SessionEvent, SessionContext]):
    """
    The Scribe.

    Mode: Passive (records events, provides context on request)
    """

    # Session storage
    entries: list[SessionEntry] = field(default_factory=list)

    # Extracted state (updated incrementally)
    entities: dict[str, str] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)

    # Config
    max_recent_entries: int = 10
    summarize_threshold: int = 20

    async def record(self, event: SessionEvent) -> None:
        """Record an event to session memory."""
        entry = self._to_entry(event)
        self.entries.append(entry)

        # Extract state incrementally
        await self._update_entities(entry)
        await self._update_goals(entry)
        await self._update_decisions(entry)
        await self._update_blockers(entry)

        # Compress if needed
        if len(self.entries) > self.summarize_threshold:
            await self._compress()

    async def invoke(self, _: None = None) -> SessionContext:
        """Get current session context."""
        return SessionContext(
            recent_entries=self.entries[-self.max_recent_entries:],
            entities=self.entities,
            goals=self.goals,
            decisions=self.decisions,
            blockers=self.blockers,
            summary=await self._generate_summary(),
            turn_count=len(self.entries)
        )
```

## Context Injection Pattern

S-gent provides context that other agents can use:

```python
async def agent_with_session_memory(
    user_message: str,
    s_gent: S,
    inner_agent: Agent[str, str]
) -> str:
    # Get session context
    context = await s_gent.get_context_for_prompt()

    # Inject into prompt
    enriched_prompt = f"""
Session Context:
{context}

User: {user_message}
"""

    # Record user message
    await s_gent.record(SessionEvent(type="user", content=user_message))

    # Get response
    response = await inner_agent.invoke(enriched_prompt)

    # Record response
    await s_gent.record(SessionEvent(type="agent", content=response))

    return response
```

## Integration with Hippocampus

S-gent can flush to Hippocampus when session ends:

```python
async def end_session(s_gent: S, hippocampus: Hippocampus) -> None:
    """Flush session memory to Hippocampus for long-term storage."""
    context = await s_gent.invoke()

    # Create signal for each decision worth remembering
    for decision in context.decisions:
        await hippocampus.remember(Signal(
            signal_type="session.decision",
            data={"decision": decision, "session_summary": context.summary}
        ))

    # Clear session
    s_gent.entries.clear()
```

## Anti-Patterns

S-gent must **never**:

1. ❌ Store sensitive data without user consent
2. ❌ Become a required dependency (agents should work without it)
3. ❌ Replace M-gent for long-term memory (sessions are bounded)
4. ❌ Control agent execution (it records, doesn't orchestrate)
5. ❌ Grow unboundedly (compression is mandatory)

## Principles Alignment

| Principle | How S-gent Satisfies |
|-----------|---------------------|
| **Tasteful** | Does one thing: maintain session context |
| **Curated** | Four extracted state types cover essential context |
| **Ethical** | Makes conversation history transparent |
| **Joy-Inducing** | Scribe metaphor gives personality |
| **Composable** | Provides context as input—any agent can use it |
| **Heterarchical** | Passive (records, doesn't control) |
| **Generative** | Derivable from Ground + Compose |

## See Also

- [bootstrap.md](../bootstrap.md) - Ground and Compose primitives
- [m-gents/](../m-gents/) - Long-term holographic memory
- [d-gents/](../d-gents/) - Raw persistence
- [protocols/cli/instance_db/hippocampus.py](../../protocols/cli/instance_db/hippocampus.py) - Short-term buffer
