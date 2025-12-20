# CLI v6: The Virtualized Document Tree

**Status:** Vision Spec
**Date:** 2025-12-19
**Supersedes:** CLI v5 (retains vision, refines implementation)
**Principle:** *"Navigating to paths, learning about them, reading and writing files—these are the primitives. Everything else is projection."*

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"There is no 'developer mode.' Browsing IS editing IS programming."* — HyperCard Legacy
>
> *"We don't need FUSE. We need the shell to understand what the path means."*
>
> *"The lattice is the truth. Everything else is a projection of the lattice."*
>
> *"The garden's grammar generates the flowers."*

---

## Part I: The Refinement

CLI v5 proposed a radical vision: **the filesystem IS the interface**. Mount `~/.kg` via FUSE, and every Unix tool becomes a kgents tool.

CLI v6 **preserves the vision** but **refines the implementation**. We don't need kernel extensions. We need a **syntax-level interpreter** that understands filesystem semantics and translates them to AGENTESE invocations.

### The Key Insight

```bash
# User types this:
$ cat ~/.kg/self/soul/.manifest

# The kg-shell intercepts BEFORE execution
# It recognizes the pattern and translates:
#   → logos.invoke("self.soul", aspect="manifest")

# User types this:
$ echo "hello" > ~/.kg/self/memory/.capture

# The kg-shell intercepts and translates:
#   → logos.invoke("self.memory", aspect="capture", content="hello")
```

**We're not puppeting the filesystem. We're simulating filesystem semantics at the syntax layer.**

The path `~/.kg/self/soul` never needs to exist on disk. The shell understands what it *means* and acts accordingly. This is like how a virtual machine doesn't need real hardware—it intercepts instructions and simulates responses.

---

## Part II: The Lattice Model

Think of the document tree not as files but as a **lattice of nodes**—a field of potentials. The filesystem syntax is just one projection of this underlying structure.

```
                    ┌─────────────────────────────────────────────┐
                    │           THE LATTICE (Ground Truth)         │
                    │                                             │
                    │    ◉ ─── ● ─── ○                            │
                    │    │     │     │                            │
                    │    ● ─── ◉ ─── ●                            │
                    │    (AGENTESE @node registry)                │
                    │                                             │
                    └─────────────────────────────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   FILESYSTEM    │    │      TUI        │    │      REPL       │
    │   PROJECTION    │    │   PROJECTION    │    │   PROJECTION    │
    │                 │    │                 │    │                 │
    │ ~/.kg/self/...  │    │  ◉ self         │    │ [self] » ...    │
    │ cat, ls, echo   │    │  ├── memory     │    │                 │
    └─────────────────┘    │  └── soul       │    └─────────────────┘
                           └─────────────────┘
```

### 2.1 The Lattice IS the Registry

The lattice is **literally the `@node` registry**. Every path in AGENTESE corresponds to a node in the lattice. The registry is the ground truth.

```python
# The lattice is populated at import time
from protocols.agentese.gateway import logos

# This IS the lattice
lattice = logos.registry
```

### 2.2 Projections Maintain Coherence

Each projection (filesystem, TUI, REPL, web) renders the same lattice differently but maintains **sheaf coherence**:

| Projection | How It Renders | Coherence Mechanism |
|------------|----------------|---------------------|
| Filesystem | Paths as directories, aspects as special files | Invocation via read/write |
| TUI | Interactive hypermedia browser | Navigation invokes manifest |
| REPL | Direct AGENTESE syntax | Tab completion from registry |
| Web | React components | Hooks query same registry |

### 2.3 Subscription Propagation

When one projection makes a change, others update via the **SynergyBus**:

```
Filesystem write → logos.invoke() → SynergyBus event
                                          ↓
    TUI manifest update ← subscription listener
    REPL context update ← subscription listener
    Web hook refetch ← subscription listener
```

---

## Part III: Experience Layers

### The Parallel Experience Model

