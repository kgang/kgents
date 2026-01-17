# 04: Architecture Self-Description K-Blocks

> *"The system knows itself. Architecture is not documented—it is derived."*

**Status**: Design Specification
**Date**: 2026-01-10
**Prerequisites**: `spec/protocols/k-block.md`, `spec/principles/CONSTITUTION.md`, `docs/skills/hypergraph-editor.md`
**Enables**: Constitutional navigation, self-describing genesis, architecture-as-first-class-content

---

## Part I: Purpose

### Why Architecture K-Blocks?

Traditional documentation describes architecture from outside. Architecture K-Blocks make the architecture **self-describing**:

| Without Architecture K-Blocks | With Architecture K-Blocks |
|-------------------------------|----------------------------|
| README.md explains the stack | Stack explains itself through derived K-Blocks |
| Diagrams rot as code evolves | Derivations maintain coherence via Galois loss |
| New developers read docs | New developers navigate the constitutional graph |
| Architecture is opinion | Architecture derives from principles with measured loss |

### The Core Insight

**Architecture K-Blocks = Derived Understanding + Galois Loss + Constitutional Navigation**

Each K-Block captures a facet of the kgents architecture, derived from core principles with explicit loss values. The K-Blocks form a navigable graph where files are not _in folders_ but _derived from principles_.

---

## Part II: The Five Architecture K-Blocks

### Overview

| K-Block | Title | Level | Derives From | Galois Loss |
|---------|-------|-------|--------------|-------------|
| **Metaphysical Fullstack** | Every Agent Is a Vertical Slice | L3 | AD-009, L2.5 (Composable), L2.7 (Generative) | 0.12 |
| **Hypergraph Editor** | Constitutional Navigation | L3 | L2.18 (Sheaf), L2.15 (Witness), L0.2 (Morphism) | 0.18 |
| **Crown Jewels** | Domain-Specific Agent Compositions | L3 | L2.16 (Operad), L2.17 (PolyAgent), L2.5 (Composable) | 0.15 |
| **AGENTESE** | The Protocol IS the API | L3 | L0.2 (Morphism), L1.2 (Judge), L2.5 (Composable) | 0.10 |
| **Constitutional Graph** | Files as Derivations | L3 | L1.3 (Ground), L1.8 (Galois), L2.18 (Sheaf) | 0.20 |

---

## K-Block 1: Metaphysical Fullstack

### Metadata

```yaml
title: "The Metaphysical Fullstack: Every Agent Is a Vertical Slice"
level: L3
type: architecture
derives_from:
  - id: "AD-009"
    loss: 0.08
  - id: "L2.5_COMPOSABLE"
    loss: 0.12
  - id: "L2.7_GENERATIVE"
    loss: 0.15
aggregate_loss: 0.12
state: grounded
witnesses:
  - "2025-12-20: Fullstack pattern validated in Brain, Witness, Atelier"
  - "2026-01-10: Added to genesis architecture K-Blocks"
```

### Content

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

The Metaphysical Fullstack is the central architectural insight of kgents. It defines eight layers that every agent traverses, from persistence to projection:

```
LAYER  NAME                    PURPOSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  7    PROJECTION SURFACES     CLI | TUI | Web | marimo | JSON | SSE | VR
       ────────────────────────────────────────────────────────────────────
       Multiple surfaces, same underlying truth. Observer determines view.
       The projection is a functor: P[Surface] : AgentState -> Rendering

  6    AGENTESE PROTOCOL       logos.invoke(path, observer, **kwargs)
       ────────────────────────────────────────────────────────────────────
       The protocol IS the API. No explicit routes. All transports collapse
       to the same semantic path. HTTP, WebSocket, CLI, gRPC—same invoke.

  5    AGENTESE NODE           @node decorator, aspects, effects, affordances
       ────────────────────────────────────────────────────────────────────
       Semantic interface layer. Every capability is registered with its
       effects, budget estimates, and observer-dependent affordances.

  4    SERVICE MODULE          services/<name>/ — Crown Jewel business logic
       ────────────────────────────────────────────────────────────────────
       The Crown Jewels: Brain, Town, Witness, Atelier, etc.
       Domain logic + adapters + frontend components live together.
       Services are CONSUMERS of categorical infrastructure.

  3    OPERAD GRAMMAR          Composition laws, valid operations
       ────────────────────────────────────────────────────────────────────
       The grammar of what can compose with what. Laws are VERIFIED,
       not hoped for. AGENT_OPERAD, SOUL_OPERAD, WITNESS_OPERAD.

  2    POLYNOMIAL AGENT        PolyAgent[S, A, B]: state x input -> output
       ────────────────────────────────────────────────────────────────────
       State-dependent behavior. Mode determines valid inputs.
       Every agent is a polynomial functor over positions and directions.

  1    SHEAF COHERENCE         Local views -> global consistency
       ────────────────────────────────────────────────────────────────────
       Compatible local sections glue to form global truth.
       The gluing axiom: if locals agree on overlaps, global exists.

  0    PERSISTENCE LAYER       StorageProvider: membrane.db, vectors, blobs
       ────────────────────────────────────────────────────────────────────
       XDG-compliant paths, graceful degradation, migrations.
       All state flows through D-gent. Append-only by default.
```

### Key Rules (Derived from AD-009)

1. **`services/` = Crown Jewels**: Brain, Town, Witness, Atelier — domain logic, adapters, frontend
2. **`agents/` = Infrastructure**: PolyAgent, Operad, Sheaf, Flux — categorical primitives
3. **No explicit backend routes**: AGENTESE universal protocol IS the API
4. **Persistence through D-gent**: All state via `StorageProvider`
5. **Frontend lives with service**: `services/brain/web/` not `web/brain/`

### The Fullstack Flow

```
User Action (any surface)
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  7. PROJECTION    "kg brain capture 'insight'"                │
│                   or POST /agentese/self.memory.capture       │
│                   or ws.send({path: "self.memory.capture"})   │
└───────────────────────────────────────────────────────────────┘
        │ All transports collapse to:
        ▼
┌───────────────────────────────────────────────────────────────┐
│  6. AGENTESE      logos.invoke("self.memory.capture",         │
│                              observer, content="insight")     │
└───────────────────────────────────────────────────────────────┘
        │ Resolved via gateway registry
        ▼
┌───────────────────────────────────────────────────────────────┐
│  5. NODE          @node("self.memory") class MemoryNode       │
│                   @aspect(category=MUTATION, effects=[...])   │
└───────────────────────────────────────────────────────────────┘
        │ Dispatches to service
        ▼
┌───────────────────────────────────────────────────────────────┐
│  4. SERVICE       services/brain/persistence.py               │
│                   await self.persistence.capture(content)     │
└───────────────────────────────────────────────────────────────┘
        │ Validates via operad
        ▼
┌───────────────────────────────────────────────────────────────┐
│  3. OPERAD        BRAIN_OPERAD.verify_operation("capture")    │
│                   assert laws_satisfied                       │
└───────────────────────────────────────────────────────────────┘
        │ Transitions state
        ▼
┌───────────────────────────────────────────────────────────────┐
│  2. POLYNOMIAL    brain_poly.transition(IDLE, "capture")      │
│                   -> (CAPTURING, result)                      │
└───────────────────────────────────────────────────────────────┘
        │ Glues local to global
        ▼
┌───────────────────────────────────────────────────────────────┐
│  1. SHEAF         brain_sheaf.glue([session, crystal, index]) │
│                   -> coherent BrainState                      │
└───────────────────────────────────────────────────────────────┘
        │ Persists
        ▼
┌───────────────────────────────────────────────────────────────┐
│  0. PERSISTENCE   storage.relational.execute(INSERT...)       │
│                   storage.semantic.index(embedding)           │
└───────────────────────────────────────────────────────────────┘
```

