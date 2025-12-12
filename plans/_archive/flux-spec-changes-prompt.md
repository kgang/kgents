# Prompt: Execute Flux Functor Spec Changes

**Purpose**: Apply the spec changes from `docs/spec-change-proposal.md` (Flux Functor)
**Scope**: Spec files only (no implementation code)
**Key Paradigm Shifts**:
- "Loop" → "Flux" (event-driven, not timer-driven)
- `start() → None` → `start() → AsyncIterator[B]` (output flows)
- Bypass → Perturbation (state integrity)
- Ouroboric feedback (recurrence)

---

## Context

You are updating the kgents specification to add the **Flux Functor**. Flux lifts agents from **Discrete State** to **Continuous Flow**:

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]
```

This enables Living Pipelines, preserves functor laws, and solves the Sink Problem.

### Required Reading Before Starting

1. `spec/principles.md` — §6 (Heterarchical), "The noun is a lie"
2. `spec/c-gents/functor-catalog.md` — Existing 12 functors
3. `spec/c-gents/functors.md` — Functor theory
4. `spec/bootstrap.md` — Fix (μ) as foundation
5. `spec/d-gents/symbiont.md` — State threading (comparison)
6. `spec/archetypes.md` — The 8 archetypes
7. `docs/spec-change-proposal.md` — The proposal
8. `plans/agents/loop.md` — Full implementation plan (renamed but content is Flux)

---

## Critical Concepts

### The Four Critiques (Must Address)

| Problem | Solution |
|---------|----------|
| **Polling Fallacy** | Event-driven sources, not `asyncio.sleep()` |
| **Sink Problem** | `start() → AsyncIterator[B]` (output flows) |
| **Bypass Problem** | Perturbation, not direct inner.invoke() |
| **Recurrence Gap** | Ouroboric feedback_fraction |

### The Signature

```
Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where:
  Flux[T] = AsyncIterator[T]  # Asynchronous stream
```

This is NOT `LoopAgent[A, B]`. It's `Agent[Flux[A], Flux[B]]` — an agent that transforms streams.

### Living Pipelines

Because output flows (not sinks), Flux agents compose via pipe:

```python
pipeline = flux_a | flux_b | flux_c
async for result in pipeline.start(source):
    ...
```

---

## Tasks

### Task 1: Add Flux Functor to `spec/c-gents/functor-catalog.md`

**Location**: After entry #12 (Sandbox Functor)
**Action**: Add new section

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

This preserves **State Integrity**: If agent has Symbiont memory, perturbation flows through the same state-loading path as normal events. No race conditions, no "schizophrenia."

### Ouroboric Feedback
```python
config = FluxConfig(
    feedback_fraction=0.3,  # 30% of outputs feed back to input
    feedback_transform=lambda b: b.as_context(),  # B → A adapter
)
```

| Fraction | Behavior |
|----------|----------|
| 0.0 | Pure reactive (no feedback) |
| 0.1-0.3 | Light context accumulation |
| 0.5 | Equal external/internal |
| 1.0 | Full ouroboros (solipsism risk) |

### Flux Topology (Physics of Flow)
Agents are topological knots in event streams:

| Metric | Meaning | Calculation |
|--------|---------|-------------|
| **Pressure** | Queue depth | `len(queues)` |
| **Flow** | Throughput | `events/second` |
| **Turbulence** | Error rate | `errors/events` |
| **Temperature** | Token metabolism | From void/entropy |

### Configuration
```python
@dataclass
class FluxConfig:
    # Entropy (J-gent physics)
    entropy_budget: float = 1.0
    entropy_decay: float = 0.01
    max_events: int | None = None

    # Backpressure
    buffer_size: int = 100
    drop_policy: str = "block"  # "block" | "drop_oldest" | "drop_newest"

    # Ouroboros
    feedback_fraction: float = 0.0
    feedback_transform: Callable[[B], A] | None = None

    # Observability
    emit_pheromones: bool = True
    agent_id: str | None = None
