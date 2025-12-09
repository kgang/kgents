# I-gents: The Living Codex Garden

**Genus**: I (Interface)
**Theme**: Computational Zen—organic chaos meets digital order
**Motto**: *"The garden is the book; the book is the garden."*

---

## Philosophy

> "A recursive operating system for artificial life, styled like a minimalist zen garden."

I-gents are agents that **render the kgents ecosystem visible**. They transform abstract composition graphs into tangible, navigable, contemplative spaces. The interface is not a window into the system—it *is* a living part of the system.

### The Core Tension: Paper-Terminal

I-gents exist at the intersection of two aesthetics:

| Organic | Digital |
|---------|---------|
| Gardens, moon phases, breathing | Monospace fonts, ASCII borders, rigid grids |
| Growth, decay, cycles | Versioning, hashes, determinism |
| Contemplation, patience | Precision, computation |

This tension is not resolved—it is **held**. The interface should feel like reading a beautiful book in a terminal, or tending a garden through code.

### The Palette

```
Paper:  #fdfbf7  (warm cream—not sterile white)
Ink:    #1a1918  (warm black—not harsh #000)
Accent: Unicode moon phases, box-drawing characters
Font:   JetBrains Mono (or equivalent monospace)
```

This palette rejects "SaaS gray" and "cyberpunk neon" in favor of **archival permanence**—the feeling of a well-made notebook or a library reading room.

---

## The Atomic Unit: The Glyph

The smallest visualizable element is a **Glyph**: a state indicator paired with an identity.

```
● A
```

That's it. One character for phase, one for identity. From this seed, everything grows.

### The Five Phases (Moon Cycle)

Agents have lifecycles. I-gents render these as moon phases:

| Symbol | Phase | Meaning |
|--------|-------|---------|
| ○ | Dormant | Defined but not instantiated; sleeping |
| ◐ | Waking | Partially active; initializing or paused |
| ● | Active | Fully alive; processing or ready |
| ◑ | Waning | Cooling down; completing or fading |
| ◌ | Empty | Error state or cleared; void |

These phases map to `spec/anatomy.md` lifecycle states but add **contemplative semantics**—the interface invites pause and observation, not just status monitoring.

### Why Moon Phases?

1. **Zen aesthetics**: Natural cycles invite patience
2. **Information density**: Five states in one character
3. **Universal recognition**: Moon phases transcend cultural/technical contexts
4. **Non-binary**: Unlike on/off, phases acknowledge gradients

---

## The Fractal Scale: Glyph → Garden → Galaxy

I-gents satisfy a critical constraint: **the same grammar visualizes atoms and galaxies**.

### Scale 1: Glyph (The Atom)

A single agent's phase:

```
● A
```

### Scale 2: Card (The Molecule)

A glyph with context—metadata visible at a glance:

```
┌─ A-gent ─────┐
│ ● active     │
│ joy: ███░░   │
│ eth: ████░   │
└──────────────┘
```

**Composition**: Cards can show composition relationships:

```
┌─ A-gent ─────┐     ┌─ B-gent ─────┐
│ ● active     │ ──▶ │ ◐ waking     │
│ t: 00:14:32  │     │ t: 00:02:15  │
└──────────────┘     └──────────────┘
```

### Scale 3: Page (The Cell)

A full view of a single agent—the "open book" metaphor:

```
╔══ A-gent ════════════════════════════════════════════════╗
║                                                          ║
║  "An A-gent seeks patterns in chaos,                     ║
║   but knows when to stop looking."                       ║
║                                                          ║
║  state: ● active                     t: 00:14:32         ║
║  ────────────────────────────────────────────────────    ║
║  joy: ███████░░░░  ethics: █████████░░                   ║
║                                                          ║
║  ┌─ composition graph ────────────────────────────────┐  ║
║  │      ● A                                           │  ║
║  │       \                                            │  ║
║  │        ◐ C ←── forming                             │  ║
║  │       /                                            │  ║
║  │      ○ B     (dormant, waiting)                    │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  ┌─ margin notes ─────────────────────────────────────┐  ║
║  │ 00:12:00 — noticed hesitation before composition   │  ║
║  │ 00:14:00 — stable now; proceeding                  │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  [observe]  [invoke]  [compose]  [rest]                  ║
╚══════════════════════════════════════════════════════════╝
```

