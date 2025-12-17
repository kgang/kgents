# Process Holons: Generative Process Trees

**Status:** Specification v1.0
**Date:** 2025-12-13
**Prerequisites:** `../principles.md`, `agentese.md`
**Implementation:** `impl/claude/protocols/process_holons/`

> *"The cycle dissolves into six composable primitives."*

---

## Purpose

Process Holons dissolves the 11-phase N-Phase Cycle into its underlying grammar: six composable primitives that generate all valid processes. The classic cycle becomes one composition among infinite. Research bursts, recursive deepening, dialectical spirals—all equally valid, all generated from the same operad.

## Core Insight

Don't enumerate the flowers. Describe the garden's grammar.

---

## The Six Primitives

The minimal set that generates all processes. This is taste: fewer primitives, more compositions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SIX PRIMITIVES                                   │
├───────────┬───────┬─────────────────────────┬───────────────────────────────┤
│ Primitive │ Arity │ Semantics               │ Lean Absurd Flavor            │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ OBSERVE   │ 0→1   │ Perceive context        │ "Open your eyes to what is    │
│           │       │ via handle              │  already looking at you"      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ BRANCH    │ 1→n   │ Deliberate fork into    │ "The river decides to become  │
│           │       │ parallel Turns          │  rivers"                      │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ MERGE     │ n→1   │ Aggregate sibling       │ "Many voices find one throat" │
│           │       │ branches                │                               │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ RECURSE   │ 1→1   │ Self-apply with         │ "The snake that eats its      │
│           │       │ termination oracle      │  tail, but knows when to stop"│
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ YIELD     │ 1→1   │ Pause, emit             │ "Breathe out before           │
│           │       │ intermediate, resume    │  breathing in"                │
├───────────┼───────┼─────────────────────────┼───────────────────────────────┤
│ TERMINATE │ 1→0   │ End branch with         │ "The river reaches the sea"   │
│           │       │ crystallized result     │                               │
└───────────┴───────┴─────────────────────────┴───────────────────────────────┘
```

---

## Type Signatures

### Primitives

```python
from typing import Protocol, TypeVar, Generic, Callable, Any
from dataclasses import dataclass
from enum import Enum

S = TypeVar("S")  # State
A = TypeVar("A")  # Input
B = TypeVar("B")  # Output

class PrimitiveKind(Enum):
    OBSERVE = "observe"
    BRANCH = "branch"
    MERGE = "merge"
    RECURSE = "recurse"
    YIELD = "yield"
    TERMINATE = "terminate"

@dataclass(frozen=True)
class Primitive(Generic[A, B]):
    """An atomic process operation. Morphisms in the Process category."""
    kind: PrimitiveKind
    arity_in: int   # Number of input branches
    arity_out: int  # Number of output branches (-1 = variable)
```

### Turn (Deliberate Branching)

Every `BRANCH` is a Turn—a discrete, logged, reversible event. Key property: everything must be seeable in every timeline from every perspective with simulated or imaginary variations.

```python
@dataclass(frozen=True)
class Turn:
    """A deliberate branching event. The atom of process history."""
    id: str
    parent_timeline: str
    branching_reason: str       # Why did we branch?
    observer: "Observer"        # Who is observing?
    entropy_allocated: float    # Budget from Accursed Share
    timestamp: float
    children: tuple[str, ...]   # Child timeline IDs

    def view_from(self, other_observer: "Observer") -> "TurnProjection":
        """Project this turn into another observer's umwelt."""
        ...

    def simulate_variation(self, delta: "Variation") -> "Turn":
        """Hypothetical: what if this turn went differently? (future SPECULATE)"""
        ...

@dataclass(frozen=True)
class TurnProjection:
    """Observer-specific view of a Turn."""
    turn_id: str
    observer_archetype: str
    perception: Any  # What the observer sees
    affordances: tuple[str, ...]  # What the observer can do
