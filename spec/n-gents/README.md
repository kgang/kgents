# N-gents: The Narrative Substrate

> *"The event is the stone. The story is the shadow. Collect stones. Cast shadows only when the sun is out."*

---

## Philosophy

N-gents separate **recording** (The Historian) from **telling** (The Bard).

The original sin of observability is **diegetic execution**—narrating oneself in real-time. This is kitsch. It wastes tokens on prose that may never be read. It burdens the runtime with the weight of the historian.

**The Correction**: Story is a *Read-Time* projection, not a *Write-Time* artifact.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE N-GENT SEPARATION                     │
│                                                              │
│   WRITE-TIME                          READ-TIME              │
│   (Genesis)                           (Exegesis)             │
│                                                              │
│   ┌──────────┐                        ┌──────────┐           │
│   │ Historian│  ──── Crystal ────►    │   Bard   │           │
│   │ (Record) │      (SemanticTrace)   │  (Tell)  │           │
│   └──────────┘                        └──────────┘           │
│        │                                   │                 │
│        │ Invisible tap                     │ On-demand       │
│        │ No prose                          │ Any genre       │
│        ▼                                   ▼                 │
│   Pure data                           Human story            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## The Distinction from O-gents

| Aspect | O-gent | N-gent (Historian) | N-gent (Bard) |
|--------|--------|-------------------|---------------|
| When | Real-time | Write-time | Read-time |
| What | Metrics | Semantic crystals | Stories |
| For whom | Dashboards | Storage | Humans |
| Question | "Is it healthy?" | "What occurred?" | "What does it mean?" |

**O-gents** see and measure.
**N-gent Historian** collects and crystallizes.
**N-gent Bard** interprets and tells.

---

## Part I: The Historian (Write-Time)

### 1.1 The Semantic Trace (Crystal)

The fundamental unit is the **SemanticTrace**—pure data, no prose.

```python
@dataclass(frozen=True)
class SemanticTrace:
    """
    The Crystal. Pure, compressed reality.

    NO prose. NO "content" strings. NO "thought_type" narrative.
    Just semantic atoms that can be projected into any story.
    """
    # Identity
    trace_id: str
    parent_id: str | None       # For nested calls
    timestamp: datetime

    # The Agent
    agent_id: str
    agent_genus: str            # "B", "G", "J", etc.

    # The Action (semantic, not narrative)
    action: str                 # "REVIEW_CODE", "GENERATE", "DECIDE"

    # The Data (structured, not prose)
    inputs: dict                # { "file": "module.py", "lines": 127 }
    outputs: dict | None        # { "score": 8, "issues": [...] }

    # Reproducibility
    input_hash: str             # For deduplication
    input_snapshot: bytes       # Serialized for echo
    output_hash: str | None

    # Economics (B-gent integration)
    gas_consumed: int           # Tokens used
    duration_ms: int

    # Embedding (M-gent integration)
    vector: list[float] | None  # For semantic retrieval

    # Metadata
    determinism: Determinism    # DETERMINISTIC | PROBABILISTIC | CHAOTIC
    metadata: dict


class Determinism(Enum):
    """
    Classification of trace reproducibility.

    Critical for the Echo Chamber to know what can be replayed exactly.
    """
    DETERMINISTIC = "deterministic"   # Math, lookups: exact replay possible
    PROBABILISTIC = "probabilistic"   # LLM calls: similar but not identical
    CHAOTIC = "chaotic"               # External APIs: no replay guarantee
```

### 1.2 The Historian Agent

The Historian is **invisible**. Agents don't know they're being recorded.

