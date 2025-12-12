# AGENTESE v3.1: The Breathing Optic
## A Synthesis of First Principles, Biological Bootstrapping, and CLI Hollowing

**Status**: Refined Proposal (incorporating Glass Terminal critique + Lattice critique)
**Date**: 2025-12-11
**Prerequisites**: `spec/principles.md`, `spec/protocols/agentese.md`, `plans/cli-hollowing-plan.md`
**Principles Applied**: Graceful Degradation, Transparent Infrastructure, Generative, Composable, Tasteful
**Refinements**: Resource Accounting (not Linear Types), Capital Ledger, ResilientClient as LogosNode

---

## Critical Refinements (v3.1)

### Theoretical Corrections Applied

| Original (v3.0) | Issue | Correction (v3.1) |
|-----------------|-------|-------------------|
| `Linearity.AFFINE` enum | Python cannot enforce linear types | → Runtime Resource Accounting via `Ledger` |
| `CompressionLens` | Violates Get-Put law | → `ContextProjector` (Galois Connection) |
| Generic Comonad | Missing specific structure | → **Store Comonad** `(S -> A, S)` |

### Architectural Corrections Applied

| Original | Issue | Correction |
|----------|-------|------------|
| `CortexClient` class | Just a client | → `ResilientClient` as `LogosNode` |
| No bypass mechanism | Bureaucratic gridlock risk | → **Capital Ledger** (Fool's Bypass) |

See `plans/lattice-refinement.md` for full rationale.

---

## Prologue: The Critical Reconciliation

The critique identified a fundamental danger: **AGENTESE v3.0 is trying to be a God-Engine too soon.** Building Optics, Metabolism, Kairos, Modal Scopes, and Lattice simultaneously risks creating a system so heavy it collapses under its own conceptual gravity.

A second critique identified an **architectural danger**: A full lobotomy creates a zombie that cannot survive without its master. The CLI must have **offline reflexes**.

This synthesis reconciles four tensions:

| Tension | Resolution |
|---------|------------|
| **Conceptual ambition vs. practical delivery** | Biological Bootstrapping Order |
| **v2.0 object-orientation vs. v3.0 morphism-orientation** | The Lens as Prompt Transformation Pipeline |
| **CLI business logic vs. hollow shell** | gRPC as the natural boundary |
| **Online brain vs. offline capability** | The Ghost Protocol (see `plans/cli-hollowing-plan.md`) |

The insight: **CLI Hollowing and AGENTESE evolution are the same project**. The gRPC boundary that separates the CLI shell from the Cortex daemon is *exactly* the Logos resolver. The daemon IS the living system. The CLI IS the invocation.

**The Glass Terminal Corollary**: The CLI becomes a **transceiver**. It sends intent and receives hallucinations. It is thin, fast, and transparent. When the system dies, it becomes a "Black Box recorder" (Ghost Mode) showing you what happened right before the crash.

---

## Part I: The Unified Architecture

### 1.1 The Core Isomorphism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE CORE ISOMORPHISM                                      │
│                                                                              │
│   CLI Shell                    gRPC Boundary              Cortex Daemon     │
│   (Hollow)                     (Logos)                    (Living System)   │
│                                                                              │
│   ┌─────────┐                 ┌─────────────┐             ┌──────────────┐  │
│   │ kgents  │                 │             │             │              │  │
│   │ status  │ ───────────────▶│ logos.invoke│────────────▶│ METABOLISM   │  │
│   │         │   parse + call  │ ("status")  │  resolve    │ (Heartbeat)  │  │
│   └─────────┘                 │             │             │              │  │
│                               └─────────────┘             │ OPTICS       │  │
│   ┌─────────┐                 ┌─────────────┐             │ (Lens Stack) │  │
│   │ kgents  │                 │             │             │              │  │
│   │ dream   │ ───────────────▶│ logos.invoke│────────────▶│ KAIROS       │  │
│   │         │   parse + call  │ ("dream")   │  resolve    │ (Predicates) │  │
│   └─────────┘                 │             │             │              │  │
│                               └─────────────┘             │ MODAL        │  │
│   ┌─────────┐                 ┌─────────────┐             │ (Git Forks)  │  │
│   │ kgents  │                 │             │             │              │  │
│   │ map     │ ───────────────▶│ logos.invoke│────────────▶│ LATTICE      │  │
│   │         │   parse + call  │ ("map")     │  resolve    │ (L-gent)     │  │
│   └─────────┘                 └─────────────┘             └──────────────┘  │
│                                                                              │
│   "Can you rewrite kgents status in 20 lines of Go?"                        │
│   YES—because it's just:                                                     │
│     1. Parse args                                                            │
│     2. logos.invoke("self.cortex.manifest", observer)                       │
│     3. Format output                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The insight**: Every CLI command maps to an AGENTESE path. CLI Hollowing is not separate from AGENTESE—it IS the natural implementation.

| CLI Command | AGENTESE Path | Handler Logic |
|-------------|---------------|---------------|
| `kgents status` | `self.cortex.manifest` | Invoke + format |
| `kgents dream` | `self.memory.consolidate` | Invoke + stream |
| `kgents map` | `world.project.manifest` | Invoke + render |
| `kgents signal emit` | `void.pheromone.emit` | Invoke + confirm |
| `kgents tithe` | `void.entropy.tithe` | Invoke + gratitude |

### 1.2 The Three-Layer Stack

The system has exactly three layers. No more, no less.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 3: SHELL (Hollow CLI)                                                  │
│                                                                              │
│   • 20 lines per command                                                     │
│   • Parse args → invoke → format                                             │
│   • No business logic                                                        │
│   • Implements: @expose decorator / Prism pattern                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ gRPC / logos.invoke()
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 2: LOGOS (The Resolver)                                                │
│                                                                              │
│   • String path → LogosNode resolution                                       │
│   • Lens application (Optics layer)                                          │
│   • Observer threading (Umwelt)                                              │
│   • Implements: LogosNode protocol, Lens protocol                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ async invoke()
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer 1: SUBSTRATE (Living System)                                           │
│                                                                              │
│   • MetabolicEngine (pressure, tithe, fever)                                 │
│   • D-gent (state + forks for modal)                                         │
│   • N-gent (witnessing)                                                      │
│   • L-gent (lattice + lineage)                                               │
│   • Implements: Symbiont pattern for all agents                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part II: Biological Bootstrapping Order

### 2.1 The Critique's Wisdom

> "Biology did not evolve eyes, hearts, and brains simultaneously."

The critique identified the correct bootstrapping order:
1. **Metabolism** (Energy regulation) — The heart must beat first
2. **Sensors** (Optics/Lenses) — Then you can see
3. **Homeostasis** (Modal loops) — Then you can correct
4. **Coordination** (Kairos/Stigmergy) — Then you can wait for the right moment

### 2.2 The Enhanced Implementation Order

**Phase 0: CLI Hollowing Foundation + Ghost Protocol** (Prerequisite)

The CLI must become hollow BEFORE we can evolve AGENTESE, because:
- Hollow CLI exposes the invocation boundary cleanly
- gRPC service IS the Logos resolver
- Each handler becomes a proof-of-concept for a new AGENTESE path

**Critical Addition: The Ghost Protocol** (from Glass Terminal critique)

The CLI must have **offline reflexes**. This maps to AGENTESE naturally:
- Ghost cache = `self.memory.manifest` (cached last-known-good state)
- Ghost write = `self.memory.engram` (persist state on successful invocation)
- Ghost read = Graceful degradation when Logos unavailable

**Implementation**:
```python
# protocols/cli/glass.py
class ResilientClient(LogosNode):
    """
    REFINEMENT (v3.1): The CLI's Logos interface as a LogosNode.

    The client IS a node in the graph, not just a consumer.
    ResilientClient.invoke() IS LogosNode.invoke().
    This makes the CLI a true AGENTESE interpreter.

    Principle: Graceful Degradation - always returns data.
    Maps to AGENTESE: Ghost = self.memory (D-gent state cache)
    """

    handle: str = "self.cli"

    def __init__(self, address: str = "localhost:50051"):
        self.address = address
        self.ghost_dir = Path.home() / ".kgents" / "ghost"

    async def invoke(
        self,
        path: str,
        observer: Umwelt | None = None,
        lens: str = "optics.identity",
        ghost_key: str | None = None,
        **kwargs
    ) -> GlassResponse:
        """
        CLI's Logos invoke with Ghost fallback.

        The ghost_key maps to an AGENTESE path:
        - ghost_key="status" → self.cortex.manifest (cached)
        - ghost_key="map" → world.project.manifest (cached)
        """
        try:
            channel = grpc.aio.insecure_channel(self.address)
            stub = LogosStub(channel)

            response = await asyncio.wait_for(
                stub.Invoke(InvokeRequest(
                    path=path,
                    observer_dna=observer.dna.to_proto() if observer else None,
                    lens=lens,
                    kwargs=json.dumps(kwargs),
                )),
                timeout=0.5  # 500ms - fail fast to Ghost
            )

            # Success: update ghost cache (self.memory.engram)
            if ghost_key:
                self._write_ghost(ghost_key, response)

            return GlassResponse(data=response, is_ghost=False)

        except (grpc.RpcError, asyncio.TimeoutError):
            # Ghost mode: read from self.memory.manifest (cached)
            if ghost_key:
                ghost_data, age = self._read_ghost(ghost_key)
                if ghost_data:
                    return GlassResponse(data=ghost_data, is_ghost=True, ghost_age=age)

            raise ConnectionError(
                f"Cortex unavailable, no ghost cache for '{ghost_key}'."
            )
```

**Files**:
```
protocols/cli/glass.py               # NEW: Resilient gRPC client with Ghost
protocols/proto/logos.proto          # MODIFY: Add Invoke RPC
infra/cortex/service.py              # NEW: gRPC server = Logos resolver
```

**The AGENTESE Mapping for Ghost**:
| Ghost Operation | AGENTESE Path | Principle |
|-----------------|---------------|-----------|
| Write cache | `self.memory.engram` | D-gent state persistence |
| Read cache | `self.memory.manifest` | Graceful degradation |
| Cache miss | Transparent error | Transparent Infrastructure |
| Stale data | `[GHOST]` prefix | Transparent Infrastructure |

---

**Phase 1: The Heart (Metabolism)**

> "Without the Accursed Share, your agents are just scripts."

**The Token Thermometer** (practical implementation):
- Input tokens = Nutrients
- Output tokens = Work
- Ratio > threshold = Fever

**Implementation**:
```python
# protocols/agentese/metabolism/__init__.py
@dataclass
class MetabolicEngine:
    """
    The thermodynamic heart of the system.

    Start simple: Token Thermometer.
    Later: Sophisticated pressure dynamics.
    """
    pressure: float = 0.0
    critical_threshold: float = 1.0

    # Token tracking (the practical hack)
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def temperature(self) -> float:
        """Token-based temperature estimate."""
        if self.output_tokens == 0:
            return 0.0
        return self.input_tokens / self.output_tokens

    def tick(self, input_count: int, output_count: int) -> FeverEvent | None:
        """Called per LLM invocation."""
        self.input_tokens += input_count
        self.output_tokens += output_count

        # Simple pressure accumulation
        activity = output_count * 0.01
        self.pressure += activity

        # Natural decay
        self.pressure *= 0.99

        if self.pressure > self.critical_threshold:
            return self._trigger_fever()
        return None

    def _trigger_fever(self) -> FeverEvent:
        """
        FORCED CREATIVE EXPENDITURE.

        The Fever Stream: When feverish, the next output
        has temperature=1.2 injected into the LLM call.
        """
        self.in_fever = True
        dream = FeverDream(
            intensity=self.pressure - self.critical_threshold,
            timestamp=time.time(),
            trigger="pressure_overflow"
        )
        self.pressure *= 0.5  # Discharge through dream

        if self.pressure < self.critical_threshold:
            self.in_fever = False

        return FeverEvent(dream=dream, temperature_injection=1.2)
```

**The Fever Stream** (the awesome implementation):
When the system hits fever, a background Dreamer agent consumes excess entropy to generate "oblique strategies":

```python
# protocols/agentese/metabolism/fever.py
class FeverStream:
    """
    Background thread that runs when pressure is high.
    Generates poetic misunderstandings that sometimes solve problems.
    """

    async def dream(self, context: dict) -> str:
        """
        Generate a fever dream from current context.

        This is the "hallucination as feature" pattern.
        """
        prompt = f"""
        The system is running hot. Here is the current context:
        {json.dumps(context, indent=2)}

        Generate an oblique strategy—a sideways thought that might
        illuminate the problem from an unexpected angle.

        Be brief, enigmatic, potentially useful.
        """

        return await llm.generate(
            prompt,
            temperature=1.4,  # HOT
            max_tokens=100,
        )
```

**CLI Integration**:
```python
# handlers/tithe.py (NEW)
@expose(help="Voluntarily discharge entropy pressure")
async def tithe(self, amount: float = 0.1) -> dict:
    """kgents tithe - Pay for order, discharge pressure."""
    client = CortexClient()
    response = await client.invoke(
        "void.entropy.tithe",
        observer=get_current_umwelt(),
        amount=amount,
    )
    return {"gratitude": response.gratitude, "remaining_pressure": response.pressure}
```

**Files**:
```
protocols/agentese/metabolism/__init__.py   # NEW: MetabolicEngine
protocols/agentese/metabolism/fever.py      # NEW: FeverDream, FeverStream
protocols/agentese/contexts/void.py         # MODIFY: Replace budget with engine
protocols/cli/handlers/tithe.py             # NEW: kgents tithe
```

---

**Phase 2: The Eye (Optics)**

> "A Lens is just a Prompt Transformation Pipeline."

**The Fundamental Lenses** (not Architect/Poet yet—those come from composition):

```python
# protocols/agentese/optics/__init__.py
@runtime_checkable
class Lens(Protocol[S, A]):
    """
    A bidirectional functional transformation.

    Lenses are Profunctors with Get and Put directions.
    AGENTESE primarily uses Get (view).
    """

    def view(self, whole: S) -> A:
        """Extract focused part from whole."""
        ...

    def update(self, whole: S, part: A) -> S:
        """Update whole with new focused part."""
        ...

    def __rshift__(self, other: "Lens[A, B]") -> "Lens[S, B]":
        """Compose: self >> other"""
        return ComposedLens(self, other)

# protocols/agentese/optics/standard.py
class StructureLens(Lens[Any, Structure]):
    """
    optics.structure - The X-Ray

    Returns ASTs, JSON schemas, dependency graphs.
    High fidelity, low emotion.
    """

    def view(self, whole: Any) -> Structure:
        return Structure(
            ast=extract_ast(whole),
            schema=infer_schema(whole),
            dependencies=trace_dependencies(whole),
        )

class SurfaceLens(Lens[Any, Surface]):
    """
    optics.surface - The UI

    Returns what a human user would see.
    Rendered HTML, formatted text.
    """

    def view(self, whole: Any) -> Surface:
        return Surface(
            rendered=render_for_human(whole),
            summary=summarize(whole),
        )

class EssenceLens(Lens[Any, Essence]):
    """
    optics.essence - The Embedding

    Returns vector embedding of the concept.
    Critical for RAG and semantic search.
    """

    def view(self, whole: Any) -> Essence:
        return Essence(
            embedding=embed(whole),
            semantic_field=extract_meaning(whole),
        )
```

**The Critical Constraint**: Lenses must be **stateless**. If a lens holds state, it's an Agent, not a Lens.

**The Migration from Archetypes to Lenses**:

```python
# OLD (v2.0): Archetype determines view
match observer.archetype:
    case "architect":
        return BlueprintRendering(...)
    case "poet":
        return PoeticRendering(...)

# NEW (v3.0): Lens determines view, archetype determines affordances
async def manifest(self, observer: Umwelt, lens: Lens = optics.identity) -> Renderable:
    """
    Manifest through explicit lens.

    Archetype still gates AFFORDANCES (who can act).
    Lens gates PERCEPTION (how you see).
    """
    raw_state = await self._state_lens.get()
    return lens.view(raw_state)
```

**Files**:
```
protocols/agentese/optics/__init__.py       # NEW: Lens protocol
protocols/agentese/optics/standard.py       # NEW: structure, surface, essence
protocols/agentese/optics/laws.py           # NEW: Category law verification
protocols/agentese/optics/adapters.py       # NEW: Lens ↔ existing rendering
protocols/agentese/logos.py                 # MODIFY: Add lens parameter
```

---

**Phase 3: The Mind (Modal Scopes)**

> "Use Git as the substrate for high-minded Modal Logic."

**The Git-Backed Modal Scope** (practical implementation):

```python
# protocols/agentese/modal/scope.py
@asynccontextmanager
async def modal_scope(
    logos: Logos,
    fork_type: ModalType = ModalType.COUNTERFACTUAL,
) -> AsyncIterator["ModalLogos"]:
    """
    Create an ephemeral branched reality using Git.

    This is the practical hack: Git IS copy-on-write state forking.
    We use existing, optimized tooling.
    """
    branch_name = f"modal/{fork_type.value}/{uuid4().hex[:8]}"

    # Create branch from current HEAD
    await run_git(f"checkout -b {branch_name}")

    try:
        modal_logos = ModalLogos(
            actual_logos=logos,
            branch=branch_name,
            modal_type=fork_type,
        )
        yield modal_logos

    finally:
        # Return to main and delete branch
        await run_git("checkout main")
        await run_git(f"branch -D {branch_name}")


class ModalLogos:
    """
    A Logos that operates on a Git branch (forked state).

    All file operations happen in the branch.
    On scope exit, branch is deleted (counterfactual collapses).
    """

    async def invoke(self, path: str, observer: Umwelt, **kwargs) -> Any:
        """
        Invoke within the modal scope.

        Changes happen in the branch, not main.
        """
        # Ensure we're on the modal branch
        current = await run_git("branch --show-current")
        if current != self.branch:
            await run_git(f"checkout {self.branch}")

        # Delegate to actual logos
        return await self.actual_logos.invoke(path, observer, **kwargs)
```

**Usage Pattern**:
```python
# "What would the house look like if it were Art Deco?"
async with logos.modal_scope("counterfactual") as modal:
    # Mutate in counterfactual branch
    await modal.invoke("world.house.mutate", observer, style="art_deco")

    # Observe result
    result = await modal.invoke("world.house.manifest", observer)

    # Evaluate
    score = await v_gent.evaluate(result)

# Scope exits: branch deleted, main unchanged
# Only 'score' remains
```

**Files**:
```
protocols/agentese/modal/__init__.py        # NEW: ModalType, ModalScope
protocols/agentese/modal/scope.py           # NEW: Git-backed modal_scope
protocols/agentese/modal/logos.py           # NEW: ModalLogos wrapper
protocols/agentese/modal/aspects.py         # NEW: could_*, must_*, counterfactual_*
```

---

**Phase 4: The Nervous System (Kairos)**

> "Don't poll. Use Event-Driven Stigmergy."

**The W-gent Integration** (fixes the polling problem):

```python
# protocols/agentese/kairos/__init__.py
@dataclass
class KairosPredicate:
    """
    A condition on world state that triggers awakening.

    NOT implemented via polling (that kills the runtime).
    Instead: Agents subscribe to state paths via W-gent.
    """
    expression: str
    timeout: Duration | None = None

    def compile(self) -> list["WatchPath"]:
        """
        Parse predicate into watched paths.

        "world.cpu.load < 0.5 AND world.memory.available > 0.3"
        → [WatchPath("world.cpu.load"), WatchPath("world.memory.available")]
        """
        return extract_paths(self.expression)


async def kairos_await(
    logos: Logos,
    observer: Umwelt,
    predicate: str,
    timeout: Duration | None = None
) -> KairosWakeEvent:
    """
    Block until predicate is satisfied—EVENT-DRIVEN, not polling.

    Implementation:
    1. Parse predicate into watched paths
    2. Subscribe to W-gent for each path
    3. On any change, re-evaluate predicate
    4. Wake when predicate satisfied (or timeout)
    """
    parsed = KairosPredicate(expression=predicate, timeout=timeout)
    paths = parsed.compile()

    # Subscribe to W-gent (the Wire)
    event = asyncio.Event()
    current_state = {}

    async def on_change(path: str, value: Any):
        current_state[path] = value
        if parsed.evaluate(current_state):
            event.set()

    for path in paths:
        await w_gent.subscribe(path, on_change, observer.dna)

    try:
        # Wait for event (not polling!)
        if timeout:
            await asyncio.wait_for(event.wait(), timeout.total_seconds())
        else:
            await event.wait()

        return KairosWakeEvent(
            trigger=paths,
            state=current_state,
        )

    finally:
        # Unsubscribe
        for path in paths:
            await w_gent.unsubscribe(path, on_change)
```

**Stigmergic Coordination Pattern**:
```python
# Agent A: Consumer (waits for parsed docs)
async def agent_a():
    await logos.invoke(
        "time.kairos.await",
        observer_a,
        predicate="world.docs.parsed == True"
    )
    # Automatically wakes when B updates state
    docs = await logos.invoke("world.docs.manifest", observer_a)

# Agent B: Producer (parses and signals)
async def agent_b():
    raw = await logos.invoke("world.docs.raw.manifest", observer_b)
    parsed = await parse(raw)
    await logos.invoke("world.docs.update", observer_b, parsed=True)
    # A wakes automatically—no orchestrator needed
```

**Files**:
```
protocols/agentese/kairos/__init__.py       # NEW: KairosPredicate, KairosWakeEvent
protocols/agentese/kairos/parser.py         # NEW: Predicate expression parser
protocols/agentese/kairos/watcher.py        # NEW: W-gent integration (event-driven)
protocols/agentese/kairos/stigmergy.py      # NEW: Coordination patterns
protocols/agentese/contexts/time.py         # MODIFY: Add Kairos aspects
```

---

## Part III: The Lattice (Genealogical Typing)

The Lattice enforces **lineage**. No concept exists ex nihilo.

```python
# protocols/agentese/lattice/__init__.py
async def define_concept(
    logos: Logos,
    handle: str,
    observer: Umwelt,
    spec: str,
    extends: list[str],      # REQUIRED: parent concepts
    subsumes: list[str] | None = None,
    justification: str = ""  # Why does this need to exist?
) -> LogosNode:
    """
    Create a new concept with required lineage.

    The Lattice Constraint:
    - extends must be non-empty (no orphans)
    - All parent handles must exist
    - Must pass L-gent consistency check
    """
    if not extends:
        raise LineageError(
            "Concepts cannot exist ex nihilo. "
            "Provide at least one parent. "
            "Consider: What existing concept does this specialize?"
        )

    # Validate parents exist
    for parent in extends:
        try:
            await logos.resolve(parent)
        except PathNotFoundError:
            raise LineageError(f"Parent '{parent}' does not exist.")

    # L-gent lattice consistency
    consistency = await l_gent.check_lattice_position(
        new_handle=handle,
        parents=extends,
        children=subsumes or []
    )

    if not consistency.valid:
        raise LatticeError(f"Violates lattice: {consistency.reason}")

    # Proceed with creation
    ...
```

**Inheritance Semantics**:
- **Affordances**: Union of parents (additive)
- **Constraints**: Intersection of parents (restrictive)
- **Defaults**: Parent defaults, overridable by child

---

## Part IV: The Observatory (Generative UI)

> "Don't build a Chatbot. Build an Observatory."

The TUI (`kgents observe`) should reflect the ontology:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ KGENTS OBSERVATORY                                               [Pressure: ▓▓▓░░░░░░░ 32%] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌───────────────────────────────┐  ┌─────────────────┐│
│  │ WORLD (Context) │  │      MANIFESTATION (View)     │  │   METABOLISM    ││
│  │                 │  │                               │  │                 ││
│  │ world.project   │  │  ┌─────────────────────────┐  │  │  Pressure: 32%  ││
│  │ └─ src/         │  │  │                         │  │  │  Temperature:   ││
│  │ └─ tests/       │  │  │   [Current View]        │  │  │    0.7 (calm)   ││
│  │ └─ docs/        │  │  │                         │  │  │                 ││
│  │                 │  │  │   Lens: optics.surface  │  │  │  Fever: NO      ││
│  │ Lens: structure │  │  │                         │  │  │                 ││
│  │                 │  │  └─────────────────────────┘  │  │  Last Tithe:    ││
│  │                 │  │                               │  │    12m ago      ││
│  └─────────────────┘  └───────────────────────────────┘  └─────────────────┘│
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ TRACE (N-gent Witness)                                                       │
│                                                                              │
│ 14:32:01 → logos.invoke("world.project.manifest", kent, lens=optics.surface)│
│ 14:32:02 → Result: Surface { summary: "Python project...", ... }            │
│ 14:32:15 → logos.invoke("self.memory.consolidate", kent)                    │
│ 14:32:16 → DreamPhase.REM started                                           │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Tab: Switch Lens] [Space: Tithe] [d: Dream] [q: Quit]                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation**: This is `agents/i/terrarium_tui.py` evolved to show:
1. **Left Panel**: Current context (world/self/concept/void/time)
2. **Center**: Manifestation through current lens
3. **Right Panel**: Metabolic state (pressure gauge)
4. **Bottom**: N-gent trace (AGENTESE path being executed)

