# Witness Crown Jewel as DP Formulation

The Witness witnesses itself via Dynamic Programming: every tracing decision is itself traced through PolicyTrace.

## Overview

This module defines the Witness Crown Jewel as a Markov Decision Process (MDP) where the optimal policy maximizes auditability while minimizing trace overhead.

**The Self-Referential Aspect**: The Witness watches itself witness. Every decision (MARK, SKIP, CRYSTALLIZE) is recorded in the PolicyTrace, which IS the witness of the witnessing process.

## Structure

```
dp/jewels/witness/
├── __init__.py              - Public API exports
├── formulation.py           - MDP definition and ValueAgent constructor
├── example_self_witness.py  - Demonstration of self-witnessing
├── README.md                - This file
└── _tests/
    └── test_formulation.py  - Comprehensive tests
```

## State Space

```python
class WitnessState(Enum):
    IDLE          # Not actively witnessing
    OBSERVING     # Watching for significant events
    MARKING       # Recording a mark
    CRYSTALLIZING # Promoting marks to crystal
    QUERYING      # Retrieving past marks
```

Valid transitions:
- `IDLE --[OBSERVE]--> OBSERVING`
- `OBSERVING --[MARK]--> MARKING`
- `OBSERVING --[SKIP]--> IDLE`
- `OBSERVING --[QUERY]--> QUERYING`
- `MARKING --[CRYSTALLIZE]--> CRYSTALLIZING`
- `MARKING --[OBSERVE]--> OBSERVING`
- `CRYSTALLIZING --[OBSERVE]--> OBSERVING`
- `QUERYING --[OBSERVE]--> OBSERVING`

## Action Space

```python
class WitnessAction(Enum):
    OBSERVE     # Start/continue observation
    MARK        # Emit a mark
    SKIP        # Decide event not worth marking
    CRYSTALLIZE # Promote to crystal
    QUERY       # Search past marks
```

## Reward Function

Based on the 7 kgents principles:

| Principle | Metric | How It's Rewarded |
|-----------|--------|-------------------|
| **GENERATIVE** | Compression ratio | CRYSTALLIZE gets high reward; too many MARKs get penalty |
| **ETHICAL** | Auditability | MARK significant events rewarded; SKIP significant events penalized |
| **JOY_INDUCING** | Discovery potential | QUERY (by relevance) and CRYSTALLIZE (emergent insight) |
| **COMPOSABLE** | Trace coherence | Actions that build coherent trace get bonus |
| **TASTEFUL** | Signal-to-noise ratio | MARK signal rewarded, MARK noise penalized |
| **CURATED** | Intentionality | Explicit decisions (MARK, CRYSTALLIZE, SKIP) get bonus |
| **HETERARCHICAL** | Flexibility | Actions that maintain options get bonus |

See `formulation.py::witness_reward()` for implementation.

## Usage

### Basic: Create a Witness Agent

```python
from dp.jewels.witness import create_witness_agent, WitnessState

# Create agent with optimal tracing policy
agent = create_witness_agent(gamma=0.95)

# Get optimal action from current state
action = agent.policy(WitnessState.OBSERVING)
print(f"Optimal action: {action.name}")

# Execute the action
next_state, output, trace = agent.invoke(WitnessState.OBSERVING, action)
print(f"Next state: {next_state.name}")
print(f"Trace: {trace}")
```

### With Context

Context allows you to influence the reward function based on current situation:

```python
from dp.jewels.witness import WitnessContext, create_witness_agent

# High-significance event, few marks so far
context = WitnessContext(
    event_significance=0.9,  # Very significant event
    mark_count=3,            # Only 3 marks so far
    insight_density=0.7,     # Good insight-to-mark ratio
    trace_coherence=0.8,     # Marks compose well
)

agent = create_witness_agent(context=context)
action = agent.policy(WitnessState.OBSERVING)
# Likely to be MARK (high significance, low mark count)
```

### Value Function

Compute the optimal long-term value from any state:

```python
agent = create_witness_agent()

# What's the value of being in OBSERVING state?
trace = agent.value(WitnessState.OBSERVING)
value = trace.total_value()

print(f"Value of OBSERVING: {value:.3f}")
```

### Run the Example

```bash
uv run python -m dp.jewels.witness.example_self_witness
```

This demonstrates:
1. The Witness making optimal decisions across events of varying significance
2. PolicyTrace recording every decision (witnessing the witness)
3. Optimal policy adapting to different contexts
4. Value function showing expected long-term principle satisfaction

