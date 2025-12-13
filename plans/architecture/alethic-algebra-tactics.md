# Alethic Algebra Tactics: Categorical Foundation Implementation

> *"The structure of the agent mirrors the structure of the thought. The code is merely the shadow."*

**Created**: 2025-12-12
**Status**: active
**Progress**: 95%
**Dependencies**: agents/a/halo.py ✅, agents/a/functor.py ✅, agents/k/functor.py ✅, agents/c/functor.py ✅, agents/flux/functor.py ✅, agents/o/observer_functor.py ✅, agents/d/state_monad.py ✅

---

## Strategic Context

This plan translates the Alethic Algebra research into concrete implementation tactics. The synergy analysis identified a **fundamental isomorphism crisis**: all our agents implement functors independently without a unifying structure.

**The Insight**: Halo (already implemented as declarative capabilities) is the seed of the Alethic Architecture. What's missing is the **algebraic structure** that composes these capabilities into emergent behavior.

---

## Architectural Decision: Universal Functor Mandate

> **DECISION (2025-12-12)**: All agents in kgents SHALL be reformulated through the Universal Functor Protocol.

### Rationale

1. **Isomorphism Crisis**: The synergy analysis revealed that C-gent, Flux, K-gent, O-gent, and B-gent all implement functors independently. This creates:
   - Duplicated law verification logic
   - Incompatible composition patterns
   - No unified observation mechanism

2. **Generative Principle**: A well-formed spec generates implementation. The Universal Functor Protocol IS that spec — all functor behavior derives from `lift()` and law compliance.

3. **K-gent Integration**: K-gent as the "nervous system" requires a uniform interface to intercept ANY agent. The Universal Functor Protocol provides this.

### What This Means

| Agent Genus | Current Pattern | Reformulated Pattern |
|-------------|-----------------|----------------------|
| C-gent | `MaybeAgent`, `EitherAgent`, etc. | `MaybeFunctor.lift(agent)` |
| Flux | `FluxAgent` wrapper | `FluxFunctor.lift(agent)` |
| K-gent | `KgentAgent` wrapper | `SoulFunctor.lift(agent)` |
| O-gent | `TelemetryObserver` | `ObserverFunctor.lift(agent)` |
| B-gent | `MeteredAgent` | `MeterFunctor.lift(agent)` |

### Migration Strategy

1. **Phase 1** ✅: Define `UniversalFunctor` protocol (DONE)
2. **Phase 2**: Retrofit existing C-gent functors to implement protocol
3. **Phase 3**: Define canonical functors for Flux, K-gent, O-gent, B-gent
4. **Phase 4**: Register all functors in `FunctorRegistry`
5. **Phase 5**: Verify laws across entire codebase via `FunctorRegistry.verify_all()`

### Backward Compatibility

Existing code continues to work. The reformulation is additive:
- `MaybeAgent(inner)` still works (convenience wrapper)
- `MaybeFunctor.lift(inner)` is the canonical form
- Both produce the same lifted agent

---

## Tactical Phases

### Phase 1: Universal Functor Protocol ✅ COMPLETE

**Goal**: Define a single functor protocol that unifies all existing functors.

**Files**:
- `impl/claude/agents/a/functor.py` ✅
- `impl/claude/agents/a/_tests/test_functor.py` ✅

**What Was Built**:

```python
class UniversalFunctor(Generic[F]):
    """
    All functors satisfy: F(id) = id, F(g . f) = F(g) . F(f)
    """
    @staticmethod
    @abstractmethod
    def lift(agent: Agent[A, B]) -> Agent[Any, Any]: ...

    @staticmethod
    def pure(value: A) -> Any: ...  # Optional

# Supporting infrastructure:
- Liftable[F_co] protocol for runtime_checkable
- Pointed[F_co] protocol for pure() support
- FunctorLawResult, FunctorVerificationReport dataclasses
- verify_identity_law(), verify_composition_law(), verify_functor()
- compose_functors(), identity_functor()
- FunctorRegistry with verify_all()
```

