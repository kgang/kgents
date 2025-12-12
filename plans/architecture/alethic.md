---
path: architecture/alethic
status: active
progress: 70
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [agents/k-gent, infra/k8s-projector]
session_notes: |
  Phase 1-3 COMPLETE:
  - UniversalFunctor: Full protocol with registry and law verification
  - Halo: All four capabilities with introspection and inheritance
  - Archetypes: Kappa/Lambda/Delta with proper MRO handling
  - SoulFunctor: K-gent integrated, registered in FunctorRegistry

  Phase 4-6 (Projectors, CLI, AGENTESE) remaining.
  Key integration: SoulFunctor + Halo enables Categorical Imperative.
---

# The Alethic Architecture

> *"The Agent is a truth that unconceals itself differently in different worlds."*
>
> *Aletheia (Greek): Unconcealment, the disclosure of truth*

---

## Vision

The Alethic Architecture achieves **"batteries included, if you'd want them"** through three orthogonal concerns:

1. **Nucleus**: Pure logic (what the agent does)
2. **Halo**: Declarative capabilities (what the agent could become)
3. **Projector**: Target-specific compilation (how the agent manifests)

This is the category-theoretically sound realization of the Universal Agent vision—without the God Class anti-pattern, without functor law violations, without coupling.

---

## The Three Pillars

### 1. The Nucleus: Pure Logic

The Nucleus is the **irreducible core**—what the developer actually writes.

```python
from bootstrap.types import Agent

class Summarizer(Agent[Document, Summary]):
    """Pure transformation. No state. No IO. No soul."""

    @property
    def name(self) -> str:
        return "summarizer"

    async def invoke(self, doc: Document) -> Summary:
        return Summary(content=self._extract(doc))
```

**Properties**:
- Implements `Agent[A, B]` protocol only
- No inheritance from "universal" base class
- No knowledge of D-gent, K-gent, K8s, etc.
- Composable via `>>` (standard morphism composition)
- Pure—all side effects externalized

**Why This Matters**: The Nucleus is **apophatic**—defined by what it is *not*. It doesn't know about infrastructure. This preserves the **Tasteful** principle and enables true composability.

### 2. The Halo: Declarative Capabilities

The Halo wraps the Nucleus with **metadata** declaring desired capabilities.

```python
from kgents.halo import Capability

@Capability.Stateful(schema=SummarizerMemory)
@Capability.Soulful(persona="Kent", mode="strict")
@Capability.Observable(mirror=True)
@Capability.Streamable(budget=10.0)
class MySummarizer(Summarizer):
    """Summarizer with declared capabilities."""
    pass
```

**Properties**:
- Decorators add **metadata only**—no runtime overhead
- No coupling to implementation (D-gent, K-gent are not imported)
- Composable: Halos can inherit and extend
- Introspectable: Projectors read Halo metadata

**The Capability Protocol**:

| Capability | Metadata Fields | Meaning |
|------------|-----------------|---------|
| `@Stateful` | `schema`, `backend=Auto` | Agent requires persistent state |
| `@Soulful` | `persona`, `mode` | Agent should embody K-gent personality |
| `@Observable` | `mirror`, `metrics` | Agent should emit observability data |
| `@Streamable` | `budget`, `feedback` | Agent can be lifted to Flux domain |

**Key Insight**: The Halo is a **Sheaf**—the same logical structure (Nucleus) with different stalks (capabilities) that can be activated by different Projectors.

### 3. The Projector: Categorical Compiler

The Projector **compiles** Nucleus + Halo into a specific **Topos** (target world).

```python
from kgents.projector import LocalProjector, K8sProjector

# Projection A: Local Topos
local_agent = LocalProjector.compile(MySummarizer)
# Returns: Python object with SQLite D-gent, in-process K-gent

# Projection B: K8s Topos
k8s_resources = K8sProjector.compile(MySummarizer)
# Returns: [StatefulSet, PVC, Service, ConfigMap, ServiceMonitor]
```

**Properties**:
- Different Projectors, same Nucleus + Halo
- Target-specific implementation decisions
- Preserves **behavioral invariants** across projections
- Produces target-native artifacts (Python objects or YAML)