## Tests

Run the test suite:

```bash
uv run pytest dp/jewels/witness/_tests/ -v
```

Tests verify:
- State transitions follow the witnessing process
- Actions are appropriately restricted by state
- Reward function aligns with the 7 principles
- ValueAgent produces sensible policies
- Self-referential witnessing works (PolicyTrace captures decisions)

## Key Insights

### 1. The Witness IS a Value Function

Every ValueAgent carries a value function `V(s)` that tells us the expected long-term principle satisfaction from state `s`. The Witness agent's value function encodes optimal tracing policy.

### 2. The Proof IS the Decision

The PolicyTrace is not just a log—it's the PROOF of optimality. Every entry justifies why that action was chosen (via the Bellman equation). The trace IS the witness.

### 3. Self-Referential Bottoming Out

The Witness watches itself witness, creating infinite regress:
- Witness makes decision → PolicyTrace records it
- Recording is itself a witnessing decision → PolicyTrace records that
- Recording the recording is... → PolicyTrace monad handles this elegantly

The monad structure (Writer monad) makes the infinite regress safe and productive.

### 4. Principle-Based Rewards

The reward function doesn't use arbitrary scores. Every reward component maps to one of the 7 kgents principles. This ensures optimal policies align with project values.

### 5. Context-Sensitive Optimization

The same state can have different optimal actions depending on context:
- High significance event + few marks → MARK
- Low significance event + many marks → SKIP
- Medium marks accumulated → CRYSTALLIZE

Context flows through `WitnessContext` to the reward function.

## Integration Points

### With Witness Crown Jewel

The DP formulation can guide actual Witness implementation:

```python
from dp.jewels.witness import create_witness_agent, WitnessContext
from services.witness import mark_event  # Hypothetical

# Create agent for decision-making
agent = create_witness_agent()

# When an event occurs
context = WitnessContext(event_significance=compute_significance(event))
action = agent.policy(current_state, context=context)

if action == WitnessAction.MARK:
    mark_event(event)
elif action == WitnessAction.SKIP:
    pass  # Don't record
elif action == WitnessAction.CRYSTALLIZE:
    crystallize_marks()
```

### With PolicyTrace → Witness Marks

PolicyTrace entries can be converted to Witness marks:

```python
trace = agent.value(state)
marks = trace.to_marks()  # PolicyTrace has .to_marks() method
# Each mark contains: action, state_before, state_after, value, rationale
```

### With Constitution

The WitnessFormulation uses Constitution to evaluate principle satisfaction:

```python
from dp.core import Constitution
from services.categorical.dp_bridge import Principle

constitution = Constitution()
constitution.set_evaluator(
    Principle.ETHICAL,
    lambda s, a, ns: 1.0 if a == WitnessAction.MARK else 0.5,
)

agent = create_witness_agent(constitution=constitution)
```

## Philosophy

> "The proof IS the decision. The mark IS the witness."

Every DP step emits a Mark. The PolicyTrace IS the solution.

The Witness watches itself witness, creating infinite regress that bottoms out in the PolicyTrace monad. This is not a bug—it's a feature. The self-referential structure ensures that witnessing is witnessed all the way down.

## Future Directions

1. **Multi-Agent Witnessing**: Multiple Witness agents with different contexts (session-level, project-level, lifetime-level) coordinating through shared PolicyTrace.

2. **Adaptive Context**: Learn optimal `WitnessContext` parameters from past crystallizations. MetaDP: finding the best problem formulation.

3. **Stochastic Transitions**: Current transitions are deterministic. Could model uncertainty (e.g., "MARK might fail with 5% probability").

4. **Hierarchical Witnessing**: Witness agents at different scales (micro-decisions, macro-sessions, meta-projects) forming a hierarchy.

5. **Integration with K-gent**: Use K-gent's LLM capabilities to evaluate `event_significance` and `insight_density` dynamically.

## References

- `dp/core/value_agent.py` - ValueAgent implementation
- `dp/core/constitution.py` - Principle-based reward functions
- `services/categorical/dp_bridge.py` - DP-Agent isomorphism
- `spec/protocols/witness-primitives.md` - Witness specification
- `services/witness/` - Witness Crown Jewel implementation

---

*"Daring, bold, creative, opinionated but not gaudy"* — The Witness witnesses with taste.
