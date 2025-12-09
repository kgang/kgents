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
| **observe** | View agent internals without modifying (spawns W-gent for process inspection) |
| **invoke** | Call the agent with input (functional mode) |
| **compose** | Connect with another agent (C-gent operation) |
| **rest** | Pause the agent (transition to dormant) |
| **evolve** | Trigger E-gent improvement cycle |
| **turn page** | Navigate to next/previous agent |
| **zoom** | Change scale (glyph ↔ card ↔ page ↔ garden ↔ library) |
| **rewind** | Time-travel to previous state (D-gent) |

**Note on `observe`**: The observe action spawns a **W-gent (Wire Agent)** that projects the agent's internal execution stream to a browser view at `localhost:8000`. While I-gents show *ecosystem composition* (how agents relate), W-gents show *process internals* (what an agent is thinking). See [W-gents specification](../w-gents/) for details.

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

### W-gents (Wire)

**I-gents spawn W-gents for process observation**:
- `[observe]` action launches W-gent attached to selected agent
- W-gent projects internal execution stream (logs, progress, metrics)
- W-gent observations can be exported back to I-gent margin notes
- **Complementary scope**: I-gents show ecosystem, W-gents show internals

**The relationship**:
```
I-gent (ecosystem view) ──[observe]──> W-gent (process view)
                        <──[export]──
```

See [W-gents/I-gent synergy](../w-gents/i-gent-synergy.md) for integration details.

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

## Production Integration: Batteries Included

I-gents are not mere visualizers—they are **operational interfaces** for the entire kgents ecosystem. This section defines production-ready integration patterns.

### Design Philosophy

**Batteries Included Means**:
- ✓ Zero-config startup: `kgents garden` opens a live garden
- ✓ CLI integration: Native commands, not separate tools
- ✓ Persistent sessions: Resume where you left off
- ✓ Export everywhere: Markdown, JSON, screenshots
- ✓ Graceful degradation: Works without network, GPU, or color
- ✓ Keyboard-first: Every action has a shortcut
- ✓ Hook system: Custom actions per garden

---

### Bootstrap Agent Visualization

Bootstrap agents are the **irreducible core** and deserve special rendering.

#### Ground Agent Visualization

**Ground**: `Void → Facts` (persona + world)

```
┌─ Ground (seed phase) ──────────────────────────┐
│ ○ → ● planting seed                             │
│                                                 │
│ persona:  Kent's values (7 principles)          │
│ world:    2025-12-08, macOS, Python 3.13        │
│                                                 │
│ ┌─ seed vitality ─────────────────────────────┐ │
│ │ tasteful:  ██████████ 100%                  │ │
│ │ ethical:   ██████████ 100%                  │ │
│ │ curated:   ██████████ 100%                  │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [view persona] [view world] [refresh]           │
└─────────────────────────────────────────────────┘
```

**Special semantics**: Ground is always at the root of the garden. Other agents grow from it.

#### Contradict Agent Visualization

**Contradict**: `(A, B) → Tension`

```
┌─ Contradict (tension detection) ───────────────┐
│ ● active       inputs: (thesis, antithesis)     │
│                                                 │
│ current tension:                                │
│   "Be fast" ⚡ "Be thorough"                    │
│   ├─ severity: 0.7  (high tension)              │
│   ├─ mode: PRACTICAL                            │
│   └─ first detected: 00:12:34 ago               │
│                                                 │
│ tension history: [3 total]                      │
│   ◑ resolved: "Quality vs Speed" (5min ago)     │
│   ◑ resolved: "Local vs Cloud" (15min ago)      │
│   ● active:   "Fast vs Thorough" (now)          │
│                                                 │
│ [view details] [suggest synthesis]              │
└─────────────────────────────────────────────────┘
```

**Special semantics**: Shows active tensions with visual conflict indicators (⚡).

#### Sublate Agent Visualization

**Sublate**: `Tension → Synthesis | HoldTension`

```
┌─ Sublate (synthesis engine) ───────────────────┐
│ ● active       recent: 12 syntheses, 3 holds    │
│                                                 │
│ current operation:                              │
│   input:  Tension("Fast vs Thorough")           │
│   status: ◐ evaluating strategies               │
│   time:   00:00:02 / ~00:00:05                  │
│                                                 │
│ strategy attempts:                              │
│   ✓ PreserveStrategy:  viable (87% confidence)  │
│   ⧗ NegateStrategy:    evaluating...            │
│   ○ ElevateStrategy:   pending                  │
│                                                 │
│ likely outcome: HoldTension                     │
│   reason: "Temporal tension (wait for context)" │
│                                                 │
│ [force synthesis] [accept hold] [observe]       │
└─────────────────────────────────────────────────┘
```