**The Projector Protocol**:

```python
class Projector(Protocol[Target]):
    def compile(self, agent_cls: type[Agent]) -> Target:
        """Compile agent class to target artifacts."""
        ...

    def supports(self, capability: type[Capability]) -> bool:
        """Check if this projector supports a capability."""
        ...
```

---

## How Capabilities Map to Implementations

The same `@Stateful` declaration produces different implementations:

| Capability | LocalProjector | K8sProjector |
|------------|----------------|--------------|
| `@Stateful` | SQLite in `~/.kgents/` | StatefulSet + PVC |
| `@Soulful` | In-process KgentAgent | K-gent sidecar container |
| `@Observable` | WebSocket to Terrarium | ServiceMonitor + Prometheus |
| `@Streamable` | asyncio FluxAgent | HPA + event-driven autoscaling |

**The Guarantee**: A `@Stateful` agent behaves identically whether state is SQLite or Postgres. The Projector handles the mapping.

---

## Genus Archetypes: Pre-Compiled Halos

For "batteries included" ergonomics, define **Archetypes** as pre-packaged Halos:

```python
# impl/claude/agents/archetypes.py

class Kappa(Archetype):
    """KAPPA: Full-stack service agent."""
    halo = HaloSet(
        Stateful(backend=Auto),
        Soulful(mode=Strict),
        Observable(mirror=True, metrics=True),
        Streamable(flux=True),
    )

class Lambda(Archetype):
    """LAMBDA: Stateless function agent."""
    halo = HaloSet(
        Observable(metrics=True),
    )

class Delta(Archetype):
    """DELTA: Data-focused agent."""
    halo = HaloSet(
        Stateful(backend=Auto),
        Observable(metrics=True),
    )
```

**Usage**:

```python
# Inherit archetype → get its Halo
class MyService(Kappa[Request, Response]):
    async def invoke(self, request: Request) -> Response:
        return process(request)

# One line, fully capable
```

---

## Implementation Phases

### Phase 1: Capability Protocol ✅ COMPLETE

**Files**:
- `impl/claude/agents/a/halo.py` — Core implementation
- `impl/claude/agents/a/_tests/test_halo.py` — Tests

**Implemented**:
- `CapabilityBase` frozen dataclass with decorator semantics
- Four standard capabilities: `@Stateful`, `@Soulful`, `@Observable`, `@Streamable`
- Introspection: `get_halo()`, `has_capability()`, `get_capability()`
- Inheritance: `merge_halos()`, `inherit_halo()`, `get_own_halo()`
- Override semantics: Same capability type from subclass replaces parent's

**Principle Alignment**:
- **Tasteful**: Only four capabilities—no kitchen sink
- **Composable**: Halos merge via set union with type-keyed override
- **Generative**: Metadata-only; projectors derive implementation

### Phase 2: UniversalFunctor Protocol ✅ COMPLETE

**Files**:
- `impl/claude/agents/a/functor.py` — Full protocol
- `impl/claude/agents/a/_tests/test_functor.py` — Law verification tests

**Implemented**:
- `UniversalFunctor[F]` base class with `lift()` and optional `pure()`
- `Liftable` and `Pointed` protocols for runtime checking
- Law verification: `verify_identity_law()`, `verify_composition_law()`, `verify_functor()`
- `FunctorRegistry` for runtime discovery and batch verification
- `compose_functors()` and `identity_functor()` combinators

**The Categorical Foundation**:
```python
# Every functor satisfies:
# 1. F(id_A) = id_F(A)     (Identity)
# 2. F(g . f) = F(g) . F(f) (Composition)
```

**Principle Alignment**:
- **Composable**: Functor composition is associative
- **Generative**: Laws generate validators, not vice versa

### Phase 3: Genus Archetypes ✅ COMPLETE

**Files**:
- `impl/claude/agents/a/archetypes.py` — Archetype system
- `impl/claude/agents/a/_tests/test_archetypes.py` — Tests