### Derivation from Principles

| Principle | How Fullstack Embodies It |
|-----------|--------------------------|
| **L2.5 Composable** | Each layer composes with adjacent layers; the whole is a composition |
| **L2.7 Generative** | Spec at L4 generates implementation at L0-L3 |
| **AD-009** | The fullstack agent pattern itself, canonically derived |
| **L1.8 Galois** | Loss = 0.12: vertical slice occasionally requires layer-specific exceptions |

---

## K-Block 2: Hypergraph Editor

### Metadata

```yaml
title: "The Hypergraph Editor: Constitutional Navigation"
level: L3
type: architecture
derives_from:
  - id: "L2.18_SHEAF"
    loss: 0.15
  - id: "L2.15_WITNESS"
    loss: 0.18
  - id: "L0.2_MORPHISM"
    loss: 0.20
aggregate_loss: 0.18
state: grounded
witnesses:
  - "2025-12-22: Hypergraph editor spec canonicalized"
  - "2026-01-10: Constitutional navigation K-Block formalized"
```

### Content

> *"The file is a lie. There is only the graph."*

The Hypergraph Editor is the paradigm shift from traditional file editing to constitutional navigation. Files are not _in folders_—they _derive from principles_.

### The Paradigm Shift

| Traditional Editor | Hypergraph Editor |
|-------------------|-------------------|
| Open a file | Focus a node |
| Go to line 42 | Traverse an edge |
| Save | Commit to cosmos (with witness) |
| Browse directories | Navigate siblings (gj/gk) |
| Use find-in-files | Use graph search (g/) |
| Organize by folder | Organize by derivation |

### K-Blocks as Nodes, Derivations as Edges

```
                    CONSTITUTION.md (L0)
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    L2.5_COMPOSABLE  L2.7_GENERATIVE  L2.18_SHEAF
         │                │                │
         ├────────────────┼────────────────┤
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐     ┌─────────┐     ┌─────────┐
    │ Agent   │────▶│ Fullstack│◀────│ K-Block │
    │ Town    │     │ K-Block │     │ Spec    │
    └─────────┘     └─────────┘     └─────────┘
         │                │                │
         ▼                ▼                ▼
    impl/claude/    impl/claude/    impl/claude/
    agents/town/    services/       services/
                    brain/          k_block/
```

Each edge carries:
- **Type**: `derives_from`, `implements`, `tests`, `extends`, `contradicts`
- **Loss**: Galois loss for the derivation (how much is lost in translation)
- **Witness**: When the derivation was established and by whom

### The Six Editing Modes

```
NORMAL ─┬─ 'i' ──→ INSERT  (edit content, K-Block isolation active)
        ├─ 'ge' ─→ EDGE    (connect nodes via derivation)
        ├─ 'v'  ─→ VISUAL  (select multiple nodes)
        ├─ ':' ──→ COMMAND (AGENTESE invocation)
        └─ 'gw' ─→ WITNESS (mark moments)

All modes → Esc → NORMAL
```

| Mode | Purpose | Key Operations |
|------|---------|----------------|
| **NORMAL** | Navigate the graph | gh (parent), gl (child), gj/gk (siblings), gd (definition) |
| **INSERT** | Edit node content | Automatically creates K-Block isolation; changes are local |
| **EDGE** | Create/modify derivations | ai (add implements), ad (add derives_from), d (delete edge) |
| **VISUAL** | Select multiple nodes | v (toggle), V (line), gv (block) |
| **COMMAND** | Invoke AGENTESE | `:ag self.brain.capture`, `:concept.specgraph.audit` |
| **WITNESS** | Mark decisions | mE (eureka), mG (gotcha), mT (taste), mV (veto) |

### Graph Navigation Patterns

