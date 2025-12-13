---
path: interfaces/interaction-flows
status: proposed
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Precise interaction flows for the dashboard overhaul.
  Each flow designed to minimize friction and maximize developer joy.
  Follows spec/principles.md: tasteful, heterarchical, joy-inducing.
---

# Interaction Flows: The User Journey

> *"The best interface is the one that disappears."*

This document specifies **precise interaction flows** that guide users through common tasks. Each flow is designed for:

1. **Minimal keystrokes** — Achieve goals quickly
2. **Consistent grammar** — Same keys, same effects
3. **Recoverable state** — Undo and escape always work
4. **Progressive disclosure** — Simple by default, powerful when needed

---

## Flow 1: Morning Health Check

**Goal**: Quickly assess system health across all gardens.

**Entry**: `kgents dashboard` or `kg d`

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Morning Health Check                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Dashboard opens at OBSERVATORY                                      │
│     └─ See all gardens at once                                          │
│     └─ Health bars visible: ████████░░ 80%                              │
│                                                                         │
│  2. Scan health indicators                                              │
│     └─ GREEN: All healthy                                               │
│     └─ AMBER: Investigate needed (proceed to step 3)                    │
│     └─ RED: Critical (proceed to step 4)                                │
│                                                                         │
│  3. [Tab] to cycle focus to amber garden                                │
│     └─ Press [Enter] to zoom into Terrarium                             │
│     └─ Sub-view shows recent traces                                     │
│     └─ Identify slow paths or errors                                    │
│                                                                         │
│  4. For critical issues:                                                │
│     └─ [+] zoom to specific agent                                       │
│     └─ [d] open Debugger directly                                       │
│     └─ Investigate Turn DAG for failure                                 │
│                                                                         │
│  5. [Esc] repeatedly to return to Observatory                           │
│     └─ Or [q] to quit                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| Tab | Cycle focus between gardens |
| Enter | Zoom into focused garden |
| + | Zoom to focused agent |
| d | Jump to Debugger |
| Esc | Zoom out one level |
| q | Quit |

**Time to Complete**: < 30 seconds for healthy system

---

## Flow 2: Deep Debug a Failing Agent

**Goal**: Investigate why an agent failed or produced unexpected output.

**Entry**: From any screen, focus agent + press `d`

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Deep Debug                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Enter Debugger for target agent                                     │
│     └─ [d] from any screen with agent focused                           │
│     └─ Or: Observatory → Terrarium → Cockpit → [+] to Debugger          │
│                                                                         │
│  2. Orient in Turn DAG                                                  │
│     └─ DAG shows recent turns                                           │
│     └─ Look for [GHOST] branches (rejected paths)                       │
│     └─ Look for anomalies in turn sequence                              │
│                                                                         │
│  3. Enable thought visibility                                           │
│     └─ [t] toggle thoughts                                              │
│     └─ Collapsed thoughts expand: [+3] → shows 3 thought turns          │
│     └─ Often reveals reasoning errors                                   │
│                                                                         │
│  4. Navigate to failure point                                           │
│     └─ [j/k] move through turn history                                  │
│     └─ Watch STATE DIFF panel for unexpected changes                    │
│     └─ Cursor position shows in timeline                                │
│                                                                         │
│  5. Examine causal cone                                                 │
│     └─ [c] highlight causal cone                                        │
│     └─ Shows what agent "could see" at that turn                        │
│     └─ Missing context often explains bad decisions                     │
│                                                                         │
│  6. Fork for experimentation                                            │
│     └─ Navigate to turn before failure                                  │
│     └─ [f] fork from cursor                                             │
│     └─ Creates new Weave for "what if" testing                          │
│                                                                         │
│  7. Export trace for sharing                                            │
│     └─ [x] export trace                                                 │
│     └─ Generates Markdown with full turn history                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| d | Enter Debugger |
| j/k | Navigate turns (down/up) |
| h/l | Navigate branches (for Loom) |
| t | Toggle thought visibility |
| g | Toggle ghost branches |
| c | Highlight causal cone |
| f | Fork from cursor |
| x | Export trace |
| Esc | Back to previous screen |

**Pro Tips**:
- Ghost branches often reveal "what the agent almost did"
- State diff between YIELD and next turn shows approval effects
- Concurrent turns (shown same column) indicate independence

