---
path: interfaces/dashboard-overhaul
status: proposed
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [interfaces/interaction-flows, interfaces/swarm-execution]
session_notes: |
  Strategic overhaul of kgents dashboard.
  Synthesizes Alethic Workbench primitives with 5-screen architecture.
  Incorporates Turn-gents, polynomial agents, and trace monoid.

  Key insight: The dashboard is a Perspective Functor over the System Presheaf.
  The same data renders differently based on LOD, focus, and time slice.
---

# Dashboard Overhaul: The Unified Interface

> *"The interface is not a window—it is a membrane. Through it, we touch the agents."*

**Status**: Proposed (synthesizes Alethic Workbench completion with strategic overhaul)
**Principle Alignment**: All seven + Accursed Share
**Prerequisites**: All 17 primitives complete (988 tests passing)

---

## Executive Summary

This spec defines a **complete rebuild** of the kgents dashboard with:

1. **5 New Screens** at 3 detail levels + Forge + Debugger
2. **Precise Interaction Flows** optimized for developer joy
3. **Integration** with Turn-gents, polynomial agents, trace monoid
4. **Multi-Agent Execution Strategy** for parallel implementation

The dashboard transforms from a monitoring tool to a **cognitive membrane**—an interface that makes agent thought visible and manipulable.

---

## Part 1: The Five Screens

### Screen Architecture

```
                    ┌─────────────────────────────────────┐
                    │          OBSERVATORY                │  LOD -1: ORBITAL
                    │      (Ecosystem overview)           │  All gardens, all agents
                    └──────────────┬──────────────────────┘
                                   │ Enter/+
                                   ▼
                    ┌─────────────────────────────────────┐
                    │          TERRARIUM                  │  LOD 0: SURFACE
                    │      (Garden with agents)           │  Multi-agent field
                    └──────────────┬──────────────────────┘
                                   │ Enter/+
                                   ▼
                    ┌─────────────────────────────────────┐
                    │          COCKPIT                    │  LOD 1: OPERATIONAL
                    │      (Single agent control)         │  Direct manipulation
                    └──────────────┬──────────────────────┘
                                   │ Enter/+
                                   ▼
                    ┌─────────────────────────────────────┐
                    │          DEBUGGER                   │  LOD 2: FORENSIC
                    │      (Deep trace analysis)          │  Turn DAG + cone
                    └─────────────────────────────────────┘

                    ┌─────────────────────────────────────┐
                    │          FORGE                      │  SPECIAL: CREATION
                    │      (Build/simulate agents)        │  Composition + test
                    └─────────────────────────────────────┘
```

### Screen 1: Observatory (LOD -1)

**Purpose**: Ecosystem-level view. All gardens, all agents at a glance.

**Primitives Used**: P1 (DensityField), P2 (Sparkline), P5 (GraphLayout), P13 (Card)

