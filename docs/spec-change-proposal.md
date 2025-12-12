# Spec Change Proposal: Flux Functor

**Date**: 2025-12-12
**Author**: claude-opus-4.5
**Status**: Proposed (Revised)
**Scope**: Conservative (additive, no breaking changes)

---

## Summary

This proposal adds the **Flux Functor** to the kgents specification. Flux formalizes the transformation from **Discrete State** to **Continuous Flow**, enabling agents to process streams rather than single invocations.

**Key Insight**: The original "Loop" proposal suffered from the **Polling Fallacy** — wrapping imperative timer-driven logic in functional clothing. This revision adopts the **Flux paradigm**: event-driven streams, output that flows (not sinks), and perturbation (not bypass) for running agents.

---

## The Critique That Shaped This Revision

### 1. The Polling Fallacy

**Original**: Loops with `asyncio.sleep(interval)` — zombie agents that twitch on timers.
**Revised**: Event-driven flux — agents respond to streams, not clocks.

### 2. The Sink Problem

**Original**: `start() → None` — output disappears unless side-effect captured.
**Revised**: `start() → AsyncIterator[B]` — output flows, enabling Living Pipelines.

### 3. The Bypass Problem

**Original**: `invoke()` on running loop bypasses the loop (race conditions, state schizophrenia).
**Revised**: `invoke()` on running flux = **Perturbation** (injected into stream, state integrity preserved).

### 4. The Recurrence Gap

**Original**: Feedback mentioned but not specified.
**Revised**: **Ouroboros** — configurable feedback_fraction routes output back to input.

---

## Proposed Changes

### 1. Add Flux Functor to `spec/c-gents/functor-catalog.md`

**Location**: After entry #12 (Sandbox Functor)
**Type**: Addition

```markdown
## 13. Flux Functor (agents/flux)

### Signature
```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]
```

Where `Flux[T] = AsyncIterator[T]` (asynchronous stream).

### Description
Lifts an Agent from the domain of **Discrete State** to the domain of **Continuous Flow**. It transforms an agent that maps `A → B` into a process that maps `Flux[A] → Flux[B]`.

This solves **The Sink Problem**: Where does the output go?
- In Function Mode, output is returned to the caller.
- In Flux Mode, output is emitted as a continuous stream.

**Living Pipelines**: Because output flows, Flux agents compose via pipe:
```python
pipeline = flux_a | flux_b | flux_c
async for result in pipeline.start(source):
    ...
```

### Laws
```python
# Identity Preservation
Flux(Id) ≅ Id_Flux  # Identity maps Flux[A] → Flux[A]

# Composition Preservation
Flux(f >> g) ≅ Flux(f) >> Flux(g)
```

### Key Insight
Flux operationalizes the quote *"The noun is a lie. There is only the rate of change."*

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

### The Lift Operation
```python
class Flux:
    @staticmethod
    def lift(agent: Agent[A, B]) -> FluxAgent[A, B]:
        """Lift to flux domain."""
        return FluxAgent(inner=agent)

    @staticmethod
    def unlift(flux_agent: FluxAgent[A, B]) -> Agent[A, B]:
        """Extract inner agent."""
        return flux_agent.inner
```

### The Perturbation Principle
When `invoke(x)` is called on a FluxAgent that is:
- **DORMANT**: Direct invocation (discrete mode)
- **FLOWING**: Inject `x` as high-priority perturbation into stream

This preserves **State Integrity**: If agent has Symbiont memory, perturbation flows through the same state-loading path as normal events. No race conditions.

### Ouroboric Feedback
```python
config = FluxConfig(
    feedback_fraction=0.3,  # 30% of outputs feed back to input
    feedback_transform=lambda b: b.as_context(),  # B → A adapter
)
```

### Flux Topology (Physics of Flow)
| Metric | Meaning |
|--------|---------|
| **Pressure** | Queue depth |
| **Flow** | events_processed / elapsed_time |
| **Turbulence** | errors / events_processed |
| **Temperature** | Token metabolism (void/entropy) |

### Specification
`spec/agents/flux.md`

### Implementation
`impl/claude/agents/flux/`

### Status
🔄 **Planned** - Specification complete
```

---

### 2. Create `spec/agents/flux.md`

**Location**: New file
**Type**: Addition

