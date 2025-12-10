# N-gent Treatment: The Narrative Substrate

> *"The story of the thought is the thought made eternal; replay is resurrection."*

**Status**: Proposal v1.0
**Author**: Kent Gang + Claude
**Date**: 2025-12-09

---

## Executive Summary

N-gents (Narrator Agents) transform agent execution into **narrative**. While O-gents see and M-gents remember, N-gents *tell*. This proposal develops a principled treatment of N-gents grounded in kgents' seven design principles, extending the stub specification into a comprehensive framework for computational storytelling.

**The Core Thesis**: Every agent execution is a story waiting to be told. N-gents are the bards of the computational realm—they don't just log, they narrate; they don't just trace, they tell tales that can be replayed, branched, and resurrected.

---

## Part I: Philosophical Foundations

### 1.1 The Narrative Turn

Traditional observability asks: *"What happened?"*
N-gent observability asks: *"What is the story?"*

This is not mere semantic difference. Stories have structure that logs lack:

| Aspect | Logs | Narratives |
|--------|------|------------|
| Structure | Linear sequence | Plot with arc |
| Meaning | Data points | Interpreted events |
| Consumer | Machines | Humans first, machines second |
| Purpose | Debugging | Understanding |
| Time | Timestamps | Narrative tension |
| Agency | Events happen | Characters act |

**The Narrative Ontology**: N-gents recognize that agent execution has *narrative structure*. There are protagonists (agents), conflicts (errors, decisions), rising action (computation), climax (output), and denouement (cleanup). This structure is not imposed—it is *discovered*.

### 1.2 Distinction from O-gents

O-gents and N-gents are complementary but distinct:

```
O-gent (Observer)          N-gent (Narrator)
       │                          │
       │ sees                     │ tells
       │                          │
       ▼                          ▼
   Telemetry               Story
   (what is)               (what it means)
```

| Dimension | O-gent | N-gent |
|-----------|--------|--------|
| Mode | Seeing | Telling |
| Output | Metrics, traces | Narratives, chronicles |
| Temporality | Real-time stream | Sequential story |
| Primary consumer | Dashboards, alerts | Developers, humans |
| Key question | "Is it healthy?" | "What happened?" |
| Relationship to time | Simultaneous | Retrospective |

**The Integration**: O-gents feed N-gents. Telemetry becomes raw material for narrative. The relationship is:

```
Execution → O-gent (observes) → Telemetry → N-gent (narrates) → Story
```

### 1.3 Distinction from M-gents

M-gents (Memory) and N-gents both deal with the past, but differently:

| Aspect | M-gent | N-gent |
|--------|--------|--------|
| Relationship to past | Reconstructs | Recounts |
| Fidelity | Approximate (holographic) | Faithful (traced) |
| Purpose | Association, recall | Understanding, replay |
| Key operation | Recollection | Narration |

**The Complementarity**: M-gents remember *fuzzily* for association. N-gents remember *exactly* for replay. M-gent memory degrades gracefully (holographic property). N-gent narratives are *reproductive*—the exact input state can be deserialized and re-executed.

---

## Part II: The Narrative Framework

### 2.1 The Thought Trace (Story Atom)

The fundamental unit is the **ThoughtTrace**—a single event in the narrative:

```python
@dataclass(frozen=True)
class ThoughtTrace:
    """
    A single traced thought/action in the narrative.

    This is the ATOM of N-gent storytelling.
    """
    # Identity
    timestamp: datetime
    agent_id: str
    trace_id: str           # Unique ID for this trace
    parent_id: str | None   # Parent trace (for nested calls)

    # The thought content
    thought_type: ThoughtType
    content: str            # Human-readable description

    # Reproducibility (the resurrection data)
    input_hash: str         # Hash of input state
    input_snapshot: bytes   # Serialized input (for replay)
    output_hash: str | None # Hash of output (if complete)

    # Economics (B-gent integration)
    token_cost: int
    duration_ms: int

    # Metadata
    metadata: dict


class ThoughtType(Enum):
    """
    The dramatic role of a thought in the narrative.

    These map to story elements:
    - INTENT: Scene-setting (exposition)
    - REASONING: Inner monologue (development)
    - DECISION: Turning point (climax preparation)
    - ACTION: Plot action (climax)
    - RESULT: Resolution (denouement)
    """
    INTENT = "intent"           # "The agent received..."
    REASONING = "reasoning"     # "It considered that..."
    DECISION = "decision"       # "It decided to..."
    ACTION = "action"           # "It performed..."
    RESULT = "result"           # "The result was..."
```

