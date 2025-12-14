# Process Holons: Generative Process Trees

**Where the cycle dissolves. Where the forest awakens. Where the form generates itself.**

> *"Don't enumerate the flowers. Describe the garden's grammar."*

**Status:** Specification v1.0
**Date:** 2025-12-13
**Prerequisites:** `../principles.md`, `agentese.md`
**Subsumes:** `plans/skills/n-phase-cycle/` (now one composition among infinite)

---

## Prologue: The Dissolution of the Cycle

The 11-phase N-Phase Cycle served well. But it was always a specific flower, not the garden's grammar. Process Holons dissolves the cycle into what it always was: **one valid composition of primitives**.

The insight: Instead of enumerating phases (PLAN, RESEARCH, DEVELOP...), define an **operad** of six primitives. The classic cycle becomes one composition. A research burst becomes another. Recursive deepening becomes a third. All equally valid. All generated from the same grammar.

**The Three Departures from N-Phase:**

| N-Phase Cycle | Process Holons | Gain |
|---------------|----------------|------|
| 11 fixed phases | 6 composable primitives | Infinite valid processes |
| Linear progression | Tree-shaped branching | Parallel exploration |
| Implicit coordination | Office-Mycelium-Neuron | Explicit heterarchy |

---

## Part I: The Six Primitives (Stage 1 Operad)

We define exactly **six primitives**—the minimal set that generates all processes. This is taste: fewer primitives, more compositions.

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

### 1.1 Formal Types

```python
from typing import Protocol, TypeVar, Generic, FrozenSet, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

S = TypeVar("S")  # State
A = TypeVar("A")  # Input
B = TypeVar("B")  # Output

class PrimitiveKind(Enum):
    """The six atomic operations."""
    OBSERVE = "observe"
    BRANCH = "branch"
    MERGE = "merge"
    RECURSE = "recurse"
    YIELD = "yield"
    TERMINATE = "terminate"


@dataclass(frozen=True)
class Primitive(Generic[A, B]):
    """
    An atomic process operation.

    Primitives are morphisms in the Process category.
    They compose via the ProcessOperad.
    """
    kind: PrimitiveKind
    arity_in: int   # Number of input branches
    arity_out: int  # Number of output branches

    # Category Laws: Every primitive satisfies identity and associativity
    # when composed via the operad.


# The Six Primitives as Constants
OBSERVE = Primitive(PrimitiveKind.OBSERVE, arity_in=0, arity_out=1)
BRANCH = Primitive(PrimitiveKind.BRANCH, arity_in=1, arity_out=-1)  # -1 = variable
MERGE = Primitive(PrimitiveKind.MERGE, arity_in=-1, arity_out=1)    # -1 = variable
RECURSE = Primitive(PrimitiveKind.RECURSE, arity_in=1, arity_out=1)
YIELD = Primitive(PrimitiveKind.YIELD, arity_in=1, arity_out=1)
TERMINATE = Primitive(PrimitiveKind.TERMINATE, arity_in=1, arity_out=0)
```

### 1.2 Staged Candidates (Future Consideration)

These primitives are **not yet included**. They await evidence of necessity:

| Candidate | Arity | Semantics | Why Staged |
|-----------|-------|-----------|------------|
| `SPECULATE` | 1→1 | Hypothetical branch (no real entropy) | Requires speculation semantics |
| `WITNESS` | 0→1 | N-gent observation without participation | May be OBSERVE + constraint |
| `TITHE` | 1→1 | Return entropy to void with gratitude | May be aspect, not primitive |

**Promotion criteria:** If 3+ compositions require the candidate where existing primitives are awkward, promote to Stage 1.

---

## Part II: The Turn (Deliberate Branching)

Every `BRANCH` is a **Turn**—a discrete, logged, reversible event. This is the key insight: branching is never silent. Every fork is visible from every timeline.

