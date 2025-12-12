---
path: self/interface
status: active
progress: 80
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: [self/memory, self/cli-refactor]
session_notes: |
  Phase 1 COMPLETE: FluxApp, DensityField, FlowArrow, Earth theme (40 tests)
  Phase 2 COMPLETE: Registry, OgentPoller, XYZ health bars, animations (30 tests)
  Phase 3 COMPLETE: WIRE/BODY overlays, waveform, event stream, proprioception (31 tests)
  Phase 4 COMPLETE: Glitch system, AGENTESE HUD, void.* triggers (36 tests)
  Total: 137 tests pass, mypy clean
  App launches: `uv run python -m agents.i.app --demo`
  Key bindings: h/j/k/l navigate, w wire, b body, g glitch, q quit
  Next: Phase 5 - Polish & FD3 Bridge
---

# I-gent v2.5: The Semantic Flux

**AGENTESE Context:** `self.interface.*`
**Status:** Implementation Plan
**Date:** 2025-12-11
**Supersedes:** v1.0 (stigmergic garden), v2.0 draft (agent dungeon)

---

## Executive Summary

A complete overhaul of i-gents (Interface agents) with zero regard for backwards compatibility. The v1.0 implementation was "too poetic for its utility." The v2.0 draft over-corrected toward a "server rack" aesthetic (dungeon = rooms = pods = boxes).

**v2.5 is the synthesis:**
- A **semantic flux** interface—agents as currents of cognition, not rooms to visit
- High-density Unicode aesthetics (2025 terminal, not 1980s ASCII)
- Tightly integrated with W-gent, O-gent, Omega-gent, Psi-gent, and the full agent mesh
- Automatically compatible with ALL agents by design (AgentObservable protocol)
- The medium through which Omega proprioception and Psi metaphors become tangible
- **Glitch as feature**—the Accursed Share made visible

---

## Part I: The Critique of v2.0

### Critique 1: The "Server Rack" Fallacy

**The Problem:** The "Dungeon" layout (`[ G ] --- [ J ]`) visualizes agents as boxes. This mimics Kubernetes dashboards. But kgents agents aren't just computing—they are *thinking* and *perceiving*.

**The Upgrade:** Use block elements (Unicode) for fluidity. Agents are heatmaps of intent, not rectangles:

| State | Block Rendering | Meaning |
|-------|-----------------|---------|
| Idle | `░░░` | Low density, cool |
| Thinking | `▒▓█` | High density, pulsating |
| Hallucinating | `▚▚▚` | Dithered, glitch |
| Error | Zalgo corruption | The Accursed Share made visible |

### Critique 2: Discrete States vs. Analog Qualia

**The Problem:** Progress bars (`████░░`) are binary task completion indicators. They don't convey texture.

**The Upgrade:** Sparklines and waveforms:
- Logical processing → square/rigid waveform
- Creative/void operations → noisy/stochastic waveform
- **The shape of processing is visible**

### Critique 3: The Command Line is Separate

**The Problem:** The prompt (`[/] cmd`) is a distinct footer. This separates "viewing" from "acting."

**The Upgrade:** The Agentese HUD (Heads-Up Display):
- When you focus an agent, the prompt **emanates from that agent**
- Typing `world.house` draws a visible vector line from the agent into the `world` context
- The interface visualizes Category morphisms (arrows) as you type them

---

## Part II: Design Philosophy

### The Core Metaphor: Weather Radar, Not Dungeon Map

v1.0 was a static painting.
v2.0 was a map.
**v2.5 is a radar weather system.**

Agents are not rooms to visit—they are **currents of cognition** that you tune into.