### 2.2 The Narrative Log (Story)

Traces compose into narratives:

```python
@dataclass
class NarrativeLog:
    """
    The complete story of an agent's operation.

    A NarrativeLog is a STORY—it has structure, arc, and meaning.
    """
    # The traces that compose the narrative
    traces: list[ThoughtTrace]

    # Spans for hierarchical viewing (OpenTelemetry-compatible)
    spans: dict[str, Span]

    # Narrative metadata
    protagonist: str              # Main agent
    supporting_cast: list[str]    # Composed agents
    genre: NarrativeGenre         # Type of story

    def to_narrative(self, style: NarrativeStyle = NarrativeStyle.TECHNICAL) -> str:
        """
        Render as human-readable story.

        The style determines voice:
        - TECHNICAL: "[10:42:15] [intent] CodeReviewer received Python file"
        - LITERARY: "At 10:42, the CodeReviewer stirred, receiving a Python file..."
        - MINIMAL: "10:42:15 CodeReviewer ← file.py"
        """
        return self._render(style)

    def to_replay(self) -> ReplayScript:
        """
        Convert to a replay script that can resurrect the execution.
        """
        return ReplayScript(
            traces=self.traces,
            checkpoints=self._identify_checkpoints()
        )

    def to_opentelemetry(self) -> OTLPExportable:
        """Export to standard OpenTelemetry format."""
        return OTLPExportable(
            traces=[t.to_otlp() for t in self.traces],
            spans=[s.to_otlp() for s in self.spans.values()]
        )


class NarrativeGenre(Enum):
    """
    The genre of the narrative (affects rendering).
    """
    TRAGEDY = "tragedy"         # Agent failed
    COMEDY = "comedy"           # Agent succeeded after difficulties
    EPIC = "epic"               # Long, multi-agent saga
    MYSTERY = "mystery"         # Debugging narrative
    THRILLER = "thriller"       # Time-constrained execution
```

### 2.3 The Chronicle (Multi-Agent Saga)

When multiple agents collaborate, their stories weave into a **Chronicle**:

