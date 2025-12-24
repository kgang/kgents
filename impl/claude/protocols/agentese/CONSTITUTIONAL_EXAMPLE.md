# Constitutional Node Example

This example demonstrates how to use `@node(constitutional=True)` to integrate
DP reward functions with AGENTESE nodes.

## Basic Usage

```python
from protocols.agentese.node import BaseLogosNode, BasicRendering
from protocols.agentese.registry import node

@node("world.house.manifest", constitutional=True)
class HouseManifestNode(BaseLogosNode):
    """House manifestation with constitutional evaluation."""

    @property
    def handle(self) -> str:
        return "world.house.manifest"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("build", "demolish", "renovate")

    async def manifest(self, observer, **kwargs):
        return BasicRendering(
            summary="House blueprint",
            content="A tastefully designed house"
        )

    async def _invoke_aspect(self, aspect, observer, **kwargs):
        if aspect == "build":
            return {"status": "built", "quality": "high"}
        raise NotImplementedError(f"Aspect {aspect} not implemented")
```

## What Happens

When `constitutional=True`:

1. **Every invocation** evaluates against the Constitution (7 principles)
2. **TraceEntry emitted** with principle scores for each action
3. **Logged automatically** at INFO level for monitoring

Example log output:

```
INFO Constitutional invocation: world.house.manifest.build ->
     value=0.543 (min=0.500)
```

## Custom Principle Evaluators

Override `_get_value_function()` to provide custom scoring:

```python
from services.categorical import ValueFunction, Principle

@node("world.house.manifest", constitutional=True)
class CustomHouseNode(HouseManifestNode):
    def _get_value_function(self):
        """Custom evaluator favoring tasteful designs."""

        def tasteful_eval(agent_name, state, action):
            # Give high scores to "build" with good design
            if "build" in agent_name:
                return 1.0  # Highly tasteful
            return 0.5  # Neutral

        return ValueFunction(
            principle_evaluators={
                Principle.TASTEFUL: tasteful_eval,
                Principle.JOY_INDUCING: lambda n, s, a: 0.8,
            }
        )
```

## Integration Points

### Current (Minimal Bridge)

- Emits logs with principle scores
- Uses default neutral scoring (0.5) for all principles
- State captured as hashable string for caching

### Future Enhancements

- Store TraceEntry in PolicyTrace for Witness integration
- Inject custom ValueFunction via DI container
- Emit scores to telemetry/metrics
- Use for auto-analysis and drift detection

## When to Use

Use `constitutional=True` when:

- **Actions have ethical implications** (mutations, deletions)
- **You want audit trails** of principle satisfaction
- **Building new features** where principle adherence matters
- **Experimenting with DP Bridge** patterns

Don't use for:

- Pure read operations (manifest, search)
- High-frequency, low-stakes invocations
- Performance-critical paths (adds small overhead)

## Philosophy

> "The proof IS the decision. The mark IS the witness."

Constitutional nodes make principle adherence **explicit and traceable**.
Every action emits evidence of alignment with the 7 core principles.

This is the bridge between:
- **Dynamic Programming** (reward functions, value iteration)
- **Agent Composition** (operad operations, sheaf gluing)
- **Constitutional AI** (principle-based evaluation)

## See Also

- `services/categorical/dp_bridge.py` - Full DP Bridge implementation
- `services/categorical/README.md` - Categorical reasoning theory
- `docs/theory/dp-agent-isomorphism.md` - Mathematical foundations