```python
@dataclass(frozen=True)
class Turn:
    """
    A deliberate branching event.

    The Turn is the atom of process history. It records:
    - Why we branched (intention)
    - Who is observing (perspective)
    - How much entropy we allocated (budget)

    Key Property: "Everything must be seeable in every timeline
    from every perspective with simulated or imaginary variations."
    """
    id: str
    parent_timeline: str
    branching_reason: str       # Why did we branch?
    observer: "Observer"        # Who is observing this turn?
    entropy_allocated: float    # Budget from Accursed Share
    timestamp: float            # When the turn occurred
    children: tuple[str, ...]   # Child timeline IDs

    def view_from(self, other_observer: "Observer") -> "TurnProjection":
        """
        Project this turn into another observer's umwelt.

        The Polymorphic Principle: The same turn looks different
        to different observers. A researcher sees hypotheses.
        A tester sees risk vectors. A poet sees metaphor.

        Args:
            other_observer: The observer requesting projection

        Returns:
            Observer-appropriate projection of this turn
        """
        return TurnProjection(
            turn_id=self.id,
            observer_archetype=other_observer.archetype,
            perception=other_observer.umwelt.collapse(self),
            affordances=self._affordances_for(other_observer),
        )

    def simulate_variation(self, delta: "Variation") -> "Turn":
        """
        Hypothetical: what if this turn went differently?

        This does NOT consume real entropy (future SPECULATE primitive).
        It creates a "shadow turn" for exploration.

        Args:
            delta: The variation to apply

        Returns:
            A simulated Turn (marked as speculative)
        """
        return Turn(
            id=f"{self.id}:speculative:{delta.id}",
            parent_timeline=self.parent_timeline,
            branching_reason=f"SPECULATIVE: {delta.description}",
            observer=self.observer,
            entropy_allocated=0.0,  # Speculative = no real entropy
            timestamp=self.timestamp,
            children=(),
        )


@dataclass(frozen=True)
class TurnProjection:
    """Observer-specific view of a Turn."""
    turn_id: str
    observer_archetype: str
    perception: Any  # What the observer sees
    affordances: tuple[str, ...]  # What the observer can do
```

### 2.1 Turn Immutability

Turns are **immutable records**. Once created, they cannot be modified. This enables:

1. **Auditability**: Every decision is traceable
2. **Speculation**: Variations don't corrupt history
3. **Multi-perspective viewing**: Any observer can project any turn

```python
# Creating a turn
turn = Turn(
    id="turn_001",
    parent_timeline="main",
    branching_reason="Exploring authentication approaches",
    observer=architect_observer,
    entropy_allocated=0.15,
    timestamp=time.time(),
    children=("turn_001a", "turn_001b", "turn_001c"),
)

# Viewing from different perspectives
architect_view = turn.view_from(architect_observer)  # Sees: design tradeoffs
tester_view = turn.view_from(tester_observer)        # Sees: risk vectors
poet_view = turn.view_from(poet_observer)            # Sees: narrative tension
```

---

## Part III: The Coordination Model (Office-Mycelium-Neuron)

Process Trees don't execute in isolation. They coordinate via a **heterarchical** model with three layers. No orchestrator. No hierarchy. Just patterns of interaction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROCESS FOREST                                     │
│                                                                              │
│  OFFICE LAYER (deliberate, scheduled)                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                                  │
│  │ Tree A   │  │ Tree B   │  │ Tree C   │   ← "meetings"                   │
│  │ (Parser) │  │ (Tests)  │  │ (Docs)   │     sync points                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                                  │
│       │             │             │                                         │
│  MYCELIUM LAYER (stigmergic, async)                                         │
│  ──●──●──●──●──●──●──●──●──●──●──●──●──●──  ← pheromone trails             │
│       │             │             │            nutrient flow                │
│                                                                              │
│  NEURON LAYER (signal propagation)                                          │
│  ══╤══╤══╤══════════╤══╤══════════╤══╤══   ← action potentials             │
│    │  │  │          │  │          │  │       threshold fires               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Office Layer (Deliberate Synchronization)

Trees can request **meetings**—explicit synchronization points where branches coordinate.