---

## Flow 3: Build a New Agent Pipeline

**Goal**: Compose agents into a new pipeline and test it.

**Entry**: `f` from any screen, or `kgents forge`

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Build Agent Pipeline                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Enter Forge in compose mode (default)                               │
│     └─ Left panel: Palette of available agents/primitives               │
│     └─ Right panel: Pipeline being built                                │
│                                                                         │
│  2. Add first stage                                                     │
│     └─ Navigate palette with [j/k]                                      │
│     └─ [Enter] adds selected to pipeline                                │
│     └─ Or press letter shortcut: [g] for Ground                         │
│                                                                         │
│  3. Build pipeline                                                      │
│     └─ Add stages sequentially                                          │
│     └─ Pipeline shows composition edges                                 │
│     └─ Bottom shows estimated costs:                                    │
│        └─ Entropy cost: 0.15/turn                                       │
│        └─ Token budget: ~2,400                                          │
│                                                                         │
│  4. Configure stages (optional)                                         │
│     └─ [Tab] to switch focus to pipeline                                │
│     └─ [j/k] to select stage                                            │
│     └─ [Enter] opens configuration overlay                              │
│     └─ Adjust temperature, model, etc.                                  │
│                                                                         │
│  5. Switch to simulate mode                                             │
│     └─ [2] or navigate to [simulate] tab                                │
│     └─ Input field becomes active                                       │
│                                                                         │
│  6. Test the pipeline                                                   │
│     └─ Type test input                                                  │
│     └─ [Enter] runs simulation                                          │
│     └─ Output panel shows result                                        │
│     └─ [s] to step through pipeline stages                              │
│                                                                         │
│  7. Iterate in refine mode                                              │
│     └─ [3] switches to refine mode                                      │
│     └─ Failed cases listed                                              │
│     └─ Select case, adjust pipeline, re-test                            │
│                                                                         │
│  8. Export when satisfied                                               │
│     └─ [4] switches to export mode                                      │
│     └─ Shows generated Python code                                      │
│     └─ [y] copies to clipboard                                          │
│     └─ [w] writes to file                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| f | Enter Forge |
| j/k | Navigate list |
| Enter | Add/configure |
| Tab | Switch focus (palette ↔ pipeline ↔ simulation) |
| x | Remove selected stage |
| 1-4 | Switch mode (compose/simulate/refine/export) |
| s | Step through simulation |
| r | Reset simulation |
| y | Copy code to clipboard |
| w | Write code to file |
| Esc | Back |

**Composition Rules**:
- Agents compose left-to-right (output of A → input of B)
- Type mismatches shown with warning
- Invalid compositions blocked with explanation

---

## Flow 4: Approve Pending Yields

**Goal**: Review and approve agent YIELD requests.

**Entry**: Cockpit screen shows badge when yields pending

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Approve Yields                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Notice yield badge in Cockpit                                       │
│     └─ Header shows: "YIELDS: 2 pending"                                │
│     └─ Or notification: "K-gent requests approval"                      │
│                                                                         │
│  2. Focus yield queue                                                   │
│     └─ [Tab] cycles to YIELD QUEUE panel                                │
│     └─ Or [y] jumps directly to yields                                  │
│                                                                         │
│  3. Review each yield                                                   │
│     └─ [j/k] to select yield                                            │
│     └─ Selected yield shows full details:                               │
│        └─ Turn content                                                  │
│        └─ Agent reasoning                                               │
│        └─ Proposed action                                               │
│        └─ Risk assessment                                               │
│                                                                         │
│  4. Make decision                                                       │
│     └─ [a] approve: Agent proceeds with action                          │
│     └─ [r] reject: Agent receives rejection + reason                    │
│     └─ [d] defer: Mark for later review                                 │
│                                                                         │
│  5. Batch operations (optional)                                         │
│     └─ [Space] toggles selection                                        │
│     └─ [A] approve all selected                                         │
│     └─ [R] reject all selected                                          │
│                                                                         │
│  6. View approval history                                               │
│     └─ [h] shows recent approvals/rejections                            │
│     └─ Useful for auditing                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| y | Jump to yield queue |
| j/k | Select yield |
| a | Approve |
| r | Reject |
| d | Defer |
| Space | Toggle selection |
| A | Approve all selected |
| R | Reject all selected |
| h | View history |

