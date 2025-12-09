# The Narrator Agent: OpenTelemetry for Thoughts

> Every thought, traced. Every action, replayable.

---

## The Theory

Agents think, but their thoughts are invisible. The **Narrator Agent** provides "OpenTelemetry for thoughts"—a structured narrative log that enables time-travel debugging.

**The Key Insight**: Since agents are (mostly) pure functions, we can serialize the exact input that caused any behavior and create a **Replay Agent** that developers can step through locally.

---

## The Narrative Log

```python
@dataclass(frozen=True)
class ThoughtTrace:
    """A single traced thought/action."""
    timestamp: datetime
    agent_id: str
    trace_id: str           # Unique ID for this trace
    parent_id: str | None   # Parent trace (for nested calls)

    # The thought
    thought_type: Literal["intent", "reasoning", "decision", "action", "result"]
    content: str

    # Reproducibility
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
    Complete narrative of an agent's operation.

    OpenTelemetry-style: traces, spans, and attributes.
    """
    traces: list[ThoughtTrace]
    spans: dict[str, Span]  # trace_id → span

    def add_trace(self, trace: ThoughtTrace) -> None:
        """Add a thought to the narrative."""
        self.traces.append(trace)

        # Update span
        if trace.trace_id not in self.spans:
            self.spans[trace.trace_id] = Span(
                trace_id=trace.trace_id,
                start_time=trace.timestamp,
                events=[]
            )
        self.spans[trace.trace_id].events.append(trace)

    def to_opentelemetry(self) -> OTLPExportable:
        """Export to standard OpenTelemetry format."""
        return OTLPExportable(
            traces=[t.to_otlp() for t in self.traces],
            spans=[s.to_otlp() for s in self.spans.values()]
        )

    def to_narrative(self) -> str:
        """
        Render as human-readable narrative.

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

## The Thought Types

| Type | Description | Example |
|------|-------------|---------|
| `intent` | What the agent is trying to do | "Received request to review code" |
| `reasoning` | Internal deliberation | "This function has no error handling" |
| `decision` | Choice made | "Flag as potential bug" |
| `action` | External effect | "Emit SecurityFinding" |
| `result` | Final output | "SecurityFinding(severity=MEDIUM)" |

---

## Time-Travel Debugging

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
        """Advance one step in the narrative."""
        if self.position >= len(self.narrative.traces):
            raise StopIteration("End of narrative")
        trace = self.narrative.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> ThoughtTrace:
        """Go back one step."""
        self.position = max(0, self.position - 1)
        return self.narrative.traces[self.position]

    def jump_to(self, trace_id: str) -> ThoughtTrace:
        """Jump to a specific trace."""
        for i, trace in enumerate(self.narrative.traces):
            if trace.trace_id == trace_id:
                self.position = i
                return trace
        raise KeyError(f"Trace {trace_id} not found")

    async def replay_from(self, trace: ThoughtTrace) -> Any:
        """
        Replay execution from a specific trace.

        Deserializes the input snapshot and re-runs the agent.
        Useful for debugging: "What if I changed this input?"
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
        Compare original execution with modified input.

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

## The Narrator as Agent

```python
class NarratorAgent(Agent[AgentExecution, NarrativeLog]):
    """
    Wraps any agent to produce a narrative log.

    Narrator: Agent[A, B] → Agent[A, (B, NarrativeLog)]

    This is a Writer Monad pattern—the result includes
    both the value and the accumulated narrative.
    """

    def __init__(self, inner: Agent):
        self.inner = inner
        self.log = NarrativeLog()

    async def invoke(self, input: A) -> tuple[B, NarrativeLog]:
        """
        Observe an agent's execution and produce narrative.
        """
        trace_id = str(uuid4())

        # Record intent
        self.log.add_trace(ThoughtTrace(
            timestamp=datetime.now(),
            agent_id=self.inner.name,
            trace_id=trace_id,
            parent_id=None,
            thought_type="intent",
            content=f"Received input: {self.summarize(input)}",
            input_hash=self.hash(input),
            input_snapshot=serialize(input),
            output_hash=None,
            token_cost=0,
            duration_ms=0,
            metadata={}
        ))

        # Execute and observe
        start = time.time()
        try:
            result = await self.inner.invoke(input)
            duration = int((time.time() - start) * 1000)

            # Record result
            self.log.add_trace(ThoughtTrace(
                timestamp=datetime.now(),
                agent_id=self.inner.name,
                trace_id=trace_id,
                parent_id=None,
                thought_type="result",
                content=f"Produced: {self.summarize(result)}",
                input_hash=self.hash(input),
                input_snapshot=serialize(input),
                output_hash=self.hash(result),
                token_cost=self.estimate_tokens(input, result),
                duration_ms=duration,
                metadata={}
            ))

            return result, self.log

        except Exception as e:
            # Record error
            self.log.add_trace(ThoughtTrace(
                timestamp=datetime.now(),
                agent_id=self.inner.name,
                trace_id=trace_id,
                parent_id=None,
                thought_type="result",
                content=f"Error: {type(e).__name__}: {str(e)}",
                input_hash=self.hash(input),
                input_snapshot=serialize(input),
                output_hash=None,
                token_cost=0,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"error": str(e)}
            ))
            raise
