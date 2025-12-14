---
path: plans/skills/polynomial-agent
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Skill: Building a Polynomial Agent

> Create a state-machine agent with mode-dependent behavior using the polynomial functor architecture.

**Difficulty**: Medium-Advanced
**Prerequisites**: Understanding of Agent[A, B], state machines, category theory basics
**Files Touched**: `impl/claude/agents/<letter>/polynomial.py`, `impl/claude/agents/poly/`, tests
**References**: `plans/architecture/polyfunctor.md`, `spec/architecture/polyfunctor.md`

---

## Overview

A **Polynomial Agent** extends the basic `Agent[A, B]` pattern to capture **mode-dependent behavior**—agents that behave differently based on their internal state.

### The Key Insight

```
Agent[A, B] ≅ A → B         # Stateless transformation (a lie)
PolyAgent[S, A, B]          # State-dependent behavior (the truth)
```

Traditional `Agent[A, B]` misses a critical aspect: real agents have **modes**. A file system agent in "reading" mode accepts different inputs than in "writing" mode. The polynomial functor captures this.

### When to Use Polynomial Agents

| Use Case | Traditional Agent | Polynomial Agent |
|----------|-------------------|------------------|
| Stateless transform | ✓ | ✓ (degenerates to stateless) |
| Mode-dependent I/O | ✗ | ✓ |
| State machine | ✗ | ✓ |
| Protocol phases | ✗ | ✓ |
| Composable dynamics | ✗ | ✓ |

---

## The Polynomial Agent Structure

From `impl/claude/agents/poly/protocol.py`:

```python
PolyAgent[S, A, B] = (
    positions: FrozenSet[S],          # Valid states
    directions: S → FrozenSet[Type],  # State-dependent valid inputs
    transition: S × A → (S, B)        # State × Input → (NewState, Output)
)
```

**Mathematical Interpretation** (optional):
```
P(y) = Σ_{s ∈ S} y^{E(s)}
```
Where S is positions, E(s) is directions at position s.

---

## Step-by-Step: Creating a Polynomial Agent

### Step 1: Define the State Machine

Start by identifying the states (positions) your agent needs.

**Example**: Memory Agent States

```python
from enum import Enum, auto

class MemoryPhase(Enum):
    """Positions in the memory polynomial."""
    IDLE = auto()       # Ready for commands
    LOADING = auto()    # Fetching data
    STORING = auto()    # Writing data
    QUERYING = auto()   # Searching
    FORGETTING = auto() # Clearing data
```

**Good state design**:
- Each state represents a distinct mode of operation
- States should be exhaustive (cover all cases)
- States should be mutually exclusive

### Step 2: Define Direction Functions

Directions specify what inputs are valid at each state.

```python
def memory_directions(phase: MemoryPhase) -> frozenset[type]:
    """What inputs are valid at each phase?"""
    match phase:
        case MemoryPhase.IDLE:
            # Can route to any operation
            return frozenset({LoadCommand, StoreCommand, QueryCommand, ForgetCommand})
        case MemoryPhase.LOADING:
            return frozenset({LoadCommand})
        case MemoryPhase.STORING:
            return frozenset({StoreCommand})
        case MemoryPhase.QUERYING:
            return frozenset({QueryCommand})
        case MemoryPhase.FORGETTING:
            return frozenset({ForgetCommand})
```

**Key principle**: The directions function encodes what's *valid* at each state, not just what's *possible*.

### Step 3: Define the Transition Function

The core of the polynomial agent: how state and input produce new state and output.

```python
def memory_transition(
    phase: MemoryPhase, input: Any
) -> tuple[MemoryPhase, Any]:
    """
    State transition function.

    transition: Phase × Command → (NewPhase, Response)
    """
    match phase:
        case MemoryPhase.IDLE:
            # Route to appropriate phase based on command type
            if isinstance(input, LoadCommand):
                return MemoryPhase.LOADING, input
            elif isinstance(input, StoreCommand):
                return MemoryPhase.STORING, input
            # ... etc

        case MemoryPhase.LOADING:
            cmd = input if isinstance(input, LoadCommand) else LoadCommand()
            # Perform load operation
            data = load_from_storage(cmd.key)
            return MemoryPhase.IDLE, MemoryResponse(success=True, data=data)

        case MemoryPhase.STORING:
            cmd = input if isinstance(input, StoreCommand) else StoreCommand(state=input)
            # Perform store operation
            save_to_storage(cmd.key, cmd.state)
            return MemoryPhase.IDLE, MemoryResponse(success=True)
```

