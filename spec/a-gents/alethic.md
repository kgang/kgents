# Alethic Architecture: Deep Dive

> *"Truth is not a destination but a method."*

**Status**: Canonical
**Implementation**: `impl/claude/agents/a/`
**Theory**: Polynomial functors, Hegelian dialectics

---

## Overview

The Alethic Architecture is A-gent's core contribution: a **truth-preserving** framework for agent composition. Where other architectures focus on performance or scalability, alethic architecture focuses on **correctness guarantees**.

---

## The Philosophical Foundation

### Aletheia (ἀλήθεια)

Heidegger's concept of truth as "unconcealment"—truth isn't correspondence to facts but the *process* of disclosure. In kgents:

- **Grounding**: Claims meet reality
- **Deliberating**: Evidence weighs
- **Judging**: Verdicts emerge
- **Synthesizing**: Contradictions resolve

This isn't metaphor—it's the literal state machine in `AlethicAgent`.

### Dialectical Progression

The primitives `GROUND`, `JUDGE`, `SUBLATE` mirror Hegelian dialectics:

| Primitive | Dialectical Moment | Function |
|-----------|-------------------|----------|
| GROUND | Thesis | Validate claim against reality |
| JUDGE | Negation | Accept/reject with reasoning |
| SUBLATE | Synthesis | Aufheben—preserve and transcend |

---

## The Nucleus-Halo-Projector Triad

### Nucleus: Pure Logic

The nucleus is the irreducible `Agent[A, B]`—what the agent *does*:

```python
class MyAgent(Agent[Request, Response]):
    async def invoke(self, input: Request) -> Response:
        # This is the nucleus
        return process(input)
```

The nucleus knows nothing about deployment, scaling, or persistence. It's pure transformation.

### Halo: Declarative Capabilities

The halo describes what the agent *could become*—its potentialities:

```python
@Capability.Stateful(schema=MySchema)
@Capability.Observable(metrics=["latency", "errors"])
@Capability.Soulful(persona="analyst")
class MyAgent(Agent[Request, Response]):
    ...
```

Halos are metadata, not behavior. They're read by projectors.

### Projector: Manifestation

Projectors compile Nucleus + Halo into concrete deployment:

| Projector | Output | When |
|-----------|--------|------|
| K8sProjector | YAML manifests | `kg a manifest MyAgent` |
| LocalProjector | In-process | `kg a run MyAgent` |
| CLIProjector | Shell interface | Command-line |

```python
class K8sProjector:
    def project(self, agent: type[Agent], halo: Halo) -> str:
        """Generate Kubernetes YAML from Nucleus + Halo."""
        if halo.has(StatefulCapability):
            return self._generate_statefulset(agent, halo)
        else:
            return self._generate_deployment(agent, halo)
```

---

## The Alethic Agent (Polynomial)

### State Machine

```
┌────────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────────┐
│ GROUNDING  │ ──▶ │ DELIBERATING │ ──▶ │ JUDGING │ ──▶ │ SYNTHESIZING │
└────────────┘     └──────────────┘     └─────────┘     └──────────────┘
      ▲                                                         │
      └─────────────────────────────────────────────────────────┘
```

### Polynomial Semantics

This is a PolyAgent[AlethicState, Any, Any]:

```python
PolyAgent[S, A, B] = (
    positions: FrozenSet[S],           # {GROUNDING, DELIBERATING, ...}
    directions: S → FrozenSet[A],      # What inputs are valid at each state
    transition: S × A → (S, B)         # State machine transitions
)
```

### Direction Functions

Different states accept different inputs:

| State | Valid Inputs |
|-------|--------------|
| GROUNDING | Query |
| DELIBERATING | Evidence |
| JUDGING | DeliberationResult |
| SYNTHESIZING | Verdict |

This prevents invalid transitions at the type level.

### Usage