**Special semantics**: Shows synthesis decision tree in real-time.

#### Judge Agent Visualization

**Judge**: `Agent → Verdict` (7 principles scorecard)

```
┌─ Judge (principle validator) ──────────────────┐
│ ● active       verdicts issued: 45 (12 revised) │
│                                                 │
│ judging: robin-agent                            │
│   ┌─ 7 principles scorecard ─────────────────┐  │
│   │ ✓ Tasteful:      ████████░░ 80%  pass   │  │
│   │ ✓ Curated:       ███████░░░ 70%  pass   │  │
│   │ ✓ Ethical:       ██████████ 100% pass   │  │
│   │ ✓ Joy-Inducing:  █████████░ 90%  pass   │  │
│   │ ✓ Composable:    ████████░░ 80%  pass   │  │
│   │ ⚠ Heterarchical: █████░░░░░ 50%  review  │  │
│   │ ✓ Generative:    ███████░░░ 70%  pass   │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│ overall verdict: REVISE (heterarchy concern)    │
│   suggestion: "Add multi-scale navigation"      │
│                                                 │
│ [accept] [revise agent] [view reasoning]        │
└─────────────────────────────────────────────────┘
```

**Special semantics**: The 7 principles are always visible, color-coded by threshold.

#### Fix Agent Visualization

**Fix**: Fixed-point iteration with entropy budget

```
┌─ Fix (convergence iterator) ───────────────────┐
│ ● active       iteration: 4/10, entropy: 0.65/1 │
│                                                 │
│ convergence trajectory:                         │
│   iter 1:  ════════════════════ 0.95 similarity │
│   iter 2:  ═══════════════════  0.97            │
│   iter 3:  ══════════════════   0.98            │
│   iter 4:  ═════════════════    0.99 ← current  │
│   target:  threshold reached (0.99 > 0.95)      │
│                                                 │
│ status: ● CONVERGED                             │
│   entropy remaining: 0.35 (safe margin)         │
│   next: finalize fixed point                    │
│                                                 │
│ convergence graph:                              │
│   1.00 ┤        ━━━━━━━━━ (threshold)          │
│   0.95 ┤     ╱━                                 │
│   0.90 ┤   ╱                                    │
│   0.85 ┤ ●                                      │
│        └────┬────┬────┬────                     │
│            1    2    3    4  (iterations)       │
│                                                 │
│ [view trajectory] [restart] [observe]           │
└─────────────────────────────────────────────────┘
```

**Special semantics**: Shows convergence visually with entropy budget tracking.

---

### evolve.py Integration

The `evolve.py` script **must** integrate with I-gents for live evolution visualization.

#### Pattern: Live Evolution Garden

```bash
# Terminal 1: Start evolution with garden mode
$ kgents evolve agents/e/safety.py --garden

# Terminal 2: Auto-launched I-gent garden view
┌─ Evolution Session ──────────────────── t: 00:15:32 ─┐
│                                                      │
│ target: agents/e/safety.py                           │
│                                                      │
│ pipeline:                                            │
│   ● Ground       ✓ complete                          │
│   ● Contradict   ✓ complete                          │
│   ◐ Sublate      ⧗ evaluating (iter 3/10)           │
│   ○ Judge        ⏸ waiting                           │
│   ○ Fix          ⏸ waiting                           │
│                                                      │
│ current hypothesis:                                  │
│   "Extract _validate_hypothesis to separate method"  │
│   confidence: 0.87                                   │
│   safety check: ● PASSING                            │
│                                                      │
│ code similarity: ░░░░░░████ 75%                      │
│   (target: 95% for convergence)                      │
│                                                      │
│ [pause] [skip] [abort] [view diff]                   │
└──────────────────────────────────────────────────────┘
```

**Implementation**:
```python
# In evolve.py
from agents.i import GardenRenderer, GardenState, Phase

async def evolve_with_garden(module: CodeModule):
    # Create garden state
    garden = GardenState(
        name=f"evolve-{module.name}",
        session_start=datetime.now(),
    )

    # Add bootstrap agents to garden
    garden.add_agent(AgentState("Ground", Phase.ACTIVE, ...))
    garden.add_agent(AgentState("Contradict", Phase.DORMANT, ...))

    # Evolve with live updates
    async for event in evolution_pipeline(module):
        # Update garden state
        if event.type == "phase_change":
            garden.get_agent(event.agent).transition_to(event.new_phase)

        # Render updated garden
        print("\033[2J\033[H")  # Clear screen
        print(GardenRenderer(garden).render())

        await asyncio.sleep(0.1)  # Breath cycle
```

