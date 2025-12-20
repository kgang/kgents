# AD-002: Polynomial Generalization

**Date**: 2025-12-13

> Agents SHOULD generalize from `Agent[A, B]` to `PolyAgent[S, A, B]` where state-dependent behavior is required.

---

## Context

The categorical critique revealed that `Agent[A,B] ≅ A → B` is insufficient—real agents have **modes**. An agent that accepts different inputs based on its internal state cannot be modeled as a simple function. Polynomial functors (Spivak, 2024) capture this naturally.

## Decision

Agents with state-dependent behavior use `PolyAgent[S, A, B]`:

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """Agent as polynomial functor: P(y) = Σ_{s ∈ positions} y^{directions(s)}"""
    positions: FrozenSet[S]                    # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]    # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]]  # State × Input → (NewState, Output)
```

**Key insight**: `Agent[A, B]` embeds in `PolyAgent[Unit, A, B]`—traditional agents are single-state polynomials.

## Consequences

- K-gent uses `SOUL_POLYNOMIAL` with 7 eigenvector contexts as states
- D-gent uses `MEMORY_POLYNOMIAL` with IDLE/LOADING/STORING/QUERYING/FORGETTING states
- E-gent uses `EVOLUTION_POLYNOMIAL` with 8-phase thermodynamic cycle
- Composition via **wiring diagrams**, not just `>>` operator
- Operads define composition grammar programmatically

## The Three Layers

| Layer | Description | Purpose |
|-------|-------------|---------|
| **Primitives** | Atomic polynomial agents | Building blocks |
| **Operads** | Composition grammar | What combinations are valid |
| **Sheaves** | Gluing local → global | Emergence from composition |

## Anti-patterns

- Using `Agent[A, B]` when mode-dependent behavior is needed
- Scattered state checks instead of polynomial structure
- Composition without operad laws

## Implementation

See `docs/skills/polynomial-agent.md`, `impl/claude/agents/poly/`