### Step 4: Create the PolyAgent

Assemble the pieces into a `PolyAgent`:

```python
from agents.poly.protocol import PolyAgent

MEMORY_POLYNOMIAL: PolyAgent[MemoryPhase, Any, Any] = PolyAgent(
    name="MemoryPolynomial",
    positions=frozenset(MemoryPhase),
    _directions=memory_directions,
    _transition=memory_transition,
)
```

### Step 5: Create a Backwards-Compatible Wrapper (Optional)

For integration with existing code expecting `Agent[A, B]`:

```python
class MemoryPolynomialAgent:
    """
    Async wrapper providing Agent-like interface.
    """

    def __init__(self, initial_state: Any = None) -> None:
        self._poly = MEMORY_POLYNOMIAL
        self._phase = MemoryPhase.IDLE
        if initial_state is not None:
            self._store = {"_default": initial_state}

    @property
    def phase(self) -> MemoryPhase:
        return self._phase

    async def store(self, data: Any, key: str = "_default") -> MemoryResponse:
        """Store data (async interface for compatibility)."""
        # Route through IDLE
        self._phase, _ = self._poly.transition(self._phase, StoreCommand(state=data, key=key))
        # Execute the store
        self._phase, response = self._poly.transition(self._phase, StoreCommand(state=data, key=key))
        return response
```

---

## Critical Patterns

### Pattern 1: Instance Isolation

**Problem**: Global state causes instances to share memory.

```python
# BAD: Global state
_memory_state: dict[str, Any] = {}  # All instances share this!

# GOOD: Per-instance state
class MemoryStore:
    def __init__(self) -> None:
        self.state: dict[str, Any] = {}
        self.history: list[Any] = []

def create_memory_polynomial(store: MemoryStore) -> PolyAgent:
    """Factory creates polynomial with isolated store."""
    def bound_transition(phase, input):
        return memory_transition(phase, input, store)  # Closure captures store
    return PolyAgent(..., _transition=bound_transition)
```

**Always** use factory functions for stateful polynomials.

### Pattern 2: Bayesian Confidence

When computing confidence from evidence:

```python
def compute_confidence(n_supporting: int, n_contradicting: int, prior: float = 0.5) -> float:
    """
    Bayesian confidence with Laplace smoothing.

    Prevents extreme values (0.0 or 1.0) which cause issues downstream.
    """
    total = n_supporting + n_contradicting
    if total == 0:
        return prior  # No evidence → return prior

    alpha = 1.0  # Smoothing parameter
    confidence = (n_supporting + alpha * prior) / (total + alpha)

    # Clamp to reasonable bounds
    return max(0.05, min(0.95, confidence))
```

### Pattern 3: Input Validation

Always validate inputs in the transition function:

```python
def validate_query(input: Any) -> Query:
    """Normalize and validate input."""
    if input is None:
        return Query(claim="<empty>")

    if isinstance(input, Query):
        claim = input.claim.strip() if input.claim else "<empty>"
        if len(claim) > 10000:
            claim = claim[:10000] + "... [truncated]"
        return Query(claim=claim, context=input.context)

    # Convert to string
    claim = str(input).strip() or "<empty>"
    return Query(claim=claim)
```

### Pattern 4: Composition via WiringDiagram

Compose polynomial agents:

```python
from agents.poly import WiringDiagram, sequential, parallel

# Sequential: soul → alethic
diagram = WiringDiagram(
    name="soul_then_alethic",
    left=SOUL_POLYNOMIAL,
    right=ALETHIC_AGENT,
)
composed = diagram.compose()

# Parallel: run soul and memory concurrently
par = parallel(SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL)
# State is product: (SoulContext, MemoryPhase)
```

---

## Testing Polynomial Agents

### Required Tests

1. **State Machine Tests**
   ```python
   def test_all_phases_defined(self) -> None:
       """All phases are defined."""
       for phase in MyPhase:
           assert phase in MY_POLYNOMIAL.positions
   ```