**Principle Application**:
- **Generative**: Laws defined once, verification derived
- **Composable**: `compose_functors(F, G)` is associative

---

### Phase 2: Halo + SoulFunctor Integration ✅ COMPLETE

**Goal**: Connect Halo metadata to concrete functor implementations.

**What Was Built**:

1. **Halo System** (`agents/a/halo.py`):
   - Four capabilities: `@Stateful`, `@Soulful`, `@Observable`, `@Streamable`
   - Introspection API: `get_halo()`, `has_capability()`, `get_capability()`
   - Inheritance: `merge_halos()`, `inherit_halo()` with override semantics

2. **SoulFunctor** (`agents/k/functor.py`):
   ```python
   class SoulFunctor(UniversalFunctor[SoulAgent[Any, Any]]):
       @staticmethod
       def lift(agent: Agent[A, B]) -> SoulAgent[A, B]:
           return SoulAgent(inner=agent)

       @staticmethod
       def pure(value: A) -> Soul[A]:
           return Soul(value=value)

       @staticmethod
       def lift_with_persona(agent, eigenvectors=None, persona=None):
           # Explicit persona configuration
           ...
   ```

3. **Soul Context** (`agents/k/functor.py:Soul[A]`):
   - Wraps value with eigenvectors, persona, metadata
   - `map()` preserves context through transformations
   - `context_prompt` generates LLM system context

**The Bridge**:
```python
# Halo declares intent
@Capability.Soulful(persona="Kent", mode="strict")
class MyAgent(Agent[str, str]): ...

# Projector reads Halo, applies functor
agent = SoulFunctor.lift_with_persona(MyAgent(), eigenvectors=KENT_EIGENVECTORS)
```

**Principle Application**:
- **Ethical**: `mode` controls governance strength (advisory/strict/override)
- **AGENTESE**: Soul context is observer-dependent perception

---

### Phase 3: Guard Functor + K-gent Intercept ✅ COMPLETE

**Goal**: K-gent intercept as categorical gate for any agent.

**What Was Built** (`agents/k/soul.py:KgentSoul`):

```python
class KgentSoul:
    async def intercept(self, token: Any) -> InterceptResult:
        """Shallow intercept: keyword + principle matching"""
        matching_principles = self._find_matching_principles(prompt)
        matching_patterns = self._find_matching_patterns(prompt)
        confidence = self._calculate_intercept_confidence(...)
        # High confidence → auto-resolve; Low → annotate for human

    async def intercept_deep(self, token: Any) -> InterceptResult:
        """Deep intercept: LLM-backed reasoning against principles"""
        # CRITICAL: Dangerous keywords → always escalate
        if is_dangerous:
            return InterceptResult(handled=False, recommendation="escalate")
        # LLM reasoning with structured output
        response = await self._llm.generate(system_prompt, user_prompt)
        return self._parse_intercept_response(response.text, ...)
```

**The Guard Pattern**:
```python
# KgentSoul acts as parametric Guard
# The "validator" is the eigenvector-backed principle reasoner

class SoulGuard(UniversalFunctor[Guarded]):
    def __init__(self, soul: KgentSoul):
        self.soul = soul

    async def guard(self, agent: Agent[A, B], input: A) -> Guarded[B]:
        # Check before execution
        result = await self.soul.intercept_deep(input)
        if not result.handled and result.recommendation == "escalate":
            raise EscalationRequired(result.annotation)
        return Guarded(await agent.invoke(input))
```

**Principle Application**:
- **Ethical**: `DANGEROUS_KEYWORDS` are never auto-approved
- **Heterarchical**: advisory/strict/override modes
- **Generative**: Audit trail generated from intercept logic

---

### Phase 4: LocalProjector Implementation ✅ COMPLETE

**Goal**: Compile Halo metadata to runtime functors.

