# Agent Specifications

> *Agent genus specifications: functors, monads, composition patterns.*

---

## spec.agents.README

## agent_foundations

```python
spec Agent Foundations
```

Category theory is not a genus—it IS the foundation.

### Examples
```python
>>> ┌────────────────────────────────────────────────────────────────────┐
│  SHEAF       Global coherence from local views                     │
│              Emergence, gluing, consistency                        │
├────────────────────────────────────────────────────────────────────┤
│  OPERAD      Composition grammar with laws                         │
│              Operations, laws, verification                        │
├────────────────────────────────────────────────────────────────────┤
│  POLYAGENT   State machine with mode-dependent inputs              │
│              Positions, directions, transitions                    │
└────────────────────────────────────────────────────────────────────┘
```
```python
>>> impl/claude/agents/poly/       # PolyAgent, primitives
impl/claude/agents/operad/     # Operad, operations, laws
impl/claude/agents/sheaf/      # Sheaf, gluing, emergence
impl/claude/agents/c/          # C-gent categorical implementations
impl/claude/agents/flux/       # Flux functor
```

---

## core_abstractions

```python
spec Agent Foundations: Core Abstractions
```

| Document | Description | |----------|-------------| | [primitives.md](primitives.md) | The 17 irreducible polynomial agents | | [operads.md](operads.md) | Grammar of composition | | [composition.md](composition.md) | The `>>` operator and composition laws | | [functors.md](functors.md) | Structure-preserving transformations | | [functor-catalog.md](functor-catalog.md) | Catalog of all functors across genera | | [monads.md](monads.md) | Effect sequencing patterns | | [flux.md](flux.md) | Discre

---

## the_three_layers

```python
spec Agent Foundations: The Three Layers
```

Every domain-specific system instantiates this pattern:

### Examples
```python
>>> ┌────────────────────────────────────────────────────────────────────┐
│  SHEAF       Global coherence from local views                     │
│              Emergence, gluing, consistency                        │
├────────────────────────────────────────────────────────────────────┤
│  OPERAD      Composition grammar with laws                         │
│              Operations, laws, verification                        │
├────────────────────────────────────────────────────────────────────┤
│  POLYAGENT   State machine with mode-dependent inputs              │
│              Positions, directions, transitions                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## unified_foundation

```python
spec Agent Foundations: Unified Foundation
```

All kgents genera (B-gent, D-gent, K-gent, etc.) are built on these primitives:

---

## category_laws

```python
spec Agent Foundations: Category Laws
```

These laws are not aspirational—they are **verified**:

---

## genus_specific_extensions

```python
spec Agent Foundations: Genus-Specific Extensions
```

While the foundation is universal, each genus extends it:

---

## see_also

```python
spec Agent Foundations: See Also
```

- `spec/principles.md` — The seven principles (especially §5 Composable) - `spec/bootstrap.md` — The irreducible kernel - `spec/architecture/polyfunctor.md` — Polyfunctor architecture

---

## spec.agents.composition

## agent_composition

```python
spec Agent Composition
```

Composition is at the very root of category theory—it's part of the definition of the category itself.

### Examples
```python
>>> Given: Agent f: A → B, Agent g: B → C
Composition: (g ∘ f): A → C
```
```python
>>> (f >> g) >> h ≡ f >> (g >> h)
```
```python
>>> Id >> f ≡ f ≡ f >> Id
```
```python
>>> If f: A → B and g: B → C, then (f >> g): A → C
```
```python
>>> f: String → Number
g: Number → Boolean
(f >> g): String → Boolean  ✓
```

---

## the_essence

```python
spec Agent Composition: The Essence
```

Agents are morphisms. Composition is how morphisms combine.

### Examples
```python
>>> Given: Agent f: A → B, Agent g: B → C
Composition: (g ∘ f): A → C
```

---

## type_compatibility

```python
spec Agent Composition: Type Compatibility
```

For composition to be valid, f's output type MUST be compatible with g's input type:

### Examples
```python
>>> f: String → Number
g: Number → Boolean
(f >> g): String → Boolean  ✓
```

---

## sequential_composition

```python
spec Agent Composition: Sequential Composition
```

The `>>` operator chains agents sequentially:

### Examples
```python
>>> pipeline = parse >> validate >> transform >> format
result = await pipeline.invoke(input)
```

---

## parallel_composition

```python
spec Agent Composition: Parallel Composition
```

Run multiple agents concurrently on the same input:

### Examples
```python
>>> ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
```

---

## conditional_composition

```python
spec Agent Composition: Conditional Composition
```

Branch based on runtime predicates:

### Examples
```python
>>> input → [predicate?] → [A] if true
                      → [B] if false
