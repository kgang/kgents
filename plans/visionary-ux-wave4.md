---
path: plans/visionary-ux-wave4
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town-phase8
  - inhabit-web-ui
  - monetization-dashboard
session_notes: |
  Wave 4: Agent Town Citizen Dashboard - COMPLETE
  102 tests passing: CitizenWidget (41), ColonyDashboard (33), ColonyBridge (28)
  All projections working: CLI/TUI/marimo/JSON/SSE
  Signal-driven reactive updates via ColonyDashboardBridge
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: complete
  STRATEGIZE: skipped
  CROSS-SYNERGIZE: pending
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: pending
  MEASURE: pending
  REFLECT: complete
entropy:
  planned: 0.08
  spent: 0.06
  returned: 0.02
---

# Visionary UX Wave 4: Agent Town Citizen Dashboard

> *"Agent Town is THE soul converging point"* — _focus.md

## Context

Wave 3 delivered marimo deep integration (1708 tests). Wave 4 applies the reactive substrate to Agent Town: **real-time visualization of citizens, phases, and colony dynamics**.

## Research Summary

### Existing Infrastructure

| Component | Location | Reusable For |
|-----------|----------|--------------|
| `Citizen` | `town/citizen.py` | State extraction |
| `CitizenPhase` | `town/polynomial.py` | Phase → glyph mapping |
| `TownFlux` | `town/flux.py` | Event stream source |
| `LiveDashboard` | `town/live_dashboard.py` | Composition pattern |
| `EigenvectorScatterWidgetImpl` | `town/visualization.py` | 7D projection |
| `AgentCardWidget` | `i/reactive/primitives/agent_card.py` | Base card structure |
| `HStack/VStack` | `i/reactive/composable.py` | Grid composition |
| `Signal/Computed/Effect` | `i/reactive/signal.py` | Reactive state |

### Key Insights

1. **Activity history must be computed** from `TownFlux.trace` or `nphase_history`
2. **HStack/VStack composition** handles 100+ widgets (stress-tested)
3. **Colony-level Signal** better than per-citizen (single source of truth)
4. **Existing to_marimo()** on HStack/VStack - just use it

---

## Implementation Plan

### Phase 1: CitizenWidget (Goal 1)

Create `CitizenWidget` that extends `AgentCardWidget` semantics for Town citizens.

```
agents/i/reactive/primitives/
├── citizen_card.py      # NEW: CitizenWidget, CitizenState
└── _tests/
    └── test_citizen_card.py  # NEW
```

#### CitizenState (dataclass, frozen=True)

| Field | Type | Source |
|-------|------|--------|
| `citizen_id` | str | `citizen.id` |
| `name` | str | `citizen.name` |
| `archetype` | str | `citizen.archetype` |
| `phase` | CitizenPhase | `citizen._phase` |
| `nphase` | NPhase | `citizen.nphase_state.current_phase` |
| `activity` | tuple[float, ...] | Computed from trace (last 10 events) |
| `capability` | float | `1.0 - citizen.accursed_surplus / 10` (normalized) |
| `entropy` | float | `citizen.accursed_surplus / 10` (capped) |
| `eigenvectors` | Eigenvectors | `citizen.eigenvectors` |
| `region` | str | `citizen.region` |
| `mood` | str | `citizen._infer_mood()` |

#### Phase → Glyph Mapping

| CitizenPhase | Glyph | Animation |
|--------------|-------|-----------|
| IDLE | ○ | none |
| SOCIALIZING | ◉ | breathe |
| WORKING | ● | breathe |
| REFLECTING | ◐ | pulse |
| RESTING | ◯ | none |

#### Implementation