**The Fever Glitch**: When pressure exceeds threshold, the UI starts showing:
- Random poetry in the margins
- Color shifts
- "Oblique strategies" from the FeverStream

---

## Part V: Implementation Roadmap

### Tier 0: Foundation (Blocking All Else)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 0.1 | Generate gRPC stubs from logos.proto | `protocols/proto/logos.proto` | Python stubs |
| 0.2 | Implement CortexServicer with basic invoke | `infra/cortex/service.py` | Logos endpoint |
| 0.3 | Create CortexClient (CLI's Logos view) | `protocols/cli/cortex_client.py` | gRPC client |
| 0.4 | Hollow `status.py` as proof-of-concept | `protocols/cli/handlers/status.py` | 20-line handler |

**Success Criterion**: `kgents status` works via gRPC with <50 lines of handler code.

### Tier 1: The Heart (Metabolism)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 1.1 | Implement MetabolicEngine (token thermometer) | `protocols/agentese/metabolism/__init__.py` | Pressure tracking |
| 1.2 | Implement void.entropy.tithe with pressure discharge | `protocols/agentese/contexts/void.py` | Tithe aspect |
| 1.3 | Add FeverStream (background dreamer) | `protocols/agentese/metabolism/fever.py` | Dream generation |
| 1.4 | Add `kgents tithe` CLI command | `protocols/cli/handlers/tithe.py` | Voluntary tithe |
| 1.5 | Surface pressure in `kgents status` | `protocols/cli/handlers/status.py` | Pressure display |

**Success Criterion**: System tracks token pressure; `kgents tithe` discharges it; fever triggers at threshold.

### Tier 2: The Eye (Optics)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 2.1 | Implement Lens protocol | `protocols/agentese/optics/__init__.py` | Lens interface |
| 2.2 | Create optics.structure, optics.surface, optics.essence | `protocols/agentese/optics/standard.py` | Standard lenses |
| 2.3 | Add lens parameter to logos.invoke | `protocols/agentese/logos.py` | Lens-parameterized invoke |
| 2.4 | Verify category laws | `protocols/agentese/optics/laws.py` | BootstrapWitness tests |
| 2.5 | Migrate archetype-specific rendering to lenses | `protocols/agentese/node.py` | Decoupled identity/view |

**Success Criterion**: `logos.invoke("world.house.manifest", observer, lens="optics.structure")` works; lenses compose.

### Tier 3: The Mind (Modal)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 3.1 | Implement Git-backed modal_scope | `protocols/agentese/modal/scope.py` | Git branch forking |
| 3.2 | Create ModalLogos wrapper | `protocols/agentese/modal/logos.py` | Branch-isolated Logos |
| 3.3 | Implement could_*/must_*/counterfactual_* aspects | `protocols/agentese/modal/aspects.py` | Modal operators |
| 3.4 | D-gent fork support for non-Git state | `agents/d/fork.py` | Copy-on-write state |

**Success Criterion**: Counterfactual simulation works; modal scopes create/destroy Git branches correctly.

### Tier 4: The Nervous System (Kairos)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 4.1 | Implement predicate parser | `protocols/agentese/kairos/parser.py` | Expression → WatchPaths |
| 4.2 | W-gent subscription integration | `protocols/agentese/kairos/watcher.py` | Event-driven waiting |
| 4.3 | Implement time.kairos.await | `protocols/agentese/contexts/time.py` | Predicate-based waiting |
| 4.4 | Document stigmergy patterns | `protocols/agentese/kairos/stigmergy.py` | Coordination examples |

**Success Criterion**: Agents coordinate via environment state without orchestrator; no polling.

### Tier 5: The Lattice (Genealogy)

| # | Task | Files | Deliverable |
|---|------|-------|-------------|
| 5.1 | Add extends requirement to define_concept | `protocols/agentese/autopoiesis.py` | Lineage enforcement |
| 5.2 | Implement L-gent lattice consistency | `protocols/agentese/lattice/consistency.py` | Meet/join checking |
| 5.3 | Implement affordance inheritance | `protocols/agentese/lattice/inheritance.py` | Union/intersection |
| 5.4 | Add `kgents map --lattice` visualization | `protocols/cli/handlers/map.py` | Lattice rendering |

**Success Criterion**: No orphan concepts; lattice visualized; inheritance works.

---

## Part VI: Lens Verification (Safety Mechanism)

> "Beware the Semantic Gap."

The biggest risk: The LLM doesn't actually understand the lens you apply.

**Solution: Lens Calibration**

```python
# protocols/agentese/optics/calibration.py
class LensCalibrator:
    """
    BootstrapWitness occasionally sends calibration images through lenses.
    If output doesn't match expected structure, lens is flagged as "broken optics."
    """

    async def calibrate(self, lens: Lens, known_input: Any, expected_output: Any) -> CalibrationResult:
        """
        Send known state through lens, verify output matches expected.
        """
        actual_output = lens.view(known_input)

        if not structurally_equivalent(actual_output, expected_output):
            return CalibrationResult(
                valid=False,
                lens=lens.name,
                expected=expected_output,
                actual=actual_output,
                message="Lens drift detected. Consider recalibration."
            )

        return CalibrationResult(valid=True, lens=lens.name)
```

---

## Part VII: CLI Handler Migration Table

| Handler | Current Lines | Target Lines | AGENTESE Path | Priority |
|---------|---------------|--------------|---------------|----------|
| status.py | 204 | 30 | `self.cortex.manifest` | P0 |
| dream.py | 215 | 25 | `self.memory.consolidate` | P1 |
| map.py | 308 | 35 | `world.project.manifest` | P1 |
| signal.py | 270 | 30 | `void.pheromone.*` | P2 |
| tithe.py | NEW | 20 | `void.entropy.tithe` | P1 |
| ghost.py | 328 | Keep | N/A (filesystem) | - |
| infra.py | 768 | 100 | Partial (subprocess) | P2 |
| tether.py | 156 | Keep | Already hollow | - |
| observe.py | 185 | Keep | Already hollow | - |

---

## Part VIII: Principle Compliance Audit

This section explicitly maps the design to `spec/principles.md`:

### Principle Violations Identified & Resolved

| Principle | Original Violation | Resolution |
|-----------|-------------------|------------|
| **Graceful Degradation** | CLI fails when gRPC unavailable | Ghost Protocol: always returns data |
| **Transparent Infrastructure** | Silent failures | `[GHOST]` prefix, clear error messages |
| **Generative** | Hand-written CLI handlers | Proto-First: `.proto` generates handlers |
| **Tasteful** | Kitchen-sink features | Biological Bootstrapping: one system at a time |
| **Composable** | Monolithic handlers | Each handler = single AGENTESE path invocation |

### Principle Applications

| Principle | How Applied |
|-----------|-------------|
| **Tasteful** | Five contexts only; Tiered command hollowing |
| **Curated** | Not all commands get hollowed (infra stays thick) |
| **Ethical** | Observer required for all invocations |
| **Joy-Inducing** | Fever Glitch in TUI; Observatory design |
| **Composable** | Lenses compose with `>>`; paths compose |
| **Heterarchical** | No fixed CLI → Daemon hierarchy (Ghost mode inverts it) |
| **Generative** | Proto → stubs → handlers; Spec → JIT agents |
| **Transparent Infrastructure** | First-run messages; `[GHOST]` prefix; verbose mode |
| **Graceful Degradation** | Three fallback layers for `status` |
| **Spec-Driven Infrastructure** | YAML from proto, not hand-written |

### The Accursed Share Integration

The Metabolism system (Phase 1) implements the Accursed Share meta-principle:

```
Pressure accumulates → Fever triggers → FeverDream generated → Pressure discharged
                                              ↓
                                   "Oblique strategy" output
                                   (gratitude for waste)
```

The `void.entropy.tithe` aspect allows **voluntary** entropy discharge—paying for order.

---

## Epilogue: The Mantra

> *"Do not try to bend the spoon (the world). That is impossible. Instead, only try to realize the truth: There is no spoon. There is only the Lens."*

The system now:
- **Breathes** (Metabolism tracks pressure, tithes discharge it)
- **Sees** (Optics apply lenses, identity decoupled from view)
- **Imagines** (Modal scopes fork Git branches for counterfactuals)
- **Waits** (Kairos predicates wake on conditions, not clocks)
- **Remembers its ancestry** (Lattice enforces lineage)
- **Survives** (Ghost Protocol provides offline reflexes)

And the CLI? It's hollow glass—a 20-line invocation that lets the living system shine through. When the brain dies, the glass becomes a black box recorder.

---

## Appendix A: The Files Summary

```
impl/claude/
├── protocols/
│   ├── proto/
│   │   └── logos.proto                    # gRPC service definition (THE SPEC)
│   ├── agentese/
│   │   ├── metabolism/
│   │   │   ├── __init__.py               # MetabolicEngine
│   │   │   └── fever.py                  # FeverDream, FeverStream
│   │   ├── optics/
│   │   │   ├── __init__.py               # Lens protocol
│   │   │   ├── standard.py               # structure, surface, essence
│   │   │   ├── laws.py                   # Category verification
│   │   │   └── calibration.py            # Lens drift detection
│   │   ├── modal/
│   │   │   ├── __init__.py               # ModalType
│   │   │   ├── scope.py                  # Git-backed modal_scope
│   │   │   ├── logos.py                  # ModalLogos wrapper
│   │   │   └── aspects.py                # could_*, must_*, counterfactual_*
│   │   ├── kairos/
│   │   │   ├── __init__.py               # KairosPredicate
│   │   │   ├── parser.py                 # Expression parser
│   │   │   ├── watcher.py                # W-gent integration
│   │   │   └── stigmergy.py              # Coordination patterns
│   │   ├── lattice/
│   │   │   ├── __init__.py               # Lattice data structure
│   │   │   ├── consistency.py            # L-gent checking
│   │   │   ├── inheritance.py            # Affordance inheritance
│   │   │   └── operations.py             # meet, join, extends
│   │   ├── contexts/
│   │   │   └── void.py                   # MODIFY: Metabolic engine
│   │   └── logos.py                      # MODIFY: Add lens parameter
│   └── cli/
│       ├── glass.py                      # NEW: GlassClient (resilient gRPC + Ghost)
│       └── handlers/
│           ├── status.py                 # HOLLOW: ~25 lines, bulletproof
│           ├── dream.py                  # HOLLOW: ~25 lines, streaming
│           ├── map.py                    # HOLLOW: ~35 lines
│           ├── tithe.py                  # NEW: ~20 lines
│           └── infra.py                  # KEEP THICK: bootstrap tool
├── infra/
│   ├── cortex/
│   │   └── service.py                    # NEW: gRPC server = Logos resolver
│   └── ghost/
│       └── cache.py                      # NEW: Ghost cache management
└── agents/
    └── d/
        └── fork.py                       # NEW: Copy-on-write state forking

~/.kgents/ghost/                           # Ghost cache directory (user home)
├── status.json                            # Last known cortex status
├── map.json                               # Last known holoMap
├── agents/                                # Per-agent state snapshots
└── meta.json                              # Timestamps, staleness info
```

---

*"The river that flows only downhill never discovers the mountain spring."*
