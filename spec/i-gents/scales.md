# I-gent Scales: Fractal Visualization

I-gents satisfy a critical constraint: **the same grammar visualizes atoms and galaxies**. This document specifies how the visual language scales from a single agent state to an orchestration of multiple repositories.

---

## Philosophy

> "A leaf is a tree is a forest. The pattern persists across scale."

The fractal property means:
1. Elements at lower scales compose to form higher scales
2. Navigation between scales is smooth (zoom in/out)
3. Mental models transfer: understanding a glyph helps understand a library
4. Implementation is recursive: the same rendering logic works at all scales

---

## The Five Scales

### Overview

| Scale | Unit | Contains | Typical View Size |
|-------|------|----------|-------------------|
| **1. Glyph** | Atom | Phase + Identity | 3 characters |
| **2. Card** | Molecule | Glyph + Metrics | 20×5 characters |
| **3. Page** | Cell | Card + Sections + Margins | 60×30 characters |
| **4. Garden** | Organism | Multiple Cards/Glyphs + Topology | 80×40 characters |
| **5. Library** | Ecosystem | Multiple Gardens + Orchestration | Full terminal |

---

## Scale 1: Glyph

**Definition**: The smallest meaningful visualization unit.

### Structure

```
{phase}{space}{identity}
```

### Properties

- **Width**: 2-18 characters (phase + space + identity)
- **Height**: 1 line
- **Contains**: Phase (1 char), Identity (1-16 chars)
- **Information**: State + What

### Examples

```
● A
○ robin
◐ summarizer_v2
◌ test-failed
```

### Use Cases

- Inline status indicators
- Dense listings
- Aggregated views in gardens

---

## Scale 2: Card

**Definition**: A glyph with surrounding context.

### Structure

```
┌─ {name} ─────────┐
│ {phase} {label}  │
│ {metrics...}     │
└──────────────────┘
```

### Properties

- **Width**: 18-30 characters
- **Height**: 3-8 lines
- **Contains**: Name, Phase, Key metrics
- **Information**: State + What + How (brief)

### Variants

**Minimal**:
```
┌─ A ──────┐
│ ● active │
└──────────┘
```

**Standard**:
```
┌─ A-gent ─────────┐
│ ● active         │
│ t: 00:14:32      │
│ joy: ███░░       │
└──────────────────┘
```

**Extended**:
```
┌─ A-gent ─────────────────┐
│ ● active                 │
│ t: 00:14:32              │
│ joy: ███████░░░  7/10    │
│ eth: █████████░  9/10    │
│ ─────────────────────────│
│ composing: C, K          │
└──────────────────────────┘
```

### Use Cases

- Agent selection menus
- Comparison views
- Garden components (when space permits)

---

## Scale 3: Page

**Definition**: Full view of a single agent.

### Structure

```
╔══ {name} ═══════════════════════════════════════╗
║                                                 ║
║  "{epigraph}"                                   ║
║                                                 ║
║  state: {phase} {label}         t: {time}       ║
║  ─────────────────────────────────────────────  ║
║  {metrics}                                      ║
║                                                 ║
║  ┌─ {section} ─────────────────────────────┐    ║
║  │ {content}                               │    ║
║  └─────────────────────────────────────────┘    ║
║                                                 ║
║  ┌─ margin notes ──────────────────────────┐    ║
║  │ {notes}                                 │    ║
║  └─────────────────────────────────────────┘    ║
║                                                 ║
║  [{action}]  [{action}]  [{action}]             ║
╚═════════════════════════════════════════════════╝
```

### Properties

- **Width**: 50-80 characters
- **Height**: 20-40 lines
- **Contains**: All agent details
- **Information**: State + What + How + Why + History

### Sections

Standard sections (all optional):

| Section | Content |
|---------|---------|
| composition graph | Agent relationship visualization |
| inputs | Input schema and recent inputs |
| outputs | Output schema and recent outputs |
| configuration | Current config values |
| history | Invocation log |
| margin notes | Timestamped observations |

### Use Cases

- Detailed inspection
- Debugging
- Agent configuration
- Documentation reading

---

## Scale 4: Garden

**Definition**: Multiple agents in spatial relationship.

### Structure