**What Was Built**:

| Capability | Functor Available | Implementation |
|------------|-------------------|----------------|
| `@Stateful` | StatefulAdapter | `system/projector/local.py` ✅ |
| `@Soulful` | SoulfulAdapter | `system/projector/local.py` ✅ |
| `@Observable` | ObservableMixin | `system/projector/local.py` ✅ |
| `@Streamable` | FluxAgent | `agents/flux/agent.py` ✅ |

**LocalProjector** (`impl/claude/system/projector/local.py`):
- Reads capability decorators via `get_halo()`
- Applies functors in canonical order: D → K → Mirror → Flux
- 100% test coverage via `_tests/test_local.py`

**CLI Integration** (`kgents a`):
- `kgents a list` - List available agents
- `kgents a inspect <name>` - Inspect agent Halo
- `kgents a manifest <name>` - Generate K8s manifests
- `kgents a run <name>` - Run agent locally

**Files Created**:
- `impl/claude/system/projector/__init__.py` ✅
- `impl/claude/system/projector/base.py` ✅
- `impl/claude/system/projector/local.py` ✅
- `impl/claude/system/projector/k8s.py` ✅
- `impl/claude/system/projector/_tests/test_local.py` ✅

---

### Phase 5: Law Registry ✅ COMPLETE

**Goal**: Define laws once, generate validators everywhere.

**What Was Built** (`agents/a/functor.py:FunctorRegistry`):

```python
class FunctorRegistry:
    _functors: dict[str, type[UniversalFunctor[Any]]] = {}

    @classmethod
    def register(cls, name: str, functor: type[UniversalFunctor[Any]]) -> None:
        """Register a functor with the registry."""
        cls._functors[name] = functor

    @classmethod
    async def verify_all(
        cls,
        identity_agent: Agent[A, A],
        f: Agent[A, B],
        g: Agent[B, C],
        test_input_factory: Callable[[str], Any],
    ) -> dict[str, FunctorVerificationReport]:
        """Verify all registered functors against laws."""
        reports = {}
        for name, functor in cls._functors.items():
            test_input = test_input_factory(name)
            reports[name] = await verify_functor(functor, identity_agent, f, g, test_input)
        return reports
```

**All Functors Registered** (10+ functors):
- `Maybe`, `Either`, `List`, `Async`, `Logged`, `Fix` from `agents/c/functor.py` ✅
- `Flux` from `agents/flux/functor.py` ✅
- `Soul` from `agents/k/functor.py` ✅
- `Observer` from `agents/o/observer_functor.py` ✅
- `State` from `agents/d/state_monad.py` ✅

**Principle Application**:
- **Generative**: `verify_all()` generates verification from registration
- **Composable**: Registry tracks composition compatibility

---

## Integration Points

### K-gent Soul as Nervous System ✅ OPERATIONAL

The `KgentSoul` class is the operational realization of the Categorical Imperative:

```python
# Soul is now the middleware of consciousness
soul = KgentSoul()

# Direct dialogue with budget tiers
output = await soul.dialogue("What am I avoiding?", DialogueMode.REFLECT)
# Returns: SoulDialogueOutput with eigenvector context

# Semaphore mediation via intercept
result = await soul.intercept(semaphore_token)  # Shallow: keyword matching
result = await soul.intercept_deep(semaphore_token)  # Deep: LLM reasoning
```

**The Four Capabilities of K-gent**:
| Capability | Implementation | Status |
|------------|----------------|--------|
| Gatekeeper | `intercept_deep()` with DANGEROUS_KEYWORDS | ✅ |
| Fractal Expander | `dialogue()` with budget tiers | ✅ |
| Holographic Constitution | Eigenvectors in `to_system_prompt_section()` | ✅ |
| Sommelier | Rodizio pattern + halo mode query | 🔄 |

### Terrarium + Observable Integration

The Terrarium work (`agents/terrarium.md` archive) provides the infrastructure:

```python
@Capability.Observable(mirror=True, metrics=True)
class MyFluxAgent(Kappa[Event, Summary]): ...

# LocalProjector wiring:
# 1. HolographicBuffer for Terrarium WebSocket
# 2. Prometheus metrics for ServiceMonitor
```

### Semaphore + Halo Synergy

The Rodizio pattern (`agents/semaphores.md` archive) yields tokens:

```
FluxAgent.invoke() → yield SemaphoreToken
    ↓
Purgatory captures token
    ↓
KgentSoul.intercept(token)
    ↓
Query Halo @Soulful mode:
  - advisory: annotate, human decides
  - strict: auto-resolve high-confidence, escalate rest
  - override: K-gent decides all (risky, use sparingly)
```

### Cross-Agent Pipelines

With functors unified under `UniversalFunctor`:

```python
# Compose lifts
full_stack = compose_functors(
    TelemetryFunctor,  # O-gent: observe
    SoulFunctor,       # K-gent: govern
    FluxFunctor,       # Flux: stream
)

# Apply to any agent
enhanced = full_stack(MyBusinessLogic())

# Or via archetype + projector
class MyService(Kappa[Request, Response]):
    async def invoke(self, req): return process(req)

agent = LocalProjector().compile(MyService)  # All four capabilities
```

---

## Implementation Order (Updated)

| Phase | Name | Status | Outcome |
|-------|------|--------|---------|
| 1 | UniversalFunctor | ✅ COMPLETE | Protocol + Registry + Verification |
| 2 | Halo + SoulFunctor | ✅ COMPLETE | Capabilities + K-gent lift |
| 3 | Guard + Intercept | ✅ COMPLETE | KgentSoul with LLM-backed reasoning |
| 4 | LocalProjector | ✅ COMPLETE | Compile Halo → runtime functor chain |
| 5 | LawRegistry | ✅ COMPLETE | FunctorRegistry.verify_all() |
| 6 | CLI Integration | ✅ COMPLETE | `kgents a {list,inspect,manifest,run}` |
| 7 | C-gent Retrofit | ✅ COMPLETE | All 6 C-gent functors retrofitted |
| 8 | Flux Retrofit | ✅ COMPLETE | FluxFunctor implements UniversalFunctor |
| 9 | Cross-Functor Composition | ✅ COMPLETE | compose_functors() verified |

**All Phases Complete!** The Alethic Algebra foundation is operational.

---

## Agent Reformulation Status

> **Goal**: Every functor-like pattern in kgents derives from `UniversalFunctor`.

### K-gent SoulFunctor ✅ COMPLETE

| Functor | File | Status | Registry |
|---------|------|--------|----------|
| `SoulFunctor` | `agents/k/functor.py` | ✅ | `FunctorRegistry.get("Soul")` |

**Implementation**:
- `Soul[A]` context wrapper with eigenvectors, persona, metadata
- `SoulAgent[A, B]` lifts agents to soul domain
- `SoulFunctor.lift()`, `SoulFunctor.pure()`, `SoulFunctor.lift_with_persona()`
- Auto-registers on import

### C-gent Functors ✅ RETROFITTED

All C-gent functors now derive from `UniversalFunctor` and auto-register:

| Functor | File | Implementation | Registry |
|---------|------|----------------|----------|
| `MaybeFunctor` | `agents/c/functor.py` | `MaybeAgent` + `unlift_maybe()` | ✅ |
| `EitherFunctor` | `agents/c/functor.py` | `EitherAgent` + `unlift_either()` | ✅ |
| `ListFunctor` | `agents/c/functor.py` | `ListAgent` + `unlift_list()` | ✅ |
| `AsyncFunctor` | `agents/c/functor.py` | `AsyncAgent` + `unlift_async()` | ✅ |
| `LoggedFunctor` | `agents/c/functor.py` | `LoggedAgent` + `unlift_logged()` | ✅ |
| `FixFunctor` | `agents/c/functor.py` | `FixAgent` + `unlift_fix()` | ✅ |