**Layout**:
```
┌─ OBSERVATORY ──────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌─ GARDEN: main ────────────────┐  ┌─ GARDEN: experiment-α ─────────┐ │
│  │                                │  │                                │ │
│  │  ●K ─── ●A ─── ○D              │  │  ◐robin ─── ○test              │ │
│  │         │      │               │  │     │                          │ │
│  │         ●L ─── ◐E              │  │     ○valid                     │ │
│  │                                │  │                                │ │
│  │  ▁▂▃▄▅▆▇█▇▆  health: 80%      │  │  ▁▁▂▃▂▁▁▁  health: 45%        │ │
│  │  flux: 2.3 ev/s                │  │  flux: 0.4 ev/s                │ │
│  └────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                         │
│  ══════════════════════════════════════════════════════════════════════ │
│                                                                         │
│  ORCHESTRATION: ●converging     BREATH: ░░████░░░░    AGENTS: 7        │
│                                                                         │
│  ┌─ VOID (Accursed Share) ───────────────────────────────────────────┐ │
│  │  Entropy budget: ██░░░░░░ 25%  │  Suggestion: "Honor thy error"   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  [Tab] cycle  [Enter] zoom  [f] forge  [d] debugger  [?] help          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Interactions**:
| Input | Action | Result |
|-------|--------|--------|
| Tab | Cycle focus | Highlight next garden |
| Enter | Zoom in | → Terrarium for focused garden |
| + | Zoom to agent | → Cockpit for focused agent |
| f | Open Forge | → Forge screen |
| d | Open Debugger | → Debugger for focused agent |
| g | Toggle graph | Switch between semantic/tree layout |
| Space | Emergency brake | Pause all flux streams |

**Data Sources**:
- Garden list from `FluxState.gardens`
- Agent glyphs from `AgentSnapshot.phase`
- Health from `TraceMonoid.health_metric()`
- Orchestration from `PolyAgent.current_mode`

---

### Screen 2: Terrarium (LOD 0) — Enhanced

**Purpose**: Multi-agent view with stigmergic field dynamics.

**Primitives Used**: P1, P4 (FlowArrow), P5, P8 (Waveform), P9 (GlitchEffect), P10 (EntropyVisualizer)

**Layout**:
```
┌─ TERRARIUM: main ────────────────────────────────────────────────────────┐
│                                                                           │
│  [ENTROPY ████████████░░░░░░] 72%      [HEAT ███████░░░░░░░░░░░] 35%     │
│                                                                           │
│  ┌─ FIELD ─────────────────────────────────────────────────────────────┐ │
│  │                                                                      │ │
│  │       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░░░▒▒▒▓▓▓K▓▓▓▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░░░░░░▒═══════▒░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░░░░░░║░░░░░░░║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░▒▒▒▓A▓▒▒╝░░░░░░░╚▒▒▒▓L▓▒▒░░░░░░░░░░░*task░░░░░░░        │ │
│  │       ░░░░░░░░▒║▒░░░░░░░░░░░░░░░║░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░║░░░░░░░░░░░░░░░░║░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░▒▒▓D▓╝░░░░░░░░░░░░▒▒▓E▓▒▒░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  PHASE: ●FLUX          FOCUS: [K-gent]          TURN RATE: 3.2/s         │
│                                                                           │
│  ┌─ SUB-VIEW ───────────────────────────────────────────────────────────┐ │
│  │  [1]FIELD  [2]TRACES  [3]FLUX  [4]TURNS                              │ │
│  │                                                                       │ │
│  │  Recent AGENTESE invocations:                                         │ │
│  │  ├─ self.soul.challenge ("singleton") → ACCEPT      [12ms]           │ │
│  │  ├─ world.cortex.invoke (claude-3) → success        [1.2s]           │ │
│  │  └─ void.entropy.tithe (0.05) → discharged          [<1ms]           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  [+] cockpit  [-] observatory  [f] forge  [t] loom  [Space] pause        │
└───────────────────────────────────────────────────────────────────────────┘
```

**Sub-Views** (toggle with 1-4):
1. **FIELD** — Spatial layout with pheromone density (default)
2. **TRACES** — Recent AGENTESE path invocations
3. **FLUX** — Event stream with throughput graph
4. **TURNS** — Turn-gents summary (counts by type)

**New Features**:
- Pheromone visualization (density gradients)
- Task attractors (gravity wells shown as `*task`)
- Entropy-aware borders (dissolve when uncertain)
- Turn rate indicator

---

### Screen 3: Cockpit (LOD 1) — Enhanced

**Purpose**: Single-agent operational control with polynomial state.

**Primitives Used**: P1, P2, P8, P10, P11 (Slider), P6 (BranchTree preview)

**New Panels**:

```
┌─ POLYNOMIAL STATE ─────────────────────────────────────────────────────┐
│                                                                         │
│  Mode: DELIBERATING                                                     │
│                                                                         │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐      │
│  │ GROUNDING│ ──▶ │DELIBERAT │ ──▶ │ JUDGING  │ ──▶ │ COMPLETE │      │
│  │    ●     │     │    ●     │     │    ○     │     │    ○     │      │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘      │
│       ↑                                                                │
│       └─────────────── [restart] ──────────────────────────────────────│
│                                                                         │
│  Valid inputs: [Claim, Evidence, Objection]                            │
│  State hash: 7a3f...                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ TURN PREVIEW (last 5) ────────────────────────────────────────────────┐
│                                                                         │
│  ● SPEECH "I'll analyze the structure..."                     -2s      │
│  ● ACTION world.grep.invoke                                   -5s      │
│  ○ THOUGHT "Filter by relevance..."                           -8s      │
│  ● SPEECH "Found 47 matches"                                  -12s     │
│  ● ACTION self.memory.store                                   -15s     │
│                                                                         │
│  [d] full debugger  [t] loom                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─ YIELD QUEUE ──────────────────────────────────────────────────────────┐
│                                                                         │
│  Pending approvals: 2                                                   │
│                                                                         │
│  ⏳ [1] "Execute rm -rf?" (YIELD:ACTION)              [a]pprove [r]eject│
│  ⏳ [2] "Publish to npm?" (YIELD:ACTION)              [a]pprove [r]eject│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Polynomial Integration**:
- Show current mode in state machine
- Visualize valid transitions
- Display state hash for debugging
- Enable mode forcing (dev only)

