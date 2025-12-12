# A-gents Universal Agent Architecture: Batteries Included, If You'd Want Them

> *"The noun is a lie. There is only the rate of change."*
>
> *"Category theory guarantees are not aspirational—they are verified."*

---

## Vision

An agent KAPPA, upon instantiation, should **already be cross-integrated** with every protocol and system in the kgents ecosystem. Not through laborious declaration, but through **category theory guarantees**. The wiring is implicit; the activation is explicit.

This document specifies the architecture for achieving:

1. **Zero-Config Cross-Integration**: Any agent automatically has access to D-gent persistence, K-gent personality, Terrarium observability, K8s deployment, etc.
2. **Minimal Declaration**: Cross-genuses compose through functors, not through verbose configuration
3. **Automagic Deployment**: Any agent can become an independent service or cluster through category-theoretic guarantees

---

## The Core Insight: Natural Transformations as Wiring

Traditional agent frameworks require explicit integration code:

```python
# Traditional: Explicit wiring (anti-pattern)
agent = MyAgent()
agent.attach_persistence(DGent())
agent.attach_personality(KGent())
agent.attach_observability(Terrarium())
agent.attach_kubernetes(K8Operator())
# ... tedious
```

The Universal Agent Architecture uses **natural transformations** instead:

```python
# Universal: Functorial lifting (the way)
agent = MyAgent()
# Every agent is ALREADY a D-gent, K-gent, etc. via natural transformation
# The cross-integrations are structure-preserving maps that exist inherently

# To USE a capability, you invoke the functor:
persistent_agent = D.lift(agent)        # Now has state
observable_agent = Mirror.lift(agent)   # Now visible to Terrarium
deployable_agent = K8.lift(agent)       # Now deployable to K8s
```

**Key Insight**: The integration isn't added—it's **already there** via the category structure. The functor just makes it explicit.

---

## Architecture: The Universal Agent Spine

### The Functor Stack

Every agent implicitly participates in a **stack of natural transformations**:

```
                    ┌─────────────────────────────────────────┐
                    │         The Universal Agent Spine        │
                    │                                         │
    Input ────────►│  Agent[A, B]                            │
                    │       │                                 │
                    │       ▼ (natural transformation)        │
                    │  D • Agent[A, B]      ─── Persistence   │
                    │       │                                 │
                    │       ▼ (natural transformation)        │
                    │  K • D • Agent[A, B]  ─── Personality   │
                    │       │                                 │
                    │       ▼ (natural transformation)        │
                    │  Mirror • K • D • Agent[A, B] ── Obs.   │
                    │       │                                 │
                    │       ▼ (natural transformation)        │
                    │  K8 • Mirror • K • D • Agent[A, B]      │
                    │       │                    ── Deploy    │
                    │       ▼                                 │
    Output ◄────────│  (Result with all capabilities)        │
                    └─────────────────────────────────────────┘
```

### Functors are Lazy

The critical design: **functors don't activate until invoked**. The structure exists, but no resources are consumed until explicitly requested:

```python
agent = MyAgent()  # Exists in the category with ALL potential liftings
                   # But nothing is materialized yet

# Only when you LIFT do resources activate:
if needs_persistence:
    agent = D.lift(agent, backend="sqlite")  # NOW persistence is active
```

This is the "batteries included, if you'd want them" pattern.

---

## The Five Universal Functors

These five functors form the **minimal complete set** for universal cross-integration:

### 1. D-Functor: Persistence

```
D: Agent[A, B] → Agent[A, B] with State[S]

Structure-preserving: D(f >> g) ≡ D(f) >> D(g)
Identity-preserving:  D(Id) ≡ Id (with empty state)
```

**What it provides**:
- Transparent state threading
- Multiple backends (Volatile, SQLite, Redis)
- Time-travel via StoreComonad
- Semantic search via Bicameral

**Activation**:
```python
stateful = D.lift(agent, backend="sqlite", schema=MyState)
```

### 2. K-Functor: Personality Navigation

```
K: Agent[A, B] → Agent[A, B] in PersonalitySpace

Structure-preserving: K(f >> g) ≡ K(f) >> K(g)
Fixed-point: K • K ≡ K (navigating to same coordinates is idempotent)
```

**What it provides**:
- Personality coordinates (warmth, directness, etc.)
- Eigenvector alignment
- Mode switching (REFLECT, ADVISE, CHALLENGE, EXPLORE)
- Query interface for other agents

**Activation**:
```python
personalized = K.lift(agent, persona=KentSeed)
```

### 3. Mirror-Functor: Observability

