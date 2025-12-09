# I-gent Grammar: The Visual Language

The I-gent grammar is a **compositional visual language** where simple elements combine to express complex states. Like a written language, it has atoms (glyphs), molecules (cards), sentences (pages), paragraphs (gardens), and documents (libraries).

---

## Design Principles

### 1. Compositional Consistency

The same visual elements appear at every scale. A glyph in isolation uses the same symbols as a glyph within a library view.

### 2. Information Density

Maximum meaning per character. The grammar prioritizes **density over decoration**.

### 3. Keyboard Navigability

Every element is addressable via keyboard. Mouse is optional; terminal is primary.

### 4. Monochrome Legibility

The grammar must be fully legible in monochrome. Color enhances but is not required.

---

## Level 1: The Glyph

The irreducible atom of I-gent visualization.

### Structure

```
{phase} {identity}
```

### Examples

```
● A        # Active A-gent
○ B        # Dormant B-gent
◐ K        # Waking K-gent
◑ robin    # Waning robin (B-gent)
◌ test-1   # Empty/errored test agent
```

### Phase Symbols

| Symbol | Unicode | Name | Meaning |
|--------|---------|------|---------|
| ○ | U+25CB | White Circle | Dormant |
| ◐ | U+25D0 | Circle Left Half Black | Waking |
| ● | U+25CF | Black Circle | Active |
| ◑ | U+25D1 | Circle Right Half Black | Waning |
| ◌ | U+25CC | Dotted Circle | Empty/Error |

### Identity Rules

- **Single character**: For standard genera (A, B, C, D, E, F, H, I, J, K, L, T)
- **Short name**: For specific instances (robin, test-1, summarizer_v2)
- **Maximum length**: 16 characters (truncate with ellipsis: `summariz…`)

### Glyph Composition

Multiple glyphs can appear together to show state-at-a-glance:

```
●A ○B ◐C ●K    # Four agents: A active, B dormant, C waking, K active
```

---

## Level 2: The Card

A glyph with surrounding context. The "molecule" of visualization.

### Structure

```
┌─ {name} ─────┐
│ {phase} {state_label} │
│ {metrics...}         │
└──────────────────────┘
```

### Minimal Card

```
┌─ A-gent ─────┐
│ ● active     │
└──────────────┘
```

### Standard Card

```
┌─ A-gent ─────────┐
│ ● active         │
│ t: 00:14:32      │
│ joy: ███░░       │
│ eth: ████░       │
└──────────────────┘
```

### Extended Card

```
┌─ A-gent ─────────────────┐
│ ● active                 │
│ t: 00:14:32              │
│ joy: ███████░░░  7/10    │
│ eth: █████████░  9/10    │
│ ─────────────────────────│
│ composing with: C, K     │
│ last: invoke at 00:14:00 │
└──────────────────────────┘
```

### Card Metrics

**Progress bars** use block characters:

| Char | Unicode | Meaning |
|------|---------|---------|
| █ | U+2588 | Full block (filled) |
| ░ | U+2591 | Light shade (empty) |

**Standard metrics**:
- `t:` — Time since epoch
- `joy:` — Joy-inducing principle alignment (1-10 scale)
- `eth:` — Ethical principle alignment (1-10 scale)

### Card Borders

Box-drawing characters define card boundaries:

| Char | Unicode | Position |
|------|---------|----------|
| ┌ | U+250C | Top-left |
| ┐ | U+2510 | Top-right |
| └ | U+2514 | Bottom-left |
| ┘ | U+2518 | Bottom-right |
| │ | U+2502 | Vertical |
| ─ | U+2500 | Horizontal |

---

## Level 3: The Page

A full-view rendering of a single agent. The "sentence" of visualization.

### Structure

```
╔══ {name} ════════════════════════════════════════════════╗
║                                                          ║
║  "{epigraph}"                                            ║
║                                                          ║
║  state: {phase} {label}              t: {time}           ║
║  ────────────────────────────────────────────────────    ║
║  {metrics}                                               ║
║                                                          ║
║  ┌─ {section} ────────────────────────────────────────┐  ║
║  │ {section content}                                  │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  ┌─ margin notes ─────────────────────────────────────┐  ║
║  │ {timestamped notes}                                │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
║  [{action1}]  [{action2}]  [{action3}]  [{action4}]      ║
╚══════════════════════════════════════════════════════════╝
```

### Page Sections

Standard sections (all optional):

| Section | Content |
|---------|---------|
| composition graph | Visual graph of agent relationships |
| inputs | Last/expected input schema |
| outputs | Last/expected output schema |
| config | Current configuration |
| history | Recent invocation log |
| margin notes | Timestamped observations |

### Page Borders

Double-line box drawing for pages (distinguishes from cards):

| Char | Unicode | Position |
|------|---------|----------|
| ╔ | U+2554 | Top-left |
| ╗ | U+2557 | Top-right |
| ╚ | U+255A | Bottom-left |
| ╝ | U+255D | Bottom-right |
| ║ | U+2551 | Vertical |
| ═ | U+2550 | Horizontal |

### Page Actions

Actions appear as bracketed verbs:

```
[observe]  [invoke]  [compose]  [rest]
```

Standard actions:
- `[observe]` — Read-only inspection
- `[invoke]` — Execute with input
- `[compose]` — Connect to another agent
- `[rest]` — Transition to dormant
- `[evolve]` — Trigger E-gent improvement
- `[timeline]` — Switch to timeline view

---

## Level 4: The Garden

Multiple agents in spatial relationship. The "paragraph" of visualization.

### Structure

```
┌─ {garden_name} ────────────────────────── t: {time} ─┐
│                                                      │
│  {spatial layout of glyphs with connecting lines}    │
│                                                      │
│  ════════════════════════════════════════════════    │
│  breath: {breath_indicator}                          │
│                                                      │
│  focus: [{agent}]  │  > {command_prompt}             │
└──────────────────────────────────────────────────────┘
```

### Spatial Layout Rules

Agents are positioned based on **composition relationships**, not list order.

**Positioning heuristics**:
1. Agents that compose often cluster together
2. Independent agents maintain spacing
3. The current focus agent is visually centered
4. Dormant agents drift to periphery

### Connection Lines

Lines show composition relationships:

| Pattern | Meaning |
|---------|---------|
| `───` | Sequential composition (A >> B) |
| `─┬─` | Branching point |
| `─┼─` | Crossing (no connection) |
| `─▶` | Direction of data flow |
| `···` | Pending/uncommitted composition |
| `─ ─` | Weak/optional composition |

### Example Garden

```
┌─ research garden ────────────────────────── t: 01:23:45 ─┐
│                                                          │
│       ● robin ─────────┐                                 │
│          │             │                                 │
│          ▼             ▼                                 │
│       ◐ analyze     ● summarize                          │
│          │             │                                 │
│          └─────┬───────┘                                 │
│                ▼                                         │
│             ● report                                     │
│                │                                         │
│                ▼                                         │
│             ○ archive                                    │
│                                                          │
│  ════════════════════════════════════════════════════    │
│  breath: ░░░░░███░░░░  (inhale)                          │
│                                                          │
│  focus: [robin]  │  > open page robin                    │
└──────────────────────────────────────────────────────────┘
```

### The Breath Indicator

A slow-cycling animation representing system liveliness:

```
breath: ████░░░░░░░░  (inhale)
breath: ░░░░████░░░░  (hold)
breath: ░░░░░░░░████  (exhale)
breath: ░░░░████░░░░  (hold)
```

Cycle: 4 seconds (1s inhale, 1s hold, 1s exhale, 1s hold)

---

## Level 5: The Library

Multiple gardens in orchestration view. The "document" of visualization.

### Structure

```
┌─ {library_name} ─────────────────────────── t: {time} ─┐
│                                                        │
│  ┌─ {garden1} ────────┐  ┌─ {garden2} ────────┐        │
│  │  {glyph summary}   │  │  {glyph summary}   │        │
│  │  health: {bar}     │  │  health: {bar}     │        │
│  └────────────────────┘  └────────────────────┘        │
│           │                       │                    │
│           └───────────┬───────────┘                    │
│                       ▼                                │
│           ┌─ {garden3} ────────────┐                   │
│           │  {glyph summary}       │                   │
│           │  health: {bar}         │                   │
│           └────────────────────────┘                   │
│                                                        │
│  total: {n} gardens  │  orchestration: {status}        │
│  > {command_prompt}                                    │
└────────────────────────────────────────────────────────┘
```

### Garden Summaries

Within library view, gardens are compressed to:
- Glyph row: All agents as phase+identity pairs
- Health bar: Aggregate status metric

```
┌─ garden:main ───────────┐
│  ●A  ○B  ◐C  ●K         │
│  health: ████░  80%     │
└─────────────────────────┘
```

### Orchestration Status

The library tracks cross-garden relationships:

| Status | Meaning |
|--------|---------|
| converging | Gardens approaching common state |
| diverging | Gardens evolving differently |
| synchronized | Gardens in identical state |
| conflicting | Gardens have incompatible states |
| isolated | Gardens have no relationships |

### Garden Connections