```
  KGENTS v2.5  │  ⌬ FLUX: HIGH  │  ⏣ ENTROPY: STABLE
 ────────────────────────────────────────────────────────

      ╭── SCOPE: World ──╮
      │                  │
    ▒▒▓▓  G-gent         │     ░░░░░░
    ▓▓▓▓  (Grammar)      │     ░ J ░░  J-gent
    ▒▒▓▓                 │     ░░░░░░  (Waiting)
      │   ║              │        :
      │   ║ (70 t/s)     │        : (lazy link)
      ▼   ▼              │        ▼
    ██████████           │     ▄▄▄▄▄▄
    █ ROBIN  █━━━━━━━━━━━┷━━━━━█ S █  Summarizer
    ██████████                 ▀▀▀▀▀▀

    [ PROCESSING... ]
    ▰▰▰▰▱▱▱▱▱▱  Hypothesis synthesis

    >>> logos.invoke("concept.justice.refine")_
```

### Key Visual Innovations

1. **Link Thickness:** Connector style (`║` vs `:` vs `━`) denotes bandwidth/throughput
2. **Glyph Density:** Agent body changes texture based on CPU/context load
3. **Depth (Bokeh):** Dim colors for background agents; focus brings forward
4. **Processing Waveforms:** Shape reveals logical vs. creative work

### The Glitch Mechanic (Accursed Share)

When `void.*` is invoked or an agent fails:
- **Do not show a red error box**
- **Corrupt the rendering.** Briefly replace agent glyphs with Zalgo text or random characters
- **Why?** It makes the system feel organic and volatile. A glitch is more visceral than an error message. It respects the **Joy-Inducing** principle (surprise).

---

## Part III: The Qualia We're Chasing

These are the feelings the interface must evoke:

| Qualia | How Achieved |
|--------|--------------|
| **Joyous j/k anticipation** | Smooth 30fps updates; something visibly transforms as you navigate |
| **Creation satisfaction** | Agents visibly materialize when spawned |
| **Simplicity pleasure** | Single-keystroke actions; no modal hell |
| **Maker's pride** | Your composed pipeline glows when it runs |
| **Vicarious joy** | Watching sub-agents work is like watching children paint |

All require **immediate feedback loops** combined with **ownership/agency**.

---

## Part IV: Technical Architecture

### Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | **Textual** | Modern TUI, async, reactive, web-deployable |
| Animation | **30fps target** | Balances smoothness with CPU |
| Color Palette | **Deep earth tones + pink/purple** | Per Kent's preference |
| Web Mode | **High priority** | `textual serve` for browser access |
| State Persistence | **Core feature** | Cursor position, layouts saved |
| Sound | **None** | Silent operation |
| Terminal Support | **Modern only** | iTerm2, Alacritty, Windows Terminal |
| Expected Scale | **Up to 40 agents** | No heroic scaling needed |

### The Three Modes (Evolved)

#### 1. FLUX Mode (Default)

Navigate the semantic flux. Agents as currents.

```python
class FluxScreen(Screen):
    """
    The semantic weather map.

    Agents are rendered as density fields, not boxes.
    Connections are flow arrows with thickness = throughput.
    """

    BINDINGS = [
        ("h", "move_left", "Left"),
        ("j", "move_down", "Down"),
        ("k", "move_up", "Up"),
        ("l", "move_right", "Right"),
        ("enter", "focus_agent", "Focus"),
        ("w", "enter_wire", "Wire"),
        ("b", "enter_body", "Body"),
        ("p", "psi_insight", "Psi"),
        ("escape", "zoom_out", "Back"),
    ]
```

**Visual treatment:**
- Agents render as clusters of block elements based on activity
- Focus creates "spotlight" effect (brightness gradient)
- Idle agents drift toward edges (conceptual, not literal animation)

#### 2. WIRE Mode (W-gent Integration)

Deep-dive into event streams. Holds `w` to overlay, release to return.

```
┌─ WIRE: robin ──────────────────────────────────────────────────┐
│                                                                │
│  ┌─ Processing Waveform ─────────────────────────────────────┐ │
│  │ ╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮╭╮  (logical: square)               │ │
│  │ ╰╯╰╯╰╯╰╯╰╯╰╯╰╯╰╯╰╯╰╯╰╯╰╯                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─ Event Stream ────────────────────────────────────────────┐ │
│  │ 10:42:15 [search]    Querying PubMed...                  │ │
│  │ 10:42:18 [search]    15 papers found                      │ │
│  │ 10:42:20 [filter]    3 high-relevance                     │ │
│  │ 10:42:25 [synthesize] Drafting conclusion...              │ │
│  │ ▶ 10:42:30 [synthesize] Pattern detected: β-sheet        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  [j/k] scroll │ [f] follow │ [e] export │ [esc] back           │
└────────────────────────────────────────────────────────────────┘
```