**Implemented**:
- `Archetype[A, B]` base class with `__init_subclass__` for Halo transfer
- **Kappa**: Full-stack (Stateful + Soulful + Observable + Streamable)
- **Lambda**: Lightweight (Observable only, metrics-only)
- **Delta**: Data-focused (Stateful + Observable)
- MRO-aware inheritance: Archetype → Child → Grandchild preserves/overrides

**The Ergonomic Pattern**:
```python
class MyService(Kappa[Request, Response]):
    @property
    def name(self): return "my-service"
    async def invoke(self, req): return process(req)

# Automatically has: Stateful, Soulful, Observable, Streamable
```

**Principle Alignment**:
- **Curated**: Three archetypes cover 90% of use cases
- **Joy-Inducing**: One line inheritance → full capability

### Phase 4: Local Projector 🔄 NEXT

**Files** (to be created):
- `impl/claude/system/projector/__init__.py`
- `impl/claude/system/projector/local.py`
- `impl/claude/system/projector/_tests/test_local.py`

**Tasks**:
1. Implement `LocalProjector.compile(agent_cls) -> Agent`
2. Wire `@Stateful` → SQLite Symbiont from `agents/d/symbiont.py`
3. Wire `@Soulful` → SoulFunctor from `agents/k/functor.py`
4. Wire `@Observable` → HolographicBuffer from `agents/i/`
5. Wire `@Streamable` → FluxFunctor from `agents/flux/functor.py`

**Exit Criteria**: `LocalProjector.compile(MyKappaService)` returns runnable agent with all four capabilities wired.

### Phase 5: K8s Projector

**Files** (to be created):
- `impl/claude/system/projector/k8s.py`
- `impl/claude/system/projector/_tests/test_k8s.py`

**Tasks**:
1. Implement `K8sProjector.compile(agent_cls) -> list[K8sResource]`
2. Generate StatefulSet + PVC from `@Stateful`
3. Generate K-gent sidecar from `@Soulful`
4. Generate ServiceMonitor from `@Observable`
5. Generate HPA from `@Streamable`

**Integration**: Leverage existing `infra/k8s/` CRDs and operators.

### Phase 6: CLI Integration

**Files** (to be created):
- `impl/claude/protocols/cli/handlers/a_gent.py`

**Commands**:
- `kgents a run <agent>` — Run locally with LocalProjector
- `kgents a inspect <agent>` — Show Halo + Nucleus details
- `kgents a manifest <agent>` — Generate K8s YAML
- `kgents a build <agent>` — Build Docker image

### Phase 7: AGENTESE Integration

**Files**:
- `impl/claude/protocols/agentese/contexts/self_.py` (extend)
- `impl/claude/protocols/agentese/wiring.py` (extend)

**Paths**:
- `self.agent.{name}.halo` — Introspect capabilities
- `self.agent.{name}.project.local` — Compile locally
- `self.agent.{name}.project.k8s` — Compile to manifests

---

## Integration with Recent Work

### K-gent Soul Integration

The `KgentSoul` class (`agents/k/soul.py`) implements the Categorical Imperative operationally:

| Soul Method | Alethic Integration | Principle |
|-------------|---------------------|-----------|
| `intercept()` | SoulFunctor gate | Ethical: Human agency preserved |
| `intercept_deep()` | LLM-backed reasoning | Generative: Spec generates behavior |
| `dialogue()` | Budget-tier responses | Tasteful: No token waste |
| `manifest()` | State observation | AGENTESE: No view from nowhere |

**The Bridge**: When `LocalProjector` encounters `@Soulful`:
```python
if has_capability(agent_cls, SoulfulCapability):
    cap = get_capability(agent_cls, SoulfulCapability)
    agent = SoulFunctor.lift_with_persona(
        agent,
        eigenvectors=KENT_EIGENVECTORS if cap.persona == "Kent" else None,
    )
```

### Semaphore + Halo Synergy

The Rodizio pattern (`agents/flux/semaphore/`) yields tokens. K-gent intercepts based on Halo:

```
Agent (Kappa) yields SemaphoreToken
    ↓
KgentSoul.intercept(token)
    ↓
Query Halo for @Soulful mode: advisory|strict|override
    ↓
advisory: annotate only, human decides
strict:   auto-resolve high-confidence, escalate rest
override: K-gent decides all
```