```
┌─ {garden_name} ─────────────────── t: {time} ─┐
│                                               │
│  {spatial layout of agents with connections}  │
│                                               │
│  ══════════════════════════════════════════   │
│  breath: {indicator}                          │
│                                               │
│  focus: [{agent}]  │  > {prompt}              │
└───────────────────────────────────────────────┘
```

### Properties

- **Width**: 60-120 characters
- **Height**: 30-50 lines
- **Contains**: Multiple agents, composition edges
- **Information**: Relationships + Flow + Health

### Layout Modes

**Graph Mode** (default):
```
     ● A ─────────┐
                  │
     ○ B ─────────┼──── ◐ C
                  │
     ◐ D ─────────┘
```

**Grid Mode** (for many agents):
```
  ●A  ○B  ◐C
  ●D  ◌E  ●F
  ○G  ●H  ◐I
```

**List Mode** (for linear pipelines):
```
  ● A ──▶ ◐ B ──▶ ○ C ──▶ ● D
```

### Agent Representation in Gardens

Gardens can show agents as:
- **Glyphs**: Dense, many agents visible (default for >10 agents)
- **Cards**: More detail, fewer agents visible (default for 3-10 agents)
- **Mixed**: Focus agent as card, others as glyphs

### Use Cases

- Session overview
- Composition planning
- Health monitoring
- Navigation hub

---

## Scale 5: Library

**Definition**: Multiple gardens in orchestration view.

### Structure

```
┌─ {library_name} ─────────────────── t: {time} ─┐
│                                                │
│  ┌─ {garden} ─────────┐  ┌─ {garden} ─────┐    │
│  │  {summary}         │  │  {summary}     │    │
│  │  health: {bar}     │  │  health: {bar} │    │
│  └────────────────────┘  └────────────────┘    │
│           │                      │             │
│           └──────────┬───────────┘             │
│                      ▼                         │
│           ┌─ {garden} ─────────────┐           │
│           │  {summary}             │           │
│           │  health: {bar}         │           │
│           └────────────────────────┘           │
│                                                │
│  total: {n} gardens  │  status: {status}       │
│  > {prompt}                                    │
└────────────────────────────────────────────────┘
```

### Properties

- **Width**: 80-160 characters (full terminal)
- **Height**: 40-60 lines
- **Contains**: Multiple gardens, cross-garden relationships
- **Information**: Ecosystem health + Orchestration + Lineage

### Garden Summaries

Within library view, gardens compress to:
```
┌─ garden:main ───────────┐
│  ●A  ○B  ◐C  ●K         │  ← Glyph row
│  health: ████░  80%     │  ← Aggregate metric
└─────────────────────────┘
```

### Orchestration Status

| Status | Meaning |
|--------|---------|
| converging | Gardens approaching common state |
| diverging | Gardens evolving differently |
| synchronized | Gardens in identical state |
| conflicting | Incompatible states detected |
| isolated | No relationships between gardens |

### Use Cases

- Multi-repo management
- Deployment orchestration
- Environment comparison (dev/staging/prod)
- Lineage tracking

---

## Scale Transitions

### Zoom Operations

| Action | Key | Effect |
|--------|-----|--------|
| Zoom In | `z` | Glyph → Card → Page |
| Zoom Out | `Z` | Page → Garden → Library |
| Focus | `Enter` | Expand selected element |
| Back | `Esc` | Return to previous scale |

### Transition Animations

When zooming:
1. **In**: Current element expands to fill view
2. **Out**: Current view shrinks to element in larger context
3. **Duration**: 150ms (fast but perceptible)

### Context Preservation

When zooming out:
- The previously-focused element remains highlighted
- Cursor position preserved
- Scroll position calculated to keep focus visible

When zooming in:
- The selected element becomes the new view
- Parent context shown in header/breadcrumb

---

## Fractal Consistency Rules

### Rule 1: Symbol Preservation

A phase symbol in a glyph is identical to the same symbol in a library view.

```
Glyph:   ● A
Card:    │ ● active │
Page:    ║  state: ● active
Garden:  ●A
Library: ●A
```

### Rule 2: Composition Nesting

Higher scales contain lower scales:

```
Library
└── Garden
    └── Page
        └── Card
            └── Glyph
```

### Rule 3: Information Monotonicity

