# The Narrator Specification: Historian, Bard, Echo

> *"Collect stones. Cast shadows only when the sun is out."*

---

## Overview

This specification details the three components of the N-gent architecture:

1. **The Historian** (Write-Time): Invisible crystal collection
2. **The Bard** (Read-Time): Story generation from crystals
3. **The Echo Chamber** (Replay): Simulation, not resurrection

---

## Part I: The Crystal (SemanticTrace)

### 1.1 Core Data Structure

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class Determinism(Enum):
    """
    Classification of trace reproducibility.
    """
    DETERMINISTIC = "deterministic"   # Math, lookups
    PROBABILISTIC = "probabilistic"   # LLM calls
    CHAOTIC = "chaotic"               # External APIs


@dataclass(frozen=True)
class SemanticTrace:
    """
    The Crystal. Pure, compressed reality. No prose.

    This is the fundamental unit of N-gent recording.
    """
    # Identity
    trace_id: str
    parent_id: str | None
    timestamp: datetime

    # Agent
    agent_id: str
    agent_genus: str

    # Action (semantic atom)
    action: str

    # Data
    inputs: dict
    outputs: dict | None

    # Reproducibility
    input_hash: str
    input_snapshot: bytes
    output_hash: str | None

    # Economics
    gas_consumed: int
    duration_ms: int

    # Embedding
    vector: list[float] | None

    # Classification
    determinism: Determinism
    metadata: dict
```

### 1.2 Action Vocabulary

Actions are **semantic atoms**, not narrative prose:

| Action | Meaning | Determinism |
|--------|---------|-------------|
| `INVOKE` | Agent invocation | PROBABILISTIC |
| `COMPOSE` | Agent composition | DETERMINISTIC |
| `DECIDE` | Decision point | PROBABILISTIC |
| `LOOKUP` | Data retrieval | DETERMINISTIC |
| `CALL_API` | External API call | CHAOTIC |
| `TRANSFORM` | Data transformation | DETERMINISTIC |
| `GENERATE` | LLM generation | PROBABILISTIC |
| `PARSE` | Parsing operation | DETERMINISTIC |
| `VALIDATE` | Validation check | DETERMINISTIC |
| `ERROR` | Error occurrence | N/A |

### 1.3 Serialization

Crystals use **binary serialization**, not JSON prose:

```python
import msgpack

class CrystalSerializer:
    """
    Efficient binary serialization for crystals.
    """

    def serialize(self, trace: SemanticTrace) -> bytes:
        """
        Serialize to compact binary format.

        NOT JSON. NOT prose. Compact, fast, reproducible.
        """
        return msgpack.packb({
            "trace_id": trace.trace_id,
            "parent_id": trace.parent_id,
            "timestamp": trace.timestamp.isoformat(),
            "agent_id": trace.agent_id,
            "agent_genus": trace.agent_genus,
            "action": trace.action,
            "inputs": trace.inputs,
            "outputs": trace.outputs,
            "input_hash": trace.input_hash,
            "input_snapshot": trace.input_snapshot,
            "output_hash": trace.output_hash,
            "gas_consumed": trace.gas_consumed,
            "duration_ms": trace.duration_ms,
            "vector": trace.vector,
            "determinism": trace.determinism.value,
            "metadata": trace.metadata,
        }, use_bin_type=True)

    def deserialize(self, data: bytes) -> SemanticTrace:
        """Deserialize from binary format."""
        obj = msgpack.unpackb(data, raw=False)
        return SemanticTrace(
            trace_id=obj["trace_id"],
            parent_id=obj["parent_id"],
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            # ... rest of fields
            determinism=Determinism(obj["determinism"]),
            metadata=obj["metadata"],
        )
```

---

## Part II: The Historian

### 2.1 Core Interface

```python
from contextvars import ContextVar
from uuid import uuid4


