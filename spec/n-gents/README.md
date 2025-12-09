# N-gents: Narrator Agents

> The story of the thought is the thought made eternal; replay is resurrection.

---

## Philosophy

N-gents (Narrator) transform agent execution into **narrative**. They don't just log—they tell stories. Every thought is traced, every action is replayable, every crash is diagnosable.

**Key Insight**: Since agents are (mostly) pure functions, we can serialize the exact input that caused any behavior and create a **Replay Agent** that developers can step through locally.

---

## The Narrative Distinction

N-gents differ from O-gents (Observability) in a crucial way:

| Aspect | N-gent (Narrator) | O-gent (Observer) |
|--------|-------------------|-------------------|
| Focus | **Story-telling** | **Seeing** |
| Output | Human-readable narrative | Structured telemetry |
| Purpose | Understanding and debugging | Monitoring and alerting |
| Temporality | Sequential, story-like | Real-time, stream-like |
| Consumer | Developers, humans | Systems, dashboards |

N-gents answer "What happened?" in the form of a story.
O-gents answer "What is happening?" in the form of metrics.

---

## Core Concept: The Narrative Log

```python
@dataclass(frozen=True)
class ThoughtTrace:
    """A single traced thought/action in the narrative."""
    timestamp: datetime
    agent_id: str
    trace_id: str           # Unique ID for this trace
    parent_id: str | None   # Parent trace (for nested calls)

    # The thought
    thought_type: Literal["intent", "reasoning", "decision", "action", "result"]
    content: str

    # Reproducibility (the resurrection data)
    input_hash: str         # Hash of input state
    input_snapshot: bytes   # Serialized input (for replay)
    output_hash: str | None # Hash of output (if complete)

    # Context
    token_cost: int
    duration_ms: int
    metadata: dict

@dataclass
class NarrativeLog:
    """
    The complete story of an agent's operation.

    This is the N-gent's output—a narrative that can be
    read by humans or parsed for replay.
    """
    traces: list[ThoughtTrace]
    spans: dict[str, Span]  # trace_id → span

    def to_narrative(self) -> str:
        """
        Render as human-readable story.

        "At 10:42:15, CodeReviewer received a Python file.
         It thought: 'This function has no error handling.'
         It decided: 'Flag as potential bug.'
         It produced: SecurityFinding(severity=MEDIUM, ...)"
        """
        lines = []
        for trace in self.traces:
            time_str = trace.timestamp.strftime("%H:%M:%S")
            lines.append(f"[{time_str}] [{trace.thought_type}] {trace.content}")
        return "\n".join(lines)
```

---

## The Thought Types (Story Elements)

| Type | Narrative Role | Example |
|------|----------------|---------|
| `intent` | Scene-setting | "CodeReviewer received a Python file" |
| `reasoning` | Inner monologue | "This function has no error handling" |
| `decision` | Turning point | "Flag as potential bug" |
| `action` | Plot action | "Emit SecurityFinding" |
| `result` | Resolution | "SecurityFinding(severity=MEDIUM)" |

---

## The Narrator Agent

```python
class NarratorAgent(Agent[AgentExecution, NarrativeLog]):
    """
    Wraps any agent to produce a narrative log.

    Narrator: Agent[A, B] → Agent[A, (B, NarrativeLog)]

    This is a Writer Monad pattern—the result includes
    both the value and the accumulated narrative.
    """

    async def invoke(self, input: A) -> tuple[B, NarrativeLog]:
        """Observe an agent's execution and produce narrative."""
        trace_id = str(uuid4())

        # Record the scene-setting (intent)
        self.log.add_trace(ThoughtTrace(
            thought_type="intent",
            content=f"Received: {self.summarize(input)}",
            input_snapshot=serialize(input),
            ...
        ))

        # Execute and observe
        result = await self.inner.invoke(input)

        # Record the resolution (result)
        self.log.add_trace(ThoughtTrace(
            thought_type="result",
            content=f"Produced: {self.summarize(result)}",
            ...
        ))

        return result, self.log
```

