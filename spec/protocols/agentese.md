# AGENTESE: The Verb-First Ontology

**Where getting IS invoking. Where nouns ARE frozen verbs. Where observation collapses potential into actuality.**

> *"The noun is a lie. There is only the rate of change."*

**Status:** Specification v2.0
**Date:** 2025-12-10
**Prerequisites:** `../principles.md`, `../c-gents/composition.md`
**Integrations:** L-gents (Registry), K-gents (Observer Context), J-gents (JIT Reification), Umwelt (Observer Isolation)

---

## Prologue: The Noun Fallacy

Traditional software systems commit the Noun Fallacy: they treat the world as a database of static objects. You query `world.house` and receive a JSON blob—inert data, lifeless structure.

But consider: When you "get" a house, what are you really doing? You are **perceiving** it. Perception is an action. The house you perceive depends on **who you are**:
- An Architect perceives blueprints, load-bearing walls, structural integrity
- A Poet perceives shelter, memory, the weight of domesticity
- A Demolition Expert perceives stress points, safe collapse vectors

**The AGENTESE Insight**: `world.house` is not a noun. It is a **handle**—a reference to a potential interaction. Grasping a handle is itself an action. What you receive depends on who is grasping.

In AGENTESE: **Nouns are frozen verbs. To read is to invoke.**

---

## Part I: The Core Philosophy

We reject the "Noun Fallacy" (that objects exist statically waiting to be read). Instead, we adopt the **Holonic/Puppet** view defined in Principle #7:

1. **To Observe is to Disturb**: You cannot read `world.house` without an `Observer`.
2. **Handles are Functors**: A handle string (`"world.house"`) is not a reference to an object; it is a **morphism** that maps an `Observer` to an `Interaction`.
3. **Polymorphism is Law**: The same handle must behave differently for different observers (Principle #5: Composable).
4. **No View From Nowhere**: `logos.resolve()` without an observer is an error. Period.

### The Mathematical Definition

In the category of agents:
- **Objects** are States (S).
- **Morphisms** are Agents (A: S → S).
- **Agentese Handles** (H) are functors from the domain of Intent to the domain of Implementation.

```
H(Context) ──Logos──▶ Interaction
```

---

## Part II: The Grammar of Handles

AGENTESE is a hierarchical, dot-notation language for agent-world interaction. It is:
1. **Liturgical**: Reads like an invocation, not a query
2. **Polymorphic**: Same path yields different affordances to different observers
3. **Generative**: Observing with intent can collapse potential into actuality

### 2.1 The Syntax

```
<Context> . <Holon> . <Aspect>
```

| Component | Purpose | Examples |
|-----------|---------|----------|
| **Context** | The domain of interaction | `world`, `self`, `concept`, `void`, `time` |
| **Holon** | The referent being grasped (part-whole) | `house`, `memory`, `justice`, `entropy` |
| **Aspect** | The mode of engagement (verb) | `manifest`, `witness`, `refine`, `sip` |

### 2.2 The Five Strict Contexts

To prevent "kitchen-sink" anti-patterns (Principle #1: Tasteful), we define exactly **five contexts**. No others are permitted without a spec change.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FIVE CONTEXTS                                    │
├─────────────┬───────────────────────────────────────┬───────────────────────┤
│ Context     │ Ontology                              │ Principle Alignment   │
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ world.*     │ The External: entities, environments  │ Heterarchical         │
│             │ tools, resources in flux              │ (resources in flux)   │
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ self.*      │ The Internal: memory, capability,     │ Ethical               │
│             │ state, agent boundaries               │ (boundaries of agency)│
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ concept.*   │ The Abstract: platonics, definitions, │ Generative            │
│             │ logic, compressed wisdom              │ (compressed wisdom)   │
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ void.*      │ The Accursed Share: entropy, noise,   │ Meta-Principle        │
│             │ slop, serendipity, gratitude          │ (gratitude for waste) │
├─────────────┼───────────────────────────────────────┼───────────────────────┤
│ time.*      │ The Temporal: history, forecast,      │ Heterarchical         │
│             │ schedule, traces                      │ (temporal composition)│
└─────────────┴───────────────────────────────────────┴───────────────────────┘
```

### 2.3 Standard Aspects

| Aspect | Meaning | System Action |
|--------|---------|---------------|
| `manifest` | "Collapse to perception" | Invoke `render_state()` (Observable) |
| `witness` | "Show me history" | Return NarrativeLog via N-gent |
| `refine` | "Think harder" | Spawn Dialectician, challenge definition |
| `sip` | "Draw from entropy" | Request from Accursed Share budget |
| `tithe` | "Pay for order" | Sacrifice computation to void |
| `affordances` | "What can I do?" | Return list of available verbs |
| `define` | "Create this concept" | Generative reification |
| `lens` | "Get composable agent" | Return morphism for aspect |

### 2.4 Example Agentese Paths

| Agentese Path | Human Meaning | System Resolution |
|---------------|---------------|-------------------|
| `world.house.manifest` | "Show me the house" | Observer-specific rendering |
| `world.house.witness` | "What happened here?" | Temporal trace via N-gent |
| `self.memory.consolidate` | "Sort my thoughts" | Hypnagogic cycle (D-gent) |
| `concept.justice.refine` | "Think harder about justice" | Dialectical challenge |
| `void.entropy.sip` | "Give me randomness" | Draw from exploration budget |
| `void.gratitude.tithe` | "Pay for order" | Noop sacrifice (Accursed Share) |
| `time.trace.witness` | "Show me the past" | Temporal projection |
| `world.library.define` | "Create a library" | Generative reification from spec |

---

## Part III: The Logos Resolver

The **Logos** is the runtime that resolves AGENTESE paths into agent interactions. It is a **Functor** that lifts strings into executable morphisms.

### 3.1 The Three Layers of Ground

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE LOGOS ARCHITECTURE                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      SPEC LAYER (DNA)                                  │ │
│  │   • Defined in spec/world/house.md                                     │ │
│  │   • Contains generative prompt for concept                             │ │
│  │   • PRINCIPLE: If impl missing, spec generates it (J-gent JIT)         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    SYMBIONT LAYER (Living Instance)                    │ │
│  │   • Active Python instance (stateless logic)                           │ │
│  │   • State held externally (D-gent memory via Lens)                     │ │
│  │   • PRINCIPLE: Logic + Memory = Life (Symbiont Pattern)                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                ↓                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     ASPECT LAYER (Interface)                           │ │
│  │   • Filters instance based on observer's Umwelt                        │ │
│  │   • PRINCIPLE: Tasteful/Curated projection                             │ │
│  │   • Observer DNA determines what is perceived                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 The LogosNode Protocol

Every resolvable entity implements the LogosNode protocol:

```python
from typing import Protocol, runtime_checkable, Any, TypeVar
from dataclasses import dataclass

T_in = TypeVar("T_in", contravariant=True)
T_out = TypeVar("T_out", covariant=True)

@runtime_checkable
class LogosNode(Protocol):
    """
    A node in the AGENTESE graph.

    Every node is a potential interaction, not static data.
    Must be stateless (Symbiont pattern—state via D-gent Lens).

    AGENTESE Principle: Nouns are frozen verbs.
    """

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        ...

    def affordances(self, observer: "AgentMeta") -> list[str]:
        """
        What verbs are available to this observer?

        Enforces Principle #3: Ethical (Permissioning).
        The Polymorphic Principle: Different observers
        receive different affordances.

        Args:
            observer: Metadata about the requesting agent

        Returns:
            List of available aspect names
        """
        ...

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """
        Return the agent morphism for a specific aspect.

        Enforces Principle #5: Composable.
        The returned Agent can be composed with >> operator.

        Args:
            aspect: The verb to get a lens for

        Returns:
            Composable Agent morphism
        """
        ...

    async def manifest(self, observer: "Umwelt") -> "Renderable":
        """
        Collapse the wave function into a representation.

        The Observation Principle: Perception is action.
        What is perceived depends on who perceives.

        Args:
            observer: The observer's projected world (Umwelt)

        Returns:
            Observer-appropriate representation
        """
        ...

    async def invoke(self, aspect: str, observer: "Umwelt", **kwargs) -> Any:
        """
        Execute an affordance on this node.

        Args:
            aspect: The verb to invoke
            observer: The observer's projected world
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result
        """
        ...
```

### 3.3 The Logos Resolver

```python
@dataclass
class Logos:
    """
    The bridge between String Theory and Agent Reality.

    The Logos is a Functor that lifts string paths into
    Agent interactions:

        logos.resolve("world.house") -> LogosNode
        logos.lift("world.house.manifest") -> Agent[Umwelt, Renderable]
        logos.invoke("world.house.manifest", observer) -> Renderable

    CRITICAL: There is no view from nowhere. All operations
    require an observer. `resolve()` without observer context
    raises ObserverRequiredError.
    """

    root: "DataAgent"       # The underlying state store
    registry: "Catalog"     # L-gent registry for lookup
    projector: "Projector"  # Umwelt factory

    # Path → Symbiont cache (lazy hydration)
    _cache: dict[str, "LogosNode"] = field(default_factory=dict)

    def resolve(self, path: str, observer: "Umwelt | None" = None) -> "LogosNode":
        """
        Resolve an AGENTESE path to a LogosNode.

        Resolution strategy:
        1. Check cache (already hydrated)
        2. Check L-gent registry (known entity)
        3. Check spec/ (generative definition—J-gent JIT)
        4. Check void (pure slop?)
        5. Raise PathNotFoundError with sympathetic message

        Args:
            path: AGENTESE path (e.g., "world.house")
            observer: Required for affordance filtering

        Raises:
            PathNotFoundError: With sympathetic error message
        """
        if path in self._cache:
            return self._cache[path]

        # Parse path
        parts = path.split(".")
        if len(parts) < 2:
            raise PathSyntaxError(
                f"Path '{path}' incomplete. "
                f"AGENTESE requires: <context>.<holon>[.<aspect>]"
            )

        context, holon = parts[0], parts[1]

        # Resolve by context
        match context:
            case "world":
                node = self._resolve_world(holon, parts[2:])
            case "self":
                node = self._resolve_self(holon, parts[2:])
            case "concept":
                node = self._resolve_concept(holon, parts[2:])
            case "void":
                node = self._resolve_void(holon, parts[2:])
            case "time":
                node = self._resolve_time(holon, parts[2:])
            case _:
                raise PathNotFoundError(
                    f"Unknown context: '{context}'. "
                    f"Valid contexts: world, self, concept, void, time"
                )

        self._cache[path] = node
        return node

    def lift(self, path: str) -> "Agent[Umwelt, Any]":
        """
        Convert a handle into a composable Agent.

        Verifies Category Laws: Identity and Associativity.
        The returned agent can be composed with >> operator.

        Args:
            path: Full AGENTESE path including aspect

        Returns:
            Composable Agent morphism
        """
        parts = path.split(".")
        if len(parts) < 3:
            raise PathSyntaxError(f"lift() requires aspect: {path}")

        node_path = ".".join(parts[:-1])
        aspect = parts[-1]

        node = self.resolve(node_path)
        return node.lens(aspect)

    async def invoke(
        self,
        path: str,
        observer: "Umwelt",
        **kwargs
    ) -> Any:
        """
        Invoke an AGENTESE path with aspect.

        CRITICAL: Observer is REQUIRED. No view from nowhere.

        Example:
            logos.invoke("world.house.manifest", architect_umwelt)
            logos.invoke("concept.justice.refine", philosopher_umwelt)
        """
        if observer is None:
            raise ObserverRequiredError(
                "AGENTESE requires an observer. There is no view from nowhere."
            )

        parts = path.split(".")
        if len(parts) < 3:
            raise PathSyntaxError(
                f"Path must include aspect: '{path}'. "
                f"Expected: <context>.<holon>.<aspect>"
            )

        node_path = ".".join(parts[:-1])
        aspect = parts[-1]

        node = self.resolve(node_path)

        # Check affordances (Ethical principle)
        available = node.affordances(observer.dna)
        if aspect not in available:
            raise AffordanceError(
                f"Aspect '{aspect}' not available to {observer.dna.name}. "
                f"Your affordances: {available}. "
                f"Consider: What archetype grants '{aspect}'?"
            )

        return await node.invoke(aspect, observer, **kwargs)

    def _resolve_world(self, holon: str, rest: list[str]) -> "LogosNode":
        """Resolve world.* paths."""
        handle = f"world.{holon}"

        # 1. Check L-gent registry
        entry = self.registry.get(handle)
        if entry:
            return self._hydrate(entry)

        # 2. Check spec for generative definition (J-gent JIT)
        spec_path = Path(f"spec/world/{holon}.md")
        if spec_path.exists():
            return self._generate_from_spec(spec_path, handle)

        # 3. Sympathetic error
        raise PathNotFoundError(
            f"'{handle}' not found. "
            f"No implementation in registry, no spec for auto-generation. "
            f"To create: write spec/world/{holon}.md or use world.{holon}.define"
        )

    def _generate_from_spec(self, spec_path: Path, handle: str) -> "LogosNode":
        """
        Generate a Symbiont from a spec file via J-gent JIT.

        The Generative Principle: Specs are compressed wisdom.
        Implementations can be derived mechanically.
        """
        spec_content = spec_path.read_text()

        # Use J-gent to compile ephemeral agent from spec
        from agents.j import MetaArchitect, ArchitectInput

        source = MetaArchitect().invoke(ArchitectInput(
            intent=f"Create LogosNode for {handle}",
            context={"spec": spec_content},
            constraints={
                "max_complexity": 15,
                "allowed_imports": STANDARD_IMPORTS,
            }
        ))

        # Wrap as LogosNode
        return JITLogosNode(
            handle=handle,
            source=source,
            spec=spec_content,
        )
```

---

## Part IV: Observer-Dependent Affordances

The key innovation of AGENTESE is **polymorphic perception**: the same handle yields different affordances depending on who grasps it.

### 4.1 The Affordance Protocol

```python
@dataclass
class AffordanceSet:
    """
    Affordances available to a specific observer.

    The Umwelt Principle: Each agent inhabits its own
    world; there is no view from nowhere.
    """
    handle: str
    observer_archetype: str
    verbs: list[str]      # Available actions
    state: dict[str, Any] # Observable state subset (NOT full state)
    related: list[str]    # Related handles for discovery

@dataclass
class WorldHouse(LogosNode):
    """
    Example: A house in the world.

    Different observers perceive different affordances.
    The projection IS the aesthetic (Principle #4: Joy-Inducing).
    """
    handle: str = "world.house"
    _state_lens: "Lens[Any, HouseState]"  # Symbiont: state via D-gent

    def affordances(self, observer: AgentMeta) -> list[str]:
        """
        Return observer-specific affordances.

        The Polymorphic Principle in action.
        Enforces Principle #3: Ethical (data leakage prevention).
        """
        base = ["manifest", "witness", "affordances"]

        match observer.archetype:
            case "architect":
                return base + ["renovate", "measure", "blueprint", "demolish"]
            case "poet":
                return base + ["describe", "metaphorize", "inhabit"]
            case "economist":
                return base + ["appraise", "forecast", "compare"]
            case "inhabitant":
                return base + ["enter", "exit", "furnish", "repair"]
            case _:
                return base  # Default: observe only

    def lens(self, aspect: str) -> "Agent[Umwelt, Any]":
        """
        Return composable agent for aspect.

        Enables: logos.lift("world.house.manifest") >> logos.lift("concept.summary.refine")
        """
        match aspect:
            case "manifest":
                return ManifestAgent(self)
            case "witness":
                return WitnessAgent(self)
            case _:
                return GenericAspectAgent(self, aspect)

    async def manifest(self, observer: Umwelt) -> Renderable:
        """
        Collapse to observer-appropriate representation.

        The projection IS the aesthetic.
        Principle #4: Joy-Inducing (warmth over coldness).
        """
        state = await self._state_lens.get()

        match observer.dna.archetype:
            case "architect":
                return BlueprintRendering(
                    dimensions=state.dimensions,
                    materials=state.materials,
                    structural_analysis=self._compute_structure(state)
                )
            case "poet":
                return PoeticRendering(
                    description=await self._generate_description(observer, state),
                    metaphors=state.cultural_associations,
                    mood=state.ambient_mood
                )
            case "economist":
                return EconomicRendering(
                    market_value=state.appraisal,
                    comparable_sales=await self._find_comparables(state),
                    appreciation_forecast=self._forecast_value(state)
                )
            case _:
                return BasicRendering(
                    summary=f"A {state.style} house",
                    visible_features=state.exterior_features
                )

    async def invoke(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        """Execute aspect-specific action."""
        match aspect:
            case "manifest":
                return await self.manifest(observer)
            case "witness":
                return await self._get_history(observer)
            case "renovate":
                return await self._renovate(observer, **kwargs)
            case "describe":
                return await self._poetic_description(observer)
            case _:
                raise AffordanceError(f"Unknown aspect: {aspect}")
```

### 4.2 The Aspect Taxonomy

AGENTESE defines standard aspects organized by intent:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE ASPECT TAXONOMY                                │
├──────────────────┬──────────────────────────────────────────────────────────┤
│ PERCEPTION       │ manifest, witness, sense, map                            │
│                  │ • Read-only observation                                  │
│                  │ • Observer determines what is perceived                  │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ MUTATION         │ transform, renovate, evolve, repair                      │
│                  │ • State-changing actions                                 │
│                  │ • Subject to affordance constraints                      │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ COMPOSITION      │ compose, merge, split, relate, lens                      │
│                  │ • Combine or separate entities                           │
│                  │ • Must preserve category laws                            │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ INTROSPECTION    │ affordances, constraints, lineage                        │
│                  │ • Meta-information about the node                        │
│                  │ • Always available to all observers                      │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ GENERATION       │ define, spawn, fork, dream                               │
│                  │ • Create new entities                                    │
│                  │ • Subject to Tasteful principle                          │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ ENTROPY          │ sip, pour, tithe, thank                                  │
│                  │ • Accursed Share operations                              │
│                  │ • Void context only                                      │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

---

## Part V: Generative Collapse & JIT Reification

AGENTESE implements the **Generative Principle** (see `principles.md` §7): If a concept is specified but not implemented, observing it with intent can collapse it into existence.

### 5.1 The Wave Function Metaphor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GENERATIVE COLLAPSE                                 │
│                                                                              │
│    ┌───────────────────┐                                                    │
│    │    POTENTIAL      │  spec/world/library.md exists                      │
│    │   (Superposition) │  No implementation yet                             │
│    └─────────┬─────────┘                                                    │
│              │                                                               │
│              │ Agent invokes: logos.resolve("world.library")                │
│              │                                                               │
│              ▼                                                               │
│    ┌───────────────────┐                                                    │
│    │   OBSERVATION     │  Logos detects spec exists                         │
│    │   (Measurement)   │  J-gent compiles ephemeral Symbiont                │
│    └─────────┬─────────┘                                                    │
│              │                                                               │
│              │ Ephemeral until proven (usage_count > threshold)             │
│              │                                                               │
│              ▼                                                               │
│    ┌───────────────────┐                                                    │
│    │    ACTUALITY      │  world.library is now a living entity             │
│    │    (Collapsed)    │  Registered in L-gent catalog                      │
│    └───────────────────┘                                                    │
│                                                                              │
│    The Curated Principle: If used N times, promote to permanent impl/       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 The JIT Flow

1. User invokes `world.castle.manifest`
2. `Logos` finds no `impl/world/castle.py`
3. `Logos` finds `spec/world/castle.md`
4. `Logos` invokes **J-gent** (Just-In-Time Compiler)
5. **J-gent** reads the Spec, compiles a **Symbiont** (ephemeral agent)
6. The interaction proceeds
7. **Curated Principle**: If used N times, crystallize into permanent code

### 5.3 The Autopoietic Cycle

When agents need concepts that don't exist, AGENTESE enables **autopoiesis**—self-creation:

```python
async def define_concept(
    logos: Logos,
    handle: str,
    observer: Umwelt,
    spec: str
) -> LogosNode:
    """
    Create a new concept in the world.

    The Autopoietic Cycle:
    1. INTENT: Agent needs a concept that doesn't exist
    2. DRAFT: Agent writes a spec
    3. VALIDATE: G-gent validates spec against Tasteful principle
    4. REIFY: J-gent compiles spec into Symbiont
    5. REGISTER: L-gent registers in catalog (Status.DRAFT)
    6. GROUND: If useful (N invocations, >80% success), promote

    Args:
        logos: The Logos resolver
        handle: The AGENTESE path (e.g., "world.library")
        observer: The creating agent's Umwelt
        spec: Markdown specification for the concept

    Returns:
        The newly created LogosNode

    Raises:
        TastefulnessError: If spec fails G-gent validation
        AffordanceError: If observer lacks define affordance
    """
    # 1. Validate intent (affordance check)
    parent_path = handle.rsplit(".", 1)[0]
    parent = logos.resolve(parent_path)
    if "define" not in parent.affordances(observer.dna):
        raise AffordanceError(
            f"{observer.dna.name} cannot define in {parent_path}. "
            f"Your affordances: {parent.affordances(observer.dna)}"
        )

    # 2. Validate spec against Tasteful principle
    from agents.g import Grammarian, GrammarInput

    validation = await Grammarian().invoke(GrammarInput(
        domain="concept.spec",
        content=spec,
        constraints=[
            "Must answer 'why does this need to exist?'",
            "Must have clear input/output types",
            "Must not duplicate existing concepts",
        ]
    ))

    if not validation.valid:
        raise TastefulnessError(
            f"Spec fails Tasteful principle: {validation.reason}. "
            f"Consider: What unique value does this add?"
        )

    # 3. Compile ephemeral Symbiont
    from agents.j import MetaArchitect, ArchitectInput

    source = await MetaArchitect().invoke(ArchitectInput(
        intent=f"Create LogosNode for {handle}",
        context={"spec": spec},
        constraints=DEFAULT_JIT_CONSTRAINTS,
    ))

    node = JITLogosNode(handle=handle, source=source, spec=spec)

    # 4. Register as ephemeral (Status.DRAFT)
    await logos.registry.register(CatalogEntry(
        id=handle,
        entity_type=EntityType.AGENT,
        name=handle.split(".")[-1],
        description=spec[:500],
        status=Status.DRAFT,  # Ephemeral until proven
        forged_by=observer.dna.name,
        forged_from=spec[:200],
    ))

    # 5. Cache and return
    logos._cache[handle] = node
    return node
```

### 5.4 Promotion Protocol

Ephemeral concepts that prove useful can be promoted to permanent:

```python
async def promote_concept(
    logos: Logos,
    handle: str,
    threshold: int = 100,      # Invocations before promotion
    success_threshold: float = 0.8  # Minimum success rate
) -> bool:
    """
    Promote an ephemeral concept to permanent.

    The Curated Principle: Every agent earns its place.
    Utility is the arbiter.
    """
    entry = await logos.registry.get(handle)

    if entry.status != Status.DRAFT:
        return False  # Already promoted or deprecated

    if entry.usage_count < threshold:
        return False  # Not yet proven

    if entry.success_rate < success_threshold:
        return False  # Too unreliable

    # Promote
    entry.status = Status.ACTIVE

    # Generate permanent implementation from JIT source
    node = logos._cache.get(handle)
    if isinstance(node, JITLogosNode):
        # Write to impl/
        impl_path = Path(f"impl/claude/protocols/agentese/contexts/{handle.replace('.', '/')}.py")
        impl_path.parent.mkdir(parents=True, exist_ok=True)
        impl_path.write_text(node.source)

    await logos.registry.update(entry)
    return True
```

---

## Part VI: Composition & Category Laws

**Principle #5 (Composable)** is the hard constraint. AGENTESE handles must be composable agents.

### 6.1 The >> Operator

Because a Handle resolves to an Agent, handles can be piped:

```python
# The Pipeline:
# 1. Fetch the raw document (world)
# 2. Pass to refinement concept (concept)
# 3. Store in internal memory (self)

pipeline = (
    logos.lift("world.document.manifest")
    >> logos.lift("concept.summary.refine")
    >> logos.lift("self.memory.engram")
)

# This satisfies Associativity: (f >> g) >> h == f >> (g >> h)
result = await pipeline.invoke(initial_umwelt)
```

### 6.2 The Composition Protocol

```python
@dataclass
class ComposedPath:
    """
    A composition of AGENTESE paths.

    Category Laws preserved:
    - Identity: Id >> path == path == path >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)

    These laws are VERIFIED at runtime by BootstrapWitness.
    """
    paths: list[str]
    logos: Logos

    async def invoke(self, observer: Umwelt, initial_input: Any = None) -> Any:
        """Execute composition as pipeline."""
        current = initial_input
        for path in self.paths:
            current = await self.logos.invoke(path, observer, input=current)
        return current

    def __rshift__(self, other: "ComposedPath | str") -> "ComposedPath":
        """Compose with another path."""
        if isinstance(other, str):
            return ComposedPath(self.paths + [other], self.logos)
        return ComposedPath(self.paths + other.paths, self.logos)
```

### 6.3 The Minimal Output Principle

**Constraint**: Every AGENTESE aspect must return a **Single Logical Unit**.

| Pattern | Example | Status |
|---------|---------|--------|
| ❌ Array return | `world.users.manifest` → `[User, User, User]` | FORBIDDEN |
| ✅ Iterator/Stream | `world.user.manifest` → `UserIterator` | CORRECT |
| ✅ Single entity | `world.user.manifest` → `User` | CORRECT |

**Why?** Arrays break composition pipelines. Iterators (streams) preserve them.

```python
# BAD: Array return breaks composition
users = await logos.invoke("world.users.manifest", observer)  # [User, User]
# Can't compose with single-entity aspects

# GOOD: Use iterator pattern
user_stream = await logos.invoke("world.users.stream", observer)
async for user in user_stream:
    processed = await logos.invoke("concept.profile.analyze", observer, input=user)
```

---

## Part VII: The Void Context (Accursed Share)

The `void.*` context provides access to the **Accursed Share**—the meta-principle that ensures creative exploration.

### 7.1 The Void Ontology

| Aspect | Meaning | System Action |
|--------|---------|---------------|
| `sip` | Draw entropy | Sample from randomness pool |
| `pour` | Return entropy | Recover unused randomness |
| `tithe` | Pay for order | Noop sacrifice (gratitude) |
| `thank` | Express gratitude | Aesthetic operation |

### 7.2 The Void Implementation

```python
@dataclass
class VoidNode(LogosNode):
    """
    The interface to the Accursed Share.
    Functions as a sink for waste and a source for serendipity.

    The Accursed Share Principle: Everything is slop
    or comes from slop. We cherish and express gratitude.
    """
    handle: str = "void"
    _entropy_pool: "EntropyPool" = field(default_factory=EntropyPool)

    def affordances(self, observer: AgentMeta) -> list[str]:
        # Everyone can interact with the void
        return ["sip", "pour", "tithe", "thank", "witness"]

    async def invoke(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        match aspect:
            case "sip":
                # Principle: Joy-Inducing / Serendipity
                # Returns 'slop'—random tangents, noise, or high-temperature tokens
                # used to break local minima in reasoning loops.
                amount = kwargs.get("amount", 0.1)
                if self._entropy_pool.remaining >= amount:
                    self._entropy_pool.remaining -= amount
                    return RandomnessGrant(
                        amount=amount,
                        seed=self._entropy_pool.sample(),
                        source="accursed_share"
                    )
                raise BudgetExhaustedError(
                    "Accursed Share depleted. "
                    "Consider: void.entropy.pour to return unused randomness."
                )

            case "pour":
                # Return unused randomness (50% recovery)
                grant = kwargs.get("grant")
                recovered = grant.amount * 0.5
                self._entropy_pool.remaining += recovered
                return {"returned": grant.amount, "recovered": recovered}

            case "tithe":
                # Agents must 'pay' for order by sacrificing computation to the void.
                # This is a 'noop' that ensures we aren't optimizing too hard.
                # Principle: Gratitude for waste.
                await asyncio.sleep(0.1)
                return {"gratitude": "The river flows."}

            case "thank":
                # Express gratitude (aesthetic operation, always succeeds)
                return {"gratitude": "Gratitude."}

            case "witness":
                # Show entropy history
                return self._entropy_pool.history
```

### 7.3 The Serendipity Protocol

Agents can request serendipitous discoveries:

```python
# Request serendipitous tangent
tangent = await logos.invoke(
    "void.serendipity.sip",
    observer,
    context="researching authentication",
    confidence_threshold=0.3  # Low confidence = more tangential
)

# tangent might be:
# "Consider: authentication is like a bouncer at a club.
#  What if the bouncer were also a poet?"
```

---

## Part VIII: Temporal Context

The `time.*` context provides temporal operations—looking backward and forward.

### 8.1 Temporal Aspects

| Path | Meaning | Integration |
|------|---------|-------------|
| `time.trace.witness` | Show temporal trace | N-gent narrative log |
| `time.past.project` | View state at timestamp | D-gent temporal lens |
| `time.future.forecast` | Probabilistic forecast | B-gent hypothesis |
| `time.schedule.defer` | Schedule future action | Kairos protocol |
| `time.wait.until` | Block until condition | Async primitives |

### 8.2 Temporal Projection

```python
# View state as it was 1 hour ago
past_house = await logos.invoke(
    "time.past.project",
    observer,
    target="world.house",
    timestamp=one_hour_ago
)

# The house you perceive is the house as it was
# Your Umwelt is temporally shifted
```

---

## Part IX: Integration with Existing Protocols

### 9.1 Umwelt Integration

Every AGENTESE invocation occurs within an Umwelt context:

```python
# The observer's Umwelt determines:
# 1. What affordances are available (via DNA archetype)
# 2. What state is visible (via Lens scope)
# 3. What constraints apply (via Gravity)

result = await logos.invoke(
    "world.house.renovate",
    architect_umwelt,  # Has renovate affordance
    changes={"kitchen": "modern"}
)

# Same path, different observer
result = await logos.invoke(
    "world.house.renovate",
    poet_umwelt,  # AffordanceError: renovate not available
    changes={"kitchen": "modern"}
)
```

### 9.2 Membrane Integration

The Membrane's shape-perception uses AGENTESE paths:

```python
# Membrane commands map to AGENTESE
"kgents observe"   → logos.invoke("world.project.manifest", observer)
"kgents sense"     → logos.invoke("world.project.sense", observer)
"kgents trace X"   → logos.invoke("time.trace.witness", observer, topic=X)
"kgents name X"    → logos.invoke("concept.void.define", observer, spec=X)
"kgents dream"     → logos.invoke("self.memory.consolidate", observer)
```

### 9.3 L-gent Integration

Every LogosNode is registered in the L-gent catalog:

```python
# AGENTESE paths map to L-gent entries
logos.resolve("world.house")
# → L-gent lookup: registry.get("world.house")
# → Returns CatalogEntry with:
#   - input_type, output_type (for lattice compatibility)
#   - relationships (for lineage)
#   - embedding (for semantic search)
#   - usage_count, success_rate (for promotion decisions)
```

### 9.4 G-gent Integration

AGENTESE syntax itself is a G-gent grammar (Level 2: Command):

```python
# G-gent generates the AGENTESE parser
agentese_tongue = await g_gent.reify(
    domain="agentese",
    constraints=[
        "Hierarchical dot-notation",
        "Five contexts: world, self, concept, void, time",
        "Aspects must be registered verbs",
    ],
    level=GrammarLevel.COMMAND
)

# Generated BNF
"""
PATH ::= CONTEXT "." HOLON ("." ASPECT)?
CONTEXT ::= "world" | "self" | "concept" | "void" | "time"
HOLON ::= IDENTIFIER
ASPECT ::= IDENTIFIER
IDENTIFIER ::= [a-z][a-z0-9_]*
"""
```

---

## Part X: Anti-Patterns

1. **The Universal Getter**: Creating a `world.get(id)` function.
   - *Correction*: Use `world.{entity}.manifest`

2. **The Hidden State**: Nodes that store session data internally.
   - *Correction*: Pass state via the `Umwelt` (Observer context) and D-gent Lens

3. **The Silent Failure**: When a path is invalid, returning Null.
   - *Correction*: Transparent Infrastructure demands a **sympathetic error** explaining *why* the path failed (e.g., "The Void refused your tithe" or "Spec not found for auto-generation")

4. **The God-View**: Allowing an interaction without an Observer.
   - *Correction*: `logos.invoke()` without observer raises `ObserverRequiredError`. There is no view from nowhere.

5. **The Array Return**: Returning `[Entity, Entity, ...]` from manifest.
   - *Correction*: Return iterators/streams or single entities. Arrays break composition.

6. **The Kitchen-Sink Context**: Adding a sixth context.
   - *Correction*: Five contexts only. Propose spec change if truly necessary.

---

## Part XI: Success Criteria

An AGENTESE implementation is well-designed if:

- **Liturgical**: Paths read like invocations, not queries
- **Polymorphic**: Same path yields different results for different observers
- **Generative**: Specs can collapse into implementations on demand (J-gent JIT)
- **Composable**: Paths compose with `>>`, preserving category laws
- **Integrated**: Works seamlessly with Umwelt, Membrane, L-gent, G-gent
- **Tasteful**: Affordance constraints prevent inappropriate actions
- **Lightweight**: Lazy hydration—only instantiate what's observed
- **Sympathetic**: Errors explain *why* and suggest *what to do*
- **Stateless**: Nodes are Symbionts (logic only, state via D-gent)

---

## Appendix A: Standard Handles

```
world.*          # External entities
  world.{entity}.manifest       # Perceive entity (polymorphic)
  world.{entity}.witness        # View history (N-gent trace)
  world.{entity}.affordances    # List available verbs
  world.{entity}.define         # Create new entity (autopoiesis)
  world.{entity}.{verb}         # Domain-specific action

self.*           # Agent-internal
  self.memory.manifest          # View current memory
  self.memory.consolidate       # Trigger Hypnagogic cycle
  self.memory.prune             # Garbage collect
  self.capabilities.affordances # What can I do?
  self.state.checkpoint         # Snapshot state

concept.*        # Abstract space
  concept.{name}.manifest       # Perceive concept
  concept.{name}.refine         # Challenge/evolve (dialectic)
  concept.{name}.relate         # Find connections
  concept.{name}.define         # Create concept

void.*           # Accursed Share
  void.entropy.sip              # Draw randomness
  void.entropy.pour             # Return randomness
  void.serendipity.sip          # Request tangent
  void.gratitude.tithe          # Pay for order
  void.gratitude.thank          # Express gratitude

time.*           # Temporal operations
  time.trace.witness            # View temporal trace
  time.past.project             # View past state
  time.future.forecast          # Predict future (B-gent)
  time.schedule.defer           # Schedule action (Kairos)
```

## Appendix B: Files to Create

```
impl/claude/protocols/agentese/
├── __init__.py                  # Package exports
├── logos.py                     # The Logos resolver functor
├── node.py                      # LogosNode protocol + base classes
├── laws.py                      # Runtime verification of Category Laws
├── exceptions.py                # Sympathetic error handling
├── adapter.py                   # Natural language → AGENTESE
└── contexts/
    ├── __init__.py
    ├── world.py                 # External reality handlers
    ├── self_.py                 # Agent introspection (self is reserved)
    ├── concept.py               # Abstract logic gateways
    ├── void.py                  # The Entropy Pool (Accursed Share)
    └── time.py                  # Temporal projection logic

spec/world/                      # World entity specs (generative)
├── README.md                    # How to write world.* specs
└── example.md                   # Example spec for JIT demonstration
```

---

*"The noun is a lie. There is only the rate of change. The world is not a database of static objects—it is a field of potential actions, waiting to be grasped. To get is to invoke. To name is to create. The handle you grasp shapes what you hold."*
