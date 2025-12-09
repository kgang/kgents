# I-gent & W-gent Synergy

How Interface agents (I-gents) and Wire agents (W-gents) work together.

---

## The Complementary Pair

```
┌──────────────────────────────────────────────────┐
│               The Kgents Observatory             │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─ I-gent ────────────────────────────────┐    │
│  │ "What is the ecosystem doing?"          │    │
│  │                                          │    │
│  │ • Agent composition graphs               │    │
│  │ • Moon phases (lifecycle states)         │    │
│  │ • Garden topology                        │    │
│  │ • Cross-agent relationships              │    │
│  │                                          │    │
│  │ Aesthetic: Contemplative, archival       │    │
│  │ Persistence: Markdown-first, exportable  │    │
│  │ Scope: Ecosystem-wide                    │    │
│  └──────────────────────────────────────────┘    │
│                       │                          │
│                       │ [observe] action         │
│                       ↓                          │
│  ┌─ W-gent ────────────────────────────────┐    │
│  │ "What is this agent thinking?"          │    │
│  │                                          │    │
│  │ • Internal execution stream              │    │
│  │ • Task progress & stages                 │    │
│  │ • Performance metrics                    │    │
│  │ • Real-time event log                    │    │
│  │                                          │    │
│  │ Aesthetic: Instrumental, ephemeral       │    │
│  │ Persistence: Transient, localhost-served │    │
│  │ Scope: Single-agent internal state       │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Comparison Table

| Aspect | I-gent | W-gent |
|--------|--------|--------|
| **Question** | "How do agents compose?" | "How does this agent think?" |
| **Metaphor** | Zen garden / Library | Wire / Oscilloscope |
| **Granularity** | Ecosystem-level | Process-level |
| **Time scale** | Hours to days (sessions) | Seconds to minutes (tasks) |
| **Aesthetic** | Paper-terminal, warm, archival | Matrix/Dashboard, functional |
| **Primary output** | Markdown (exportable to paper) | HTML (localhost browser) |
| **Persistence** | Permanent (margin notes, history) | Ephemeral (stops with observation) |
| **Visual grammar** | Glyphs, cards, pages, gardens | Logs, progress bars, dashboards |
| **User posture** | Tending, contemplating, navigating | Debugging, monitoring, investigating |
| **Startup time** | Seconds (rendering ecosystem) | Instant (<100ms) |
| **Typical usage** | "Show me the garden" | "Why is robin stuck?" |

---

## The [observe] → W-gent Flow

### User Journey

**1. User is in I-gent, viewing a garden**

```
┌─ research garden ────────────────────────── t: 01:23:45 ─┐
│                                                          │
│       ● robin ─────────┐                                 │
│                        │                                 │
│       ◐ analyze     ● summarize                          │
│                        │                                 │
│             ● report                                     │
│                                                          │
│  focus: [robin]  │  > open page robin                    │
└──────────────────────────────────────────────────────────┘
```

**2. User opens robin's page**

```
╔══ robin ═════════════════════════════════════════════════╗
║                                                          ║
║  "A B-gent researching protein folding patterns."        ║
║                                                          ║
║  state: ● active                     t: 01:23:00         ║
║  ────────────────────────────────────────────────────    ║
║  joy: █████████░░  9/10                                  ║
║                                                          ║
║  [observe]  [invoke]  [compose]  [rest]                  ║
╚══════════════════════════════════════════════════════════╝
```

**3. User clicks [observe]**

I-gent executes:
```bash
kgents wire attach robin --detach
```

**4. Browser opens to W-gent view**

```
┌─ live wire :: robin ──────────────────────────────┐
│                                                   │
│  ┌─ Current Task ────────────────────────────┐   │
│  │ Stage: Hypothesis Synthesis               │   │
│  │ Progress: 67%                             │   │
│  │ ████████████████░░░░░░░░                  │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Event Stream ────────────────────────────┐   │
│  │ 01:22:45 [search] Querying PubMed         │   │
│  │ 01:22:50 [parse] 15 papers found          │   │
│  │ 01:23:00 [synthesize] Drafting v3         │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  [export to I-gent notes]  [download log]        │
└────────────────────────────────────────────────────┘
```

**5. User clicks [export to I-gent notes]**

W-gent appends to `.wire/robin/margin-notes.jsonl`

**6. User returns to I-gent**

I-gent page now shows:

```
╔══ robin ═════════════════════════════════════════════════╗
║                                                          ║
║  ┌─ margin notes ─────────────────────────────────────┐  ║
║  │ 01:23:07 — [w-gent] Synthesizing v3 (67% complete) │  ║
║  │ 01:23:07 — [w-gent] 42 API calls, 12.4k tokens     │  ║
║  └────────────────────────────────────────────────────┘  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## Why Two Agents Instead of One?

### Separation of Concerns

**I-gent** optimizes for:
- **Composition visibility**: How agents relate
- **Long-term contemplation**: Reading sessions like books
- **Archival permanence**: Printable, versionable
- **Fractal consistency**: Same grammar at all scales