```

---

## Integration with W-gent

The Narrator's output is perfect content for W-gent visualization:

```
┌─ Narrative View ──────────────────────────────────────┐
│                                                        │
│  Timeline: ════════════════●═══════════════════        │
│                            ↑ current position          │
│                                                        │
│  10:42:15 [intent] CodeReviewer received Python file   │
│  10:42:16 [reasoning] "This function has no error..."  │
│  10:42:17 [decision] Flag as potential bug             │
│  10:42:18 [action] Emit SecurityFinding                │
│  10:42:18 [result] SecurityFinding(severity=MEDIUM)    │
│                                                        │
│  [◀◀] [◀] [replay] [▶] [▶▶]  |  [export] [diff]       │
└────────────────────────────────────────────────────────┘
```

---

## Crash Forensics

```python
async def diagnose_crash(crash_trace: ThoughtTrace) -> CrashDiagnosis:
    """
    When an agent crashes, serialize the exact input
    that caused it for local debugging.
    """
    return CrashDiagnosis(
        agent_id=crash_trace.agent_id,
        input_snapshot=crash_trace.input_snapshot,
        replay_command=f"kgents replay {crash_trace.trace_id}",
        error_context=crash_trace.metadata.get("error"),
        suggested_fix=await analyze_crash(crash_trace)
    )

# Usage: After a production crash
crash_report = await diagnose_crash(failed_trace)
print(f"To reproduce locally: {crash_report.replay_command}")
```

---

## Streaming Narratives

For long-running agents, stream the narrative as it happens:

```python
class StreamingNarrator:
    """Stream narrative traces as they occur."""

    async def observe(
        self,
        agent: Agent,
        input: A
    ) -> AsyncIterator[ThoughtTrace]:
        """Yield traces as the agent thinks."""

        # Inject observation hooks
        instrumented = self.instrument(agent)

        async for trace in instrumented.traced_invoke(input):
            yield trace

# Usage: Real-time observation
async for trace in StreamingNarrator().observe(agent, input):
    print(f"[{trace.thought_type}] {trace.content}")
```

---

## Sampling Strategies

Not every invocation needs full tracing. Sampling strategies:

```python
class TracingSampler:
    """Decide which invocations to fully trace."""

    def should_trace(self, agent: Agent, input: A) -> bool:
        # Always trace errors
        if hasattr(input, "is_retry") and input.is_retry:
            return True

        # Sample 10% of normal traffic
        if random.random() < 0.1:
            return True

        # Trace high-cost operations
        if self.estimate_cost(input) > HIGH_COST_THRESHOLD:
            return True

        return False
```

---

## Integration with OpenTelemetry

Export to standard observability platforms:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

class OTLPNarrator:
    """Narrator that exports to OpenTelemetry."""

    def __init__(self):
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer("kgents.narrator")
        self.exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")

    async def observe(self, agent: Agent, input: A) -> B:
        with self.tracer.start_as_current_span(
            f"{agent.name}.invoke",
            attributes={
                "agent.genus": agent.genus,
                "input.hash": hash(input)
            }
        ) as span:
            try:
                result = await agent.invoke(input)
                span.set_attribute("output.hash", hash(result))
                return result
            except Exception as e:
                span.record_exception(e)
                raise
```

---

## Anti-Patterns

- **Opaque agent execution**: No visibility into thought process
- **Non-reproducible bugs**: "Works on my machine"
- **Narrative logs without replay capability**: Traces are useless without reproduction
- **Excessive tracing overhead**: Sample judiciously
- **Ignoring serialization failures**: If input can't serialize, trace is useless

---

*Zen Principle: The story of the thought is the thought made eternal; replay is resurrection.*

---

## See Also

- [archetypes.md](../archetypes.md) - The Witness archetype
- [w-gents/](../w-gents/) - Visualization integration
- [reliability.md](../reliability.md) - Error tracking and recovery
- [testing.md](../testing.md) - SpyAgent (related observation pattern)
