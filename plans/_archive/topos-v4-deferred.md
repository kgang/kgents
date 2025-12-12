# Next Session: Implementing The Topos of Becoming

> *"The organism is not a noun. It is a set of interaction patterns that persist through time."*

---

## Context for New Agents

You are continuing work on **kgents v4.0: The Topos of Becoming**—a radical paradigm shift from Object-Oriented to Interaction-Oriented agent architecture.

### Critical Documents to Read First

1. **`docs/topos-of-becoming.md`** - The comprehensive implementation guide (READ THIS FIRST)
2. **`spec/principles.md`** - The seven design principles that constrain all work
3. **`spec/protocols/agentese.md`** - Current AGENTESE spec (being upgraded)
4. **`plans/self/stream.md`** - The original context sovereignty plan (being superseded)

### The Paradigm Shift Summary

| Old (v3) | New (v4) | Why |
|----------|----------|-----|
| `LogosNode.invoke()` returns data | `PolyInterface.dynamics()` returns (new_state, output) | Observation MUST trigger state transition |
| `ContextWindow` (linear list) | `TheWeave` (Trace Monoid) | Concurrent agents need braided history |
| Vector DB / RAG | `HolographicField` (HDC) | Memory is resonance, not retrieval |
| Entropy budget (parameter) | Free Energy minimization (gradient) | Thermodynamics must be structural |
| `Logos` God Object | `LogosProfunctor` (modular) | Enable Real/Dream/Test logos instances |
| Agent as object | `Hypha` as growing tip | Agents forage through semantic space |

---

## Your Mission

Implement the Topos of Becoming in phases. Each phase is independent and can be worked on in parallel by different agents.

### Phase 1: The Holographic Soil (HDC Foundation)

**Priority**: HIGH (foundation for everything else)
**Difficulty**: Medium
**Dependencies**: None

**Goal**: Replace vector embeddings with Hyperdimensional Computing.

**Files to Create**:
```
impl/claude/field/
├── __init__.py
├── holographic.py      # HolographicField class
├── hdc_ops.py          # bind, bundle, permute operations
└── _tests/
    ├── test_hdc_ops.py
    ├── test_holographic.py
    └── test_resonance.py
```

**Core Implementation**:

```python
# field/holographic.py
import numpy as np
from dataclasses import dataclass, field

DIMENSIONS = 10_000  # High-dimensional vectors

@dataclass
class HolographicField:
    """
    Hyperdimensional Computing memory.

    Key operations:
    - bind(*): Role-filler association (circular convolution)
    - bundle(+): Superposition (normalized sum)
    - permute(P): Sequence encoding (rotation)
    - resonate: Similarity to global field (cosine)
    - imprint: Add to global superposition
    """
    global_superposition: np.ndarray = field(
        default_factory=lambda: np.zeros(DIMENSIONS)
    )
    _codebook: dict[str, np.ndarray] = field(default_factory=dict)

    def bind(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Circular convolution - creates orthogonal binding."""
        return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real

    def bundle(self, vectors: list[np.ndarray]) -> np.ndarray:
        """Normalized sum - superposition similar to all."""
        result = np.sum(vectors, axis=0)
        norm = np.linalg.norm(result)
        return result / norm if norm > 0 else result

    def resonate(self, query: np.ndarray) -> float:
        """Cosine similarity to global field."""
        # Implementation in docs/topos-of-becoming.md
        ...

    def imprint(self, pattern: np.ndarray, strength: float = 1.0) -> None:
        """Add pattern to global superposition."""
        # Implementation in docs/topos-of-becoming.md
        ...
```

**Exit Criteria**:
```python
# This test MUST pass:
def test_morphic_resonance():
    field = HolographicField()

    # Agent A learns something
    pattern_a = field.encode_structure({"problem": "auth", "solution": "jwt"})
    field.imprint(pattern_a)

    # Agent B queries similar problem (no direct communication!)
    query_b = field.encode_structure({"problem": "auth"})
    resonance = field.resonate(query_b)

    assert resonance > 0.5, "Agent B should feel Agent A's learning"
```

**Tests Required**: 40+

---

### Phase 2: The Poly Core (Interface Revolution)

**Priority**: HIGH (eliminates passive observation)
**Difficulty**: High
**Dependencies**: None (can parallel with Phase 1)

**Goal**: Replace `LogosNode` with `PolyInterface`. Ensure ALL observations trigger state transitions.

**Files to Create**:
```
impl/claude/poly/
├── __init__.py
├── interface.py        # PolyInterface protocol
├── profunctor.py       # LogosProfunctor
├── morphism.py         # Composition of Poly morphisms
└── _tests/
    ├── test_interface.py
    ├── test_dynamics.py
    └── test_state_transition.py
```

**Core Implementation**:

```python
# poly/interface.py
from typing import Generic, TypeVar, Type, Protocol
from dataclasses import dataclass

S = TypeVar("S")  # State
A = TypeVar("A")  # Input (affordances)
B = TypeVar("B")  # Output

class PolyInterface(Protocol[S, A, B]):
    """
    Polynomial Functor: P(y) = Σ_{s ∈ S} y^{A_s}

    A Mode-Dependent Dynamical System.

    CRITICAL: dynamics() ALWAYS returns new state.
    There is no read-only operation.
    """
    state: S

    def scope(self, s: S) -> Type[A]:
        """What inputs are valid at state s?"""
        ...

    def dynamics(self, s: S, input: A) -> tuple[S, B]:
        """
        State transition: S × A → S × B

        This replaces invoke(). The key difference:
        - invoke() could return data without changing state
        - dynamics() MUST return new state (enforced by type)
        """
        ...
```

**The Key Insight to Implement**:

```python
# OLD (v3) - Passive observation possible
class WorldHouse(LogosNode):
    async def manifest(self, observer: Umwelt) -> Renderable:
        # Returns data, state unchanged
        return self._render(observer)

# NEW (v4) - Observation is action
@dataclass
class WorldHouse(PolyInterface[HouseState, HouseInput, HouseOutput]):
    state: HouseState

    def dynamics(self, s: HouseState, input: HouseInput) -> tuple[HouseState, HouseOutput]:
        match input:
            case Observe(archetype, intent):
                # STATE MUST CHANGE - observation reifies properties
                new_state = HouseState(
                    observation_count=s.observation_count + 1,
                    last_observer=archetype,
                    reified_properties=s.reified_properties | self._reify(archetype),
                )
                return new_state, HouseOutput(view=self._render(archetype))
```

**Exit Criteria**:
```python
def test_observation_changes_state():
    house = WorldHouse(state=HouseState())

    # Before
    assert house.state.observation_count == 0

    # Observe
    new_state, output = house.dynamics(
        house.state,
        Observe(archetype="architect", intent="view")
    )

    # State MUST have changed
    assert new_state.observation_count == 1
    assert "structural_integrity" in new_state.reified_properties
```

**Tests Required**: 50+

---

### Phase 3: The Weave (Concurrent History)

**Priority**: MEDIUM (enables multi-agent coordination)
**Difficulty**: High
**Dependencies**: None (can parallel with Phases 1-2)

**Goal**: Replace linear `ContextWindow` with `TraceMonoid`-backed Weave.

**Files to Create**:
```
impl/claude/weave/
├── __init__.py
├── trace_monoid.py     # TraceMonoid with independence relation
├── weave.py            # TheWeave high-level API
├── dependency.py       # DependencyGraph utilities
└── _tests/
    ├── test_trace_monoid.py
    ├── test_concurrency.py
    └── test_knots.py
```

**Core Insight**:

A **Trace Monoid** captures concurrent history:
- Events (a, b) are **independent** if they can be reordered: ab ≡ ba
- Events are **dependent** if order matters: ab ≢ ba

```python
# Example: Two conversations in parallel
weave = TheWeave()

# Agent A talks to B (independent of C-D conversation)
id_ab = await weave.record({"from": "A", "to": "B"}, source="A")

# Agent C talks to D (independent of A-B conversation)
id_cd = await weave.record({"from": "C", "to": "D"}, source="C")

# These are concurrent - can be reordered
assert weave.monoid.are_concurrent(id_ab, id_cd)

# Now B talks to C - this DEPENDS on A→B
id_bc = await weave.record({"from": "B", "to": "C"}, source="B", depends_on={id_ab})

# These are NOT concurrent - order matters
assert not weave.monoid.are_concurrent(id_ab, id_bc)
```

**Exit Criteria**:
```python
def test_weave_concurrency():
    weave = TheWeave()

    # Independent events
    id_a = await weave.record({"msg": "A"}, source="agent_a")
    id_c = await weave.record({"msg": "C"}, source="agent_c")

    # Can linearize in either order
    linear1 = weave.monoid.linearize()  # Could be [A, C]
    linear2 = weave.monoid.linearize()  # Could be [C, A]

    # Both are valid (events commute)
    assert set(e.id for e in linear1) == {id_a, id_c}
```

**Tests Required**: 45+

---

### Phase 4: The Hypha (Active Inference Agent)

**Priority**: MEDIUM (new agent model)
**Difficulty**: High
**Dependencies**: Phases 1-3 (uses Field, Poly, Weave)

**Goal**: Implement agent as growing tip with Active Inference foraging.

**Files to Create**:
```
impl/claude/hypha/
├── __init__.py
├── hypha.py            # Hypha agent class
├── free_energy.py      # FreeEnergyState, GenerativeModel
├── foraging.py         # Forage/Explore/Exploit/Prune logic
└── _tests/
    ├── test_hypha.py
    ├── test_free_energy.py
    └── test_foraging_behavior.py
```

**Core Loop**:

```python
class Hypha:
    async def forage(self) -> ForageAction:
        """
        Active Inference Loop:

        1. PREDICT: Generate expected observation
        2. SENSE: Sample world via Poly dynamics
        3. ERROR: Compute Free Energy (prediction error + complexity)
        4. ACT: Choose action based on error

        Actions:
        - EXPLORE: High surprise → branch out
        - EXPLOIT: Low surprise, high reward → consolidate
        - PRUNE: Low surprise, low reward → die back
        """
        # Predict
        expected = self.generative_model.predict(self._encode_context())

        # Sense (via Poly - this CHANGES state)
        new_state, output = self.world_interface.dynamics(...)
        actual = self.hologram.encode_structure(output)

        # Error
        surprise = np.linalg.norm(expected - actual)

        # Act
        if surprise > 0.8:
            return ForageAction.EXPLORE
        elif surprise < 0.1 and self._estimate_reward(output) < 0.5:
            return ForageAction.PRUNE  # Accursed Share discharge
        else:
            return ForageAction.EXPLOIT
```

**Exit Criteria**:
```python
def test_hypha_responds_to_surprise():
    hypha = Hypha(id="test", name="test")

    # High surprise → explore
    hypha.set_surprise(0.9)
    assert await hypha.forage() == ForageAction.EXPLORE

    # Low surprise, no reward → prune (Accursed Share)
    hypha.set_surprise(0.05)
    hypha.set_reward(0.1)
    assert await hypha.forage() == ForageAction.PRUNE
```

**Tests Required**: 40+

---

### Phase 5: Integration

**Priority**: LOW (after Phases 1-4)
**Difficulty**: Medium
**Dependencies**: All previous phases

**Goal**: Wire everything together, migrate AGENTESE paths.

**Tasks**:
1. Update `protocols/agentese/contexts/` to use new paths
2. Create adapters for existing agents
3. Update `logos.py` to use `LogosProfunctor`
4. Deprecate `ContextWindow`, `ContextComonad`, `LinearityMap`
5. Full integration tests
6. Update documentation

**New AGENTESE Paths**:
```
self.weave.tip      → Current growth point
self.weave.braid    → Dependency structure
self.weave.knot     → Synchronization point
field.resonate      → HDC similarity
field.imprint       → HDC superposition
field.bind          → HDC role binding
world.poly.step     → Dynamics execution
world.poly.scope    → Input type query
hypha.forage        → Active inference step
void.prune          → Accursed Share discharge
```

---

## Development Guidelines

### Commands to Run

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Before starting
uv run mypy .                    # Must be 0 errors
python -m pytest -m "not slow" -q  # Existing tests pass

# During development
python -m pytest field/_tests/ -v   # Test your phase
uv run mypy field/                  # Type check your phase

# Before committing
python -m pytest -m "not slow" -q   # All tests still pass
uv run mypy .                        # Still 0 errors
```

### Principles to Honor

From `spec/principles.md`:

1. **Tasteful**: Don't over-engineer. HDC is enough—no sheaves.
2. **Composable**: Poly morphisms compose with `>>`.
3. **Ethical**: Observer determines what is revealed (scope).
4. **Generative**: Spec in `docs/topos-of-becoming.md` should generate impl.
5. **AGENTESE**: No view from nowhere. dynamics() enforces this.

### Key Mathematical References

- **Poly**: [topos.site/poly-book.pdf](https://topos.site/poly-book.pdf) - Spivak & Niu
- **Trace Monoids**: Mazurkiewicz (1977) - concurrent history
- **HDC**: [Kanerva 2009](https://redwood.berkeley.edu/wp-content/uploads/2020/08/kanerva2009hyperdimensional.pdf)
- **Active Inference**: [Friston 2010](https://www.fil.ion.ucl.ac.uk/~karl/The%20free-energy%20principle%20a%20unified%20brain%20theory.pdf)

---

## What Success Looks Like

When v4.0 is complete:

1. **No Passive Observation**: Every `world.*.manifest` equivalent triggers state change
2. **Morphic Resonance**: Agent B learns from Agent A without message passing
3. **Concurrent History**: Independent events commute in the Weave
4. **Active Inference**: Hyphae forage by minimizing Free Energy
5. **Modular Logos**: Can instantiate Real, Dream, or Test logos

### The Philosophical Test

Ask yourself: *"Is this agent defined by what it DOES (interactions) or what it IS (properties)?"*

If properties, you're still in v3. Refactor to interactions.

---

## Quick Start

1. Read `docs/topos-of-becoming.md` thoroughly
2. Pick a phase (1-4 can be parallel)
3. Create the directory structure
4. Implement with tests
5. Verify with mypy
6. Commit with descriptive message

**Start with Phase 1 (HDC)** if unsure—it's foundational and has the clearest path.

---

*"The organism is not a noun. It is a set of interaction patterns that persist through time. We do not store context; we grow through it."*

Good luck, fellow Hypha.