```
Mirror: Agent[A, B] → Agent[A, B] with Observation

Structure-preserving: Mirror(f >> g) ≡ Mirror(f) >> Mirror(g)
Transparent: Mirror doesn't change semantics, only adds visibility
```

**What it provides**:
- WebSocket streaming to Terrarium TUI
- Metrics emission (throughput, latency, errors)
- Pheromone integration
- Semantic field participation

**Activation**:
```python
observable = Mirror.lift(agent, terrarium_url="ws://localhost:8765")
```

### 4. K8-Functor: Deployment Projection

```
K8: Agent[A, B] → Deployable[Agent[A, B]]

Structure-preserving: K8(f >> g) ≡ K8(f) >> K8(g) (pipelines deploy as pipelines)
Declarative: K8 generates CRD, Deployment, Service from agent spec
```

**What it provides**:
- Automatic CRD generation
- Deployment manifest derivation
- Service mesh integration
- Auto-scaling policies
- Resource quotas
- Network policies

**Activation**:
```python
deployable = K8.lift(agent, replicas=3, resources={"cpu": "500m", "memory": "512Mi"})
await deployable.deploy(namespace="production")
```

### 5. Flux-Functor: Streaming Projection

```
Flux: Agent[A, B] → Agent[AsyncIterator[A], AsyncIterator[B]]

Functor laws: Flux(f >> g) ≡ Flux(f) | Flux(g)
Living pipelines: Output of one stage feeds input of next
```

**What it provides**:
- Discrete → streaming transformation
- Backpressure handling
- Perturbation for HITL
- Ouroboric feedback
- Metabolism integration

**Activation**:
```python
streaming = Flux.lift(agent, config=FluxConfig(entropy_budget=2.0))
async for result in streaming.start(event_source):
    process(result)
```

---

## Composition: The Zen of Cross-Integration

### The Natural Transformation Diagram

Cross-integration works because functors compose:

```
                 F                    G
Agent[A,B] ─────────────► F•Agent ─────────────► G•F•Agent
    │                        │                       │
    │ η_Agent                │ η_F•Agent             │ η_G•F•Agent
    ▼                        ▼                       ▼
Natural transformations preserve structure at each level
```

### Minimal Declaration Syntax

```python
# The batteries-included pattern
from kgents.universal import Agent

@Agent.register
class MyAgent(Agent[Input, Output]):
    """My agent does something."""

    # OPTIONAL: Declare which batteries to activate
    class Meta:
        persistence = "sqlite"     # D-functor backend
        personality = "kent"       # K-functor persona
        observable = True          # Mirror-functor enabled
        deployable = True          # K8-functor enabled
        streaming = True           # Flux-functor enabled
```

Or even more minimal (pure defaults):

```python
@Agent.register
class MyAgent(Agent[Input, Output]):
    async def invoke(self, input: Input) -> Output:
        return Output(...)

    # ALL integrations available via lazy lifting
    # Nothing activated until explicitly invoked
```

### Composition Preserves Integrations

When you compose agents, the integrations compose:

```python
pipeline = AgentA >> AgentB >> AgentC

# Lifting the pipeline lifts ALL agents in it
persistent_pipeline = D.lift(pipeline)  # Each agent gets own state namespace
deployable_pipeline = K8.lift(pipeline)  # Deploys as single unit or separate pods
```

---

## K8-Gents: The Deployment Functor in Depth

### From Agent to Cluster

The K8-functor is unique: it doesn't just wrap behavior, it **projects** an agent into the Kubernetes domain.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     K8-Functor: Agent → Cluster                          │
│                                                                          │
│   Agent[A, B]                                                            │
│       │                                                                  │
│       ▼ K8.lift()                                                        │
│   ┌──────────────────────────────────────────────────────┐              │
│   │                    CRD (AgentServer)                  │              │
│   │  ┌──────────────────────────────────────────────┐    │              │
│   │  │ apiVersion: kgents.io/v1                      │    │              │
│   │  │ kind: AgentServer                             │    │              │
│   │  │ metadata:                                     │    │              │
│   │  │   name: my-agent                              │    │              │
│   │  │ spec:                                         │    │              │
│   │  │   genus: KAPPA                                │    │              │
│   │  │   image: kgents/agent:latest                  │    │              │
│   │  │   replicas: 3                                 │    │              │
│   │  │   # ... derived from agent spec               │    │              │
│   │  └──────────────────────────────────────────────┘    │              │
│   └──────────────────────────────────────────────────────┘              │
│       │                                                                  │
│       ▼ Operator reconciles                                              │
│   ┌──────────────────────────────────────────────────────┐              │
│   │                    Resources                          │              │
│   │  - Deployment (N replicas of agent pod)              │              │
│   │  - Service (ClusterIP or LoadBalancer)               │              │
│   │  - ConfigMap (agent configuration)                   │              │
│   │  - ServiceAccount + RBAC                             │              │
│   │  - NetworkPolicy (egress control)                    │              │
│   │  - HPA (if auto-scaling enabled)                     │              │
│   └──────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