The full specification covering:
1. Philosophy (discrete → continuous)
2. FluxAgent protocol
3. FluxConfig (entropy, backpressure, feedback)
4. The Perturbation Principle
5. The Ouroboros
6. Living Pipelines
7. Sources (event-driven, not timer-driven)
8. Flux Topology (fluid dynamics view)

See `plans/agents/loop.md` for complete content.

---

### 3. Update `spec/principles.md` §6

**Location**: After "The Dual Loop" diagram
**Type**: Addition

```markdown
### The Flux Topology

The Heterarchical Principle asserts dual modes. The **Flux Functor** operationalizes this.

The quote at the core of kgents — *"The noun is a lie. There is only the rate of change."* — becomes literal:

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

This allows agents to be modeled using **fluid dynamics**:
- **Pressure**: Queue depth (backlog)
- **Flow**: Throughput (events/second)
- **Turbulence**: Error rate

### The Perturbation Principle

When a FluxAgent is **FLOWING** (processing a stream), calling `invoke()` doesn't bypass the stream — it **perturbs** it. The invocation becomes a high-priority event injected into the flux.

**Why?** If the agent has Symbiont memory, bypassing would cause:
- State loaded twice (race condition)
- Inconsistent updates ("schizophrenia")

Perturbation preserves **State Integrity**.

See:
- `spec/c-gents/functor-catalog.md` §13 — Flux functor
- `spec/agents/flux.md` — Full specification
```

---

### 4. Update `spec/bootstrap.md`

**Location**: After "The Seven Bootstrap Agents"
**Type**: Addition

