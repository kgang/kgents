# CLI v5: The Living Interface

**Status:** Vision Draft
**Date:** 2025-12-19
**Principle:** *"The interface is not a window—it's a membrane."*

---

## Epigraph

> *"The noun is a lie. There is only the rate of change."*
>
> *"Everything is a file—but files are living."* — Plan 9 Heresy
>
> *"There is no 'developer mode.' Browsing IS editing IS programming."* — HyperCard Legacy
>
> *"Liveness is not a feature. Liveness is the point."* — Morphic Wisdom
>
> *"The best protocol is the one that disappears."* — AGENTESE v3

---

## Part I: The Problem with Commands

The history of the terminal is the history of **imperative enumeration**:

```
$ git add .
$ git commit -m "message"
$ git push
$ docker build -t myimage .
$ kubectl apply -f deployment.yaml
$ npm install
$ npm run build
```

Every tool invents its own vocabulary. You learn one, then another, then another. The cognitive load compounds. The grammar never unifies.

CLI v4 recognized this: **"There are no commands, only paths."**

CLI v5 goes further: **"There is no shell, only the membrane."**

---

## Part II: Three Revolutionary Ideas

### Idea 1: The Filesystem as Living Interface (From Plan 9)

> *"9P is the only protocol the kernel knows."*

Plan 9's insight: **everything is a file**—but not just a metaphor. Actual files. The process table is a directory. Network connections are files. The window manager exposes a filesystem.

What if AGENTESE did the same?

```
~/.kg/
├── world/
│   ├── town/
│   │   ├── citizens/
│   │   │   ├── elara      # reading this file = manifest
│   │   │   └── marcus     # writing to this file = invoke
│   │   └── coalitions/
│   └── park/
├── self/
│   ├── memory/
│   │   ├── crystals/      # each crystal is a file
│   │   └── .capture       # write here to capture
│   └── soul/
├── concept/
└── void/
    └── entropy            # read for randomness
```

**The paths ARE the filesystem. The filesystem IS the paths.**

No CLI needed. Use `cat`, `echo`, `ls`. Every Unix tool becomes a kgents tool:

```bash
# List all citizens
$ ls ~/.kg/world/town/citizens
elara  marcus  kai  zara

# Get citizen manifest
$ cat ~/.kg/world/town/citizens/elara
{"name": "Elara", "personality": "curious", "role": "researcher"}

# Capture a memory
$ echo "Category theory is beautiful" > ~/.kg/self/memory/.capture

# Compose via pipes
$ cat ~/.kg/self/memory/crystals/abc123 | \
  ~/.kg/concept/summary/.refine | \
  tee ~/.kg/self/memory/.capture

# Subscribe via tail
$ tail -f ~/.kg/world/town/citizens
```

**Implementation:** FUSE filesystem backed by Logos. Each read triggers `manifest`. Each write triggers the appropriate mutation aspect. The registry IS the directory structure.

---

### Idea 2: The REPL as Hypermedia Environment (From HyperCard)

> *"There was no separate 'developer mode.'"*

HyperCard collapsed the distinction between using and creating. You weren't switching between "user" and "creator"—you were both, simultaneously.

The current AGENTESE REPL is a step in this direction:

```
[root] » self.memory
→ memory
[self.memory] » capture "text"
✓ Crystal captured: abc123
```

But it's still imperative. CLI v5 makes it **hypermedia**:

```
╭─────────────────────────────────────────────────────────────────╮
│  self.memory                                              [▸◀] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ╭─ Crystals (3) ─────────────────────────────────────────────╮ │
│  │  ● Category theory notes     [manifest] [edit] [forget]   │ │
│  │  ● Session reflections       [manifest] [edit] [forget]   │ │
│  │  ● Design decisions          [manifest] [edit] [forget]   │ │
│  ╰────────────────────────────────────────────────────────────╯ │
│                                                                 │
│  ╭─ Actions ──────────────────────────────────────────────────╮ │
│  │  [capture: text]     [recall: query]     [forget: id]     │ │
│  ╰────────────────────────────────────────────────────────────╯ │
│                                                                 │
│  Breadcrumb: root > self > memory                              │
│  Related: self.soul, world.atelier.canvas                      │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
» _
```