```typescript
// Navigation primitives
gh    Parent (inverse derives_from edge)
gl    Child (forward derives_from edge)
gj    Next sibling (same parent)
gk    Prev sibling
gd    Go to definition (implements edge)
gr    Go to references (inverse implements)
gt    Go to tests
gp    Go to parent spec (derives_from)
gf    Follow edge under cursor
```

### The Derivation Trail Bar

Traditional breadcrumbs show folder path. The Derivation Trail Bar shows semantic path:

```
┌─────────────────────────────────────────────────────────────────┐
│ TRAIL: CONSTITUTION → L2.5_COMPOSABLE → Fullstack K-Block  [N] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  This document describes the Metaphysical Fullstack...         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The trail records HOW you got here, not just where you are. Navigation is reversible: `''` jumps back through the trail.

### Derivation from Principles

| Principle | How Hypergraph Editor Embodies It |
|-----------|----------------------------------|
| **L2.18 Sheaf** | Nodes are local sections; edges are overlap agreements; the graph is the global view |
| **L2.15 Witness** | Every commit is witnessed; INSERT mode creates K-Block with witness trail |
| **L0.2 Morphism** | Edges ARE morphisms between nodes; navigation is morphism composition |

---

## K-Block 3: Crown Jewels

### Metadata

```yaml
title: "Crown Jewels: Domain-Specific Agent Compositions"
level: L3
type: architecture
derives_from:
  - id: "L2.16_OPERAD"
    loss: 0.12
  - id: "L2.17_POLYAGENT"
    loss: 0.15
  - id: "L2.5_COMPOSABLE"
    loss: 0.18
aggregate_loss: 0.15
state: grounded
witnesses:
  - "2025-12-19: Crown Jewel pattern formalized"
  - "2026-01-10: Five active jewels documented"
```

### Content

> *"Crown Jewels are not services. They are categorical compositions with domain semantics."*

Crown Jewels are the domain-specific compositions of categorical primitives. Each jewel is built from PolyAgent, Operad, and Sheaf, but instantiated with domain-specific semantics.

### The Five Crown Jewels

| Jewel | Purpose | Polynomial Positions | AGENTESE Context |
|-------|---------|---------------------|------------------|
| **Brain** | Memory cathedral | IDLE, CAPTURING, CONSOLIDATING, RECALLING | `self.memory.*`, `self.brain.*` |
| **Town** | Multi-agent simulation | IDLE, ACTIVE, DIALOGUING, INHABITING | `world.town.*`, `world.citizen.*` |
| **Witness** | Autonomous agency | L0_OBSERVER, L1_READER, L2_WRITER, L3_KENT | `time.witness.*`, `self.witness.*` |
| **Atelier** | Design studio | SKETCHING, REFINING, CRITIQUING, SHIPPING | `concept.atelier.*`, `self.atelier.*` |
| **K-Block** | Transactional editing | PRISTINE, DIRTY, STALE, CONFLICTING | `self.kblock.*` |

### Categorical Structure of Each Jewel

Every Crown Jewel follows the same categorical pattern:

```python
# 1. PolyAgent: State-dependent behavior
JewelPolynomial = PolyAgent[JewelState, JewelInput, JewelOutput]

# 2. Operad: Composition grammar with laws
JEWEL_OPERAD = Operad(
    operations={...},
    laws=[
        Law("identity", ...),
        Law("associativity", ...),
        Law("domain_specific_1", ...),
    ]
)

# 3. Sheaf: Local-to-global coherence
JewelSheaf = Sheaf[JewelSection](
    opens={...},
    restriction=lambda section, open: ...,
    compatible=lambda s1, s2: ...,
    glue=lambda sections: ...,
)
```

### Crown Jewel Directory Structure

```
services/<jewel>/
├── __init__.py           # Public API exports
├── core.py               # Core domain logic
├── polynomial.py         # JewelPolynomial state machine
├── operad.py             # JEWEL_OPERAD with laws
├── sheaf.py              # JewelSheaf local-global gluing
├── persistence.py        # D-gent integration (adapters HERE, not in models/)
├── node.py               # AGENTESE @node registration
├── contracts.py          # Pydantic models, API contracts
├── web/                  # Frontend lives with service
│   ├── components/       # React components
│   └── hooks/            # Frontend hooks
└── _tests/
    ├── test_polynomial.py
    ├── test_operad_laws.py
    └── test_sheaf_gluing.py