@dataclass
class TraceContext:
    """Context for an in-progress trace."""
    trace_id: str
    parent_id: str | None
    agent_id: str
    agent_genus: str
    input_snapshot: bytes
    input_hash: str
    start_time: datetime


class Historian:
    """
    The invisible recorder.

    Key property: Agents are UNAWARE of the Historian.
    """

    _current_trace: ContextVar[str | None] = ContextVar(
        "current_trace", default=None
    )

    def __init__(self, store: CrystalStore):
        self.store = store

    def begin_trace(self, agent: Agent, input: Any) -> TraceContext:
        """
        Begin recording a trace.

        Called by the RUNTIME, not the agent.
        """
        trace_id = str(uuid4())
        parent_id = self._current_trace.get()

        # Set current trace for nested calls
        self._current_trace.set(trace_id)

        return TraceContext(
            trace_id=trace_id,
            parent_id=parent_id,
            agent_id=agent.name,
            agent_genus=getattr(agent, "genus", "unknown"),
            input_snapshot=self._serialize(input),
            input_hash=self._hash(input),
            start_time=datetime.now(),
        )

    def end_trace(
        self,
        ctx: TraceContext,
        action: str,
        outputs: dict,
        determinism: Determinism,
    ) -> SemanticTrace:
        """
        Complete and store a trace.
        """
        # Restore parent trace
        self._current_trace.set(ctx.parent_id)

        crystal = SemanticTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            agent_id=ctx.agent_id,
            agent_genus=ctx.agent_genus,
            action=action,
            inputs=self._extract_inputs(ctx.input_snapshot),
            outputs=outputs,
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=self._hash(outputs) if outputs else None,
            gas_consumed=self._estimate_gas(ctx, outputs),
            duration_ms=self._duration(ctx),
            vector=None,  # Computed later by L-gent
            determinism=determinism,
            metadata={},
        )

        self.store.store(crystal)
        return crystal

    def abort_trace(self, ctx: TraceContext, error: Exception) -> SemanticTrace:
        """
        Record a failed trace.
        """
        self._current_trace.set(ctx.parent_id)

        crystal = SemanticTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            agent_id=ctx.agent_id,
            agent_genus=ctx.agent_genus,
            action="ERROR",
            inputs=self._extract_inputs(ctx.input_snapshot),
            outputs={"error": str(error), "type": type(error).__name__},
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=None,
            gas_consumed=0,
            duration_ms=self._duration(ctx),
            vector=None,
            determinism=Determinism.CHAOTIC,
            metadata={"exception": repr(error)},
        )

        self.store.store(crystal)
        return crystal

    def _serialize(self, obj: Any) -> bytes:
        return msgpack.packb(obj, use_bin_type=True)

    def _hash(self, obj: Any) -> str:
        import hashlib
        return hashlib.sha256(self._serialize(obj)).hexdigest()[:16]

    def _duration(self, ctx: TraceContext) -> int:
        return int((datetime.now() - ctx.start_time).total_seconds() * 1000)

    def _estimate_gas(self, ctx: TraceContext, outputs: dict) -> int:
        # Estimate based on input/output size
        input_tokens = len(ctx.input_snapshot) // 4
        output_tokens = len(str(outputs)) // 4 if outputs else 0
        return input_tokens + output_tokens