```

---

## graph_composition

```python
spec Agent Composition: Graph Composition
```

Extend pipelines to directed acyclic graphs (DAGs):

### Examples
```python
>>> Graph Composition = Compose + Fix + Conditional
```

---

## the_curry_howard_correspondence

```python
spec Agent Composition: The Curry-Howard Correspondence
```

We treat the **System Prompt** as a **Type Signature**. The agent's output must be a valid *inhabitant* of that type.

---

## composition_vs_operad

```python
spec Agent Composition: Composition vs Operad
```

**Composition** is the binary operation: `f >> g`.

---

## see_also

```python
spec Agent Composition: See Also
```

- [operads.md](operads.md) — Grammar of composition - [primitives.md](primitives.md) — The 17 atomic agents - [functors.md](functors.md) — Structure-preserving transformations - [flux.md](flux.md) — Discrete → Continuous lifting

---

## spec.agents.d-gent

## d_gent_the_data_agent

```python
spec D-gent: The Data Agent
```

The cortex is singular. Memory is global. Context is local.

### Examples
```python
>>> @dataclass(frozen=True)
class Datum:
    id: str                      # UUID or content-addressed hash
    content: bytes               # Schema-free payload
    created_at: float            # Unix timestamp
    causal_parent: str | None    # Enables lineage tracing
    metadata: dict[str, str]     # Optional tags
```
```python
>>> class DgentProtocol(Protocol):
    async def put(self, datum: Datum) -> str: ...      # Store, return ID
    async def get(self, id: str) -> Datum | None: ...  # Retrieve by ID
    async def delete(self, id: str) -> bool: ...       # Remove, return success
    async def list(self, prefix: str | None = None, after: float | None = None, limit: int = 100) -> list[Datum]: ...
    async def causal_chain(self, id: str) -> list[Datum]: ...  # Trace ancestry
```
```python
>>> Tier 0: Memory     → Ephemeral, fastest (~1μs)
Tier 1: JSONL      → Simple file, append-only (~1ms)
Tier 2: SQLite     → Local database, concurrent reads (~5ms)
Tier 3: Postgres   → Production database, ACID (~10ms)
```
```python
>>> router = DgentRouter(namespace="brain", preferred=Backend.SQLITE)
await router.put(datum)  # Routes to best available backend
```
```python
>>> Symbiont[I, O, S] = StateFunctor.lift_logic(f) where backend is D-gent
```

### Things to Know

⚠️ **Note:** Anti-pattern: ❌ Hardcoded paths

⚠️ **Note:** Anti-pattern: ❌ Multiple databases per project

⚠️ **Note:** Anti-pattern: ❌ Direct file I/O

⚠️ **Note:** Anti-pattern: ❌ Bypassing Symbiont state threading

🚨 **Critical:** Law (GetPut): lens.set(s, lens.get(s)) == s

🚨 **Critical:** Law (PutGet): lens.get(lens.set(s, a)) == a

🚨 **Critical:** Law (PutPut): lens.set(lens.set(s, a), b) == lens.set(s, b)

🚨 **Critical:** Law (Functor): spec/agents/functor-catalog.md` §14 (State Functor)

---

## purpose

```python
spec D-gent: The Data Agent: Purpose
```

D-gent owns all persistence for kgents. It is **Layer 0** of the Metaphysical Fullstack—the foundation upon which services build. D-gent is infrastructure, not a Crown Jewel.

---

## xdg_compliance

```python
spec D-gent: The Data Agent: XDG Compliance
```

| Purpose | Path | Env Variable | |---------|------|--------------| | Config | `~/.config/kgents/` | `XDG_CONFIG_HOME` | | Data | `~/.local/share/kgents/` | `XDG_DATA_HOME` | | Cache | `~/.cache/kgents/` | `XDG_CACHE_HOME` |

---

## symbiont_state_threading

```python
spec D-gent: The Data Agent: Symbiont: State Threading
```