**CLI integration**:
```bash
# With garden visualization
$ kgents evolve --garden
$ kgents evolve --garden --export evolution-session.md

# Attach to running evolution
$ kgents garden attach --process evolve-12345
```

---

### Cross-Genus Workflows

Each genus has specific interaction patterns that I-gents must support.

#### E-gents: Evolution Visualization

```
┌─ E-gent: EvolutionPipeline ────────────────────────┐
│ ◐ waking       phase: hypothesize                  │
│                                                    │
│ workflow progress:                                 │
│   ✓ Ground (AST analysis)                          │
│   ✓ Hypothesize (5 ideas generated)                │
│   ◐ Memory Filter (checking history...)            │
│   ○ Experiment                                     │
│   ○ Validate                                       │
│   ○ Incorporate                                    │
│                                                    │
│ current module: agents/e/safety.py                 │
│   hypotheses: 3 passed filter, 2 rejected          │
│   next: run syntax validation                      │
│                                                    │
│ [view hypotheses] [skip to validate] [observe]     │
└────────────────────────────────────────────────────┘
```

#### F-gents: Forge Workflow

```
┌─ F-gent: ForgeAgent ───────────────────────────────┐
│ ● active       phase: 3/5 (prototype)              │
│                                                    │
│ forge pipeline:                                    │
│   ✓ 1. Intent Parsing     (complete)               │
│   ✓ 2. Contract Synthesis (complete)               │
│   ◐ 3. Prototype         (generating code...)      │
│   ○ 4. Validate          (pending)                 │
│   ○ 5. Crystallize       (pending)                 │
│                                                    │
│ artifact: weather-agent.alo.md                     │
│   type: Agent[str, WeatherData]                    │
│   contract: 3 invariants, 2 composition rules      │
│   status: ◐ prototype in progress                  │
│                                                    │
│ [view contract] [view code] [skip to validate]     │
└────────────────────────────────────────────────────┘
```

#### H-gents: Dialectic Visualization

```
┌─ H-gent: HegelAgent ───────────────────────────────┐
│ ● active       dialectic: thesis/antithesis → ?    │
│                                                    │
│ current dialectic:                                 │
│   thesis:      "Fast iteration"                    │
│   antithesis:  "Thorough validation"               │
│   tension:     0.7 severity (PRACTICAL mode)       │
│                                                    │
│ sublation status: ◐ evaluating strategies          │
│   strategy 1: PRESERVE both (87% viable)           │
│   strategy 2: NEGATE speed (12% viable)            │
│   strategy 3: ELEVATE to "smart shortcuts"         │
│                                                    │
│ likely outcome: SYNTHESIS (elevate)                │
│   result: "Fast validation via caching"            │
│                                                    │
│ dialectic lineage: [view 12 prior syntheses]       │
│                                                    │
│ [force synthesis] [hold tension] [observe]         │
└────────────────────────────────────────────────────┘
```

#### D-gents: State History Playback

```
┌─ D-gent: PersistentAgent ──────────────────────────┐
│ ● active       storage: .state/robin-persona.json  │
│                                                    │
│ state history: [15 snapshots, 2.5 hours]           │
│   ├─ 18:00  PersonaState(confidence=0.6)           │
│   ├─ 18:30  PersonaState(confidence=0.7)           │
│   ├─ 19:00  PersonaState(confidence=0.8)           │
│   └─ 19:30  PersonaState(confidence=0.9) ← now     │
│                                                    │
│ timeline scrubber:                                 │
│   18:00 ├───┼───┼───┼───┤ 19:30                    │
│         ↑           ↑   ↑                          │
│        start      peak  now                        │
│                                                    │
│ playback controls:                                 │
│   [◀◀] [◀] [⏸] [▶] [▶▶]  speed: 1x                │
│                                                    │
│ [export history] [diff snapshots] [observe]        │
└────────────────────────────────────────────────────┘
```

#### L-gents: Library Navigation

```
┌─ L-gent: Registry (synaptic librarian) ────────────┐
│ ● active       catalog: 47 entries, 12 genera      │
│                                                    │
│ search: "hypothesis" ────────────────┐             │
│   ✓ B-hypothesis-agent               │ 5 results  │
│   ✓ hypothesis-indexing (L-gent)     │             │
│   ✓ generate_targeted_hypotheses     │             │
│   ✓ HypothesisOutput (dataclass)     │             │
│   ✓ hypothesis outcome tracking      │             │
│ ──────────────────────────────────────┘             │
│                                                    │
│ focus: B-hypothesis-agent                          │
│   type: Agent[Domain, HypothesisOutput]            │
│   author: spec/b-gents/hypothesis.md               │
│   tags: scientific-method, discovery, testable     │
│   relationships:                                   │
│     ├─ composes_with: PersonaAgent                 │
│     └─ used_by: RobinAgent                         │
│                                                    │
│ [open page] [view relationships] [observe]         │
└────────────────────────────────────────────────────┘
```