```

### 2.2 Wire Tap Integration

```python
class HistorianTap(WireTap):
    """
    A wire tap that feeds the Historian.

    Observes W-gent wire protocol frames without mutation.
    """

    def __init__(self, historian: Historian):
        self.historian = historian
        self._active: dict[str, TraceContext] = {}

    async def on_frame(self, frame: WireFrame) -> WireFrame:
        """
        Observe and pass through.

        The frame is UNCHANGED—this is pure observation.
        """
        match frame.frame_type:
            case FrameType.INVOKE_START:
                ctx = self.historian.begin_trace(
                    agent=frame.agent,
                    input=frame.payload,
                )
                self._active[frame.correlation_id] = ctx

            case FrameType.INVOKE_END:
                if frame.correlation_id in self._active:
                    ctx = self._active.pop(frame.correlation_id)
                    self.historian.end_trace(
                        ctx=ctx,
                        action=frame.metadata.get("action", "INVOKE"),
                        outputs=frame.payload,
                        determinism=self._classify_determinism(frame),
                    )

            case FrameType.ERROR:
                if frame.correlation_id in self._active:
                    ctx = self._active.pop(frame.correlation_id)
                    self.historian.abort_trace(ctx, frame.payload)

        return frame  # Pass through unchanged

    def _classify_determinism(self, frame: WireFrame) -> Determinism:
        """
        Classify the determinism of an operation.
        """
        if frame.metadata.get("llm_call"):
            return Determinism.PROBABILISTIC
        if frame.metadata.get("external_api"):
            return Determinism.CHAOTIC
        return Determinism.DETERMINISTIC
```

### 2.3 Crystal Store

```python
from abc import ABC, abstractmethod