```python
# citizen_card.py
from agents.i.reactive.primitives.agent_card import AgentCardWidget, AgentCardState
from agents.town.polynomial import CitizenPhase

PHASE_TO_GLYPH: dict[CitizenPhase, tuple[str, str]] = {
    CitizenPhase.IDLE: ("idle", "none"),
    CitizenPhase.SOCIALIZING: ("active", "breathe"),
    CitizenPhase.WORKING: ("active", "breathe"),
    CitizenPhase.REFLECTING: ("thinking", "pulse"),
    CitizenPhase.RESTING: ("resting", "none"),
}

@dataclass(frozen=True)
class CitizenState:
    """Immutable state for a Town citizen widget."""
    citizen_id: str = ""
    name: str = "Citizen"
    archetype: str = "unknown"
    phase: CitizenPhase = CitizenPhase.IDLE
    nphase: NPhase = NPhase.SENSE
    activity: tuple[float, ...] = ()
    capability: float = 1.0
    entropy: float = 0.0
    region: str = ""
    mood: str = "calm"
    seed: int = 0
    t: float = 0.0

    def to_agent_card_state(self) -> AgentCardState:
        """Convert to AgentCardState for rendering."""
        phase_str, animation = PHASE_TO_GLYPH.get(self.phase, ("idle", "none"))
        return AgentCardState(
            agent_id=self.citizen_id,
            name=self.name,
            phase=phase_str,
            activity=self.activity,
            capability=self.capability,
            entropy=self.entropy,
            seed=self.seed,
            t=self.t,
            breathing=animation == "breathe",
        )

    @classmethod
    def from_citizen(cls, citizen: Citizen, activity_samples: tuple[float, ...] = ()) -> "CitizenState":
        """Extract state from a Citizen entity."""
        return cls(
            citizen_id=citizen.id,
            name=citizen.name,
            archetype=citizen.archetype,
            phase=citizen._phase,
            nphase=citizen.nphase_state.current_phase,
            activity=activity_samples,
            capability=max(0.0, 1.0 - citizen.accursed_surplus / 10),
            entropy=min(1.0, citizen.accursed_surplus / 10),
            region=citizen.region,
            mood=citizen._infer_mood(),
        )

class CitizenWidget(CompositeWidget[CitizenState]):
    """Widget for visualizing a Town citizen."""
    # Wraps AgentCardWidget with citizen-specific semantics
```

#### Tests

- `test_citizen_state_from_citizen`: Extract state from Citizen entity
- `test_phase_glyph_mapping`: All phases map correctly
- `test_to_agent_card_state`: Conversion preserves semantics
- `test_citizen_widget_project_cli`: ASCII output matches mockup
- `test_citizen_widget_project_marimo`: HTML structure correct
- `test_activity_history_bounds`: Activity values clamped to [0, 1]

---

### Phase 2: ColonyDashboard (Goal 2)

Compose multiple CitizenWidgets into a colony-level dashboard.

```
agents/i/reactive/
├── colony_dashboard.py      # NEW: ColonyDashboard, ColonyState
└── _tests/
    └── test_colony_dashboard.py  # NEW
```

#### ColonyState (dataclass, frozen=True)

| Field | Type | Description |
|-------|------|-------------|
| `colony_id` | str | Colony identifier |
| `citizens` | tuple[CitizenState, ...] | All citizen states |
| `phase` | TownPhase | Current simulation phase |
| `day` | int | Simulation day |
| `total_events` | int | Event counter |
| `total_tokens` | int | Token spend |
| `entropy_budget` | float | Remaining entropy |
| `selected_citizen_id` | str \| None | Currently selected |
| `grid_cols` | int | Citizens per row (default 4) |

#### ColonyDashboard Composition

```python
class ColonyDashboard(KgentsWidget[ColonyState]):
    """Unified dashboard for Agent Town colony visualization."""

    def __init__(self, initial: ColonyState | None = None) -> None:
        state = initial or ColonyState()
        super().__init__(state)

    def _build_citizen_grid(self) -> VStack:
        """Build citizen widget grid using HStack/VStack composition."""
        state = self.state.value
        citizens = state.citizens
        cols = state.grid_cols

        # Chunk citizens into rows
        rows: list[HStack] = []
        for i in range(0, len(citizens), cols):
            chunk = citizens[i:i+cols]
            widgets = [CitizenWidget(c) for c in chunk]
            if widgets:
                row = widgets[0]
                for w in widgets[1:]:
                    row = row >> w
                rows.append(row)

        # Stack rows vertically
        if not rows:
            return VStack(children=[])

        grid = rows[0]
        for row in rows[1:]:
            grid = grid // row

        return grid

    def project(self, target: RenderTarget) -> Any:
        """Project colony dashboard to rendering target."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()
            case _:
                return self._to_json()
```

#### CLI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT TOWN DASHBOARD                          │
├─────────────────────────────────────────────────────────────────┤
│ Colony: kgent-colony-1 │ Citizens: 12 │ Phase: MORNING │ Day: 3 │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│ │ ◉ Alice  │ │ ◉ Bob    │ │ ○ Carol  │ │ ● Dave   │           │
│ │ Builder  │ │ Trader   │ │ Healer   │ │ Sage     │           │
│ │ ▁▂▃▅▆▇█▆▅│ │ ▁▁▂▃▅▇██▇│ │ ▁▁▁▁▁▁▁▁▁│ │ ▁▂▁▂▁▂▁▂▁│           │
│ │ cap: 0.85│ │ cap: 0.92│ │ cap: 0.45│ │ cap: 0.78│           │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
├─────────────────────────────────────────────────────────────────┤
│ Entropy: 0.15 │ Budget: $0.42 remaining │ Events: 42           │
└─────────────────────────────────────────────────────────────────┘
```

#### Tests

- `test_colony_dashboard_empty`: Handles zero citizens
- `test_colony_dashboard_grid_4_cols`: Default 4 columns
- `test_colony_dashboard_grid_variable`: Different grid sizes
- `test_colony_state_from_flux`: Extract from TownFlux
- `test_colony_dashboard_cli`: ASCII output structure
- `test_colony_dashboard_marimo`: HTML div structure
- `test_colony_dashboard_json`: JSON serialization
- `test_citizen_selection`: Selected citizen highlighted
- `test_grid_composition_stress`: 25 citizens in <50ms

---

### Phase 3: Signal Integration (Goal 3)

Wire dashboard to live colony state updates.

#### ColonySignal Bridge

```python
# In colony_dashboard.py