**Turn Preview**:
- Last 5 turns with type badges
- Relative timestamps
- Quick navigation to Debugger

**Yield Queue**:
- Pending YIELD turns awaiting approval
- Inline approve/reject actions
- Count badge in header

---

### Screen 4: Forge (SPECIAL)

**Purpose**: Agent creation, composition, simulation, refinement.

**Primitives Used**: P5, P11, P12 (Button), P13, P14 (Grid), P15 (Overlay)

**Layout**:
```
┌─ FORGE ─────────────────────────────────────────────────────────────────┐
│                                                                          │
│  MODE: [●compose] [○simulate] [○refine] [○export]                       │
│                                                                          │
│  ┌─ PALETTE ────────────────────┐  ┌─ PIPELINE ────────────────────────┐│
│  │                               │  │                                   ││
│  │  AGENTS                       │  │    ┌───────────────┐              ││
│  │  ──────                       │  │    │   Ground      │ (primitive)  ││
│  │  [A] Alethic     ★★★★        │  │    │   "claim"     │              ││
│  │  [B] Bio         ★★★★        │  │    └───────┬───────┘              ││
│  │  [D] Data        ★★          │  │            │                       ││
│  │  [E] Evolution   ★★★         │  │            ▼                       ││
│  │  [K] Soul        ★★★★★       │  │    ┌───────────────┐              ││
│  │  [L] Lattice     ★★★         │  │    │   K-gent      │ (persona)    ││
│  │                               │  │    │   temp=0.7    │              ││
│  │  PRIMITIVES                   │  │    └───────┬───────┘              ││
│  │  ──────────                   │  │            │                       ││
│  │  [g] Ground      ○            │  │            ▼                       ││
│  │  [j] Judge       ○            │  │    ┌───────────────┐              ││
│  │  [s] Sublate     ○            │  │    │   Judge       │ (verdict)   ││
│  │  [c] Contradict  ○            │  │    │               │              ││
│  │  [f] Fix         ○            │  │    └───────────────┘              ││
│  │                               │  │                                   ││
│  │  [Enter] add to pipeline →    │  │  ════════════════════════════    ││
│  │  [x] remove selected          │  │  Entropy cost: 0.15/turn         ││
│  │                               │  │  Token budget: ~2,400             ││
│  └───────────────────────────────┘  └───────────────────────────────────┘│
│                                                                          │
│  ┌─ SIMULATION ──────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Status: READY                                                     │  │
│  │                                                                    │  │
│  │  Input:  [Enter claim to test: _________________________________] │  │
│  │                                                                    │  │
│  │  Output: (awaiting input)                                          │  │
│  │                                                                    │  │
│  │  [Enter] run  │  [s] step  │  [r] reset  │  [Tab] switch focus    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  [Esc] back  │  [e] export to code  │  [?] help                         │
└──────────────────────────────────────────────────────────────────────────┘
```

**Modes**:

| Mode | Purpose | Key Interactions |
|------|---------|------------------|
| **compose** | Build pipelines | Enter to add, x to remove, arrows to navigate |
| **simulate** | Test with input | Enter to run, s to step, r to reset |
| **refine** | Iterate on failures | Select failed case, adjust parameters |
| **export** | Generate code | Preview Python, copy to clipboard |

**Pipeline Semantics**:
- Agents compose via `>>=` (Kleisli composition)
- Show composition edges
- Estimate entropy cost per turn
- Validate type compatibility

---

### Screen 5: Debugger (LOD 2)

**Purpose**: Deep forensic analysis with Turn DAG and causal cones.

**Primitives Used**: P6, P7 (Timeline), P9, P10, TurnDAGRenderer