```

### AGENTESE Paths by Jewel

**Brain** (`self.memory.*`, `self.brain.*`):
```
self.memory.capture      # Capture a crystal (thought/insight)
self.memory.recall       # Semantic search over crystals
self.memory.consolidate  # Compress and prune
self.brain.manifest      # Brain status overview
self.brain.status        # Health check
```

**Town** (`world.town.*`, `world.citizen.*`):
```
world.town.manifest      # Town state overview
world.town.simulate      # Advance simulation
world.citizen.manifest   # Citizen list
world.citizen.inhabit    # Enter citizen perspective
world.citizen.dialogue   # Initiate dialogue
```

**Witness** (`time.witness.*`, `self.witness.*`):
```
time.witness.mark        # Create witness mark
time.witness.trail       # Recent marks
time.witness.session     # Session walk
self.witness.manifest    # Witness status
self.witness.trust       # Current trust level
```

**Atelier** (`concept.atelier.*`):
```
concept.atelier.sketch   # Begin design
concept.atelier.refine   # Iterate on design
concept.atelier.critique # Request critique
concept.atelier.ship     # Finalize and ship
```

**K-Block** (`self.kblock.*`):
```
self.kblock.create       # Create isolated editing context
self.kblock.save         # Commit to cosmos
self.kblock.discard      # Abandon changes
self.kblock.checkpoint   # Create restore point
self.kblock.entangle     # Link two K-Blocks
```

### Derivation from Principles

| Principle | How Crown Jewels Embody It |
|-----------|---------------------------|
| **L2.16 Operad** | Each jewel has its own operad with verified laws |
| **L2.17 PolyAgent** | State machines govern mode-dependent behavior |
| **L2.5 Composable** | Jewels compose via AGENTESE paths; cross-jewel via SynergyBus |

---

## K-Block 4: AGENTESE

### Metadata

```yaml
title: "AGENTESE: The Protocol IS the API"
level: L3
type: architecture
derives_from:
  - id: "L0.2_MORPHISM"
    loss: 0.08
  - id: "L1.2_JUDGE"
    loss: 0.10
  - id: "L2.5_COMPOSABLE"
    loss: 0.12
aggregate_loss: 0.10
state: grounded
witnesses:
  - "2025-12-12: AGENTESE parser and resolver complete"
  - "2025-12-17: Universal gateway replaces explicit routes"
  - "2026-01-10: Protocol formalized as architecture K-Block"
```

### Content

> *"The noun is a lie. There is only the rate of change."*

AGENTESE is the verb-first ontology for agent-world interaction. It replaces traditional API routes with semantic paths that work across all transports.

### The Five Contexts

```
CONTEXT     PURPOSE                         EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
world.*     The External                    world.house.manifest
            Entities, environments, tools   world.town.citizen
            Things that exist independently world.calendar.events

self.*      The Internal                    self.memory.capture
            Memory, capability, state       self.soul.dialogue
            Observer's own properties       self.kblock.create

concept.*   The Abstract                    concept.compiler.priors
            Platonics, definitions, logic   concept.atelier.sketch
            Ideas that exist timelessly     concept.specgraph.audit

void.*      The Accursed Share              void.entropy.sip
            Entropy, serendipity, gratitude void.gratitude.offer
            What escapes capture            void.serendipity.invoke

time.*      The Temporal                    time.witness.mark
            Traces, forecasts, schedules    time.differance.recent
            Change over time                time.branch.explore
