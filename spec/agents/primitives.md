# Agent Primitives: The 17 Atomic Agents

> *"From 17 atoms, all agents emerge."*

## Status

**Version**: 1.0
**Status**: Canonical
**Implementation**: `impl/claude/agents/poly/primitives.py`
**Tests**: Verified via `test_primitives.py`

## Overview

Primitives are the irreducible building blocks from which all other agents are composed via operad operations. Each primitive is a `PolyAgent` with well-defined:

- **Positions**: States the agent can occupy
- **Directions**: Valid inputs per state
- **Transitions**: State × Input → (State, Output)

## Primitive Categories

| Category | Count | Purpose |
|----------|-------|---------|
| **Bootstrap** | 7 | Core composition and logic |
| **Perception** | 3 | Observer-dependent interaction |
| **Entropy** | 3 | Accursed Share / void.* |
| **Memory** | 2 | D-gent persistence |
| **Teleological** | 2 | Evolve + Narrate primitives |

---

## Bootstrap Primitives (7)

### 1. ID (Identity)

The identity morphism—passes input through unchanged.

```python
ID: PolyAgent[str, Any, Any]
  positions: {"ready"}
  directions: λs → {Any}
  transition: λ(s, x) → ("ready", x)
```

**Role**: Unit for sequential composition. `seq(id, a) = a = seq(a, id)`.

### 2. GROUND

Grounds queries to factual basis.

```python
GROUND: PolyAgent[GroundState, Any, dict]
  positions: {GROUNDED, FLOATING}
  directions: λs → {Any}
  transition: λ(s, x) → (GROUNDED|FLOATING, {grounded: bool, content: x})
```

**State Machine**:
```
FLOATING --[valid input]--> GROUNDED
FLOATING --[invalid input]--> FLOATING
```

### 3. JUDGE

Evaluates claims and renders verdicts.

```python
JUDGE: PolyAgent[JudgeState, Claim, Verdict]
  positions: {DELIBERATING, DECIDED}
  directions: λs → {Claim} if s == DELIBERATING else {}
  transition: λ(s, claim) → (DECIDED, Verdict(claim, accepted, reasoning))
```

**Types**:
```python
@dataclass(frozen=True)
class Claim:
    content: str
    confidence: float = 0.5

@dataclass(frozen=True)
class Verdict:
    claim: Claim
    accepted: bool
    reasoning: str
```

### 4. CONTRADICT

Generates antithesis from thesis (Hegelian dialectic).

```python
CONTRADICT: PolyAgent[ContradictState, Thesis, Antithesis]
  positions: {SEEKING, FOUND}
  directions: λs → {Thesis}
  transition: λ(s, thesis) → (FOUND, Antithesis(thesis, contradiction))
```

### 5. SUBLATE

Synthesizes thesis and antithesis (Aufhebung).

```python
SUBLATE: PolyAgent[SublateState, (Thesis, Antithesis), Synthesis]
  positions: {ANALYZING, SYNTHESIZED}
  directions: λs → {tuple}
  transition: λ(s, (t, a)) → (SYNTHESIZED, Synthesis(t, a, resolution))
```

**Dialectical Pattern**:
```
Thesis --[contradict]--> Antithesis --[sublate]--> Synthesis
```

### 6. COMPOSE

Meta-composition primitive (actual composition happens in operad).

```python
COMPOSE: PolyAgent[str, Any, Any]
  positions: {"ready"}
  directions: λs → {Any}
  transition: λ(s, pair) → ("ready", pair)
```

### 7. FIX

Fixed-point / retry primitive.

```python
FIX: PolyAgent[FixState, (Any, int), dict]
  positions: {TRYING, SUCCEEDED, FAILED}
  directions: λs → {Any} if s == TRYING else {}
  transition: λ(s, (value, retries)) → ...
```

**State Machine**:
```
TRYING --[success]--> SUCCEEDED
TRYING --[failure, retries < 3]--> TRYING
TRYING --[failure, retries >= 3]--> FAILED
```

---

## Perception Primitives (3)

### 8. MANIFEST

Observer-dependent perception (AGENTESE `*.manifest`).

```python
MANIFEST: PolyAgent[str, (Handle, Umwelt), Manifestation]
  positions: {"observing"}
  directions: λs → {tuple}
  transition: λ(s, (handle, umwelt)) → ("observing", Manifestation(...))
```

**Key Types**:
```python
@dataclass(frozen=True)
class Handle:
    path: str           # AGENTESE path
    entity: Any = None

@dataclass(frozen=True)
class Umwelt:
    observer_type: str
    capabilities: FrozenSet[str] = frozenset()

@dataclass(frozen=True)
class Manifestation:
    handle: Handle
    umwelt: Umwelt
    perception: Any     # Observer-dependent result
```

**AGENTESE Integration**:
```python
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

### 9. WITNESS

Trace recording and replay (N-gent foundation).

```python
WITNESS: PolyAgent[WitnessState, Any, Trace]
  positions: {RECORDING, REPLAYING}
  directions: λs → {Any} if RECORDING else {"replay", Any}
  transition: λ(s, x) → (state, Trace(events, timestamp))