The filesystem projection doesn't *replace* the classic CLI and REPL. It's another layer that coexists. Each layer serves different use cases:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   EXPERIENCE LAYERS (All Valid, All Maintained)                             │
│   ═══════════════════════════════════════════════                          │
│                                                                             │
│   Layer 3: ORGANIC GARDEN                                                   │
│            kg garden                                                        │
│            Spatial, visual, living topology                                 │
│            For: Exploration, cultivation, big-picture thinking             │
│                                                                             │
│   Layer 2: HYPERMEDIA TUI                                                   │
│            kg tui                                                           │
│            Navigable, affordance-visible, live updates                      │
│            For: Interactive exploration, learning the system               │
│                                                                             │
│   Layer 1: CLASSIC REPL                                                     │
│            kg repl                                                          │
│            Direct AGENTESE invocation: self.memory.capture "text"           │
│            For: Precision, debugging, direct access                         │
│                                                                             │
│   Layer 0: API                                                              │
│            curl localhost:8000/agentese/invoke                              │
│            Raw HTTP/JSON                                                    │
│            For: Programmatic access, external integrations                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Layer Decision: Essential vs. Nice-to-Have

| Layer | Essential? | Rationale |
|-------|------------|-----------|
| **Layer 0: API** | ✅ Essential | Foundation—everything builds on this |
| **Layer 1: REPL** | ✅ Essential | Direct access for debugging and precision |
| **Layer 2: TUI** | ✅ Essential | Primary learning/exploration interface |
| **Layer 3: Garden** | ⚡ Power-user | Spatial thinking, cultivation metaphor |

### 3.2 Default Experience

**When user types just `kg`:**

```
$ kg
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│   Welcome to kgents                                         observer: guest │
│   ═══════════════                                                           │
│                                                                              │
│   What would you like to do?                                                │
│                                                                              │
│   [1] Explore the lattice         kg tui                                    │
│   [2] Direct invocation           kg repl                                   │
│   [3] Cultivate the garden        kg garden                                 │
│                                                                              │
│   Quick actions:                                                             │
│   • kg self.memory.manifest       See your memories                         │
│   • kg world.town.manifest        See the town                              │
│   • kg --help                     Full command reference                    │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 3.3 Layer Composition

Layers can be composed. The TUI can include a terminal pane for REPL commands. The garden can accept filesystem-style paths:

```
╭─ kg tui ────────────────────────────────────────────────────────────────────╮
│                                                                              │
│   [Manifest Panel]                               [Navigation Tree]          │
│                                                                              │
│   self.memory.crystals.abc123                    world                       │
│   ─────────────────────────────                  ├── town                    │
│   "Category theory as a way of                   │   └── citizens            │
│    seeing relationships..."                      ├── park                    │
│                                                  └── atelier                 │
│   [afford: edit] [afford: forget]                                           │
│                                                  self                        │
│                                                  ├── memory ◉                │
│                                                  └── soul                    │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  Terminal (embedded REPL)                                                    │
│  [self.memory] » capture "new thought"                                       │
│  ✓ Crystal captured: def789                                                  │
│  [self.memory] » _                                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## Part IV: Text Editor Interface

For longer content, the CLI supports an editor interface:

### 4.1 Triggering Editor Mode

```bash
# Explicit compose command
$ kg compose self.memory.capture
# Opens $EDITOR with template

# Aspect-specific trigger
$ kg self.memory.capture --editor
# Opens editor for this specific aspect

# Auto-detection (if input would be long)
$ kg self.memory.capture
# If no argument, opens editor
```

### 4.2 Template Format

Templates use YAML frontmatter + Markdown body:

```yaml
# ─────────────────────────────────────────────────────────
# self.memory.capture
#
# Write your thought below the --- line.
# Delete this comment block when done.
# ─────────────────────────────────────────────────────────
aspect: capture
path: self.memory
tags: []
---

Your thought here...

```

### 4.3 Preview Mode

Before execution, show a preview:

```bash
$ kg compose self.memory.capture
# ... user writes in editor, saves, closes ...

╭─ Preview ───────────────────────────────────────────────────────────────────╮
│                                                                              │
│ Path:   self.memory                                                         │
│ Aspect: capture                                                             │
│ Tags:   [category-theory, insight]                                          │
│                                                                              │
│ Content:                                                                     │
│   "Category theory isn't just math—it's a way of seeing                    │
│    relationships that already exist but were invisible.                     │
│    Like putting on glasses."                                                │
│                                                                              │
│ [Execute]  [Edit again]  [Cancel]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### 4.4 Inline vs. External Editor

**Decision: External $EDITOR by default, with inline option.**

```bash
# Default: external editor
$ kg compose self.memory.capture
# Opens vim, nvim, code, etc.