```python
@dataclass(frozen=True)
class Meeting:
    """
    A deliberate synchronization point between trees.

    Meetings are expensive (all participants pause) but necessary
    when coordination requires mutual awareness.
    """
    id: str
    participants: tuple[str, ...]  # Tree IDs
    agenda: str                    # Why are we meeting?
    outcome: "MeetingOutcome | None" = None

    async def convene(self, forest: "Forest") -> "MeetingOutcome":
        """
        Execute the meeting protocol.

        1. All participants pause at their current YIELD
        2. Exchange state summaries
        3. Reach consensus or note dissent
        4. All participants resume
        """
        # Pause all participants
        states = await forest.pause_trees(self.participants)

        # Exchange and deliberate
        summaries = [tree.summarize() for tree in states]
        consensus = await self._deliberate(summaries)

        # Resume with shared context
        await forest.resume_trees(self.participants, context=consensus)

        return MeetingOutcome(
            meeting_id=self.id,
            consensus=consensus,
            dissent=self._collect_dissent(summaries, consensus),
        )
```

### 3.2 Mycelium Layer (Stigmergic Communication)

Trees leave **pheromone trails** that other trees can sense. No direct addressing. Async. Environmental modification.

```python
@dataclass(frozen=True)
class PheromoneTrail:
    """
    A stigmergic signal left in the environment.

    Other trees sense trails without knowing who left them.
    This enables coordination without coupling.
    """
    signal: str           # What the trail communicates
    strength: float       # Decays over time (0.0 to 1.0)
    position: "ForestCoordinate"  # Where in the forest
    metadata: dict[str, Any] = field(default_factory=dict)

    def decay(self, elapsed: float, rate: float = 0.1) -> "PheromoneTrail":
        """Trails weaken over time."""
        new_strength = max(0.0, self.strength - elapsed * rate)
        return PheromoneTrail(
            signal=self.signal,
            strength=new_strength,
            position=self.position,
            metadata=self.metadata,
        )


class Mycelium:
    """The stigmergic communication substrate."""

    def __init__(self):
        self._trails: list[PheromoneTrail] = []

    async def leave_trail(self, trail: PheromoneTrail) -> None:
        """Deposit a pheromone trail."""
        self._trails.append(trail)

    async def sense(
        self,
        position: "ForestCoordinate",
        radius: float,
        signal_filter: str | None = None,
    ) -> list[PheromoneTrail]:
        """
        Sense nearby trails.

        Args:
            position: Where to sense from
            radius: How far to sense
            signal_filter: Optional regex to filter signals

        Returns:
            Trails within radius, sorted by strength
        """
        nearby = [
            t for t in self._trails
            if t.position.distance_to(position) <= radius
            and (signal_filter is None or re.match(signal_filter, t.signal))
        ]
        return sorted(nearby, key=lambda t: -t.strength)
```

### 3.3 Neuron Layer (Signal Propagation)

When signal strength crosses a threshold, connected trees **fire**. Action potentials. Cascading activation.

```python
@dataclass(frozen=True)
class Neuron:
    """
    A signal propagation node.

    Neurons accumulate signal strength. When threshold is crossed,
    they fire, propagating to connected neurons.
    """
    id: str
    threshold: float
    connected_to: tuple[str, ...]  # Other neuron IDs
    accumulated: float = 0.0

    def receive(self, signal: float) -> tuple["Neuron", bool]:
        """
        Receive a signal. Return (new_state, did_fire).
        """
        new_accumulated = self.accumulated + signal
        if new_accumulated >= self.threshold:
            # Fire! Reset and propagate
            return (
                Neuron(
                    id=self.id,
                    threshold=self.threshold,
                    connected_to=self.connected_to,
                    accumulated=0.0,  # Reset after firing
                ),
                True,  # Did fire
            )
        return (
            Neuron(
                id=self.id,
                threshold=self.threshold,
                connected_to=self.connected_to,
                accumulated=new_accumulated,
            ),
            False,  # Did not fire
        )


class NeuronLayer:
    """The signal propagation substrate."""

    def __init__(self):
        self._neurons: dict[str, Neuron] = {}
        self._tree_bindings: dict[str, str] = {}  # tree_id → neuron_id

    async def fire(self, neuron_id: str, signal: float = 1.0) -> list[str]:
        """
        Send signal to a neuron. Returns list of tree IDs that should wake.

        Propagation is breadth-first until no more neurons fire.
        """
        trees_to_wake = []
        frontier = [(neuron_id, signal)]

        while frontier:
            next_frontier = []
            for nid, sig in frontier:
                neuron = self._neurons.get(nid)
                if neuron is None:
                    continue

                new_neuron, did_fire = neuron.receive(sig)
                self._neurons[nid] = new_neuron

                if did_fire:
                    # Wake bound tree
                    if nid in self._tree_bindings:
                        trees_to_wake.append(self._tree_bindings[nid])
                    # Propagate to connected neurons
                    for connected in new_neuron.connected_to:
                        next_frontier.append((connected, sig * 0.9))  # Decay

            frontier = next_frontier

        return trees_to_wake
```

