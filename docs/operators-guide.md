# The Operator's Guide to kgents

> *"The garden knows its gardener. The system reflects its steward."*

This is a living document for Kent—developer, operator, user, consumer—to master his own creation. Agents may append suggestions to the **Stigmergic Surface** at the end.

---

## Table of Contents

1. [Philosophy: You Are the Observer](#philosophy-you-are-the-observer)
2. [Easy: Immediate Gratification](#easy-immediate-gratification)
3. [Medium: Compositional Power](#medium-compositional-power)
4. [Hard: Production Mastery](#hard-production-mastery)
5. [Scenarios: The Living Garden](#scenarios-the-living-garden)
6. [Quick Reference](#quick-reference)
7. [The Inner Game: Working with Your Own Eigenvectors](#the-inner-game-working-with-your-own-eigenvectors)
8. [Stigmergic Surface](#stigmergic-surface)

**Companion Document**: [Categorical Foundations](./categorical-foundations.md) — The mathematical and philosophical grounding

---

## Philosophy: You Are the Observer

In AGENTESE, there is no view from nowhere. When you invoke `world.house`, you don't get "a house"—you get a house *as you perceive it*. The architect sees blueprints; the poet sees metaphor; the economist sees appraisal.

As the operator of kgents, you are the privileged observer. The system unconceals itself to you differently than it would to an external user. You see:

- **The Nucleus**: Pure logic, the irreducible transform
- **The Halo**: Declared capabilities, potential waiting to manifest
- **The Projector**: The categorical compiler that makes potential actual

This guide teaches you to wield these three pillars fluently.

---

## Easy: Immediate Gratification

**Payoff**: Working agents in under 5 minutes. Zero configuration. Joy-inducing simplicity.

### Scenario 1: "What Can This Agent Do?"

You've inherited an agent class and want to understand its capabilities without reading the source.

```bash
# Inspect any agent's Halo
kgents a inspect Kappa

# Output:
# [A] Agent: Kappa
#
#   Archetype: Kappa
#
#   Capabilities:
#     @StatefulCapability(schema=dict, backend=auto)
#     @SoulfulCapability(persona=default, mode=advisory)
#     @ObservableCapability(mirror=True, metrics=True)
#     @StreamableCapability(budget=10.0, feedback=0.0)
#
#   Module: agents.a.archetypes
```

**The Insight**: You now know Kappa is the "full-stack" archetype—stateful, soulful, observable, streamable. Lambda is minimal (Observable only). Delta is data-focused (Stateful + Observable).

```bash
# Compare archetypes
kgents a list

# [A] Available Archetypes:
#
#   Kappa
#     Full-stack: Stateful + Soulful + Observable + Streamable
#
#   Lambda
#     Minimal: Observable only
#
#   Delta
#     Data-focused: Stateful + Observable
```

### Scenario 2: "Generate K8s Manifests Instantly"

You need to deploy an agent to Kubernetes. You don't want to write YAML.

```bash
# Generate manifests for any agent
kgents a manifest Kappa --namespace production > kappa-deployment.yaml

# Validate before applying
kgents a manifest Kappa --namespace production --validate
# [A] Generated 6 valid K8s resources
```

What you get: StatefulSet, PVC, Service, ServiceMonitor, HPA, ConfigMap—all with proper labels, probes, and resource limits.

```bash
# Inspect the JSON structure
kgents a manifest Kappa --json | jq '.manifests[].kind'
# "StatefulSet"
# "PersistentVolumeClaim"
# "Service"
# "ServiceMonitor"
# "HorizontalPodAutoscaler"
# "ConfigMap"
```

### Scenario 3: "Run an Agent Locally"

You've written a concrete agent and want to test it immediately.

```python
# my_agents/summarizer.py
from agents.a.archetypes import Lambda

class Summarizer(Lambda[str, str]):
    @property
    def name(self) -> str:
        return "summarizer"

    async def invoke(self, text: str) -> str:
        # Your summarization logic
        words = text.split()
        return " ".join(words[:10]) + "..." if len(words) > 10 else text
```

```bash
# Run it
kgents a run my_agents.Summarizer --input "The quick brown fox jumps over the lazy dog and runs away"
# [A] Compiled: Flux(summarizer)
# [A] Output: The quick brown fox jumps over the lazy dog and...
```

**The Payoff**: Zero ceremony. Write a class, run it. The LocalProjector handles wrapping.

---

## Medium: Compositional Power

**Payoff**: Multi-agent workflows. State that persists. Souls that govern. Streams that flow.

### Scenario 4: "The Stateful Accumulator"

You're building a metrics aggregator that accumulates events across invocations.

```python
# agents/metrics/accumulator.py
from dataclasses import dataclass, field
from agents.a.archetypes import Delta
from agents.a.halo import Capability

@dataclass
class MetricsState:
    count: int = 0
    total: float = 0.0
    events: list[str] = field(default_factory=list)

@Capability.Stateful(schema=MetricsState)  # Override Delta's dict schema
class MetricsAccumulator(Delta[float, dict]):
    """Accumulates metrics across invocations."""

    @property
    def name(self) -> str:
        return "metrics-accumulator"

    async def invoke(self, value: float) -> dict:
        # Note: State is managed by StatefulAdapter
        # Access via parent reference pattern (advanced)
        return {
            "received": value,
            "message": f"Accumulated {value}"
        }
```

```bash
# Inspect to confirm capability override
kgents a inspect agents.metrics.accumulator.MetricsAccumulator --json | jq '.capabilities'
# Shows MetricsState schema instead of dict
```

### Scenario 5: "The Governed Service"

You want K-gent personality to influence an agent's behavior—taste, restraint, the Categorical Imperative.

```python
# agents/creative/writer.py
from agents.a.archetypes import Kappa
from agents.a.halo import Capability

@Capability.Soulful(persona="Kent", mode="strict")  # Override default advisory
class CreativeWriter(Kappa[str, str]):
    """A writer governed by Kent's aesthetic sensibilities."""

    @property
    def name(self) -> str:
        return "creative-writer"

    async def invoke(self, prompt: str) -> str:
        # In strict mode, K-gent intercepts and may modify outputs
        # that violate eigenvector alignment (minimalism, depth, etc.)
        return f"[Draft] {prompt}"
```

**The Insight**: `mode="advisory"` annotates only. `mode="strict"` auto-resolves high-confidence violations. The SoulfulAdapter provides access to `persona` for consultation.

### Scenario 6: "The Living Pipeline"

You want to process a stream of events, not just single invocations.

```python
# agents/stream/transformer.py
from agents.a.archetypes import Kappa
from agents.a.halo import Capability

@Capability.Streamable(budget=20.0, feedback=0.1)  # High budget, some feedback
class EventTransformer(Kappa[dict, dict]):
    """Transforms events in a continuous stream."""

    @property
    def name(self) -> str:
        return "event-transformer"

    async def invoke(self, event: dict) -> dict:
        event["transformed"] = True
        event["timestamp"] = "now"
        return event
```

```python
# Usage in code
from system.projector import LocalProjector
import asyncio

async def main():
    projector = LocalProjector()
    compiled = projector.compile(EventTransformer)

    # compiled is a FluxAgent - it can process streams
    async def event_source():
        for i in range(100):
            yield {"id": i, "data": f"event-{i}"}

    async for result in compiled.start(event_source()):
        print(result)
        # {"id": 0, "data": "event-0", "transformed": True, "timestamp": "now"}

asyncio.run(main())
```

**The Payoff**: The `@Streamable` decorator with `feedback=0.1` enables ouroboric processing—10% of outputs feed back as inputs. The `budget=20.0` allows 20 entropy units before the stream collapses to Ground.

### Scenario 7: "Compose Agents with `>>`"

Agents are morphisms. They compose.

```python
from bootstrap.types import Agent

class Sanitizer(Agent[str, str]):
    @property
    def name(self) -> str:
        return "sanitizer"

    async def invoke(self, text: str) -> str:
        return text.strip().lower()

class Tokenizer(Agent[str, list[str]]):
    @property
    def name(self) -> str:
        return "tokenizer"

    async def invoke(self, text: str) -> list[str]:
        return text.split()

# Composition
pipeline = Sanitizer() >> Tokenizer()
# pipeline: Agent[str, list[str]]

result = await pipeline.invoke("  Hello World  ")
# ["hello", "world"]
```

**The Insight**: `>>` is morphism composition. `pipeline.name` is `"sanitizer >> tokenizer"`. The Alethic Architecture preserves this through lifting—`Flux.lift(a >> b)` equals `Flux.lift(a) >> Flux.lift(b)`.

---

## Hard: Production Mastery

**Payoff**: Custom archetypes. Multi-target deployment. Full categorical control.

### Scenario 8: "Define a Custom Archetype"

You've identified a pattern in your organization: services that need state, observability, and rate limiting, but NOT soul governance.

```python
# agents/org/archetypes.py
from typing import Generic, TypeVar
from agents.a.archetypes import Archetype
from agents.a.halo import Capability

A = TypeVar("A")
B = TypeVar("B")

@Capability.Stateful(schema=dict, backend="redis")
@Capability.Observable(mirror=True, metrics=True)
@Capability.Streamable(budget=5.0, feedback=0.0)
class Epsilon(Archetype[A, B], Generic[A, B]):
    """
    EPSILON: Rate-limited stateful service.

    Capabilities:
    - Stateful: Redis-backed state
    - Observable: Full Terrarium integration
    - Streamable: Rate-limited (budget=5.0)
    - NO Soulful: No persona governance

    Use when: Building internal services that need durability
    and observability but operate without personality.
    """
    pass
```

Now your team can use `Epsilon` as easily as `Kappa`:

```python
from agents.org.archetypes import Epsilon

class RateLimitedCache(Epsilon[str, str]):
    @property
    def name(self) -> str:
        return "rate-limited-cache"

    async def invoke(self, key: str) -> str:
        return f"cached:{key}"
```

### Scenario 9: "Multi-Environment Deployment"

The same agent, three environments, zero code changes.

```python
# agents/api/gateway.py
from agents.a.archetypes import Kappa

class APIGateway(Kappa[dict, dict]):
    @property
    def name(self) -> str:
        return "api-gateway"

    async def invoke(self, request: dict) -> dict:
        return {"status": "ok", "request_id": request.get("id")}
```

```bash
# Development: Run locally with SQLite state
kgents a run agents.api.gateway.APIGateway --input '{"id": "dev-123"}'

# Staging: Generate manifests for staging cluster
kgents a manifest agents.api.gateway.APIGateway \
  --namespace staging \
  --validate > staging-gateway.yaml
kubectl apply -f staging-gateway.yaml

# Production: Same manifests, different namespace
kgents a manifest agents.api.gateway.APIGateway \
  --namespace production \
  --validate > prod-gateway.yaml
kubectl apply -f prod-gateway.yaml
```

**The Isomorphism**: LocalProjector and K8sProjector produce semantically equivalent agents. The behavior is identical; only the substrate differs.

### Scenario 10: "The Functor Stack"

You want to understand and customize how capabilities compose.

```
Canonical Functor Ordering:

    Nucleus → D → K → Mirror → Flux
            (inner)        (outer)

When you compile a Kappa agent:
1. Nucleus: Your invoke() logic
2. D (Stateful): StatefulAdapter wraps nucleus, provides state
3. K (Soulful): SoulfulAdapter wraps stateful, provides persona
4. Mirror (Observable): Marked for Terrarium attachment
5. Flux (Streamable): FluxAgent wraps everything, enables streaming
```

To inspect the actual functor stack:

```python
from system.projector import LocalProjector
from agents.a.archetypes import Kappa

class MyService(Kappa[str, str]):
    @property
    def name(self) -> str:
        return "my-service"

    async def invoke(self, x: str) -> str:
        return x

projector = LocalProjector()
compiled = projector.compile(MyService)

# Peel the onion
print(f"Outer: {type(compiled).__name__}")  # FluxAgent
print(f"Next:  {type(compiled.inner).__name__}")  # SoulfulAdapter
print(f"Next:  {type(compiled.inner.inner).__name__}")  # StatefulAdapter
print(f"Core:  {type(compiled.inner.inner.inner).__name__}")  # MyService
```

### Scenario 11: "AGENTESE Path Integration"

Access agent capabilities through AGENTESE paths.

```python
from protocols.agentese import Logos

logos = Logos()

# Manifest an agent's state
state = await logos.invoke("self.agent.my-service.manifest", observer_umwelt)

# Future: Project via AGENTESE
# local_agent = await logos.invoke("self.agent.my-service.project.local", umwelt)
# k8s_manifests = await logos.invoke("self.agent.my-service.project.k8s", umwelt)
```

---

## Scenarios: The Living Garden

These are evocative scenarios that show the system's potential.

### "The Morning Ritual"

It's 6:47 AM. You open your terminal. The soul stirs.

```bash
# What's the garden's health?
kgents soul manifest

# Challenge the soul
kgents soul challenge "Should I refactor the authentication module today?"

# The soul responds with eigenvector-weighted advice:
# - Minimalism score: 0.15 (the current code is baroque)
# - Depth score: 0.85 (but it has earned its complexity)
# - Recommendation: "Simplify the interface, preserve the depths."
```

### "The Ambient Presence"

K-gent runs continuously, observing the codebase, perturbable but never intrusive.

```python
# In your Flux stream
from agents.k import KgentFlux

async def development_loop():
    kgent = KgentFlux()

    async for event in kgent.start(codebase_events()):
        if event.type == "drift_detected":
            # K-gent noticed implementation drifting from spec
            print(f"Drift: {event.file} violates {event.principle}")
        elif event.type == "suggestion":
            # Proactive suggestion based on observed patterns
            print(f"Consider: {event.suggestion}")
```

### "The Midnight Deploy"

It's 11:58 PM. Production is waiting. You trust the system.

```bash
# Generate, validate, deploy
kgents a manifest agents.api.critical.PaymentProcessor \
  --namespace production \
  --validate \
  | kubectl apply -f -

# The manifest includes:
# - StatefulSet with PVC for transaction state
# - K-gent sidecar for governance (mode=strict)
# - ServiceMonitor for Prometheus
# - HPA scaling from budget=10.0

# Watch it come alive
kubectl get pods -n production -w
# payment-processor-0   2/2   Running   (agent + kgent-sidecar)
```

### "The Terrarium Window"

You've attached a HolographicBuffer to your running FluxAgent. The Terrarium shows:

```
┌─────────────────────────────────────────────┐
│  payment-processor          ████████░░ 80%  │
│  ─────────────────────────────────────────  │
│  entropy: 7.2 / 10.0                        │
│  throughput: 142 events/sec                 │
│  state: FLOWING                             │
│  drift: none detected                       │
│                                             │
│  [pressure] ▁▂▃▅▆▇█▇▅▃▂▁  (last 60s)       │
│  [soul]     advisory: 3 | strict: 0         │
└─────────────────────────────────────────────┘
```

### "The Categorical Imperative in Action"

A junior developer submits code that violates the minimalism principle:

```python
# Their code
class OverEngineeredService(Kappa[str, str]):
    async def invoke(self, x: str) -> str:
        # 47 helper methods
        # 3 abstract factories
        # 2 visitor patterns
        return self._process_through_seventeen_layers(x)
```

K-gent (in strict mode) intercepts:

```
[K-gent] Governance Alert: OverEngineeredService
         Minimalism score: 0.02 (threshold: 0.10)

         The Categorical Imperative asks:
         "Could this complexity become a universal law?"

         Suggested: Reduce to single transform path.

         [Override] [Simplify] [Discuss]
```

---

## Quick Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `kgents a list` | List available archetypes |
| `kgents a inspect <agent>` | Show Halo + Nucleus details |
| `kgents a manifest <agent>` | Generate K8s YAML |
| `kgents a run <agent>` | Compile and run locally |
| `kgents soul manifest` | Show soul state |
| `kgents soul challenge <prompt>` | Query the soul |

### Flags

| Flag | Commands | Description |
|------|----------|-------------|
| `--json` | all | Output as JSON |
| `--namespace <ns>` | manifest | K8s namespace |
| `--validate` | manifest | Validate before output |
| `--input <data>` | run | Input for invocation |

### Archetypes

| Archetype | Capabilities | Use When |
|-----------|--------------|----------|
| `Kappa` | All four | Full-stack service agents |
| `Lambda` | Observable | Stateless functions |
| `Delta` | Stateful + Observable | Data pipelines |

### Functor Order

```
Nucleus → D (Stateful) → K (Soulful) → Mirror (Observable) → Flux (Streamable)
        (innermost)                                         (outermost)
```

---

## The Inner Game: Working with Your Own Eigenvectors

> *"K-gent doesn't add personality—it navigates to specific coordinates in the inherent personality-emotion manifold."*

As the operator, you have a unique privilege: K-gent is calibrated to YOU. Here's how to use that.

### Your Six Coordinates

| Eigenvector | Your Value | What This Means for Daily Work |
|-------------|------------|-------------------------------|
| **Aesthetic** | 0.15 (Minimalist) | Before adding anything, ask: "Does this need to exist?" Default to deletion. |
| **Categorical** | 0.92 (Abstract) | When stuck, ask: "What's the morphism?" Find the composition. |
| **Gratitude** | 0.78 (Sacred) | Honor the slop. Failed experiments are offerings, not waste. |
| **Heterarchy** | 0.88 (Peer-to-Peer) | Resist orchestrator patterns. Agents are peers. |
| **Generativity** | 0.90 (Generation) | Write specs, not docs. Let impl be derived. |
| **Joy** | 0.75 (Playful) | If it's not delightful, something is wrong. |

### Using K-gent Effectively

**When you're stuck**: Use CHALLENGE mode.
```bash
kgents soul challenge "I can't decide between X and Y"
```
K-gent will remind you what you actually believe. It's Kent-on-his-best-day talking to Kent-on-his-worst-day.

**When you need clarity**: Use REFLECT mode.
```bash
kgents soul challenge "I think I should refactor the auth module" --mode reflect
```
K-gent mirrors back, surfacing hidden assumptions.

**When you need options**: Use EXPLORE mode.
```bash
kgents soul challenge "What are different approaches to state management?" --mode explore
```
K-gent follows tangents, connects to category theory, biology, economics.

### The Dialectical Framework

When you're truly stuck, K-gent runs dialectics:

1. **THESIS**: What are you claiming?
2. **ANTITHESIS**: What would you push back on if a junior said this?
3. **SYNTHESIS**: Not resolution—clarity about what's actually at stake.

Example:
```
You: "I'm thinking of adding a caching layer."

K-gent: "Your Aesthetic coordinate is 0.15—strongly minimalist. A cache
adds complexity. Have you measured the actual bottleneck?

THESIS: 'We need caching for performance.'
ANTITHESIS: Your own principle says 'premature optimization is waste.'
SYNTHESIS: What's the smallest experiment that would prove caching necessary?

What would you tell someone else in this position?"
```

### Your Patterns (For Reference)

These are extracted from your actual behavior:

**Thinking**:
- Starts from first principles
- Asks "what would falsify this?"
- Seeks composable abstractions

**Decision-Making**:
- Prefers reversible choices
- Values optionality

**Communication**:
- Uses analogies frequently
- Appreciates precision in technical contexts

### Deeper Foundations

For the category theory grounding and philosophical depth, see:
- [`docs/categorical-foundations.md`](./categorical-foundations.md) — The mathematical and philosophical foundations
- `spec/principles.md` — The seven principles + meta-principles
- `impl/claude/agents/k/eigenvectors.py` — The eigenvector extraction and usage

---

## Stigmergic Surface

> *Agents may append observations and suggestions below. Kent curates monthly.*

### Agent Observations

```
2025-12-12  [claude-opus-4.5]
  - LocalProjector exists but doesn't use actual Symbiont from agents/d/
  - Consider wiring StatefulAdapter to SQLiteAgent for true persistence
  - The "Observable" pre-attachment pattern is incomplete (no actual mirror)

2025-12-12  [claude-opus-4.5]
  - kgents a run cannot run archetypes directly (now has helpful error)
  - Consider shipping example agents in agents/examples/ for immediate testing
  - AGENTESE paths for projector (self.agent.*.project.local) not yet wired
```

### Suggested Enhancements

```
[ ] Add `kgents a new <name> --archetype Kappa` to scaffold agents
[ ] Add `kgents a build <agent>` to build Docker images
[ ] Wire Observable to actual HolographicBuffer attachment
[ ] Create agents/examples/ with runnable examples
[ ] Add `--watch` flag to `kgents a run` for hot-reload during development
```

### Kent's Notes

```
(Space for Kent to add his own observations as he uses the system)
```

---

*"The operator's mastery is measured not by what they build, but by what they choose not to build."*

*Last updated: 2025-12-12*