```python
class Historian:
    """
    The invisible recorder. Creates crystals, not stories.

    Implementation via ContextVar or WireTap—the agent
    is unaware of observation.
    """

    # Storage for the crystals
    crystal_store: CrystalStore

    # The tap (invisible to agents)
    _context: ContextVar[list[SemanticTrace]]

    def begin_trace(self, agent: Agent, input: Any) -> TraceContext:
        """
        Start recording. Returns context for nested traces.

        The agent doesn't call this—the runtime does.
        """
        trace_id = str(uuid4())
        parent_id = self._get_current_trace_id()

        return TraceContext(
            trace_id=trace_id,
            parent_id=parent_id,
            agent_id=agent.name,
            agent_genus=agent.genus,
            input_snapshot=self._serialize(input),
            input_hash=self._hash(input),
            start_time=datetime.now()
        )

    def end_trace(
        self,
        ctx: TraceContext,
        action: str,
        outputs: dict,
        determinism: Determinism
    ) -> SemanticTrace:
        """
        Complete the crystal. Store it.
        """
        crystal = SemanticTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            agent_id=ctx.agent_id,
            agent_genus=ctx.agent_genus,
            action=action,
            inputs=self._extract_semantic_inputs(ctx.input_snapshot),
            outputs=outputs,
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=self._hash(outputs),
            gas_consumed=self._measure_gas(ctx),
            duration_ms=self._measure_duration(ctx),
            vector=None,  # Computed lazily by L-gent
            determinism=determinism,
            metadata={}
        )

        self.crystal_store.store(crystal)
        return crystal

    def _serialize(self, obj: Any) -> bytes:
        """
        Efficient binary serialization.

        NOT JSON prose. Compact, fast, reproducible.
        """
        return msgpack.packb(obj, use_bin_type=True)
```

### 1.3 The Wire Tap (Integration)

The Historian integrates via W-gent wire protocol:

```python
class HistorianTap(WireTap):
    """
    A wire tap that feeds the Historian.

    Sits on the wire, observes frames, creates crystals.
    Non-blocking, non-invasive.
    """

    def __init__(self, historian: Historian):
        self.historian = historian
        self._active_contexts: dict[str, TraceContext] = {}

    async def on_frame(self, frame: WireFrame) -> WireFrame:
        """
        Observe without mutating.

        Returns the frame unchanged—this is a tap, not a transform.
        """
        match frame.frame_type:
            case FrameType.INVOKE_START:
                ctx = self.historian.begin_trace(
                    agent=frame.agent,
                    input=frame.payload
                )
                self._active_contexts[frame.correlation_id] = ctx

            case FrameType.INVOKE_END:
                ctx = self._active_contexts.pop(frame.correlation_id)
                self.historian.end_trace(
                    ctx=ctx,
                    action=frame.action,
                    outputs=frame.payload,
                    determinism=frame.determinism
                )

        return frame  # Pass through unchanged
```

---

## Part II: The Bard (Read-Time)

### 2.1 The Narrative Request

The Bard is invoked **post-mortem**, when a human wants a story.

```python
@dataclass
class NarrativeRequest:
    """
    A request to the Bard.

    The Bard takes crystals and casts them into shadow.
    """
    # Which crystals to narrate
    traces: list[SemanticTrace]

    # How to tell the story
    genre: NarrativeGenre = NarrativeGenre.TECHNICAL
    perspective: str = "third_person"    # "first_person", "omniscient"
    verbosity: Verbosity = Verbosity.NORMAL

    # What to focus on
    focus: list[str] | None = None       # Agent IDs to highlight
    filter_actions: list[str] | None = None  # Actions to include


class NarrativeGenre(Enum):
    """
    The genre determines voice and style.

    The SAME crystals can become different stories.
    """
    TECHNICAL = "technical"     # "[10:42:15] CodeReviewer received..."
    LITERARY = "literary"       # "At 10:42, the agent stirred..."
    NOIR = "noir"               # "The code came in like trouble..."
    SYSADMIN = "sysadmin"       # "10:42 - module.py reviewed, 2 issues"
    MINIMAL = "minimal"         # "10:42:15 ← file.py → 2 issues"
    DETECTIVE = "detective"     # "The first clue appeared at 10:42..."


class Verbosity(Enum):
    TERSE = "terse"       # One line per major event
    NORMAL = "normal"     # Balanced detail
    VERBOSE = "verbose"   # Full detail, reasoning included
```

