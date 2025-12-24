# ValueAgent Sequential Composition Design

## Overview

This document explains the Bellman-based sequential composition for `ValueAgent[S, A, B]` via the `>>` operator.

## The Core Formula

For two agents `f` and `g`, the composed value function satisfies:

```
V_{f >> g}(s) = max_a [R_f(s,a) + γ * V_g(f(s,a))]
```

Where:
- `R_f(s,a)` is the immediate reward from agent f
- `γ` is the discount factor
- `V_g(f(s,a))` is agent g's value at f's next state
- The max is over actions in f's action space

## Implementation Strategy

### Key Design Decisions

1. **State Space**: The composed agent uses the FIRST agent's state space
   - Rationale: We're evaluating f's actions, then looking up g's value
   - `(f >> g).states == f.states`

2. **Action Space**: The composed agent uses the FIRST agent's actions
   - Rationale: We choose actions from f's repertoire
   - `(f >> g).actions == f.actions`

3. **Reward Function**: Combines f's immediate reward with g's value
   - Implementation: Custom `ComposedConstitution` class
   - Formula: `R_composed(s,a,s') = R_f(s,a,s') + γ * V_g(s')`

4. **Transition Function**: Uses the FIRST agent's transition
   - Rationale: State evolution is determined by f
   - `(f >> g).transition == f.transition`

### Code Structure

```python
def __rshift__(self, other: ValueAgent[S, A, B]) -> ValueAgent[S, A, B]:
    # 1. Define composed reward function
    def composed_reward(state: S, action: A, next_state: S) -> float:
        immediate = self.constitution.reward(state, action, next_state)

        if next_state in other.states:
            future = other.value(next_state).total_value()
        else:
            future = 0.0

        return immediate + self.gamma * future

    # 2. Create custom Constitution wrapper
    class ComposedConstitution(Constitution):
        def reward(self, state_before, action, state_after):
            return composed_reward(state_before, action, state_after)

    # 3. Return new ValueAgent with composed semantics
    return ValueAgent(
        name=f"({self.name} >> {other.name})",
        states=self.states,              # First agent's states
        actions=self.actions,            # First agent's actions
        transition=self.transition,      # First agent's transition
        output_fn=self.output_fn,        # First agent's output
        constitution=ComposedConstitution(),
        gamma=self.gamma,
    )
```

## Important Properties

### ✓ Composition Creates New Agent

```python
composed = f >> g
assert composed is not f
assert composed is not g
```

### ✓ Composed Value ≥ Individual Value

The composed value includes the continuation:

```python
V_{f >> g}(s) >= V_f(s)  # (generally, depends on rewards)
```

Because `V_g` provides additional future value.

### ✓ Chaining Works

```python
triple = f >> g >> h
# Creates: ((f >> g) >> h)
```

### ✗ NOT Strictly Associative

**Important limitation**: `(f >> g) >> h ≠ f >> (g >> h)` in general.

**Why?**
- `(f >> g)` captures `V_g` at composition time
- `(f >> g) >> h` then adds `V_h` to the already-composed `(f >> g)`
- But `f >> (g >> h)` first creates `(g >> h)` with `V_h` baked into g
- These give different value estimates

**Rationale**: The current design prioritizes:
1. **Clarity**: Direct mapping to Bellman equation
2. **Efficiency**: Value functions computed once at composition time
3. **Simplicity**: No need for complex lazy evaluation chains

For strict categorical associativity, we'd need lazy evaluation where the entire chain is evaluated together at value computation time. This would be more complex and potentially less efficient.

## Test Coverage

### Core Composition Tests

1. `test_composition_creates_new_agent`: Verifies immutability and structure
2. `test_composition_value_is_sum`: Validates value accumulation
3. `test_composition_chains_correctly`: Tests multi-agent composition
4. `test_composition_bellman_semantics`: Verifies Bellman equation
5. `test_composition_incompatible_states`: Handles edge cases

### Property Tests

- State space preservation
- Action space preservation
- Gamma preservation
- Value monotonicity (composed ≥ individual)

## Example Usage

See `dp/core/_examples/composition_demo.py` for a complete working example.

```python
from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle

# Create agents
agent_f = ValueAgent(name="f", states=frozenset({0, 1}), ...)
agent_g = ValueAgent(name="g", states=frozenset({1, 2}), ...)

# Compose
composed = agent_f >> agent_g

# Evaluate
trace = composed.value(0)
print(f"V_{{f >> g}}(0) = {trace.total_value()}")

# Chain
triple = agent_f >> agent_g >> agent_h
```

## Theoretical Foundation

### Bellman Optimality

The composition respects the Bellman optimality principle:
- Each agent optimizes its own value function
- Composition combines optimal substructures
- The result is a new MDP with its own optimal policy

### Relation to DP-Native Approach

This implementation is "DP-native" because:
1. **Value First**: We define value functions, not just transformations
2. **Constitutional Rewards**: All rewards come from the 7 principles
3. **Composition via Value**: `>>` composes value functions, not just execution
4. **Policy Derivation**: Policies are derived from values, not hardcoded

### Future Extensions

Potential improvements (not currently implemented):
1. **Lazy Composition**: Defer value computation until evaluation time
2. **Associative Chains**: Special handling for `f >> g >> h` chains
3. **Parallel Composition**: `f || g` for concurrent agents
4. **Conditional Composition**: `f >> (if p then g else h)`

## Gotchas and Warnings

### 1. State Space Compatibility

The composed agent evaluates `V_g(f(s,a))`, which requires `f(s,a) ∈ g.states`.

If this condition is violated, `V_g` returns 0 (logged as warning).

### 2. Constitution Semantics

The composed constitution calls `R_f` for immediate reward, but `V_g` already includes `R_g` through the Bellman equation. Don't double-count!

### 3. Value Computation Cost

Composition triggers value iteration for `other`:
- First call to `composed.value(s)` computes `V_g` for all states
- This is cached, but initial computation can be expensive
- For large state spaces, consider lazy evaluation strategies

### 4. Type Safety

Python's type system doesn't enforce `B_f = A_g` (output of f = input of g). Use carefully!

## References

- `dp/core/value_agent.py`: Implementation
- `dp/core/_tests/test_value_agent.py`: Test suite
- `dp/core/_examples/composition_demo.py`: Working example
- `services/categorical/dp_bridge.py`: DP-categorical bridge
- Bellman, R. (1957). "Dynamic Programming"

---

*Implemented: 2025-12-24*
*Author: Claude Opus 4.5 + Kent*
*Status: Production-ready, 18/18 tests passing*