class CrystalStore(ABC):
    """
    Abstract storage for crystals.

    Implementations: D-gent backed, file-based, memory.
    """

    @abstractmethod
    def store(self, crystal: SemanticTrace) -> None:
        """Store a crystal."""
        ...

    @abstractmethod
    def get(self, trace_id: str) -> SemanticTrace | None:
        """Retrieve a crystal by ID."""
        ...

    @abstractmethod
    def query(
        self,
        agent_id: str | None = None,
        action: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[SemanticTrace]:
        """Query crystals by criteria."""
        ...

    @abstractmethod
    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """Get child traces (nested calls)."""
        ...


class MemoryCrystalStore(CrystalStore):
    """In-memory crystal store for testing."""

    def __init__(self):
        self._crystals: dict[str, SemanticTrace] = {}

    def store(self, crystal: SemanticTrace) -> None:
        self._crystals[crystal.trace_id] = crystal

    def get(self, trace_id: str) -> SemanticTrace | None:
        return self._crystals.get(trace_id)

    def query(self, **kwargs) -> list[SemanticTrace]:
        results = list(self._crystals.values())
        if kwargs.get("agent_id"):
            results = [c for c in results if c.agent_id == kwargs["agent_id"]]
        if kwargs.get("action"):
            results = [c for c in results if c.action == kwargs["action"]]
        return results[: kwargs.get("limit", 100)]

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        return [c for c in self._crystals.values() if c.parent_id == trace_id]
```

---

## Part III: The Bard

### 3.1 Narrative Types

```python
class NarrativeGenre(Enum):
    """The genre determines voice and style."""
    TECHNICAL = "technical"
    LITERARY = "literary"
    NOIR = "noir"
    SYSADMIN = "sysadmin"
    MINIMAL = "minimal"
    DETECTIVE = "detective"


class Verbosity(Enum):
    """How much detail to include."""
    TERSE = "terse"
    NORMAL = "normal"
    VERBOSE = "verbose"


@dataclass
class NarrativeRequest:
    """A request to the Bard."""
    traces: list[SemanticTrace]
    genre: NarrativeGenre = NarrativeGenre.TECHNICAL
    perspective: str = "third_person"
    verbosity: Verbosity = Verbosity.NORMAL
    focus: list[str] | None = None
    filter_actions: list[str] | None = None


@dataclass
class Chapter:
    """A coherent unit of the narrative."""
    name: str
    start_trace_id: str
    end_trace_id: str
    theme: str
    agents_involved: list[str]


@dataclass
class Narrative:
    """The output of the Bard."""
    text: str
    genre: NarrativeGenre
    traces_used: list[SemanticTrace]
    chapters: list[Chapter]
    metadata: dict

    def render(self, format: str = "text") -> str:
        if format == "markdown":
            return self._to_markdown()
        if format == "html":
            return self._to_html()
        return self.text

    def _to_markdown(self) -> str:
        lines = [f"# {self.metadata.get('title', 'Narrative')}\n"]
        for chapter in self.chapters:
            lines.append(f"## {chapter.name}\n")
        lines.append(self.text)
        return "\n".join(lines)

    def _to_html(self) -> str:
        # HTML rendering
        ...
```

### 3.2 The Bard Agent

```python
class Bard(Agent[NarrativeRequest, Narrative]):
    """
    The Storyteller. Runs POST-MORTEM.

    Takes cold crystals and projects them into story.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def invoke(self, request: NarrativeRequest) -> Narrative:
        """Cast the shadow."""
        prompt = self._build_prompt(request)
        story_text = await self.llm.generate(prompt)

        return Narrative(
            text=story_text,
            genre=request.genre,
            traces_used=request.traces,
            chapters=self._identify_chapters(request.traces, story_text),
            metadata={
                "perspective": request.perspective,
                "verbosity": request.verbosity.value,
            },
        )

    def _build_prompt(self, request: NarrativeRequest) -> str:
        crystals_formatted = self._format_crystals(request.traces)

        genre_instructions = {
            NarrativeGenre.TECHNICAL: (
                "Write a technical log with timestamps. "
                "Format: [HH:MM:SS] Agent: Action (inputs → outputs)"
            ),
            NarrativeGenre.LITERARY: (
                "Write an engaging narrative with character and drama. "
                "Personify the agents. Use vivid language."
            ),
            NarrativeGenre.NOIR: (
                "Write in the style of hardboiled detective fiction. "
                "The code came in like trouble on a rainy night..."
            ),
            NarrativeGenre.SYSADMIN: (
                "Write terse operational notes. "
                "Just the facts. No flourish."
            ),
            NarrativeGenre.MINIMAL: (
                "Write the most compact summary possible. "
                "One line per significant event."
            ),
            NarrativeGenre.DETECTIVE: (
                "Write as if investigating a mystery. "
                "Clues, deductions, timeline analysis."
            ),
        }

        verbosity_instructions = {
            Verbosity.TERSE: "Be extremely brief. One sentence per event.",
            Verbosity.NORMAL: "Balance brevity and detail.",
            Verbosity.VERBOSE: "Include all details. Explain reasoning.",
        }

        return f"""
You are the Bard, a storyteller who transforms execution traces into narratives.

GENRE: {request.genre.value}
STYLE: {genre_instructions[request.genre]}

VERBOSITY: {request.verbosity.value}
{verbosity_instructions[request.verbosity]}

PERSPECTIVE: {request.perspective}

Here are the execution crystals (semantic traces):

{crystals_formatted}

Now tell the story of what happened.
"""

    def _format_crystals(self, traces: list[SemanticTrace]) -> str:
        """Format crystals for the prompt."""
        lines = []
        for t in traces:
            lines.append(
                f"- [{t.timestamp.strftime('%H:%M:%S')}] "
                f"Agent={t.agent_id}, Action={t.action}, "
                f"Inputs={t.inputs}, Outputs={t.outputs}"
            )
        return "\n".join(lines)

    def _identify_chapters(
        self,
        traces: list[SemanticTrace],
        story: str,
    ) -> list[Chapter]:
        """
        Identify chapter boundaries.

        Heuristics:
        - Agent changes
        - Temporal gaps > 1 minute
        - Error/recovery cycles
        """
        chapters = []
        current_agents = set()
        chapter_start = traces[0].trace_id if traces else None
        chapter_traces = []

        for i, trace in enumerate(traces):
            chapter_traces.append(trace)

            # Detect chapter break
            is_break = (
                # Agent change
                (trace.agent_id not in current_agents and len(current_agents) > 0)
                # Error
                or trace.action == "ERROR"
                # Temporal gap
                or (
                    i > 0
                    and (trace.timestamp - traces[i - 1].timestamp).seconds > 60
                )
            )

            if is_break and chapter_traces:
                chapters.append(
                    Chapter(
                        name=f"Chapter {len(chapters) + 1}",
                        start_trace_id=chapter_start,
                        end_trace_id=traces[i - 1].trace_id,
                        theme=self._infer_theme(chapter_traces),
                        agents_involved=list(current_agents),
                    )
                )
                chapter_start = trace.trace_id
                chapter_traces = [trace]
                current_agents = set()

            current_agents.add(trace.agent_id)

        # Final chapter
        if chapter_traces:
            chapters.append(
                Chapter(
                    name=f"Chapter {len(chapters) + 1}",
                    start_trace_id=chapter_start,
                    end_trace_id=traces[-1].trace_id,
                    theme=self._infer_theme(chapter_traces),
                    agents_involved=list(current_agents),
                )
            )

        return chapters

    def _infer_theme(self, traces: list[SemanticTrace]) -> str:
        """Infer a theme from traces."""
        actions = [t.action for t in traces]
        if "ERROR" in actions:
            return "Error Handling"
        if "GENERATE" in actions:
            return "Generation"
        if "VALIDATE" in actions:
            return "Validation"
        return "Processing"
```

---

## Part IV: The Echo Chamber

### 3.1 Echo Types

```python
class EchoMode(Enum):
    """How to handle replay."""
    STRICT = "strict"   # Return stored output exactly
    LUCID = "lucid"     # Re-execute with stored input


@dataclass
class Echo:
    """An echo of a past execution."""
    original_trace: SemanticTrace
    echo_output: dict
    mode: EchoMode
    drift: float | None = None


@dataclass
class DriftReport:
    """Report of drift detected during lucid echo."""
    trace: SemanticTrace
    drift: float
    original_output: dict
    current_output: dict
```

### 3.2 The Echo Chamber

```python
class EchoChamber:
    """
    The replay engine.

    Creates echoes, not resurrections.
    """

    def __init__(self, traces: list[SemanticTrace]):
        self.traces = traces
        self.position = 0

    def step_forward(self) -> SemanticTrace:
        trace = self.traces[self.position]
        self.position = min(self.position + 1, len(self.traces) - 1)
        return trace

    def step_backward(self) -> SemanticTrace:
        self.position = max(0, self.position - 1)
        return self.traces[self.position]

    def jump_to(self, trace_id: str) -> SemanticTrace:
        for i, t in enumerate(self.traces):
            if t.trace_id == trace_id:
                self.position = i
                return t
        raise KeyError(f"Trace {trace_id} not found")

    async def echo_from(
        self,
        trace: SemanticTrace,
        mode: EchoMode = EchoMode.STRICT,
        agent_registry: dict[str, Agent] | None = None,
    ) -> Echo:
        """Create an echo of a trace."""
        if mode == EchoMode.STRICT:
            return Echo(
                original_trace=trace,
                echo_output=trace.outputs,
                mode=mode,
                drift=0.0,
            )

        # Lucid mode: Re-execute
        match trace.determinism:
            case Determinism.DETERMINISTIC:
                input_state = msgpack.unpackb(trace.input_snapshot)
                agent = self._get_agent(trace.agent_id, agent_registry)
                new_output = await agent.invoke(input_state)
                return Echo(
                    original_trace=trace,
                    echo_output=new_output,
                    mode=mode,
                    drift=0.0,
                )

            case Determinism.PROBABILISTIC:
                input_state = msgpack.unpackb(trace.input_snapshot)
                agent = self._get_agent(trace.agent_id, agent_registry)
                new_output = await agent.invoke(input_state)
                drift = self._measure_drift(trace.outputs, new_output)
                return Echo(
                    original_trace=trace,
                    echo_output=new_output,
                    mode=mode,
                    drift=drift,
                )

            case Determinism.CHAOTIC:
                # Cannot safely replay external calls
                return Echo(
                    original_trace=trace,
                    echo_output=trace.outputs,
                    mode=EchoMode.STRICT,
                    drift=None,
                )

    def _get_agent(
        self,
        agent_id: str,
        registry: dict[str, Agent] | None,
    ) -> Agent:
        if registry and agent_id in registry:
            return registry[agent_id]
        raise ValueError(f"Agent {agent_id} not found in registry")

    def _measure_drift(self, original: dict, echo: dict) -> float:
        """
        Measure semantic drift.

        0.0 = identical, 1.0 = completely different
        """
        # Simple structural comparison
        original_str = str(original)
        echo_str = str(echo)

        if original_str == echo_str:
            return 0.0

        # Character-level similarity
        common = sum(a == b for a, b in zip(original_str, echo_str))
        max_len = max(len(original_str), len(echo_str))

        return 1.0 - (common / max_len) if max_len > 0 else 0.0
```

### 3.3 Lucid Dreamer

```python
class LucidDreamer:
    """Explore counterfactuals through lucid echoes."""

    async def dream_variant(
        self,
        trace: SemanticTrace,
        modified_input: Any,
        agent_registry: dict[str, Agent],
    ) -> tuple[Echo, Echo]:
        """Compare original vs modified execution."""
        chamber = EchoChamber([trace])

        # Original
        original_echo = await chamber.echo_from(
            trace, EchoMode.LUCID, agent_registry
        )

        # Variant
        modified_trace = SemanticTrace(
            trace_id=f"{trace.trace_id}_variant",
            parent_id=trace.parent_id,
            timestamp=datetime.now(),
            agent_id=trace.agent_id,
            agent_genus=trace.agent_genus,
            action=trace.action,
            inputs=modified_input if isinstance(modified_input, dict) else {"input": modified_input},
            outputs=None,
            input_hash="modified",
            input_snapshot=msgpack.packb(modified_input),
            output_hash=None,
            gas_consumed=0,
            duration_ms=0,
            vector=None,
            determinism=trace.determinism,
            metadata={"variant_of": trace.trace_id},
        )

        variant_echo = await chamber.echo_from(
            modified_trace, EchoMode.LUCID, agent_registry
        )

        return original_echo, variant_echo

    async def detect_drift_over_time(
        self,
        traces: list[SemanticTrace],
        agent_registry: dict[str, Agent],
        interval: int = 10,
    ) -> list[DriftReport]:
        """Re-run old traces to detect model drift."""
        reports = []

        for trace in traces[::interval]:
            if trace.determinism == Determinism.PROBABILISTIC:
                chamber = EchoChamber([trace])
                echo = await chamber.echo_from(
                    trace, EchoMode.LUCID, agent_registry
                )

                if echo.drift and echo.drift > 0.1:
                    reports.append(
                        DriftReport(
                            trace=trace,
                            drift=echo.drift,
                            original_output=trace.outputs,
                            current_output=echo.echo_output,
                        )
                    )

        return reports
```

---

## Part V: The Chronicle

```python
@dataclass
class Interaction:
    """A point where agent timelines intersect."""
    timestamp: datetime
    from_agent: str
    to_agent: str
    correlation_id: str
    from_trace_id: str
    to_trace_id: str


class Chronicle:
    """A collection of crystals from multiple agents."""

    def __init__(self):
        self.crystals: dict[str, list[SemanticTrace]] = {}
        self.interactions: list[Interaction] = []

    def add_crystal(self, trace: SemanticTrace) -> None:
        if trace.agent_id not in self.crystals:
            self.crystals[trace.agent_id] = []
        self.crystals[trace.agent_id].append(trace)
        self._detect_interaction(trace)

    def weave(self) -> list[SemanticTrace]:
        """Interleave all crystals by timestamp."""
        all_traces = []
        for traces in self.crystals.values():
            all_traces.extend(traces)
        return sorted(all_traces, key=lambda t: t.timestamp)

    async def to_narrative(
        self,
        bard: Bard,
        genre: NarrativeGenre = NarrativeGenre.LITERARY,
    ) -> Narrative:
        """Ask the Bard to tell the chronicle."""
        woven = self.weave()
        return await bard.invoke(
            NarrativeRequest(
                traces=woven,
                genre=genre,
                verbosity=Verbosity.NORMAL,
            )
        )

    def _detect_interaction(self, trace: SemanticTrace) -> None:
        """Detect interactions via correlation IDs in metadata."""
        if "correlation_id" in trace.metadata:
            corr_id = trace.metadata["correlation_id"]
            # Find matching trace in other agent
            for agent_id, traces in self.crystals.items():
                if agent_id == trace.agent_id:
                    continue
                for other in traces:
                    if other.metadata.get("correlation_id") == corr_id:
                        self.interactions.append(
                            Interaction(
                                timestamp=trace.timestamp,
                                from_agent=other.agent_id,
                                to_agent=trace.agent_id,
                                correlation_id=corr_id,
                                from_trace_id=other.trace_id,
                                to_trace_id=trace.trace_id,
                            )
                        )
```

---

## Part VI: Forensic Bard

```python
@dataclass
class Diagnosis:
    """A crash diagnosis."""
    narrative: str
    failure_trace: SemanticTrace
    probable_cause: str
    echo_command: str
    similar_failures: list[SemanticTrace]


class ForensicBard(Bard):
    """The Detective. Specializes in crash narratives."""

    async def diagnose(
        self,
        failure_trace: SemanticTrace,
        context_traces: list[SemanticTrace],
        store: CrystalStore | None = None,
    ) -> Diagnosis:
        """Produce a crash diagnosis."""
        prompt = self._build_forensic_prompt(failure_trace, context_traces)
        analysis = await self.llm.generate(prompt)

        similar = []
        if store:
            similar = store.query(
                action="ERROR",
                limit=5,
            )

        return Diagnosis(
            narrative=analysis,
            failure_trace=failure_trace,
            probable_cause=self._extract_cause(analysis),
            echo_command=f"kgents echo {failure_trace.trace_id}",
            similar_failures=similar,
        )

    def _build_forensic_prompt(
        self,
        failure: SemanticTrace,
        context: list[SemanticTrace],
    ) -> str:
        context_formatted = self._format_crystals(context)

        return f"""
You are a forensic analyst investigating a system failure.

THE FAILURE:
- Timestamp: {failure.timestamp}
- Agent: {failure.agent_id} ({failure.agent_genus})
- Action: {failure.action}
- Inputs: {failure.inputs}
- Outputs: {failure.outputs}
- Duration: {failure.duration_ms}ms

CONTEXT (events leading up to failure):
{context_formatted}

ANALYZE:
1. What was the agent trying to do?
2. What went wrong?
3. What is the probable root cause?
4. How might this be prevented in the future?

Be specific. Reference trace IDs where relevant.
"""

    def _extract_cause(self, analysis: str) -> str:
        """Extract the probable cause from analysis."""
        # Simple heuristic: look for "root cause" or "because"
        lines = analysis.split("\n")
        for line in lines:
            if "root cause" in line.lower() or "because" in line.lower():
                return line.strip()
        return lines[0] if lines else "Unknown"
```

---

## Summary

The N-gent architecture separates concerns cleanly:

| Component | Phase | Responsibility |
|-----------|-------|----------------|
| **SemanticTrace** | Data | Pure crystal, no prose |
| **Historian** | Write | Invisible collection |
| **HistorianTap** | Write | Wire protocol integration |
| **CrystalStore** | Write | Persistence |
| **Bard** | Read | Story generation |
| **ForensicBard** | Read | Crash diagnosis |
| **EchoChamber** | Read | Replay simulation |
| **LucidDreamer** | Read | Counterfactuals |
| **Chronicle** | Both | Multi-agent weaving |

**The key insight**: By separating recording from telling, we:
1. Save tokens at write-time (no prose storage)
2. Enable multiple genres from the same data
3. Get Rashomon for free
4. Acknowledge the non-ergodic nature of LLMs (echoes, not resurrections)