```

### Why "The Noun Is a Lie"

Traditional APIs treat entities as primary: `GET /users/123`, `POST /documents`. The entity exists; we act upon it.

AGENTESE inverts this: **the action is primary**. Entities emerge from the pattern of actions upon them.

```python
# Traditional (noun-first)
user = await api.get("/users/123")
user.name = "New Name"
await api.put("/users/123", user)

# AGENTESE (verb-first)
await logos.invoke("self.identity.rename", observer, new_name="New Name")
# The "user" is not a thing we manipulate—it's a pattern of identity operations
```

### How Handles Work: Morphisms from Observer to Interaction

AGENTESE paths return **handles**, not data. A handle is a morphism from Observer to Interaction:

```
Handle : Observer -> Interaction
```

Different observers perceive the same path differently:

```python
# Same path, different observers
await logos.invoke("world.house.manifest", architect_umwelt)
# -> Blueprint{floor_plan, materials, load_calculations}

await logos.invoke("world.house.manifest", poet_umwelt)
# -> Metaphor{shelter, dwelling, threshold between worlds}

await logos.invoke("world.house.manifest", child_umwelt)
# -> Drawing{big roof, windows for eyes, door for mouth}
```

This is not polymorphism—it's **observer-dependent projection**. The house doesn't change; the observer's umwelt determines what aspects manifest.

### The Universal Protocol

All transports collapse to the same invocation:

```python
# CLI
kg brain capture "insight"
# -> logos.invoke("self.memory.capture", cli_observer, content="insight")

# HTTP (auto-generated from AGENTESE registration)
POST /agentese/self.memory.capture {"content": "insight"}
# -> logos.invoke("self.memory.capture", http_observer, content="insight")

# WebSocket
ws.send({"path": "self.memory.capture", "args": {"content": "insight"}})
# -> logos.invoke("self.memory.capture", ws_observer, content="insight")

# gRPC, GraphQL, marimo, VR... all the same pattern
```

**Key Insight**: There are no routes to maintain because the protocol IS the route.

### Affordances and Archetypes

Different observers have different affordances (valid actions):

```python
@node("self.memory")
class MemoryNode:
    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        match archetype:
            case "admin":
                return ("capture", "recall", "consolidate", "prune", "wipe")
            case "developer":
                return ("capture", "recall", "consolidate")
            case "guest":
                return ("recall",)  # Read-only
```

Affordances are not access control—they're **capability discovery**. An observer can ask "what can I do here?" and receive a list appropriate to their archetype.

### Derivation from Principles

| Principle | How AGENTESE Embodies It |
|-----------|-------------------------|
| **L0.2 Morphism** | Handles ARE morphisms; paths compose as morphism chains |
| **L1.2 Judge** | Affordances are judge applied to capabilities |
| **L2.5 Composable** | Paths compose: `self.memory.capture >> time.witness.mark` |

---

## K-Block 5: Constitutional Graph

### Metadata

```yaml
title: "The Constitutional Graph: Files as Derivations"
level: L3
type: architecture
derives_from:
  - id: "L1.3_GROUND"
    loss: 0.18
  - id: "L1.8_GALOIS"
    loss: 0.22
  - id: "L2.18_SHEAF"
    loss: 0.20
aggregate_loss: 0.20
state: grounded
witnesses:
  - "2026-01-10: Constitutional graph formalized for genesis"
```

### Content

> *"Files are not IN folders. Files DERIVE FROM principles."*

The Constitutional Graph is the paradigm shift from folder hierarchy to derivation graph. Every file in the system is positioned not by where it lives, but by what it derives from.

### The Paradigm Shift

**Traditional View (Folder Hierarchy)**:
```
kgents/
├── spec/
│   ├── protocols/
│   │   └── k-block.md        <- "k-block.md is in protocols/ in spec/"
│   └── principles/
│       └── CONSTITUTION.md   <- "CONSTITUTION.md is in principles/"
└── impl/
    └── claude/
        └── services/
            └── k_block/      <- "k_block/ is in services/"
