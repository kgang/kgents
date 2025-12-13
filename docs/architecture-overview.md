# Architecture Overview

> *"Agents are morphisms. Functors lift them. Projectors compile them."*

This document provides a high-level overview of the kgents architecture.

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

| Genus | Letter | Role |
|-------|--------|------|
| Alethic | A | Architecture, functors |
| Category | C | Composition primitives |
| Data | D | State, memory |
| Flux | Flux | Streams, events |
| Interface | I | TUI, semantic fields |
| Kent | K | Persona, governance |
| Lattice | L | Semantic registry |
| Testing | T | Types I-V |
| Utility | U | Tools, MCP |

---

## The Functor System

### Universal Functor Protocol

Every transformation in kgents is a functor:

```python
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

### Built-in Functors

| Functor | Effect |
|---------|--------|
| `Maybe` | Handle optional values |
| `Either` | Handle success/error |
| `List` | Process collections |
| `Fix` | Add retries |
| `Logged` | Add observability |
| `Soul` | Add K-gent governance |
| `Flux` | Enable streaming |
| `Observer` | Add telemetry |
| `State` | Add memory |

### Composition

Functors compose:

```python
stack = compose_functors(LoggedFunctor, FixFunctor, SoulFunctor)
resilient_agent = stack(my_agent)
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
- `WorldContextResolver` — External entities
- `SelfContextResolver` — Internal state (soul, memory, semaphore)
- `ConceptContextResolver` — Platonic definitions
- `VoidContextResolver` — Entropy, gratitude, pataphysics
- `TimeContextResolver` — Traces, forecasts

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
| **Tithe** | Voluntary pressure discharge |
| **Oblique** | Free creative output during fever |
| **Dream** | LLM-generated creative output (expensive) |

---

## Directory Structure

```
impl/claude/
├── agents/           # Agent implementations by genus
│   ├── a/           # Alethic (functor registry, archetypes)
│   ├── c/           # Category (Maybe, Either, Monad)
│   ├── d/           # Data (memory, modal scope, crystals)
│   ├── flux/        # Streams (living pipelines)
│   ├── i/           # Interface (TUI, widgets, hints)
│   ├── k/           # K-gent (persona, hypnagogia, garden)
│   └── ...          # Other genera
├── protocols/
│   ├── agentese/    # AGENTESE runtime
│   │   ├── contexts/    # Five context resolvers
│   │   ├── metabolism/  # Entropy, fever
│   │   └── middleware/  # Curator
│   ├── cli/         # CLI framework
│   └── terrarium/   # K8s integration
├── infra/
│   ├── cortex/      # LLM integration
│   ├── stigmergy/   # Pheromone store
│   └── k8s/         # Operators, CRDs
└── shared/          # Capital, costs, budget
```

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Universal Functor** | All transformations are functors (AD-001) |
| **Spec-first** | Spec is compression; impl is derivable |
| **Five contexts only** | No kitchen-sink anti-pattern |
| **Graceful degradation** | Always work, even without K8s |
| **Personality space** | LLMs have inherent personality; navigate, don't inject |

---

*"The architecture is the message."*
