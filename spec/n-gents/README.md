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

## Ergodic Narratives (Branching Timelines)

N-gents support **ergodic narratives**—stories with multiple possible paths:

```python
class ErgodicNarrative:
    """
    A branching narrative structure.

    Like a choose-your-own-adventure book, but for agent execution.
    Each branch is a possible timeline the agent could have taken.
    """

    def __init__(self, root: NarrativeLog):
        self.root = root
        self.branches: dict[str, NarrativeLog] = {}  # branch_id → story

    def branch_at(self, trace: ThoughtTrace, alternate_input: Any) -> str:
        """
        Create an alternate timeline from a decision point.

        "What if the agent had received different input here?"
        """
        branch_id = f"branch_{trace.trace_id}_{hash(alternate_input)}"
        alternate_story = self.replay_with_modification(trace, alternate_input)
        self.branches[branch_id] = alternate_story
        return branch_id

    def compare_timelines(self, branch_a: str, branch_b: str) -> TimelineDiff:
        """
        Compare two alternate timelines.

        Useful for "what-if" analysis: "If we had used GPT-4 instead
        of Claude here, how would the story differ?"
        """
        story_a = self.branches[branch_a]
        story_b = self.branches[branch_b]

        return TimelineDiff(
            divergence_point=self.find_divergence(story_a, story_b),
            a_only_events=self.events_unique_to(story_a, story_b),
            b_only_events=self.events_unique_to(story_b, story_a),
            outcome_diff=self.compare_outcomes(story_a, story_b)
        )

    def visualize(self) -> str:
        """
        Render branching structure as ASCII tree.

        main: ═══════════════════════════════►
                    ╲
                     ╲ branch_gpt4: ═══════►
                      ╲
                       ╲ branch_retry: ════►
        """
        ...
```

### The Counterfactual Pattern

```python
class CounterfactualNarrator:
    """
    Generate "what-if" stories automatically.

    Given a narrative, explore counterfactuals:
    - "What if the input was malformed?"
    - "What if the timeout was shorter?"
    - "What if a different model was used?"
    """

    async def generate_counterfactuals(
        self,
        narrative: NarrativeLog,
        dimensions: list[str] = ["input", "model", "timeout"]
    ) -> list[ErgodicNarrative]:
        """Generate alternate timelines along specified dimensions."""
        ergodic = ErgodicNarrative(narrative)

        for trace in narrative.decision_points():
            for dimension in dimensions:
                alternate = self.vary_dimension(trace, dimension)
                ergodic.branch_at(trace, alternate)

        return ergodic
```

---

## The Unreliable Narrator

Sometimes the story itself is suspect. The **UnreliableNarrator** pattern handles hallucinations and inconsistencies:

```python
class UnreliableNarrator:
    """
    A narrator that knows it might be wrong.

    LLMs can hallucinate. The unreliable narrator pattern
    marks confidence levels and tracks contradictions.
    """

    @dataclass
    class UnreliableTrace(ThoughtTrace):
        confidence: float  # 0.0 - 1.0
        corroborated_by: list[str]  # Other traces that support this
        contradicted_by: list[str]  # Traces that contradict this
        reliability_score: float  # Computed from above

    async def narrate(self, execution: AgentExecution) -> NarrativeLog:
        """
        Produce a narrative with reliability annotations.
        """
        traces = []
        for event in execution:
            trace = self.trace_event(event)

            # Check for self-contradiction
            contradictions = self.find_contradictions(trace, traces)
            if contradictions:
                trace.contradicted_by = contradictions
                trace.reliability_score *= 0.5  # Penalize contradictions

            # Check for corroboration
            corroborations = self.find_corroborations(trace, traces)
            if corroborations:
                trace.corroborated_by = corroborations
                trace.reliability_score *= 1.2  # Boost corroboration

            traces.append(trace)

        return NarrativeLog(traces=traces)

    def detect_hallucination(self, trace: UnreliableTrace) -> HallucinationReport:
        """
        Flag potential hallucinations.

        Signs: High confidence + zero corroboration + contradicts ground truth
        """
        is_hallucination = (
            trace.confidence > 0.8 and
            len(trace.corroborated_by) == 0 and
            self.contradicts_ground_truth(trace)
        )

        return HallucinationReport(
            trace=trace,
            is_hallucination=is_hallucination,
            evidence=self.gather_evidence(trace)
        )
```

---

## Chronicle: Multi-Agent Sagas

