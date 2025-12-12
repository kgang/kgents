# kgents Architecture Overview

> *"The noun is a lie. There is only the rate of change."*

This document provides a comprehensive architectural overview of kgents for study and reference.

---

## Table of Contents

1. [Philosophy & Principles](#philosophy--principles)
2. [Structural Overview](#structural-overview)
3. [The Bootstrap Kernel](#the-bootstrap-kernel)
4. [Agent Taxonomy](#agent-taxonomy)
5. [AGENTESE Protocol](#agentese-protocol)
6. [Core Type System](#core-type-system)
7. [Runtime Architecture](#runtime-architecture)
8. [K-gent Soul Architecture](#k-gent-soul-architecture)
9. [Flux Functor](#flux-functor)
10. [Integration Map](#integration-map)
11. [Key Abstractions](#key-abstractions)

---

## Philosophy & Principles

### The Seven Non-Negotiable Principles

Every design decision flows from these principles:

| Principle | Description | Implication |
|-----------|-------------|-------------|
| **Tasteful** | Clear justified purpose | Avoid feature creep |
| **Curated** | Quality over quantity | Say "no" more than "yes" |
| **Ethical** | Augment human capability | Preserve human agency |
| **Joy-Inducing** | Personality encouraged | Warmth over coldness |
| **Composable** | Agents are morphisms | Category laws verified |
| **Heterarchical** | No fixed hierarchy | Agents exist in flux |
| **Generative** | Regenerable from spec | Compressed design wisdom |

### The Python/CPython Model

```
spec/   = Language Specification (conceptual, implementation-agnostic)
impl/   = Reference Implementation (Claude Code + Open Router)
```

The spec defines WHAT, the impl defines HOW.

---

## Structural Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         kgents Architecture                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      AGENTESE LAYER                          │    │
│  │   world.* | self.* | concept.* | void.* | time.*            │    │
│  │              ↓ Logos Resolver (Functor)                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              ↓                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    AGENT TAXONOMY                            │    │
│  │  A  B  C  D  E  F  G  H  I  J  K  L  M  N  O  P  T  U  W  Y │    │
│  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │  │ │    │
│  │  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓ │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         │                                            │
│  ┌──────────────────────┴──────────────────────────────────────┐    │
│  │                   BOOTSTRAP KERNEL                           │    │
│  │    Id    Compose    Judge    Ground    Contradict            │    │
│  │                     Sublate           Fix                    │    │
│  │                                                              │    │
│  │         Agent[A, B]  →  ComposedAgent[A, B, C]              │    │
│  └──────────────────────┬──────────────────────────────────────┘    │
│                         │                                            │
│  ┌──────────────────────┴──────────────────────────────────────┐    │
│  │                    RUNTIME LAYER                             │    │
│  │     ClaudeCLIRuntime  |  ClaudeRuntime  |  OpenRouterRuntime│    │
│  │                                                              │    │
│  │          LLMAgent.build_prompt() → AgentContext             │    │
│  │          LLMAgent.parse_response() ← String                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Bootstrap Kernel

The 7 bootstrap agents are **axioms**—irreducible primitives from which all of kgents can be regenerated:

```
┌────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP AGENTS                             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐     ┌─────────────┐     ┌─────────┐             │
│   │   Id    │────▶│   Compose   │────▶│ Result  │             │
│   │  A → A  │     │ (f,g) → f>>g│     │Agent[A,C│             │
│   └─────────┘     └─────────────┘     └─────────┘             │
│        │                                    │                   │
│        │         Category Laws              │                   │
│        │    ────────────────────            │                   │
│        │    Id >> f ≡ f ≡ f >> Id           │                   │
│        │    (f >> g) >> h ≡ f >> (g >> h)   │                   │
│        │                                    │                   │
│   ┌─────────┐     ┌─────────────┐     ┌─────────┐             │
│   │  Judge  │     │   Ground    │     │   Fix   │             │
│   │7 Princip│     │ Void→Facts  │     │iterate()│             │
│   └─────────┘     └─────────────┘     └─────────┘             │
│        │                │                   │                   │
│        │                │                   │                   │
│   ┌─────────┐     ┌─────────────┐                              │
│   │Contradict│    │   Sublate   │                              │
│   │ Tension │────▶│  Synthesis  │                              │
│   └─────────┘     └─────────────┘                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Bootstrap Agent Details

| Agent | Signature | Purpose |
|-------|-----------|---------|
| **Id** | `A → A` | Identity morphism, unit of composition |
| **Compose** | `(Agent, Agent) → Agent` | The agent-that-makes-agents |
| **Judge** | `Agent → Verdict` | Embodies 7 principles as executable judgment |
| **Ground** | `Void → Facts` | Empirical seed (persona, world, history) |
| **Contradict** | `(A, B) → Tension?` | Detects logical/pragmatic/axiological tensions |
| **Sublate** | `Tension → Synthesis` | Hegelian synthesis preserving both sides |
| **Fix** | `(f, x₀) → x*` | Fixed-point iteration until convergence |

---

## Agent Taxonomy

The alphabetical taxonomy (A-Ω) organizes agents by concern:

```
┌──────────────────────────────────────────────────────────────────────┐
│                        AGENT GENERA (A-Ω)                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ABSTRACT/META                    COGNITIVE                          │
│  ┌─────┐ ┌─────┐ ┌─────┐        ┌─────┐ ┌─────┐ ┌─────┐            │
│  │  A  │ │  C  │ │  O  │        │  G  │ │  H  │ │  M  │            │
│  │Archi│ │Categ│ │Obser│        │Gramm│ │Hegel│ │Memor│            │
│  │tect │ │ory  │ │vabi│        │ar   │ │ian  │ │y    │            │
│  └─────┘ └─────┘ └─────┘        └─────┘ └─────┘ └─────┘            │
│                                                                       │
│  DATA/STATE                       GENERATION                         │
│  ┌─────┐ ┌─────┐ ┌─────┐        ┌─────┐ ┌─────┐ ┌─────┐            │
│  │  D  │ │  L  │ │  N  │        │  E  │ │  F  │ │  J  │            │
│  │Data │ │Libra│ │Narra│        │Evolu│ │Forge│ │JIT  │            │
│  │     │ │ry   │ │tor  │        │tion │ │     │ │     │            │
│  └─────┘ └─────┘ └─────┘        └─────┘ └─────┘ └─────┘            │
│                                                                       │
│  INTERFACE                        UTILITY                            │
│  ┌─────┐ ┌─────┐ ┌─────┐        ┌─────┐ ┌─────┐ ┌─────┐            │
│  │  I  │ │  W  │ │  Ω  │        │  P  │ │  T  │ │  U  │            │
│  │Inter│ │Wire │ │Somat│        │Parse│ │Test │ │Utili│            │
│  │face │ │     │ │ic   │        │r    │ │     │ │ty   │            │
│  └─────┘ └─────┘ └─────┘        └─────┘ └─────┘ └─────┘            │
│                                                                       │
│  SPECIAL                                                             │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                    │
│  │  K  │ │  B  │ │  Ψ  │ │  Y  │                                    │
│  │Soul │ │Bio/ │ │Psych│ │Y-Com│                                    │
│  │     │ │Bank │ │opomp│ │bine │                                    │
│  └─────┘ └─────┘ └─────┘ └─────┘                                    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Agent Genus Reference

| Letter | Name | Theme | Key Responsibility |
|--------|------|-------|-------------------|
| **A** | Agents | Abstract architectures | BootstrapWitness, Creativity Coach |
| **B** | Bgents | Bio/Scientific + Banking | Resource allocation, economics |
| **C** | Cgents | Category Theory | Composition laws, functors, monads |
| **D** | Dgents | Data Agents | SQL, Redis, Lens, Graph, Cached |
| **E** | Egents | Evolution | Teleological thermodynamics |
| **F** | Fgents | Forge | Artifact synthesis, contracts |
| **G** | Ggents | Grammar | Parsing, natural language |
| **H** | Hgents | Hegelian | Dialectics, sublation |
| **I** | Igents | Interface | Terrarium TUI, semantic field |
| **J** | Jgents | JIT | Lazy evaluation, instantiation |
| **K** | Kgent | Kent Simulacra | Persona, soul, governance |
| **L** | Lgents | Library | Semantic registry, lattice |
| **M** | Mgents | Memory | Holographic associative memory |
| **N** | Ngents | Narrator | Temporal traces, witness |
| **O** | Ogents | Observability | Telemetry, bootstrap witness |
| **P** | Pgents | Parser | Multi-strategy parsing |
| **T** | Tgents | Testing | Types I-V, algebraic reliability |
| **U** | Ugents | Utility | Tool use, MCP integration |
| **W** | Wgents | Wire | Ephemeral observation, stigmergy |
| **Y** | Ygents | Y-Combinator | Cognitive + somatic topology |
| **Ψ** | Psigents | Psychopomp | Holonic projection, metaethics |
| **Ω** | Omegagents | Somatic | Morphemes, proprioception |

---

## AGENTESE Protocol

AGENTESE is the **verb-first ontology** for agent-world interaction.

### The Five Strict Contexts

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENTESE CONTEXTS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   world.*    ────────▶  The External                        │
│   │                     (entities, environments, tools)      │
│   │                                                          │
│   self.*     ────────▶  The Internal                        │
│   │                     (memory, capability, state)          │
│   │                                                          │
│   concept.*  ────────▶  The Abstract                        │
│   │                     (platonics, definitions, logic)      │
│   │                                                          │
│   void.*     ────────▶  The Accursed Share                  │
│   │                     (entropy, serendipity, gratitude)    │
│   │                                                          │
│   time.*     ────────▶  The Temporal                        │
│                         (traces, forecasts, schedules)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Path Syntax

```
<Context> . <Holon> . <Aspect>

Examples:
  world.house.manifest          # Perceive house
  world.house.witness           # Show house history
  self.memory.consolidate       # Trigger hypnagogia
  concept.justice.refine        # Dialectical challenge
  void.entropy.sip              # Draw randomness
  time.trace.witness            # Show the past
```

### Standard Aspects

| Aspect | Category | Description |
|--------|----------|-------------|
| `manifest` | Perception | Collapse to observer's view |
| `witness` | Perception | Show history (N-gent) |
| `refine` | Generation | Dialectical challenge |
| `sip` | Entropy | Draw from Accursed Share |
| `tithe` | Entropy | Pay for order (gratitude) |
| `affordances` | Query | What verbs are available? |
| `define` | Generation | Create this concept (JIT) |
| `lens` | Composition | Get composable agent |

### Observer-Centric Perception (Umwelt)

```python
# Different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
await logos.invoke("world.house.manifest", economist_umwelt)  # → Appraisal
```

---

## Core Type System

### Agent Protocol

```python
class Agent(ABC, Generic[A, B]):
    """An agent is a morphism A → B in the category of agents."""

    @property
    def name(self) -> str: ...

    async def invoke(self, input: A) -> B: ...

    def __rshift__(self, other: Agent[B, C]) -> ComposedAgent[A, B, C]:
        """Composition: f >> g"""
        return ComposedAgent(self, other)
```

### Result Type (Railway Oriented Programming)

```python
Result = Union[Ok[T], Err[E]]

@dataclass
class Ok(Generic[T]):
    value: T
    def map(self, f): return Ok(f(self.value))

@dataclass
class Err(Generic[E]):
    error: E
    def map(self, f): return self  # Propagate error
```

### Domain Types

```python
@dataclass
class Tension:
    thesis: Any
    antithesis: Any
    mode: TensionMode  # logical, pragmatic, axiological, temporal, aesthetic
    severity: float    # 0.0 to 1.0

@dataclass
class Synthesis:
    resolution_type: str  # preserve, negate, elevate
    result: Any
    preserved_from_thesis: tuple[str, ...]
    preserved_from_antithesis: tuple[str, ...]

@dataclass
class Verdict:
    type: VerdictType  # accept, revise, reject
    partial_verdicts: tuple[PartialVerdict, ...]
    reasoning: str
```

---

## Runtime Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RUNTIME LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐                                           │
│   │    LLMAgent     │                                           │
│   │   extends Agent │                                           │
│   ├─────────────────┤                                           │
│   │ build_prompt()  │───▶ AgentContext                         │
│   │ parse_response()│◀─── String                               │
│   └────────┬────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐       │
│   │                   Runtime                            │       │
│   │                   (abstract)                         │       │
│   ├─────────────────────────────────────────────────────┤       │
│   │  execute(agent, input) → AgentResult                │       │
│   │  raw_completion(context) → (text, metadata)         │       │
│   └────────┬────────────────┬────────────────┬──────────┘       │
│            │                │                │                   │
│   ┌────────▼────────┐ ┌─────▼──────┐ ┌──────▼──────┐           │
│   │ClaudeCLIRuntime │ │ClaudeRuntime│ │OpenRouter   │           │
│   │  (OAuth via CLI)│ │ (API Key)   │ │Runtime      │           │
│   │  `claude -p`    │ │             │ │             │           │
│   └─────────────────┘ └─────────────┘ └─────────────┘           │
│                                                                  │
│   IMPORTANT: For kgents development, use ClaudeCLIRuntime       │
│   which piggybacks on Claude Code CLI's OAuth authentication.   │
│   ClaudeRuntime requires direct API keys.                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## K-gent Soul Architecture

K-gent is the **Governance Functor**—the system's fix point that personalizes all agents.

```
┌─────────────────────────────────────────────────────────────────┐
│                    K-GENT SOUL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      KgentSoul                           │   │
│   │              "Middleware of Consciousness"               │   │
│   ├─────────────────────────────────────────────────────────┤   │
│   │                                                          │   │
│   │  THREE MODES:                                            │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │   │
│   │  │  INTERCEPTS  │ │   INHABITS   │ │    DREAMS    │    │   │
│   │  │  Semaphores  │ │  Terrarium   │ │  Hypnagogia  │    │   │
│   │  │  Purgatory   │ │  Presence    │ │  Refinement  │    │   │
│   │  └──────────────┘ └──────────────┘ └──────────────┘    │   │
│   │                                                          │   │
│   │  DIALOGUE MODES:                                         │   │
│   │  ┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐        │   │
│   │  │REFLECT │ │ADVISE  │ │CHALLENGE │ │ EXPLORE │        │   │
│   │  │(0.4)   │ │(0.5)   │ │(0.6)     │ │ (0.8)   │        │   │
│   │  │Mirror  │ │Suggest │ │Push back │ │Tangents │        │   │
│   │  └────────┘ └────────┘ └──────────┘ └─────────┘        │   │
│   │       ↑ Temperature per mode                             │   │
│   │                                                          │   │
│   │  BUDGET TIERS:                                           │   │
│   │  DORMANT → WHISPER → DIALOGUE → DEEP                    │   │
│   │  (0 tok)   (100)     (4000)     (8000+)                 │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│        ┌─────────────────────┼─────────────────────┐            │
│        │                     │                     │            │
│        ▼                     ▼                     ▼            │
│   ┌─────────┐         ┌──────────┐         ┌──────────┐        │
│   │KgentAgent│        │Eigenvectors│       │AuditTrail │        │
│   │ Dialogue │        │ Personality│       │ Mediation │        │
│   │  Engine  │        │ Coordinates│       │   Log     │        │
│   └─────────┘         └──────────┘         └──────────┘        │
│        │                     │                                   │
│        ▼                     ▼                                   │
│   ┌─────────┐         ┌──────────┐                              │
│   │LLMClient│         │PersonaState│                             │
│   │ClaudeCLI│         │Preferences │                             │
│   │ Runtime │         │ Patterns   │                             │
│   └─────────┘         └──────────┘                              │
│                                                                  │
│   DEEP INTERCEPT (Semantic Gatekeeper):                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 1. Check DANGEROUS_KEYWORDS → Always escalate           │   │
│   │ 2. LLM reasoning against principles                     │   │
│   │ 3. Low confidence (<0.7) → Escalate                     │   │
│   │ 4. Log to AuditTrail                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Eigenvector Coordinates

```
┌────────────────────────────────────────────────┐
│              KENT EIGENVECTORS                  │
├────────────────────────────────────────────────┤
│                                                 │
│  Aesthetic:    Minimalist ◀──●────── Baroque   │
│                          (0.15)                 │
│                                                 │
│  Categorical:  Concrete ────────●──▶ Abstract  │
│                               (0.85)            │
│                                                 │
│  Heterarchy:   Hierarchical ────●──▶ Peer      │
│                               (0.85)            │
│                                                 │
│  Joy:          Serious ─────────●──▶ Playful   │
│                               (0.75)            │
│                                                 │
│  Tempo:        Deliberate ──●─────── Rapid     │
│                          (0.40)                 │
│                                                 │
│  Risk:         Conservative ───●───── Bold     │
│                             (0.60)              │
│                                                 │
└────────────────────────────────────────────────┘
```

---

## Flux Functor

Transform agents from discrete state to continuous flow.

```
┌─────────────────────────────────────────────────────────────────┐
│                       FLUX FUNCTOR                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Discrete:  Agent[A, B]                                        │
│                 │                                                │
│                 │  Flux : Agent → FluxAgent                     │
│                 ▼                                                │
│   Continuous: FluxAgent[Flux[A], Flux[B]]                       │
│                                                                  │
│   where Flux[T] = AsyncIterator[T]                              │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Static:   Agent: A → B          (point transformation)        │
│   Dynamic:  Flux(Agent): dA/dt → dB/dt  (continuous flow)       │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   METABOLISM METRICS:                                           │
│   ┌─────────┐  ┌─────────┐  ┌─────────────┐                    │
│   │Pressure │  │  Flow   │  │ Temperature │                    │
│   │(backlog)│  │(rate)   │  │  (stress)   │                    │
│   └─────────┘  └─────────┘  └─────────────┘                    │
│                                                                  │
│   PIPELINE COMPOSITION:                                         │
│   source | transform | filter | sink                            │
│                                                                  │
│   PERTURBATION:                                                 │
│   External signal injection during flow                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    CROSS-AGENT INTEGRATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                        ┌───────┐                                │
│                        │   K   │◀──── Personalizes ALL          │
│                        │ Soul  │                                 │
│                        └───┬───┘                                │
│                            │                                     │
│   ┌────────────────────────┼────────────────────────┐           │
│   │                        │                        │           │
│   ▼                        ▼                        ▼           │
│ ┌───┐                   ┌───┐                    ┌───┐          │
│ │ D │◀────────────────▶│ M │◀─────────────────▶│ L │          │
│ │Data│   Persistence    │Mem│   Holographic     │Lib│          │
│ └─┬─┘                   └─┬─┘                   └─┬─┘          │
│   │                       │                       │             │
│   │     ┌─────────────────┴─────────────────┐    │             │
│   │     │                                   │    │             │
│   ▼     ▼                                   ▼    ▼             │
│ ┌───┐ ┌───┐                              ┌───┐ ┌───┐          │
│ │ U │─│ P │  Tools + Parsing             │ T │─│ O │          │
│ │Util│ │Pars│                            │Test│ │Obs│          │
│ └───┘ └───┘                              └───┘ └───┘          │
│   │                                         │     │             │
│   └────────────────────┬────────────────────┘     │             │
│                        │                          │             │
│                        ▼                          │             │
│                     ┌───┐                         │             │
│                     │ W │◀────────────────────────┘             │
│                     │Wire│   Traces ALL                         │
│                     └─┬─┘                                       │
│                       │                                          │
│                       ▼                                          │
│                    ┌───┐                                        │
│                    │ I │  Terrarium Visualization               │
│                    │Int│                                        │
│                    └───┘                                        │
│                                                                  │
│   OTHER KEY INTEGRATIONS:                                       │
│   D + E : E-gents use D-gent memory for evolution state        │
│   J + F : F-gent artifacts JIT-instantiated via J-gent         │
│   H + Ψ : Ψ-gent uses H-gent dialectics                        │
│   B + B : B-Banker controls B-Bio resource allocation          │
│   Ω + Y : Y-gent topology uses Ω-gent for bodies               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Abstractions

### Handle (AGENTESE)

```python
# Traditional: world.house returns a JSON object
# AGENTESE: world.house returns a HANDLE

# A handle is a morphism: Observer → Interaction
handle = await logos.resolve("world.house")
result = await handle.manifest(observer_umwelt)
```

### Affordance

```python
# What can this observer DO with this entity?
affordances = await logos.affordances("world.house", observer_umwelt)
# → ["enter", "observe", "value", "photograph"]
```

### Umwelt (Observer World)

```python
@dataclass
class Umwelt:
    observer_type: str        # architect, poet, economist
    perception_modes: list    # visual, semantic, economic
    value_priorities: list    # efficiency, beauty, profit
    interpretation_rules: dict
```

### Symbiont Pattern

```python
# Pure logic (stateless) + D-gent memory (state)
# = Living agent

class PureLogic:
    async def invoke(self, input: A) -> B:
        return transform(input)

# Compose with memory
stateful_agent = DgentMemory(PureLogic())
```

### LogosNode Protocol

```python
@runtime_checkable
class LogosNode(Protocol):
    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        ...

    def affordances(self, observer: AgentMeta) -> list[str]:
        """What can this observer do here?"""
        ...
```

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Specification files | 153 |
| Test files | 542 |
| Test lines | 295,035 |
| Passing tests | 9,046+ |
| Agent genera | 14+ (A-Ω) |
| Bootstrap agents | 7 |
| AGENTESE contexts | 5 |

---

## Key Files for Study

### Specifications
- `spec/bootstrap.md` - The irreducible kernel
- `spec/anatomy.md` - What is an agent
- `spec/principles.md` - The 7 principles
- `spec/protocols/agentese.md` - Verb-first ontology
- `spec/c-gents/composition.md` - Category laws

### Implementations
- `impl/claude/bootstrap/types.py` - Core type system
- `impl/claude/agents/k/soul.py` - K-gent soul
- `impl/claude/protocols/agentese/logos.py` - AGENTESE resolver
- `impl/claude/agents/flux/agent.py` - Flux functor
- `impl/claude/runtime/cli.py` - ClaudeCLIRuntime

---

*"This is not a collection of isolated agents but a cohesive ecosystem where every piece serves the whole."*