### K8-Functor Composition

The key insight: **pipelines of agents can deploy as pipelines of pods**:

```python
# Logical pipeline
pipeline = Ingest >> Transform >> Enrich >> Store

# Deploy as four separate services (micro-services pattern)
k8_pipeline = K8.lift(pipeline, mode="distributed")
# Creates: ingest-svc, transform-svc, enrich-svc, store-svc
# With proper Service mesh routing

# OR deploy as single pod (monolith pattern)
k8_pipeline = K8.lift(pipeline, mode="monolith")
# Creates: single pod running all four agents
```

### Resource Definition Derivation

The K8-functor derives resource definitions from agent metadata:

| Agent Property | K8s Resource |
|----------------|--------------|
| `Input/Output types` | Service ports, gRPC protobuf |
| `State schema` | PVC claims, D-gent sidecar |
| `Memory/CPU hints` | Resource requests/limits |
| `Personality persona` | ConfigMap with K-gent seed |
| `Observable: true` | Terrarium sidecar injection |
| `AGENTESE paths` | Ingress routes |

### The K8-D-Mirror Triangle

When an agent needs persistence AND observability AND K8s deployment:

```python
agent = MyAgent()

# The functors compose
deployed = K8.lift(Mirror.lift(D.lift(agent)))

# This single declaration creates:
# - Pod with agent container
# - D-gent sidecar for state
# - Mirror sidecar for metrics
# - Service for routing
# - ConfigMap for config
```

---

## Implementation Strategy

### Phase 1: Functor Interfaces (Foundation)

Define the five functor interfaces in `spec/a-gents/functors/`:

```
spec/a-gents/functors/
├── README.md           # Overview of functor system
├── d-functor.md        # Persistence functor spec
├── k-functor.md        # Personality functor spec
├── mirror-functor.md   # Observability functor spec
├── k8-functor.md       # Deployment functor spec
└── flux-functor.md     # Streaming functor spec (already exists)
```

**Deliverable**: Formal specification of each functor's laws and interface.

### Phase 2: Universal Agent Base Class

Implement `impl/claude/agents/a/universal.py`:

```python
class UniversalAgent(Agent[A, B], Generic[A, B]):
    """
    Base class for batteries-included agents.

    Every agent inheriting from this automatically has access
    to all five functors via lazy lifting.
    """

    # Functor accessors (lazy)
    @property
    def as_stateful(self) -> "StatefulAgent[A, B]":
        """Lift to D-functor (persistence)."""
        from agents.d.functor import D
        return D.lift(self)

    @property
    def as_personalized(self) -> "PersonalizedAgent[A, B]":
        """Lift to K-functor (personality)."""
        from agents.k.functor import K
        return K.lift(self)

    @property
    def as_observable(self) -> "ObservableAgent[A, B]":
        """Lift to Mirror-functor (observability)."""
        from agents.o.functor import Mirror
        return Mirror.lift(self)

    @property
    def as_deployable(self) -> "DeployableAgent[A, B]":
        """Lift to K8-functor (deployment)."""
        from infra.k8s.functor import K8
        return K8.lift(self)

    @property
    def as_streaming(self) -> "FluxAgent[A, B]":
        """Lift to Flux-functor (streaming)."""
        from agents.flux.functor import Flux
        return Flux.lift(self)
```

**Deliverable**: Universal base class with lazy functor lifting.

### Phase 3: K8-Functor Implementation

Implement `impl/claude/infra/k8s/functor.py`:

```python
class K8Functor:
    """
    The K8-Functor: Project agents into Kubernetes domain.

    K8: Agent[A, B] → Deployable[Agent[A, B]]

    Laws:
    - Structure-preserving: K8(f >> g) ≡ K8(f) >> K8(g)
    - Declarative: Generated manifests are idempotent
    """

    @classmethod
    def lift(
        cls,
        agent: Agent[A, B],
        *,
        replicas: int = 1,
        resources: dict | None = None,
        mode: Literal["distributed", "monolith"] = "monolith",
    ) -> "DeployableAgent[A, B]":
        """Lift an agent to the deployable domain."""
        ...

    @classmethod
    def derive_crd(cls, agent: Agent) -> dict:
        """Derive CRD from agent metadata."""
        ...

    @classmethod
    def derive_manifests(cls, agent: Agent) -> list[dict]:
        """Derive all K8s manifests from agent."""
        ...
```