# Inline mode for quick edits
$ kg compose self.memory.capture --inline
╭─ Compose ───────────────────────────────────────────────────────────────────╮
│ > Category theory isn't just math—it's a way of seeing                     │
│   relationships that already exist but were invisible. _                    │
│                                                                              │
│ [Ctrl-D] Submit  [Ctrl-C] Cancel  [Ctrl-E] Open in $EDITOR                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## Part V: The Hypermedia TUI

### 5.1 Tech Choice: textual (Python)

**Rationale:**
- Same language as backend (direct Logos access)
- Rich widget library with async support
- CSS-like styling for Living Earth palette
- Active development by Will McGugan

### 5.2 Design Tokens: Web → Terminal Mapping

The TUI echoes web component patterns:

| Web Component | Terminal Widget | Shared Pattern |
|---------------|-----------------|----------------|
| `Breathe.tsx` | Breathing border animation | 3-4s pulse, 2-3% amplitude |
| `Pop.tsx` | Scale transition on focus | 300ms spring |
| `ElasticCard.tsx` | Box widget with density modes | Compact/Comfortable/Spacious |
| `TracePanel.tsx` | Event log widget | Scrollable, timestamped |
| `TeachingCallout.tsx` | Info panel with 💡 | Yellow-tinted border |

### 5.3 Living Earth Palette (Terminal Safe)

```
╭───────────────────────────────────────────────────────────────────────────╮
│  LIVING EARTH PALETTE (Terminal Safe)                                     │
│  ═══════════════════════════════════                                     │
│                                                                           │
│  BACKGROUND:                                                              │
│  ┌─────────┐                                                              │
│  │ #1A1612 │  Deep soil (almost black but warm)                          │
│  └─────────┘                                                              │
│                                                                           │
│  TEXT:                                                                    │
│  ┌─────────┐ ┌─────────┐                                                  │
│  │ #F5E6D3 │ │ #AB9080 │  Cream (primary) / Sand (secondary)             │
│  └─────────┘ └─────────┘                                                  │
│                                                                           │
│  NODE STATES:                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│  │ #8BAB8B │ │ #4A6B4A │ │ #D4A574 │ │ #8B6F5C │ │ #4A3728 │            │
│  │ Sprout  │ │  Sage   │ │  Amber  │ │  Clay   │ │  Bark   │            │
│  │ (seed)  │ │ (grow)  │ │ (bloom) │ │ (fade)  │ │(compost)│            │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│                                                                           │
│  EDGES:                                                                   │
│  ┌─────────┐ ┌─────────┐                                                  │
│  │ #6B4E3D │ │ #C08552 │  Wood (structural) / Copper (semantic)          │
│  └─────────┘ └─────────┘                                                  │
│                                                                           │
╰───────────────────────────────────────────────────────────────────────────╯
```

### 5.4 Screen Regions

```
╭────────────────────────────────────────────────────────────────────╮
│ BREADCRUMB: root > world > town > citizens > elara           [◉]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ╭─ MANIFEST ────────────────────────────────────────────────────╮ │
│  │  name: "Elara"                                                 │ │
│  │  personality: curious, contemplative                          │ │
│  │  role: researcher                                             │ │
│  │  mood: contemplative                                          │ │
│  │  current_thought: "What patterns connect these ideas?"        │ │
│  ╰───────────────────────────────────────────────────────────────╯ │
│                                                                    │
│  ╭─ AFFORDANCES ─────────────────────────────────────────────────╮ │
│  │  [greet]  [challenge]  [witness]  [polynomial]                │ │
│  ╰───────────────────────────────────────────────────────────────╯ │
│                                                                    │
│  ╭─ RELATED ─────────────────────────────────────────────────────╮ │
│  │  ← citizens/marcus    ↑ coalitions    → self.memory           │ │
│  ╰───────────────────────────────────────────────────────────────╯ │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│ » greet --target=marcus                                            │
╰────────────────────────────────────────────────────────────────────╯
```