**Layout**:
```
┌─ DEBUGGER: K-gent ──────────────────────────────────────────────────────┐
│                                                                          │
│  MODE: [●forensic] [○replay] [○diff]     TIME: -2m 34s → now            │
│                                                                          │
│  ┌─ TURN DAG ────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  Turns by K-gent (12 visible, 8 thoughts collapsed)               │  │
│  │                                                                    │  │
│  │     ● SPEECH "I'll analyze the code"                     -3m      │  │
│  │        │                                                          │  │
│  │        ├─● ACTION world.grep.invoke                      -2m 50s  │  │
│  │        │     │                                                    │  │
│  │        │     └─● SPEECH "Found 47 matches"               -2m 40s  │  │
│  │        │           │                                              │  │
│  │        │           └─○ THOUGHT "Filter by relevance..." [+3]      │  │
│  │        │                │                                         │  │
│  │        │                └─● ACTION self.memory.store     -2m 20s  │  │
│  │        │                     │                                    │  │
│  │        │                     └─● SPEECH "Stored 12 items" -2m 10s │  │
│  │        │                                                          │  │
│  │        └─○ [GHOST] ACTION world.ast.parse (rejected)     -2m 50s  │  │
│  │              └─ reasoning: "grep faster for this case"            │  │
│  │                                                                    │  │
│  │  [j/k] navigate  [t] toggle thoughts  [g] toggle ghosts           │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─ CAUSAL CONE ────────────┐  ┌─ STATE DIFF ──────────────────────┐   │
│  │                          │  │                                    │   │
│  │  Context for K-gent:     │  │  Turn: SPEECH → ACTION             │   │
│  │                          │  │                                    │   │
│  │  ● K-gent     (5 turns)  │  │  phase: GROUNDING → JUDGING       │   │
│  │    ├ world.grep (1)      │  │  confidence: 0.72 → 0.85 (+18%)   │   │
│  │    └ self.memory (1)     │  │  entropy: 0.12 → 0.15 (+0.03)     │   │
│  │                          │  │                                    │   │
│  │  Total: 7 turns          │  │  memory.keys: +1 ("analysis")     │   │
│  │  Compression: 58%        │  │  semaphores: +0 -0                │   │
│  │                          │  │                                    │   │
│  │  [c] highlight cone      │  │  [Tab] cycle turns                │   │
│  └──────────────────────────┘  └────────────────────────────────────┘   │
│                                                                          │
│  ┌─ TIMELINE ────────────────────────────────────────────────────────┐  │
│  │  t=-5m       t=-4m       t=-3m       t=-2m       t=-1m       now  │  │
│  │  │───────────│───────────│───────────│───────────│───────────│   │  │
│  │  ○           ○           ●           ●           ●           ●   │  │
│  │  init        warmup      analyze     process     store       *   │  │
│  │                                          ▲                        │  │
│  │                                       cursor                      │  │
│  │                                                                    │  │
│  │  [◀ rewind]  [▶ step]  [f] fork from cursor  [x] export trace    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  [Esc] back  │  [l] loom  │  [?] help                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Modes**:

| Mode | Purpose | Features |
|------|---------|----------|
| **forensic** | Investigate past | Full DAG, cone, diff |
| **replay** | Step through history | Time-travel, watch state |
| **diff** | Compare two points | Side-by-side state comparison |

**Turn DAG Features**:
- Render via `TurnDAGRenderer`
- Thought collapse (toggle with `t`)
- Ghost branches visible (toggle with `g`)
- Dependency edges shown
- YIELD status indicators (✓ approved, ⏳ pending)

**Causal Cone Features**:
- Show what agent could see at cursor position
- Group by source (agent, world, self)
- Compression ratio (context efficiency)
- Highlight with `c`

**State Diff Features**:
- Compare state between any two turns
- Show changes in phase, confidence, entropy
- Memory delta (keys added/removed)
- Semaphore changes

**Timeline Features**:
- Horizontal scrubber
- Major events labeled
- Cursor position
- Rewind/step controls
- Fork creates new Weave from cursor

---

## Part 2: The Three Detail Levels

All screens support consistent LOD transitions:

| Level | Name | What Shows | Navigation |
|-------|------|------------|------------|
| **-1** | ORBITAL | Glyphs, gardens as cards | Observatory |
| **0** | SURFACE | Cards with metrics, field | Terrarium |
| **1** | OPERATIONAL | Full panels, controls | Cockpit |
| **2** | FORENSIC | Raw state, traces | Debugger |

**Transition Keys**:
- `+` or `Enter`: Zoom in (increase detail)
- `-` or `Esc`: Zoom out (decrease detail)

**Smooth Transitions**:
- Animate card → panel expansion
- Preserve scroll position
- Maintain focus on same agent

---

## Part 3: Integration Points

### 3.1 Polynomial Agent Integration

```python
# Cockpit shows polynomial state
class CockpitScreen:
    def compose_polynomial_panel(self) -> ComposeResult:
        agent = self.get_polynomial_agent()
        if agent:
            yield PolynomialStateWidget(
                mode=agent.current_mode,
                valid_inputs=agent.valid_inputs(),
                state_hash=agent.state_hash(),
                transition_history=agent.transitions[-5:],
            )