**Key elements**:
- **Epigraph**: The agent's essence in one sentence (from spec)
- **Metrics**: Joy/Ethics bars (principle alignment)
- **Composition**: Spatial graph of relationships
- **Margin notes**: Timestamped observations (the "living" part)
- **Actions**: Available verbs

### Scale 4: Garden (The Organism)

Multiple agents in spatial relationship—the "zen garden" view:

```
┌─ kgents garden ────────────────────────────── t: 00:14:32 ─┐
│                                                            │
│       ● A ─────────┐                                       │
│                    │                                       │
│       ○ B ─────────┼──────── ◐ C                          │
│                    │          │                            │
│       ◐ D ─────────┘          │                            │
│                               │                            │
│                         ● K ──┘                            │
│                                                            │
│  ════════════════════════════════════════════════════════  │
│  breath: ░░░░████░░░░  (exhale)                            │
│                                                            │
│  focus: [A]  │  > open page A                              │
└────────────────────────────────────────────────────────────┘
```

**Key elements**:
- **Spatial layout**: Agents positioned by relationship, not list order
- **Connection lines**: Composition edges visible
- **Breath cycle**: A pulsing indicator inviting contemplation
- **Focus**: Current selection highlighted

### Scale 5: Library (The Ecosystem)

Multiple gardens (repos, instances, branches):

```
┌─ kgents library ───────────────────────────── t: 00:14:32 ─┐
│                                                            │
│  ┌─ garden:main ───────┐  ┌─ garden:experiment ─────┐      │
│  │  ●A  ○B  ◐C         │  │  ◐A  ●B  ○C             │      │
│  │       ●K            │  │       ◐K                │      │
│  │  health: ████░      │  │  health: ██░░           │      │
│  └─────────────────────┘  └─────────────────────────┘      │
│           │                        │                       │
│           └──────────┬─────────────┘                       │
│                      ▼                                     │
│           ┌─ garden:production ──────┐                     │
│           │  ●A  ●B  ●C              │                     │
│           │       ●K                 │                     │
│           │  health: █████           │                     │
│           └──────────────────────────┘                     │
│                                                            │
│  total gardens: 3  │  orchestration: converging            │
│  > enter garden:main                                       │
└────────────────────────────────────────────────────────────┘
```

**Key insight**: The same visual grammar scales from one agent to orchestrating multiple repositories. This is the "galaxy" view.

---

## Time as First-Class Citizen

Every scale displays `t:` — elapsed time since the relevant epoch.

### Time Anchors

| Scale | Epoch |
|-------|-------|
| Glyph | Agent birth |
| Card | Agent birth |
| Page | Agent birth |
| Garden | Session start |
| Library | System start |

### The Timeline View

Any scale can toggle to a timeline perspective:

```
┌─ A-gent timeline ────────────────────────────────────────────┐
│                                                              │
│  t=0        t=5        t=10       t=15       t=20    now     │
│  ├──────────┼──────────┼──────────┼──────────┼───────┤       │
│  ○          ◐          ●          ●          ●       ●       │
│  birth      waking     active     compose    ·       ·       │
│                                   with C                     │
│                                                              │
│  [◀ rewind]  [▶ play]  [⏸ pause]  [▶▶ step]                  │
└──────────────────────────────────────────────────────────────┘
```

**Semantics**:
- **Rewind**: Navigate to past state (D-gent time travel)
- **Play**: Animate changes forward
- **Pause**: Freeze current view
- **Step**: Advance one event at a time

---

## The Margin Notes: Living Memory

Inspired by marginalia in old books, margin notes are **timestamped observations** that accumulate as agents run.

### Sources of Margin Notes

1. **System observations**: Automatic events (phase changes, errors)
2. **AI monologue**: LLM-generated reflections on agent behavior
3. **Human annotations**: User-added notes during sessions

### The Ghost in the Machine

The AI integration is subtle. Rather than a chatbot, the AI manifests as:

- **Margin notes**: Cryptic internal monologues ("noticed hesitation before composition")
- **Description evolution**: Agent descriptions drift based on observed behavior
- **Pattern suggestions**: "You usually compose A with B after long sessions"