---

## Part VI: The Organic Garden

The organic garden (`kg garden`) is a spatial visualization of the lattice—seeing the filesystem as a living, breathing topology.

### 6.1 Integration with CLI v6

The garden is Layer 4—a projection that renders the same lattice as filesystem or TUI, but with organic metaphors:

```
FILESYSTEM              TUI                    GARDEN
───────────             ───                    ──────
~/.kg/self/memory/      │ self                    ◉ memory
├── crystals/           │ ├── memory ◉             ╭───┴───╮
│   ├── abc123          │ │   └── crystals      crystals  .capture
│   └── def456          │ └── soul                 │
└── .capture            │                    ╭─────┼─────╮
                        │                   abc   def   ghi
                        │                    ●     ●     ○
```

### 6.2 Garden-Specific Commands

```bash
$ kg garden                    # Enter organic garden view
$ kg garden --focus self       # Start focused on self branch
$ kg garden --whispers off     # Disable garden suggestions
```

### 6.3 Cultivation Verbs

These verbs work in any layer but have special animations in garden view:

| Verb | Effect | Animation |
|------|--------|-----------|
| `seed` | Create new node | `. → · → • → ●` (400ms) |
| `graft` | Merge two nodes | Two nodes flow together (600ms) |
| `prune` | Remove cleanly | Fade with gratitude (800ms) |
| `compost` | Archive | Shrink, dim, disappear (800ms) |
| `tend` | Refresh life state | Pulse brightens (500ms) |
| `bloom` | Promote visibility | Expand, radiate (500ms) |

---

## Part VII: Core Primitives

### The Three Core Primitives

> *"Navigating to paths, learning about them interactively or passively, and reading/writing files will be the core primitives of the kgents system always."*

1. **NAVIGATE** — Move through the lattice
2. **LEARN** — Understand what's at a path (manifest, affordances, schema)
3. **READ/WRITE** — Invoke perception and mutation aspects

Everything else is projection of these three primitives.

### 7.1 Navigate

```bash
# All equivalent ways to navigate
$ kg cd self.memory              # REPL-style
» self.memory                    # TUI navigation
focus self.memory               # Garden command
```

### 7.2 Learn

```bash
# Passive learning (just observe)
$ kg self.memory                 # Show manifest

# Interactive learning (discover affordances)
$ kg self.memory --affordances   # List what you can do
$ kg self.memory ?               # REPL-style discovery

# Deep learning (understand schema)
$ kg self.memory --schema        # JSON schema
```

### 7.3 Read/Write

```bash
# Read (perception aspects)
$ kg self.memory.manifest        # Invoke manifest
$ kg self.memory.crystals        # List crystals

# Write (mutation aspects)
$ kg self.memory.capture "text"  # Capture with inline content
$ kg compose self.memory.capture # Long-form via $EDITOR

# Structured write
$ kg self.memory.capture --content="text" --tags="[insight]"
```

---

## Part VIII: Architecture

### 8.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLI v6 ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Layer 4: EXPERIENCE PROJECTIONS                                            │
│            ├── kg-garden        → Organic spatial view (textual)             │
│            ├── kg-tui           → Hypermedia browser (textual)               │
│            └── kg-repl          → Direct invocation (prompt_toolkit)         │
│                                                                              │
│   Layer 3: EDITOR INTEGRATION                                                │
│            kg-compose           → $EDITOR interface with templates           │
│                                                                              │
│   Layer 2: CLI CORE                                                          │
│            kg                   → Entry point, routing, dispatch             │
│            kg --complete        → Tab completion for all projections         │
│                                                                              │
│   Layer 1: AGENTESE PROTOCOL                                                 │
│            logos.invoke()       → Unified invocation                         │
│            logos.query()        → Path matching                              │
│            logos.subscribe()    → Live updates                               │
│                                                                              │
│   Layer 0: NODE REGISTRY                                                     │
│            @node declarations   → Ground truth lattice                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 File Structure