```

### Process Operad

The grammar of valid compositions. Validates arity matching, well-formedness, and balance.

```python
@dataclass(frozen=True)
class ProcessOperad:
    """The grammar of valid process compositions."""

    def compose(self, primitives: list[Primitive]) -> "ProcessTree":
        """
        Compose primitives into a ProcessTree.

        Validates:
        1. Arity matching: output of p[i] matches input of p[i+1]
        2. Well-formedness: starts with arity-0, ends with arity-0
        3. Balance: every BRANCH has a matching MERGE
        """
        ...

@dataclass(frozen=True)
class ProcessTree:
    """A validated composition of primitives."""
    primitives: tuple[Primitive, ...]
```

### Coordination Layers (Office-Mycelium-Neuron)

Process trees coordinate via heterarchy. No orchestrator. Just patterns of interaction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESS FOREST                                     │
│                                                                              │
│  OFFICE LAYER (deliberate, scheduled)                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                                  │
│  │ Tree A   │  │ Tree B   │  │ Tree C   │   ← "meetings"                   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     sync points                  │
│       │             │             │                                         │
│  MYCELIUM LAYER (stigmergic, async)                                         │
│  ──●──●──●──●──●──●──●──●──●──●──●──●──●──  ← pheromone trails             │
│                                                                              │
│  NEURON LAYER (signal propagation)                                          │
│  ══╤══╤══╤══════════╤══╤══════════╤══╤══   ← action potentials             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Office Layer:**

```python
@dataclass(frozen=True)
class Meeting:
    """Deliberate synchronization point between trees."""
    id: str
    participants: tuple[str, ...]  # Tree IDs
    agenda: str                    # Why are we meeting?
    outcome: "MeetingOutcome | None" = None

    async def convene(self, forest: "Forest") -> "MeetingOutcome":
        """Pause all participants, exchange state, reach consensus, resume."""
        ...
```

**Mycelium Layer:**

```python
@dataclass(frozen=True)
class PheromoneTrail:
    """Stigmergic signal left in the environment. Async coordination without coupling."""
    signal: str
    strength: float       # Decays over time (0.0 to 1.0)
    position: "ForestCoordinate"
    metadata: dict[str, Any]

    def decay(self, elapsed: float, rate: float = 0.1) -> "PheromoneTrail":
        """Trails weaken over time."""
        ...

class Mycelium:
    async def leave_trail(self, trail: PheromoneTrail) -> None: ...
    async def sense(
        self,
        position: "ForestCoordinate",
        radius: float,
        signal_filter: str | None = None,
    ) -> list[PheromoneTrail]: ...
```

**Neuron Layer:**

```python
@dataclass(frozen=True)
class Neuron:
    """Signal propagation node. Fires when threshold crossed."""
    id: str
    threshold: float
    connected_to: tuple[str, ...]
    accumulated: float = 0.0

    def receive(self, signal: float) -> tuple["Neuron", bool]:
        """Receive signal. Return (new_state, did_fire)."""
        ...

class NeuronLayer:
    async def fire(self, neuron_id: str, signal: float = 1.0) -> list[str]:
        """Send signal. Returns tree IDs to wake. Propagates breadth-first."""
        ...
```

### Observer as Fixed Point

The observer is the ground of truth. Not universal principles, but perception through an umwelt.

```python
@dataclass(frozen=True)
class Observer:
    """The grounding point for process truth. No view from nowhere."""
    id: str
    archetype: str            # "researcher", "tester", "poet", etc.
    umwelt: "Umwelt"          # Observer's projected world
    taste_confidence: float   # 0.0 to 1.0

    def should_elevate_to_taste(self, perception: "Perception") -> bool:
        """
        Elevate to explicit taste-grounding when:
        1. Observer confidence below threshold
        2. Perception is ambiguous
        3. Stakes are high (entropy investment)
        """
        ...