**W-gent** optimizes for:
- **Process transparency**: What's happening now
- **Debugging immediacy**: Find the stuck loop
- **Ephemeral observation**: No persistent overhead
- **Fidelity adaptation**: Match data structure to view

**Counterexample**: If combined, we'd have:
- ❌ Complex UI trying to do both (cognitive overload)
- ❌ Archival data mixed with transient logs (clutter)
- ❌ Startup overhead (loading full ecosystem to observe one agent)
- ❌ Unclear purpose (is this for contemplation or debugging?)

### The Unix Philosophy

> "Do one thing well, compose easily."

- **I-gent**: Visualizes ecosystem composition → Does it well
- **W-gent**: Projects process internals → Does it well
- **Composition**: I-gent's `[observe]` spawns W-gent → Composes easily

---

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Agent (robin)                        │
│                                                         │
│  • Runs evolution loop                                  │
│  • Generates hypotheses                                 │
│  • Queries databases                                    │
│                                                         │
│  Writes to:                                             │
│    └─ .wire/robin/state.json     (current state)       │
│    └─ .wire/robin/stream.log     (event log)           │
│    └─ .wire/robin/metrics.json   (performance)         │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ↓                            ↓
   ┌─────────────────┐        ┌──────────────────────┐
   │    I-gent       │        │      W-gent          │
   │                 │        │                      │
   │ Reads:          │        │ Reads:               │
   │ • state.json    │        │ • state.json         │
   │ • margin notes  │        │ • stream.log         │
   │                 │        │ • metrics.json       │
   │ Renders:        │        │                      │
   │ • Moon phase    │        │ Renders:             │
   │ • Garden view   │        │ • Live dashboard     │
   │ • Timeline      │        │ • Event stream       │
   │                 │        │ • Progress bars      │
   │ Exports to:     │        │                      │
   │ • Markdown      │        │ Exports to:          │
   │ • Paper         │◄───────│ • I-gent notes       │
   └─────────────────┘        │ • Log download       │
                              └──────────────────────┘
```

### Shared State: `.wire/` Directory

```
.wire/
└── robin/
    ├── state.json              # Current state (both read)
    ├── stream.log              # Event log (W-gent writes, I-gent can read)
    ├── metrics.json            # Performance (W-gent writes)
    ├── margin-notes.jsonl      # I-gent notes (W-gent appends to)
    └── i-gent.lock             # Lock file (indicates I-gent active)
```

**Why `.wire/`?**
- Conventional location (agents know where to write)
- I-gent and W-gent both use it
- Gitignore-friendly (transient data, not committed)
- Easy to clean: `rm -rf .wire/`

---

## Use Case: Debugging Evolution Stuck Loop

### Scenario
Evolution pipeline is stuck. User wants to know why.

### Step 1: I-gent Shows High-Level Issue

```
┌─ preflight.py evolution ──────────────────────────┐
│ ◐ waning                       t: 00:45:23        │
│ Last activity: 00:15:00 ago                       │
│                                                   │
│ Something seems stuck...                          │
└────────────────────────────────────────────────────┘
```

**I-gent tells us**: Agent is in "waning" phase, no recent activity.

**But doesn't tell us**: WHY it's stuck, WHAT stage, WHERE the loop is.

### Step 2: User Clicks [observe] → W-gent Opens

```
┌─ live wire :: preflight.py ───────────────────────┐
│                                                   │
│  ┌─ Pipeline Stages ──────────────────────────┐  │
│  │ ✓ Ground (AST analysis)          2.1s     │  │
│  │ ✓ Hypothesis (idea generation)   5.3s     │  │
│  │ ⏳ Experiment (validation)        ...      │  │
│  │   └─ Stuck in mypy validation (00:30:12)  │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌─ Current Experiment ───────────────────────┐  │
│  │ Hypothesis: "Add type hints"               │  │
│  │ Status: Running mypy...                    │  │
│  │ Stderr:                                    │  │
│  │   mypy: error: Cannot find module 'foo'    │  │
│  │   (repeating for 30 minutes)               │  │
│  └───────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

**W-gent reveals**: mypy stuck on missing module, loop repeating error.

**User action**: Fix environment (install module), restart evolution.

---

## Use Case: Monitoring Long-Running Research

### Scenario
robin is running multi-hour research session. User wants to check in occasionally.

### Approach 1: I-gent (Ambient Monitoring)

User keeps I-gent open in terminal, glances at garden view:

```
┌─ research garden ────────────────────────── t: 03:45:12 ─┐
│                                                          │
│       ● robin ─────────┐                                 │
│                        │                                 │
│       ● analyze     ● summarize                          │
│                                                          │
│  breath: ░░░░████░░░░  (exhale)                          │
└──────────────────────────────────────────────────────────┘
```

**Information gleaned**:
- robin is ● active (not stuck)
- Composition graph stable
- Breath cycle = system alive

**What's missing**: What hypothesis? How much progress? Any errors?

### Approach 2: W-gent (Active Debugging)

User clicks `[observe]` on robin, browser shows:

```
┌─ live wire :: robin ──────────────────────────────┐
│                                                   │
│  ┌─ Current Task ────────────────────────────┐   │
│  │ Hypothesis: v12 "Beta-sheet stability"    │   │
│  │ Progress: 84%                             │   │
│  └───────────────────────────────────────────┘   │
│                                                   │
│  ┌─ Recent Events ───────────────────────────┐   │
│  │ 03:40:00 Queried 15 databases             │   │
│  │ 03:42:00 Synthesized patterns (3 found)   │   │
│  │ 03:44:00 Drafting conclusion              │   │
│  └───────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

**Information gleaned**:
- On hypothesis v12 (progress over time)
- 84% complete (almost done)
- 3 patterns found (positive result)
- Currently drafting conclusion (final stage)

User clicks `[export to I-gent notes]` to capture this snapshot.

---

## Design Rationale: Why Not One Unified View?

### Attempted Unified Design (Rejected)

Imagine a single "Observation Agent" that tries to do both:

```
╔══ UNIFIED OBSERVER ══════════════════════════════════════╗
║                                                          ║
║  ┌─ Ecosystem View (I-gent) ────────────────────────┐   ║
║  │ ●A  ○B  ◐C  ●K                                   │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  ┌─ robin Details (W-gent) ──────────────────────────┐  ║
║  │ Current task: Hypothesis v3                       │  ║
║  │ Progress: 67%                                     │  ║
║  │ Events: [long list]                               │  ║
║  └──────────────────────────────────────────────────┘  ║
║                                                          ║
║  ┌─ analyze Details (W-gent) ─────────────────────────┐ ║
║  │ Current task: Parsing                             │ ║
║  │ Progress: 23%                                     │ ║
║  └──────────────────────────────────────────────────┘ ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

**Problems**:
1. **Information overload**: Too much detail at once
2. **Unclear purpose**: Is this for contemplation or debugging?
3. **Performance**: Rendering all agents' internals simultaneously
4. **Cognitive clash**: Archival + ephemeral in same view
5. **Export confusion**: What gets saved? Ecosystem state or agent logs?

### Separated Design (Adopted)

**I-gent**: One tab, ecosystem view, left open for hours
**W-gent**: Spawned on-demand, focused investigation, closed when done

User can have:
- **1 I-gent** (ecosystem) + **N W-gents** (agent internals) running concurrently
- Each W-gent on different port (8000, 8001, 8002...)
- I-gent coordinates via `[observe]` action

---

## Future Synergies

### Margin Note Auto-Export

W-gent could **automatically** export key events to I-gent:

```toml
# Config: ~/.kgents/config.toml
[wire.i-gent-integration]
auto_export_events = true
export_threshold = "WARN"  # Export WARN and ERROR to margin notes
```

**Effect**: Errors automatically appear in I-gent margin notes without manual export.

### I-gent Embedded Mini-Wire

I-gent could embed a **mini W-gent view** within the page:

```
╔══ robin ═════════════════════════════════════════════════╗
║                                                          ║
║  state: ● active                     t: 01:23:00         ║
║                                                          ║
║  ┌─ live preview (mini W-gent) ────────────────────────┐ ║
║  │ Current: Synthesizing v3 (67%)                      │ ║
║  │ Last: Queried PubMed (5 results)                    │ ║
║  └─────────────────────────────────────────────────────┘ ║
║                                                          ║
║  [observe (full)]  [invoke]  [compose]                   ║
╚══════════════════════════════════════════════════════════╝
```

**Benefit**: Glanceable detail without leaving I-gent.
**Caveat**: Adds complexity to I-gent (may violate simplicity principle).

### Timeline Integration

I-gent timeline view could **link to W-gent snapshots**:

```
┌─ robin timeline ──────────────────────────────────────────┐
│                                                           │
│  t=0        t=5        t=10       t=15       t=20   now   │
│  ├──────────┼──────────┼──────────┼──────────┼───────┤    │
│  ○          ◐          ●          ●          ●       ●    │
│             ↑                     ↑                       │
│         [observe]             [observe]                   │
│         (W-gent: v1)          (W-gent: v3)                │
└───────────────────────────────────────────────────────────┘
```

Click `[observe]` → Opens W-gent view of agent at that timestamp (if logged).

---

## Principle Alignment

### Tasteful
Both I-gent and W-gent have **clear, distinct purposes**. No overlap, no competition.

### Curated
Two agents, not twenty. Each justified, each excellent at its role.

### Ethical
Both respect privacy (localhost-only), transparency (show truth), agency (don't manipulate).

### Joy-Inducing
I-gent: Contemplative delight (garden metaphor)
W-gent: Debugging relief (instant clarity)

### Composable
I-gent `>>` W-gent (composition via `[observe]` action).

### Heterarchical
Neither controls the other. I-gent can spawn W-gent; W-gent can export to I-gent. Peer relationship.

### Generative
Both regenerable from spec. This document defines the composition.

---

## See Also

- [W-gent README](README.md) - W-gent specification
- [I-gent README](../i-gents/README.md) - I-gent specification
- [integration.md](integration.md) - Technical integration details
- [../principles.md](../principles.md) - Core design principles
