# Functor Catalog: kgents Transformation Patterns

**Status:** Standard
**Foundation:** All functors are polynomial endofunctors on `PolyAgent[S, A, B]`

## Purpose

This catalog formalizes functor patterns across the kgents ecosystem. Many agent transformations follow functor laws but weren't explicitly documented as such. This reference makes them explicit, enabling systematic reasoning about agent transformations across genera.

## Core Insight

Every agent transformation is a polynomial endofunctor that modifies positions (state space), directions (inputs), or transitions (dynamics).

---

## Polynomial Functor Summary

Each functor transforms a polynomial agent `P(y) = Σ_{s ∈ S} y^{E(s)}` according to how it modifies positions (S), directions (E), and transitions.

| Functor | Position Transform | Direction Transform | Transition Transform | Category |
|---------|-------------------|---------------------|---------------------|----------|
| **Promise** | Add `resolved` state | Identity | Lazy evaluation | Lifting |
| **View** | Map to widget state | UI events | Render | Lifting |
| **Metered** | Add budget state | Identity | Cost accounting | Economizing |
| **Personalization** | Filter by eigenvector | Identity | Soul-mediated | Filtering |
| **Lens** | Focus state | Bidirectional | Get/Set | Lifting |
| **Optimization** | Identity | Identity | Improved prompts | Endofunctor |
| **Spy** | Add history state | Identity | Log + forward | Observing |
| **Mock** | Collapse to constant | Accept all | Return constant | Terminal |
| **Parser** | Add parse state | Text only | Extract structure | Lifting |
| **Tool** | Add MCP state | Add capability check | Sandboxed + Result | Lifting |
| **Trace** | Add emission state | Identity | Emit + forward | Observing |
| **Sandbox** | Namespace isolation | Filter forbidden | Guard execution | Filtering |
| **Flux** | Add flow state | Streams | Continuous dynamics | Lifting |
| **State** | Add load/save state | Identity | Thread S through | Lifting |

---

## Functor Quick Reference

| Functor | Signature | Genus | Status | Description |
|---------|-----------|-------|--------|-------------|
| **Promise** | `A → Promise[A]` | J, C | ✅ Documented | Lazy computation deferral |
| **View** | `Agent[A,B] → Widget` | I | 🔄 Implicit | Visual representation |
| **Metered** | `Agent[A,B] → Transaction[A,B]` | B | 🔄 Implicit | Economic wrapping |
| **Personalization** | `Agent[A,B] → Agent[A,B]` | K | 🔄 Implicit | Personality field application |
| **Lens** | `S → A` (bidirectional) | D | 🔄 Implicit | State focus/update |
| **Optimization** | `Agent[A,B] → Agent'[A,B]` | R | 🔄 Implicit | Prompt optimization (endofunctor) |
| **Spy** | `Agent[A,A] → Agent[A,A]` | T | 🔄 Implicit | Identity + tracing side effect |
| **Mock** | `Agent[A,B] → Agent[A,B]` | T | 🔄 Implicit | Replace with constant |
| **Parser** | `Text → ParseResult[A]` | P | 🔄 Implicit | Structured extraction |
| **Tool** | `Agent[A,B] → Tool[A,B]` | T+J | 🔄 Implicit | Tool-use wrapping |
| **Trace** | `Agent[A,B] → Agent[A,B]` | W | 🔄 Implicit | Observability wrapping |
| **Sandbox** | `Agent[A,B] → Agent[A,B]` | J | 🔄 Implicit | Safety isolation |
| **Flux** | `Agent[A,B] → Agent[Flux[A], Flux[B]]` | C | 🔄 Planned | Discrete → Continuous flow |
| **State** | `Agent[A,B] → StatefulAgent[S,A,B]` | D | ✅ Specified | State threading (monad) |

---

## 1. Promise Functor

**Signature:** `Promise: Agent[A, B] → Agent[A, Promise[B]]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × PromiseState, A, Promise[B]]`
where `PromiseState = { PENDING, RESOLVED, FAILED }`

**Transform:** Adds promise lifecycle state; defers computation until explicitly resolved.

**Laws:**
- Identity: `Promise(Id[A]) ≅ Id[Promise[A]]`
- Composition: `Promise(f >> g) ≅ Promise(f) >> Promise(map(g))`