```markdown
---

## Why Flux Is Not a Bootstrap Agent

**Question**: Should Flux be added to the bootstrap?

**Analysis**:

| Criterion | Flux | Assessment |
|-----------|------|------------|
| **Irreducible?** | Derivable from Fix | Flux ≅ Fix applied to streams |
| **Required for regeneration?** | No | Can regenerate without Flux |
| **Categorical necessity?** | No | Composition works without Flux |

**The Derivation**:
```python
Flux(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

**Conclusion**: Flux is a **derived functor**. It belongs in:
- `spec/c-gents/functor-catalog.md` §13
- `spec/agents/flux.md`

However, Flux is **foundational infrastructure** for living agents. Without it, all agents are corpses that only move when poked.
```

---

### 5. Update `spec/archetypes.md`

**Location**: After "The Eight Archetypes"
**Type**: Addition

```markdown
---

## Archetypes as Flux Configurations

The eight archetypes are **instantiations of Flux** with specific configurations.

| Archetype | Flux Configuration | Key Insight |
|-----------|-------------------|-------------|
| **Consolidator** | `source=idle_signal` | Await, don't poll |
| **Spawner** | Flux that emits child FluxAgents | Recursive flux |
| **Witness** | `Flux(Id)` with trace | Identity + side effects |
| **Questioner** | Flux with Type IV Critic inner | Never produces, only questions |
| **Uncertain** | Flux with N parallel output streams | Superposition until collapse |
| **Dialectician** | `feedback_fraction=0.5` | Equal thesis/antithesis |
| **Shapeshifter** | Dynamic Observable | Self-determined visualization |
| **Introspector** | Hegel→Lacan→Jung pipeline | Deep reflection |

### The Event-Driven Insight

Archetypes are NOT timer-driven zombies. The **Consolidator** doesn't poll every N seconds — it **awaits an idle signal**:

```python
# BAD: Timer zombie
async def consolidate_loop():
    while True:
        await asyncio.sleep(300)  # Poll every 5 min
        await consolidate()

# GOOD: Event-driven
async def consolidate_flux(idle_signal: AsyncIterator[IdleEvent]):
    async for _ in idle_signal:
        await consolidate()
```

See `spec/agents/flux.md` for full Flux specification.
```

---

## Design Decisions

### Why "Flux" Instead of "Loop"?

| "Loop" | "Flux" |
|--------|--------|
| Implies iteration | Implies flow |
| Timer-centric | Event-centric |
| `start() → None` | `start() → AsyncIterator[B]` |
| Bypass invocation | Perturbation |

"Flux" captures the ontology: agents are knots in a stream of events, not ticking clocks.

### Why Output Must Flow

```python
# BAD: The Sink Problem
async def start(self, source) -> None:
    async for event in source:
        result = await self.inner.invoke(event)
        # result goes... where?

# GOOD: Output flows
async def start(self, source) -> AsyncIterator[B]:
    async for event in source:
        yield await self.inner.invoke(event)
```

Returning `AsyncIterator[B]` enables:
- **Living Pipelines**: `flux_a | flux_b | flux_c`
- **Composition preservation**: Functor laws hold
- **No sink problem**: Output has a destination

### Why Perturbation, Not Bypass

```python
# BAD: Bypass (schizophrenia risk)
async def invoke(self, input):
    if self._flowing:
        return await self.inner.invoke(input)  # Bypasses state!

# GOOD: Perturbation (state integrity)
async def invoke(self, input):
    if self._flowing:
        future = asyncio.Future()
        await self._perturbation_queue.put((input, future))
        return await future  # Goes through flux
```

Perturbation ensures:
- Symbiont memory loads/saves in order
- No race conditions
- Result returned to caller (feels like invoke)

---

## Principle Assessment

| Principle | Assessment |
|-----------|------------|
| **Tasteful** | Single functor, clear purpose (lift to flux) |
| **Curated** | Not a God construct — just stream transformation |
| **Ethical** | Entropy bounds, perturbation preserves integrity |
| **Joy-Inducing** | Living pipelines feel alive |
| **Composable** | `|` operator, functor laws preserved |
| **Heterarchical** | invoke() and start() coexist via perturbation |
| **Generative** | Archetypes derive from Flux configuration |

### Is This a God Construct?

**No.** Flux does ONE thing: lift `Agent[A,B] → Agent[Flux[A], Flux[B]]`.

It doesn't:
- Manage memory (Symbiont)
- Judge outputs (Judge)
- Handle errors (Ground)
- Create agents (Spawner archetype)

---

## Implementation Path

### Phase 1: Spec Updates (This Proposal)
- [ ] Add Flux to functor-catalog.md §13
- [ ] Create spec/agents/flux.md
- [ ] Update principles.md §6 (Flux Topology)
- [ ] Update bootstrap.md (why not bootstrap)
- [ ] Update archetypes.md (Flux configurations)

### Phase 2: Core Implementation
- [ ] agents/flux/functor.py
- [ ] agents/flux/agent.py (FluxAgent)
- [ ] agents/flux/config.py (FluxConfig)
- [ ] agents/flux/perturbation.py
- [ ] Tests: 80+

### Phase 3: Pipeline & Sources
- [ ] agents/flux/pipeline.py (FluxPipeline, `|` operator)
- [ ] agents/flux/sources/ (events, pheromones, periodic)
- [ ] Tests: 20+

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Functor laws violated | Low | High | Property-based tests |
| Backpressure deadlock | Medium | Medium | drop_policy config |
| Perturbation race | Low | High | Queue-based implementation |
| Ouroboros solipsism | Medium | Low | feedback_fraction < 1.0 default |

---

## Open Questions

### Q1: Should FluxAgent implement Agent protocol?

**Yes.** FluxAgent.invoke() works in both modes:
- DORMANT: Direct invocation
- FLOWING: Perturbation

This preserves the Heterarchical Principle.

### Q2: How do parallel FluxAgents share state?

Via **Symbiont with shared D-gent**. Flux doesn't manage state — it just threads time. Symbiont threads state. Both compose.

### Q3: What happens to perturbation results?

Perturbation results go to the caller (via Future), NOT to the output stream. This is intentional — perturbations are synchronous interactions with an asynchronous system.

---

## Success Criteria

This proposal succeeds when:

1. **Spec is clear**: Reader understands Flux signature and semantics
2. **No Sink Problem**: Output flows, not disappears
3. **No Polling Fallacy**: Event-driven, not timer-driven
4. **Perturbation works**: invoke() on FLOWING preserves state integrity
5. **Living Pipelines**: `flux_a | flux_b` compiles and runs
6. **Not a God**: Flux does ONE thing

---

## References

- `spec/principles.md` §6 (Heterarchical Principle)
- `spec/c-gents/functor-catalog.md` (Functor patterns)
- `spec/c-gents/functors.md` (Functor theory)
- `spec/bootstrap.md` (Fix as foundation)
- `spec/d-gents/symbiont.md` (State threading comparison)
- `spec/archetypes.md` (Flux instantiations)
- `plans/agents/loop.md` (Implementation plan)

---

*"The noun is a lie. There is only the rate of change."*
*"Static: A → B. Dynamic: dA/dt → dB/dt."*