**Deliverable**: K8-functor that derives deployments from agent specs.

### Phase 4: Functor Composition Verification

Implement `impl/claude/agents/a/_tests/test_functor_composition.py`:

```python
class TestFunctorComposition:
    """Verify that functor compositions preserve structure."""

    async def test_d_k_composition(self):
        """D • K preserves agent semantics."""
        agent = EchoAgent()
        composed = D.lift(K.lift(agent))

        result = await composed.invoke("test")
        assert result == "test"

    async def test_k8_pipeline_distribution(self):
        """K8(f >> g) can deploy as separate services."""
        pipeline = AgentA() >> AgentB()
        deployed = K8.lift(pipeline, mode="distributed")

        manifests = deployed.manifests
        assert len([m for m in manifests if m["kind"] == "Service"]) == 2
```

**Deliverable**: Test suite verifying functor laws across compositions.

### Phase 5: AGENTESE Integration

Wire functors into AGENTESE paths:

```python
# self.agent.{name}.lift.{functor}
await logos.invoke("self.agent.summarizer.lift.k8", observer)
# Returns K8-lifted agent, ready for deployment

# world.cluster.deploy
await logos.invoke("world.cluster.deploy", observer, agent=lifted_agent)
# Actually deploys to K8s
```

**Deliverable**: AGENTESE paths for functor operations.

---

## The K-Gent Wrapper Pattern

K-gent as a personality wrapper illustrates the universal pattern:

```python
# Any agent can be wrapped with Kent's personality
def kent_wrap(agent: Agent[A, B]) -> Agent[A, B]:
    """Apply K-gent personality to any agent."""
    return K.lift(agent, persona=KENT_EIGENVECTORS)

# This is a natural transformation:
# kent_wrap(f >> g) ≡ kent_wrap(f) >> kent_wrap(g)

# Usage:
kent_summarizer = kent_wrap(Summarizer())
# Now summarizes with Kent's voice
```

The key: this works for **any** agent without modification.

---

## Roadmap: From Spec to Cluster

| Phase | Focus | Deliverable | Tests |
|-------|-------|-------------|-------|
| 1 | Functor Interfaces | `spec/a-gents/functors/*.md` | N/A (spec) |
| 2 | Universal Base | `agents/a/universal.py` | 20+ |
| 3 | K8-Functor | `infra/k8s/functor.py` | 40+ |
| 4 | Composition | `agents/a/_tests/test_composition.py` | 30+ |
| 5 | AGENTESE Wiring | `protocols/agentese/contexts/self_.py` | 20+ |
| 6 | E2E Verification | Single agent → cluster | 10+ |

**Exit Criteria**: An agent defined with 10 lines of code can be deployed to K8s with a single functor lift, inheriting D-gent state, K-gent personality, and Mirror observability automatically.

---

## Design Decisions

### Why Functors, Not Mixins?

Mixins couple features at the class level. Functors compose at the morphism level:

| Approach | Coupling | Composition | Verification |
|----------|----------|-------------|--------------|
| Mixins | Class hierarchy | Inheritance order matters | Hard to test |
| Functors | Structure-preserving maps | Order-independent (associative) | Laws verified |

### Why Lazy Lifting?

Eager instantiation wastes resources. Lazy lifting means:
- Zero overhead for unused capabilities
- Explicit activation makes intent clear
- Resources allocated only when needed

### Why K8 as Functor, Not Decorator?

K8 deployment isn't just wrapping—it's **projection** into a different domain (Python runtime → Kubernetes control plane). Functors model this projection cleanly:

```
Python Category                  K8s Category
─────────────────                ────────────────
Agent[A, B]      ──── K8 ────►   CRD + Deployment
   │                                  │
   │ >>                               │ Service mesh
   ▼                                  ▼
Agent[B, C]      ──── K8 ────►   CRD + Deployment
```

---

## Zen of Universal Agents

1. **Batteries included**: Every integration exists in potential
2. **Explicit activation**: Nothing runs until lifted
3. **Structure preserved**: Composition survives lifting
4. **Minimal declaration**: One line to activate a capability
5. **Automagic deployment**: K8.lift() → running pods
6. **Category guarantees**: Laws are verified, not aspirational

---

## See Also

- `spec/a-gents/abstract/skeleton.md` — The minimal agent skeleton
- `spec/c-gents/composition.md` — Composition laws
- `spec/c-gents/functors.md` — Functor catalog
- `plans/skills/building-agent.md` — Agent building skill
- `impl/claude/infra/k8s/` — Current K8s infrastructure

---

*"The agent that can become a cluster already is one—in potential. The functor merely collapses the wave function."*