---

### CLI Integration

I-gents provide first-class CLI commands, not separate tools.

```bash
# Garden commands
$ kgents garden                        # Open live garden (current session)
$ kgents garden --load session.json   # Load saved session
$ kgents garden --filter "genus=B"    # Show only B-gents
$ kgents garden --export garden.md    # Export to markdown

# Evolution with visualization
$ kgents evolve --garden               # Evolve with live garden
$ kgents evolve --garden --record      # Record garden evolution

# Attach to running process
$ kgents garden attach --pid 12345     # Attach to process
$ kgents garden attach --name robin    # Attach to named agent

# History and playback
$ kgents garden history                # Show session history
$ kgents garden replay session.json   # Replay saved session
$ kgents garden diff session1.json session2.json  # Compare sessions

# Export formats
$ kgents garden export --format md     # Markdown
$ kgents garden export --format json   # JSON state dump
$ kgents garden export --format mermaid  # Mermaid diagram
$ kgents garden export --format ascii  # Raw ASCII (for docs)
```

---

### Keyboard Shortcuts (TUI Mode)

When running `kgents garden` in terminal:

```
Navigation:
  h/j/k/l     Vim-style movement
  ←/↓/↑/→     Arrow keys
  g/G         Jump to top/bottom
  /           Search agents
  n/N         Next/previous search result

Scale Operations:
  +/-         Zoom in/out (card ↔ page ↔ garden)
  0           Reset to garden view
  1-5         Jump to scale (1=glyph, 5=library)

Agent Actions:
  o           Observe (spawn W-gent)
  i           Invoke (run agent)
  c           Compose (with another agent)
  r           Rest (pause agent)
  d           Details (full page view)

Filters:
  fA-Z        Filter by genus (fB = B-gents only)
  fp          Filter by phase (active, dormant, etc.)
  fe          Filter by ethics score
  fj          Filter by joy score
  fc          Clear all filters

Session:
  s           Save session
  l           Load session
  e           Export to markdown
  q           Quit (save prompt)
  Q           Quit without saving
  ?           Show help
```

---

### Persistent Sessions

Garden states are first-class entities that can be saved, loaded, and diffed.

#### Session Format (.garden.json)

```json
{
  "name": "robin-development-2025-12-08",
  "session_start": "2025-12-08T18:00:00Z",
  "session_end": "2025-12-08T21:30:00Z",
  "duration_seconds": 12600,
  "agents": {
    "Ground": {
      "phase": "active",
      "birth_time": "2025-12-08T18:00:00Z",
      "joy": 1.0,
      "ethics": 1.0,
      "margin_notes": [
        {
          "timestamp": "2025-12-08T18:00:01Z",
          "source": "system",
          "content": "Session initialized"
        }
      ]
    },
    "B-robin": {
      "phase": "active",
      "birth_time": "2025-12-08T18:05:00Z",
      "joy": 0.9,
      "ethics": 0.85,
      "composes_with": ["PersonaAgent", "HypothesisAgent", "HegelAgent"],
      "margin_notes": [...]
    }
  },
  "global_notes": [
    {
      "timestamp": "2025-12-08T18:30:00Z",
      "source": "human",
      "content": "Switched focus to robin narrative synthesis"
    }
  ],
  "metadata": {
    "commit": "4b02086",
    "branch": "main",
    "python_version": "3.13.0",
    "platform": "darwin"
  }
}
```

#### Session Diff

```bash
$ kgents garden diff session-morning.json session-evening.json

Agents changed: 3
  ● B-robin:      joy 0.7 → 0.9, ethics 0.8 → 0.85
  ● E-evolve:     phase dormant → active
  ● F-forge:      phase waking → waning

New agents: 2
  + L-library (active, joy=0.8)
  + T-validator (active, joy=0.75)

Removed agents: 1
  - K-kent (waning → retired)

Notable events:
  [18:30] Human note: "Switched focus to robin"
  [19:45] B-robin: Phase transition active → waning
  [20:15] F-forge: Artifact crystallized (weather.alo.md)
```

---

### Hook System

Gardens can define custom hooks for emergent behaviors.

#### .garden-hooks.py