```
impl/claude/cli/
├── __init__.py
├── main.py              # Entry point: `kg` command
├── completion.py        # Tab completion engine
├── compose.py           # Editor interface
├── tui/
│   ├── __init__.py
│   ├── app.py           # Textual application
│   ├── widgets/
│   │   ├── manifest.py  # Manifest display widget
│   │   ├── tree.py      # Navigation tree widget
│   │   ├── prompt.py    # Command input widget
│   │   └── trace.py     # Event trace widget
│   └── styles.py        # Living Earth CSS
├── garden/
│   ├── __init__.py
│   ├── app.py           # Organic garden application
│   ├── layout.py        # Force-directed organic layout
│   ├── nodes.py         # Node rendering with life states
│   └── gestures.py      # Cultivation verb animations
└── repl/
    ├── __init__.py
    ├── loop.py          # REPL main loop
    └── parser.py        # AGENTESE syntax parsing
```

---

## Part IX: Implementation Phases

### Phase 0: Foundation (Week 1)

**Goal:** Core CLI with direct invocation

**Deliverables:**
- [ ] `kg <path>` invokes manifest
- [ ] `kg <path>.<aspect> [args]` invokes aspect
- [ ] `kg --complete` returns completions from registry
- [ ] Basic error handling with warm messages

**Test:**
```bash
$ kg self.memory
# Returns manifest JSON
$ kg self.memory.capture "test thought"
# Returns capture result
```

### Phase 1: REPL (Week 2)

**Goal:** Interactive REPL with context

**Deliverables:**
- [ ] `kg repl` enters REPL mode
- [ ] Navigation via path expressions
- [ ] Tab completion in REPL
- [ ] Context-aware prompts

**Test:**
```bash
$ kg repl
[root] » self.memory
→ memory
[self.memory] » capture "thought"
✓ Crystal captured: abc123
```

### Phase 2: TUI (Weeks 3-4)

**Goal:** Hypermedia browser with textual

**Deliverables:**
- [ ] `kg tui` launches browser
- [ ] Manifest, affordances, related panels
- [ ] Vim-style navigation
- [ ] Embedded terminal for REPL commands
- [ ] Living Earth color scheme

**Test:**
```bash
$ kg tui
# Full screen TUI with navigation
```

### Phase 3: Editor Integration (Week 5)

**Goal:** Compose interface for long content

**Deliverables:**
- [ ] `kg compose <path>.<aspect>` opens editor
- [ ] YAML frontmatter + Markdown body templates
- [ ] Preview before execution
- [ ] Inline mode with `--inline`

**Test:**
```bash
$ kg compose self.memory.capture
# Opens $EDITOR with template
# On save, shows preview, executes on confirm
```

### Phase 4: Garden (Weeks 6-7)

**Goal:** Organic spatial visualization

**Deliverables:**
- [ ] `kg garden` enters garden view
- [ ] Force-directed layout with organic jitter
- [ ] Life states (seed, growing, mature, fading, composting)
- [ ] Cultivation verbs with animations
- [ ] Whisper system for suggestions

**Test:**
```bash
$ kg garden
# Full screen organic visualization
# Nodes breathe, edges show relationships
# Whispers suggest connections
```

### Phase 5: Live Mode (Week 8)

**Goal:** Real-time subscriptions

**Deliverables:**
- [ ] `kg --live <path>` shows live updates
- [ ] TUI manifest updates automatically
- [ ] Garden nodes pulse on change
- [ ] `[◉]` indicator shows subscription active

**Test:**
```bash
$ kg --live world.town.citizens
# Display updates as citizens change
```

---

## Part X: Decision Log

### D1: Is the Lattice Just the Registry?

**Question:** Is the lattice just the node registry, or a richer semantic structure?

**Decision:** The lattice IS the registry. Additional semantic structure (relationships, life states) is metadata on nodes.

**Rationale:**
- Single source of truth
- No synchronization complexity
- Registry already has aspect metadata, affordances

### D2: How Do Projections Subscribe?

**Question:** How do projections subscribe to lattice changes?

**Decision:** Via SynergyBus events emitted after logos.invoke().