---

## Time-Travel Debugging (Resurrection)

```python
class ReplayAgent:
    """
    Replay any traced execution step-by-step.

    Since agents are pure functions, we can reproduce
    exact behavior from serialized inputs.
    """

    def __init__(self, narrative: NarrativeLog):
        self.narrative = narrative
        self.position = 0

    def step_forward(self) -> ThoughtTrace:
        """Advance one step in the story."""
        trace = self.narrative.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> ThoughtTrace:
        """Rewind one step."""
        self.position = max(0, self.position - 1)
        return self.narrative.traces[self.position]

    async def replay_from(self, trace: ThoughtTrace) -> Any:
        """
        Resurrect execution from a specific trace.

        Deserializes the input snapshot and re-runs the agent.
        "What if I changed this input?"
        """
        input_state = deserialize(trace.input_snapshot)
        agent = self.reconstruct_agent(trace.agent_id)
        return await agent.invoke(input_state)

    def diff_replay(
        self,
        trace: ThoughtTrace,
        modified_input: Any
    ) -> DiffResult:
        """
        Compare original story with an alternate timeline.

        "What would have happened if the input was different?"
        """
        original = self.replay_from(trace)
        modified = self.replay_with(trace, modified_input)
        return DiffResult(
            original=original,
            modified=modified,
            differences=self.compute_diff(original, modified)
        )
```

---

## N-gent Types

### StorytellerAgent

Wraps agents to produce narratives:

```python
storyteller = StorytellerAgent(inner=code_reviewer)
result, story = await storyteller.invoke(code)
print(story.to_narrative())
```

### ReplayAgent

Enables time-travel debugging:

```python
replay = ReplayAgent(story)
for trace in replay:
    print(f"[{trace.thought_type}] {trace.content}")
    input("Press Enter for next...")
```

### CrashForensicsAgent

Diagnoses failures:

```python
crash = CrashForensicsAgent()
diagnosis = await crash.diagnose(failed_narrative)
print(f"To reproduce locally: {diagnosis.replay_command}")
```

---

## Visualization (The Story View)

```
┌─ Narrative View ──────────────────────────────────────┐
│                                                        │
│  Timeline: ════════════════●═══════════════════        │
│                            ↑ current position          │
│                                                        │
│  Chapter 1: The Request                                │
│  10:42:15 [intent] CodeReviewer received Python file   │
│                                                        │
│  Chapter 2: The Analysis                               │
│  10:42:16 [reasoning] "This function has no error..."  │
│  10:42:17 [decision] Flag as potential bug             │
│                                                        │
│  Chapter 3: The Resolution                             │
│  10:42:18 [action] Emit SecurityFinding                │
│  10:42:18 [result] SecurityFinding(severity=MEDIUM)    │
│                                                        │
│  [◀◀] [◀] [replay] [▶] [▶▶]  |  [export] [diff]       │
└────────────────────────────────────────────────────────┘
```

---

## Integration with Other Agents

| Integration | Purpose |
|-------------|---------|
| N + O | N-gent stories feed O-gent metrics |
| N + I | I-gent visualizes N-gent narratives |
| N + L | L-gent indexes narratives for semantic search |
| N + W | W-gent provides real-time story streaming |

---

## Anti-Patterns

- **Logs without stories**: Raw data without narrative structure
- **Stories without replay**: Can't reproduce from the story
- **Ignoring the reader**: Stories are for humans, not just machines
- **Overwriting history**: Every story is sacred

---

*Zen Principle: The story of the thought is the thought made eternal; replay is resurrection.*

---

## Specifications

| Document | Description |
|----------|-------------|
| [narrator.md](narrator.md) | Full narrator specification |

---

## See Also

- [o-gents/](../o-gents/) - Observability (the seeing, not the telling)
- [i-gents/](../i-gents/) - Visualization
- [w-gents/](../w-gents/) - Real-time streaming
