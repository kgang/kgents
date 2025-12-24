# Brain Crown Jewel as DP Formulation

Brain is the spatial cathedral of memory. As a DP problem: **optimal capture/recall policies**.

## Overview

This module formulates Brain's memory management as a Markov Decision Process (MDP), where the agent must balance:

- **Capturing** new memories (storage cost)
- **Recalling** existing memories (accuracy reward)
- **Forgetting** low-value memories (capacity management)
- **Consolidating** memories (compression)

The reward function maps directly to kgents principles:

- **COMPOSABLE**: Do memories compose coherently?
- **GENERATIVE**: Is storage efficient (compression ratio)?
- **JOY_INDUCING**: Are unexpected connections made (serendipity)?

## The MDP

**State**: `(memory_load, relevance_decay, query_pending)`
- `memory_load`: How full is memory (0.0-1.0)
- `relevance_decay`: How stale is recent context (0.0-1.0)
- `query_pending`: Is there an active query waiting? (bool)

**Actions**: `{CAPTURE, RECALL, FORGET, CONSOLIDATE, WAIT}`

**Reward**: Weighted sum of principle satisfaction
```
R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')
```

Where `wᵢ` is the weight for principle `i` and `Rᵢ` is the principle-specific score.

**Transition**: Deterministic state evolution based on action

## Quick Start

```python
from dp.jewels.brain import create_brain_agent, BrainState, BrainAction

# Create the Brain agent
brain = create_brain_agent(granularity=2)  # 2×2×2 = 8 states

# Examine a state
state = BrainState(memory_load=0.5, relevance_decay=0.3, query_pending=True)

# Check available actions
actions = brain.actions(state)
# → {CAPTURE, RECALL, FORGET, CONSOLIDATE, WAIT}

# Execute a transition (manual, no DP)
next_state = brain.transition(state, BrainAction.CONSOLIDATE)
output = brain.output_fn(state, BrainAction.CONSOLIDATE, next_state)
print(output)  # → "Brain: CONSOLIDATE (load 0.4, decay 0.0)"
```

## Example

Run the full example:

```bash
uv run python dp/jewels/brain/example_brain.py
```

This demonstrates:
1. State space generation
2. Action availability
3. State transitions
4. Constitution (reward function)
5. Manual transitions (without DP solving)

## Testing

Run the fast tests (recommended):

```bash
uv run pytest dp/jewels/brain/ -v -m "not slow"
```

Run all tests including slow DP solving tests:

```bash
uv run pytest dp/jewels/brain/ -v
```

## Implementation Notes

### Why is DP solving slow?

Brain has **no explicit goal state**—it's a continuous process of memory management. This means:

1. Value iteration runs through `max_depth` (default 100) iterations
2. All reachable states must be explored
3. Convergence depends on discount factor `gamma` (default 0.95)

For production use, consider:

- **Smaller granularity**: Fewer states = faster solving
- **Approximate methods**: Function approximation instead of tabular DP
- **Model-free RL**: Q-learning, policy gradients, actor-critic
- **Direct policy**: Hand-crafted policies based on domain knowledge

### State Space Discretization

Continuous variables (load, decay) are discretized into a grid:

- `granularity=2` → 2×2×2 = 8 states (fast)
- `granularity=3` → 3×3×2 = 18 states (slow)
- `granularity=5` → 5×5×2 = 50 states (very slow)

Higher granularity improves fidelity but increases computation exponentially.

### Principle Mapping

The reward function encodes Brain's design principles:

| Principle | Evaluator | Evidence |
|-----------|-----------|----------|
| **COMPOSABLE** | Rewards CONSOLIDATE (coherence), low decay (fresh context) | "Coherence: 0.90" |
| **GENERATIVE** | Rewards CONSOLIDATE (compression), low load (efficiency) | "Compression: 1.00" |
| **JOY_INDUCING** | Rewards RECALL in serendipity zone (moderate decay 0.3-0.7) | "Serendipity: 0.85" |

Unconfigured principles default to neutral (0.5) score.

## Files

- **`formulation.py`**: Core MDP definition (state, actions, transitions, rewards)
- **`__init__.py`**: Public API exports
- **`test_formulation.py`**: Comprehensive tests
- **`example_brain.py`**: Runnable example
- **`README.md`**: This file

## Integration

To integrate with the full Brain Crown Jewel:

1. Use this formulation for **policy optimization**
2. Bridge to actual memory operations via adapters
3. Project DP traces to UI/CLI via AGENTESE

See `services/brain/` for the full Crown Jewel implementation.

## See Also

- **`dp/core/value_agent.py`**: ValueAgent primitive
- **`dp/core/constitution.py`**: 7 principles as reward
- **`services/categorical/dp_bridge.py`**: DP ↔ Agent isomorphism
- **`spec/protocols/brain.md`**: Brain specification

---

*Created: 2025-12-24 | Part of the DP-native Crown Jewel formulation series*