### 2.2 The Bard Agent

The Bard is an **LLM Agent** that reads crystals and writes stories.

```python
class Bard(Agent[NarrativeRequest, Narrative]):
    """
    The Storyteller. Runs POST-MORTEM.

    Takes cold crystals and shines light through them
    to project a story.

    This is the N-gent proper.
    """

    async def invoke(self, request: NarrativeRequest) -> Narrative:
        """
        Cast the shadow.

        The Bard interprets the crystals according to
        the requested genre and perspective.
        """
        # Build the prompt based on genre
        prompt = self._build_prompt(request)

        # Let the LLM weave the story
        story_text = await self.llm.generate(prompt)

        # Structure the output
        return Narrative(
            text=story_text,
            genre=request.genre,
            traces_used=request.traces,
            chapters=self._identify_chapters(request.traces, story_text),
            metadata={
                "perspective": request.perspective,
                "verbosity": request.verbosity
            }
        )

    def _build_prompt(self, request: NarrativeRequest) -> str:
        """
        Build the narration prompt.

        The crystals are presented as structured data.
        The Bard interprets them into prose.
        """
        crystals_json = self._format_crystals(request.traces)

        genre_instructions = {
            NarrativeGenre.TECHNICAL: "Write a technical log with timestamps.",
            NarrativeGenre.LITERARY: "Write an engaging narrative with character.",
            NarrativeGenre.NOIR: "Write in the style of hardboiled detective fiction.",
            NarrativeGenre.SYSADMIN: "Write terse operational notes.",
            NarrativeGenre.MINIMAL: "Write the most compact summary possible.",
            NarrativeGenre.DETECTIVE: "Write as if investigating a mystery.",
        }

        return f"""
        You are the Bard. You transform execution traces into stories.

        Genre: {request.genre.value}
        Style: {genre_instructions[request.genre]}
        Perspective: {request.perspective}
        Verbosity: {request.verbosity.value}

        Here are the execution crystals (semantic traces):

        {crystals_json}

        Now tell the story of what happened.
        """


@dataclass
class Narrative:
    """
    The output of the Bard.

    A story that can be rendered, searched, or analyzed.
    """
    text: str
    genre: NarrativeGenre
    traces_used: list[SemanticTrace]
    chapters: list[Chapter]
    metadata: dict

    def render(self, format: str = "text") -> str:
        """Render to text, markdown, or HTML."""
        ...
```

### 2.3 The Rashomon Pattern (Free)

Because the Bard interprets crystals at read-time, **Rashomon comes free**:

```python
async def rashomon(
    traces: list[SemanticTrace],
    genres: list[NarrativeGenre]
) -> dict[NarrativeGenre, Narrative]:
    """
    Tell the same story from multiple perspectives.

    This is FREE—we just call the Bard multiple times
    with the same crystals but different genres.
    """
    bard = Bard()
    narratives = {}

    for genre in genres:
        request = NarrativeRequest(traces=traces, genre=genre)
        narratives[genre] = await bard.invoke(request)

    return narratives


# Usage: What happened, told three ways
stories = await rashomon(
    traces=historian.get_traces(session_id),
    genres=[
        NarrativeGenre.TECHNICAL,   # For the log
        NarrativeGenre.DETECTIVE,   # For debugging
        NarrativeGenre.LITERARY     # For the retrospective
    ]
)
```

---

## Part III: The Echo Chamber (Replay)

### 3.1 The Echo Principle

**LLMs are Non-Ergodic**. Even with `temperature=0`, floating-point non-determinism makes "exact" replay a myth.

We don't "resurrect" the dead. We create **Echoes**.

```python
class EchoMode(Enum):
    """
    How to handle non-deterministic traces during replay.
    """
    STRICT = "strict"
        # Return stored output exactly.
        # Perfect reproduction, but brittle.
        # If the stored output is wrong, you replay the wrong thing.

    LUCID = "lucid"
        # Re-execute with stored input.
        # Allows drift detection and counterfactuals.
        # The "dream" may differ from the "memory."


@dataclass
class Echo:
    """
    An echo of a past execution.

    NOT the original. A simulation. A shadow of a shadow.
    """
    original_trace: SemanticTrace
    echo_output: dict
    mode: EchoMode
    drift: float | None = None  # How different was the echo?
```