class ColonyDashboardBridge:
    """Bridge between TownFlux events and ColonyDashboard state."""

    def __init__(self, flux: TownFlux, dashboard: ColonyDashboard) -> None:
        self.flux = flux
        self.dashboard = dashboard
        self._activity_buffers: dict[str, list[float]] = {}  # citizen_id -> activity samples

    def _compute_activity_sample(self, event: TownEvent) -> float:
        """Convert TownEvent to 0-1 activity sample."""
        if event.operation == "solo":
            return 0.3
        elif event.operation in ("greet", "trade"):
            return 0.7
        elif event.operation == "gossip":
            return 0.9
        return 0.5

    def handle_event(self, event: TownEvent) -> None:
        """Process TownEvent and update dashboard state."""
        # Update activity buffers for participants
        sample = self._compute_activity_sample(event)
        for name in event.participants:
            citizen = self._find_citizen_by_name(name)
            if citizen:
                buf = self._activity_buffers.setdefault(citizen.id, [])
                buf.append(sample)
                if len(buf) > 10:
                    buf.pop(0)

        # Update colony state
        self._refresh_state()

    def _refresh_state(self) -> None:
        """Rebuild ColonyState from current flux state."""
        status = self.flux.get_status()

        citizens_state = []
        for citizen in self.flux.citizens:
            activity = tuple(self._activity_buffers.get(citizen.id, []))
            state = CitizenState.from_citizen(citizen, activity_samples=activity)
            citizens_state.append(state)

        new_state = ColonyState(
            colony_id=f"colony-{id(self.flux)}",
            citizens=tuple(citizens_state),
            phase=self.flux.current_phase,
            day=self.flux.day,
            total_events=status["total_events"],
            total_tokens=status["total_tokens"],
            entropy_budget=status["accursed_surplus"],
        )

        self.dashboard.state.set(new_state)
```

#### Integration with EventBus

```python
async def wire_dashboard_to_flux(flux: TownFlux, dashboard: ColonyDashboard) -> None:
    """Wire dashboard to receive flux events."""
    bridge = ColonyDashboardBridge(flux, dashboard)

    if flux.event_bus:
        subscription = flux.event_bus.subscribe()
        async for event in subscription:
            if event is None:
                break
            bridge.handle_event(event)
```

#### Tests

- `test_activity_buffer_rolling`: 10-sample window
- `test_event_to_activity_sample`: Operation → sample mapping
- `test_bridge_refresh_state`: State updates on event
- `test_dashboard_signal_update`: Signal notifies subscribers
- `test_event_bus_integration`: Full integration test

---

### Phase 4: Projections (Goal 4)

Implement all render targets.

#### CLI Projection

Already described in Phase 2. Uses box-drawing characters per `meta.md`:
> Glyph grammar: middle dot (·) > period; box-drawing chars (═ ─ │) add polish

#### TUI Projection

```python
def _to_tui(self) -> Any:
    """TUI projection using Rich/Textual."""
    from rich.panel import Panel
    from rich.table import Table

    state = self.state.value

    table = Table(show_header=False, box=None, padding=(0, 1))
    for i in range(0, len(state.citizens), state.grid_cols):
        row_widgets = [
            CitizenWidget(c).project(RenderTarget.TUI)
            for c in state.citizens[i:i+state.grid_cols]
        ]
        table.add_row(*row_widgets)

    return Panel(
        table,
        title=f"[bold]AGENT TOWN[/bold] - {state.phase.name}",
        subtitle=f"Day {state.day} | Events: {state.total_events}",
    )