**Question resolved:** W-gent embedding vs spawning → **Overlay mode** (hold key for overlay, release to return). Not a separate spawn, not a screen switch.

#### 3. BODY Mode (Omega-gent Integration)

Feel proprioception. Press `b` to enter.

```
┌─ BODY: robin ──────────────────────────────────────────────────┐
│                                                                │
│  MORPHOLOGY: Base() >> with_ganglia(3) >> with_vault("1Gi")   │
│                                                                │
│  ┌─ Proprioception ──────────────────────────────────────────┐ │
│  │                                                           │ │
│  │  strain:      ▓▓░░░░░░░░  28% (CPU)                       │ │
│  │  pressure:    ▓▓▓▓▓░░░░░  52% (Memory)                    │ │
│  │  reach:       ●●●        3 replicas                       │ │
│  │  temperature: ▓▓▓▓▓▓▓▓░░  healthy budget                  │ │
│  │  trauma:      none                                        │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                │
│  [View only. Route morphology changes through kgents CLI.]     │
└────────────────────────────────────────────────────────────────┘
```

**Resolved:** View only. Morphology modifications route through the hollow CLI.

---

## Part V: Integrations

### 5.1 Automatic Agent Compatibility

Every agent is automatically visible via protocol:

```python
class AgentObservable(Protocol):
    """Every agent must satisfy this to appear in I-gent."""

    @property
    def id(self) -> str: ...

    @property
    def phase(self) -> Phase: ...  # DORMANT, WAKING, ACTIVE, WANING, VOID

    @property
    def children(self) -> list[str]: ...  # Composition graph

    def summary(self) -> str: ...  # One-line status

    async def metrics(self) -> dict: ...  # For WIRE mode

    async def activity_level(self) -> float: ...  # 0.0-1.0 for density rendering
```

**Not opt-in.** If you're an agent in the ecosystem, you're in the flux.

### 5.2 O-gent Integration (XYZ Health)

Three-axis observation visualized inline:

```
X ▓▓▓▓▓▓▓░░░ telemetry: OK
Y ▓▓▓▓▓▓▓▓░░ semantic: OK
Z ▓▓▓▓▓▓░░░░ economic: WARN
```