**Safety Features**:
- Dangerous actions highlighted in red
- Require confirmation for irreversible operations
- Rejection requires reason (brief text input)

---

## Flow 5: Navigate Decision History (Loom)

**Goal**: Explore agent decision tree, including rejected branches.

**Entry**: `t` from Cockpit or Debugger, or `l` for Loom

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Explore Decision History                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Enter Loom screen                                                   │
│     └─ [t] from Cockpit/Debugger                                        │
│     └─ Shows cognitive tree with branches                               │
│                                                                         │
│  2. Navigate the tree                                                   │
│     └─ [j] move down (children/later in time)                           │
│     └─ [k] move up (parent/earlier in time)                             │
│     └─ [h] move to left sibling branch                                  │
│     └─ [l] move to right sibling branch                                 │
│                                                                         │
│  3. Understand branch types                                             │
│     └─ ● Selected branch (what agent did)                               │
│     └─ ○ Ghost branch (what agent considered)                           │
│     └─ ✖ Rejected branch (explicitly discarded)                         │
│     └─ : Forecast branch (predicted future)                             │
│                                                                         │
│  4. Toggle ghost visibility                                             │
│     └─ [g] toggles ghost branches                                       │
│     └─ Ghosts fade over time (opacity = age)                            │
│     └─ Often reveals "near misses"                                      │
│                                                                         │
│  5. Examine reasoning                                                   │
│     └─ Select any node                                                  │
│     └─ Detail panel shows:                                              │
│        └─ Content (what was done/considered)                            │
│        └─ Reasoning (why this choice)                                   │
│        └─ Timestamp                                                     │
│        └─ Confidence level                                              │
│                                                                         │
│  6. Crystallize important moments                                       │
│     └─ Navigate to significant decision                                 │
│     └─ [c] crystallize                                                  │
│     └─ Saves to D-gent (long-term memory)                               │
│     └─ Crystals persist across sessions                                 │
│                                                                         │
│  7. Jump to debugger for deep analysis                                  │
│     └─ [d] opens Debugger at current node                               │
│     └─ Shows full Turn DAG context                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| t/l | Enter Loom |
| j/k | Navigate time (down/up) |
| h/l | Navigate branches (left/right) |
| g | Toggle ghosts |
| c | Crystallize moment |
| d | Jump to Debugger |
| Esc | Back |

**Visual Encoding**:
- Main path: bright, solid
- Ghost branches: dim, fading
- Current position: bold highlight
- Forecasts: dotted

---

## Flow 6: Real-time Agent Monitoring

**Goal**: Watch agents work in real-time with intervention capability.

**Entry**: Terrarium with live mode enabled

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Real-time Monitoring                                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Enter Terrarium in live mode                                        │
│     └─ Default when agents are active                                   │
│     └─ Status bar shows: "LIVE ●"                                       │
│                                                                         │
│  2. Watch the field                                                     │
│     └─ Agent density fields pulse with activity                         │
│     └─ Flow arrows show message passing                                 │
│     └─ Entropy gradients visible as distortion                          │
│                                                                         │
│  3. Monitor sub-views                                                   │
│     └─ [2] TRACES: Watch AGENTESE invocations stream                    │
│     └─ [3] FLUX: See event throughput graph                             │
│     └─ [4] TURNS: Watch turn counts by type                             │
│                                                                         │
│  4. Emergency intervention                                              │
│     └─ [Space] PAUSE all flux streams                                   │
│     └─ Agents freeze in current state                                   │
│     └─ Can inspect, adjust, then [Space] to resume                      │
│                                                                         │
│  5. Adjust agent temperature                                            │
│     └─ [+] zoom to Cockpit for target agent                             │
│     └─ Use temperature slider                                           │
│     └─ Or [1-9] for quick temperature presets                           │
│                                                                         │
│  6. Handle yields                                                       │
│     └─ Yellow flash indicates pending yield                             │
│     └─ [y] shows yield overlay                                          │
│     └─ Approve/reject without leaving view                              │
│                                                                         │
│  7. Capture interesting moments                                         │
│     └─ [c] captures current frame                                       │
│     └─ Saves snapshot for later analysis                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Bindings Used**:
| Key | Action |
|-----|--------|
| Space | Pause/Resume |
| 1-4 | Switch sub-view |
| + | Zoom to agent Cockpit |
| y | Show yield overlay |
| c | Capture snapshot |
| 1-9 | Temperature presets |