2. **Direction Tests**
   ```python
   def test_idle_accepts_all_commands(self) -> None:
       """IDLE accepts all command types."""
       dirs = my_directions(MyPhase.IDLE)
       assert Command1 in dirs
       assert Command2 in dirs
   ```

3. **Transition Tests**
   ```python
   def test_transition_returns_to_idle(self) -> None:
       """Phase returns to IDLE after operation."""
       new_phase, _ = my_transition(MyPhase.PROCESSING, input)
       assert new_phase == MyPhase.IDLE
   ```

4. **Instance Isolation Tests**
   ```python
   async def test_instances_are_isolated(self) -> None:
       """Two instances don't share state."""
       agent1 = MyPolynomialAgent()
       agent2 = MyPolynomialAgent()

       await agent1.store("data1")
       result = await agent2.load()

       assert result is None  # agent2 shouldn't see agent1's data
   ```

5. **Property-Based Tests** (optional but recommended)
   ```python
   from hypothesis import given, strategies as st

   @given(input_val=st.integers())
   def test_identity_law(self, input_val: int) -> None:
       """Id >> agent = agent (left identity)."""
       composed = sequential(ID, my_agent)
       _, direct = my_agent.invoke("ready", input_val)
       _, composed_result = composed.invoke(("ready", "ready"), input_val)
       assert direct == composed_result
   ```

---

## Composition Laws

Polynomial agents must satisfy categorical laws:

| Law | Requirement | Test |
|-----|-------------|------|
| **Identity** | `Id >> f = f = f >> Id` | Compose with identity, verify same output |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | Reorder composition, verify same output |

These are verified in `impl/claude/agents/operad/_tests/test_properties.py`.

---

## Integration with Existing Architecture

### Using Primitives

Polynomial agents can compose the 17 primitives from `agents/poly/primitives.py`:

```python
from agents.poly import GROUND, JUDGE, SUBLATE, SublateState

# Example: Alethic agent composes primitives
def alethic_transition(state, input):
    match state:
        case AlethicState.GROUNDING:
            _, grounded = GROUND.invoke(GroundState.FLOATING, input)
            return AlethicState.DELIBERATING, grounded
        case AlethicState.JUDGING:
            _, verdict = JUDGE.invoke(JudgeState.DELIBERATING, claim)
            return AlethicState.SYNTHESIZING, verdict
        # ...
```

### Converting to Bootstrap Agent

Use deprecation sugar for backwards compatibility:

```python
from agents.poly import to_bootstrap_agent, from_function

# Create polynomial
poly = from_function("Doubler", lambda x: x * 2)

# Convert to bootstrap Agent interface
agent = to_bootstrap_agent(poly)
result = await agent.invoke(21)  # Returns 42
```

---

## Examples in the Codebase

| Agent | File | States | Notes |
|-------|------|--------|-------|
| **Alethic** | `agents/a/alethic.py` | GROUNDING, DELIBERATING, JUDGING, SYNTHESIZING | Composes GROUND, JUDGE, SUBLATE |
| **Soul** | `agents/k/polynomial.py` | 7 eigenvector contexts | Maps to SOUL_SHEAF |
| **Memory** | `agents/d/polynomial.py` | IDLE, LOADING, STORING, QUERYING, STREAMING, FORGETTING | Instance isolation pattern |
| **Evolution** | `agents/e/polynomial.py` | IDLE, SUN, MUTATE, SELECT, WAGER, INFECT, PAYOFF, COMPLETE | Thermodynamic cycle |

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Global state | Instances share memory | Use MemoryStore pattern with factory |
| Missing validation | Crashes on None/empty | Validate all inputs in transition |
| Extreme confidence | 0.0 or 1.0 breaks math | Use Bayesian smoothing |
| Skipping isolation tests | Bugs in production | Always test instance isolation |
| Violating category laws | Composition breaks | Write property-based tests |

---

## Cross-References

- **Spec**: `spec/architecture/polyfunctor.md`
- **Impl**: `impl/claude/agents/poly/`
- **Tests**: `impl/claude/agents/*/test_polynomial.py`
- **Plan**: `plans/architecture/polyfunctor.md`
- **Theory**: [Niu & Spivak, "Polynomial Functors"](https://arxiv.org/abs/2312.00990)
