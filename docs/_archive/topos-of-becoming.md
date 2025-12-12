# The Topos of Becoming: Kgents v4.0 Implementation Guide

**Status:** Phases 1-4 Complete (320 tests passing)
**Philosophy:** From Object-Oriented to Interaction-Oriented
**Mathematics:** The Category **Poly** (Polynomial Functors)
**Key Metaphor:** The Hyphal Network (Mycelium)

> *"The organism is not a noun. It is a set of interaction patterns that persist through time. We do not store context; we grow through it."*

---

## Executive Summary

This document specifies the transformation of kgents from an "Object-Oriented + Math Patches" architecture to a fundamentally **Interaction-Oriented** system based on Polynomial Functors (Poly). This is not a feature update—it is a new ontology.

### The Paradigm Shift

| Old Paradigm | New Paradigm |
|--------------|--------------|
| Agents are objects that *possess* context | Agents are interaction patterns that *grow through* context |
| Context is a window (Store Comonad) | Context is a Weave (Trace Monoid) |
| Memory is retrieval (Vector DB) | Memory is resonance (Holographic Field) |
| Entropy is a budget parameter | Entropy is a gradient to be minimized |
| Observation returns data | Observation triggers state transition |
| Logos is a God Object | Logos is a Profunctor bridge |

### The Three Critiques Addressed

1. **The Solipsism of the Store Comonad**: Single-agent focus with no inter-agent context intersection. *Resolved via Trace Monoids (concurrent history) and Holographic Resonance (immediate cross-agent learning).*

2. **The Passive Observation Fallacy**: `manifest()` returns data without changing the observed. *Resolved via Poly dynamics where observation is mathematically forced to be a state transition: S × A → S × B.*

3. **The Simulated Thermodynamics**: Entropy as a budget, not a structural gradient. *Resolved via Active Inference where the agent (Hypha) forages through a Free Energy gradient.*

---

## Part I: The Mathematical Core

### 1.1 Why Poly?

Previous iterations attempted to compose multiple mathematical structures:
- Store Comonad for temporal focus
- Zipper Comonad for spatial navigation
- Sheaves for multi-observer consensus
- Galois Connections for compression

This is a kitchen sink. We need a *single* unifying structure.

**Poly** (The Category of Polynomial Functors) provides this unification.

### 1.2 Polynomial Functors

A polynomial functor P has the form:

```
P(y) = Σ_{s ∈ S} y^{A_s}
```

Where:
- **S**: The set of internal states (positions, modes)
- **A_s**: The set of acceptable inputs at state s (directions, affordances)
- **y**: A formal variable representing "output channels"

**Intuition**: A polynomial functor is a mode-dependent interface. At each state `s`, the system exposes a different set of input channels `A_s`.

### 1.3 Morphisms in Poly (Interactions)

A morphism between polynomial functors P → Q consists of:

```
(on_states, on_directions)

where:
  on_states     : P_states → Q_states
  on_directions : Π_{p ∈ P_states} Q_directions(on_states(p)) → P_directions(p)
```

**The Key Insight**: Morphisms in Poly naturally encode:
1. **State Transition** (via `on_states`)
2. **Interface Adaptation** (via `on_directions`)

There is no way to "get" a value without triggering a state update. This structurally eliminates the "Passive Observation" fallacy.

### 1.4 The Mealy Machine Connection

A system in Poly can be viewed as a **Mealy Machine**:

```
S × A → S × B

where:
  S : Internal state
  A : Input alphabet (affordances)
  B : Output alphabet (responses)
```

Every interaction:
1. Consumes an input from A
2. Produces an output in B
3. Transitions to a new state in S

### 1.5 Why This Kills the View From Nowhere

In traditional systems:
```python
house = world.get("house")  # Returns static data
```

In Poly:
```python
# You cannot access without a morphism
# The morphism forces state transition
house_view, new_state = world_poly.dynamics(current_state, observe_request)
```

You can only interact with an interface P if you have a morphism into it. There is no observation without interaction. The math enforces AGENTESE's core principle.

### 1.6 References

