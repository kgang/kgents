# N-gent: The Narrator

**Status:** Standard
**Implementation:** `impl/claude/agents/n/` (full implementation)

> *"Collect stones. Cast shadows only when the sun is out."*

## Purpose

N-gent separates **recording** from **telling**. The Historian collects semantic traces (crystals) at write-time with zero prose overhead. The Bard generates narrative at read-time, enabling multiple genres from the same data. The Echo Chamber replays traces for debugging and counterfactual exploration. This separation acknowledges that story is a projection, not ground truth, and that LLMs are non-ergodic (echoes ≠ resurrections).

## Core Insight

**The event is the stone. The story is the shadow.** By storing pure semantic atoms instead of narrative, we save tokens at write-time, enable Rashomon (multiple valid tellings), and separate recording from interpretation.

## Type Signatures

### The Crystal (Core Data)

```python
class Determinism(Enum):
    """Classification of trace reproducibility."""
    DETERMINISTIC = "deterministic"   # Math, lookups: exact replay
    PROBABILISTIC = "probabilistic"   # LLM calls: similar not identical
    CHAOTIC = "chaotic"               # External APIs: no guarantees

@dataclass(frozen=True)
class SemanticTrace:
    """
    The Crystal. Pure, compressed reality. No prose.
    Fundamental unit of N-gent recording.
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

    # Embedding (for L-gent)
    vector: list[float] | None

    # Classification
    determinism: Determinism
    metadata: dict
```

### Action Vocabulary

Semantic atoms (not prose):

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

### The Historian (Write-Time)

```python
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
    _current_trace: ContextVar[str | None]

    def begin_trace(self, agent: Agent, input: Any) -> TraceContext: ...
    def end_trace(self, ctx: TraceContext, action: str, outputs: dict,
                  determinism: Determinism) -> SemanticTrace: ...
    def abort_trace(self, ctx: TraceContext, error: Exception) -> SemanticTrace: ...

class HistorianTap(WireTap):
    """Wire tap that feeds the Historian (W-gent integration)."""
    async def on_frame(self, frame: WireFrame) -> WireFrame: ...
```

### Crystal Store (Persistence)

```python
class CrystalStore(ABC):
    """Abstract storage for crystals."""
    def store(self, crystal: SemanticTrace) -> None: ...
    def get(self, trace_id: str) -> SemanticTrace | None: ...
    def query(self, agent_id: str | None = None, action: str | None = None,
              start_time: datetime | None = None, end_time: datetime | None = None,
              limit: int = 100) -> list[SemanticTrace]: ...
    def get_children(self, trace_id: str) -> list[SemanticTrace]: ...

class MemoryCrystalStore(CrystalStore): ...  # In-memory for testing
class DgentCrystalStore(CrystalStore): ...   # D-gent backed persistence
```

### The Bard (Read-Time)

```python
class NarrativeGenre(Enum):
    """The genre determines voice and style."""
    TECHNICAL = "technical"    # Timestamps, structured logs
    LITERARY = "literary"      # Engaging narrative with character
    NOIR = "noir"              # Hardboiled detective fiction
    SYSADMIN = "sysadmin"      # Terse operational notes
    MINIMAL = "minimal"        # Compact summary
    DETECTIVE = "detective"    # Mystery investigation

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

    def render(self, format: str = "text") -> str: ...

class Bard(Agent[NarrativeRequest, Narrative]):
    """The Storyteller. Runs POST-MORTEM."""
    async def invoke(self, request: NarrativeRequest) -> Narrative: ...

class ForensicBard(Bard):
    """The Detective. Specializes in crash narratives."""
    async def diagnose(self, failure_trace: SemanticTrace,
                      context_traces: list[SemanticTrace],
                      store: CrystalStore | None = None) -> Diagnosis: ...
```

### The Echo Chamber (Replay)

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
    drift: float | None = None  # 0.0 = identical, 1.0 = completely different