```

### Abundance Model Entropy

```python
@dataclass
class EntropyBudget:
    """Abundance-model entropy tracking. Soft limits, advisory warnings."""
    allocated: float
    consumed: float = 0.0
    tithe_recovered: float = 0.0

    @property
    def remaining(self) -> float: ...

    @property
    def is_advisory_exceeded(self) -> bool:
        """Soft limit exceeded—warn but don't fail."""
        ...

    def consume(self, amount: float) -> "EntropyBudget": ...

    def tithe(self, failed_branch_cost: float) -> "EntropyBudget":
        """Recover 30% entropy from failed branch."""
        ...

# Configuration
ENTROPY_CONFIG = {
    "per_instance_budget": 100_000,   # tokens per agent instance
    "forest_budget": 1_000_000,       # tokens across forest
    "tithe_recovery": 0.3,            # failed branches return 30%
    "abundance_mode": True,           # soft caps, not hard
}
```

### Termination Oracle

```python
@dataclass(frozen=True)
class TerminationOracle:
    """Determines when RECURSE should stop. Every RECURSE must have an oracle."""
    condition: Callable[[Any], bool]  # When to stop
    max_iterations: int = 1000        # Hard cap (abundance, but not infinite)
    iteration_cost: float = 1.0       # Entropy cost per iteration

    def should_terminate(self, state: Any, iteration: int) -> bool: ...