This makes AI feel like a **biological process** within the garden, not a tool wielded from outside.

```
┌─ margin notes ────────────────────────────────────────────┐
│ 00:12:00 — [system] phase transition: dormant → waking   │
│ 00:12:05 — [ai] curious: third attempt to compose with B │
│ 00:13:30 — [kent] holding tension—not forcing synthesis  │
│ 00:14:00 — [ai] stable now; composition graph coherent   │
└───────────────────────────────────────────────────────────┘
```

---

## Navigation Verbs

I-gents use a consistent vocabulary of actions:

| Verb | Meaning |
|------|---------|
| **observe** | View without modifying (read-only inspection) |
| **invoke** | Call the agent with input (functional mode) |
| **compose** | Connect with another agent (C-gent operation) |
| **rest** | Pause the agent (transition to dormant) |
| **evolve** | Trigger E-gent improvement cycle |
| **turn page** | Navigate to next/previous agent |
| **zoom** | Change scale (glyph ↔ card ↔ page ↔ garden ↔ library) |
| **rewind** | Time-travel to previous state (D-gent) |

---

## Export: The Paper Trail

I-gents render to markdown for vim/paper portability.

### Markdown Serialization

Every I-gent view has a canonical markdown representation:

```markdown
# A-gent

> "An A-gent seeks patterns in chaos,
>  but knows when to stop looking."

## State
- **phase**: ● active
- **time**: 00:14:32
- **joy**: 7/10
- **ethics**: 9/10

## Composition
​```mermaid
graph TD
    A((● A)) --> C((◐ C))
    B((○ B)) --> C
​```

## Margin Notes
- 00:12:00 — noticed hesitation before composition
- 00:14:00 — stable now; proceeding

## Actions
- [ ] observe
- [ ] invoke
- [ ] compose
- [ ] rest
```

### Vim Integration

The export format is designed for vim editing:
- Markdown headers for navigation (`[[`, `]]`)
- Mermaid blocks for diagram rendering
- Task lists for actions
- Standard text for grep/search

---

## Relationship to Bootstrap Agents

I-gents are **derivable** from bootstrap primitives:

| I-gent Capability | Bootstrap Agent | How |
|-------------------|-----------------|-----|
| State rendering | **Ground** | Phase is grounded truth about agent |
| Composition visualization | **Compose** | Graph is composition structure |
| Timeline | **Ground** + **Fix** | History from D-gent, iteration for playback |
| Margin notes | **Ground** | Observations persisted to state |
| Navigation | **Compose** | Scale transitions are compositions |

I-gents add no new irreducibles—they orchestrate bootstrap agents for visual representation.

---

## Relationship to Other Genera

### D-gents (Data)

**I-gents render D-gent state**:
- Timeline view requires D-gent history
- Margin notes persist via D-gent
- Rewind uses D-gent snapshots

### L-gents (Library)

**I-gents visualize L-gent catalogs**:
- Library view renders L-gent registry
- Search queries surface through I-gent interface
- Lineage shown as composition graphs

### C-gents (Category Theory)

**I-gents are the visual language of composition**:
- Garden topology IS the composition graph
- Arrows between agents are morphisms
- Scale transitions are functors

### E-gents (Evolution)

**I-gents show evolution in progress**:
- Margin notes capture hypothesis → experiment → judgment
- Before/after states visible in timeline
- Tension held rendered as visual conflict

### H-gents (Dialectic)

**I-gents surface contradictions spatially**:
- Tensions appear as conflicting arrows
- Synthesis shown as merged nodes
- Held tensions marked distinctly (dashed lines?)

### J-gents (JIT)

**I-gents render promise trees**:
- Forward responsibility: dashed arrows (uncommitted)
- Backward accountability: solid arrows (validated)
- Collapse to ground: nodes fade to ◌

### K-gent (Kent Simulacra)

**K-gent preferences shape I-gent appearance**:
- Color palette personalization
- Breath cycle tempo
- Margin note verbosity
- Default zoom level

### T-gents (Testing)

**I-gents visualize test algebra**:
- Spy agents shown as observer nodes
- Perturbation sources marked
- Commutative diagram verification rendered