**Visual Feedback**:
- Live indicator pulses
- Paused state dims slightly
- Yields flash yellow border
- High entropy agents glitch

---

## Flow 7: Export and Share

**Goal**: Export traces, snapshots, or configurations for sharing.

**Entry**: `x` from any screen

**Steps**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ FLOW: Export and Share                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Trigger export overlay                                              │
│     └─ [x] from any screen                                              │
│     └─ Context-aware: exports what's visible                            │
│                                                                         │
│  2. Select export type                                                  │
│     └─ [1] Trace (full turn history, Markdown)                          │
│     └─ [2] Snapshot (current state, JSON)                               │
│     └─ [3] Configuration (agent setup, YAML)                            │
│     └─ [4] Screenshot (ASCII art, TXT)                                  │
│                                                                         │
│  3. Select scope                                                        │
│     └─ [a] All visible                                                  │
│     └─ [f] Focused agent only                                           │
│     └─ [s] Selection (if multi-select active)                           │
│                                                                         │
│  4. Choose destination                                                  │
│     └─ [c] Clipboard                                                    │
│     └─ [w] Write to file (prompts for path)                             │
│     └─ [p] Print to stdout (for piping)                                 │
│                                                                         │
│  5. Confirmation                                                        │
│     └─ Shows preview of first 20 lines                                  │
│     └─ [Enter] confirms                                                 │
│     └─ [Esc] cancels                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Export Formats**:

| Type | Format | Contains |
|------|--------|----------|
| Trace | Markdown | Full turn history with reasoning |
| Snapshot | JSON | Current state of all agents |
| Configuration | YAML | Agent setup for reproduction |
| Screenshot | TXT | ASCII art of current screen |

---

## Universal Key Reference

### Global (All Screens)

| Key | Action |
|-----|--------|
| q | Quit (with confirmation if unsaved) |
| ? | Help overlay |
| : | Command mode (vim-style) |
| / | Search/filter |
| Space | Emergency pause |
| x | Export |
| Esc | Back/dismiss/zoom out |

### Navigation (Vim-Style)

| Key | Action |
|-----|--------|
| j/k | Down/Up |
| h/l | Left/Right (also branch nav) |
| gg | Jump to top |
| G | Jump to bottom |
| Ctrl+d | Page down |
| Ctrl+u | Page up |

### Zoom (LOD)

| Key | Action |
|-----|--------|
| + | Zoom in (more detail) |
| - | Zoom out (less detail) |
| Enter | Zoom into focused item |
| Esc | Zoom out one level |

### Agent Actions

| Key | Action |
|-----|--------|
| d | Debugger for agent |
| t/l | Loom (decision tree) |
| f | Forge (build/edit) |
| c | Crystallize (save to memory) |
| y | Yield queue |

### Numbers

| Key | Action |
|-----|--------|
| 1-9 | Context-dependent: sub-views, presets, or selection |
| 0 | Reset to default |

---

## Accessibility Notes

### Keyboard-First Design
- Every action reachable via keyboard
- No mouse required
- Consistent vim-style navigation

### Color Independence
- Phase symbols differ by shape, not just color
- Health uses block characters, not just color
- Ghost branches differ by opacity AND character

### Screen Reader Support
- All panels have semantic labels
- Turn content fully describable
- State changes announced

---

## Error Recovery

### Undo Operations
- Most operations are reversible
- [u] undoes last action where applicable
- Forge keeps history of pipeline changes

### Escape Hatches
- [Esc] always returns to previous state
- [q] quits with confirmation
- [Space] pauses everything safely

### Confirmation for Dangerous Operations
- Deleting pipelines
- Rejecting all yields
- Force-stopping agents

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Dashboard Overhaul | `plans/interfaces/dashboard-overhaul.md` |
| Alethic Workbench | `plans/interfaces/alethic-workbench.md` |
| Primitives | `plans/interfaces/primitives.md` |
| I-gent Grammar | `spec/i-gents/grammar.md` |
| Keybinding Standard | `docs/cli-reference.md` |

---

*"The interface should feel like an extension of thought."*