**Navigation IS viewing IS editing.** Click a crystal to expand. Click `[edit]` to mutate. Click a related path to navigate. The prompt at the bottom is just one way to interact.

**Key insight:** The REPL isn't a command line—it's a **TUI browser for AGENTESE space**.

---

### Idea 3: Reactive Dataflow (From Observable + Smalltalk)

> *"Observable notebooks update reactively any time a cell's value changes."*

The current CLI is one-shot: invoke → result → done. But AGENTESE supports subscriptions. What if the CLI was **live**?

```bash
$ kg --live world.town.citizens

╭─ world.town.citizens (live) ────────────────────────────────────╮
│                                                                  │
│  ● elara       mood: contemplative   [updated 2s ago]           │
│  ● marcus      mood: energetic       [updated 1m ago]           │
│  ● kai         mood: playful         [just now ◉]               │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  Events:                                                         │
│    12:34:05  kai.greet(target=elara) → "Hello!"                  │
│    12:34:02  elara.reflect() → [contemplating]                   │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

The display **updates in real-time** as the world changes. No polling. No refresh. Subscriptions → Flux → Terminal.

**Composition becomes dataflow:**

```bash
$ kg --live self.memory.crystals \
    | kg concept.summary.refine \
    | kg self.memory.capture

# This pipeline is LIVE:
# - New crystals flow through
# - Each is refined
# - Each is captured
# - Display shows the flow
```

**The pipe is not batch. The pipe is stream.**

---

## Part III: The Unified Vision

These three ideas compose into something greater:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE LIVING INTERFACE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Layer 4: PROJECTION SURFACES                                               │
│            ├── Filesystem (FUSE)     → Unix tools, scripts, IDE             │
│            ├── Hypermedia TUI        → Interactive exploration               │
│            ├── Live Shell            → Reactive dataflow                     │
│            └── Web/marimo/API        → Existing surfaces                     │
│                                                                              │
│   Layer 3: SUBSCRIPTION ENGINE                                               │
│            Logos.subscribe() → Flux streams → all surfaces                   │
│                                                                              │
│   Layer 2: AGENTESE PROTOCOL                                                 │
│            logos.invoke(path, observer, **kwargs)                            │
│                                                                              │
│   Layer 1: NODE REGISTRY                                                     │
│            @node declarations in services/*/node.py                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The CLI is not a command interpreter. It's a membrane between you and the living system.**

---

## Part IV: The Grammar (Simplified)

### 4.1 Core Grammar

With the filesystem as interface, the "grammar" becomes Unix:

| Operation | Traditional | Filesystem | Live |
|-----------|-------------|------------|------|
| Invoke | `kg self.memory.manifest` | `cat ~/.kg/self/memory` | `kg --live self.memory` |
| Mutate | `kg self.memory.capture "text"` | `echo "text" > ~/.kg/self/memory/.capture` | (streaming input) |
| Query | `kg q self.*` | `find ~/.kg/self -type f` | `kg q --live self.*` |
| Subscribe | N/A | `tail -f ~/.kg/...` | `kg --live ...` |
| Compose | `kg a >> b >> c` | `cat a \| b \| c` | `kg --live a \| b \| c` |

**The filesystem IS the grammar.**

### 4.2 Interactive Grammar

For the hypermedia TUI:

```
Navigation:     ←↓↑→ or h/j/k/l      move through paths
Enter:          invoke manifest or descend
Tab:            autocomplete
/:              fuzzy search paths
?:              show affordances for current node
!:              invoke with kwargs (opens input)
>>:             enter composition mode
Ctrl-L:         toggle live mode
```

### 4.3 Shell Escapes

Infrastructure that can't be a path (chicken-egg problem):

```bash
$ kg mount                   # Mount FUSE filesystem
$ kg unmount                 # Unmount
$ kg daemon start/stop       # Daemon lifecycle
$ kg status                  # System status
```

These are the ONLY commands. Everything else is a path.

---

## Part V: The Filesystem Protocol

### 5.1 Directory Structure

```
~/.kg/                          # FUSE mount point
├── .meta/                      # System metadata (hidden)
│   ├── discover                # Read = /agentese/discover
│   ├── schema                  # JSON schemas
│   └── aliases                 # User aliases
├── world/
│   ├── town/
│   │   ├── .manifest           # Read = invoke manifest
│   │   ├── .polynomial         # Write = invoke polynomial
│   │   ├── citizens/           # Subdirectory = child paths
│   │   │   ├── elara
│   │   │   └── marcus
│   │   └── coalitions/
│   ├── park/
│   └── atelier/
├── self/
│   ├── memory/
│   │   ├── .manifest
│   │   ├── .capture            # Write "text" to capture
│   │   ├── .recall             # Write query, read result
│   │   └── crystals/           # Read individual crystals
│   ├── soul/
│   └── forest/
├── concept/
│   ├── gardener/
│   └── nphase/
├── void/
│   ├── entropy                 # Read for randomness
│   └── shadow/
└── time/
    └── trace/
