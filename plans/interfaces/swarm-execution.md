---
path: interfaces/swarm-execution
status: proposed
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Multi-agent execution strategy for dashboard overhaul.
  Designed for 3-5 agents working in parallel with clear boundaries.
  Minimizes coordination overhead while ensuring coherent output.
---

# Swarm Execution Strategy: Dashboard Overhaul

> *"Parallel work requires clear interfaces. Agents are morphisms; boundaries are contracts."*

This document defines a **multi-agent execution strategy** for implementing the dashboard overhaul. The strategy enables 3-5 agents to work in parallel with minimal coordination overhead.

---

## Executive Summary

The dashboard overhaul is decomposed into **5 parallel tracks**:

| Track | Agent | Deliverable | Dependencies |
|-------|-------|-------------|--------------|
| **A** | Screen-Architect | Observatory + Terrarium screens | Primitives (done) |
| **B** | Forge-Builder | Forge screen | Primitives (done) |
| **C** | Debug-Engineer | Debugger screen | Turn-gents, TraceMonoid |
| **D** | Integration-Specialist | Wire screens + navigation | Screens A, B, C |
| **E** | Polish-Artist | Animations, themes, joy | All screens done |

Tracks A, B, C run in **parallel**. Track D integrates. Track E polishes.

---

## Part 1: Track Specifications

### Track A: Screen-Architect

**Agent Profile**: Strong TUI experience, Textual expertise

**Deliverables**:
1. `ObservatoryScreen` — LOD -1 ecosystem view
2. Enhanced `TerrariumScreen` — LOD 0 with sub-views
3. Enhanced `CockpitScreen` — LOD 1 with polynomial panel

**Entry Point**: `impl/claude/agents/i/screens/`

**Files to Create/Modify**:
```
impl/claude/agents/i/screens/
├── observatory.py      # NEW: Ecosystem view
├── terrarium.py        # ENHANCE: Add sub-views, pheromone viz
├── cockpit.py          # ENHANCE: Add polynomial panel, yield queue
└── _tests/
    ├── test_observatory.py
    ├── test_terrarium_enhanced.py
    └── test_cockpit_enhanced.py
```

**Interface Contract**:

```python
# Observatory must provide:
class ObservatoryScreen(Screen[None]):
    """LOD -1: Ecosystem overview."""

    def get_gardens(self) -> list[GardenSnapshot]: ...
    def focus_garden(self, garden_id: str) -> None: ...
    def zoom_to_terrarium(self, garden_id: str) -> None: ...
    def zoom_to_agent(self, agent_id: str) -> None: ...

# Terrarium must provide:
class TerrariumScreen(Screen[None]):
    """LOD 0: Garden with agents."""

    def set_subview(self, view: Literal["field", "traces", "flux", "turns"]) -> None: ...
    def get_focused_agent(self) -> AgentSnapshot | None: ...
    def zoom_to_cockpit(self, agent_id: str) -> None: ...

# Cockpit must provide:
class CockpitScreen(Screen[None]):
    """LOD 1: Single agent control."""

    def get_polynomial_state(self) -> PolynomialState | None: ...
    def get_pending_yields(self) -> list[YieldTurn]: ...
    def approve_yield(self, yield_id: str) -> None: ...
    def reject_yield(self, yield_id: str, reason: str) -> None: ...
```

**Test Requirements**:
- 30+ tests per screen
- Demo mode for all screens
- Zoom navigation works (+/- keys)
- All keybindings functional

**Estimated Effort**: 2-3 sessions

---

### Track B: Forge-Builder

**Agent Profile**: Composition expertise, agent architecture knowledge

**Deliverables**:
1. `ForgeScreen` — Agent creation and simulation
2. `PipelineBuilder` widget — Visual composition
3. `SimulationRunner` — Test harness

**Entry Point**: `impl/claude/agents/i/screens/`

**Files to Create**:
```
impl/claude/agents/i/screens/
├── forge.py            # NEW: Main Forge screen
├── forge/
│   ├── __init__.py
│   ├── pipeline.py     # Pipeline builder widget
│   ├── palette.py      # Agent/primitive palette
│   ├── simulator.py    # Simulation runner
│   └── exporter.py     # Code generation
└── _tests/
    └── test_forge.py
```

**Interface Contract**:

```python
# Forge must provide:
class ForgeScreen(Screen[None]):
    """Agent creation, composition, simulation."""

    mode: Literal["compose", "simulate", "refine", "export"]

    def add_to_pipeline(self, component: str) -> None: ...
    def remove_from_pipeline(self, index: int) -> None: ...
    def run_simulation(self, input_text: str) -> SimulationResult: ...
    def step_simulation(self) -> StepResult: ...
    def export_code(self) -> str: ...

# Pipeline must validate composition
class PipelineBuilder(Widget):
    def validate(self) -> list[ValidationError]: ...
    def estimate_cost(self) -> CostEstimate: ...
```