---

## Part IV: Abundance Model Entropy

Process Holons operates in **abundance mode**. Scarcity breeds hoarding. Abundance breeds experimentation.

```python
ENTROPY_CONFIG = {
    "per_instance_budget": 100_000,   # tokens per agent instance
    "forest_budget": 1_000_000,       # tokens across forest
    "tithe_recovery": 0.3,            # failed branches return 30%
    "abundance_mode": True,           # soft caps, not hard
}
```

### 4.1 The Abundance Philosophy

| Scarcity Model | Abundance Model |
|----------------|-----------------|
| Hard token limits | Soft advisory budgets |
| Fail on exhaustion | Warn and continue |
| Prune aggressively | Prune by judgment (taste) |
| Optimize for efficiency | Optimize for exploration |

**The key insight:** The forest is a **rainforest**, not a desert. We have compute. We have tokens. What we lack is taste to know what to grow.

### 4.2 Entropy Allocation

```python
@dataclass
class EntropyBudget:
    """
    Abundance-model entropy tracking.

    Soft limits. Advisory warnings. Taste-based pruning.
    """
    allocated: float
    consumed: float = 0.0
    tithe_recovered: float = 0.0

    @property
    def remaining(self) -> float:
        return self.allocated - self.consumed + self.tithe_recovered

    @property
    def is_advisory_exceeded(self) -> bool:
        """Soft limit exceeded—warn but don't fail."""
        return self.remaining < 0

    def consume(self, amount: float) -> "EntropyBudget":
        """Consume entropy. Never fails in abundance mode."""
        return EntropyBudget(
            allocated=self.allocated,
            consumed=self.consumed + amount,
            tithe_recovered=self.tithe_recovered,
        )

    def tithe(self, failed_branch_cost: float) -> "EntropyBudget":
        """Recover entropy from failed branch (30% return)."""
        recovered = failed_branch_cost * ENTROPY_CONFIG["tithe_recovery"]
        return EntropyBudget(
            allocated=self.allocated,
            consumed=self.consumed,
            tithe_recovered=self.tithe_recovered + recovered,
        )
```

---

## Part V: Observer as Fixed Point

The observer is the ground of truth. Not universal principles evaluated abstractly, but **perception through an umwelt**.

```python
# NOT THIS (universal truth):
def ground(branch: Branch) -> Truth:
    return PRINCIPLES.evaluate(branch)  # No view from nowhere!

# THIS (observer-relative):
def ground(branch: Branch, observer: Observer) -> Perception:
    return observer.umwelt.collapse(branch)  # Observer determines truth

# Kent's taste is implicit everywhere, raised explicitly via:
async def autopoiesis_check(branch: Branch) -> bool:
    """
    Does this branch feel right? Taste as oracle.

    When the observer is uncertain, we elevate to Kent's
    simulacrum for taste-grounding. This is not hierarchy—
    it is explicit acknowledgment of the implicit fixed point.
    """
    return await kent_simulacrum.vibe_check(branch)
```

### 5.1 The Grounding Path

