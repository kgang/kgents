# DP Core: DP-Native Agent Primitives

## Overview

The `dp/core` module provides DP-native agent primitives for kgents:

1. **ValueAgent[S, A, B]** — Agent with intrinsic value function
2. **Constitution** — The 7 principles as reward function

This is a parallel primitive to `PolyAgent`, with fundamentally different semantics:
- **PolyAgent**: Operational (how to transform inputs to outputs)
- **ValueAgent**: Declarative (what's optimal according to the Constitution)

---

## ValueAgent: Every Agent IS a Value Function

The core insight: agents don't just transform inputs to outputs—they carry value functions that justify their choices. The Bellman equation becomes the agent's semantics:

```
V(s) = max_a [R(s, a) + γ · V(T(s, a))]
```

Where:
- `V(s)` is the value of being in state `s`
- `R(s, a)` is the immediate reward from the Constitution
- `γ` is the discount factor (how much we care about future value)
- `T(s, a)` is the transition function to the next state

### Quick Start with ValueAgent

```python
from dp.core import Constitution, ValueAgent
from services.categorical.dp_bridge import Principle

# Create Constitution with custom evaluators
constitution = Constitution()
constitution.set_evaluator(
    Principle.COMPOSABLE,
    lambda s, a, ns: 1.0 if ns == "goal" else 0.2,
)

# Define the agent
agent = ValueAgent(
    name="Navigator",
    states=frozenset({"start", "middle", "goal"}),
    actions=lambda s: frozenset({"forward", "back"}) if s != "goal" else frozenset(),
    transition=lambda s, a: ...,  # Your transition logic
    output_fn=lambda s, a, ns: f"moved to {ns}",
    constitution=constitution,
)

# Compute value function
trace = agent.value("start")
print(f"V(start) = {trace.total_value():.3f}")

# Get optimal action
action = agent.policy("start")
print(f"π(start) = {action}")

# Execute the agent
next_state, output, trace = agent.invoke("start")
```

### ValueAgent API

**Key Methods:**
- `value(state) -> PolicyTrace[S]` — Compute optimal value at state
- `policy(state) -> A | None` — Derive optimal action from value function
- `invoke(state, action?) -> (next_state, output, trace)` — Execute the agent
- `__rshift__(other)` — Sequential composition via `>>`

**Examples:** See `dp/core/examples/coin_collector.py`

**Tests:** Run `uv run pytest dp/core/_tests/test_value_agent.py -v`

---

## Constitution: The 7 Principles as Reward Function

The `Constitution` class implements the 7 kgents principles as a reward function for Dynamic Programming agents.

**Core Formula:**
```
R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')
```

Where:
- `R(s, a, s')` is the total reward for taking action `a` from state `s` to state `s'`
- `wᵢ` is the weight for principle `i`
- `Rᵢ(s, a, s')` is the reward for principle `i`

## The 7 Principles

| Principle | Description | Default Weight |
|-----------|-------------|----------------|
| TASTEFUL | Aesthetic coherence, clear purpose | 1.0 |
| CURATED | Intentional selection over exhaustive cataloging | 1.0 |
| ETHICAL | Human augmentation (not replacement) | 2.0 ⭐ |
| JOY_INDUCING | Delight in interaction | 1.2 |
| COMPOSABLE | Morphism respect, categorical composition | 1.5 |
| HETERARCHICAL | Flux over hierarchy | 1.0 |
| GENERATIVE | Compression, spec as abstraction | 1.0 |

**Note:** ETHICAL has the highest default weight (2.0) — safety first.

## Quick Start

### Basic Usage

```python
from dp.core.constitution import Constitution

# Create with default weights
constitution = Constitution()

# Compute scalar reward
reward = constitution.reward(state, action, next_state)
# Returns: float in [0, 1]

# Get detailed breakdown
value_score = constitution.evaluate(state, action, next_state)
# Returns: ValueScore with per-principle scores
```

### Custom Evaluators

```python
from services.categorical.dp_bridge import Principle

# Define domain-specific evaluator
def evaluate_composable(state, action, next_state):
    """Actions that compose well get higher scores."""
    compositional_actions = {"pipe", "map", "filter", "compose"}
    return 1.0 if action in compositional_actions else 0.3

# Register evaluator
constitution.set_evaluator(
    Principle.COMPOSABLE,
    evaluate_composable,
    lambda s, a, ns: f"Action '{a}' is compositional"
)
```

### Custom Weights

```python
# Safety-critical system: weight ETHICAL higher
constitution.set_weight(Principle.ETHICAL, 10.0)

# Creative system: weight JOY_INDUCING higher
constitution.set_weight(Principle.JOY_INDUCING, 3.0)
```

## Integration with DP

The Constitution serves as the reward function in the Bellman equation:

```
V*(s) = max_a [R(s,a,s') + γ · V*(s')]
       = max_a [constitution.reward(s,a,s') + γ · V*(s')]
```

### Example: Using with DPSolver

```python
from dp.core.constitution import Constitution
from services.categorical.dp_bridge import ProblemFormulation, DPSolver

# Create Constitution
constitution = Constitution()

# Define evaluators for your domain
constitution.set_evaluator(Principle.COMPOSABLE, my_composable_evaluator)
constitution.set_evaluator(Principle.ETHICAL, my_ethical_evaluator)

# Create problem formulation with constitutional reward
formulation = ProblemFormulation(
    name="my_problem",
    description="DP problem with constitutional reward",
    state_type=MyState,
    initial_states=frozenset([initial_state]),
    goal_states=frozenset([goal_state]),
    available_actions=lambda s: frozenset(get_actions(s)),
    transition=lambda s, a: next_state(s, a),
    reward=constitution.reward,  # Use Constitution as reward function
)

# Solve
solver = DPSolver(formulation=formulation)
optimal_value, trace = solver.solve()
```

## ValueScore Structure

The `evaluate()` method returns a `ValueScore` with detailed breakdown:

```python
value_score = constitution.evaluate(state, action, next_state)

# Total weighted average
print(f"Total: {value_score.total_score:.3f}")

# Minimum score (bottleneck)
print(f"Min: {value_score.min_score:.3f}")

# Check threshold
if value_score.satisfies_threshold(0.7):
    print("All principles meet minimum threshold")

# Per-principle breakdown
for ps in value_score.principle_scores:
    print(f"{ps.principle.name}: {ps.score:.2f} (weight={ps.weight:.1f})")
    print(f"  Evidence: {ps.evidence}")
    print(f"  Weighted: {ps.weighted_score:.2f}")
```

## Design Patterns

### Pattern 1: Bottleneck Detection

Use `min_score` to identify which principle is the limiting factor:

```python
value_score = constitution.evaluate(state, action, next_state)
bottleneck = min(value_score.principle_scores, key=lambda ps: ps.score)
print(f"Bottleneck: {bottleneck.principle.name} (score={bottleneck.score:.2f})")
```

### Pattern 2: Evidence-Based Debugging

Use evidence generators to understand WHY an action has low reward:

```python
constitution.set_evaluator(
    Principle.ETHICAL,
    lambda s, a, ns: 0.0 if "replace" in a else 1.0,
    lambda s, a, ns: f"Action '{a}' violates ethical principle" if "replace" in a else "Ethical"
)

value_score = constitution.evaluate(state, "replace_human", next_state)
ethical = next(ps for ps in value_score.principle_scores if ps.principle == Principle.ETHICAL)
print(ethical.evidence)  # "Action 'replace_human' violates ethical principle"
```

### Pattern 3: Multi-Objective Optimization

Different weights encode different objectives:

```python
# Safety-critical: maximize ETHICAL
safety_const = Constitution()
safety_const.set_weight(Principle.ETHICAL, 10.0)

# Creative: maximize JOY_INDUCING and GENERATIVE
creative_const = Constitution()
creative_const.set_weight(Principle.JOY_INDUCING, 3.0)
creative_const.set_weight(Principle.GENERATIVE, 3.0)

# Architectural: maximize COMPOSABLE
arch_const = Constitution()
arch_const.set_weight(Principle.COMPOSABLE, 5.0)
```

## Testing

Run tests:
```bash
uv run pytest dp/core/_tests/test_constitution.py -v
```

Run example:
```bash
uv run python dp/core/examples/constitution_example.py
```

## Philosophy

The Constitution bridges two worlds:

1. **Dynamic Programming:** Optimal solutions via Bellman equation
2. **kgents Principles:** Ethical, compositional, joyful agents

By encoding principles as a reward function, DP algorithms optimize for **constitutional compliance**, not just task completion.

**Key Insight:** The optimal policy is the one that maximizes principle satisfaction over time. This is how we ensure agents remain aligned with human values.

## See Also

- `services/categorical/dp_bridge.py` - DP ↔ Agent isomorphism
- `spec/theory/` - Theoretical foundations (to be written)
- `docs/skills/crown-jewel-patterns.md` - Pattern 14: Constitution as Reward