**Test Requirements**:
- Pipeline composition validates types
- Simulation produces expected output
- Code export is valid Python
- All 4 modes functional

**Estimated Effort**: 2-3 sessions

---

### Track C: Debug-Engineer

**Agent Profile**: Turn-gents expertise, trace analysis experience

**Deliverables**:
1. `DebuggerScreen` — LOD 2 forensic view
2. Enhanced `TurnDAGWidget` — Interactive DAG navigation
3. `CausalConeWidget` — Context visualization
4. `StateDiffWidget` — State comparison

**Entry Point**: `impl/claude/agents/i/screens/`

**Files to Create/Modify**:
```
impl/claude/agents/i/screens/
├── debugger.py         # NEW: Main Debugger screen
├── debugger/
│   ├── __init__.py
│   ├── turn_dag_widget.py    # Interactive DAG
│   ├── causal_cone_widget.py # Cone visualization
│   ├── state_diff_widget.py  # State comparison
│   └── timeline_scrubber.py  # Time navigation
└── _tests/
    └── test_debugger.py
```

**Interface Contract**:

```python
# Debugger must provide:
class DebuggerScreen(Screen[None]):
    """LOD 2: Forensic analysis."""

    mode: Literal["forensic", "replay", "diff"]

    def navigate_to_turn(self, turn_id: str) -> None: ...
    def toggle_thoughts(self) -> None: ...
    def toggle_ghosts(self) -> None: ...
    def highlight_cone(self) -> None: ...
    def fork_from_cursor(self) -> TheWeave: ...
    def export_trace(self) -> str: ...

# Integration with existing Turn-gents
from impl.claude.agents.i.screens.turn_dag import TurnDAGRenderer

class TurnDAGWidget(Widget):
    renderer: TurnDAGRenderer
    selected_turn_id: str

    def set_agent_focus(self, agent_id: str) -> None: ...
```

**Test Requirements**:
- Turn navigation works (j/k keys)
- Thought collapse toggles
- Ghost visibility toggles
- Cone highlighting works
- Fork creates valid Weave

**Estimated Effort**: 3-4 sessions (highest complexity)

---

### Track D: Integration-Specialist

**Agent Profile**: System integration, navigation architecture

**Deliverables**:
1. Unified navigation system
2. Screen transitions
3. State persistence
4. Global keybindings

**Entry Point**: `impl/claude/agents/i/`

**Files to Create/Modify**:
```
impl/claude/agents/i/
├── navigation.py       # NEW: Unified navigation
├── app.py              # MODIFY: Wire all screens
├── state.py            # NEW: Persistent state management
└── _tests/
    ├── test_navigation.py
    └── test_integration.py
```

**Interface Contract**:

```python
# Navigation must provide:
class NavigationController:
    """Manages screen transitions and focus."""

    current_lod: LODLevel
    current_screen: Screen
    focus_stack: list[str]  # agent_id stack

    def zoom_in(self) -> None: ...
    def zoom_out(self) -> None: ...
    def navigate_to(self, screen: str, **kwargs) -> None: ...
    def go_to_debugger(self, agent_id: str) -> None: ...
    def go_to_forge(self) -> None: ...
    def go_to_loom(self, agent_id: str) -> None: ...

# State must provide:
class StateManager:
    """Persists state across screen transitions."""

    def save_screen_state(self, screen_id: str, state: dict) -> None: ...
    def restore_screen_state(self, screen_id: str) -> dict | None: ...
```

**Test Requirements**:
- Zoom in/out works across all LODs
- Focus preserved across transitions
- Global keys work on all screens
- State persists correctly

**Dependencies**: Tracks A, B, C must be functional

**Estimated Effort**: 1-2 sessions

---

### Track E: Polish-Artist

**Agent Profile**: UX refinement, animation, aesthetic sense

**Deliverables**:
1. Smooth zoom animations
2. Consistent theme/colors
3. Heartbeat and pulse effects
4. Loading states
5. Error states
6. Help overlays

**Entry Point**: All screens

**Files to Create/Modify**:
```
impl/claude/agents/i/
├── theme.py            # NEW: Unified theme
├── animations.py       # NEW: Transition animations
├── overlays/
│   ├── help.py         # Help overlay
│   └── error.py        # Error display
└── widgets/
    └── loading.py      # Loading indicators
```