```

**Constitutional View (Derivation Graph)**:
```
CONSTITUTION.md (L0: Axioms)
       │
       ├─derives─▶ L2.5_COMPOSABLE (L2: Derived Principle)
       │                 │
       │                 └─derives─▶ k-block.md (L3: Spec)
       │                                   │
       │                                   └─implements─▶ services/k_block/
       │
       └─derives─▶ L2.18_SHEAF (L2: Derived Principle)
                         │
                         └─derives─▶ hypergraph-editor.md (L3: Spec)
```

### File States in the Constitutional Graph

| State | Meaning | Visual Indicator | Action Required |
|-------|---------|-----------------|-----------------|
| **Grounded** | Has explicit derivation with L < 0.3 | Green node, solid edge | None |
| **Provisional** | Has derivation with 0.3 < L < 0.7 | Yellow node, dashed edge | Consider grounding |
| **Orphan** | No derivation edges | Red node, no edges | Must derive or delete |
| **Contradicting** | Derives from principles it violates | Red node, red edges | Resolve contradiction |

### The Derivation Trail Bar

The Derivation Trail Bar replaces traditional breadcrumbs. Instead of showing folder path, it shows constitutional derivation:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ◀ L0.2_MORPHISM │ L2.5_COMPOSABLE │ fullstack.md │ ▶ impl (3 files)    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DERIVATION TRAIL:                                                      │
│  CONSTITUTION.md → L0.2_MORPHISM → L2.5_COMPOSABLE → fullstack.md       │
│                                                                         │
│  GALOIS LOSS: 0.12 (grounded)                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Project Realization (Welcome Screen)

The Project Realization is the welcome screen that shows constitutional coherence:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        K G E N T S                                      │
│                                                                         │
│           Constitutional Coherence: 87% grounded                        │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │              [CONSTITUTION.md]                                    │  │
│  │                    │                                              │  │
│  │    ┌───────────────┼───────────────┐                              │  │
│  │    │               │               │                              │  │
│  │  [L2.5]         [L2.7]         [L2.18]                            │  │
│  │    │               │               │                              │  │
│  │ ┌──┴──┐       ┌────┴────┐    ┌────┴────┐                          │  │
│  │ │Brain│       │Fullstack│    │Hypergraph│                         │  │
│  │ │     │       │         │    │Editor   │                          │  │
│  │ └─────┘       └─────────┘    └─────────┘                          │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ORPHANS (3): models/legacy.py, scripts/old_migration.py, temp/        │
│  PROVISIONAL (5): services/experimental/*, agents/wip/*                │
│                                                                         │
│  [Navigate Graph]  [Ground Orphans]  [View Constitution]               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Coherence Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Grounding Rate** | grounded_files / total_files | > 80% |
| **Average Galois Loss** | mean(L(file)) for all files | < 0.25 |
| **Orphan Count** | count(files with no derivation) | 0 |
| **Contradiction Count** | count(files with violations) | 0 |
| **Derivation Depth** | max path from CONSTITUTION to leaf | 3-5 (L0 → L3 → impl) |

### The Derivation Query Language

```
# Find all files deriving from a principle
derives_from:L2.5_COMPOSABLE

# Find orphans
state:orphan

# Find files with high loss
loss:>0.5

# Find implementations of a spec
implements:k-block.md

# Combined queries
derives_from:L2.18_SHEAF AND state:grounded AND loss:<0.2
```

### Derivation from Principles

| Principle | How Constitutional Graph Embodies It |
|-----------|-------------------------------------|
| **L1.3 Ground** | Files are grounded in principles, not folders |
| **L1.8 Galois** | Loss measures derivation quality; axiom iff L < epsilon |
| **L2.18 Sheaf** | Local files (sections) glue to global coherence (project) |

---

## Part III: Implementation Notes

### K-Block Schema for Architecture Blocks

```python
@dataclass
class ArchitectureKBlock:
    """K-Block for architecture self-description."""

    # Identity
    id: str
    title: str
    level: Literal["L0", "L1", "L2", "L3"]
    type: Literal["architecture", "principle", "spec", "impl"]

    # Derivation
    derives_from: list[Derivation]
    aggregate_loss: float
    state: Literal["grounded", "provisional", "orphan", "contradicting"]

    # Content
    content: str  # Markdown content

    # Witness
    witnesses: list[WitnessEntry]

    # Navigation
    children: list[str]  # K-Block IDs that derive from this
    implementations: list[str]  # File paths that implement this