**Polling:** ~2.2 seconds with jitter (per Kent's specification).

### 5.3 Psi-gent Integration (Metaphor Hints)

Press `p` on any composition to get metaphorical analysis:

```
┌─ Ψ insight ─────────────────────────────────────────────────────┐
│ robin → analyze → summarize                                     │
│                                                                 │
│ This composition is like: ASSEMBLY LINE                         │
│   robin = raw material intake                                   │
│   analyze = processing station                                  │
│   summarize = packaging                                         │
│                                                                 │
│ Bottleneck detected: analyze (backpressure high)                │
│ Suggestion: Add parallel processing lane (replicas)             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 D-gent Integration (Memory Garden)

Agents with D-gent symbionts show memory:

```
┌─ Memory Garden ───────────────────────────────────────────┐
│ ▓▓▓ 12 established facts (high trust)                    │
│ ▒▒  5 emerging patterns (growing)                        │
│ ░   3 new hypotheses (seeds)                             │
│ ▚   1 deprecated concept (composting)                    │
└───────────────────────────────────────────────────────────┘
```

### 5.5 L-gent Integration (Semantic Search)

Press `/` to search the lattice:

```
/ search: protein folding_

Results (by semantic similarity):
  ▓▓▓ robin/hypothesis-v3     0.92
  ▒▒  archive/protein-2024    0.87
  ░░  lib/bio-patterns        0.81
```

### 5.6 J-gent Integration (Promise Tree)

For lazy evaluation visualization:

```
○ summarize(report)
  ├─ ○ generate(hypothesis)
  │   └─ ● search(database)  ◀── evaluating
  └─ ○ validate(constraints)

Entropy budget: ▓▓▓▓▓▓░░░░ 60% remaining
```

---

## Part VI: The Agentese HUD

The groundbreaking feature: **prompts emanate from agents.**

When focused on `robin`:

```
    ██████████
    █ ROBIN  █──────────────────────────────────────►
    ██████████                                       │
                                                     │
                                                     ▼
    >>> logos.invoke("concept.justice.refine")_
                          │
                          └──────────────────► [concept.*]
```

Typing an AGENTESE path draws a **visible arrow** showing the morphism.

This visualizes Category Theory in real-time. The observer (you) sees the composition being constructed.

---

## Part VII: Color Palette

Deep earth tones with pink/purple accents (per Kent):

| Element | Color | Hex |
|---------|-------|-----|
| Background | Deep charcoal | `#1a1a1a` |
| Active agent | Warm amber | `#e6a352` |
| Dormant agent | Cool slate | `#4a4a5c` |
| Waking agent | Dusty rose | `#c97b84` |
| Waning agent | Muted sage | `#7d9c7a` |
| Void/Error | Deep purple | `#6b4b8a` |
| Connection high-throughput | Salmon pink | `#e88a8a` |
| Connection low-throughput | Muted violet | `#8b7ba5` |
| Focus highlight | Pale gold | `#f5d08a` |
| Text primary | Warm white | `#f5f0e6` |
| Text secondary | Dusty tan | `#b3a89a` |

---

## Part VIII: Implementation Phases

### Phase 1: Core Flux (First Priority)

**Deliverables:**
1. Textual app with FluxScreen
2. Agent graph as density field (block elements)
3. h/j/k/l navigation
4. Focus/zoom mechanics
5. State persistence (cursor, layout)

**Success Criteria:**
- Renders 40 agents smoothly at 30fps
- State survives session restart
- Block density changes with agent activity

### Phase 2: Live Data Integration

**Deliverables:**
1. Connect to real agent registry
2. O-gent XYZ meters (poll ~2.2s with jitter)
3. Activity-based density updates
4. Agent discovery/removal animations

**Success Criteria:**
- Shows actual running agents
- XYZ bars reflect real O-gent observations
- New agents materialize visually

### Phase 3: Overlay Modes

**Deliverables:**
1. WIRE overlay (hold `w`)
2. BODY overlay (press `b`)
3. Event stream scrolling
4. Waveform visualization (logical vs. creative)

**Success Criteria:**
- Overlays feel instantaneous
- Can watch agent internals live
- Waveform shape differs by operation type

### Phase 4: The Glitch & HUD

**Deliverables:**
1. Glitch rendering on `void.*` or error
2. AGENTESE HUD with visible morphism arrows
3. Psi-gent metaphor hints (`p`)
4. L-gent semantic search (`/`)

**Success Criteria:**
- Glitches feel organic, not broken
- Morphism arrows draw as you type
- Metaphors are insightful

### Phase 5: Polish

**Deliverables:**
1. Web deployment via `textual serve`
2. D-gent memory garden visualization
3. J-gent promise tree
4. Full keyboard help overlay
5. Session state (window layouts)

---

## Part IX: What We Delete from v1.0

| v1.0 Feature | Status | Reason |
|--------------|--------|--------|
| Stigmergic pheromone traces | **Delete** | Overly abstract |
| Brownian motion simulation | **Delete** | Visual noise |
| Heat/entropy metaphors | **Delete** | Replaced by O-gent metrics |
| The compost heap metaphor | **Delete** | O-gent error tracking is better |
| Breath indicator | **Delete** | Too subtle; explicit activity instead |
| Semantic/Topological/Physical layers | **Delete** | Flattened into flux |
| Moon phase cycling animation | **Simplify** | Phases exist as static indicators |
| 5-level hierarchy (glyph→card→page→garden→library) | **Delete** | Too much ceremony |

**Keep:**
- Phase symbols (●○◐◑◌)
- Keyboard-first navigation
- Monochrome legibility requirement
- Export to markdown
- W-gent synergy concept (reimplemented)

---

## Part X: Questions Resolved

| Question | Answer | Rationale |
|----------|--------|-----------|
| Textual vs Pure Rich? | **Textual** | Async reactive model |
| Web mode priority? | **High** | `textual serve` for browser |
| State persistence? | **Core feature** | Essential for continuity |
| W-gent embedding vs spawning? | **Overlay mode** | Hold key for overlay |
| O-gent polling frequency? | **~2.2s with jitter** | Kent's specification |
| Can I-gent modify morphology? | **View only** | Route through hollow CLI |
| Animation budget? | **30fps** | Kent's specification |
| Color palette? | **Deep earth + pink/purple** | Kent's preference |
| Sound? | **None** | Silent operation |
| Scale handling? | **Up to 40 agents** | No heroic scaling |
| Legacy terminal? | **Unnecessary** | Modern terminals only |

---

## Part XI: Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Block element rendering inconsistency | Medium | Medium | Test across terminal emulators |
| Overlay mode complexity | Medium | Medium | Start with single overlay, iterate |
| Glitch rendering UX | Low | Low | Make glitch duration short (~200ms) |
| HUD arrow rendering | Medium | Medium | Prototype early |
| Waveform CPU cost | Low | Low | Only compute for focused agent |

---

## Part XII: Files

```
impl/claude/agents/i/
├── __init__.py
├── app.py              # Main Textual Application
├── screens/
│   ├── flux.py         # FLUX mode (default)
│   └── overlays/
│       ├── wire.py     # WIRE overlay
│       └── body.py     # BODY overlay
├── widgets/
│   ├── density_field.py   # Agent as density cluster
│   ├── flow_arrow.py      # Connection with throughput
│   ├── waveform.py        # Processing waveform
│   ├── xyz_meter.py       # O-gent health bars
│   ├── glitch.py          # Glitch effect renderer
│   ├── agentese_hud.py    # Path completion with arrows
│   └── memory_garden.py   # D-gent visualization
├── data/
│   ├── registry.py     # Agent registry connection
│   ├── ogent.py        # O-gent polling
│   └── state.py        # Session persistence
├── theme/
│   └── earth.py        # Deep earth + pink/purple palette
└── _tests/
    ├── test_flux.py
    ├── test_overlays.py
    └── test_glitch.py
```

---

## Appendix A: Visual Vocabulary (v2.5)

### Agent Density Rendering

```
Idle:       ░░░░░░  (light shade, sparse)
Waking:     ░▒▒░░░  (transitioning)
Active:     ▒▓▓▒▒▒  (medium-high density)
Intense:    ▓▓██▓▓  (full blocks, pulsing)
Void/Error: ▚▞▚▞▚▞  (dithered glitch)
```

### Connection Bandwidth

```
High throughput:    ════════  (double line, thick)
Medium throughput:  ────────  (single line)
Low throughput:     ........  (dotted)
Lazy/Promise:       : : : :   (sparse dots)
```

### Waveform Shapes

```
Logical processing:   ╭╮╭╮╭╮╭╮╭╮ (square wave)
Creative/void:        ~∿~∿~∿~∿~ (noisy sine)
Waiting:              ────────── (flat line)
```

---

## Appendix B: Principles Alignment

| Principle | How I-gent v2.5 Aligns |
|-----------|------------------------|
| **Tasteful** | Single purpose: semantic flux visualization |
| **Curated** | Block elements only—no ASCII cruft |
| **Ethical** | View-only mode; no hidden modifications |
| **Joy-Inducing** | Glitch as feature; processing waveforms; HUD arrows |
| **Composable** | AgentObservable protocol; overlays compose |
| **Heterarchical** | No fixed agent hierarchy; flux is flat |
| **Generative** | Config-driven themes; state-driven layouts |
| **AGENTESE** | HUD visualizes morphisms as you type |
| **Accursed Share** | Glitch mechanic celebrates entropy |
| **Personality Space** | Color palette creates emotional register |

---

*"The interface is not a window—it is the weather."*
