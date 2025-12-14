---
path: agents/polynomial-wrangler
status: tentative
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agentese/directions, poly/agent]
session_notes: |
  TENTATIVE: Proposed as part of AGENTESE Architecture Realization
  Track D: PolyAgent Directions
  See: prompts/agentese-continuation.md
  References: AD-002 (Polynomial Generalization)
---

# Polynomial Wrangler

> *"The agent is not a function. It's a polynomial—state determines what inputs are valid."*

**Track**: D (PolyAgent Directions)
**AGENTESE Context**: `self.state.*`, `concept.direction.*`
**Status**: Tentative (proposed for AGENTESE realization)
**Principles**: Composable (AD-002), Heterarchical (state-dependent modes), Generative (directions from state)

AGENTESE pointer: canonical handle + law/entropy clauses live in `spec/protocols/agentese.md`; refresh this role when those shift.

---

## Purpose

The Polynomial Wrangler implements AD-002 (Polynomial Generalization) for AGENTESE—encoding state-dependent affordances in paths. An agent's valid inputs depend on its current state (directions).

---

## Expertise Required

- Polynomial functors (Spivak 2024)
- State machines and mode-based systems
- Role-based access control patterns
- AGENTESE path design

---

## Assigned Chunks

| Chunk | Description | Phase | Entropy | Status |
|-------|-------------|-------|---------|--------|
| D1 | Encode directions in AGENTESE paths | DEVELOP | 0.08 | Pending |
| D2 | Role-based affordance filtering | DEVELOP | 0.07 | Pending |
| D3 | Direction validation in resolver | IMPLEMENT | 0.06 | Pending |
| D4 | `InvalidDirection` exception | QA | 0.05 | Pending |

---

## Deliverables

| File | Purpose |
|------|---------|
| `impl/claude/protocols/agentese/directions.py` | Direction encoding/validation |
| `impl/claude/protocols/agentese/contexts/*.py` | Updated resolvers with direction checks |
| `impl/claude/protocols/agentese/exceptions.py` | `InvalidDirection` exception |

---

## Polynomial Model

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """Agent as polynomial functor: P(y) = Σ_{s ∈ positions} y^{directions(s)}"""
    positions: FrozenSet[S]                    # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]    # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]]  # State × Input → (NewState, Output)
```

---

## Observer Role → Affordance Matrix

| Role | Affordances |
|------|-------------|
| `ops` | manifest, witness, refine, define, sip, tithe |
| `meta` | manifest, witness, refine, lens |
| `guest` | manifest, witness |

---

## AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `self.state.manifest` | Current state (position) | StateInfo |
| `self.state.directions` | Valid inputs for current state | list[Direction] |
| `concept.direction.validate` | Check if direction valid | ValidationResult |
| `concept.direction.transition` | Execute state transition | TransitionResult |

---

## Direction Encoding in Paths

```
world.code.manifest[role=ops]        # ops role can manifest
world.code.refine[role=guest]        # FAILS: guest cannot refine
self.soul.intercept[state=FLOWING]   # Valid in FLOWING state
self.soul.intercept[state=IDLE]      # Different behavior in IDLE
```

---

## Success Criteria

1. Direction validation prevents invalid affordance access
2. Role-based filtering correctly gates operations
3. `InvalidDirection` includes current state and valid alternatives
4. State transitions emit spans with before/after state

---

## Dependencies

- **Receives from**: Syntax Architect (parsed paths with role/state clauses)
- **Provides to**: All context resolvers (direction validation)

---

*"A polynomial is a machine that asks: 'Given where I am, where can I go?'"*