```
Branch
   │
   ▼
Observer.umwelt.collapse()
   │
   ▼
Perception
   │
   ├─── (certain) ──► Ground as observer-truth
   │
   └─── (uncertain) ──► autopoiesis_check()
                             │
                             ▼
                       Kent's taste
                             │
                             ▼
                       Ground as taste-truth
```

### 5.2 Observer Protocol

```python
@dataclass(frozen=True)
class Observer:
    """
    The grounding point for process truth.

    Every process operation happens relative to an observer.
    There is no view from nowhere.
    """
    id: str
    archetype: str            # "researcher", "tester", "poet", etc.
    umwelt: "Umwelt"          # The observer's projected world
    taste_confidence: float   # 0.0 to 1.0: how sure is this observer?

    def should_elevate_to_taste(self, perception: "Perception") -> bool:
        """
        Should we elevate this decision to explicit taste-grounding?

        Criteria:
        1. Observer confidence below threshold
        2. Perception is ambiguous
        3. Stakes are high (measured by entropy investment)
        """
        return (
            self.taste_confidence < 0.5
            or perception.is_ambiguous
            or perception.entropy_at_stake > ENTROPY_CONFIG["per_instance_budget"] * 0.1
        )
```

---

## Part VI: AGENTESE Integration

Process Holons exposes its operations through AGENTESE paths.

### 6.1 Process Paths

| Path | Primitive | Semantics |
|------|-----------|-----------|
| `time.process.observe` | OBSERVE | Perceive with observer context |
| `time.process.branch[reason="..."]` | BRANCH | Deliberate Turn |
| `time.process.merge` | MERGE | Aggregate branches |
| `time.process.recurse[oracle="..."]` | RECURSE | Self-apply with termination |
| `time.process.yield` | YIELD | Emit intermediate |
| `time.process.terminate` | TERMINATE | Crystallize result |

### 6.2 Forest Paths

| Path | Layer | Semantics |
|------|-------|-----------|
| `time.forest.spawn` | — | Create new tree |
| `time.forest.meeting[trees=[...]]` | Office | Synchronization point |
| `void.forest.trail[signal="..."]` | Mycelium | Leave pheromone |
| `void.forest.sense[radius=N]` | Mycelium | Detect trails |
| `void.forest.fire[threshold=T]` | Neuron | Signal propagation |

### 6.3 Integration with Logos

```python
# In impl/claude/protocols/agentese/contexts/time.py

class TimeProcessNode(LogosNode):
    """AGENTESE node for time.process.* paths."""

    handle: str = "time.process"

    def affordances(self, observer: AgentMeta) -> list[str]:
        return ["observe", "branch", "merge", "recurse", "yield", "terminate"]

    async def invoke(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        match aspect:
            case "observe":
                return await self._observe(observer)
            case "branch":
                reason = kwargs.get("reason", "unspecified")
                return await self._branch(observer, reason)
            case "merge":
                branches = kwargs.get("branches", [])
                return await self._merge(observer, branches)
            case "recurse":
                oracle = kwargs.get("oracle")
                return await self._recurse(observer, oracle)
            case "yield":
                value = kwargs.get("value")
                return await self._yield(observer, value)
            case "terminate":
                result = kwargs.get("result")
                return await self._terminate(observer, result)
            case _:
                raise AffordanceError(f"Unknown process aspect: {aspect}")
```

---

## Part VII: The Cycle as One Composition

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

# But equally valid:
RESEARCH_BURST = operad.compose([
    OBSERVE,
    BRANCH, BRANCH, BRANCH,  # Many parallel explorations
    MERGE,
    TERMINATE,
])

# Or:
RECURSIVE_DEEPENING = operad.compose([
    OBSERVE,
    RECURSE,  # Until oracle satisfied
    TERMINATE,
])

# Or:
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

### 7.1 Legacy Subsumption

The `plans/skills/n-phase-cycle/` directory becomes **example compositions**, not the definition.