### 3.2 The Echo Chamber

```python
class EchoChamber:
    """
    The replay engine.

    Explicitly NOT called "ReplayAgent" because replay implies
    exact reproduction. This is an Echo—similar, but not identical.
    """

    def __init__(self, traces: list[SemanticTrace]):
        self.traces = traces
        self.position = 0
        self.echoes: list[Echo] = []

    def step_forward(self) -> SemanticTrace:
        """Advance one step through the crystals."""
        trace = self.traces[self.position]
        self.position += 1
        return trace

    def step_backward(self) -> SemanticTrace:
        """Rewind one step."""
        self.position = max(0, self.position - 1)
        return self.traces[self.position]

    async def echo_from(
        self,
        trace: SemanticTrace,
        mode: EchoMode = EchoMode.STRICT
    ) -> Echo:
        """
        Create an echo of a trace.

        Strict: Return the stored output.
        Lucid: Re-execute and compare.
        """
        if mode == EchoMode.STRICT:
            return Echo(
                original_trace=trace,
                echo_output=trace.outputs,
                mode=mode,
                drift=0.0
            )

        # Lucid mode: Re-execute
        match trace.determinism:
            case Determinism.DETERMINISTIC:
                # Safe to re-run: Math, lookups
                input_state = self._deserialize(trace.input_snapshot)
                agent = self._reconstruct_agent(trace.agent_id)
                new_output = await agent.invoke(input_state)

                return Echo(
                    original_trace=trace,
                    echo_output=new_output,
                    mode=mode,
                    drift=0.0  # Deterministic = no drift
                )

            case Determinism.PROBABILISTIC:
                # LLM call: Will drift
                input_state = self._deserialize(trace.input_snapshot)
                agent = self._reconstruct_agent(trace.agent_id)
                new_output = await agent.invoke(input_state)

                drift = self._measure_drift(trace.outputs, new_output)

                return Echo(
                    original_trace=trace,
                    echo_output=new_output,
                    mode=mode,
                    drift=drift
                )

            case Determinism.CHAOTIC:
                # External API: Can't replay safely
                return Echo(
                    original_trace=trace,
                    echo_output=trace.outputs,  # Use stored
                    mode=EchoMode.STRICT,       # Forced to strict
                    drift=None  # Unknown
                )

    def _measure_drift(self, original: dict, echo: dict) -> float:
        """
        Measure semantic drift between original and echo.

        0.0 = identical
        1.0 = completely different
        """
        # Use embeddings or structural comparison
        ...
```

### 3.3 Counterfactuals via Lucid Dreaming

```python
class LucidDreamer:
    """
    Explore counterfactuals through lucid echoes.

    "What if the input had been different?"
    "What if we used a different model?"
    """

    async def dream_variant(
        self,
        trace: SemanticTrace,
        modified_input: Any
    ) -> tuple[Echo, Echo]:
        """
        Compare: What happened vs What might have happened.

        Returns both the original echo and the variant.
        """
        chamber = EchoChamber([trace])

        # Original echo (lucid mode)
        original_echo = await chamber.echo_from(trace, EchoMode.LUCID)

        # Modified trace
        modified_trace = self._modify_trace(trace, modified_input)
        variant_echo = await chamber.echo_from(modified_trace, EchoMode.LUCID)

        return original_echo, variant_echo

    async def detect_drift_over_time(
        self,
        traces: list[SemanticTrace],
        interval: int = 10
    ) -> list[DriftReport]:
        """
        Re-run old traces to detect model drift.

        Useful for: "Is our agent behaving differently now
        than it did last month?"
        """
        reports = []
        for trace in traces[::interval]:
            echo = await EchoChamber([trace]).echo_from(trace, EchoMode.LUCID)
            if echo.drift and echo.drift > 0.1:
                reports.append(DriftReport(
                    trace=trace,
                    drift=echo.drift,
                    original_output=trace.outputs,
                    current_output=echo.echo_output
                ))
        return reports
```