All functors support **symmetric lifting**: `unlift(lift(agent)) ≅ agent`

### Flux Functor ✅ RETROFITTED

| Functor | File | Implementation | Registry |
|---------|------|----------------|----------|
| `FluxFunctor` | `agents/flux/functor.py` | `FluxAgent` + `Flux.unlift()` | ✅ |

**FluxFunctor** (`agents/flux/functor.py`):
- Derives from `UniversalFunctor[FluxAgent[Any, Any]]`
- `lift()` creates FluxAgent for stream processing
- `pure()` creates single-element async stream
- Auto-registers on import

### O-gent UnifiedObserverFunctor ✅ COMPLETE

| Functor | File | Implementation | Registry |
|---------|------|----------------|----------|
| `UnifiedObserverFunctor` | `agents/o/observer_functor.py` | `ObservedAgent` | ✅ |

**Consolidates**:
- O-gent telemetry
- N-gent narrative traces
- T-gent metrics

### D-gent StateMonadFunctor ✅ COMPLETE

| Functor | File | Implementation | Registry |
|---------|------|----------------|----------|
| `StateMonadFunctor` | `agents/d/state_monad.py` | `StatefulAgent` | ✅ |

**Enables**:
- Automatic state threading
- Composition with Flux and other functors
- Symmetric lifting with `unlift()`

---

## Functor Composition Examples

### Current State (Working)

```python
# SoulFunctor composition is available now
from agents.k.functor import SoulFunctor, soul, soul_lift

# Lift any agent to soul domain
soul_agent = SoulFunctor.lift(my_agent)

# Invoke with soul context
result = await soul_agent.invoke(soul("What should I prioritize?"))
# result is Soul[B] with preserved eigenvectors

# Compose functors (once C-gent retrofitted)
from agents.a.functor import compose_functors
stack = compose_functors(SoulFunctor, MaybeFunctor)  # Soul ∘ Maybe
```

### Target State (After LocalProjector)

```python
# Halo-driven composition via projector
@Capability.Stateful(schema=dict)
@Capability.Soulful(persona="Kent", mode="strict")
@Capability.Observable(mirror=True)
@Capability.Streamable(budget=10.0)
class MyService(Agent[Request, Response]):
    @property
    def name(self): return "my-service"
    async def invoke(self, req): return process(req)

# One-line compilation
agent = LocalProjector().compile(MyService)
# Returns: FluxAgent wrapping MirrorAgent wrapping SoulAgent wrapping Symbiont
```

### With Archetypes (Available Now)

```python
# Kappa gives you the full Halo automatically
class MyService(Kappa[Request, Response]):
    @property
    def name(self): return "my-service"
    async def invoke(self, req): return process(req)

# Introspect the Halo
from agents.a.halo import get_halo, has_capability
halo = get_halo(MyService)  # {Stateful, Soulful, Observable, Streamable}
assert has_capability(MyService, SoulfulCapability)
```

---

## Verification Strategy

### Current State

**SoulFunctor Law Tests** (`agents/k/_tests/test_soul_functor_laws.py`):
- Verifies identity and composition laws
- Uses `verify_functor()` from `agents/a/functor.py`

**FunctorRegistry** (`agents/a/functor.py`):
- `verify_all()` available for batch verification
- Currently only Soul registered

### Target State (After C-gent Retrofit)

```python
# In test suite
async def test_all_registered_functors():
    """Verify all functors satisfy categorical laws."""
    reports = await FunctorRegistry.verify_all(
        identity_agent=Id(),
        f=double_agent,
        g=add_one_agent,
        test_input_factory=create_test_input,
    )

    # All must pass
    for name, report in reports.items():
        assert report.passed, f"Functor {name} failed: {report.identity_law.explanation}"
```

### CI Commands