```

**Types**:
```python
@dataclass(frozen=True)
class Trace:
    events: tuple[Any, ...]
    timestamp: float = 0.0
```

### 10. LENS

Composable sub-agent extraction (bidirectional).

```python
LENS: PolyAgent[str, Any, Any]
  positions: {"ready"}
  directions: λs → {Any}
  transition: λ(s, selector) → ("ready", selector)
```

**Future**: Will support get/set semantics for sub-agent views.

---

## Entropy Primitives (3)

These primitives interact with the **Accursed Share** (void.* context).

### 11. SIP

Draw entropy from the void (AGENTESE `void.entropy.sip`).

```python
SIP: PolyAgent[SipState, EntropyRequest, EntropyGrant]
  positions: {THIRSTY, SATED}
  directions: λs → {EntropyRequest} if THIRSTY else {}
  transition: λ(s, req) → (SATED, EntropyGrant(random * req.amount))
```

**Types**:
```python
@dataclass(frozen=True)
class EntropyRequest:
    amount: float = 0.5  # 0-1 scale

@dataclass(frozen=True)
class EntropyGrant:
    value: float
    source: str = "void.entropy"
```

### 12. TITHE

Pay gratitude to the void (AGENTESE `void.gratitude.tithe`).

```python
TITHE: PolyAgent[TitheState, Offering, dict]
  positions: {OWING, PAID}
  directions: λs → {Offering} if OWING else {}
  transition: λ(s, offering) → (PAID, {tithed: True, ...})
```

**Types**:
```python
@dataclass(frozen=True)
class Offering:
    content: Any
    gratitude_level: float = 0.5
```

### 13. DEFINE

Autopoietic creation (AGENTESE `void.define`).

```python
DEFINE: PolyAgent[str, Spec, Definition]
  positions: {"creating"}
  directions: λs → {Spec}
  transition: λ(s, spec) → ("creating", Definition(spec, created, message))
```

**Types**:
```python
@dataclass(frozen=True)
class Spec:
    name: str
    signature: str
    behavior: str

@dataclass(frozen=True)
class Definition:
    spec: Spec
    created: bool
    message: str
```

---

## Memory Primitives (2)

Foundation for D-gent (Data Agent).

### 14. REMEMBER

Persist to memory.

```python
REMEMBER: PolyAgent[RememberState, Memory, MemoryResult]
  positions: {IDLE, STORING, STORED}
  directions: λs → {Memory} if s != STORED else {}
  transition: λ(s, memory) → (STORED, MemoryResult(key, success, content))
```

### 15. FORGET

Remove from memory.

```python
FORGET: PolyAgent[ForgetState, str, MemoryResult]
  positions: {IDLE, FORGETTING, FORGOTTEN}
  directions: λs → {str} if s != FORGOTTEN else {}
  transition: λ(s, key) → (FORGOTTEN, MemoryResult(key, success, None))
```

**Shared Types**:
```python
@dataclass(frozen=True)
class Memory:
    key: str
    content: Any
    timestamp: float = 0.0

@dataclass(frozen=True)
class MemoryResult:
    key: str
    success: bool
    message: str
    content: Any = None
```

---

## Teleological Primitives (2)

Foundation for evolution and narrative patterns.
Note: Originally designed for E-gent (Evolution, archived 2025-12-16) and N-gent (Narrative).

### 16. EVOLVE

Teleological evolution step.

```python
EVOLVE: PolyAgent[EvolveState, Organism, Evolution]
  positions: {DORMANT, MUTATING, SELECTING, CONVERGED}
  directions: λs → {Organism} if s != CONVERGED else {}
  transition: λ(s, organism) → (new_state, Evolution(...))
```

**State Machine**:
```
DORMANT --[init]--> MUTATING
MUTATING --[mutate]--> SELECTING
SELECTING --[low fitness]--> MUTATING
SELECTING --[high fitness]--> CONVERGED
```

**Types**:
```python
@dataclass(frozen=True)
class Organism:
    genome: tuple[Any, ...]
    fitness: float = 0.0
    generation: int = 0

@dataclass(frozen=True)
class Evolution:
    organism: Organism
    mutation_applied: bool
    selected: bool
    message: str
```

### 17. NARRATE

Construct story from events (N-gent witness).

```python
NARRATE: PolyAgent[NarrateState, tuple[Any, ...], Story]
  positions: {LISTENING, COMPOSING, TOLD}
  directions: λs → {tuple} if s != TOLD else {}
  transition: λ(s, events) → (TOLD, Story(title, events, moral))
```

**Types**:
```python
@dataclass(frozen=True)
class Story:
    title: str
    events: tuple[Any, ...]
    moral: str
    narrator: str = "witness"
```

---

## Registry API

```python
from agents.poly.primitives import (
    PRIMITIVES,      # Dict[str, PolyAgent]
    get_primitive,   # (name: str) → PolyAgent | None
    all_primitives,  # () → list[PolyAgent]
    primitive_names, # () → list[str]
)
```

---

## Cross-References

- **Polyfunctor Architecture**: `spec/architecture/polyfunctor.md`
- **Operads**: `spec/agents/operads.md`
- **AGENTESE Spec**: `spec/protocols/agentese.md`
- **Implementation**: `impl/claude/agents/poly/primitives.py`