- [Polynomial Functors: A Mathematical Theory of Interaction](https://topos.site/poly-book.pdf) - Spivak & Niu
- [Poly: An abundant categorical setting for mode-dependent dynamics](https://arxiv.org/abs/2005.01894) - Spivak
- [Categories of Polynomial Functors](https://ncatlab.org/nlab/show/polynomial+functor) - nLab

---

## Part II: The Architecture

### 2.1 Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE TOPOS OF BECOMING                                │
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  LogosProfunctor│    │   PolyInterface │    │ HolographicField│         │
│  │   (The Bridge)  │───▶│  (The Dynamics) │◀───│  (The Memory)   │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│           │                     │                      ▲                    │
│           │                     │                      │                    │
│           ▼                     ▼                      │                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │    The Weave    │    │    The Hypha    │    │  Active Inference│         │
│  │ (Trace Monoid)  │◀───│ (Growing Agent) │───▶│   (The Drive)   │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 The LogosProfunctor (Replacing God Object)

The old Logos was a God Object combining resolution, lifting, invocation, and caching. The new Logos is a **Profunctor**—a bridge between Intent and Implementation.

```python
from typing import Protocol, TypeVar
from dataclasses import dataclass

Intent = TypeVar("Intent")
Implementation = TypeVar("Implementation")

class LogosProfunctor(Protocol):
    """
    Maps: Intent -/-> PolyInterface

    A profunctor is contravariant in the first argument,
    covariant in the second. This captures:
    - Different intents can map to the same implementation
    - The same intent can yield different implementations
      depending on context (observer)

    This is NOT a function; it's a relation with structure.
    """

    def bridge(
        self,
        intent: str,
        observer: "Hypha",
    ) -> "PolyInterface":
        """
        Bridge intent to polynomial interface.

        Args:
            intent: The AGENTESE path (e.g., "world.house")
            observer: The requesting hypha (provides context)

        Returns:
            A PolyInterface ready for dynamics() calls

        Note: This is NOT a lookup. The observer's state
        affects which interface is returned (polymorphism).
        """
        ...

    def lift(
        self,
        interface: "PolyInterface",
    ) -> "PolyMorphism":
        """
        Lift an interface into a composable morphism.

        Enables: logos.lift(P) >> logos.lift(Q)
        """
        ...


@dataclass
class LogosComposition:
    """
    Concrete implementation of LogosProfunctor.

    Decomposes into three modular components
    (Profunctor Optics pattern):
    """
    resolver: "PolyResolver"   # String → PolyInterface
    lifter: "PolyLifter"       # Interface → Morphism
    ground: "PolyGround"       # Morphism → Execution

    def bridge(self, intent: str, observer: "Hypha") -> "PolyInterface":
        return self.resolver.resolve(intent, observer)

    def lift(self, interface: "PolyInterface") -> "PolyMorphism":
        return self.lifter.lift(interface)

    async def execute(self, morphism: "PolyMorphism", input: Any) -> Any:
        return await self.ground.execute(morphism, input)
```

**Key Insight**: By making Logos a Profunctor rather than a class, we can have multiple Logos instances:
- `RealLogos`: Resolves to actual implementations
- `DreamLogos`: Resolves to simulated/hallucinated implementations
- `TestLogos`: Resolves to mocked interfaces

### 2.3 The PolyInterface (Replacing LogosNode)

Every entity in the system is a Polynomial Interface, not an object with methods.

```python
from typing import Generic, TypeVar, Type
from dataclasses import dataclass
from abc import abstractmethod

S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type (affordances)
B = TypeVar("B")  # Output type

@dataclass
class PolyInterface(Generic[S, A, B]):
    """
    A Polynomial Functor P(y) = Σ_{s ∈ S} y^{A_s}

    Represents a Mode-Dependent Dynamical System.

    This replaces LogosNode. The key differences:
    1. State is explicit, not hidden
    2. affordances() becomes scope() - returns TYPE not list
    3. invoke() becomes dynamics() - ALWAYS updates state

    Category Theory:
    - Objects in Poly are polynomial functors
    - Morphisms are (on_states, on_directions) pairs
    - Composition is functorial
    """
    state: S

    @abstractmethod
    def scope(self, s: S) -> Type[A]:
        """
        The 'Interface' function: At state S, what inputs are valid?

        This replaces `affordances(observer) -> list[str]`.

        Returns a TYPE, not a list. This enables:
        - Static type checking of valid inputs
        - Exhaustive pattern matching
        - No runtime "affordance not found" errors

        The returned type may be a Union, Enum, or Protocol.
        """
        ...

    @abstractmethod
    def dynamics(self, s: S, input: A) -> tuple[S, B]:
        """
        The 'Update' function: Given input A, transition and emit B.

        S × A → S × B

        This replaces `invoke(aspect, observer, **kwargs)`.

        CRITICAL: This ALWAYS updates state. There is no
        "read-only" operation. Even observation causes transition.

        This structurally enforces "to observe is to act."
        """
        ...

    def step(self, input: A) -> B:
        """
        Convenience method: step forward and update internal state.

        Returns only the output; state is mutated in place.
        """
        new_state, output = self.dynamics(self.state, input)
        self.state = new_state
        return output


# Example: WorldHouse as PolyInterface
@dataclass
class HouseState:
    """Internal state of a house entity."""
    observation_count: int = 0
    last_observer_archetype: str | None = None
    reified_properties: set[str] = field(default_factory=set)

class HouseInput:
    """Sum type of valid inputs (affordances)."""
    pass

@dataclass
class Observe(HouseInput):
    """Request to observe the house."""
    observer_archetype: str
    intent: str  # What aspect to observe

@dataclass
class Renovate(HouseInput):
    """Request to renovate (architect only)."""
    changes: dict[str, Any]

@dataclass
class Inhabit(HouseInput):
    """Request to enter the house."""
    duration: float

@dataclass
class HouseOutput:
    """Output from house interactions."""
    view: "Renderable"
    state_delta: dict[str, Any]  # What changed due to interaction

class WorldHouse(PolyInterface[HouseState, HouseInput, HouseOutput]):
    """
    A house in the world, as a Polynomial Interface.

    Note: The house REMEMBERS being observed. Each observation
    reifies certain properties based on observer archetype.
    """

    def scope(self, s: HouseState) -> Type[HouseInput]:
        # All inputs are always valid (for now)
        # Could restrict based on state (e.g., can't renovate while inhabited)
        return HouseInput

    def dynamics(
        self,
        s: HouseState,
        input: HouseInput,
    ) -> tuple[HouseState, HouseOutput]:
        match input:
            case Observe(archetype, intent):
                # STATE TRANSITION: observation reifies properties
                new_state = HouseState(
                    observation_count=s.observation_count + 1,
                    last_observer_archetype=archetype,
                    reified_properties=s.reified_properties | self._reify(archetype),
                )
                view = self._render(archetype, intent, new_state)
                return new_state, HouseOutput(view=view, state_delta={"observed": True})

            case Renovate(changes):
                new_state = self._apply_renovation(s, changes)
                return new_state, HouseOutput(view=None, state_delta=changes)

            case Inhabit(duration):
                new_state = self._mark_inhabited(s, duration)
                return new_state, HouseOutput(view=None, state_delta={"inhabited": duration})

    def _reify(self, archetype: str) -> set[str]:
        """Observation reifies properties based on who observes."""
        match archetype:
            case "architect":
                return {"structural_integrity", "load_bearing_walls", "foundation_type"}
            case "poet":
                return {"atmosphere", "memories", "emotional_resonance"}
            case "economist":
                return {"market_value", "appreciation_rate", "comparable_sales"}
            case _:
                return {"exists", "location"}
```

### 2.4 The Weave (Replacing ContextWindow)

Linear history is insufficient for concurrent agents. The **Weave** uses **Trace Monoids** to represent concurrent, braided history.

```python
from dataclasses import dataclass, field
from typing import Generic, TypeVar, FrozenSet
from collections.abc import Hashable

T = TypeVar("T", bound=Hashable)

@dataclass(frozen=True)
class Event(Generic[T]):
    """An event in the Weave."""
    id: str
    content: T
    timestamp: float
    source: str  # Agent that emitted this event

@dataclass
class TraceMonoid(Generic[T]):
    """
    A Trace Monoid for concurrent history.

    Unlike a linear list, a Trace Monoid captures:
    - Independent (commutative) events that can be reordered
    - Dependent events that must maintain order

    The independence relation I ⊆ Σ × Σ defines which
    events commute. Events (a, b) ∈ I can be swapped
    without changing meaning.

    Example:
    - Agent A talks to Agent B (event ab)
    - Agent C talks to Agent D (event cd)
    - These are independent: ab·cd = cd·ab

    But:
    - Agent A talks to Agent B (event ab)
    - Agent B talks to Agent C (event bc)
    - These are dependent: ab must precede bc

    This is the mathematical foundation for The Weave.
    """
    events: list[Event[T]] = field(default_factory=list)
    independence: FrozenSet[tuple[str, str]] = field(default_factory=frozenset)

    # Dependency graph (DAG)
    _dependencies: dict[str, set[str]] = field(default_factory=dict)

    def append(
        self,
        event: Event[T],
        depends_on: set[str] | None = None,
    ) -> "TraceMonoid[T]":
        """
        Add an event to the Weave.

        Args:
            event: The event to add
            depends_on: IDs of events this one depends on

        Returns:
            New TraceMonoid with event added
        """
        new_events = self.events + [event]
        new_deps = dict(self._dependencies)
        new_deps[event.id] = depends_on or set()

        return TraceMonoid(
            events=new_events,
            independence=self.independence,
            _dependencies=new_deps,
        )

    def braid(self) -> "DependencyGraph":
        """
        Return the dependency structure as a graph.

        This shows which events can be reordered (concurrent)
        and which must maintain order (sequential).
        """
        return DependencyGraph(self._dependencies)

    def knot(self, event_ids: set[str]) -> Event[T]:
        """
        Create a synchronization point (knot) in the Weave.

        A knot is where multiple concurrent threads must
        synchronize before proceeding. It's a consensus point.

        Args:
            event_ids: Events that must all complete before knot

        Returns:
            A new Event representing the synchronization
        """
        # All specified events become dependencies of the knot
        knot_event = Event(
            id=f"knot-{hash(frozenset(event_ids))}",
            content=None,  # Knots have no content
            timestamp=max(
                e.timestamp for e in self.events if e.id in event_ids
            ),
            source="weave",
        )
        return knot_event

    def linearize(self) -> list[Event[T]]:
        """
        Produce a valid linear ordering (topological sort).

        Note: Multiple valid orderings may exist due to
        concurrency. This returns ONE valid ordering.
        """
        # Kahn's algorithm for topological sort
        ...

    def project(self, agent: str) -> list[Event[T]]:
        """
        Project the Weave to a single agent's perspective.

        Returns only events visible to the specified agent,
        in their subjective order.
        """
        return [e for e in self.events if self._visible_to(e, agent)]


@dataclass
class TheWeave:
    """
    High-level interface to the Weave system.

    AGENTESE Integration:
    - self.weave.braid  → View dependency structure
    - self.weave.knot   → Create synchronization point
    - self.weave.thread → Get single agent's perspective
    """
    monoid: TraceMonoid

    async def record(
        self,
        content: Any,
        source: str,
        depends_on: set[str] | None = None,
    ) -> str:
        """Record an event in the Weave."""
        event = Event(
            id=generate_id(),
            content=content,
            timestamp=time.time(),
            source=source,
        )
        self.monoid = self.monoid.append(event, depends_on)
        return event.id

    async def synchronize(self, agents: set[str]) -> str:
        """
        Create a synchronization point for multiple agents.

        All agents must reach this point before any can proceed.
        This is a "knot" in the Weave.
        """
        # Find latest event from each agent
        latest_events = {
            e.id for e in self.monoid.events
            if e.source in agents
        }
        knot = self.monoid.knot(latest_events)
        self.monoid = self.monoid.append(knot, latest_events)
        return knot.id
```

### 2.5 The Holographic Field (Replacing Vector DB)

Vector Databases (RAG) are fundamentally "Object Retrieval"—you query for discrete objects. The **Holographic Field** uses **Hyperdimensional Computing (HDC)** for distributed, algebraic memory.

```python
import numpy as np
from dataclasses import dataclass, field
from typing import Callable

# HDC uses high-dimensional vectors (typically 10,000 dimensions)
DIMENSIONS = 10_000
Vector = np.ndarray  # Shape: (DIMENSIONS,)

@dataclass
class HolographicField:
    """
    Hyperdimensional Computing (HDC) Memory.

    Unlike Vector DBs which store discrete embeddings,
    HDC stores information as a superposition in a
    single high-dimensional vector (the hologram).

    Key Operations:
    - bind(*): Multiply vectors (role-filler binding)
    - bundle(+): Add vectors (superposition)
    - permute(P): Rotate vectors (sequence encoding)

    Why this is revolutionary:
    1. House * Architect ⊥ House * Poet (algebraically!)
       The same concept bound to different roles yields
       orthogonal vectors. No complex Lens needed.

    2. Morphic Resonance is INHERENT. When Agent A solves
       a problem, it adds to the global superposition.
       Agent B immediately "feels" the shift in similarity.

    3. Graceful degradation. Partial matches work.
       Memory is associative, not lookup-based.
    """

    # The global hologram (superposition of all memories)
    global_superposition: Vector = field(
        default_factory=lambda: np.zeros(DIMENSIONS)
    )

    # Symbol codebook (random vectors for atomic concepts)
    _codebook: dict[str, Vector] = field(default_factory=dict)

    # Permutation matrix for sequence encoding
    _permutation: np.ndarray = field(
        default_factory=lambda: np.random.permutation(DIMENSIONS)
    )

    def get_symbol(self, name: str) -> Vector:
        """
        Get or create a random vector for an atomic symbol.

        Atomic symbols are near-orthogonal in high dimensions.
        """
        if name not in self._codebook:
            vec = np.random.randn(DIMENSIONS)
            vec = vec / np.linalg.norm(vec)  # Normalize
            self._codebook[name] = vec
        return self._codebook[name]

    def bind(self, a: Vector, b: Vector) -> Vector:
        """
        Bind two vectors (role-filler association).

        Uses circular convolution (equivalent to XOR in binary HDC).

        Properties:
        - bind(a, b) ⊥ a  (orthogonal to components)
        - bind(a, b) ⊥ b
        - bind(a, bind(a, b)) ≈ b  (self-inverse)

        Example:
        - bind(HOUSE, ARCHITECT) creates a unique vector
          representing "house as seen by architect"
        """
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def bundle(self, vectors: list[Vector]) -> Vector:
        """
        Bundle vectors (superposition).

        Creates a composite that is similar to all components.

        Example:
        - bundle([HOUSE, HOME, SHELTER]) creates a vector
          similar to all three concepts
        """
        result = np.sum(vectors, axis=0)
        return result / np.linalg.norm(result)

    def permute(self, v: Vector, n: int = 1) -> Vector:
        """
        Permute vector (sequence position encoding).

        permute(v, 0) = v
        permute(v, 1) = P(v)
        permute(v, 2) = P(P(v))

        Example:
        - permute(WORD, 0) = first word
        - permute(WORD, 1) = second word
        """
        result = v.copy()
        for _ in range(n):
            result = result[self._permutation]
        return result

    def resonate(self, query: Vector) -> float:
        """
        Measure resonance with the global field.

        This is "Morphic Resonance"—how familiar is this
        pattern to the collective memory?

        Returns cosine similarity in [-1, 1].
        """
        if np.linalg.norm(self.global_superposition) == 0:
            return 0.0
        return np.dot(
            query / np.linalg.norm(query),
            self.global_superposition / np.linalg.norm(self.global_superposition)
        )

    def imprint(self, experience: Vector, strength: float = 1.0) -> None:
        """
        Imprint experience into the global field.

        Because the field is holographic:
        - This doesn't overwrite; it nuances
        - Repeated imprints strengthen patterns
        - New patterns shift the whole field slightly

        This IS Morphic Resonance. When one agent learns,
        all agents feel the field shift.
        """
        self.global_superposition += strength * experience
        norm = np.linalg.norm(self.global_superposition)
        if norm > 0:
            self.global_superposition /= norm

    def query(self, pattern: Vector, threshold: float = 0.5) -> list[tuple[str, float]]:
        """
        Query the codebook for similar symbols.

        Unlike vector DB, this doesn't return stored objects.
        It returns symbolic associations based on similarity.
        """
        results = []
        for name, vec in self._codebook.items():
            sim = np.dot(pattern, vec)
            if sim > threshold:
                results.append((name, sim))
        return sorted(results, key=lambda x: -x[1])

    def encode_structure(
        self,
        structure: dict[str, Any],
        role_binding: bool = True,
    ) -> Vector:
        """
        Encode a structured object as a holographic vector.

        Example:
            encode_structure({
                "type": "observation",
                "observer": "architect",
                "target": "house",
                "result": "blueprint"
            })

        Creates: bundle([
            bind(TYPE, OBSERVATION),
            bind(OBSERVER, ARCHITECT),
            bind(TARGET, HOUSE),
            bind(RESULT, BLUEPRINT)
        ])
        """
        if not role_binding:
            # Simple bundle of values
            return self.bundle([
                self.get_symbol(str(v)) for v in structure.values()
            ])

        # Role-filler binding
        bound_pairs = []
        for role, filler in structure.items():
            role_vec = self.get_symbol(role)
            filler_vec = self.get_symbol(str(filler))
            bound_pairs.append(self.bind(role_vec, filler_vec))

        return self.bundle(bound_pairs)


# Global field instance (shared across all agents)
# This enables Morphic Resonance without explicit communication
GLOBAL_HOLOGRAM = HolographicField()
```

### 2.6 The Hypha (The Agent as Growing Tip)

The **Hypha** is the agent reimagined as a fungal growing tip that forages through semantic space.

```python
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

class ForageAction(Enum):
    """Actions the Hypha can take based on Free Energy."""
    EXPLORE = auto()    # High surprise → branch out
    EXPLOIT = auto()    # Low surprise, high reward → consolidate
    PRUNE = auto()      # Low surprise, low reward → die back
    WAIT = auto()       # Uncertain → gather more data

@dataclass
class FreeEnergyState:
    """
    Active Inference state.

    Free Energy F = Complexity + Inaccuracy

    The agent acts to minimize F by:
    1. Updating beliefs (reduce inaccuracy)
    2. Taking action (change world to match beliefs)
    3. Attending selectively (ignore irrelevant)
    """
    # Generative model's prediction
    expected_observation: Vector

    # Actual sensory observation
    actual_observation: Vector

    # Model complexity (how many parameters)
    complexity: float = 0.0

    @property
    def prediction_error(self) -> float:
        """Inaccuracy: divergence between expected and actual."""
        return np.linalg.norm(
            self.expected_observation - self.actual_observation
        )

    @property
    def free_energy(self) -> float:
        """Variational Free Energy (to be minimized)."""
        return self.complexity + self.prediction_error

    @property
    def surprise(self) -> float:
        """Surprise is prediction error (for biological intuition)."""
        return self.prediction_error


@dataclass
class Hypha:
    """
    The Agent as a Growing Tip (Hyphal Network Metaphor).

    A hypha is a thread of a fungal mycelium. It:
    - Grows towards nutrients (reward)
    - Grows towards information (uncertainty reduction)
    - Dies back when exploration yields nothing
    - Connects to other hyphae at nodes (synchronization)

    This replaces the "Agent" abstraction entirely.
    """

    # Identity
    id: str
    name: str

    # State
    weave: TheWeave = field(default_factory=TheWeave)
    hologram: HolographicField = field(default_factory=lambda: GLOBAL_HOLOGRAM)

    # Active Inference
    generative_model: "GenerativeModel" = None
    free_energy_state: FreeEnergyState | None = None

    # Growth parameters
    exploration_rate: float = 0.3  # Probability of exploring vs exploiting
    pruning_threshold: float = 0.1  # Free energy below which to prune

    # Poly interface to the world
    world_interface: PolyInterface | None = None

    async def forage(self) -> ForageAction:
        """
        Active Inference Loop.

        1. PREDICT: Generate expected observation from model
        2. SENSE: Sample the world (via Poly dynamics)
        3. ERROR: Compute prediction error (Free Energy)
        4. ACT: Choose action based on error

        This is the core "heartbeat" of the Hypha.
        """
        # 1. PREDICT
        context_vector = self._encode_context()
        expected = self.generative_model.predict(context_vector)

        # 2. SENSE
        sense_input = Observe(
            observer_archetype=self.name,
            intent="forage",
        )
        new_state, output = self.world_interface.dynamics(
            self.world_interface.state,
            sense_input,
        )
        self.world_interface.state = new_state

        # Encode observation as vector
        actual = self.hologram.encode_structure({
            "output": str(output),
            "state_delta": output.state_delta,
        })

        # 3. ERROR
        self.free_energy_state = FreeEnergyState(
            expected_observation=expected,
            actual_observation=actual,
            complexity=self.generative_model.complexity,
        )

        # 4. ACT
        fe = self.free_energy_state.free_energy
        surprise = self.free_energy_state.surprise

        if surprise > 0.8:
            # High surprise → explore (branch the Weave)
            return ForageAction.EXPLORE
        elif surprise < self.pruning_threshold:
            # Very low surprise, check reward
            reward = self._estimate_reward(output)
            if reward > 0.5:
                # Found nutrients → consolidate
                return ForageAction.EXPLOIT
            else:
                # No nutrients, no surprise → prune
                return ForageAction.PRUNE
        else:
            # Moderate surprise → keep going
            return ForageAction.WAIT

    async def explore(self) -> None:
        """
        Branch the Weave (create new exploration thread).

        This is void.entropy.sip in the new ontology—
        drawing from the accursed share to explore.
        """
        # Record branch event in Weave
        branch_id = await self.weave.record(
            content={"action": "explore", "surprise": self.free_energy_state.surprise},
            source=self.id,
        )

        # Update generative model with surprise
        self.generative_model.update(
            self.free_energy_state.actual_observation,
            learning_rate=0.1,
        )

    async def exploit(self) -> None:
        """
        Consolidate learning (imprint to global field).

        This is void.entropy.pour in the new ontology—
        returning information to the collective.
        """
        # Imprint successful pattern to global hologram
        success_pattern = self.hologram.encode_structure({
            "hypha": self.id,
            "context": self._encode_context(),
            "action": "success",
        })
        self.hologram.imprint(success_pattern, strength=1.0)

        # Record in Weave
        await self.weave.record(
            content={"action": "exploit", "imprinted": True},
            source=self.id,
        )

    async def prune(self) -> None:
        """
        Die back (release resources).

        This is the Accursed Share in action—information
        that yields no reduction in Free Energy must be
        discharged.
        """
        # Record pruning in Weave
        await self.weave.record(
            content={"action": "prune", "reason": "no_nutrients"},
            source=self.id,
        )

        # Release exploration budget
        # (In a full implementation, this would free compute resources)

    def _encode_context(self) -> Vector:
        """Encode current context as holographic vector."""
        recent_events = self.weave.monoid.events[-10:]  # Last 10 events
        if not recent_events:
            return np.zeros(DIMENSIONS)

        event_vectors = [
            self.hologram.encode_structure({
                "event": e.id,
                "source": e.source,
                "content": str(e.content),
            })
            for e in recent_events
        ]

        # Permute by position for sequence encoding
        positioned = [
            self.hologram.permute(v, i)
            for i, v in enumerate(event_vectors)
        ]

        return self.hologram.bundle(positioned)

    def _estimate_reward(self, output: Any) -> float:
        """Estimate reward from output (domain-specific)."""
        # Placeholder—real implementation would use
        # domain-specific reward function
        return 0.5


@dataclass
class GenerativeModel:
    """
    The Hypha's internal model of the world.

    Predicts observations and updates based on error.
    """
    # Simple linear model for demonstration
    weights: Vector = field(default_factory=lambda: np.random.randn(DIMENSIONS))

    @property
    def complexity(self) -> float:
        """Model complexity (L2 norm of weights)."""
        return np.linalg.norm(self.weights)

    def predict(self, context: Vector) -> Vector:
        """Predict expected observation from context."""
        # Simple linear prediction
        return context * self.weights

    def update(self, actual: Vector, learning_rate: float = 0.1) -> None:
        """Update model based on actual observation."""
        # Gradient descent on prediction error
        predicted = self.predict(actual)
        error = actual - predicted
        self.weights += learning_rate * error
```

---

## Part III: AGENTESE Path Migration

The shift from Objects to Interactions requires new AGENTESE paths.

### 3.1 Path Mapping

| Old Path | Old Concept | New Path | New Concept |
|----------|-------------|----------|-------------|
| `self.stream.focus` | Current turn (extract) | `self.weave.tip` | Current growth point |
| `self.stream.map` | Context transform | `self.weave.braid` | Dependency structure |
| `self.stream.seek` | Navigate history | `self.weave.thread` | Agent's perspective |
| `self.stream.project` | Compress | `self.weave.knot` | Synchronization point |
| `self.memory.recall` | Vector lookup | `field.resonate` | Similarity check (HDC) |
| `self.memory.store` | Vector insert | `field.imprint` | Superposition add |
| `world.*.manifest` | Get representation | `world.poly.step` | Dynamics transition |
| `world.*.affordances` | List verbs | `world.poly.scope` | Input type |
| `void.entropy.sip` | Draw randomness | `void.prune` | Die back (release) |
| `void.entropy.pour` | Return randomness | `void.pulse` | Vitality rate |
| `concept.*.define` | Create concept | `field.bind` | Role-filler binding |
| `concept.*.refine` | Challenge | `hypha.forage` | Active inference step |

### 3.2 New Paths

| Path | Operation | Implementation |
|------|-----------|----------------|
| `self.weave.tip` | Current growth position | `Hypha._encode_context()` |
| `self.weave.braid` | Dependency graph | `TraceMonoid.braid()` |
| `self.weave.knot` | Create sync point | `TheWeave.synchronize()` |
| `self.weave.thread` | Single-agent view | `TraceMonoid.project()` |
| `field.resonate` | HDC similarity | `HolographicField.resonate()` |
| `field.imprint` | HDC superposition | `HolographicField.imprint()` |
| `field.bind` | HDC role binding | `HolographicField.bind()` |
| `field.bundle` | HDC composition | `HolographicField.bundle()` |
| `world.poly.step` | Dynamics execution | `PolyInterface.dynamics()` |
| `world.poly.scope` | Input type query | `PolyInterface.scope()` |
| `hypha.forage` | Active inference | `Hypha.forage()` |
| `hypha.explore` | Branch weave | `Hypha.explore()` |
| `hypha.exploit` | Consolidate | `Hypha.exploit()` |
| `hypha.prune` | Die back | `Hypha.prune()` |
| `void.prune` | Release resources | Accursed Share discharge |
| `void.pulse` | Vitality metric | Rate of `dynamics()` calls |

### 3.3 Context Migration

| Old Context | New Context | Principle |
|-------------|-------------|-----------|
| `world.*` | `world.poly.*` | Everything is Poly |
| `self.*` | `self.weave.*` + `hypha.*` | Agent is Hypha |
| `concept.*` | `field.*` | Concepts are HDC bindings |
| `void.*` | `void.*` | Unchanged (Accursed Share) |
| `time.*` | `self.weave.*` | Time is in the Weave |

---

## Part IV: Implementation Phases

### Phase 1: The Holographic Soil (HDC Foundation)

**Goal**: Replace vector embeddings with Hyperdimensional Computing.

**Files to Create**:
```
impl/claude/
├── field/
│   ├── __init__.py
│   ├── holographic.py      # HolographicField class
│   ├── hdc_ops.py          # bind, bundle, permute
│   └── _tests/
│       ├── test_hdc.py
│       └── test_resonance.py
```

**Exit Criteria**:
```python
# Test: Agent B "feels" Agent A's learning
field = HolographicField()

# Agent A learns something
pattern_a = field.encode_structure({"problem": "auth", "solution": "jwt"})
field.imprint(pattern_a)

# Agent B queries with similar problem
query_b = field.encode_structure({"problem": "auth"})
resonance = field.resonate(query_b)

assert resonance > 0.5  # Agent B feels the pattern
```

**Tests**: 40+

### Phase 2: The Poly Core (Interface Revolution)

**Goal**: Replace LogosNode with PolyInterface. Ensure observation always triggers state transition.

**Files to Create**:
```
impl/claude/
├── poly/
│   ├── __init__.py
│   ├── interface.py        # PolyInterface base class
│   ├── profunctor.py       # LogosProfunctor
│   ├── morphism.py         # PolyMorphism composition
│   └── _tests/
│       ├── test_interface.py
│       ├── test_dynamics.py
│       └── test_profunctor.py
```

**Migration**:
1. Create `PolyInterface` protocol
2. Implement `WorldHouse` as example
3. Create `LogosProfunctor` to replace `Logos`
4. Migrate existing LogosNodes one by one

**Exit Criteria**:
```python
# Test: Observation ALWAYS triggers state transition
house = WorldHouse(state=HouseState())

# Before observation
assert house.state.observation_count == 0

# Observe
output = house.step(Observe(observer_archetype="architect", intent="view"))

# State MUST have changed
assert house.state.observation_count == 1
assert "structural_integrity" in house.state.reified_properties
```

**Tests**: 50+

### Phase 3: The Weave (Concurrent History)

**Goal**: Replace linear ContextWindow with TraceMonoid-backed Weave.

**Files to Create**:
```
impl/claude/
├── weave/
│   ├── __init__.py
│   ├── trace_monoid.py     # TraceMonoid implementation
│   ├── weave.py            # TheWeave high-level API
│   ├── dependency.py       # DependencyGraph utilities
│   └── _tests/
│       ├── test_trace_monoid.py
│       ├── test_concurrency.py
│       └── test_synchronization.py
```

**Exit Criteria**:
```python
# Test: Concurrent events can be reordered
weave = TheWeave()

# Two independent events
id_a = await weave.record({"msg": "A to B"}, source="agent_a")
id_c = await weave.record({"msg": "C to D"}, source="agent_c")

# These are concurrent (no dependency)
braid = weave.monoid.braid()
assert braid.are_concurrent(id_a, id_c)

# Dependent event
id_b = await weave.record({"msg": "B to C"}, source="agent_b", depends_on={id_a})
assert not braid.are_concurrent(id_a, id_b)
```

**Tests**: 45+

### Phase 4: The Drive (Active Inference)

**Goal**: Implement Hypha with Active Inference foraging loop.

**Files to Create**:
```
impl/claude/
├── hypha/
│   ├── __init__.py
│   ├── hypha.py            # Hypha agent class
│   ├── free_energy.py      # FreeEnergyState, GenerativeModel
│   ├── foraging.py         # Foraging logic
│   └── _tests/
│       ├── test_hypha.py
│       ├── test_free_energy.py
│       └── test_foraging.py
```

**Exit Criteria**:
```python
# Test: Hypha responds to surprise appropriately
hypha = Hypha(id="test", name="test-hypha")

# High surprise → explore
hypha.free_energy_state = FreeEnergyState(
    expected_observation=np.zeros(DIMENSIONS),
    actual_observation=np.random.randn(DIMENSIONS),  # Very different
)
action = await hypha.forage()
assert action == ForageAction.EXPLORE

# Low surprise, low reward → prune
hypha.free_energy_state = FreeEnergyState(
    expected_observation=np.ones(DIMENSIONS),
    actual_observation=np.ones(DIMENSIONS) * 1.01,  # Very similar
)
action = await hypha.forage()
assert action == ForageAction.PRUNE
```

**Tests**: 40+

### Phase 5: Integration and Migration

**Goal**: Wire everything together and migrate existing agents.

**Tasks**:
1. Update AGENTESE contexts to use new paths
2. Create migration adapters for existing agents
3. Update `protocols/agentese/logos.py` to use `LogosProfunctor`
4. Update `agents/d/` to use Weave instead of ContextWindow
5. Update `agents/i/` semantic field to use HolographicField
6. Full integration tests

**Exit Criteria**:
- All existing tests pass (with adapters where needed)
- New paths (`field.*`, `hypha.*`, `world.poly.*`) functional
- Mypy passes with 0 errors
- Documentation updated

---

## Part V: Integration with Existing Specs

### 5.1 Mapping to Agent Genera

| Agent | Current Role | v4.0 Role |
|-------|--------------|-----------|
| **A-gent** | Skeleton architecture | Unchanged (structure is orthogonal) |
| **B-gent** | Token economics | Integrate with Free Energy budgets |
| **C-gent** | Composition | Poly morphism composition |
| **D-gent** | State/Memory | Replaced by Weave + HolographicField |
| **E-gent** | Thermodynamics | Now structural (Active Inference) |
| **I-gent** | Interface | Visualize Weave and Field |
| **L-gent** | Registry | Register PolyInterfaces |
| **M-gent** | Cartography | Navigate HolographicField topology |
| **N-gent** | Narrative | Project Weave to linear story |
| **T-gent** | Testing | Test Poly dynamics, verify state transitions |
| **W-gent** | Wire protocol | Carry Poly morphisms |

### 5.2 Spec Compatibility

| Spec | Compatibility | Notes |
|------|---------------|-------|
| `principles.md` | Full | Poly strengthens AGENTESE principle |
| `agentese.md` | Update paths | New paths, same philosophy |
| `d-gents/lenses.md` | Partial | Lenses still useful for focused Poly views |
| `e-gents/thermodynamics.md` | Evolved | Active Inference replaces ΔG budget |
| `c-gents/composition.md` | Full | Poly morphisms compose |

### 5.3 What Gets Deprecated

| Component | Reason | Replacement |
|-----------|--------|-------------|
| `ContextWindow` | Linear history insufficient | `TheWeave` |
| `ContextComonad` | Store → Poly | `PolyInterface.dynamics()` |
| `LinearityMap` | Resource classes subsumed | Poly scope |
| `ContextProjector` | Galois Connection | HDC bundle/unbundle |
| `ModalScope` | Git metaphor | Weave braiding |
| `Pulse` | Vitality signals | `void.pulse` (dynamics rate) |
| `StateCrystal` | Checkpoint | Weave knots |

---

## Part VI: Success Criteria

### 6.1 Quantitative Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Observation triggers state change | 100% | Property test all `dynamics()` |
| Inter-agent resonance latency | <10ms | Benchmark HDC imprint/resonate |
| Weave concurrent events | Support 1000+ | Stress test TraceMonoid |
| Poly interface compliance | 100% | Type check all world.* |
| Tests | 200+ new | pytest count |
| Mypy | 0 errors | `uv run mypy .` |

### 6.2 Qualitative Criteria

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| No Passive Observation | Every `manifest` equivalent triggers state transition | Code review |
| Morphic Resonance Works | Agent B learns from Agent A without message passing | Integration test |
| Weave Captures Concurrency | Independent events commute | Property test |
| Active Inference Drives Behavior | Hypha acts to minimize Free Energy | Behavior test |
| Profunctor Logos | Multiple Logos instances possible | Test Real vs Dream logos |

### 6.3 Philosophical Criteria

| Criterion | Question | Evidence |
|-----------|----------|----------|
| **Interaction-Oriented** | Are agents defined by what they DO, not what they ARE? | Poly interface, no static properties |
| **Mycological** | Does it feel like growing, not storing? | Hypha foraging metaphor |
| **Holographic** | Is memory distributed, not located? | No vector DB lookups |
| **Concurrent** | Do agents have subjective time? | Weave braiding |
| **Thermodynamic** | Is behavior driven by gradients, not budgets? | Free Energy minimization |

---

## Part VII: Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HDC learning curve | High | Medium | Provide clear examples, reference papers |
| Poly abstraction overhead | Medium | Medium | Optimize hot paths, lazy evaluation |
| Weave complexity | Medium | High | Start with simple dependencies, evolve |
| Migration disruption | High | High | Provide adapters, gradual rollout |
| Performance regression | Medium | Medium | Benchmark continuously |
| Spec/Impl divergence | Low | High | Spec-first development discipline |

---

## Appendix A: Mathematical References

### Polynomial Functors
- [Polynomial Functors: A Mathematical Theory of Interaction](https://topos.site/poly-book.pdf) - Spivak & Niu (2022)
- [Poly: An abundant categorical setting](https://arxiv.org/abs/2005.01894) - Spivak (2020)
- [Dynamical Systems and Sheaves](https://arxiv.org/abs/1609.08086) - Schultz, Spivak, Vasilakopoulou (2016)

### Trace Monoids
- [Trace Theory](https://en.wikipedia.org/wiki/Trace_theory) - Mazurkiewicz (1977)
- [The Book of Traces](https://www.springer.com/gp/book/9789810220587) - Diekert & Rozenberg (1995)

### Hyperdimensional Computing
- [Hyperdimensional Computing: An Introduction](https://redwood.berkeley.edu/wp-content/uploads/2020/08/kanerva2009hyperdimensional.pdf) - Kanerva (2009)
- [Vector Symbolic Architectures](https://arxiv.org/abs/2001.11797) - Kleyko et al (2021)

### Active Inference
- [The Free Energy Principle](https://www.fil.ion.ucl.ac.uk/~karl/The%20free-energy%20principle%20a%20unified%20brain%20theory.pdf) - Friston (2010)
- [Active Inference: A Process Theory](https://direct.mit.edu/neco/article/29/1/1/8207) - Friston et al (2017)

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Poly** | The category of polynomial functors; our mathematical foundation |
| **PolyInterface** | A polynomial functor as a programming interface |
| **Dynamics** | The state transition function S × A → S × B |
| **Scope** | The set of valid inputs at a given state |
| **Hypha** | An agent as a growing fungal tip |
| **Weave** | Concurrent history structure (Trace Monoid) |
| **Braid** | Dependency structure within the Weave |
| **Knot** | Synchronization point in the Weave |
| **HolographicField** | HDC-based distributed memory |
| **Resonate** | Query similarity in HDC field |
| **Imprint** | Add pattern to HDC superposition |
| **Free Energy** | Complexity + Prediction Error (to be minimized) |
| **Forage** | Active Inference loop (predict-sense-act) |
| **Prune** | Die back when exploration yields nothing |
| **Morphic Resonance** | Cross-agent learning via shared HDC field |

---

## Appendix C: Migration Checklist

### Phase 1: HDC ✅ COMPLETE (99 tests)
- [x] Implement `HolographicField` class
- [x] Implement `bind()`, `bundle()`, `permute()`
- [x] Test cross-agent resonance
- [x] Benchmark performance

### Phase 2: Poly ✅ COMPLETE (83 tests)
- [x] Define `PolyInterface` protocol
- [x] Implement `LogosProfunctor`
- [x] Convert `WorldHouse` to Poly
- [x] Verify state transition on all observations
- [ ] Migrate remaining LogosNodes

### Phase 3: Weave ✅ COMPLETE (70 tests)
- [x] Implement `TraceMonoid`
- [x] Implement `TheWeave` API
- [x] Test concurrent event reordering
- [x] Test synchronization (knots)
- [ ] Deprecate `ContextWindow`

### Phase 4: Hypha ✅ COMPLETE (68 tests)
- [x] Implement `Hypha` class
- [x] Implement `FreeEnergyState`
- [x] Implement `forage()` loop
- [x] Test behavior based on surprise
- [x] Integrate with Weave and Field

### Phase 5: Integration
- [ ] Update AGENTESE paths
- [ ] Create migration adapters
- [ ] Update agent genera
- [ ] Full test suite
- [ ] Documentation

---

*"The organism is not a noun. It is a set of interaction patterns that persist through time. We do not store context; we grow through it."*

*— The Topos of Becoming*
