---
context: concept
---

# Architecture Overview

> *"Agents are morphisms. Functors lift them. Polynomials generalize them. Operads compose them."*

This document provides a comprehensive overview of the kgents architecture.

---

## Table of Contents

1. [The Three Pillars](#the-three-pillars)
2. [Agent Categories](#agent-categories)
3. [The Functor System](#the-functor-system)
4. [Polynomial Architecture](#polynomial-architecture)
5. [The Meta-Construction System](#the-meta-construction-system)
6. [Agent Synergy Patterns](#agent-synergy-patterns)
7. [AGENTESE Runtime](#agentese-runtime)
8. [Infrastructure Layer](#infrastructure-layer)
9. [Metabolism (Entropy System)](#metabolism-entropy-system)
10. [Directory Structure](#directory-structure)
11. [Architectural Decisions](#architectural-decisions)

---

## The Three Pillars

```
┌─────────────────────────────────────────────────────────────────┐
│                        THE ALETHIC TRIAD                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     NUCLEUS     │      HALO       │         PROJECTOR           │
│   Pure Logic    │  Capabilities   │    Categorical Compiler     │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ Agent[A, B]     │ @Stateful       │ LocalProjector              │
│ invoke(a) → b   │ @Soulful        │ K8sProjector                │
│                 │ @Observable     │                             │
│                 │ @Streamable     │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

<details>
<summary>🌫️ Ghost: Why not microservices?</summary>

The obvious path was distributed services—each agent genus as its own deployable unit with REST APIs, message queues, service mesh. We had the K8s expertise. The architecture diagrams were drawn.

We chose AGENTESE + monorepo instead because:

1. **Composition breaks at network boundaries**. The `>>` operator can't cross HTTP without losing its categorical guarantees.
2. **Microservices optimize for team boundaries**, not semantic boundaries. Agents compose by meaning, not by org chart.
3. **The protocol IS the API**. AGENTESE paths work whether the agent is in-process or remote—deployment is an implementation detail, not an architectural one.

*"Tasteful > feature-complete"* — Microservices would have been feature-complete. AGENTESE is tasteful.

</details>

### 1. Nucleus (Pure Logic)

The irreducible transform. Every agent has a nucleus—the `invoke(a) → b` function that defines what it does.

### 2. Halo (Capabilities)

Declared capabilities that wrap the nucleus. Decorators like `@Stateful`, `@Soulful`, `@Observable`, `@Streamable` declare what the agent needs without implementing it.

### 3. Projector (Compiler)

The categorical compiler that makes potential actual. Takes Halo declarations and compiles them to runnable code (LocalProjector) or K8s manifests (K8sProjector).

---

## Agent Categories

### By Capability (Archetypes)

| Archetype | Capabilities | Use Case |
|-----------|--------------|----------|
| **Kappa** | All 4 | Production services |
| **Lambda** | Observable only | Lightweight processors |
| **Delta** | Stateful + Observable | Data handlers |

### By Function (Genera)

| Genus | Letter | Role | Polynomial |
|-------|--------|------|------------|
| Alethic | A | Architecture, functors | `ALETHIC_AGENT` |
| Category | C | Composition primitives | — |
| Data | D | State, memory | `MEMORY_POLYNOMIAL` |
| Evolution | E | Thermodynamic optimization | `EVOLUTION_POLYNOMIAL` |
| Flux | Flux | Streams, events | — |
| Interface | I | TUI, semantic fields | — |
| Kent | K | Persona, governance | `SOUL_POLYNOMIAL` |
| Lattice | L | Semantic registry | — |
| Testing | T | Types I-V | — |
| Utility | U | Tools, MCP | — |

---

## The Functor System

### Universal Functor Protocol (AD-001)

Every transformation in kgents is a functor:

```python
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

### Built-in Functors

| Functor | Effect | Use Case |
|---------|--------|----------|
| `Maybe` | Handle optional values | Nullable results |
| `Either` | Handle success/error | Error propagation |
| `List` | Process collections | Batch operations |
| `Fix` | Add retries | Resilience |
| `Logged` | Add observability | Debugging |
| `Soul` | Add K-gent governance | Ethical alignment |
| `Flux` | Enable streaming | Real-time processing |
| `Observer` | Add telemetry | Monitoring |
| `State` | Add memory | Stateful computation |

### Functor Composition

Functors compose into stacks:

```python
stack = compose_functors(LoggedFunctor, FixFunctor, SoulFunctor)
resilient_agent = stack(my_agent)
```

<details>
<summary>🌫️ Ghost: The Original Functor Zoo</summary>

Before AD-001 (Universal Functor Mandate), we had a zoo:

- `MaybeAgent` with its own `lift()`
- `EitherAgent` with a different `lift()` signature
- `FluxWrapper` that wasn't even called a functor
- K-gent's `intercept()` pretending it wasn't a functor
- Five different law verification approaches

The isomorphism crisis: everything was secretly the same pattern, implemented five different ways. The zoo was eventually unified into `UniversalFunctor`, and now:

```python
# All functors derive from the same protocol
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

The ghost teaches: **find the isomorphism, collapse the complexity**.

</details>

---

## Polynomial Architecture

> *"Agent[A, B] ≅ A → B is a lie. Real agents have modes."*

The polynomial functor architecture (AD-002) captures **state-dependent behavior**—agents that accept different inputs based on their internal state.

### The Core Insight

Traditional agents are functions: given input A, produce output B. But real agents have **modes**—internal states that determine what inputs are valid and how to respond.

```
Traditional:  Agent[A, B] ≅ A → B           (stateless function)
Polynomial:   PolyAgent[S, A, B] ≅ S → (A → (S, B))  (state machine)
```

<details>
<summary>🌫️ Ghost: Agent[A,B] was almost enough</summary>

For months, `Agent[A, B]` seemed sufficient. Clean, simple, categorical. We built composition, functors, the whole algebra on it.

Then K-gent broke the model. K-gent in REFLECT mode accepts different inputs than K-gent in CHALLENGE mode. Same agent, different valid operations based on internal state. The fix attempts:

1. **Union types**: `Agent[ReflectInput | ChallengeInput, Output]` — Ugly, loses mode information
2. **Separate agents**: `ReflectAgent`, `ChallengeAgent` — Loses the unity of K-gent
3. **Runtime validation**: Check mode in invoke — Throws away type safety

The real answer was in Spivak's polynomial functors: `PolyAgent[S, A, B]` where S is the state space and `directions(s)` gives valid inputs per state. The mode isn't hidden—it's the first type parameter.

*"The noun is a lie. There is only the rate of change."* — And sometimes the rate of change depends on where you are.

</details>

### PolyAgent Protocol

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """
    Agent as polynomial functor.

    P(y) = Σ_{s ∈ positions} y^{directions(s)}

    Following Spivak's "Polynomial Functors: A Mathematical Theory of Interaction"
    """
    name: str
    positions: FrozenSet[S]                    # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]    # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]]  # State × Input → (NewState, Output)

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """Execute one step of the dynamical system."""
        assert state in self.positions
        assert input in self.directions(state)
        return self.transition(state, input)
```

**Key insight**: `Agent[A, B] ≅ PolyAgent[Unit, A, B]`—traditional agents embed as single-state polynomials.

### Polynomial Agent Genera

| Genus | Polynomial | States | Description |
|-------|------------|--------|-------------|
| A-gent | `ALETHIC_AGENT` | GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING | Dialectical reasoning pipeline |
| K-gent | `SOUL_POLYNOMIAL` | 7 eigenvector contexts | Persona-informed governance |
| D-gent | `MEMORY_POLYNOMIAL` | IDLE, LOADING, STORING, QUERYING, FORGETTING | State persistence |
| E-gent | `EVOLUTION_POLYNOMIAL` | 8-phase thermodynamic cycle | Evolutionary optimization |

### Example: K-gent as Polynomial

```python
SOUL_POLYNOMIAL = PolyAgent(
    name="SoulPolynomial",
    positions=frozenset({
        "aesthetic", "categorical", "gratitude",
        "heterarchy", "generativity", "joy", "ethics"
    }),
    directions=lambda mode: {
        "aesthetic": frozenset({AestheticQuery, TasteChallenge}),
        "categorical": frozenset({StructureQuery, MorphismRequest}),
        "gratitude": frozenset({TitheRequest, AppreciationQuery}),
        # ... per-mode valid inputs
    }[mode],
    transition=soul_transition
)
```

### Composition via Wiring Diagrams

Polynomial agents compose via **wiring diagrams**—graphical representations of how outputs connect to inputs:

```python
from agents.poly import sequential, parallel, WiringDiagram

# Sequential: soul → alethic
composed = sequential(SOUL_POLYNOMIAL, ALETHIC_AGENT)

# Parallel: run soul and memory concurrently
par = parallel(SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL)

# Complex wiring
diagram = WiringDiagram()
diagram.add_box("soul", SOUL_POLYNOMIAL)
diagram.add_box("memory", MEMORY_POLYNOMIAL)
diagram.wire("soul.output", "memory.input")
composed = diagram.compile()
```

---

## The Meta-Construction System

> *"Don't build agents. Build the machine that builds agents."*

The meta-construction system (AD-003) replaces enumeration with generation. Instead of listing 600+ CLI commands, we define the **grammar** that generates them.

### The Three Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     META-CONSTRUCTION SYSTEM                             │
│                                                                          │
│    ┌──────────┐      ┌──────────┐      ┌──────────┐                     │
│    │PRIMITIVES│  +   │ OPERADS  │  +   │ SHEAVES  │  =  EMERGENCE       │
│    │(atoms)   │      │(grammar) │      │(gluing)  │                     │
│    └──────────┘      └──────────┘      └──────────┘                     │
│         │                 │                 │                            │
│         ▼                 ▼                 ▼                            │
│    Base agents      Composition       Local → Global                    │
│    Types            rules             behavior                           │
│    Operations       Wiring            Emergence                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Primitives (13 Atoms)

The irreducible polynomial agents from which all others compose:

| Primitive | Category | Purpose |
|-----------|----------|---------|
| `id` | Bootstrap | Identity morphism |
| `ground` | Bootstrap | Reality anchoring |
| `judge` | Bootstrap | Evaluation |
| `contradict` | Bootstrap | Find tensions |
| `sublate` | Bootstrap | Hegelian synthesis |
| `compose` | Bootstrap | Sequential composition |
| `fix` | Bootstrap | Retry/recursion |
| `manifest` | Perception | Observer-dependent projection |
| `witness` | Perception | Trace recording |
| `lens` | Perception | Focus/selection |
| `sip` | Entropy | Draw from Accursed Share |
| `tithe` | Entropy | Pay for order |
| `define` | Entropy | Autopoiesis |

### Layer 2: Operads (Composition Grammar)

Operads define **what compositions are valid**:

```python
AGENT_OPERAD = Operad(
    name="AgentOperad",
    operations={
        "seq": Operation(arity=2, signature="Agent[A,B] × Agent[B,C] → Agent[A,C]"),
        "par": Operation(arity=2, signature="Agent[A,B] × Agent[A,C] → Agent[A,(B,C)]"),
        "branch": Operation(arity=3, signature="Pred[A] × Agent[A,B] × Agent[A,B] → Agent[A,B]"),
        "fix": Operation(arity=2, signature="Pred[B] × Agent[A,B] → Agent[A,B]"),
        "trace": Operation(arity=1, signature="Agent[A,B] → Agent[A,B] (with observation)"),
    },
    laws=[
        "seq(seq(a, b), c) = seq(a, seq(b, c))",  # Associativity
        "seq(id, a) = a = seq(a, id)",             # Identity
    ]
)
```

**Domain-specific operads** extend the base:

```python
# Example: Soul-specific operations extending the universal operad
SOUL_OPERAD = Operad(
    name="SoulOperad",
    operations=AGENT_OPERAD.operations | {
        "introspect": Operation(arity=0, compose=introspect_compose),
        "shadow": Operation(arity=1, compose=shadow_compose),
        "dialectic": Operation(arity=2, compose=dialectic_compose),
    }
)
```

### Layer 3: Sheaves (Emergence)

Sheaves enable **gluing local behaviors into global behavior**:

```python
SOUL_SHEAF = AgentSheaf(
    contexts={"aesthetic", "categorical", "gratitude", "heterarchy", "generativity", "joy"},
    overlap=eigenvector_overlap
)

# Local agents per context
local_souls = {
    "aesthetic": aesthetic_soul_agent,
    "categorical": categorical_soul_agent,
    "joy": joy_soul_agent,
}

# Glue into emergent global soul
KENT_SOUL = SOUL_SHEAF.glue(local_souls)
```

The global agent has **emergent behavior** that no local agent has alone.

### The Two Paths

Both careful design and chaotic happenstance produce valid compositions:

```python
# Path 1: Careful Design (intentional)
pipeline = SOUL_OPERAD.compose(["ground", "introspect", "shadow", "dialectic"])

# Path 2: Chaotic Happenstance (void.* entropy)
pipeline = await void.compose.sip(
    primitives=PRIMITIVES,
    grammar=SOUL_OPERAD,
    entropy=0.7
)
```

The operad guarantees validity. Entropy introduces variation.

---

## Agent Synergy Patterns

Agents combine in powerful ways. These patterns emerge from the categorical structure.

### Synergy Matrix

```
         K    H    U    P    J    I    M    N    A    B    E    O
    ┌─────────────────────────────────────────────────────────────┐
  K │  ·   ⭐   ○    ○    ○   ⭐   ○   ⭐   ○    ○    ○    ○   │
  H │ ⭐    ·   ○    ○    ○    ○   ○   ⭐   ○    ○    ○    ○   │
  U │  ○    ○    ·   ⭐   ⭐  ⭐   ○    ○   ○    ○    ○   ⭐   │
  P │  ○    ○   ⭐    ·   ⭐   ○   ○    ○   ○    ○    ○    ○   │
  I │ ⭐    ○   ⭐    ○    ○    ·   ○    ○   ○   ⭐  ⭐  ⭐   │
    └─────────────────────────────────────────────────────────────┘

⭐ = High synergy    ○ = Moderate synergy    · = Self
```

### Top Synergy Patterns

| Pattern | Agents | Emergent Capability |
|---------|--------|---------------------|
| **Soul Introspection** | K + H | Soul-aware shadow detection, personality-informed dialectics |
| **Self-Healing Pipeline** | U + P + J | Parse → Classify → Retry/Collapse gracefully |
| **Living Visualization** | I + Flux | Real-time breathing dashboards |
| **Memory as Story** | M + N | Autobiographical system history |
| **Soul-Governed Approval** | K + Judge | Ethical judgment informed by personality |

### Implementation Pattern

```python
# K-gent + H-gent synergy example
kgent = KgentAgent.from_context(ctx)
eigenvectors = await kgent.get_eigenvectors()

# H-jung analyzes through soul lens
jung = JungAgent()
shadow = await jung.analyze_shadow(eigenvectors)
# Result: Soul-aware shadow analysis
```

---

## AGENTESE Runtime

### The Five Contexts

```
world.*    — External (entities, tools)
self.*     — Internal (memory, state)
concept.*  — Abstract (platonics, logic)
void.*     — Accursed Share (entropy)
time.*     — Temporal (traces, forecasts)
```

### Logos (The Invoker)

```python
from protocols.agentese import Logos

logos = Logos()
result = await logos.invoke("self.soul.challenge", umwelt, "idea")
```

### Context Resolvers

Each context has a resolver that maps paths to handlers:

| Resolver | Context | Examples |
|----------|---------|----------|
| `WorldContextResolver` | world.* | world.tool.invoke, world.entity.manifest |
| `SelfContextResolver` | self.* | self.soul.challenge, self.memory.store |
| `ConceptContextResolver` | concept.* | concept.functor.lift, concept.type.define |
| `VoidContextResolver` | void.* | void.entropy.sip, void.gratitude.tithe |
| `TimeContextResolver` | time.* | time.trace.witness, time.forecast.predict |

### Observer-Dependent Affordances

The same path yields different results to different observers (AGENTESE polymorphism):

```python
# Same path, different observers
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
await logos.invoke("world.house.manifest", economist_umwelt)  # → Appraisal
```

---

## Infrastructure Layer

### Cortex (LLM Integration)

```
┌─────────────────────────────────────────┐
│              CORTEX                      │
├─────────────────────────────────────────┤
│ • LLM client management                 │
│ • Cognitive probes (health != HTTP 200) │
│ • Token metering                        │
│ • Cost tracking                         │
└─────────────────────────────────────────┘
```

### Stigmergy (Semantic Field)

```
┌─────────────────────────────────────────┐
│            STIGMERGY                     │
├─────────────────────────────────────────┤
│ • Pheromone store (Redis)               │
│ • Intensity decay over time             │
│ • Agent coordination without coupling   │
└─────────────────────────────────────────┘
```

### K-Terrarium (K8s Integration)

```
┌─────────────────────────────────────────┐
│           K-TERRARIUM                    │
├─────────────────────────────────────────┤
│ • CRD-driven deployment                 │
│ • Mirror Protocol (observe only)        │
│ • Graceful degradation to subprocess    │
│ • Live reload development               │
└─────────────────────────────────────────┘
```

---

## Metabolism (Entropy System)

### Pressure Dynamics

```
             pressure
                ^
                |
    threshold --|-------------- fever trigger
                |      /\
                |     /  \   /\
                |    /    \_/  \
                |   /           \___
                +-----------------------> time
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Pressure** | Accumulates from agent activity |
| **Fever** | Triggers when pressure exceeds threshold |
| **Tithe** | Voluntary pressure discharge (gratitude) |
| **Oblique** | Free creative output during fever |
| **Dream** | LLM-generated creative output (expensive) |

---

## Directory Structure

```
impl/claude/
├── agents/              # Agent implementations by genus
│   ├── a/              # Alethic (functor registry, archetypes, AlethicAgent)
│   ├── c/              # Category (Maybe, Either, Monad)
│   ├── d/              # Data (memory, modal scope, MemoryPolynomialAgent)
│   ├── e/              # Evolution (EvolutionPolynomialAgent)
│   ├── flux/           # Streams (living pipelines)
│   ├── i/              # Interface (TUI, widgets, hints)
│   ├── k/              # K-gent (persona, SoulPolynomialAgent)
│   ├── poly/           # Polynomial agents (PolyAgent, 17 primitives)
│   │   ├── protocol.py     # PolyAgent base class
│   │   ├── primitives.py   # 13 atomic polynomials
│   │   └── wiring.py       # Wiring diagram composition
│   ├── operad/         # Composition grammar
│   │   ├── base.py         # Operad, Operation classes
│   │   ├── agent_operad.py # Universal agent operad
│   │   └── domain/         # SOUL_OPERAD, PARSE_OPERAD, etc.
│   ├── sheaf/          # Emergence
│   │   ├── agent_sheaf.py  # AgentSheaf class
│   │   └── soul_sheaf.py   # SOUL_SHEAF, KENT_SOUL
│   └── ...             # Other genera
├── protocols/
│   ├── agentese/       # AGENTESE runtime
│   │   ├── contexts/       # Five context resolvers
│   │   ├── metabolism/     # Entropy, fever
│   │   └── middleware/     # Curator
│   ├── cli/            # CLI framework
│   └── terrarium/      # K8s integration
├── infra/
│   ├── cortex/         # LLM integration
│   ├── stigmergy/      # Pheromone store
│   └── k8s/            # Operators, CRDs
└── shared/             # Capital, costs, budget
```

---

## Architectural Decisions

| AD | Decision | Rationale |
|----|----------|-----------|
| **AD-001** | Universal Functor Mandate | All transformations are functors with verified laws |
| **AD-002** | Polynomial Generalization | Agent[A,B] embeds in PolyAgent[S,A,B]; mode-dependent behavior |
| **AD-003** | Generative Over Enumerative | Define operads that generate compositions, not lists of instances |
| — | Spec-first | Spec is compression; impl is derivable |
| — | Five contexts only | No kitchen-sink anti-pattern |
| — | Graceful degradation | Always work, even without K8s |
| — | Personality space | LLMs have inherent personality; navigate, don't inject |
| — | Instance isolation | Stateful agents use factory patterns to avoid shared state |

---

## New/Experimental
- `docs/weekly-summary/index.html` — Operators/observers: weekly forest health dashboard + status snapshots.  
- `kgents_ A Next-Generation Agentic Memory Architecture.pdf` — Leadership/partners: narrative framing of memory architecture.  
- `Radical Redesign Proposal for the Kgents UI_UX Ecosystem.pdf` — Design/UX: exploratory layout and interaction treatments.  
- `Visualization & Interactivity_ A Synthesis (Enhanced with Category Theory & UX Patterns).pdf` — Visualization/education: patterns for interactive explainability.

---

## Further Reading

- `spec/principles.md` — Design principles and architectural decisions
- `docs/functor-field-guide.md` — Deep dive into the functor system
- `docs/categorical-foundations.md` — Category theory background
- `plans/skills/polynomial-agent.md` — How to create polynomial agents
- `plans/skills/building-agent.md` — General agent construction guide

---

*"The architecture is the message."*