```

---

## Laws/Invariants

### Category Laws

Process Holons form a category. These laws are **verified**, not aspirational.

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `Id >> process ≡ process ≡ process >> Id` | `ProcessWitness.verify_identity()` |
| Associativity | `(p >> q) >> r ≡ p >> (q >> r)` | `ProcessWitness.verify_associativity()` |

### Termination Guarantee

Every valid composition **must terminate**. The operad ensures this by construction:

1. All processes must end with `TERMINATE` (arity_out=0)
2. Every `RECURSE` must have a `TerminationOracle`
3. Oracle has hard cap of `max_iterations`

### Well-Formedness Invariants

| Invariant | Description | Enforced By |
|-----------|-------------|-------------|
| Start | Process starts with `arity_in=0` | `operad.compose()` |
| End | Process ends with `arity_out=0` | `operad.compose()` |
| Balance | Every BRANCH has matching MERGE | `operad.compose()` |
| Termination | RECURSE has oracle | `TerminationOracle` required |
| Observer | Every operation has observer | `Logos.invoke()` requires Umwelt |

---

## Integration

### AGENTESE Paths

**Process Paths:**

| Path | Primitive | Semantics |
|------|-----------|-----------|
| `time.process.observe` | OBSERVE | Perceive with observer context |
| `time.process.branch[reason="..."]` | BRANCH | Deliberate Turn |
| `time.process.merge` | MERGE | Aggregate branches |
| `time.process.recurse[oracle="..."]` | RECURSE | Self-apply with termination |
| `time.process.yield` | YIELD | Emit intermediate |
| `time.process.terminate` | TERMINATE | Crystallize result |

**Forest Paths:**

| Path | Layer | Semantics |
|------|-------|-----------|
| `time.forest.spawn` | — | Create new tree |
| `time.forest.meeting[trees=[...]]` | Office | Synchronization point |
| `void.forest.trail[signal="..."]` | Mycelium | Leave pheromone |
| `void.forest.sense[radius=N]` | Mycelium | Detect trails |
| `void.forest.fire[threshold=T]` | Neuron | Signal propagation |

### Logos Integration

```python
class TimeProcessNode(LogosNode):
    """AGENTESE node for time.process.* paths."""
    handle: str = "time.process"

    def affordances(self, observer: AgentMeta) -> list[str]:
        return ["observe", "branch", "merge", "recurse", "yield", "terminate"]

    async def invoke(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        # Match aspect to primitive, invoke with observer context
        ...
```

---

## Example Compositions

### The Classic Cycle (One Among Infinite)

The 11-phase N-Phase Cycle is **not special**. It is one valid composition of primitives.

```python
# The classic cycle as operad composition
CLASSIC_CYCLE = operad.compose([
    OBSERVE,   # PLAN
    OBSERVE,   # RESEARCH
    YIELD,     # DEVELOP
    YIELD,     # STRATEGIZE
    BRANCH,    # CROSS-SYNERGIZE (explore combinations)
    MERGE,     # (collect combinations)
    YIELD,     # IMPLEMENT
    YIELD,     # QA
    YIELD,     # TEST
    YIELD,     # EDUCATE
    YIELD,     # MEASURE
    TERMINATE, # REFLECT
])
```

### Research Burst

```python
RESEARCH_BURST = operad.compose([
    OBSERVE,
    BRANCH, BRANCH, BRANCH,  # Many parallel explorations
    MERGE,
    TERMINATE,
])
```

### Recursive Deepening

```python
RECURSIVE_DEEPENING = operad.compose([
    OBSERVE,
    RECURSE,  # Until oracle satisfied
    TERMINATE,
])
```

### Dialectic Spiral

```python
DIALECTIC_SPIRAL = operad.compose([
    OBSERVE,          # Thesis
    BRANCH,           # Generate antithesis
    RECURSE,          # Synthesize until stable
    MERGE,
    YIELD,            # Emit synthesis
    RECURSE,          # Spiral deeper
    TERMINATE,
])
```

### Legacy Subsumption

The `plans/skills/n-phase-cycle/` directory becomes **example compositions**, not the definition.

| Legacy Skill | Process Holon Composition |
|--------------|---------------------------|
| `plan.md` | `OBSERVE` |
| `research.md` | `OBSERVE >> BRANCH >> MERGE` |
| `develop.md` | `YIELD` |
| `cross-synergize.md` | `BRANCH >> MERGE` |
| `implement.md` | `YIELD` |
| `reflect.md` | `TERMINATE` |

---

## Anti-Patterns

1. **Unbounded Recursion**: Every `RECURSE` must have a `TerminationOracle`. No infinite loops.

2. **Silent Branching**: Every `BRANCH` is a logged Turn. Never fork without recording intention and observer.

3. **Scarcity Thinking**: Abundance model uses soft limits. Don't optimize for token efficiency at expense of exploration.

4. **Hierarchy Instead of Heterarchy**: Use Office-Mycelium-Neuron layers, not centralized orchestrator.

5. **View From Nowhere**: Every operation has an observer. No universal truth evaluation.

---

## Principle Alignment

This specification embodies the seven principles:

| Principle | Manifestation |
|-----------|---------------|
| Tasteful | 6 primitives, not 60. Lean absurd flavor. |
| Curated | Judgment-based pruning, not scarcity limits |
| Ethical | Every Turn is logged, reversible, observable |
| Joy-Inducing | Lean absurd descriptions. The river decides. |
| Composable | Operad generates all valid processes |
| Heterarchical | Office-Mycelium-Neuron, no orchestrator |
| Generative | Spec generates implementation |

---

## Implementation Reference

See: `impl/claude/protocols/process_holons/`

```
process_holons/
├── primitives.py                # The six primitives
├── turn.py                      # Turn, TurnProjection
├── tree.py                      # ProcessTree
├── forest.py                    # Forest, coordination layers
├── operad.py                    # ProcessOperad, composition
├── coordination/
│   ├── office.py                # Meeting, synchronization
│   ├── mycelium.py              # PheromoneTrail, stigmergy
│   └── neuron.py                # Neuron, signal propagation
├── entropy.py                   # EntropyBudget, abundance model
├── observer.py                  # Observer, taste-grounding
├── witness.py                   # ProcessWitness, law verification
└── _tests/
    ├── test_primitives.py
    ├── test_operad.py           # Property-based tests for laws
    ├── test_coordination.py
    └── test_classic_cycle.py    # Verify classic cycle composes
```

---

*"The cycle dissolves into what it always was: one flowering among infinite. void.gratitude.tithe."*