Fuses stateless logic with stateful memory.

### Examples
```python
>>> Symbiont[I, O, S] = StateFunctor.lift_logic(f) where backend is D-gent
```
```python
>>> def chat_logic(msg: str, history: list) -> tuple[str, list]:
    """Pure function: (input, state) → (output, new_state)"""
    history.append(("user", msg))
    response = generate(history)
    history.append(("bot", response))
    return response, history

memory = VolatileAgent(_state=[])
chatbot = Symbiont(logic=chat_logic, memory=memory)
await chatbot.invoke("Hello")  # State threaded automatically
```

---

## lenses_focused_state_access

```python
spec D-gent: The Data Agent: Lenses: Focused State Access
```

Compositional getter/setter pairs for sub-state access.

### Examples
```python
>>> Lens[S, A] = (get: S → A, set: (S, A) → S)
```
```python
>>> global_dgent = PersistentAgent[GlobalState](...)
user_dgent = LensAgent(global_dgent, user_lens)  # Sees only user slice
```

---

## databus_integration

```python
spec D-gent: The Data Agent: DataBus Integration
```

D-gent emits events on state changes:

### Examples
```python
>>> class DataEventType(Enum):
    CREATED = auto()
    UPDATED = auto()
    DELETED = auto()

@dataclass
class DataEvent:
    event_type: DataEventType
    datum_id: str
    namespace: str
    timestamp: float
```

---

## dual_protocol_design

```python
spec D-gent: The Data Agent: Dual Protocol Design
```

D-gent provides **two complementary protocols** for different use cases:

---

## spec.agents.emergence

## agent_emergence_from_local_to_global_via_sheaves

```python
spec Agent Emergence: From Local to Global via Sheaves
```

A sheaf is defined as a presheaf satisfying locality and gluing conditions, ensuring coherent global structure while preserving local properties.

### Examples
```python
>>> AgentSheaf[Ctx] = (
    contexts: Set[Ctx],                    # Observation contexts
    overlap: Ctx × Ctx → Ctx | None,       # Context intersection
    restrict: Agent × Ctx → Agent,         # Global → Local
    compatible: Dict[Ctx, Agent] → bool,   # Check agreement
    glue: Dict[Ctx, Agent] → Agent         # EMERGENCE: Local → Global
)
```
```python
>>> @dataclass(frozen=True)
class Context:
    name: str
    capabilities: FrozenSet[str] = frozenset()
    parent: str | None = None
```
```python
>>> def restrict(
    agent: PolyAgent,
    subcontext: Ctx,
    position_filter: Callable[[Any, Ctx], bool] | None = None,
) → PolyAgent
```
```python
>>> restrict(restrict(a, C1), C2) = restrict(a, C1 ∩ C2)
```
```python
>>> def compatible(
    locals: dict[Ctx, PolyAgent],
    equivalence: Callable[[Any, Any], bool] | None = None,
) → bool
```

---

## status

```python
spec Agent Emergence: From Local to Global via Sheaves: Status
```

**Version**: 1.0 **Status**: Canonical **Implementation**: `impl/claude/agents/sheaf/` **Tests**: Verified via `test_emergence.py`

---

## overview

```python
spec Agent Emergence: From Local to Global via Sheaves: Overview
```

A **sheaf** captures the mathematical structure of **emergence**:

---

## soul_sheaf_emergence_of_kent_soul

```python
spec Agent Emergence: From Local to Global via Sheaves: Soul Sheaf: Emergence of Kent Soul
```

The canonical example is **SOUL_SHEAF**, which glues 6 eigenvector-local souls into one emergent Kent Soul.

---

## theory_background

```python
spec Agent Emergence: From Local to Global via Sheaves: Theory Background
```