**Status:** ✅ Fully documented in `spec/c-gents/functors.md` and `spec/j-gents/lazy.md`
**Impl:** `impl/claude/agents/j/promise.py`

---

## 2. View Functor

**Signature:** `View: Agent[A, B] → Widget[Agent[A, B]]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[WidgetState, UIEvent, WidgetOutput]`
where `WidgetState = { INITIAL, LOADING, DISPLAYING, ERROR }`

**Transform:** Maps agent state to widget lifecycle; agent inputs become UI events. View is a **quotient morphism** collapsing agent state to visible widget state.

**Laws:**
- Identity preservation: `View(Id)` produces `GlyphWidget(Id)`
- Composition visualization: `View(f >> g)` produces `GraphWidget([View(f), View(g)])`

**Key Insight:** Form reveals function—widget ontology corresponds to agent behavioral patterns.

**Status:** 🔄 Implicit (fully specified in `spec/i-gents/view-functor.md` but not in catalog)

---

## 3. Metered Functor

**Signature:** `Metered: Agent[A, B] → Transaction[A, B]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × BudgetState, A, (B, Receipt)]`
where `BudgetState = { AVAILABLE(tokens), EXHAUSTED, RATE_LIMITED }`

**Transform:** Adds economic state; transitions blocked if budget exhausted. Budget is a **linear resource**—the polynomial fiber at EXHAUSTED has no valid directions.

**Laws:**
- Cost preservation: `cost(Metered(f).invoke(x)) == cost(f.invoke(x))`
- Composition economics: `Metered(f >> g) ≡ Metered(f) >> Metered(g)`

**Key Insight:** Linear types—tokens cannot be copied, only spent.

**Status:** 🔄 Implicit (described in `spec/b-gents/banker.md`)

---

## 4. Personalization Functor

**Signature:** `K: Agent[A, B] → Agent[A, B]` (same signature, personalized behavior)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S ∩ SoulCompatible, A, B]`
where `SoulCompatible = { s ∈ S | eigenvector_alignment(s) ≥ threshold }`

**Transform:** Filters positions to soul-compatible subset (sheaf restriction). K-functor selects the fiber compatible with eigenvector context.

**Connection to SOUL_SHEAF:**
```python
K(agent, AESTHETIC) = SOUL_SHEAF.restrict(agent, AESTHETIC)
```

**Laws:**
- Identity: `K(Id) ≅ Id`
- Composition: `K(f >> g) ≅ K(f) >> K(g)`

**Key Insight:** Personality as field—not stored preferences, but the shape of the space itself. K-gent is the fixed point: `K = Fix(λsystem. developer_adapts(system))`

**Status:** 🔄 Implicit (described in `spec/k-gent/README.md`)

---

## 5. Lens Functor

**Signature:** `Lens[S, A]: (get: S → A, set: (S, A) → S)` (bidirectional)

**Polynomial:** Bidirectional morphism with forward (get) and backward (set) maps.
- Forward: `P(y) = Σ_{s ∈ S} y^{Get(s)}`
- Backward: `P(y) = Σ_{s ∈ S} y^{Set(s)}`

**Transform:** Focus on sub-parts while preserving update capability.

**Laws:**
- GetPut: `lens.set(state, lens.get(state)) == state`
- PutGet: `lens.get(lens.set(state, value)) == value`
- PutPut: `lens.set(lens.set(state, v1), v2) == lens.set(state, v2)`

**Composition:**
```python
(lens1 >> lens2).get(state) == lens2.get(lens1.get(state))
(lens1 >> lens2).set(state, val) == lens1.set(state, lens2.set(lens1.get(state), val))
```

**Status:** 🔄 Implicit (documented in `spec/d-gents/lenses.md`)

---

## 6. Optimization Endofunctor

**Signature:** `R: Agent[A, B] → Agent'[A, B]` (same signature, optimized prompts)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S, A, B]` (identical structure)

**Transform:** Pure endofunctor—only changes transition function implementation (the prompt), not the polynomial structure. Optimization within a fiber.

**Laws:**
- Identity: `R(Id) ≅ Id`
- Composition: `R(f >> g) ≅ R(f) >> R(g)` or optimize pipeline as unit
- Monotonicity: `Loss(R(agent)) ≤ Loss(agent)`