```python
from agents.a import AlethicAgent, Query

agent = AlethicAgent()
response = await agent.reason(Query(
    claim="The Earth orbits the Sun",
    context={"source": "heliocentrism"},
    confidence_threshold=0.7
))

print(response.verdict.accepted)       # True
print(response.final_confidence)       # 0.95
print(response.reasoning_trace)        # ["Grounded: ...", "Deliberated: ...", ...]
```

---

## The Functor Protocol

### Why Functors?

Functors let you lift operations across container types while preserving structure:

```python
# Instead of writing:
result1 = Option.map(lambda x: x + 1, Option.Some(5))
result2 = List.map(lambda x: x + 1, [1, 2, 3])

# You write once:
f = lift(lambda x: x + 1)
result1 = f(Option.Some(5))  # Some(6)
result2 = f([1, 2, 3])       # [2, 3, 4]
```

### Law Verification

The `UniversalFunctor` protocol verifies categorical laws at runtime:

```python
from agents.a import verify_functor, FunctorRegistry

# Register a functor
FunctorRegistry.register(MyFunctor)

# Verify it obeys laws
result = verify_functor(MyFunctor)
assert result.identity_passed
assert result.composition_passed
```

**Laws verified**:
1. **Identity**: `fmap(id) == id`
2. **Composition**: `fmap(f . g) == fmap(f) . fmap(g)`

---

## Archetypes

Archetypes are pre-packaged Halos for common patterns:

### Kappa (κ) — Stateless Service

```python
class MyService(Kappa[Request, Response]):
    """Horizontally scalable, stateless microservice."""
    async def invoke(self, req: Request) -> Response:
        return process(req)
```

Kappa implies:
- Stateless (no memory between invocations)
- Replicated (can run N instances)
- Horizontal scaling (load balance)

### Lambda (λ) — Event Function

```python
class MyFunction(Lambda[Event, Result]):
    """Triggered by events, ephemeral."""
    async def invoke(self, event: Event) -> Result:
        return handle(event)
```

Lambda implies:
- Event-triggered
- Short-lived
- Cold start acceptable

### Delta (δ) — Stateful Actor

```python
class MyActor(Delta[Message, Reply]):
    """Persistent state, exactly-once semantics."""
    async def invoke(self, msg: Message) -> Reply:
        self.state = update(self.state, msg)
        return Reply(ok=True)
```

Delta implies:
- Persistent state
- Exactly-once processing
- Virtual actors (Orleans-style)

---

## Integration with AGENTESE

AGENTESE paths map to alethic operations:

```python
# world.claim.ground → GROUND primitive
# world.claim.judge → JUDGE primitive
# world.claim.sublate → SUBLATE primitive
# world.claim.reason → Full AlethicAgent cycle
```

The Alethic Agent can be invoked via AGENTESE:

```python
await logos.invoke("world.claim.reason", observer, Query(claim="..."))
```

---

## Design Principles

### 1. Correctness Over Performance

The Alethic Architecture prioritizes truth-preservation over speed. If a composition would violate categorical laws, it's rejected—even if it would be faster.

### 2. Explicit State

Unlike implicit state machines, AlethicAgent's states are explicit positions in a polynomial. You can inspect `agent.state` at any time.

### 3. Composable Verification

Halos compose. If Agent A has `Stateful` and Agent B has `Observable`, their composition has both (via `merge_halos`).

### 4. Separation of Concerns

- Nucleus: What it does
- Halo: What it could become
- Projector: How it manifests

Each concern is independent and composable.

---

## Cross-References

- [core/skeleton.md](core/skeleton.md) — Minimal agent contract
- [../architecture/polyfunctor.md](../architecture/polyfunctor.md) — Polynomial theory
- [../agents/primitives.md](../agents/primitives.md) — 17 atomic agents
- [../protocols/agentese-as-route.md](../protocols/agentese-as-route.md) — AGENTESE integration

---

*"The ground upon which all agents stand."*