Lines between garden boxes show:
- Data flow (one garden's output feeds another)
- Fork/merge relationships (experiment branch)
- Dependency (production depends on staging)

---

## Composite Structures

### The Composition Graph

Used within pages and gardens to show agent relationships:

```
┌─ composition graph ────────────────────────────────────┐
│                                                        │
│      ● A ──────────┐                                   │
│         \          │                                   │
│          \         ▼                                   │
│           ◐ C ←── merge                                │
│          /                                             │
│         /                                              │
│      ○ B                                               │
│                                                        │
│  legend: ─── = compose, ▶ = direction, ← = forming     │
└────────────────────────────────────────────────────────┘
```

### The Timeline

Used within pages and gardens to show temporal evolution:

```
┌─ timeline ─────────────────────────────────────────────┐
│                                                        │
│  t=0       t=5       t=10      t=15      t=20   now    │
│  ├─────────┼─────────┼─────────┼─────────┼──────┤      │
│  ○         ◐         ●         ●         ●      ●      │
│  birth     wake      active    compose   ·      ·      │
│                                with C                  │
│                                                        │
│  [◀ rewind]  [▶ play]  [⏸ pause]  [▶▶ step]            │
└────────────────────────────────────────────────────────┘
```

### The Margin Notes Panel

Timestamped observations panel:

```
┌─ margin notes ─────────────────────────────────────────┐
│ 00:12:00 — [system] phase: dormant → waking            │
│ 00:12:05 — [ai] third attempt to compose with B        │
│ 00:13:30 — [kent] holding tension—not forcing          │
│ 00:14:00 — [ai] stable; composition graph coherent     │
│ ────────────────────────────────────────────────────── │
│ > add note: __________________________________________ │
└────────────────────────────────────────────────────────┘
```

Note prefixes:
- `[system]` — Automatic observations
- `[ai]` — LLM-generated reflections
- `[{username}]` — Human annotations

---

## Typography and Spacing

### Alignment

- Left-align all text by default
- Right-align time values
- Center agent names in card/page headers

### Spacing

- 1 space after phase symbol
- 2 spaces between glyph pairs
- 1 blank line between sections

### Truncation

When content exceeds available width:
- Names: Truncate with ellipsis (`summarizer_v…`)
- Notes: Wrap to next line with indent
- Graphs: Scroll horizontally (keyboard nav)

---

## Color (Optional Enhancement)

When color is available, enhance (but don't depend on) the grammar:

| Element | Suggested Color | Fallback |
|---------|-----------------|----------|
| Active phase (●) | Green | Bold |
| Dormant phase (○) | Gray | Normal weight |
| Error phase (◌) | Red | Inverted |
| Focus highlight | Yellow background | Underline |
| Connection lines | Dim | Normal |
| Breath cycle | Pulsing intensity | Static |

---

## Keyboard Navigation

All elements are keyboard-addressable:

| Key | Action |
|-----|--------|
| `h/j/k/l` | Vim-style navigation |
| `Enter` | Select/open focused element |
| `Esc` | Back/up one level |
| `Tab` | Cycle through actions |
| `z` | Zoom (cycle glyph → card → page) |
| `Z` | Zoom out (cycle page → garden → library) |
| `t` | Toggle timeline view |
| `m` | Focus margin notes |
| `/` | Search |
| `?` | Help |

---

## Grammar Composition Rules

### Rule 1: Nesting

Higher scales contain lower scales:
- Library contains Gardens
- Garden contains Cards (or Glyphs in compact mode)
- Page contains Sections
- Card contains Glyph + Metrics
- Glyph is atomic

### Rule 2: Consistency

A glyph in a library view uses the same phase symbol as when viewed in isolation.

### Rule 3: Context Collapse

When zooming out, detail collapses gracefully:
- Page → Card: Sections disappear, metrics compress
- Card → Glyph: Metrics disappear, only phase+identity remain
- Garden → Library summary: Individual agents become glyph row

### Rule 4: Time Preservation

Time (`t:`) appears at every scale but references different epochs.

---

## Examples

### Research Session

```
┌─ research library ────────────────────────── t: 02:15:00 ─┐
│                                                           │
│  ┌─ hypothesis:alpha ───────┐                             │
│  │  ●robin  ◐analyze  ○test │                             │
│  │  health: ███░░  60%      │                             │
│  └──────────────────────────┘                             │
│              │                                            │
│              ▼                                            │
│  ┌─ experiment:beta ────────┐                             │
│  │  ●A  ●B  ●C  ○validate   │                             │
│  │  health: ████░  80%      │                             │
│  └──────────────────────────┘                             │
│                                                           │
│  total: 2 gardens  │  orchestration: converging           │
│  > enter hypothesis:alpha                                 │
└───────────────────────────────────────────────────────────┘
```

### Debugging a Pipeline

```
╔══ FailingAgent ═══════════════════════════════════════════╗
║                                                           ║
║  "A T-gent that fails deterministically for testing."     ║
║                                                           ║
║  state: ◌ error                       t: 00:05:12         ║
║  ─────────────────────────────────────────────────────    ║
║  fail_count: 3/3 (exhausted)                              ║
║  error_type: NetworkTimeout                               ║
║                                                           ║
║  ┌─ margin notes ──────────────────────────────────────┐  ║
║  │ 00:05:00 — [system] invocation #1 failed            │  ║
║  │ 00:05:05 — [system] invocation #2 failed            │  ║
║  │ 00:05:12 — [system] invocation #3 failed (final)    │  ║
║  │ 00:05:12 — [ai] exhausted retries; escalating       │  ║
║  └─────────────────────────────────────────────────────┘  ║
║                                                           ║
║  [observe]  [reset]  [reconfigure]  [retire]              ║
╚═══════════════════════════════════════════════════════════╝
```

---

## See Also

- [README.md](README.md) - I-gent philosophy and overview
- [states.md](states.md) - Moon phase state definitions
- [scales.md](scales.md) - Fractal scaling rules
- [export.md](export.md) - Markdown serialization
- [../c-gents/composition.md](../c-gents/composition.md) - Composition as morphisms