```

#### marimo Projection

```python
def _to_marimo(self) -> str:
    """marimo projection as HTML with anywidget support."""
    grid = self._build_citizen_grid()
    grid_html = grid.to_marimo(use_anywidget=False)  # HTML fallback

    # Add header and footer
    state = self.state.value
    header = f'''
    <div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #dee2e6;">
        <span style="font-weight: bold;">AGENT TOWN DASHBOARD</span>
        <span>{state.phase.name} | Day {state.day}</span>
    </div>
    '''

    footer = f'''
    <div style="display: flex; justify-content: space-between; padding: 8px; border-top: 1px solid #dee2e6; font-size: 0.875rem;">
        <span>Citizens: {len(state.citizens)}</span>
        <span>Events: {state.total_events}</span>
        <span>Entropy: {state.entropy_budget:.2f}</span>
    </div>
    '''

    return f'<div class="kgents-colony-dashboard">{header}{grid_html}{footer}</div>'
```

#### JSON Projection

```python
def _to_json(self) -> dict[str, Any]:
    """JSON projection for API responses."""
    state = self.state.value
    return {
        "type": "colony_dashboard",
        "colony_id": state.colony_id,
        "phase": state.phase.name,
        "day": state.day,
        "metrics": {
            "total_events": state.total_events,
            "total_tokens": state.total_tokens,
            "entropy_budget": state.entropy_budget,
        },
        "citizens": [
            {
                "id": c.citizen_id,
                "name": c.name,
                "archetype": c.archetype,
                "phase": c.phase.name,
                "nphase": c.nphase.name,
                "mood": c.mood,
                "region": c.region,
                "capability": c.capability,
                "entropy": c.entropy,
                "activity": list(c.activity),
            }
            for c in state.citizens
        ],
        "grid_cols": state.grid_cols,
        "selected_citizen_id": state.selected_citizen_id,
    }
```

#### SSE Projection

Extend existing `TownSSEEndpoint`:

```python
async def push_dashboard_state(self, state: ColonyState) -> None:
    """Push full dashboard state to SSE clients."""
    sse = SSEEvent(
        event="town.dashboard",
        data=state.to_dict(),  # Same as JSON projection
    )
    await self._queue.put(sse)
```

#### Tests

- `test_cli_projection_layout`: Box chars, alignment
- `test_tui_projection_rich`: Rich Panel structure
- `test_marimo_projection_html`: Valid HTML, CSS classes
- `test_json_projection_schema`: Matches API schema
- `test_sse_projection_format`: SSE wire format

---

## Integration with Agent Town Phase 8

Wave 4 enables Phase 8 "Inhabit":

| Wave 4 Output | Phase 8 Consumer |
|---------------|------------------|
| `CitizenWidget` | Citizen detail views |
| `ColonyDashboard` | Main dashboard |
| `ColonySignal` | Real-time updates |
| marimo projection | Notebook demos |
| SSE projection | Web UI streaming |
| JSON projection | REST API |

---

## File Summary

| File | Action | LOC (est) |
|------|--------|-----------|
| `agents/i/reactive/primitives/citizen_card.py` | NEW | ~150 |
| `agents/i/reactive/primitives/_tests/test_citizen_card.py` | NEW | ~100 |
| `agents/i/reactive/colony_dashboard.py` | NEW | ~250 |
| `agents/i/reactive/_tests/test_colony_dashboard.py` | NEW | ~200 |
| `agents/town/visualization.py` | MODIFY | +50 (SSE) |
| `agents/town/flux.py` | MODIFY | +20 (dashboard emit) |

**Total new tests**: ~30-40 (targeting comprehensive coverage)

---

## Success Criteria

- [x] `CitizenWidget` renders phase glyph, sparkline, capability bar
- [x] `CitizenState.from_citizen()` extracts all fields
- [x] `ColonyDashboard` composes 12+ citizen widgets in grid
- [x] CLI projection matches ASCII mockup
- [x] marimo projection renders interactive cards
- [x] Signal-driven updates via `ColonyDashboardBridge`
- [x] Performance: Full dashboard render < 50ms for 25 citizens (verified)

---

## Entropy Budget

| Item | Planned | Notes |
|------|---------|-------|
| CitizenState extraction | 0.02 | Clear mapping |
| Grid composition | 0.02 | HStack/VStack proven |
| Signal wiring | 0.02 | EventBus pattern exists |
| Projections | 0.02 | Follow existing patterns |
| **Total** | **0.08** | Low uncertainty |

---

## Auto-Inducer

⟿[COMPLETE]
/hydrate plans/visionary-ux-wave4.md
handles: scope=wave4-agent-town-dashboard; checkpoints=citizen+composition+signals+projections; ledger={DEVELOP:complete,TEST:complete}; entropy=0.06
mission: COMPLETE - CitizenWidget, ColonyDashboard, ColonyDashboardBridge implemented.
exit: 102 tests passing; enables Phase 8 Inhabit and Web UI integration.

---

*Guard [phase=REFLECT][entropy=0.06][law_check=true][wave=4][status=COMPLETE]*