**Rationale:**
- SynergyBus already exists for cross-jewel events
- Clean separation between invocation and notification
- Multiple projections can subscribe independently

### D3: TUI Technology

**Question:** textual vs. rich vs. ink?

**Decision:** textual (Python).

**Rationale:**
- Same language as backend (direct Logos access)
- Rich widget library
- Async-native (important for subscriptions)
- CSS-like styling maps well to Living Earth palette

### D4: Default kg Experience

**Question:** What's the default `kg` experience?

**Decision:** Welcome screen with options, not immediate TUI entry.

**Rationale:**
- New users need orientation
- Experts can configure default (`kg --default=tui` in config)
- Clear paths to each experience layer

### D5: Editor Mode Trigger

**Question:** What triggers editor mode?

**Decision:** Explicit `kg compose` command, or `--editor` flag, or no-argument invocation of mutation aspects.

**Rationale:**
- Explicit is predictable
- No-argument behavior is intuitive for capture-like aspects
- Flag available for any aspect

### D6: Template Format

**Question:** TOML vs. YAML vs. Markdown frontmatter?

**Decision:** YAML frontmatter + Markdown body.

**Rationale:**
- Familiar to developers (Hugo, Jekyll, etc.)
- YAML handles structured kwargs
- Markdown body is natural for content

---

## Part XI: What We Delete

### From v5

| Component | v5 Proposal | v6 Status |
|-----------|-------------|-----------|
| FUSE filesystem | kgfs mount | **Dropped** — pure CLI instead |
| macfuse dependency | Required for macOS | **Gone** — no OS dependencies |
| Kernel extension | FUSE requires | **Gone** — userspace only |
| Shell virtualization | Intercept cat/ls/echo | **Dropped** — overengineered |

### From Legacy

| Component | Status |
|-----------|--------|
| `COMMAND_REGISTRY` (50+ entries) | **Gone** — paths only |
| `handlers/*.py` (55 files) | **Gone** — logos.invoke |
| `contexts/*.py` (5 files) | **Gone** — registry is context |
| `hollow.py` (900 lines) | **Reduced to ~100** |

---

## Part XII: Success Criteria

### Quantitative

| Metric | Current | v6 Target |
|--------|---------|-----------|
| Commands | 50+ | **3** (tui, repl, garden) |
| Handler files | 55 | **0** |
| Learning curve | 30 min docs | **Exploration** |
| Time to first "whoa" | Unknown | **< 30 seconds** |

### Qualitative

- [ ] `kg tui` feels like browsing a living world
- [ ] `kg garden` creates a sense of cultivation
- [ ] Direct path invocation (`kg self.memory`) returns manifest
- [ ] Tab completion works everywhere
- [ ] New user can explore with zero documentation
- [ ] Editor interface feels natural for long content

### The Mirror Test

> *"Does K-gent feel like me on my best day?"*
> *"Daring, bold, creative, opinionated but not gaudy"*

CLI v6 should feel:
- **Daring**: Paths-as-interface replaces 50+ commands
- **Bold**: Deleting all handlers, using paths only
- **Creative**: Garden view, cultivation verbs, breathing nodes
- **Opinionated**: One way to navigate (paths), many ways to view (projections)
- **Not gaudy**: Living Earth palette, subtle animations, no visual noise

---

## Appendix A: ASCII Mockups

### A.1 TUI with Embedded Terminal

```
╭─────────────────────────────────────────────────────────────────────────────╮
│ self.memory                                                    observer: dev│
├────────────────────┬────────────────────────────────────────────────────────┤
│                    │                                                        │
│   NAVIGATION       │   MANIFEST                                             │
│   ══════════       │   ════════                                             │
│                    │                                                        │
│   ◉ root           │   {                                                    │
│   ├─● world        │     "crystal_count": 23,                               │
│   │  ├─○ town      │     "last_capture": "2025-12-19T10:30:00Z",            │
│   │  └─○ park      │     "active_crystals": [                               │
│   └─◉ self         │       "abc123",                                        │
│      ├─◉ memory ←  │       "def456",                                        │
│      │  └─● cryst  │       "ghi789"                                         │
│      └─○ soul      │     ]                                                  │
│                    │   }                                                    │
│                    │                                                        │
│   ◉ blooming       │   AFFORDANCES                                          │
│   ● growing        │   ═══════════                                          │
│   ○ dormant        │   [capture]  [recall]  [forget]  [crystals]            │
│                    │                                                        │
├────────────────────┴────────────────────────────────────────────────────────┤
│ [self.memory] » capture "Category theory insight: morphisms are primary"    │
│ ✓ Crystal captured: xyz789                                                  │
│ [self.memory] » _                                                           │
╰─────────────────────────────────────────────────────────────────────────────╯
```