Zooming in reveals more information; zooming out aggregates.

```
Library: health: 80%
  → Garden: ●3 ○2 ◐1
    → Card: ● active, t: 00:14:32, joy: 7/10
      → Page: (full detail)
```

### Rule 4: Edge Consistency

Composition edges visible at one scale are visible (possibly aggregated) at all higher scales.

```
Page:    A ──▶ C
Garden:  ●A ──▶ ◐C
Library: (garden-to-garden edges shown)
```

### Rule 5: Time Coherence

Time (`t:`) appears at every scale, with appropriate epoch.

---

## Scale Selection Heuristics

**Auto-select** based on context:

| Context | Default Scale |
|---------|---------------|
| Single agent inspection | Page |
| Comparing 2-5 agents | Card grid |
| Session overview | Garden |
| Multi-repo work | Library |
| Quick status check | Glyph list |

**Force** via command or navigation:

```
> zoom page A-gent
> zoom garden
> zoom library
```

---

## Responsive Scaling

Adjust detail based on terminal size:

### Small Terminal (80×24)

- Library shows 2-4 gardens (summarized)
- Garden shows glyphs only
- Page omits some sections

### Medium Terminal (120×40)

- Library shows 4-8 gardens
- Garden shows mix of cards and glyphs
- Page shows full sections

### Large Terminal (160×60)

- Library shows detailed garden views
- Garden shows all agents as cards
- Page shows extended detail

---

## Scale and Memory

Each scale has different memory requirements:

| Scale | State Needed | D-gent Impact |
|-------|--------------|---------------|
| Glyph | Phase only | Minimal |
| Card | Phase + recent metrics | Low |
| Page | Full agent state | Medium |
| Garden | All agents in garden | High |
| Library | All gardens (summary) | Very High |

**Lazy Loading**: Higher scales load detail on demand:
- Library loads garden summaries first
- Garden detail loads when zooming in
- Page sections load progressively

---

## Cross-Scale Relationships

### L-gent Integration

L-gent (Library agent) provides the data for library scale:
- Catalog of all agents/gardens
- Search across scales
- Lineage for garden relationships

### D-gent Integration

D-gent state enables scale features:
- Page: Full state for detail view
- Garden: Aggregate metrics
- Timeline: Historical state at all scales

### C-gent Integration

C-gent composition is visualized across scales:
- Page: Detailed composition graph
- Garden: Edge topology
- Library: Cross-garden dependencies

---

## Scale Examples

### Research Workflow (Zooming Sequence)

**1. Library View**: See all research branches
```
┌─ research library ─────────────────────────────┐
│  ┌─ hypothesis:A ─┐  ┌─ hypothesis:B ─┐        │
│  │  ●robin  ◐test │  │  ●robin  ●test │        │
│  │  health: ██░░  │  │  health: ████  │        │
│  └────────────────┘  └────────────────┘        │
└────────────────────────────────────────────────┘
```

**2. Garden View**: Focus on hypothesis:B
```
┌─ hypothesis:B ─────────────────────────────────┐
│      ● robin ───▶ ● test ───▶ ○ archive        │
│  breath: ░░░░████░░░░                          │
└────────────────────────────────────────────────┘
```

**3. Page View**: Inspect robin
```
╔══ robin ═══════════════════════════════════════╗
║  "The B-gent that turns curiosity to science." ║
║  state: ● active             t: 01:23:45       ║
║  ┌─ composition ─────────────────────────────┐ ║
║  │  → test (validated: 12 hypotheses)        │ ║
║  └───────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════╝
```

**4. Card View**: Quick comparison (zoom out partially)
```
┌─ robin ─────────┐  ┌─ test ──────────┐
│ ● active        │  │ ● active        │
│ hyp: 12 tested  │  │ pass: 10 (83%)  │
└─────────────────┘  └─────────────────┘
```

---

## See Also

- [README.md](README.md) - I-gent philosophy
- [grammar.md](grammar.md) - Visual grammar at each scale
- [time.md](time.md) - Time epochs per scale
- [export.md](export.md) - Serialization at each scale
- [../agents/composition.md](../agents/composition.md) - Composition edges
- [../l-gents/README.md](../l-gents/README.md) - Library data source