---

## Part IV: The Chronicle (Multi-Agent Sagas)

### 4.1 Weaving Crystals

When multiple agents collaborate, their crystals weave into a **Chronicle**.

```python
class Chronicle:
    """
    A collection of crystals from multiple agents.

    NOT a story yet—that's the Bard's job.
    This is the structured substrate for multi-agent narratives.
    """

    def __init__(self):
        self.crystals: dict[str, list[SemanticTrace]] = {}  # agent_id → traces
        self.interactions: list[Interaction] = []

    @dataclass
    class Interaction:
        """A point where agent timelines intersect."""
        timestamp: datetime
        from_agent: str
        to_agent: str
        correlation_id: str
        from_trace_id: str
        to_trace_id: str

    def add_crystal(self, trace: SemanticTrace):
        """Add a crystal to the chronicle."""
        if trace.agent_id not in self.crystals:
            self.crystals[trace.agent_id] = []
        self.crystals[trace.agent_id].append(trace)

        # Detect interactions via correlation
        self._detect_interaction(trace)

    def weave(self) -> list[SemanticTrace]:
        """
        Interleave all crystals by timestamp.

        Returns a unified timeline, ready for the Bard.
        """
        all_traces = []
        for traces in self.crystals.values():
            all_traces.extend(traces)

        return sorted(all_traces, key=lambda t: t.timestamp)

    def to_narrative(
        self,
        bard: Bard,
        genre: NarrativeGenre = NarrativeGenre.LITERARY
    ) -> Narrative:
        """
        Ask the Bard to tell the chronicle as a saga.
        """
        woven = self.weave()
        return bard.invoke(NarrativeRequest(
            traces=woven,
            genre=genre,
            verbosity=Verbosity.NORMAL
        ))
```

### 4.2 Chapter Detection

Chapters are **Read-Time** constructs. The Bard identifies them.

```python
@dataclass
class Chapter:
    """
    A coherent unit of the narrative.

    Identified by the Bard based on:
    - Agent transitions
    - Temporal gaps
    - Goal boundaries
    - Error/recovery cycles
    """
    name: str
    start_trace_id: str
    end_trace_id: str
    theme: str
    agents_involved: list[str]
```

---

## Part V: Forensics

### 5.1 Crash Diagnosis

When things go wrong, the Bard becomes a **Detective**.

```python
class ForensicBard(Bard):
    """
    The Detective. Specializes in crash narratives.

    Takes a crystal trail leading to failure and
    tells the story of what went wrong.
    """

    async def diagnose(
        self,
        failure_trace: SemanticTrace,
        context_traces: list[SemanticTrace]
    ) -> Diagnosis:
        """
        Produce a crash diagnosis.
        """
        # Build detective prompt
        prompt = self._build_forensic_prompt(failure_trace, context_traces)

        # Let the LLM investigate
        analysis = await self.llm.generate(prompt)

        return Diagnosis(
            narrative=analysis,
            failure_trace=failure_trace,
            probable_cause=self._extract_cause(analysis),
            echo_command=f"kgents echo {failure_trace.trace_id}",
            similar_failures=await self._find_similar(failure_trace)
        )

    def _build_forensic_prompt(
        self,
        failure: SemanticTrace,
        context: list[SemanticTrace]
    ) -> str:
        return f"""
        You are a forensic analyst investigating a system failure.

        The failure occurred at {failure.timestamp}:
        - Agent: {failure.agent_id}
        - Action: {failure.action}
        - Input: {failure.inputs}
        - Output: {failure.outputs}

        Here is the context leading up to the failure:
        {self._format_crystals(context)}

        Analyze:
        1. What was the agent trying to do?
        2. What went wrong?
        3. What is the probable root cause?
        4. How might this be prevented?
        """
```