```python
"""
Garden hooks for robin-development garden.

Hooks are Python functions that run on garden events.
"""

from agents.i import AgentState, GardenState, MarginNote, NoteSource

async def on_agent_error(agent: AgentState, error: Exception):
    """Called when any agent enters error phase (◌)."""
    # Auto-spawn W-gent for debugging
    from agents.w import serve_agent
    await serve_agent(agent.agent_id, port=8000)

    # Add margin note
    agent.add_note(
        f"ERROR: {error} → W-gent spawned at localhost:8000",
        NoteSource.SYSTEM
    )

async def on_synthesis(result):
    """Called when Sublate produces synthesis."""
    # Log synthesis to L-gent catalog
    from agents.l import Registry
    registry = Registry()
    await registry.register(
        name=f"synthesis-{result.timestamp}",
        entity_type="PATTERN",
        description=result.explanation,
        tags=["synthesis", "hegel"],
    )

async def on_evolution_complete(module: str, incorporated: int):
    """Called when E-gent completes evolution."""
    if incorporated > 0:
        # Celebration breath cycle (slow exhale)
        from agents.i import BreathManager
        breath = BreathManager()
        await breath.celebrate()  # Extra-long exhale
```

**Usage**:
```bash
$ kgents garden --hooks .garden-hooks.py
# Hooks auto-execute on events
```

---

### Real-World Workflow Example

**Scenario**: Evolving the robin agent while monitoring principles.

```bash
# Terminal 1: Start evolution with garden
$ kgents evolve agents/b/robin.py --garden --record

# Garden view auto-opens, showing:
┌─ Evolution: robin-agent ──────────── t: 00:00:15 ─┐
│                                                    │
│ bootstrap pipeline:                                │
│   ● Ground       ✓ Persona loaded                  │
│   ● Contradict   ● Detecting tensions...           │
│   ○ Sublate      ⏸ Waiting                         │
│   ○ Judge        ⏸ Waiting                         │
│                                                    │
│ target agent: B-robin                              │
│   current: ● active (joy=0.9, eth=0.85)            │
│   proposed: 3 hypotheses pending                   │
│                                                    │
│ [Press 'o' on any agent to observe details]        │
└────────────────────────────────────────────────────┘

# User presses 'o' on Judge agent
# W-gent browser opens at localhost:8001

# Browser shows Judge agent internals:
#   - Real-time principle evaluation
#   - Scorecard as it's calculated
#   - Reasoning for each score
#   - Suggestions for improvement

# Back in garden, user presses 's' to save
# Session saved to: .garden-sessions/robin-evolution-2025-12-08.json

# Later, resume:
$ kgents garden load .garden-sessions/robin-evolution-2025-12-08.json
# Garden restores exact state, including:
#   - All agent phases
#   - Margin notes
#   - Composition relationships
#   - Timeline position
```

---

### Integration Checklist

A production-ready I-gent implementation must:

- [ ] **Bootstrap Awareness**: Special rendering for Ground/Contradict/Sublate/Judge/Fix
- [ ] **evolve.py Hook**: `--garden` flag for live evolution visualization
- [ ] **Persistent Sessions**: Save/load/diff garden states (.garden.json)
- [ ] **CLI Commands**: `kgents garden`, `kgents garden attach`, etc.
- [ ] **Keyboard Navigation**: Full TUI with vim bindings
- [ ] **Export Formats**: Markdown, JSON, Mermaid, ASCII
- [ ] **Hook System**: Custom Python hooks for garden events
- [ ] **W-gent Spawning**: [observe] action spawns W-gent server
- [ ] **D-gent Integration**: Load history, timeline scrubber
- [ ] **L-gent Navigation**: Search catalog from garden view
- [ ] **Cross-Genus Workflows**: Special UI for E/F/H/J/D/L-gent patterns
- [ ] **Graceful Degradation**: Works in pure ASCII, no color, 80x24
- [ ] **Performance**: <100ms render time for gardens with 50+ agents
- [ ] **Documentation**: Man pages for all CLI commands

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
- [../w-gents/](../w-gents/) - Wire agents (process observation backend for `[observe]` action)
- [../w-gents/i-gent-synergy.md](../w-gents/i-gent-synergy.md) - I-gent/W-gent integration details
- [../d-gents/](../d-gents/) - State persistence (I-gent's memory backend)
- [../l-gents/](../l-gents/) - Library catalog (I-gent's library view source)
- [../c-gents/](../c-gents/) - Composition foundations (I-gent visualizes morphisms)
- [../principles.md](../principles.md) - Core design principles
- [../anatomy.md](../anatomy.md) - Agent lifecycle (mapped to moon phases)