```

### Specification
`spec/agents/flux.md`

### Implementation
`impl/claude/agents/flux/`

### Status
🔄 **Planned** - Specification complete
```

---

### Task 2: Create `spec/agents/flux.md`

**Location**: New file
**Action**: Create comprehensive spec

The spec must cover:

1. **Philosophy**: Discrete → Continuous (The Flux Insight)
2. **The Signature**: `Agent[A,B] → Agent[Flux[A], Flux[B]]`
3. **FluxAgent Protocol**: With `start() → AsyncIterator[B]`
4. **FluxConfig**: Entropy, backpressure, feedback
5. **The Perturbation Principle**: invoke() on FLOWING = inject, not bypass
6. **The Ouroboros**: feedback_fraction routes output to input
7. **Living Pipelines**: `|` operator, FluxPipeline
8. **Flux Topology**: Pressure, Flow, Turbulence, Temperature
9. **Sources**: Event-driven (NOT timer-driven)
10. **Relationship to Symbiont, Fix, Archetypes**
11. **Anti-Patterns**: Polling Fallacy, Sink Problem, Bypass, Solipsism

Use the content from `plans/agents/loop.md` as the basis (it's already revised for Flux).

Key sections that MUST be present:

```markdown
## The Critical Method: start() Returns a Stream

```python
async def start(self, source: AsyncIterator[A]) -> AsyncIterator[B]:
    """
    Start the flux and return the output stream.

    This is the key insight: start() doesn't return None.
    It returns Flux[B], enabling Living Pipelines.
    """
```

## The Perturbation Principle

```python
async def invoke(self, input_data: A) -> B:
    """
    If DORMANT: Direct invocation.
    If FLOWING: Inject as high-priority perturbation.

    Why not bypass? If agent has Symbiont memory, bypassing
    causes race conditions ("schizophrenia"). Perturbation
    preserves State Integrity.
    """
    if self._state == FluxState.FLOWING:
        future = asyncio.Future()
        await self._perturbation_queue.put((input_data, future))
        return await future  # Wait for flux to process
```

## Sources: Event-Driven, Not Timer-Driven

```python
# BAD: Timer zombie
async def heartbeat(interval):
    while True:
        yield time.time()
        await asyncio.sleep(interval)  # POLLING!

# GOOD: Event-driven
async def from_events(bus: EventBus) -> AsyncIterator[Event]:
    async for event in bus.subscribe():
        yield event  # REACTIVE!
```
```

---

### Task 3: Update `spec/principles.md` §6

**Location**: After "The Dual Loop" diagram (around line 182)
**Action**: Add Flux Topology section

Find:
```markdown
An agent can be **invoked** (functional) or **running** (autonomous). The same agent, two modes.
```

Add immediately after:

```markdown

### The Flux Topology

The Heterarchical Principle asserts dual modes. The **Flux Functor** operationalizes this.

The quote at the core of kgents — *"The noun is a lie. There is only the rate of change."* — becomes literal:

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

Agents are not architecture — they are **topological knots in event streams**. This allows modeling via fluid dynamics:

| Metric | Meaning |
|--------|---------|
| **Pressure** | Queue depth (backlog) |
| **Flow** | Throughput (events/second) |
| **Turbulence** | Error rate |
| **Temperature** | Token metabolism (void/entropy) |

### The Perturbation Principle

When a FluxAgent is **FLOWING**, calling `invoke()` doesn't bypass the stream — it **perturbs** it. The invocation becomes a high-priority event injected into the flux.

**Why?** If the agent has Symbiont memory, bypassing would cause:
- State loaded twice (race condition)
- Inconsistent updates ("schizophrenia")

Perturbation preserves **State Integrity**.

See:
- `spec/c-gents/functor-catalog.md` §13 — Flux functor
- `spec/agents/flux.md` — Full specification
```

---

### Task 4: Update `spec/bootstrap.md`

**Location**: After "The Seven Bootstrap Agents" section
**Action**: Add clarification

```markdown
---

## Why Flux Is Not a Bootstrap Agent

**Question**: Should Flux be the eighth bootstrap agent?

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

### Task 5: Update `spec/archetypes.md`

**Location**: After "The Eight Archetypes" section
**Action**: Add Flux configurations + Event-Driven insight

```markdown
---

## Archetypes as Flux Configurations

The eight archetypes are **instantiations of the Flux functor** with specific configurations.

| Archetype | Flux Configuration | Key Insight |
|-----------|-------------------|-------------|
| **Consolidator** | `source=idle_signal` | Await, don't poll |
| **Spawner** | Flux that emits child FluxAgents | Recursive flux |
| **Witness** | `Flux(Id)` with trace side effects | Identity + observation |
| **Questioner** | Flux with Type IV Critic inner | Never produces, only questions |
| **Uncertain** | Flux with N parallel output streams | Superposition until collapse |
| **Dialectician** | `feedback_fraction=0.5` | Equal thesis/antithesis |
| **Shapeshifter** | Dynamic Observable | Self-determined visualization |
| **Introspector** | Hegel→Lacan→Jung pipeline | Deep reflection |

### The Event-Driven Insight

Archetypes are NOT timer-driven zombies. The **Consolidator** doesn't poll every N seconds — it **awaits an idle signal**:

```python
# BAD: Timer zombie (Polling Fallacy)
async def consolidate_loop():
    while True:
        await asyncio.sleep(300)  # Poll every 5 min
        await consolidate()

# GOOD: Event-driven (Flux pattern)
async def consolidate_flux(idle_signal: AsyncIterator[IdleEvent]):
    async for _ in idle_signal:
        await consolidate()
```

### Example: Dialectician as Flux

```python
# Dialectician: thesis → antithesis → synthesis
# Uses 50% feedback so output (synthesis) becomes next input (thesis)

dialectician_flux = Flux.lift(
    Contradict() >> Sublate(),
    config=FluxConfig(
        feedback_fraction=0.5,  # Equal internal/external
        feedback_transform=lambda synthesis: synthesis.as_thesis(),
    )
)

# External theses come from source, internal from feedback
async for synthesis in dialectician_flux.start(thesis_source):
    ...
```

See `spec/agents/flux.md` for full Flux specification.
```

---

## Verification Checklist

After completing all tasks:

- [ ] `spec/c-gents/functor-catalog.md` has 13 entries (Flux is #13)
- [ ] `spec/agents/flux.md` exists and covers all 11 sections
- [ ] `spec/principles.md` §6 has Flux Topology and Perturbation Principle
- [ ] `spec/bootstrap.md` explains why Flux is not bootstrap
- [ ] `spec/archetypes.md` shows Event-Driven Insight
- [ ] All cross-references valid
- [ ] No timer-driven examples in new content
- [ ] `start()` always returns `AsyncIterator[B]`, never `None`
- [ ] Perturbation, not bypass, in all invoke() descriptions

---

## Anti-Patterns to AVOID in Spec Content

### 1. Timer-Driven Zombies

```python
# DO NOT write examples like this:
while True:
    await asyncio.sleep(interval)
    # ...
```

### 2. Void Output

```python
# DO NOT spec start() as returning None:
async def start(self, source) -> None:  # BAD!
```

### 3. Bypass Invocation

```python
# DO NOT describe invoke() as bypassing:
async def invoke(self, input):
    return await self.inner.invoke(input)  # BAD if FLOWING!
```

### 4. "Loop" Terminology

Use "Flux", "flow", "stream" — NOT "loop", "iterate", "poll".

---

## Style Guidelines

1. **Voice**: Declarative, present tense
2. **Examples**: Python with type hints
3. **Cross-references**: Relative paths
4. **Key quotes**: Include *"The noun is a lie..."* and *"dA/dt → dB/dt"*
5. **Tables**: Use for comparisons
6. **Code blocks**: Triple backticks with `python`

---

*"The noun is a lie. There is only the rate of change."*
*"Static: A → B. Dynamic: dA/dt → dB/dt."*
