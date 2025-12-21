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
| **Flux** | `Agent[A,B] → Agent[Flux[A], Flux[B]]` | C | ✅ Documented | Discrete → Continuous flow |
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

**Impl:** `impl/claude/agents/j/promise.py`

---

## 2. View Functor

**Signature:** `View: Agent[A, B] → Widget[Agent[A, B]]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[WidgetState, UIEvent, WidgetOutput]`
where `WidgetState = { INITIAL, LOADING, DISPLAYING, ERROR }`

**Transform:** Maps agent state to widget lifecycle; agent inputs become UI events.

**Key Insight:** Form reveals function—widget ontology corresponds to agent behavioral patterns.

---

## 3. Metered Functor

**Signature:** `Metered: Agent[A, B] → Transaction[A, B]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × BudgetState, A, (B, Receipt)]`
where `BudgetState = { AVAILABLE(tokens), EXHAUSTED, RATE_LIMITED }`

**Transform:** Adds economic state; transitions blocked if budget exhausted.

**Key Insight:** Linear types—tokens cannot be copied, only spent.

---

## 4. Personalization Functor (K-gent)

**Signature:** `K: Agent[A, B] → Agent[A, B]` (same signature, personalized behavior)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S ∩ SoulCompatible, A, B]`
where `SoulCompatible = { s ∈ S | eigenvector_alignment(s) ≥ threshold }`

**Transform:** Filters positions to soul-compatible subset (sheaf restriction).

**Key Insight:** Personality as field—not stored preferences, but the shape of the space itself.

---

## 5. Lens Functor

**Signature:** `Lens[S, A]: (get: S → A, set: (S, A) → S)` (bidirectional)

**Laws:**
- GetPut: `lens.set(state, lens.get(state)) == state`
- PutGet: `lens.get(lens.set(state, value)) == value`
- PutPut: `lens.set(lens.set(state, v1), v2) == lens.set(state, v2)`

**Composition:**
```python
(lens1 >> lens2).get(state) == lens2.get(lens1.get(state))
```

---

## 6. Optimization Endofunctor (R-gent)

**Signature:** `R: Agent[A, B] → Agent'[A, B]` (same signature, optimized prompts)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S, A, B]` (identical structure)

**Transform:** Pure endofunctor—only changes transition function implementation (the prompt), not the polynomial structure.

**Key Insight:** Unique among all kgents functors—preserves entire polynomial structure, operates on "implementation" not "interface."

---

## 7. Spy Functor (T-gent)

**Signature:** `Spy: Agent[A, A] → Agent[A, A]` (identity with logging)

**Polynomial:** `PolyAgent[S, A, A] → PolyAgent[S × History, A, A]`
where `History = List[(timestamp, input, output)]`

**Transform:** Adds writer fiber—history is a monoid that accumulates across transitions.

---

## 8. Mock Functor (T-gent)

**Signature:** `Mock: Agent[A, B] → Agent[A, B]` (constant output, ignores input)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[Unit, Any, B]` (single-state, constant-output)

**Transform:** Terminal morphism—maps any polynomial to constant polynomial.

---

## 9. Parser Functor (P-gent)

**Signature:** `Parser: Text → ParseResult[A]`

**Polynomial:** `PolyAgent[ParseState, Text, ParseResult[A]]`
where `ParseState = { READY, PARSING, REPAIRING, COMPLETE, FAILED }`

**Transform:** Non-trivial state machine—polynomial captures retry logic and repair strategies.

---

## 10. Tool Functor (U-gent)

**Signature:** `Tool: Agent[A, B] → Tool[A, B]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × ToolState, A, Result[B, ToolError]]`
where `ToolState = { READY, CHECKING_CAPS, EXECUTING, SANDBOXED }`

**Transform:** Adds capability-gated directions.

---

## 11. Trace Functor (W-gent)

**Signature:** `Trace: Agent[A, B] → Agent[A, B]` (with observability side effects)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × TraceState, A, B]`

**Transform:** Side-effecting endofunctor—adds positions for emission state but observable output unchanged.

---

## 12. Sandbox Functor (J-gent)

**Signature:** `Sandbox: Agent[A, B] → Agent[A, B]` (isolated execution)

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × Namespace, A, Result[B, SandboxError]]`

**Transform:** Filtering functor with namespace fiber.

---

## 13. Flux Functor

**Signature:** `Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]`
where `Flux[T] = AsyncIterator[T]`

**Polynomial:** `PolyAgent[S, A, B] → PolyAgent[S × FluxState, Stream[A], Stream[B]]`
where `FluxState = { DORMANT, FLOWING(queue, backpressure), DRAINING, STOPPED }`

**Transform:** Continuous extension—lifts discrete polynomial dynamics to continuous-time.

**Key Insight:** Operationalizes *"The noun is a lie. There is only the rate of change."*

See: [flux.md](flux.md) for full specification.

---

## 14. State Functor (D-gent)

**Signature:** `State[S]: Agent[A, B] → StatefulAgent[S, A, B]`

**Polynomial:** `PolyAgent[P, A, B] → PolyAgent[P × LoadSave, A, B]`
where `LoadSave = { LOADING, READY, SAVING }`

**Transform:** Adds monad fiber—state S flows through computation as monad.

See: [monads.md](monads.md) for State monad details.

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

### Order Matters

```python
# These are NOT equivalent:
Metered(Trace(agent))  # Measures traced execution cost
Trace(Metered(agent))  # Traces metering overhead
```

Always document order dependencies.

---

## Anti-Patterns

### Breaking Functor Laws

```python
# BAD: Optimization that degrades performance
R(agent) where Loss(R(agent)) > Loss(agent)

# BAD: Spy that modifies data
Spy(agent).invoke(x) != x
```

### Implicit Functor Stacking

```python
# BAD: Hidden wrapping
def run_agent(agent):
    return Metered(Trace(Personalize(agent)))

# GOOD: Explicit composition
agent = K(agent)
agent = Trace(agent)
agent = Metered(agent)
```

---

## Implementation Reference

- [functors.md](functors.md) — Core functor theory
- [monads.md](monads.md) — Functors with structure
- [primitives.md](primitives.md) — 17 primitive polynomial agents
- [operads.md](operads.md) — Operad composition grammar
- [emergence.md](emergence.md) — Sheaf-based emergence
- `spec/architecture/polyfunctor.md` — The polynomial theory

---

*"Every transformation is a functor. Every functor preserves structure."*