```bash
# Run functor law tests
pytest agents/a/_tests/test_functor.py -v
pytest agents/k/_tests/test_soul_functor_laws.py -v

# Run all law tests
pytest -k "functor_law or law_test" --tb=short
```

---

## Principle Alignment Audit

How the Alethic Algebra realizes spec/principles.md:

| Principle | Alethic Realization |
|-----------|---------------------|
| **Tasteful** | Four capabilities only. No kitchen sink. |
| **Curated** | Three archetypes (Kappa/Lambda/Delta) cover 90% of use cases |
| **Ethical** | `@Soulful(mode=)` controls governance strength; dangerous keywords never auto-approve |
| **Joy-Inducing** | One-line archetype inheritance → full capability stack |
| **Composable** | Functors satisfy identity + composition laws; `compose_functors()` is associative |
| **Heterarchical** | advisory/strict/override modes; no fixed orchestrator |
| **Generative** | Laws define structure; verification derives from laws |
| **AGENTESE** | Soul context carries eigenvectors; observation is not neutral |
| **Accursed Share** | `@Streamable(budget=)` + entropy depletion → graceful collapse to Ground |

---

## Risk Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Breaking existing functors | Backward-compat: existing code unaffected, algebra is additive | ✅ Achieved |
| Complexity creep | Tasteful: only implement what K-gent + Projector need | ✅ Holding |
| Performance overhead | Zero-cost abstraction: Halo is metadata-only until projection | ✅ Achieved |
| Law violations | `verify_functor()` catches violations at test time | ✅ Available |

---

## Success Criteria (Updated)

| Criterion | Status |
|-----------|--------|
| UniversalFunctor protocol defined | ✅ |
| SoulFunctor implements protocol | ✅ |
| FunctorRegistry with `verify_all()` | ✅ |
| Halo capabilities introspectable | ✅ |
| Archetypes inherit Halo | ✅ |
| K-gent intercept_deep() works | ✅ |
| LocalProjector compiles Halo → runtime | ✅ |
| C-gent functors retrofitted | ✅ |
| Flux functor retrofitted | ✅ |
| All functors registered in batch | ✅ (10+ functors) |
| Cross-functor composition tested | ✅ |
| CLI integration complete | ✅ |

---

## Next Actions

**The Alethic Algebra is functionally complete.** All planned features are implemented.

**Future Enhancements** (not blocking):
1. **B-gent Functors**: `MeteredFunctor`, `ValueFunctor` for token accounting
2. **Extended Law Verification**: Property-based testing with Hypothesis
3. **Performance Optimization**: Lazy functor composition
4. **Documentation**: Comprehensive functor composition guide

---

*"The skeleton exists. The algebra provides the muscles. The soul breathes life."*

---

## Completion Summary (2025-12-12)

The Alethic Algebra implementation is **95% complete**:

- **10+ functors** registered in `FunctorRegistry`
- **Symmetric lifting** (`lift/unlift`) for all major functors
- **Cross-functor composition** verified via `compose_functors()`
- **LocalProjector** compiles Halo → runtime in canonical order
- **K8sProjector** generates Kubernetes manifests from Halo
- **CLI** provides full agent lifecycle management

The remaining 5% represents future enhancements (B-gent functors, extended verification) that are not blocking for the current architecture.

---

## Next Phase: Polish & Batteries Included

**See**: `prompts/alethic-polish.md`

The architecture is sound. Now make it delightful:

| Component | Purpose |
|-----------|---------|
| Examples directory | 5 runnable examples (zero to agent in 5 min) |
| Convenience imports | `from agents import *` gives you everything |
| `@agent` decorator | One-liner agent creation |
| `kgents a new` | Scaffold new agents with boilerplate |
| Functor Field Guide | Docs accessible without category theory |
| Test helpers | `assert_agent_output`, `assert_functor_laws` |

*"The difference between a good system and a great one is the last 5%."*