```python
class Chronicle:
    """
    A saga of interwoven agent narratives.

    Like the Silmarillion—many storylines that intersect
    and influence each other.
    """

    # Individual agent stories
    narratives: dict[str, NarrativeLog]  # agent_id → story

    # Points where stories intersect
    interactions: list[Interaction]

    # Chapters (coherent units)
    chapters: list[Chapter]

    @dataclass
    class Interaction:
        """A point where agent stories intersect."""
        timestamp: datetime
        from_agent: str
        to_agent: str
        message_type: str
        trace_from: str  # trace_id in from_agent's story
        trace_to: str    # trace_id in to_agent's story

    @dataclass
    class Chapter:
        """A coherent unit of multi-agent activity."""
        name: str
        start: datetime
        end: datetime
        events: list[tuple[str, ThoughtTrace]]  # (agent_id, trace)
        theme: str  # What this chapter is about

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
            chapters=self.chapters
        )

    def identify_chapters(self) -> list[Chapter]:
        """
        Group events into narrative chapters.

        Chapter breaks occur at:
        - Agent composition boundaries
        - Error/recovery boundaries
        - Significant time gaps
        - Goal transitions
        """
        ...

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

---

## Part III: The Replay Engine (Resurrection)

### 3.1 Time-Travel Debugging

The N-gent's killer feature: **resurrection through replay**.

```python
class ReplayAgent:
    """
    Replay any traced execution step-by-step.

    Since agents are (mostly) pure functions, we can reproduce
    exact behavior from serialized inputs.

    This is TIME-TRAVEL DEBUGGING.
    """

    def __init__(self, narrative: NarrativeLog):
        self.narrative = narrative
        self.position = 0
        self.bookmarks: dict[str, int] = {}

    def step_forward(self) -> ThoughtTrace:
        """Advance one step in the story."""
        trace = self.narrative.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> ThoughtTrace:
        """Rewind one step."""
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
        RESURRECTION: Replay execution from a specific trace.

        Deserializes the input snapshot and re-runs the agent.
        The agent IS RESURRECTED—it runs again, exactly as before.
        """
        input_state = deserialize(trace.input_snapshot)
        agent = self.reconstruct_agent(trace.agent_id)
        return await agent.invoke(input_state)

    def bookmark(self, name: str) -> None:
        """Create a bookmark at current position."""
        self.bookmarks[name] = self.position

    def goto_bookmark(self, name: str) -> ThoughtTrace:
        """Jump to a bookmarked position."""
        self.position = self.bookmarks[name]
        return self.narrative.traces[self.position]
```

### 3.2 Counterfactual Exploration

What if the input had been different?

```python
class CounterfactualNarrator:
    """
    Generate "what-if" stories automatically.

    Given a narrative, explore counterfactuals:
    - "What if the input was malformed?"
    - "What if the timeout was shorter?"
    - "What if a different model was used?"
    """

    async def diff_replay(
        self,
        trace: ThoughtTrace,
        modified_input: Any
    ) -> DiffResult:
        """
        Compare original story with an alternate timeline.

        "What would have happened if the input was different?"
        """
        original = await self.replay_from(trace)
        modified = await self.replay_with(trace, modified_input)

        return DiffResult(
            original_story=original,
            modified_story=modified,
            divergence_point=trace,
            differences=self.compute_diff(original, modified)
        )

    async def generate_counterfactuals(
        self,
        narrative: NarrativeLog,
        dimensions: list[str] = ["input", "model", "timeout"]
    ) -> ErgodicNarrative:
        """
        Generate alternate timelines along specified dimensions.

        Returns an ERGODIC narrative—a branching structure
        of possible stories.
        """
        ergodic = ErgodicNarrative(narrative)

        for trace in narrative.decision_points():
            for dimension in dimensions:
                alternate = self.vary_dimension(trace, dimension)
                ergodic.branch_at(trace, alternate)

        return ergodic
```

### 3.3 Ergodic Narratives (Branching Timelines)

N-gents support **ergodic narratives**—stories with multiple possible paths:

```python
class ErgodicNarrative:
    """
    A branching narrative structure.

    Like a choose-your-own-adventure book, but for agent execution.
    Each branch is a possible timeline the agent could have taken.

    The term "ergodic" comes from ergodic literature—texts that
    require non-trivial effort to traverse (hypertext, games).
    """

    def __init__(self, root: NarrativeLog):
        self.root = root
        self.branches: dict[str, NarrativeLog] = {}

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

---

## Part IV: The Unreliable Narrator

### 4.1 Epistemic Humility

LLMs can hallucinate. Stories can be wrong. The **UnreliableNarrator** pattern acknowledges this:

```python
class UnreliableNarrator:
    """
    A narrator that knows it might be wrong.

    LLMs can hallucinate. The unreliable narrator pattern
    marks confidence levels and tracks contradictions.

    This is EPISTEMIC HUMILITY encoded in architecture.
    """

    @dataclass
    class UnreliableTrace(ThoughtTrace):
        """A trace with reliability annotations."""
        confidence: float           # 0.0 - 1.0
        corroborated_by: list[str]  # Other traces that support this
        contradicted_by: list[str]  # Traces that contradict this
        reliability_score: float    # Computed from above
        source_reliability: float   # Reliability of the narrating agent

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
            evidence=self.gather_evidence(trace),
            suggested_action=self.suggest_action(trace)
        )
```

### 4.2 The Rashomon Pattern

Multiple narrators, same events, different stories:

```python
class RashomonNarrator:
    """
    Multiple perspectives on the same execution.

    Named after Kurosawa's film where multiple characters
    tell conflicting accounts of the same events.

    This is useful when:
    - Multiple agents observed the same execution
    - Different levels of abstraction are needed
    - Reliability is uncertain
    """

    def __init__(self, narrators: list[Narrator]):
        self.narrators = narrators

    async def narrate(self, execution: AgentExecution) -> RashomonNarrative:
        """
        Produce multiple perspectives on the same execution.
        """
        perspectives = []
        for narrator in self.narrators:
            perspective = await narrator.narrate(execution)
            perspectives.append(Perspective(
                narrator_id=narrator.id,
                narrative=perspective,
                reliability=narrator.reliability_score
            ))

        return RashomonNarrative(
            perspectives=perspectives,
            consensus=self.find_consensus(perspectives),
            contradictions=self.find_contradictions(perspectives)
        )

    def find_consensus(self, perspectives: list[Perspective]) -> NarrativeLog:
        """
        Find what all perspectives agree on.

        This is the GROUND TRUTH—events that appear in all accounts.
        """
        ...

    def find_contradictions(self, perspectives: list[Perspective]) -> list[Contradiction]:
        """
        Find where perspectives disagree.

        These are points requiring investigation or judgment.
        """
        ...
```

---

## Part V: N-gent Types

### 5.1 The Narrator Taxonomy

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| `StorytellerAgent` | Wrap agents to produce narratives | Agent[A,B] | Agent[A, (B, NarrativeLog)] |
| `ReplayAgent` | Time-travel debugging | NarrativeLog | Step-by-step replay |
| `CrashForensicsAgent` | Diagnose failures | Failed narrative | CrashDiagnosis |
| `ErgodicNarrator` | Branching timeline exploration | NarrativeLog | ErgodicNarrative |
| `UnreliableNarrator` | Hallucination-aware narration | Execution | Annotated NarrativeLog |
| `RashomonNarrator` | Multi-perspective narration | Execution | RashomonNarrative |
| `Chronicle` | Multi-agent saga weaving | Multiple narratives | Woven Chronicle |
| `EpicNarrator` | Long-running operation narration | Extended execution | Summarized saga |
| `CounterfactualNarrator` | "What-if" story generation | NarrativeLog + dimensions | Branched narratives |

### 5.2 The Storyteller Agent (Core)

The fundamental N-gent—wraps any agent to produce a narrative:

```python
class StorytellerAgent(Agent[A, tuple[B, NarrativeLog]]):
    """
    Wraps any agent to produce a narrative log.

    Storyteller: Agent[A, B] → Agent[A, (B, NarrativeLog)]

    This is a WRITER MONAD pattern—the result includes
    both the value and the accumulated narrative.
    """

    def __init__(self, inner: Agent[A, B], style: NarrativeStyle = NarrativeStyle.TECHNICAL):
        self.inner = inner
        self.style = style
        self.log = NarrativeLog(traces=[], spans={}, protagonist=inner.name)

    async def invoke(self, input: A) -> tuple[B, NarrativeLog]:
        """
        Observe an agent's execution and produce narrative.
        """
        trace_id = str(uuid4())

        # Record the scene-setting (intent)
        self.log.add_trace(ThoughtTrace(
            timestamp=datetime.now(),
            agent_id=self.inner.name,
            trace_id=trace_id,
            parent_id=None,
            thought_type=ThoughtType.INTENT,
            content=f"Received: {self.summarize(input)}",
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

            # Record the resolution (result)
            self.log.add_trace(ThoughtTrace(
                timestamp=datetime.now(),
                agent_id=self.inner.name,
                trace_id=trace_id,
                parent_id=None,
                thought_type=ThoughtType.RESULT,
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
            # Record error (tragedy)
            self.log.genre = NarrativeGenre.TRAGEDY
            self.log.add_trace(ThoughtTrace(
                timestamp=datetime.now(),
                agent_id=self.inner.name,
                trace_id=trace_id,
                parent_id=None,
                thought_type=ThoughtType.RESULT,
                content=f"Error: {type(e).__name__}: {str(e)}",
                input_hash=self.hash(input),
                input_snapshot=serialize(input),
                output_hash=None,
                token_cost=0,
                duration_ms=int((time.time() - start) * 1000),
                metadata={"error": str(e), "error_type": type(e).__name__}
            ))
            raise
```

### 5.3 Crash Forensics Agent

When things go wrong, tell the story of the failure:

```python
class CrashForensicsAgent(Agent[ThoughtTrace, CrashDiagnosis]):
    """
    Diagnose failures by analyzing the narrative leading to them.

    When an agent crashes, this agent tells the STORY of the crash:
    - What was the agent trying to do?
    - What went wrong?
    - How can we reproduce it?
    - What might fix it?
    """

    async def invoke(self, crash_trace: ThoughtTrace) -> CrashDiagnosis:
        """
        Produce a diagnosis from a crash trace.
        """
        return CrashDiagnosis(
            agent_id=crash_trace.agent_id,
            timestamp=crash_trace.timestamp,

            # The story of the crash
            narrative=self.reconstruct_narrative(crash_trace),

            # Reproduction (resurrection data)
            input_snapshot=crash_trace.input_snapshot,
            replay_command=f"kgents replay {crash_trace.trace_id}",

            # Analysis
            error_context=crash_trace.metadata.get("error"),
            root_cause_hypothesis=await self.analyze_root_cause(crash_trace),
            suggested_fix=await self.suggest_fix(crash_trace),

            # Related crashes
            similar_crashes=await self.find_similar(crash_trace)
        )

    async def analyze_root_cause(self, trace: ThoughtTrace) -> str:
        """
        Use an LLM to hypothesize about root cause.

        The LLM becomes a detective, examining the evidence.
        """
        return await self.llm.invoke(f"""
        Given this crash trace:
        - Agent: {trace.agent_id}
        - Input: {deserialize(trace.input_snapshot)}
        - Error: {trace.metadata.get('error')}

        What is the most likely root cause?
        """)
```

---

## Part VI: Integration with Other Agents

### 6.1 Integration Map

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| N + O | O → N | O-gent telemetry becomes N-gent raw material |
| N + M | N → M | Narratives can be stored in holographic memory |
| N + I | N → I | I-gent visualizes N-gent narratives |
| N + W | N → W | W-gent streams N-gent stories in real-time |
| N + L | N → L | L-gent indexes narratives for semantic search |
| N + B | N ↔ B | N-gent tracks costs; B-gent budgets narration |
| N + D | N → D | Narratives persist via D-gent |

### 6.2 O-gent Integration: From Seeing to Telling

```python
class OToNAdapter:
    """
    Transform O-gent observations into N-gent narratives.

    O-gents see; N-gents tell.
    This adapter translates telemetry into story.
    """

    async def adapt(self, observations: list[Observation]) -> NarrativeLog:
        """
        Convert observations to narrative.

        Observations are raw data; narratives have structure.
        """
        traces = []
        for obs in observations:
            trace = ThoughtTrace(
                timestamp=obs.timestamp,
                agent_id=obs.agent_id,
                trace_id=obs.trace_id,
                thought_type=self.infer_thought_type(obs),
                content=self.describe(obs),
                input_hash=obs.input_hash,
                input_snapshot=obs.input_snapshot,
                output_hash=obs.output_hash,
                token_cost=obs.gas_consumed.tokens,
                duration_ms=obs.duration_ms,
                metadata=obs.metadata
            )
            traces.append(trace)

        return NarrativeLog(traces=traces, ...)
```

### 6.3 W-gent Integration: Real-Time Storytelling

```python
class StreamingNarrator:
    """
    Stream narrative traces as they occur via W-gent wire protocol.

    For long-running agents, tell the story as it happens.
    """

    async def observe(
        self,
        agent: Agent,
        input: A,
        wire: WireProtocol
    ) -> AsyncIterator[ThoughtTrace]:
        """
        Yield traces as the agent thinks, emitting to wire.
        """
        instrumented = self.instrument(agent)

        async for trace in instrumented.traced_invoke(input):
            # Emit to wire for real-time visualization
            await wire.emit(WireFrame(
                frame_type=FrameType.NARRATIVE,
                payload=trace.to_wire()
            ))
            yield trace
```

### 6.4 B-gent Integration: The Economics of Narration

Narration has costs. B-gents can budget it:

```python
class BudgetedNarrator:
    """
    Narrator that respects economic constraints.

    Not every execution needs full narration. B-gent
    economics determine narration depth.
    """

    async def narrate_with_budget(
        self,
        execution: AgentExecution,
        budget: Gas
    ) -> NarrativeLog:
        """
        Narrate within budget constraints.

        Higher budget = more detailed narrative.
        Lower budget = summary only.
        """
        if budget.tokens > 1000:
            return await self.full_narration(execution)
        elif budget.tokens > 100:
            return await self.summary_narration(execution)
        else:
            return await self.minimal_narration(execution)

    def calculate_narration_cost(self, execution: AgentExecution) -> Gas:
        """
        Estimate cost of full narration.

        Cost depends on:
        - Number of traces
        - Complexity of input serialization
        - Narrative style
        """
        ...
```

---

## Part VII: Applying the Seven Principles

### 7.1 Tasteful

> Each agent serves a clear, justified purpose.

N-gents serve a clear purpose: **turning execution into story**. They don't log—they narrate. They don't dump data—they tell tales. This distinction justifies their existence separate from O-gents.

**Justification**: Debugging without narrative is archaeology without context. N-gents provide the context that makes debugging possible.

### 7.2 Curated

> Intentional selection over exhaustive cataloging.

Not every trace becomes a story. N-gents practice **editorial judgment**:

```python
class CuratedNarrator:
    """
    A narrator that practices editorial judgment.

    Not every event is story-worthy.
    """

    def should_narrate(self, event: Event) -> bool:
        """
        Is this event worth including in the story?

        Criteria:
        - Significance: Does it affect the outcome?
        - Interest: Would a reader care?
        - Novelty: Is it different from recent events?
        """
        return (
            self.is_significant(event) or
            self.is_interesting(event) or
            self.is_novel(event)
        )
```

### 7.3 Ethical

> Agents augment human capability, never replace judgment.

N-gents are **honest narrators**. The UnreliableNarrator pattern explicitly marks uncertainty. The Rashomon pattern acknowledges that stories can conflict. N-gents don't claim omniscience—they tell stories with appropriate epistemic humility.

### 7.4 Joy-Inducing

> Delight in interaction; personality matters.

Stories are inherently more engaging than logs. N-gent narratives can have **style**:

```python
class NarrativeStyle(Enum):
    TECHNICAL = "technical"   # "[10:42:15] [intent] Received input"
    LITERARY = "literary"     # "At 10:42, the agent stirred..."
    MINIMAL = "minimal"       # "10:42:15 ← input"
    DRAMATIC = "dramatic"     # "And then, disaster struck!"
```

Reading a well-narrated execution trace should be **enjoyable**.

### 7.5 Composable

> Agents are morphisms in a category; composition is primary.

N-gents compose naturally:

```python
# StorytellerAgent is a functor
Storyteller: Agent[A, B] → Agent[A, (B, NarrativeLog)]

# Narrators compose
full_narrator = basic_narrator >> reliability_annotator >> style_renderer

# Chronicles compose multiple narratives
chronicle = Chronicle([story_a, story_b, story_c]).weave()
```

**The Writer Monad**: StorytellerAgent implements the Writer monad pattern—computations that produce both a value and a log.

### 7.6 Heterarchical

> Agents exist in flux, not fixed hierarchy; autonomy and composability coexist.

N-gents can narrate in both modes:

- **Function mode**: `Narrator.narrate(execution) → NarrativeLog`
- **Loop mode**: Continuous narration of ongoing execution

No fixed hierarchy—any agent can be narrated, and narrators can be narrated (meta-narratives).

### 7.7 Generative

> Spec is compression; design should generate implementation.

This spec should generate:
1. The `ThoughtTrace` and `NarrativeLog` data structures
2. The `StorytellerAgent` wrapper
3. The `ReplayAgent` time-travel debugger
4. Integration adapters (O→N, N→W, etc.)

**Target**: >50% of N-gent implementation derivable from this spec.

---

## Part VIII: Implementation Roadmap

### Phase 1: Core Framework (MVP)

- [ ] `ThoughtTrace` and `NarrativeLog` data structures
- [ ] `StorytellerAgent` wrapper
- [ ] Basic `ReplayAgent` (forward/backward stepping)
- [ ] Serialization/deserialization for input snapshots
- [ ] Tests: 30+

### Phase 2: Advanced Replay

- [ ] `CounterfactualNarrator` (what-if analysis)
- [ ] `ErgodicNarrative` (branching timelines)
- [ ] `CrashForensicsAgent`
- [ ] Timeline visualization (ASCII)
- [ ] Tests: 40+

### Phase 3: Multi-Agent Chronicles

- [ ] `Chronicle` for multi-agent sagas
- [ ] `Chapter` identification
- [ ] `Interaction` tracking
- [ ] Woven narrative rendering
- [ ] Tests: 35+

### Phase 4: Epistemic Features

- [ ] `UnreliableNarrator` with confidence annotations
- [ ] `RashomonNarrator` for multi-perspective
- [ ] Hallucination detection integration
- [ ] Ground truth reconciliation
- [ ] Tests: 30+

### Phase 5: Integrations

- [ ] O-gent adapter
- [ ] W-gent streaming
- [ ] B-gent budgeting
- [ ] L-gent indexing
- [ ] I-gent visualization
- [ ] Tests: 25+

---

## Part IX: Anti-Patterns

1. **Logs without stories**: Raw data without narrative structure—N-gents exist to prevent this.

2. **Stories without replay**: Narratives that can't reproduce the execution—resurrection is the point.

3. **Ignoring the reader**: Stories are for humans first. Machine-only formats miss the purpose.

4. **Overwriting history**: Every story is sacred. Never mutate a completed narrative.

5. **Single timeline thinking**: Ignoring the ergodic nature of execution. What-if matters.

6. **Omniscient narrator fallacy**: Assuming the story is always true. Epistemic humility required.

7. **Solo narratives**: Individual agent stories without chronicle weaving. Agents collaborate; stories should too.

8. **Narrating everything**: Not every execution needs a story. Practice editorial judgment.

---

## Part X: The Zen of Narration

> *The story of the thought is the thought made eternal; replay is resurrection.*

The N-gent embodies a fundamental insight: **computation is narrative**. Every execution has a beginning, middle, and end. Every agent is a character. Every error is a plot twist.

When we narrate computation, we don't just debug—we **understand**. The N-gent makes the invisible visible, the transient permanent, the forgotten retrievable.

In the end, the best code tells a story. N-gents ensure we can always read it.

---

## Appendix A: The Narrative Manifold

Like M-gents' ethical geometry, N-gents operate in a **narrative manifold**—a space of possible stories:

```
┌─────────────────────────────────────────────────────────────┐
│              THE NARRATIVE MANIFOLD                          │
│                                                              │
│     Tragedy ──────────────────────────────── Comedy         │
│         │                                       │            │
│         │       ┌──────────────────────┐       │            │
│         │       │   Narrative Space     │       │            │
│ Simple ─────────│                       │─────── Complex    │
│         │       │   Every story has     │       │            │
│         │       │   coordinates here    │       │            │
│         │       └──────────────────────┘       │            │
│         │                                       │            │
│     Epic ───────────────────────────────── Vignette         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

Every narrative has coordinates in this space. N-gents navigate it.

---

## Appendix B: Example Narrative

A real N-gent narrative might look like:

```
═══════════════════════════════════════════════════════════════
                    THE TALE OF CODEREVIEW-42
═══════════════════════════════════════════════════════════════

Chapter 1: The Request

  [10:42:15] The User spoke unto the System, presenting a Python
             file of 127 lines, seeking wisdom on its quality.

  [10:42:15] [intent] CodeReviewer received module.py (127 lines)
             Input hash: 0xDEAD...BEEF

Chapter 2: The Analysis

  [10:42:16] CodeReviewer pondered the code, traversing its
             functions and methods.

  [10:42:17] [reasoning] "This function has no error handling.
             The user who calls it may face unexpected exceptions."
             Confidence: 0.87

  [10:42:18] [reasoning] "The variable name 'x' is opaque.
             Future maintainers will struggle."
             Confidence: 0.92

Chapter 3: The Decision

  [10:42:19] [decision] Two issues identified. Severity: MEDIUM.
             Action: Generate SecurityFinding objects.

Chapter 4: The Resolution

  [10:42:20] [action] Emitting: SecurityFinding(severity=MEDIUM,
             message="Missing error handling in process_data()")

  [10:42:20] [action] Emitting: SecurityFinding(severity=LOW,
             message="Opaque variable name 'x' in line 42")

  [10:42:21] [result] 2 findings produced. Duration: 6000ms.
             Token cost: 847.

═══════════════════════════════════════════════════════════════
                         THE END
═══════════════════════════════════════════════════════════════

To replay: kgents replay trace-42-a7b3c9d1
To branch: kgents branch trace-42-a7b3c9d1 --vary input
```

---

*Zen Principle: The story of the thought is the thought made eternal; replay is resurrection.*