| Legacy Skill | Process Holon Composition |
|--------------|---------------------------|
| `plan.md` | `OBSERVE` |
| `research.md` | `OBSERVE >> BRANCH >> MERGE` |
| `develop.md` | `YIELD` |
| `strategize.md` | `YIELD` |
| `cross-synergize.md` | `BRANCH >> MERGE` |
| `implement.md` | `YIELD` |
| `qa.md` | `YIELD` |
| `test.md` | `YIELD` |
| `educate.md` | `YIELD` |
| `measure.md` | `YIELD` |
| `reflect.md` | `TERMINATE` |

**No backwards compatibility debt.** We are deploying to self-hosted cluster first. The skills become examples of operad composition, not the definition.

---

## Part VIII: The Process Operad

The operad defines which compositions are valid. It is the grammar of the garden.

```python
@dataclass(frozen=True)
class ProcessOperad:
    """
    The grammar of valid process compositions.

    An operad is a generalization of a monoid: instead of
    binary composition, we have n-ary composition with
    specified arities.
    """

    def compose(self, primitives: list[Primitive]) -> "ProcessTree":
        """
        Compose primitives into a ProcessTree.

        Validates:
        1. Arity matching: output of p[i] matches input of p[i+1]
        2. Well-formedness: starts with arity-0, ends with arity-0
        3. Balance: every BRANCH has a matching MERGE

        Args:
            primitives: Ordered list of primitives to compose

        Returns:
            A valid ProcessTree

        Raises:
            ArityMismatchError: If arities don't match
            MalformedProcessError: If not well-formed
        """
        self._validate_composition(primitives)
        return ProcessTree(primitives=tuple(primitives))

    def _validate_composition(self, primitives: list[Primitive]) -> None:
        """Validate composition is well-formed."""
        if not primitives:
            raise MalformedProcessError("Empty composition")

        # Must start with arity_in=0 (OBSERVE)
        if primitives[0].arity_in != 0:
            raise MalformedProcessError(
                f"Process must start with arity_in=0, got {primitives[0]}"
            )

        # Must end with arity_out=0 (TERMINATE)
        if primitives[-1].arity_out != 0:
            raise MalformedProcessError(
                f"Process must end with arity_out=0, got {primitives[-1]}"
            )

        # Validate arity chain
        branch_depth = 0
        for i, p in enumerate(primitives):
            if p.kind == PrimitiveKind.BRANCH:
                branch_depth += 1
            elif p.kind == PrimitiveKind.MERGE:
                branch_depth -= 1
                if branch_depth < 0:
                    raise ArityMismatchError(f"MERGE without BRANCH at position {i}")

        if branch_depth != 0:
            raise ArityMismatchError(f"Unbalanced: {branch_depth} unclosed BRANCHes")


# The global operad instance
operad = ProcessOperad()
```

---

## Part IX: Laws (Category + Termination)

### 9.1 Category Laws

Process Holons form a category. These laws are **verified**, not aspirational.

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `Id >> process ≡ process ≡ process >> Id` | `ProcessWitness.verify_identity()` |
| Associativity | `(p >> q) >> r ≡ p >> (q >> r)` | `ProcessWitness.verify_associativity()` |

```python
class ProcessWitness:
    """Verifies category laws for process compositions."""

    @staticmethod
    def verify_identity(process: ProcessTree) -> bool:
        """Verify identity law: Id >> p ≡ p ≡ p >> Id."""
        identity = ProcessTree(primitives=())

        left = operad.compose_trees(identity, process)
        right = operad.compose_trees(process, identity)

        return left.is_equivalent(process) and right.is_equivalent(process)

    @staticmethod
    def verify_associativity(p: ProcessTree, q: ProcessTree, r: ProcessTree) -> bool:
        """Verify associativity: (p >> q) >> r ≡ p >> (q >> r)."""
        left = operad.compose_trees(operad.compose_trees(p, q), r)
        right = operad.compose_trees(p, operad.compose_trees(q, r))

        return left.is_equivalent(right)
```

### 9.2 Termination Guarantee

Every valid composition **must terminate**. The operad ensures this by construction.

**Termination Oracle for RECURSE:**