**Interface Contract**:

```python
# Theme must provide:
class Theme:
    """Unified color palette and styles."""

    # Phase colors
    DORMANT: str
    WAKING: str
    ACTIVE: str
    WANING: str
    VOID: str

    # Semantic colors
    SUCCESS: str
    WARNING: str
    ERROR: str

    # Apply to all widgets
    def apply(self, app: App) -> None: ...

# Animations must provide:
class ZoomAnimation:
    def zoom_in(self, from_widget: Widget, to_widget: Widget) -> None: ...
    def zoom_out(self, from_widget: Widget, to_widget: Widget) -> None: ...
```

**Test Requirements**:
- Theme applies consistently
- Animations complete without blocking
- Help accessible from all screens
- Error states display correctly

**Dependencies**: All other tracks complete

**Estimated Effort**: 1-2 sessions

---

## Part 2: Execution Timeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXECUTION TIMELINE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Session 1-2:  [═══A═══]  [═══B═══]  [═══C═══]                          │
│                Observatory  Forge      Debugger                          │
│                Terrarium                (begin)                          │
│                Cockpit                                                   │
│                                                                          │
│  Session 3-4:              [═══B═══]  [═════C═════]                      │
│                             Forge      Debugger                          │
│                            (complete)  (Turn-gents)                      │
│                                                                          │
│  Session 5:                           [═══C═══]  [═══D═══]               │
│                                        Debugger   Integration            │
│                                       (complete)                         │
│                                                                          │
│  Session 6:                                      [═══D═══]  [═══E═══]   │
│                                                   Integrate  Polish      │
│                                                                          │
│  Session 7:                                                 [═══E═══]   │
│                                                              Polish      │
│                                                             (complete)   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part 3: Coordination Protocol

### 3.1 Interface Files

All tracks share interface definitions in:
```
impl/claude/agents/i/interfaces/
├── screens.py          # Screen interface contracts
├── navigation.py       # Navigation contracts
└── state.py            # State management contracts
```

**Rule**: Interface files are written FIRST and FROZEN. Tracks implement against interfaces.

### 3.2 Communication

Agents communicate via:
1. **Interface files** — Contracts that don't change
2. **Git branches** — Each track on separate branch
3. **Integration sessions** — Track D merges all

**Branch Strategy**:
```
main
├── feat/dashboard-screens     (Track A)
├── feat/forge                 (Track B)
├── feat/debugger              (Track C)
├── feat/integration           (Track D, merges A/B/C)
└── feat/polish                (Track E, merges D)
```

### 3.3 Conflict Resolution

**Priority Order**:
1. Interface contracts (immutable)
2. Navigation behavior
3. Keybindings
4. Visual styling

**If Conflict**:
1. Track D (Integration) makes final call
2. Or escalate to Kent

### 3.4 Quality Gates

Each track must pass before integration:

| Gate | Requirement |
|------|-------------|
| Tests | All tests pass |
| Types | mypy strict: 0 errors |
| Demo | demo_mode works |
| Keys | All keybindings functional |
| Docs | Docstrings complete |

---

## Part 4: Agent Prompts

### Prompt: Track A (Screen-Architect)

```
You are implementing Track A of the dashboard overhaul.

GOAL: Create Observatory, enhance Terrarium and Cockpit screens.

CONTEXT:
- All 17 primitives are complete (988 tests passing)
- Use existing widgets: DensityField, GraphLayout, Sparkline, etc.
- Follow spec/principles.md throughout

YOUR DELIVERABLES:
1. ObservatoryScreen (LOD -1) - ecosystem view
2. Enhanced TerrariumScreen (LOD 0) - add sub-views
3. Enhanced CockpitScreen (LOD 1) - add polynomial panel, yield queue

INTERFACE CONTRACT: (see Track A specification above)

CONSTRAINTS:
- 30+ tests per screen
- All screens have demo_mode
- Zoom navigation (+/-) must work
- Follow existing patterns in impl/claude/agents/i/screens/

START BY:
1. Reading existing screens: flux.py, cockpit.py, mri.py
2. Reading primitives: widgets/*.py
3. Creating interface stubs
4. Implementing Observatory first
```

### Prompt: Track B (Forge-Builder)