```

### 5.2 File Operations → AGENTESE

| Operation | AGENTESE Effect |
|-----------|-----------------|
| `open(f, "r")` | Prepare to invoke aspect |
| `read(f)` | `logos.invoke(path, aspect="manifest")` |
| `write(f, data)` | `logos.invoke(path, aspect=<inferred>, **data)` |
| `readdir(d)` | `logos.query(path + ".*")` |
| `stat(f)` | Metadata: last modified, size, permissions |
| `inotify_add_watch` | `logos.subscribe(path)` |

### 5.3 Special Files

| File | Purpose |
|------|---------|
| `.manifest` | Read invokes manifest aspect |
| `.{aspect}` | Write invokes that aspect |
| `.affordances` | Read lists available aspects |
| `.schema` | Read returns JSON schema |
| `.watch` | Read blocks, yields on change (like FUSE poll) |

### 5.4 Permissions (Observer-Dependent)

The filesystem exposes observer-dependent affordances:

```bash
$ export KG_ARCHETYPE=guest
$ ls ~/.kg/self/memory/crystals
ls: cannot access: Permission denied

$ export KG_ARCHETYPE=developer
$ ls ~/.kg/self/memory/crystals
abc123  def456  ghi789
```

**The observer archetype determines what's visible.**

---

## Part VI: The Hypermedia TUI

### 6.1 Design Principles

1. **Navigation = Invocation**: Moving to a node invokes its manifest
2. **Visible Affordances**: What you can do is always shown
3. **No Hidden Commands**: Everything is discoverable by exploration
4. **Warm Errors**: Failures suggest next steps
5. **Live by Default**: Subscriptions stream updates automatically

### 6.2 Screen Regions

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

### 6.3 Interaction Flow

```
User presses 'g' (greet affordance)
  → Modal opens: "greet(target: ___)"
  → User types "marcus" or selects from completion
  → Enter confirms
  → Result displays inline
  → Manifest updates (live subscription)
```

### 6.4 Composition Mode

Press `>>` to enter composition mode:

```
╭─ COMPOSITION MODE ──────────────────────────────────────────────────╮
│                                                                      │
│  Step 1: self.memory.recall query="last week"                        │
│          ↓                                                           │
│  Step 2: concept.summary.refine                                      │
│          ↓                                                           │
│  Step 3: self.memory.capture                                         │
│                                                                      │
│  [Preview Effects]  [Execute]  [Cancel]                              │
│                                                                      │
│  Combined Effects:                                                   │
│    reads: memory_crystals                                            │
│    writes: memory_crystals                                           │
│    calls: llm                                                        │
│                                                                      │
╰──────────────────────────────────────────────────────────────────────╯
```

---

## Part VII: Live Mode

### 7.1 The Reactive Shell

```bash
$ kg --live world.town.citizens
```

This opens a live view that:
1. Subscribes to `world.town.citizens.*`
2. Displays current state
3. Streams updates as they happen
4. Allows inline invocation

### 7.2 Live Pipelines

```bash
$ kg --live self.memory.crystals | kg concept.tag | kg --live self.forest.nodes