@dataclass
class DriftReport:
    """Report of drift detected during lucid echo."""
    trace: SemanticTrace
    drift: float
    original_output: dict
    current_output: dict

class EchoChamber:
    """
    The replay engine. Creates echoes, not resurrections.
    Respects Determinism classification:
    - DETERMINISTIC: Exact replay possible
    - PROBABILISTIC: Similar but not identical
    - CHAOTIC: Cannot replay safely
    """
    def step_forward(self) -> SemanticTrace: ...
    def step_backward(self) -> SemanticTrace: ...
    def jump_to(self, trace_id: str) -> SemanticTrace: ...
    async def echo_from(self, trace: SemanticTrace, mode: EchoMode = EchoMode.STRICT,
                        agent_registry: dict[str, Agent] | None = None) -> Echo: ...

class LucidDreamer:
    """Explore counterfactuals through lucid echoes."""
    async def dream_variant(self, trace: SemanticTrace, modified_input: Any,
                           agent_registry: dict[str, Agent]) -> tuple[Echo, Echo]: ...
    async def detect_drift_over_time(self, traces: list[SemanticTrace],
                                     agent_registry: dict[str, Agent],
                                     interval: int = 10) -> list[DriftReport]: ...
```

### The Chronicle (Multi-Agent)

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
    def add_crystal(self, trace: SemanticTrace) -> None: ...
    def weave(self) -> list[SemanticTrace]: ...  # Interleave by timestamp
    async def to_narrative(self, bard: Bard,
                          genre: NarrativeGenre = NarrativeGenre.LITERARY) -> Narrative: ...
```

## Laws/Invariants

### Write-Time Laws

1. **Invisibility**: `∀agent. agent.knows(historian) = False`
   - Agents never know they're being traced
   - Recording happens at runtime level, not agent level

2. **Immutability**: `∀crystal. after(store(crystal)) ⟹ frozen(crystal)`
   - Crystals cannot be modified after creation
   - History is append-only

3. **Causality**: `∀t₁,t₂. t₁.parent_id = t₂.trace_id ⟹ t₁.timestamp ≥ t₂.timestamp`
   - Child traces occur after parent traces
   - Causality is preserved in the trace tree

4. **Determinism Classification**:
   - `DETERMINISTIC ⟹ hash(input) = hash(input') ⟹ output = output'`
   - `PROBABILISTIC ⟹ hash(input) = hash(input') ⟹ similar(output, output')`
   - `CHAOTIC ⟹ no guarantees`

### Read-Time Laws

5. **Rashomon**: `∀crystals,g₁,g₂. bard(crystals,g₁) ≠ bard(crystals,g₂) ∧ valid(both)`
   - Multiple valid tellings from the same crystals
   - Genre changes interpretation, not facts

6. **Projection**: `narrative ∈ project(crystals, genre, perspective, verbosity)`
   - Narrative is a projection, not ground truth
   - Original crystals are recoverable from narrative metadata

7. **Echo Determinism**:
   - `STRICT mode ⟹ echo.output = trace.output` (exact)
   - `LUCID + DETERMINISTIC ⟹ echo.drift = 0.0` (reproducible)
   - `LUCID + PROBABILISTIC ⟹ echo.drift > 0.0` (drift expected)
   - `LUCID + CHAOTIC ⟹ fallback to STRICT` (unsafe to replay)

## Integration

### AGENTESE Paths

```python
# Recording (invisible - happens at runtime layer)
# No direct AGENTESE paths - Historian is transparent

# Retrieval
await logos.invoke("self.memory.witness", {
    "agent_id": "gardener-001",
    "limit": 100
})  # → list[SemanticTrace]

# Narrative generation
await logos.invoke("self.memory.tell", {
    "trace_ids": ["abc123", "def456"],
    "genre": "noir",
    "verbosity": "verbose"
})  # → Narrative

# Replay
await logos.invoke("self.memory.echo", {
    "trace_id": "abc123",
    "mode": "lucid"
})  # → Echo
```