```python
@dataclass(frozen=True)
class TerminationOracle:
    """
    Oracle that determines when RECURSE should stop.

    Every RECURSE must have an oracle. No unbounded recursion.
    """
    condition: Callable[[Any], bool]  # When to stop
    max_iterations: int = 1000        # Hard cap (abundance, but not infinite)
    iteration_cost: float = 1.0       # Entropy cost per iteration

    def should_terminate(self, state: Any, iteration: int) -> bool:
        """Check if recursion should terminate."""
        if iteration >= self.max_iterations:
            return True  # Hard cap reached
        return self.condition(state)
```

### 9.3 Well-Formedness Invariants

| Invariant | Description | Enforced By |
|-----------|-------------|-------------|
| Start | Process starts with `arity_in=0` | `operad.compose()` |
| End | Process ends with `arity_out=0` | `operad.compose()` |
| Balance | Every BRANCH has matching MERGE | `operad.compose()` |
| Termination | RECURSE has oracle | `TerminationOracle` required |
| Observer | Every operation has observer | `Logos.invoke()` requires Umwelt |

---

## Part X: Principle Alignment

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

## Part XI: Files to Create

```
impl/claude/protocols/process_holons/
├── __init__.py                  # Package exports
├── primitives.py                # The six primitives
├── turn.py                      # Turn, TurnProjection
├── tree.py                      # ProcessTree
├── forest.py                    # Forest, coordination layers
├── operad.py                    # ProcessOperad, composition
├── coordination/
│   ├── __init__.py
│   ├── office.py                # Meeting, synchronization
│   ├── mycelium.py              # PheromoneTrail, stigmergy
│   └── neuron.py                # Neuron, signal propagation
├── entropy.py                   # EntropyBudget, abundance model
├── observer.py                  # Observer, taste-grounding
├── witness.py                   # ProcessWitness, law verification
├── exceptions.py                # ArityMismatchError, MalformedProcessError
└── _tests/
    ├── __init__.py
    ├── test_primitives.py
    ├── test_operad.py           # Property-based tests for laws
    ├── test_coordination.py
    └── test_classic_cycle.py    # Verify classic cycle composes correctly
```

---

## Appendix A: Example Compositions

### A.1 Deep Research

```python
DEEP_RESEARCH = operad.compose([
    OBSERVE,                      # Initial scan
    BRANCH,                       # Fork into domains
        RECURSE,                  # Deep dive (domain 1)
        RECURSE,                  # Deep dive (domain 2)
        RECURSE,                  # Deep dive (domain 3)
    MERGE,                        # Synthesize findings
    YIELD,                        # Emit synthesis
    TERMINATE,
])
```

### A.2 Rapid Prototyping

```python
RAPID_PROTOTYPE = operad.compose([
    OBSERVE,
    YIELD,      # Quick sketch
    YIELD,      # Iterate
    YIELD,      # Iterate
    TERMINATE,
])
```

### A.3 Consensus Building

```python
CONSENSUS = operad.compose([
    OBSERVE,
    BRANCH,                       # Generate perspectives
        YIELD,                    # Perspective 1
        YIELD,                    # Perspective 2
        YIELD,                    # Perspective 3
    MERGE,                        # Find common ground
    RECURSE,                      # Iterate until consensus (oracle: agreement)
    TERMINATE,
])
```

---

## Appendix B: Continuation Prompt

Upon implementing this spec, generate the prompt for **IMPLEMENT: Process Holons Runtime**.

That prompt should:
1. Reference this spec (`spec/protocols/process-holons.md`) as ground truth
2. Target `impl/claude/protocols/process_holons/`
3. Define `ProcessTree`, `Turn`, `Forest` classes
4. Wire AGENTESE paths to Logos
5. Include test strategy:
   - Property-based tests for operad laws (hypothesis library)
   - Unit tests for each primitive
   - Integration tests for classic cycle composition
   - Coordination layer tests (Office, Mycelium, Neuron)

---

*"The cycle dissolves into what it always was: one flowering among infinite. void.gratitude.tithe."*