From [Mac Lane & Moerdijk, "Sheaves in Geometry and Logic"](https://www.cambridge.org/core/books/sheaves-in-geometry-and-logic/):

---

## spec.agents.flux

## flux_discrete_to_continuous

```python
spec Flux: Discrete to Continuous
```

The noun is a lie. There is only the rate of change.

### Examples
```python
>>> result = await agent.invoke(input)  # Discrete: twitch, return, die
```
```python
>>> async for result in flux_agent.start(source):  # Continuous: live, respond, flow
    ...
```
```python
>>> Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]
```
```python
>>> # BAD: Output vanishes
async def start(self, source) -> None:
    async for event in source:
        result = await self.invoke(event)  # result goes... where?

# GOOD: Output flows
async def start(self, source) -> AsyncIterator[B]:
    async for event in source:
        yield await self.invoke(event)  # Living Pipeline enabled
```
```python
>>> # BAD: Zombie on a timer
while True:
    await asyncio.sleep(1.0)  # twitch

# GOOD: Respond to events
async for event in source:
    yield await self.invoke(event)  # live
```

---

## the_insight

```python
spec Flux: Discrete to Continuous: The Insight
```

Agents are corpses. They only move when poked.

### Examples
```python
>>> result = await agent.invoke(input)  # Discrete: twitch, return, die
```
```python
>>> async for result in flux_agent.start(source):  # Continuous: live, respond, flow
    ...
```

---

## the_perturbation_principle

```python
spec Flux: Discrete to Continuous: The Perturbation Principle
```

When `invoke()` is called on a FLOWING flux:

---

## flux_topology

```python
spec Flux: Discrete to Continuous: Flux Topology
```

Agents are topological knots in event streams:

---

## relationship_to_bootstrap

```python
spec Flux: Discrete to Continuous: Relationship to Bootstrap
```

**Flux is derived from Fix**, not irreducible:

### Examples
```python
>>> Flux(agent) ≅ Fix(
    transform=lambda stream: map_async(agent.invoke, stream),
    equality_check=lambda s1, s2: s1.exhausted and s2.exhausted
)
```

---

## relationship_to_symbiont

```python
spec Flux: Discrete to Continuous: Relationship to Symbiont
```

| Pattern | Threads | Domain | |---------|---------|--------| | **Symbiont** | State (S) | Space | | **Flux** | Time (Δt) | Time |

---

## archetypes_as_flux

```python
spec Flux: Discrete to Continuous: Archetypes as Flux
```

| Archetype | Flux Configuration | |-----------|-------------------| | Consolidator | `source=idle_signal` | | Spawner | Flux emitting child FluxAgents | | Witness | `Flux(Id)` with trace | | Dialectician | `feedback_fraction=0.5` |

---

## see_also

```python
spec Flux: Discrete to Continuous: See Also
```

- [functor-catalog.md](functor-catalog.md) §13 — Flux in functor catalog - [composition.md](composition.md) — Sequential composition foundation - `spec/principles.md` §6 — Heterarchical Principle, Flux Topology - `spec/archetypes.md` — Archetypes as Flux configurations

---

## spec.agents.functor-catalog

## purpose

```python
spec Functor Catalog: kgents Transformation Patterns: Purpose
```

This catalog formalizes functor patterns across the kgents ecosystem. Many agent transformations follow functor laws but weren't explicitly documented as such. This reference makes them explicit, enabling systematic reasoning about agent transformations across genera.

---

## core_insight

```python
spec Functor Catalog: kgents Transformation Patterns: Core Insight
```

Every agent transformation is a polynomial endofunctor that modifies positions (state space), directions (inputs), or transitions (dynamics).

---

## polynomial_functor_summary

```python
spec Functor Catalog: kgents Transformation Patterns: Polynomial Functor Summary
```

Each functor transforms a polynomial agent `P(y) = Σ_{s ∈ S} y^{E(s)}` according to how it modifies positions (S), directions (E), and transitions.

---

## functor_quick_reference

```python
spec Functor Catalog: kgents Transformation Patterns: Functor Quick Reference
```

| Functor | Signature | Genus | Status | Description | |---------|-----------|-------|--------|-------------| | **Promise** | `A → Promise[A]` | J, C | ✅ Documented | Lazy computation deferral | | **View** | `Agent[A,B] → Widget` | I | 🔄 Implicit | Visual representation | | **Metered** | `Agent[A,B] → Transaction[A,B]` | B | 🔄 Implicit | Economic wrapping | | **Personalization** | `Agent[A,B] → Agent[A,B]` | K | 🔄 Implicit | Personality field application | | **Lens** | `S → A` (bidirectional) | 

---

## 1_promise_functor

```python
spec Functor Catalog: kgents Transformation Patterns: 1. Promise Functor
```

**Signature:** `Promise: Agent[A, B] → Agent[A, Promise[B]]`

---

## 2_view_functor

```python
spec Functor Catalog: kgents Transformation Patterns: 2. View Functor
```

**Signature:** `View: Agent[A, B] → Widget[Agent[A, B]]`

---

## 3_metered_functor

```python
spec Functor Catalog: kgents Transformation Patterns: 3. Metered Functor
```

**Signature:** `Metered: Agent[A, B] → Transaction[A, B]`

---

## 4_personalization_functor_k_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 4. Personalization Functor (K-gent)
```

**Signature:** `K: Agent[A, B] → Agent[A, B]` (same signature, personalized behavior)

---

## 5_lens_functor

```python
spec Functor Catalog: kgents Transformation Patterns: 5. Lens Functor
```

**Signature:** `Lens[S, A]: (get: S → A, set: (S, A) → S)` (bidirectional)

### Examples
```python
>>> (lens1 >> lens2).get(state) == lens2.get(lens1.get(state))
```

---

## 6_optimization_endofunctor_r_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 6. Optimization Endofunctor (R-gent)
```

**Signature:** `R: Agent[A, B] → Agent'[A, B]` (same signature, optimized prompts)

---

## 7_spy_functor_t_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 7. Spy Functor (T-gent)
```

**Signature:** `Spy: Agent[A, A] → Agent[A, A]` (identity with logging)

---

## 8_mock_functor_t_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 8. Mock Functor (T-gent)
```

**Signature:** `Mock: Agent[A, B] → Agent[A, B]` (constant output, ignores input)

---

## 9_parser_functor_p_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 9. Parser Functor (P-gent)
```

**Signature:** `Parser: Text → ParseResult[A]`

---

## 10_tool_functor_u_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 10. Tool Functor (U-gent)
```

**Signature:** `Tool: Agent[A, B] → Tool[A, B]`

---

## 11_trace_functor_w_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 11. Trace Functor (W-gent)
```

**Signature:** `Trace: Agent[A, B] → Agent[A, B]` (with observability side effects)

---

## 12_sandbox_functor_j_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 12. Sandbox Functor (J-gent)
```

**Signature:** `Sandbox: Agent[A, B] → Agent[A, B]` (isolated execution)

---

## 13_flux_functor

```python
spec Functor Catalog: kgents Transformation Patterns: 13. Flux Functor
```

**Signature:** `Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]` where `Flux[T] = AsyncIterator[T]`

---

## 14_state_functor_d_gent

```python
spec Functor Catalog: kgents Transformation Patterns: 14. State Functor (D-gent)
```

**Signature:** `State[S]: Agent[A, B] → StatefulAgent[S, A, B]`

---

## spec.agents.functors

## functors

```python
spec Functors
```

A functor is a structure-preserving map between categories.

### Examples
```python
>>> F: Category C → Category D
```
```python
>>> F(id_A) = id_F(A)
```
```python
>>> F(g ∘ f) = F(g) ∘ F(f)
```
```python
>>> Traditional: F: Agent[A, B] → Agent[A', B']
Polynomial:  F: PolyAgent[S, A, B] → PolyAgent[S', A', B']
```
```python
>>> Agent: A → B
MaybeAgent: Maybe[A] → Maybe[B]

If input is Nothing: output is Nothing
If input is Just(a): output is Just(agent.invoke(a))
```

---

## definition

```python
spec Functors: Definition
```

A **functor** maps agents from one category to another while preserving composition:

### Examples
```python
>>> F: Category C → Category D
```

---

## functor_categories

```python
spec Functors: Functor Categories
```

| Category | State Transform | Direction Transform | Transition Transform | |----------|-----------------|---------------------|----------------------| | **Lifting** | Add states | Wrap types | Wrap dynamics | | **Filtering** | Restrict states | Restrict inputs | Guard transitions | | **Observing** | Add observation state | Identity | Emit side effects | | **Economizing** | Add budget state | Identity | Meter transitions |

---

## common_functors

```python
spec Functors: Common Functors
```

| Functor | Signature | Purpose | |---------|-----------|---------| | Maybe | `Agent[A,B] → Agent[Maybe[A], Maybe[B]]` | Handle optional values | | Either | `Agent[A,B] → Agent[A, Either[E,B]]` | Carry error information | | Async | `Agent[A,B] → Agent[A, Awaitable[B]]` | Non-blocking execution | | Logged | `Agent[A,B] → Agent[A, B]` + side effect | Add observability | | Promise | `Agent[A,B] → Agent[A, Promise[B]]` | Defer computation |

---

## universal_functor_protocol_ad_001

```python
spec Functors: Universal Functor Protocol (AD-001)
```

All functor-like patterns derive from `UniversalFunctor`:

### Examples
```python
>>> class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

---

## laws_in_polynomial_terms

```python
spec Functors: Laws in Polynomial Terms
```

**Identity Preservation** (polynomial):

### Examples
```python
>>> F(Id_P) = Id_{F(P)}
```
```python
>>> F(P ∘ Q) = F(P) ∘ F(Q)
```

---

## see_also

```python
spec Functors: See Also
```

- [functor-catalog.md](functor-catalog.md) — Complete catalog with polynomial interpretations - [composition.md](composition.md) — Agent composition - [monads.md](monads.md) — Functors with structure - [primitives.md](primitives.md) — 17 primitive polynomial agents - `spec/architecture/polyfunctor.md` — Polyfunctor architecture

---

## spec.agents.monads

## monads

```python
spec Monads
```

A monad is just a monoid in the category of endofunctors.

### Examples
```python
>>> unit: A → M[A]
```
```python
>>> bind: M[A] → (A → M[B]) → M[B]
```
```python
>>> unit(a).bind(f) ≡ f(a)
```
```python
>>> m.bind(unit) ≡ m
```
```python
>>> m.bind(f).bind(g) ≡ m.bind(a → f(a).bind(g))
```

### Things to Know

🚨 **Critical:** Law (Identity): StateFunctor.lift(Id) ≅ Id

🚨 **Critical:** Law (Composition): lift(f >> g) ≅ lift(f) >> lift(g)

---

## definition

```python
spec Monads: Definition
```

A **monad** is a functor with additional structure that allows sequencing computations with context.

---

## why_monads_matter_for_agents

```python
spec Monads: Why Monads Matter for Agents
```

**Without monads**, composing effectful agents is awkward:

### Examples
```python
>>> result1 = agent1.invoke(input)
if result1.is_error: return result1
result2 = agent2.invoke(result1.value)
if result2.is_error: return result2
...
```
```python
>>> agent1.bind(agent2).bind(agent3).invoke(input)
```

---

## the_state_monad_in_detail

```python
spec Monads: The State Monad in Detail
```

**Signature**: `State[S]: Agent[A, B] → StatefulAgent[S, A, B]`

---

## monad_transformers

```python
spec Monads: Monad Transformers
```

Stack multiple monads:

---

## monads_in_kgents

```python
spec Monads: Monads in kgents
```

| Monad | Use Case | Implementation | |-------|----------|----------------| | Maybe | Optional values | `agents/c/maybe.py` | | Either | Error handling | `agents/c/either.py` | | State | State threading | `agents/d/symbiont.py` | | Async | Async operations | Built-in |

---

## see_also

```python
spec Monads: See Also
```

- [composition.md](composition.md) — Basic composition - [functors.md](functors.md) — Structure-preserving maps - [functor-catalog.md](functor-catalog.md) — Functor catalog including State

---

## spec.agents.operads

## agent_operads_grammar_of_composition

```python
spec Agent Operads: Grammar of Composition
```

An operad O defines a theory or grammar of composition.

### Examples
```python
>>> @dataclass
class Operation:
    name: str                                    # Operation identifier
    arity: int                                   # Number of input agents
    signature: str                               # Type signature (for docs)
    compose: Callable[..., PolyAgent]           # Composition function
    description: str = ""
```
```python
>>> @dataclass
class Law:
    name: str                                    # Law identifier
    equation: str                                # Mathematical equation
    verify: Callable[..., LawVerification]      # Verification function
    description: str = ""
```
```python
>>> @dataclass
class Operad:
    name: str
    operations: dict[str, Operation]
    laws: list[Law]
    description: str = ""

    def compose(self, op_name: str, *agents) → PolyAgent
    def verify_law(self, law_name: str, *test_agents) → LawVerification
    def verify_all_laws(self, *test_agents) → list[LawVerification]
    def enumerate(self, primitives, depth, filter_fn) → list[PolyAgent]
```
```python
>>> seq(id, a) = a = seq(a, id)
```
```python
>>> shadow(dialectic(t, a)) = dialectic(shadow(t), shadow(a))
```

---

## status

```python
spec Agent Operads: Grammar of Composition: Status
```

**Version**: 1.0 **Status**: Canonical **Implementation**: `impl/claude/agents/operad/` **Tests**: Verified via `test_core.py`, `test_domains.py`, `test_properties.py`

---

## overview

```python
spec Agent Operads: Grammar of Composition: Overview
```

An **operad** makes composition rules explicit and programmable. Instead of hardcoded operators like `>>`, operads define:

---

## universal_agent_operad

```python
spec Agent Operads: Grammar of Composition: Universal Agent Operad
```

The **AGENT_OPERAD** is the base from which all domain operads derive.

---

## domain_operads

```python
spec Agent Operads: Grammar of Composition: Domain Operads
```

Domain operads **extend** AGENT_OPERAD with domain-specific operations.

---

## enumeration

```python
spec Agent Operads: Grammar of Composition: Enumeration
```

Operads can **enumerate** all valid compositions up to a depth:

---

## theory_background

```python
spec Agent Operads: Grammar of Composition: Theory Background
```

From [Spivak et al., "Operads for Complex System Design"](https://www.researchgate.net/publication/352685957):

---

## spec.agents.primitives

## agent_primitives_the_17_atomic_agents

```python
spec Agent Primitives: The 17 Atomic Agents
```

From 17 atoms, all agents emerge.

### Examples
```python
>>> ID: PolyAgent[str, Any, Any]
  positions: {"ready"}
  directions: λs → {Any}
  transition: λ(s, x) → ("ready", x)
```
```python
>>> GROUND: PolyAgent[GroundState, Any, dict]
  positions: {GROUNDED, FLOATING}
  directions: λs → {Any}
  transition: λ(s, x) → (GROUNDED|FLOATING, {grounded: bool, content: x})
```
```python
>>> FLOATING --[valid input]--> GROUNDED
FLOATING --[invalid input]--> FLOATING
```
```python
>>> JUDGE: PolyAgent[JudgeState, Claim, Verdict]
  positions: {DELIBERATING, DECIDED}
  directions: λs → {Claim} if s == DELIBERATING else {}
  transition: λ(s, claim) → (DECIDED, Verdict(claim, accepted, reasoning))
```
```python
>>> @dataclass(frozen=True)
class Claim:
    content: str
    confidence: float = 0.5

@dataclass(frozen=True)
class Verdict:
    claim: Claim
    accepted: bool
    reasoning: str
```

---

## status

```python
spec Agent Primitives: The 17 Atomic Agents: Status
```

**Version**: 1.0 **Status**: Canonical **Implementation**: `impl/claude/agents/poly/primitives.py` **Tests**: Verified via `test_primitives.py`

---

## overview

```python
spec Agent Primitives: The 17 Atomic Agents: Overview
```

Primitives are the irreducible building blocks from which all other agents are composed via operad operations. Each primitive is a `PolyAgent` with well-defined:

---

## primitive_categories

```python
spec Agent Primitives: The 17 Atomic Agents: Primitive Categories
```

| Category | Count | Purpose | |----------|-------|---------| | **Bootstrap** | 7 | Core composition and logic | | **Perception** | 3 | Observer-dependent interaction | | **Entropy** | 3 | Accursed Share / void.* | | **Memory** | 2 | D-gent persistence | | **Teleological** | 2 | Evolve + Narrate primitives |

---

## entropy_primitives_3

```python
spec Agent Primitives: The 17 Atomic Agents: Entropy Primitives (3)
```

These primitives interact with the **Accursed Share** (void.* context).

---

## memory_primitives_2

```python
spec Agent Primitives: The 17 Atomic Agents: Memory Primitives (2)
```

Foundation for D-gent (Data Agent).

---

## teleological_primitives_2

```python
spec Agent Primitives: The 17 Atomic Agents: Teleological Primitives (2)
```

Foundation for evolution and narrative patterns. Note: Originally designed for E-gent (Evolution, archived 2025-12-16) and N-gent (Narrative).

---

*83 symbols, 10 teaching moments*

*Generated by Living Docs — 2025-12-21*