@dataclass
class Derivation:
    """Single derivation edge."""
    source_id: str
    loss: float
    edge_type: Literal["derives_from", "implements", "tests", "extends"]
    witness: WitnessEntry | None = None
```

### AGENTESE Registration

```python
@node("concept.architecture", dependencies=("kblock_store",))
class ArchitectureNode:
    """AGENTESE access to architecture K-Blocks."""

    store: KBlockStore

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> ArchitectureManifest:
        """Get architecture overview."""
        return await self.store.get_architecture_manifest()

    @aspect(category=AspectCategory.PERCEPTION)
    async def kblock(self, observer: Observer, id: str) -> ArchitectureKBlock:
        """Get specific architecture K-Block."""
        return await self.store.get_kblock(id)

    @aspect(category=AspectCategory.PERCEPTION)
    async def derivations(self, observer: Observer, from_id: str) -> list[ArchitectureKBlock]:
        """Get all K-Blocks deriving from a given block."""
        return await self.store.get_derivations(from_id)

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("kblocks")])
    async def ground(
        self,
        observer: Observer,
        kblock_id: str,
        derives_from: str,
        loss: float
    ) -> GroundResult:
        """Ground an orphan K-Block by establishing derivation."""
        return await self.store.ground(kblock_id, derives_from, loss)
```

---

## Part IV: Connection to Genesis

These five architecture K-Blocks form the self-describing core of the kgents genesis:

1. **Metaphysical Fullstack** explains HOW agents are structured
2. **Hypergraph Editor** explains HOW navigation works
3. **Crown Jewels** explains WHAT domain compositions exist
4. **AGENTESE** explains HOW agents communicate
5. **Constitutional Graph** explains HOW coherence is maintained

Together, they enable a new developer to understand kgents not by reading documentation, but by navigating the constitutional graph from principles to implementations.

---

## Part V: Verification Criteria

### K-Block Coherence Tests

```python
def test_all_architecture_kblocks_grounded():
    """All architecture K-Blocks must be grounded (L < 0.3)."""
    blocks = get_architecture_kblocks()
    for block in blocks:
        assert block.state == "grounded"
        assert block.aggregate_loss < 0.3

def test_derivation_edges_valid():
    """All derivation edges must point to existing K-Blocks."""
    blocks = get_architecture_kblocks()
    all_ids = {b.id for b in blocks}
    for block in blocks:
        for deriv in block.derives_from:
            assert deriv.source_id in all_ids or deriv.source_id.startswith("L")

def test_no_circular_derivations():
    """Derivation graph must be acyclic."""
    blocks = get_architecture_kblocks()
    graph = build_derivation_graph(blocks)
    assert is_acyclic(graph)

def test_implementations_exist():
    """All referenced implementations must exist on disk."""
    blocks = get_architecture_kblocks()
    for block in blocks:
        for impl_path in block.implementations:
            assert Path(impl_path).exists()
```

---

## Closing Meditation

> *"The system knows itself. Architecture is not documented—it is derived."*

These five K-Blocks are not descriptions of architecture. They ARE architecture, self-describing through derivation from principles with measured Galois loss.

When a new developer enters kgents, they do not read a README. They navigate the constitutional graph, following derivation edges from CONSTITUTION.md through L2 principles to L3 specifications to implementations.

The files are not _in folders_. The files _derive from principles_.

---

*Design specification written: 2026-01-10*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