# Crystal added → tagged → forest node created
# All visible in real-time
```

**Pipelines become dataflow graphs.**

### 7.3 Watch Mode

```bash
$ kg watch self.forest.manifest --on-change="say 'Forest updated'"
```

Execute arbitrary commands on path changes.

---

## Part VIII: What We Build

### 8.1 Components

| Component | Purpose | Priority |
|-----------|---------|----------|
| **kgfs** | FUSE filesystem exposing AGENTESE | P1 |
| **kg-tui** | Hypermedia TUI browser | P1 |
| **kg-live** | Live/reactive shell mode | P2 |
| **kg-sh** | Minimal escape hatch commands | P0 |

### 8.2 Implementation Path

**Phase 1: Foundation (Week 1-2)**
- `kgfs`: Basic FUSE mount with read-only manifest
- `kg-sh`: Mount/unmount/status commands only

**Phase 2: Mutation (Week 3-4)**
- `kgfs`: Write support (aspect invocation)
- `kgfs`: Directory operations (query)

**Phase 3: TUI (Week 5-6)**
- `kg-tui`: Hypermedia browser
- Navigation, affordances, inline invocation

**Phase 4: Liveness (Week 7-8)**
- `kgfs`: inotify support (subscriptions)
- `kg-live`: Reactive shell mode
- Live pipelines

---

## Part IX: What We Delete

### 9.1 Removed Completely

| Component | Lines | Fate |
|-----------|-------|------|
| `COMMAND_REGISTRY` | 50+ entries | **Gone** |
| `handlers/*.py` | 55 files | **Gone** |
| `contexts/*.py` | 5 files | **Gone** |
| `hollow.py` (most) | 900 lines | **Reduced to ~50** |
| Legacy compatibility | N/A | **Never existed** |

### 9.2 What Remains

```
kg
├── mount          # Mount ~/.kg FUSE filesystem
├── unmount        # Unmount
├── daemon         # start/stop/status
├── status         # System health
└── (that's it)
```

Four commands. Everything else is a path.

---

## Part X: Connection to Principles

| Principle | How CLI v5 Embodies It |
|-----------|------------------------|
| **Tasteful** | 55 handlers → 4 commands → the filesystem |
| **Curated** | One interface (filesystem) subsumes all others |
| **Ethical** | Transparent: what you see is what exists |
| **Joy-Inducing** | `cat ~/.kg/void/entropy` feels like magic |
| **Composable** | Unix pipes ARE composition |
| **Heterarchical** | Live mode (loop) + one-shot (function) |
| **Generative** | Filesystem derived from `@node` registry |

---

## Part XI: The Deeper Insight

The CLI v4 insight was: **"There are no commands, only paths."**

CLI v5 goes deeper: **"There is no interface, only the membrane between observer and observed."**

The filesystem is not a metaphor. It's not "like" the AGENTESE namespace. It IS the namespace. Reading a file IS invoking an aspect. Writing a file IS mutation. The `@node` registry IS the directory structure.

This is what Plan 9 understood: when everything is a file, the filesystem becomes the universal protocol. Every tool that operates on files operates on your system. You don't need a "CLI"—you need a mount point.

---

## Part XII: Philosophical Foundation

### 12.1 The Membrane Model

Traditional interfaces:
```
User ──[commands]──→ System ──[results]──→ User
```

The membrane model:
```
User ←────────[membrane]────────→ System
      ↑                      ↑
   (observer)           (observed)
```

The membrane is bidirectional, continuous, alive. Changes on either side propagate through. The user's observation affects what's visible. The system's state affects what the user perceives.

### 12.2 Liveness as Ontology

The current CLI is dead: invoke → result → done. The connection closes.

The living interface maintains connection. You're not "using" the system—you're in relationship with it. Changes flow. State evolves. The boundary between "your actions" and "the system's state" blurs.

This is what Smalltalk's Morphic understood: **liveness is not a feature, it's the point**.

### 12.3 Discovery Through Exploration

HyperCard's genius: there's no documentation because you can just look. Click something, see what it does. Navigate, observe, try.

The filesystem embodies this: `ls` shows what exists. `cat` shows what it contains. No man pages needed for `~/.kg/world/town/citizens/elara`—just look.

---

## Part XIII: Research Frontiers

### 13.1 AGENTESE over 9P

What if `kgfs` spoke 9P instead of FUSE? Then:
- Remote mounts: `mount -t 9p kgents.example.com /mnt/kg`
- Network transparency for free
- Plan 9 compatibility

### 13.2 Semantic Filesystem

Beyond simple files:
```bash
$ cat ~/.kg/world/town/citizens/elara/thoughts
$ echo "What if we tried X?" > ~/.kg/world/town/citizens/elara/.ponder
$ cat ~/.kg/world/town/citizens/elara/response
```

The filesystem becomes a dialogue interface.

### 13.3 Temporal Files

```bash
$ cat ~/.kg/time/2025-12-01/self/memory
# Memory as it was on that date

$ diff ~/.kg/time/yesterday/self/forest ~/.kg/self/forest
# What changed?
```

Time as a filesystem dimension.

### 13.4 Compositional Directories

```bash
$ mkdir ~/.kg/composed/my-pipeline
$ ln -s ~/.kg/self/memory/crystals ~/.kg/composed/my-pipeline/1-source
$ ln -s ~/.kg/concept/summary/.refine ~/.kg/composed/my-pipeline/2-process
$ ln -s ~/.kg/self/memory/.capture ~/.kg/composed/my-pipeline/3-sink
$ cat ~/.kg/composed/my-pipeline/.run
```

Composition as directory structure.

---

## Part XIV: Success Criteria

### 14.1 Quantitative

| Metric | Current | v4 Target | v5 Target |
|--------|---------|-----------|-----------|
| Commands | 50+ | 4 | **0** (filesystem) |
| Handler files | 55 | 2-3 | **0** |
| `hollow.py` lines | 900 | 100 | **50** |
| Time to understand | 30 min | 10 min | **Exploration** |

### 14.2 Qualitative

- [ ] `cat ~/.kg/self/memory` returns crystals
- [ ] `echo "text" > ~/.kg/self/memory/.capture` captures
- [ ] `ls ~/.kg/world/town/citizens` lists citizens
- [ ] `tail -f ~/.kg/world/town` streams events
- [ ] `kg-tui` feels like browsing a living world
- [ ] New contributor needs no documentation—just exploration

---

## Appendix A: Prior Art

### A.1 Plan 9 / 9P

- [Plan 9 Desktop Guide](https://pspodcasting.net/dan/blog/2019/plan9_desktop.html)
- [9P Protocol Notes](https://blog.gnoack.org/post/9pnotes/)
- [Everything is a file (Wikipedia)](https://en.wikipedia.org/wiki/Everything_is_a_file)

### A.2 HyperCard

- [HyperCard Wikipedia](https://en.wikipedia.org/wiki/HyperCard)
- [The HyperCard Legacy](https://medium.com/the-nextographer/the-hypercard-legacy-e5b9eb273b6a)
- [HyperCard's Revolution We Lost](https://medium.com/@avonliden/hypercards-legacy-the-revolution-we-lost-2819ca0b63ac)

### A.3 Morphic / Smalltalk

- [Morphic Introduction](https://handbook.selflanguage.org/2017.1/morphic.html)
- [Squeak Features](https://squeak.org/features/index.html)

### A.4 Observable / Reactive

- [Reactive Dataflow (Observable)](https://observablehq.com/@observablehq/reactive-dataflow)
- [Observable Runtime](https://github.com/observablehq/runtime)

### A.5 FUSE

- [FUSE Wikipedia](https://en.wikipedia.org/wiki/Filesystem_in_Userspace)
- [libfuse GitHub](https://github.com/libfuse/libfuse)

### A.6 Modern Terminals

- [Nushell](https://www.nushell.sh/) - Structured data shell
- [Warp Terminal](https://www.warp.dev/) - AI-powered terminal
- [CLIG Guidelines](https://clig.dev/)

---

## Appendix B: The Anti-Sausage Check

Before finalizing this document:

- ❓ *Did I smooth anything that should stay rough?*
  **No.** The filesystem-as-interface is deliberately radical.

- ❓ *Did I add words Kent wouldn't use?*
  **Checking:** "membrane," "liveness," "hypermedia"—these feel aligned with the philosophical bent.

- ❓ *Did I lose any opinionated stances?*
  **No.** This is MORE opinionated than v4.

- ❓ *Is this still daring, bold, creative—or did I make it safe?*
  **Daring.** "Delete all commands, use the filesystem" is not safe.

---

## Part XV: The Organic Garden Extension

> *"Directories are trees. Trees are graphs. The filesystem is already a mind-map."*

CLI v5's filesystem-as-interface creates the foundation. But the projection of that filesystem matters profoundly. The **Organic Garden** extension transforms how we perceive the namespace.

### 15.1 The Insight

Traditional filesystem views (ls, tree, finder) show dead structure:
```
~/.kg/self/memory/crystals/
├── abc123
├── def456
└── ghi789
```

The organic garden shows **living topology**:
```
                    ◉ memory
                        │
              ╭─────────┴─────────╮
          crystals            .capture
              │               (dormant)
    ╭─────────┼─────────╮
    │         │         │
◉ abc123  ● def456  ○ ghi789
   🌱        🌿        🍂
  (new)    (growing)  (fading)
```

Same data. Different perception. The observer's mode determines the projection.

### 15.2 Life States

Every node has a life state that manifests visually:

| State | Symbol | Meaning | Visual |
|-------|--------|---------|--------|
| Seed | 🌱 | Just planted, not yet read | Small, bright green |
| Growing | 🌿 | Active, being read, connecting | Medium, healthy green |
| Mature | 🌳 | Stable, well-connected | Large, deep green |
| Fading | 🍂 | Untouched for 30+ days | Dimming, amber |
| Composting | 💀 | Archived, but findable | Nearly invisible |

### 15.3 Cultivation Verbs

The garden introduces new verbs beyond traditional file operations:

| Verb | Effect | Metaphor |
|------|--------|----------|
| `seed` | Create new node | Plant something |
| `graft` | Merge two nodes | Combine wisdom |
| `prune` | Remove cleanly | Shape the garden |
| `compost` | Archive with gratitude | Nothing truly dies |
| `tend` | Visit and refresh | Show attention |
| `cross` | Find unexpected connections | Cross-pollination |
| `bloom` | Promote to high visibility | Let it flower |

### 15.4 The Garden View

```
$ kg garden
```

Enters an organic TUI where:
- Nodes breathe (5-10% size pulse every 5 seconds)
- Edges show relationships (structural solid, semantic dashed)
- Layout is force-directed with organic jitter (not grid)
- Colors are warm earth tones (Living Earth palette)
- Navigation is spatial, not hierarchical

### 15.5 Whispers

The garden doesn't alert—it *whispers*:

> • "sheaf-coherence" and "distributed-systems" want to meet
> • 3 crystals are becoming compost (47+ days untouched)
> • The concept.gardener branch is flourishing

Whispers are passive, positive, optional, and periodic—respecting attention.

### 15.6 Integration

The organic garden is a *view* on CLI v5, not a replacement:

```bash
$ ls ~/.kg/...        # Always works (filesystem)
$ kg                  # Hypermedia TUI browser
$ kg garden           # Organic garden visualization
$ kg --live path      # Reactive shell mode
```

All views share the same underlying FUSE filesystem and AGENTESE protocol.

**Full specification:** See `plans/cli-organic-garden.md`

---

*"The garden grows not by force, but by invitation."*

*"Everything is slop or comes from slop. We cherish and express gratitude."*

*"The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."*

---

*Last updated: 2025-12-19*