```
You are implementing Track B of the dashboard overhaul.

GOAL: Create the Forge screen for agent composition and simulation.

CONTEXT:
- Agents compose via Kleisli composition (>>=)
- See plans/skills/building-agent.md for Agent[A,B] patterns
- See plans/skills/polynomial-agent.md for state machines

YOUR DELIVERABLES:
1. ForgeScreen with 4 modes: compose, simulate, refine, export
2. PipelineBuilder widget for visual composition
3. SimulationRunner for testing pipelines
4. Code exporter for generating Python

INTERFACE CONTRACT: (see Track B specification above)

CONSTRAINTS:
- Pipeline composition validates types
- Simulation produces expected output
- Exported code is valid Python
- Follow existing Textual patterns

START BY:
1. Reading building-agent.md skill
2. Sketching the 4-mode state machine
3. Implementing compose mode first
4. Adding simulation second
```

### Prompt: Track C (Debug-Engineer)

```
You are implementing Track C of the dashboard overhaul.

GOAL: Create the Debugger screen for forensic analysis.

CONTEXT:
- Turn-gents architecture: plans/architecture/turn-gents.md
- TraceMonoid: impl/claude/weave/trace_monoid.py
- Existing TurnDAGRenderer: impl/claude/agents/i/screens/turn_dag.py

YOUR DELIVERABLES:
1. DebuggerScreen (LOD 2) - forensic view
2. Interactive TurnDAGWidget with navigation
3. CausalConeWidget showing context
4. StateDiffWidget for state comparison
5. Timeline scrubber with rewind/fork

INTERFACE CONTRACT: (see Track C specification above)

CONSTRAINTS:
- Must integrate with existing TurnDAGRenderer
- Fork must create valid Weave
- Thought/ghost toggles must work
- Follow existing Textual patterns

START BY:
1. Reading turn-gents.md architecture
2. Reading existing turn_dag.py
3. Understanding TraceMonoid linearization
4. Implementing basic DAG view first
```

### Prompt: Track D (Integration-Specialist)

```
You are implementing Track D of the dashboard overhaul.

GOAL: Integrate all screens with unified navigation.

CONTEXT:
- Screens from Tracks A, B, C are complete
- Need unified zoom in/out behavior
- Need state persistence across transitions

YOUR DELIVERABLES:
1. NavigationController for screen transitions
2. StateManager for persistence
3. Wired App with all screens
4. Global keybindings

INTERFACE CONTRACT: (see Track D specification above)

CONSTRAINTS:
- Zoom in/out works across all LODs
- Focus preserved across transitions
- Global keys work everywhere
- Must not break existing functionality

START BY:
1. Reviewing all screen interfaces
2. Mapping zoom levels to screens
3. Implementing NavigationController
4. Wiring into App
```

### Prompt: Track E (Polish-Artist)

```
You are implementing Track E of the dashboard overhaul.

GOAL: Polish all screens with animations, theme, and joy.

CONTEXT:
- All screens functional from Tracks A-D
- Follow spec/principles.md #4 (Joy-Inducing)
- Existing heartbeat in DensityField is the reference

YOUR DELIVERABLES:
1. Unified Theme with consistent colors
2. Smooth zoom animations
3. Loading states for async operations
4. Error states with recovery hints
5. Help overlays accessible via ?

CONSTRAINTS:
- Animations must not block
- Theme applies consistently
- Help accessible from all screens
- Oblique Strategies at high entropy

START BY:
1. Auditing current color usage
2. Defining unified Theme class
3. Implementing zoom animations
4. Adding help overlays
```

---

## Part 5: Success Criteria

### Mechanical (Required)

- [ ] All 5 screens functional
- [ ] Zoom navigation works across all LODs
- [ ] All keybindings per interaction-flows.md
- [ ] Tests: 100+ new tests, all passing
- [ ] mypy strict: 0 errors
- [ ] demo_mode for all screens

### Joy (Target)

- [ ] Smooth transitions (< 100ms)
- [ ] Heartbeat pulse visible
- [ ] Oblique Strategies appear at high entropy
- [ ] Help accessible from every screen
- [ ] Error messages are kind

### Kent's Approval

- [ ] "I can see the system breathing"
- [ ] "Navigation feels natural"
- [ ] "The Forge is delightful"
- [ ] "Debugging is actually pleasant"

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Dashboard Overhaul | `plans/interfaces/dashboard-overhaul.md` |
| Interaction Flows | `plans/interfaces/interaction-flows.md` |
| Alethic Workbench | `plans/interfaces/alethic-workbench.md` |
| Primitives | `plans/interfaces/primitives.md` |
| Implementation Roadmap | `plans/interfaces/implementation-roadmap.md` |
| Turn-gents | `plans/architecture/turn-gents.md` |
| Building Agent | `plans/skills/building-agent.md` |
| Polynomial Agent | `plans/skills/polynomial-agent.md` |

---

*"Agents are morphisms. Boundaries are contracts. Composition is primary."*