### W-gent Integration

The `HistorianTap` observes W-gent wire protocol frames without mutation:

```python
# Wire tap observes frames
tap = HistorianTap(historian)
wire.add_tap(tap)

# Frames flow through unchanged
# INVOKE_START → begin_trace()
# INVOKE_END → end_trace()
# ERROR → abort_trace()
```

### D-gent Integration

Crystals are stored in D-gent for persistence:

```python
store = DgentCrystalStore(dgent_client)
historian = Historian(store)
```

### L-gent Integration

Semantic embeddings for retrieval:

```python
# L-gent computes vectors for crystals
crystal.vector = await lgent.embed(crystal.action + str(crystal.inputs))

# Query by semantic similarity
similar = store.semantic_search("authentication failures", limit=10)
```

## Anti-Patterns

1. **Storing Narrative at Write-Time**
   - Don't: `trace.narrative = "The agent tried to..."`
   - Do: Store semantic atoms, generate narrative at read-time
   - Why: Wastes tokens, locks in single perspective, prevents Rashomon

2. **Agent Self-Awareness**
   - Don't: `agent.log("I'm doing X")`
   - Do: Historian observes invisibly via wire tap
   - Why: Agents should be pure, recording is a cross-cutting concern

3. **Mixing Recording and Business Logic**
   - Don't: `await agent.invoke_and_trace(input)`
   - Do: Runtime adds tracing transparently
   - Why: Separation of concerns, composability

4. **Replaying CHAOTIC Operations**
   - Don't: `echo_from(api_call_trace, mode=LUCID)`
   - Do: Check determinism, fallback to STRICT for CHAOTIC
   - Why: External APIs may have changed, produce side effects

5. **Resurrection Instead of Echo**
   - Don't: "This will replay the exact same execution"
   - Do: "This creates an echo - similar but not identical for probabilistic ops"
   - Why: LLMs are non-ergodic, drift is expected and informative

## Implementation Reference

**Core**: `impl/claude/agents/n/`

| Module | Purpose |
|--------|---------|
| `types.py` | SemanticTrace, Determinism, Action vocabulary |
| `historian.py` | Historian, TraceContext, invisible recording |
| `tap.py` | HistorianTap (W-gent integration) |
| `store.py` | CrystalStore ABC, MemoryCrystalStore |
| `dgent_store.py` | DgentCrystalStore (D-gent backed) |
| `bard.py` | Bard, ForensicBard, Narrative types |
| `echo_chamber.py` | EchoChamber, LucidDreamer, Echo types |
| `chronicle.py` | Chronicle, Interaction (multi-agent weaving) |
| `epistemic.py` | Epistemic status tracking |
| `integrations.py` | L-gent, M-gent integrations |

**Usage Example**:

```python
# Setup (runtime level)
store = MemoryCrystalStore()
historian = Historian(store)
tap = HistorianTap(historian)
wire.add_tap(tap)

# Agent execution (invisible recording)
result = await agent.invoke(input)

# Later: Generate narrative
traces = store.query(agent_id="agent-1", limit=100)
bard = Bard(llm_provider)
narrative = await bard.invoke(NarrativeRequest(
    traces=traces,
    genre=NarrativeGenre.NOIR,
    verbosity=Verbosity.VERBOSE
))
print(narrative.render("markdown"))

# Replay for debugging
chamber = EchoChamber(traces)
echo = await chamber.echo_from(traces[5], mode=EchoMode.LUCID)
if echo.drift and echo.drift > 0.3:
    print(f"Significant drift detected: {echo.drift}")
```

---

**Key Design Decision**: By separating recording (Historian) from telling (Bard) and replay (Echo), we acknowledge that:
1. Story is projection, not ground truth (Rashomon)
2. Recording should be invisible (agents stay pure)
3. LLMs are non-ergodic (echoes show drift)
4. Multiple genres from one dataset (save tokens)