When multiple agents collaborate, their individual stories weave into a **Chronicle**:

```python
class Chronicle:
    """
    A saga of interwoven agent narratives.

    Like the Silmarillion—many storylines that intersect
    and influence each other.
    """

    def __init__(self):
        self.narratives: dict[str, NarrativeLog] = {}  # agent_id → story
        self.interactions: list[Interaction] = []

    @dataclass
    class Interaction:
        """A point where agent stories intersect."""
        timestamp: datetime
        from_agent: str
        to_agent: str
        message_type: str
        trace_from: str  # trace_id in from_agent's story
        trace_to: str    # trace_id in to_agent's story

    def add_narrative(self, agent_id: str, narrative: NarrativeLog):
        """Add an agent's story to the chronicle."""
        self.narratives[agent_id] = narrative
        self.detect_interactions(agent_id, narrative)

    def weave(self) -> WovenNarrative:
        """
        Weave all narratives into a single timeline.

        Interleaves events by timestamp, showing the
        full saga of agent collaboration.
        """
        all_events = []
        for agent_id, narrative in self.narratives.items():
            for trace in narrative.traces:
                all_events.append((trace.timestamp, agent_id, trace))

        all_events.sort(key=lambda x: x[0])

        return WovenNarrative(
            events=all_events,
            interactions=self.interactions,
            chapters=self.identify_chapters(all_events)
        )

    def identify_chapters(self, events: list) -> list[Chapter]:
        """
        Group events into narrative chapters.

        A chapter is a coherent unit of activity—
        like "The Research Phase" or "The Conflict Resolution".
        """
        chapters = []
        current_chapter = Chapter(name="Prologue")

        for timestamp, agent_id, trace in events:
            # New chapter on significant transitions
            if self.is_chapter_break(trace, current_chapter):
                chapters.append(current_chapter)
                current_chapter = Chapter(
                    name=self.generate_chapter_name(trace),
                    start=timestamp
                )

            current_chapter.add_event(agent_id, trace)

        chapters.append(current_chapter)
        return chapters

    def to_saga(self) -> str:
        """
        Render the full chronicle as a readable saga.

        "Chapter 1: The Request

         At 10:42, the User spoke unto the System...
         CodeReviewer stirred, receiving the sacred Python file.

         Meanwhile, in the depths of the Banker's domain,
         tokens flowed like water..."
        """
        ...
```

### The Epic Pattern

For long-running multi-agent operations:

```python
class EpicNarrator:
    """
    Narrator for epic-scale operations.

    Manages chronicles that span hours/days and
    involve dozens of agents.
    """

    def __init__(self):
        self.chronicle = Chronicle()
        self.summaries: list[Summary] = []  # Rolling summaries

    async def summarize_chapter(self, chapter: Chapter) -> Summary:
        """
        Compress a chapter into a summary.

        For epics, we can't store every detail—
        we need the Rolling Stone strategy.
        """
        summary_agent = self.get_summarizer()
        return await summary_agent.invoke(SummaryRequest(
            chapter=chapter,
            max_tokens=500,
            preserve=["key_decisions", "failures", "interactions"]
        ))

    def the_previously_on(self) -> str:
        """
        Generate "Previously on..." recap.

        Like a TV show recap: "Last time, the CodeReviewer
        found a critical bug, but the Fixer failed to patch it..."
        """
        return "\n".join([
            f"• {s.one_liner}" for s in self.summaries[-5:]
        ])
```

---

## N-gent Types (Extended)

| Agent | Purpose |
|-------|---------|
| `StorytellerAgent` | Wrap agents to produce narratives |
| `ReplayAgent` | Time-travel debugging |
| `CrashForensicsAgent` | Diagnose failures |
| `ErgodicNarrator` | Branching timeline exploration |
| `UnreliableNarrator` | Hallucination-aware narration |
| `Chronicle` | Multi-agent saga weaving |
| `EpicNarrator` | Long-running operation narration |
| `CounterfactualNarrator` | "What-if" story generation |

---

## Anti-Patterns

- **Logs without stories**: Raw data without narrative structure
- **Stories without replay**: Can't reproduce from the story
- **Ignoring the reader**: Stories are for humans, not just machines
- **Overwriting history**: Every story is sacred
- **Single timeline thinking**: Ignoring the ergodic nature of execution
- **Omniscient narrator fallacy**: Assuming the story is always true
- **Solo narratives**: Individual agent stories without chronicle weaving

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