```

### 3.2 Turn-gents Integration

```python
# Debugger uses TurnDAGRenderer
class DebuggerScreen:
    def compose_turn_dag(self) -> ComposeResult:
        renderer = TurnDAGRenderer(
            weave=self.weave,
            config=TurnDAGConfig(
                show_thoughts=self.show_thoughts,
                highlight_cone=True,
            ),
        )
        yield TurnDAGWidget(renderer=renderer, agent_id=self.agent_id)
```

### 3.3 TraceMonoid Integration

```python
# Timeline uses TraceMonoid linearization
class TimelineWidget:
    def get_ordered_events(self) -> list[Turn]:
        monoid = self.weave.monoid
        # Get valid linearization respecting dependencies
        return monoid.linearize()

    def get_concurrent_events(self, turn_id: str) -> set[str]:
        braid = self.weave.braid()
        return braid.get_concurrent(turn_id)
```

### 3.4 AGENTESE Integration

```python
# Terrarium shows AGENTESE traces
class TerrariumScreen:
    def compose_traces_subview(self) -> ComposeResult:
        traces = self.get_recent_traces()
        for trace in traces[-10:]:
            yield AGENTESETraceRow(
                path=trace.path,
                result=trace.result,
                duration=trace.duration,
            )
```

---

## Part 4: Visual Grammar Consistency

### Phase Symbols (Universal)

| Symbol | Phase | Meaning | Color |
|--------|-------|---------|-------|
| ○ | DORMANT | Sleeping | dim gray |
| ◐ | WAKING | Initializing | warm yellow |
| ● | ACTIVE | Processing | bright gold |
| ◑ | WANING | Cooling | muted amber |
| ◌ | VOID | Error/entropy | purple glitch |

### Turn Type Badges

| Badge | Type | Color |
|-------|------|-------|
| SPEECH | Agent output | green |
| ACTION | World interaction | blue |
| THOUGHT | Internal | dim (collapsed) |
| YIELD | Awaiting approval | yellow |
| SILENCE | No-op | dim italic |

### Connection Styles

| Pattern | Meaning |
|---------|---------|
| `═══►` | High throughput |
| `───►` | Normal flow |
| `···►` | Low/pending |
| `- - ►` | Ghost (rejected) |

---

## Part 5: The Accursed Share Panel

Every screen reserves space for the Void:

```
┌─ VOID (Accursed Share) ───────────────────────────────────────────────┐
│                                                                        │
│  Entropy budget: ██████░░░░ 60%                                       │
│  Last tithe: 3m ago                                                   │
│  System temperature: 0.72                                              │
│                                                                        │
│  Oblique Strategy: "Honor thy error as a hidden intention"            │
│                                                                        │
│  [v] invoke void.entropy.sip                                          │
└────────────────────────────────────────────────────────────────────────┘
```

**Purpose**:
- Display entropy budget remaining
- Show last tithe (gratitude payment)
- Surface Oblique Strategies when entropy > 0.9
- Enable manual entropy operations

---

## Part 6: Principle Compliance

| Principle | How This Spec Complies |
|-----------|------------------------|
| **Tasteful** | 5 screens, each justified; no feature bloat |
| **Curated** | Fixed taxonomy; primitives, not plugins |
| **Ethical** | All state visible; ghosts shown; no hidden data |
| **Joy-Inducing** | Smooth zoom; heartbeat pulse; Oblique Strategies |
| **Composable** | Primitives compose; screens are functors |
| **Heterarchical** | No fixed entry; navigate freely; agents guide |
| **Generative** | 17 primitives → infinite compositions |
| **Accursed Share** | VOID panel; serendipity honored |
| **AGENTESE** | Traces panel; observer context shapes view |

---

## Part 7: Anti-Patterns

**MUST NOT**:
1. Have a "settings" screen (configure via code)
2. Require mouse for any operation
3. Hide ghost branches by default
4. Use color as sole differentiator
5. Block on slow operations
6. Accumulate panels without justification

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Alethic Workbench | `plans/interfaces/alethic-workbench.md` |
| Primitives | `plans/interfaces/primitives.md` |
| Implementation Roadmap | `plans/interfaces/implementation-roadmap.md` |
| Interaction Flows | `plans/interfaces/interaction-flows.md` |
| Swarm Execution | `plans/interfaces/swarm-execution.md` |
| Turn-gents | `plans/architecture/turn-gents.md` |
| Polynomial Agents | `plans/skills/polynomial-agent.md` |
| TraceMonoid | `impl/claude/weave/trace_monoid.py` |
| I-gent Screens | `impl/claude/agents/i/screens/` |

---

*"What you can see, you can tend. What you can navigate, you can understand. What you can fork, you can debug."*