**Key Insight:** Unique among all kgents functors—preserves entire polynomial structure, operates on "implementation" not "interface."

**Status:** 🔄 Implicit (see Refine functor pattern)

---

## 7. Spy Functor

**Signature:** `Spy: Agent[A, A] → Agent[A, A]` (identity with logging)

**Polynomial:** `PolyAgent[S, A, A] → PolyAgent[S × History, A, A]`
where `History = List[(timestamp, input, output)]`

**Transform:** Adds writer fiber—history is a monoid that accumulates across transitions. This is the categorical Writer monad applied to polynomials.

**Laws:**
- Identity: `Spy(label).invoke(x) == x` (value unchanged)
- Composition transparency: `(f >> Spy(label) >> g) ≡ (f >> g)` (semantically)
- History accumulation: `len(Spy.history)` increases with each invocation

**Key Insight:** Writer monad specialized to identity—accumulates log while passing values through.

**Status:** 🔄 Implicit (described in `spec/t-gents/taxonomy.md`)

---

## 8. Mock Functor

**Signature:** `Mock: Agent[A, B] → Agent[A, B]` (constant output, ignores input)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[Unit, Any, B]` (single-state, constant-output)

**Transform:** Terminal morphism—maps any polynomial to constant polynomial `P(y) = B`. Factors through terminal object.

**Laws:**
- Constancy: `Mock(b).invoke(a1) == Mock(b).invoke(a2)` for all `a1, a2`
- Identity absorption: `Mock(b) >> f ≠ f` unless f is also constant
- Delay simulation: `time(Mock(b, delay=t).invoke(x)) ≈ t`

**Key Insight:** Categorical constant—collapses all inputs to single output.

**Status:** 🔄 Implicit (described in `spec/t-gents/taxonomy.md`)

---

## 9. Parser Functor

**Signature:** `Parser: Text → ParseResult[A]`
where `ParseResult[A] = Success(value: A, confidence: float) | Failure(error)`

**Polynomial:** `PolyAgent[ParseState, Text, ParseResult[A]]`
where `ParseState = { READY, PARSING, REPAIRING, COMPLETE, FAILED }`

**Transform:** Non-trivial state machine—polynomial captures retry logic and repair strategies as explicit positions.

**Laws:**
- Determinism: `Parser(strategy).parse(text) == Parser(strategy).parse(text)`
- Composition (fallback): `(p1 | p2 | p3).parse(text)` returns first successful parse
- Fusion (parallel merge): `Fuse(p1, p2).parse(text)` merges results from both

**Key Insight:** Stochastic-structural gap—traditional parsers assume deterministic syntax; P-gents handle LLM sampling distributions.

**Status:** 🔄 Implicit (described in `spec/p-gents/README.md`)

---

## 10. Tool Functor

**Signature:** `Tool: Agent[A, B] → Tool[A, B]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × ToolState, A, Result[B, ToolError]]`
where `ToolState = { READY, CHECKING_CAPS, EXECUTING, SANDBOXED }`

**Transform:** Adds capability-gated directions—some inputs not in fiber if capabilities missing.

**Laws:**
- Interface preservation: `Tool(agent).invoke(x)` same semantics as `agent.invoke(x)` (wrapped in Result)
- Composition: `Tool(f >> g) ≅ Tool(f) >> Tool(g)`
- Capability enforcement: Missing capabilities → ToolError

**Key Insight:** Tool-use bridge enabling agents to be invoked via MCP, Claude Desktop, or other protocols.

**Status:** 🔄 Implicit (Phase 2 in `spec/u-gents/tool-use.md`)
**Impl:** `impl/claude/agents/j/t_integration.py`

---

## 11. Trace Functor

**Signature:** `Trace: Agent[A, B] → Agent[A, B]` (with observability side effects)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × TraceState, A, B]`
where `TraceState = { TRACING(wire_id), EMITTING, IDLE }`

**Transform:** Side-effecting endofunctor—adds positions for emission state but observable output unchanged. Contrast with Spy: Trace is ephemeral (emits externally), Spy persists (accumulates internally).