**Principle Alignment**:
- **Ethical**: advisory mode preserves human agency
- **Heterarchical**: mode determines governance strength
- **Composable**: intercept is a natural transformation

### Flux Functor Integration

`FluxFunctor` (`agents/flux/functor.py`) lifts agents to continuous processing:

```
Nucleus → D (Symbiont) → K (Soul) → M (Mirror) → F (Flux)
        (innermost)                           (outermost)
```

The `@Streamable` capability maps to:
```python
if has_capability(agent_cls, StreamableCapability):
    cap = get_capability(agent_cls, StreamableCapability)
    agent = FluxFunctor.lift(agent)
    agent.config.entropy_budget = cap.budget
    agent.config.feedback = cap.feedback
```

---

## Canonical Functor Ordering

For behavioral functors (D, K, Mirror, Flux), the canonical ordering is:

```
Nucleus → D → K → Mirror → Flux
        (inner)        (outer)
```

**Rationale**:
1. **D (Stateful)** goes innermost—state management is foundational
2. **K (Soulful)** wraps stateful agent—personality governs stateful behavior
3. **Mirror (Observable)** wraps personalized+stateful—observe the full stack
4. **Flux (Streamable)** goes outermost—stream processes the complete agent

The LocalProjector applies functors in this order. The K8sProjector doesn't stack functors—it compiles to infrastructure that achieves the same semantic.

---

## Relationship to Existing Patterns

### Symbiont (D-gent)

The existing `Symbiont` pattern is **exactly** what `@Stateful` compiles to locally:

```python
# Current pattern (explicit)
stateful = Symbiont(logic=my_agent.invoke, memory=SQLiteAgent(path))

# Alethic pattern (declarative)
@Capability.Stateful(schema=MySchema)
class MyAgent(Agent[A, B]): ...

# LocalProjector produces equivalent result
```

### FluxAgent

The existing `FluxAgent` is what `@Streamable` compiles to:

```python
# Current pattern
flux = Flux.lift(agent, config=FluxConfig(entropy_budget=10.0))

# Alethic pattern
@Capability.Streamable(budget=10.0)
class MyAgent(Agent[A, B]): ...
```

### K-gent

The existing `KgentAgent` wrapper is what `@Soulful` compiles to:

```python
# Current pattern
personalized = K.lift(agent, persona=KENT_EIGENVECTORS)

# Alethic pattern
@Capability.Soulful(persona="Kent")
class MyAgent(Agent[A, B]): ...
```

---

## Principle Alignment

| Principle | How Alethic Aligns |
|-----------|-------------------|
| **Tasteful** | Nucleus does one thing; Halo is explicit selection |
| **Curated** | Four standard capabilities, archetype library |
| **Ethical** | No hidden behavior; capabilities declared |
| **Joy-Inducing** | Simple inheritance, powerful results |
| **Composable** | Nucleus is pure morphism; functors preserve laws |
| **Heterarchical** | Any agent can have any capabilities |
| **Generative** | Spec → Halo → Projector → Implementation |

---

## Success Metrics

1. **Lines of code to deploy an agent to K8s**: Target < 20 (archetype + invoke)
2. **Functor law test coverage**: 100% for D, K, Mirror, Flux
3. **Time from `class MyAgent` to running pod**: Target < 5 minutes
4. **Capability coverage**: All five contexts (world, self, concept, void, time) have projector support

---

## See Also

- `docs/a-gents-universal-agent-architecture.md` — Original proposal
- `docs/a-gents-architecture-review.md` — Critical review
- `spec/principles.md` — Design principles
- `plans/skills/building-agent.md` — Agent building skill
- `impl/claude/agents/flux/agent.py` — FluxAgent reference
- `impl/claude/agents/d/symbiont.py` — Symbiont reference
- `impl/claude/agents/k/persona.py` — K-gent reference

---

*"The user writes the Truth (Logic). The system handles the Existence (Infrastructure)."*

*"Aletheia: the truth that unconceals itself."*