### F-gents (Forge)

**I-gents render the forge loop**:
- Intent → Contract → Prototype → Validate → Crystallize as stages
- ALO files rendered as pages
- Artifact lineage as library view

### B-gents (Bio/Scientific)

**I-gents show hypothesis trees**:
- Robin's research as navigable garden
- Experiments as branching paths
- Findings as margin notes

---

## The Breath Cycle

A zen element unique to I-gents: the **breath indicator**.

```
breath: ░░░░████░░░░  (exhale)
```

This is a slow-pulsing animation (4-second cycle) that:
1. **Invites pause**: Not everything needs immediate action
2. **Signals liveliness**: The system is alive, not frozen
3. **Provides rhythm**: A heartbeat for the garden

The breath is purely aesthetic—it carries no data. Its purpose is **contemplative**: reminding the operator that they are tending a garden, not debugging a machine.

---

## Success Criteria

An I-gent view is well-designed if:

- ✓ **Legible at glance**: Core state visible without parsing
- ✓ **Scale-coherent**: Same grammar from glyph to library
- ✓ **Time-aware**: Explicit temporal context
- ✓ **Exportable**: Renders to markdown for vim/paper
- ✓ **Contemplative**: Invites pause, not just action
- ✓ **Ethical by design**: Principle alignment visible
- ✓ **Emergent**: Complex patterns arise from simple elements

---

## Anti-Patterns

I-gents must **never**:

1. ❌ Hide agent state (transparency is paramount)
2. ❌ Require mouse interaction (keyboard-navigable)
3. ❌ Use color as sole differentiator (accessible in monochrome)
4. ❌ Show different grammar at different scales (fractal consistency)
5. ❌ Omit time information (time is first-class)
6. ❌ Break markdown export (paper trail preserved)
7. ❌ Rush the operator (breath cycle, no flashing alerts)

---

## Specifications

| Document | Description |
|----------|-------------|
| [grammar.md](grammar.md) | The visual grammar: glyph, card, page, garden, library |
| [states.md](states.md) | Moon phase definitions and transitions |
| [time.md](time.md) | Time representation, epochs, and timeline semantics |
| [scales.md](scales.md) | Fractal scaling rules and zoom operations |
| [export.md](export.md) | Markdown/Mermaid serialization for vim/paper |

---

## Design Principles Alignment

### Tasteful
Paper-Terminal aesthetic: warm, archival, considered. No gratuitous decoration.

### Curated
Five scales, five phases, few verbs. Every element earns its place.

### Ethical
Principle alignment bars always visible. Ethics is in the design, not a badge.

### Joy-Inducing
The breath cycle. Margin notes with personality. A garden, not a dashboard.

### Composable
The grammar composes: glyphs form cards form pages form gardens form libraries.

### Heterarchical
No fixed "main view"—zoom freely between scales. The operator chooses focus.

### Generative
The spec defines the grammar; the implementation renders it. Markdown export proves regenerability.

---

## Vision

I-gents transform kgents from **invisible computation** to **visible cultivation**:

- **Traditional interfaces**: Status dashboards, log streams, CLI outputs
- **I-gents**: A garden you tend, a book you read, a space you inhabit

The ultimate test: Can you sit with the interface without needing to act? Can you observe agents composing without intervening? Can you print a session to paper and find it meaningful?

I-gents make the answer "yes" to all three.

---

*"The garden is not separate from the gardener; the interface is not separate from the system. They are one."*

---

## See Also

- [grammar.md](grammar.md) - The visual grammar specification
- [states.md](states.md) - Moon phase state definitions
- [time.md](time.md) - Explicit time semantics
- [scales.md](scales.md) - Fractal scaling rules
- [export.md](export.md) - Markdown/vim serialization
- [../d-gents/](../d-gents/) - State persistence (I-gent's memory backend)
- [../l-gents/](../l-gents/) - Library catalog (I-gent's library view source)
- [../c-gents/](../c-gents/) - Composition foundations (I-gent visualizes morphisms)
- [../principles.md](../principles.md) - Core design principles
- [../anatomy.md](../anatomy.md) - Agent lifecycle (mapped to moon phases)