**Laws:**
- Transparency: `Trace(agent).invoke(x) == agent.invoke(x)` (ignoring wire emissions)
- Composition: `Trace(f >> g) ≅ Trace(f) >> Trace(g)`
- Ephemerality: Wire stops → all traces vanish (no persistence)

**Key Insight:** Ephemeral observability via Wire protocol, no internal trace.

**Status:** 🔄 Implicit (described in `spec/w-gents/README.md`)

---

## 12. Sandbox Functor

**Signature:** `Sandbox: Agent[A, B] → Agent[A, B]` (isolated execution)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × Namespace, A, Result[B, SandboxError]]`
where `Namespace = isolated execution context`

**Transform:** Filtering functor with namespace fiber—direction set shrinks based on sandbox policy, each transition gets fresh namespace.

**Laws:**
- Safety: `Sandbox(agent, forbidden=["os"]).invoke(x)` → Error if agent attempts os access
- Transparency (safe agents): If no violations, `Sandbox(agent).invoke(x) == agent.invoke(x)`
- Composition isolation: Each `Sandbox(agent)` executes in fresh namespace

**Key Insight:** Safety as functor constraint.

**Status:** 🔄 Implicit (described in `spec/j-gents/jit.md`)

---

## 13. Flux Functor

**Signature:** `Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]`
where `Flux[T] = AsyncIterator[T]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × FluxState, Stream[A], Stream[B]]`
where `FluxState = { DORMANT, FLOWING(queue, backpressure), DRAINING, STOPPED }`

**Transform:** Continuous extension—lifts discrete polynomial dynamics to continuous-time. The polynomial becomes a **streaming polynomial** where each fiber is an async stream.

**Dual mode via perturbation:**
- DORMANT: `invoke(x)` → direct discrete call
- FLOWING: `invoke(x)` → inject x as high-priority perturbation

**Laws:**
- Identity: `Flux(Id) ≅ Id_Flux`
- Composition: `Flux(f >> g) ≅ Flux(f) >> Flux(g)`

**Key Insight:** Operationalizes *"The noun is a lie. There is only the rate of change."*

```
Static:  Agent: A → B           (point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (continuous flow)
```

**Living Pipelines:**
```python
pipeline = flux_a | flux_b | flux_c
async for result in pipeline.start(source):
    ...
```

**Status:** 🔄 Planned (spec in `spec/c-gents/flux.md`)
**Impl:** `impl/claude/agents/flux/`

---

## 14. State Functor

**Signature:** `State[S]: Agent[A, B] → StatefulAgent[S, A, B]`

**Polynomial:** `PolyAgent[P, A, B] → PolyAgent[P × LoadSave, A, B]`
where `LoadSave = { LOADING, READY, SAVING }`

**Transform:** Adds monad fiber—state S flows through computation as monad, with load/save as effect handlers.

### Core Insight: State Threading

State is orthogonal to persistence:
- **D-gent**: WHERE state lives (memory, file, database)
- **State Functor**: HOW state threads through computation

The State Functor lifts agents into stateful computation where state is:
1. Loaded before each invocation
2. Threaded through the computation
3. Saved after each invocation

```python
@dataclass
class StateFunctor(Generic[S]):
    """State Monad as first-class functor."""
    state_type: type[S]
    backend: DgentProtocol  # WHERE state lives
    initial_state: S | None = None

    def lift(self, agent: Agent[A, B]) -> StatefulAgent[S, A, B]:
        """Lift agent into stateful computation."""
        return StatefulAgent(inner=agent, backend=self.backend, ...)

    def lift_logic(self, logic: Callable[[A, S], tuple[B, S]]) -> StatefulAgent[S, A, B]:
        """Lift pure logic function directly (the Symbiont pattern)."""
        return self.lift(_LogicAgent(logic))
```

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `StateFunctor.lift(Id) ≅ Id` | `test_state_identity_law` |
| Composition | `lift(f >> g) ≅ lift(f) >> lift(g)` | `test_state_composition_law` |

**Proof Sketch (Identity):**
1. `StateFunctor.lift(Id)` wraps identity in StatefulAgent
2. `StatefulAgent.invoke(a)` loads S, calls `Id(a, S)` → `(a, S)`, saves S, returns a
3. Net effect: input a → output a ≡ Id (modulo state I/O overhead)

**Proof Sketch (Composition):**
- LHS `lift(f >> g)`: Single load/save, sequential invoke
- RHS `lift(f) >> lift(g)`: Two load/save cycles
- Both produce same final state S₂ and output c
- Behavioral equivalence (intermediate saves are implementation detail)

### The Symbiont Pattern (Canonical Usage)

**Symbiont IS StateFunctor.lift_logic with a D-gent backend:**

```python
# These are equivalent:
symbiont = Symbiont(logic=chat_logic, memory=dgent_memory)

stateful = StateFunctor(
    state_type=ConversationState,
    backend=dgent_memory,
).lift_logic(chat_logic)
```

Symbiont is the **ergonomic pattern**; StateFunctor is the **formal functor**.
Use Symbiont for direct usage; use StateFunctor when you need:
- Flux composition (`StateFunctor.compose_flux`)
- Law verification
- Functor registry integration

### Composition with Flux

```python
FluxState = StateFunctor.compose_flux(state_functor)
flux_stateful = FluxState(process_agent)

async for result in flux_stateful.start(event_source):
    # Each event: load state → process → save → yield
    print(result)
```

**Composition Hierarchy:**
```
Flux ∘ State ∘ D-gent
Level 3: Flux        — Continuous event processing
Level 2: State       — State threading
Level 1: D-gent      — Persistence substrate
Level 0: Pure logic  — (I, S) → (O, S)
```

### State Threading Invariants

1. **Load-Before-Invoke**: State always loaded before inner agent invocation
2. **Save-After-Complete**: State saved only after successful invocation
3. **State Isolation**: Each StatefulAgent has isolated state via namespace

### Anti-Patterns

- **State without persistence**: Use D-gent backend, not in-memory only
- **Bypassing state loading**: Always go through StatefulAgent.invoke()
- **Mutable state in logic**: Logic function must be pure `(A, S) → (B, S)`

**Status:** ✅ Specified (formerly `spec/s-gents/`, now consolidated here)
**Impl:** `impl/claude/agents/d/symbiont.py`
**Ergonomic Pattern:** `spec/d-gents/symbiont.md`

---

## Functor Composition Patterns

### Sequential Wrapping
```python
agent = base_agent
agent = K(agent)          # Personalize
agent = Metered(agent)    # Add economics
agent = Trace(agent)      # Add observability
agent = Sandbox(agent)    # Add safety
```

### Parallel Application
```python
# View and Trace simultaneously (different concerns)
widget = View(agent, context)
traced = Trace(agent)
```

### Conditional Functor Selection
```python
def wrap_agent(agent, mode):
    match mode:
        case "dev": return Trace(agent)
        case "test": return Mock(agent, test_output)
        case "prod": return Metered(Trace(agent))
```

---

## Anti-Patterns

### 1. Breaking Functor Laws
```python
# BAD: Optimization that degrades performance
R(agent) where Loss(R(agent)) > Loss(agent)  # Violates monotonicity

# BAD: Spy that modifies data
Spy(agent).invoke(x) != x  # Violates transparency
```

### 2. Implicit Functor Stacking
```python
# BAD: Hidden wrapping without documentation
def run_agent(agent):
    return Metered(Trace(Personalize(agent)))

# GOOD: Explicit composition
agent = K(agent)
agent = Trace(agent)
agent = Metered(agent)
```

### 3. Non-Commuting Functors
```python
# Order matters!
Metered(Trace(agent)) != Trace(Metered(agent))
# First: Measures traced execution cost
# Second: Traces metering overhead

# Always document order dependencies
```

---

## Implementation Reference

All functors follow polynomial endofunctor structure. See:

- `spec/c-gents/functors.md` - Core functor theory
- `spec/c-gents/monads.md` - Functors with structure
- `spec/architecture/polyfunctor.md` - Polyfunctor architecture
- `spec/agents/primitives.md` - 17 primitive polynomial agents
- `spec/agents/operads.md` - Operad composition grammar
- `spec/agents/emergence.md` - Sheaf-based emergence
- Individual genus specs for detailed descriptions

---

**Foundation:** `spec/architecture/polyfunctor.md` - The polynomial theory underlying all transformations