---

## Part VI: Integration Map

| Integration | Direction | Purpose |
|-------------|-----------|---------|
| Historian ← W-gent | W → N | Wire tap feeds Historian |
| Historian → D-gent | N → D | Crystals persist via D-gent |
| Historian → L-gent | N → L | Crystals indexed for search |
| Historian → M-gent | N → M | Crystals resonate in memory |
| Bard → I-gent | N → I | Stories visualized |
| Bard → B-gent | N ↔ B | Narration budgeted |
| Echo ← Historian | H → E | Crystals enable echoes |

---

## Part VII: The N-gent Taxonomy

| Agent | Phase | Purpose |
|-------|-------|---------|
| **Historian** | Write | Invisible crystal collection |
| **HistorianTap** | Write | Wire protocol integration |
| **CrystalStore** | Write | Crystal persistence |
| **Bard** | Read | Story generation from crystals |
| **ForensicBard** | Read | Crash diagnosis |
| **EchoChamber** | Read | Replay via echoes |
| **LucidDreamer** | Read | Counterfactual exploration |
| **Chronicle** | Both | Multi-agent crystal weaving |

---

## Part VIII: Anti-Patterns

### Original Anti-Patterns (Retained)

1. **Logs without stories**: Raw data without Bard interpretation
2. **Stories without echo**: Can't reproduce from the narrative
3. **Ignoring the reader**: Stories are for humans
4. **Overwriting history**: Crystals are sacred
5. **Single timeline thinking**: Echoes enable exploration
6. **Omniscient narrator fallacy**: The Bard interprets, not dictates

### New Anti-Patterns (From Critique)

7. **Diegetic execution**: Narrating at runtime. The Historian must be silent.
8. **Resurrection claims**: Echoes are simulations, not exact replays. Be honest.
9. **Wrapper infection**: Story collection must be orthogonal (tap, not wrap).
10. **Prose at write-time**: Storing "CodeReviewer stirred..." wastes tokens.
11. **Genre lock-in**: Crystals must support multiple narrative projections.

---

## The Corrected Zen

~~*"The story of the thought is the thought made eternal; replay is resurrection."*~~

> *"The event is the stone. The story is the shadow.*
> *Do not mistake the shadow for the stone.*
> *Collect stones. Cast shadows only when the sun is out."*

---

## Implementation Roadmap

### Phase 1: The Historian (Core)

- [ ] `SemanticTrace` data structure (no prose)
- [ ] `Historian` with `begin_trace`/`end_trace`
- [ ] `HistorianTap` wire protocol integration
- [ ] `CrystalStore` with D-gent backend
- [ ] Tests: 40+

### Phase 2: The Bard (Narration)

- [ ] `Bard` agent with genre support
- [ ] `NarrativeRequest` and `Narrative` types
- [ ] Multiple genre renderers
- [ ] Rashomon pattern (free with architecture)
- [ ] Tests: 35+

### Phase 3: The Echo Chamber (Replay)

- [ ] `EchoChamber` with STRICT/LUCID modes
- [ ] `Echo` type with drift measurement
- [ ] `LucidDreamer` for counterfactuals
- [ ] Determinism classification
- [ ] Tests: 40+

### Phase 4: Chronicles & Forensics

- [ ] `Chronicle` for multi-agent weaving
- [ ] `ForensicBard` for crash diagnosis
- [ ] Chapter detection (read-time)
- [ ] Tests: 30+

### Phase 5: Integrations

- [ ] D-gent persistence
- [ ] L-gent indexing
- [ ] M-gent resonance
- [ ] I-gent visualization
- [ ] B-gent budgeting
- [ ] Tests: 25+

---

## See Also

- [narrator.md](narrator.md) - Detailed narrator specification
- [o-gents/](../o-gents/) - Observability (the seeing)
- [w-gents/](../w-gents/) - Wire protocol (the tap)
- [m-gents/](../m-gents/) - Memory (resonance with crystals)
- [archetypes.md](../archetypes.md) - The Witness archetype