### A.2 Garden View

```
╭─────────────────────────────────────────────────────────────────────────────╮
│ 🌱 THE GARDEN                                              23 nodes  │ dev │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ╭───────────╮                                  │
│                              │   root    │                                  │
│                              │    ◉      │                                  │
│                              ╰─────┬─────╯                                  │
│                   ╭────────────────┼────────────────╮                       │
│                   │                │                │                       │
│            ╭──────┴──────╮  ╭──────┴──────╮  ╭──────┴──────╮                │
│            │    world    │  │    self     │  │   concept   │                │
│            │      ●      │  │      ◉      │  │      ●      │                │
│            ╰──────┬──────╯  ╰──────┬──────╯  ╰──────┬──────╯                │
│           ╭───────┼───────╮  ╭─────┴─────╮        │                         │
│           │       │       │  │           │     gardener                     │
│         town    park   atelier memory   soul       ●                        │
│          ●●●     ○       ●    ◉◉●●○      ○                                  │
│                                                                             │
│   Legend: ◉ blooming  ● growing  ○ dormant                                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ WHISPERS:                                                                   │
│ • "sheaf-coherence" and "distributed-systems" want to meet                 │
│ • 3 crystals are becoming compost (47+ days untouched)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ [f]ocus  [s]eed  [g]raft  [c]ompost  [/]search  [?]help   » _              │
╰─────────────────────────────────────────────────────────────────────────────╯
```

### A.3 Compose/Editor Preview

```
╭─────────────────────────────────────────────────────────────────────────────╮
│ COMPOSE: self.memory.capture                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ╭─ Preview ─────────────────────────────────────────────────────────────╮ │
│   │                                                                       │ │
│   │  PATH:    self.memory                                                 │ │
│   │  ASPECT:  capture                                                     │ │
│   │  TAGS:    [category-theory, insight]                                  │ │
│   │                                                                       │ │
│   │  CONTENT:                                                             │ │
│   │  ─────────────────────────────────────────────────────────────────    │ │
│   │  Category theory isn't just math—it's a way of seeing                │ │
│   │  relationships that already exist but were invisible.                 │ │
│   │                                                                       │ │
│   │  The key insight is that morphisms are more fundamental              │ │
│   │  than objects. We define things by their relationships,              │ │
│   │  not their intrinsic properties. This is why functors               │ │
│   │  preserve structure: they preserve the relationships.                │ │
│   │  ─────────────────────────────────────────────────────────────────    │ │
│   │                                                                       │ │
│   ╰───────────────────────────────────────────────────────────────────────╯ │
│                                                                             │
│   [Execute]  [Edit again]  [Cancel]                                         │
│                                                                             │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## Appendix B: Anti-Sausage Check

Before implementing this spec:

- ❓ *Did I smooth anything that should stay rough?*
  **No.** The virtualization approach is deliberately unconventional.

- ❓ *Did I add words Kent wouldn't use?*
  **Checking:** "lattice," "projection," "virtualization"—these align with categorical thinking.

- ❓ *Did I lose any opinionated stances?*
  **No.** Dropping FUSE while keeping the vision is MORE opinionated, not less.

- ❓ *Is this still daring, bold, creative—or did I make it safe?*
  **Daring.** Shell virtualization without kernel extensions is novel. The garden remains unconventional.

---

*"The garden's grammar generates the flowers. The lattice projects the garden."*

*Last updated: 2025-12-19*
*Version: 6.0*
*Principle: Navigate, Learn, Read/Write—everything else is projection.*
