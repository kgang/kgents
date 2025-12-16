# Plan: Gardener-Logos Full Enactment

> *"The garden that tends itself still needs a gardener. Now we build the hands."*

**Status:** `[active]`
**Progress:** 90%
**Spec:** `spec/protocols/gardener-logos.md`
**Foundation:** `impl/claude/protocols/gardener_logos/` (178 tests passing)
**Owner:** Claude + Kent
**Created:** 2025-12-16

---

## Executive Summary

The Gardener-Logos foundation is built (garden state, tending calculus, plots, personality, ASCII projection). This plan enacts the **full system**:

1. **Phase 1: AGENTESE Wiring** — Connect to Logos, make paths live
2. **Phase 2: CLI Integration** — `kg garden`, `kg tend`, `kg plot` commands
3. **Phase 3: Persistence** — Garden state survives sessions
4. **Phase 4: Session Unification** — Merge with existing GardenerSession
5. **Phase 5: Prompt Logos Delegation** — `concept.prompt.*` flows through garden
6. **Phase 6: Synergy Bus** — Cross-jewel event integration
7. **Phase 7: Web Visualization** — React garden component
8. **Phase 8: Auto-Inducer** — Automatic season transitions

---

## Current State (Phase 6 Complete)

```
impl/claude/protocols/gardener_logos/
├── __init__.py              ✅ Package exports
├── garden.py                ✅ GardenState + Session integration (Phase 4)
├── tending.py               ✅ TendingVerb, TendingGesture, apply_gesture
├── plots.py                 ✅ PlotState, create_crown_jewel_plots
├── personality.py           ✅ TendingPersonality, joy layer
├── persistence.py           ✅ GardenStore (Phase 3)
├── agentese/
│   ├── __init__.py          ✅ Package exports
│   └── context.py           ✅ GardenerLogosNode + session.* handlers
├── meta/
│   ├── __init__.py          ✅
│   └── meta_tending.py      ✅ META_TENDING_PROMPT, invoke_meta_tending
├── projections/
│   ├── __init__.py          ✅
│   ├── ascii.py             ✅ project_garden_to_ascii
│   └── json.py              ✅ project_garden_to_json
└── _tests/
    ├── __init__.py          ✅
    ├── test_garden.py       ✅ 16 tests
    ├── test_tending.py      ✅ 23 tests
    ├── test_agentese.py     ✅ 40 tests
    ├── test_persistence.py  ✅ 37 tests
    └── test_session_unification.py ✅ 26 tests (NEW Phase 4)
```

**Total:** 159 tests passing in gardener_logos + 52 in agents/gardener = 211 tests

---

## Phase 1: AGENTESE Wiring

**Goal:** Make `concept.gardener.*` paths live in the Logos system.

### 1.1 Create GardenerLogosNode

**File:** `impl/claude/protocols/gardener_logos/agentese/context.py`

```python
@dataclass
class GardenerLogosNode(BaseLogosNode):
    """
    Unified AGENTESE node for Gardener-Logos.

    Routes:
    - concept.gardener.manifest → Garden overview
    - concept.gardener.tend → Apply tending gesture
    - concept.gardener.season.* → Season operations
    - concept.gardener.plot.* → Plot management
    - concept.gardener.session.* → Session operations
    - concept.prompt.* → Delegated to PromptContextResolver
    """

    _handle: str = "concept.gardener"
    _garden: GardenState | None = None
    _prompt_resolver: PromptContextResolver | None = None
    _personality: TendingPersonality | None = None
```

**Aspects to implement:**

| Aspect | AGENTESE Path | Handler |
|--------|--------------|---------|
| `manifest` | `concept.gardener.manifest` | Return garden ASCII/JSON |
| `tend` | `concept.gardener.tend` | Apply TendingGesture |
| `season.manifest` | `concept.gardener.season.manifest` | Current season info |
| `season.transition` | `concept.gardener.season.transition` | Change season |
| `plot.list` | `concept.gardener.plot.list` | List all plots |
| `plot.create` | `concept.gardener.plot.create` | Create new plot |
| `plot.focus` | `concept.gardener.plot.focus` | Set active plot |
| `plot.manifest` | `concept.gardener.plot.manifest` | View specific plot |
| `route` | `concept.gardener.route` | NL → path (existing) |
| `propose` | `concept.gardener.propose` | Suggestions (existing) |

### 1.2 Register with Logos

**File:** `impl/claude/protocols/agentese/contexts/__init__.py`

Add GardenerLogosNode to the context registry:

```python
from ..gardener_logos.agentese import GardenerLogosNode, GardenerLogosResolver

CONTEXT_RESOLVERS["gardener"] = GardenerLogosResolver()
```

### 1.3 Tests

**File:** `impl/claude/protocols/gardener_logos/_tests/test_agentese.py`

- Test path resolution
- Test manifest rendering
- Test tend gesture application
- Test season transitions
- Test plot operations

**Deliverables:**
- [x] `agentese/context.py` — GardenerLogosNode implementation (all aspects: manifest, tend, season.*, plot.*)
- [x] `agentese/__init__.py` — Package exports
- [ ] Registration in Logos context system (deferred to Phase 2)
- [x] 40 tests for AGENTESE integration (`_tests/test_agentese.py`)

---

## Phase 2: CLI Integration

**Goal:** `kg garden`, `kg tend`, `kg plot` commands work.

### 2.1 Garden Command Handler

**File:** `impl/claude/protocols/cli/handlers/garden.py`

```python
async def handle_garden(
    args: Namespace,
    logos: Logos,
    umwelt: Umwelt,
) -> None:
    """
    Handle `kg garden` command.

    Subcommands:
        kg garden              → Show garden status (ASCII)
        kg garden --json       → Show garden status (JSON)
        kg garden season       → Show current season
        kg garden health       → Show health metrics
    """
```

### 2.2 Tend Command Handler

**File:** `impl/claude/protocols/cli/handlers/tend.py`

```python
async def handle_tend(
    args: Namespace,
    logos: Logos,
    umwelt: Umwelt,
) -> None:
    """
    Handle `kg tend` command.

    Usage:
        kg tend observe <target>           → Observe without changing
        kg tend prune <target> --reason    → Mark for removal
        kg tend graft <target> --reason    → Add new element
        kg tend water <target> --feedback  → Nurture via TextGRAD
        kg tend rotate <target>            → Change perspective
        kg tend wait                       → Intentional pause
    """
```

### 2.3 Plot Command Handler

**File:** `impl/claude/protocols/cli/handlers/plot.py`

```python
async def handle_plot(
    args: Namespace,
    logos: Logos,
    umwelt: Umwelt,
) -> None:
    """
    Handle `kg plot` command.

    Usage:
        kg plot                    → List all plots
        kg plot <name>             → Show specific plot
        kg plot create <name>      → Create new plot
        kg plot focus <name>       → Set active plot
        kg plot link <name> <plan> → Link plot to Forest plan
    """
```

### 2.4 Register Commands

**File:** `impl/claude/protocols/cli/hollow.py`

Add to COMMAND_REGISTRY:

```python
"garden": handle_garden,
"tend": handle_tend,
"plot": handle_plot,
```

### 2.5 Tests

**File:** `impl/claude/protocols/cli/handlers/_tests/test_garden_cli.py`

**Deliverables:**
- [x] `handlers/garden.py` — Garden command (show, season, health, init, transition)
- [x] `handlers/tend.py` — Tend command (observe, prune, graft, water, rotate, wait + aliases)
- [x] `handlers/plot.py` — Plot command (list, show, create, focus, link, discover)
- [x] Registration in hollow.py (10 commands registered)
- [x] 62 CLI tests passing (`test_garden_cli.py`)

---

## Phase 3: Persistence

**Goal:** Garden state survives across sessions.

### 3.1 Garden Store

**File:** `impl/claude/protocols/gardener_logos/persistence.py`

```python
class GardenStore:
    """
    SQLite persistence for GardenState.

    Tables:
    - gardens: id, name, season, season_since, active_plot, created_at, updated_at
    - plots: id, garden_id, name, path, progress, rigidity, season_override, ...
    - gestures: id, garden_id, verb, target, tone, reasoning, entropy_cost, timestamp
    - metrics: garden_id, timestamp, health_score, entropy_spent, ...
    """

    async def save(self, garden: GardenState) -> None: ...
    async def load(self, garden_id: str) -> GardenState | None: ...
    async def get_default(self) -> GardenState: ...
    async def list_gardens(self) -> list[GardenState]: ...
```

### 3.2 Migration

**File:** `impl/claude/protocols/gardener_logos/migrations/001_initial.sql`

```sql
CREATE TABLE IF NOT EXISTS gardens (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    season TEXT NOT NULL DEFAULT 'DORMANT',
    season_since TEXT NOT NULL,
    active_plot TEXT,
    session_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plots (
    id TEXT PRIMARY KEY,
    garden_id TEXT NOT NULL REFERENCES gardens(id),
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    plan_path TEXT,
    crown_jewel TEXT,
    progress REAL DEFAULT 0.0,
    rigidity REAL DEFAULT 0.5,
    season_override TEXT,
    created_at TEXT NOT NULL,
    last_tended TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gestures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garden_id TEXT NOT NULL REFERENCES gardens(id),
    verb TEXT NOT NULL,
    target TEXT NOT NULL,
    tone REAL NOT NULL,
    reasoning TEXT,
    entropy_cost REAL NOT NULL,
    observer TEXT,
    session_id TEXT,
    result_summary TEXT,
    timestamp TEXT NOT NULL
);
```

### 3.3 Auto-Save Integration

Hook into gesture application:

```python
async def apply_gesture(garden: GardenState, gesture: TendingGesture, store: GardenStore | None = None) -> TendingResult:
    result = await _apply_gesture_internal(garden, gesture)

    if store and result.accepted:
        await store.save(garden)

    return result
```

**Deliverables:**
- [x] `persistence.py` — GardenStore class (save, load, get_default, gestures)
- [x] Schema embedded in persistence.py (gardens, plots, gestures, default tables)
- [x] Auto-save on gesture application (store parameter in apply_gesture)
- [x] 37 persistence tests in test_persistence.py

---

## Phase 4: Session Unification

**Goal:** Merge GardenerSession polynomial with GardenState.

### 4.1 Analysis

The existing `agents/gardener/session.py` has:
- SessionPhase (SENSE, ACT, REFLECT)
- SessionState, SessionIntent, SessionArtifact
- GardenerSession class with polynomial state machine

The new GardenState should **contain** session state, not replace it:

```python
@dataclass
class GardenState:
    # ... existing fields ...

    # Session link (unified)
    session: GardenerSession | None = None

    def get_or_create_session(self, name: str) -> GardenerSession:
        """Get active session or create new one."""
        if self.session is None:
            self.session = create_gardener_session(name=name)
        return self.session
```

### 4.2 Session-Garden Synergy

When session advances phases:
- SENSE → ACT: Garden might transition to SPROUTING
- ACT → REFLECT: Garden might transition to BLOOMING
- Complete: Garden might transition to HARVEST

```python
async def on_session_phase_advance(garden: GardenState, old_phase: SessionPhase, new_phase: SessionPhase) -> None:
    """React to session phase changes."""
    if old_phase == SessionPhase.SENSE and new_phase == SessionPhase.ACT:
        # Ideas are forming
        if garden.season == GardenSeason.DORMANT:
            garden.transition_season(GardenSeason.SPROUTING, "Session entered ACT phase")
```

### 4.3 Unified Handlers

Merge the handlers in `agents/gardener/handlers.py` with the new GardenerLogosNode.

**Deliverables:**
- [x] Session embedded in GardenState (`_session` field, `session` property, `get_or_create_session()`)
- [x] Phase → Season synergy hooks (`on_session_phase_advance()`, `on_session_complete()`)
- [x] Unified AGENTESE handlers (9 session.* aspects in GardenerLogosNode)
- [x] Tests for session unification (26 tests in `test_session_unification.py`)
- [ ] Migration for existing sessions (deferred - no active SessionStore data to migrate)

**Implementation Notes:**
- GardenState now owns the session via `_session` field
- Creating a session when DORMANT auto-transitions to SPROUTING
- SENSE → ACT triggers DORMANT/COMPOSTING → SPROUTING
- ACT → REFLECT triggers SPROUTING → BLOOMING
- Session complete triggers → HARVEST
- Multiple cycles (3+) can trigger BLOOMING → HARVEST
- All 211 gardener/gardener_logos tests pass

---

## Phase 5: Prompt Logos Delegation

**Goal:** `concept.prompt.*` paths flow through the garden.

### 5.1 Delegation Pattern

```python
class GardenerLogosNode(BaseLogosNode):
    async def _invoke_aspect(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        # ... garden aspects ...

        # Delegate prompt paths
        if aspect.startswith("prompt."):
            return await self._delegate_to_prompt(aspect[7:], observer, **kwargs)

    async def _delegate_to_prompt(self, sub_aspect: str, observer: Umwelt, **kwargs) -> Any:
        """Delegate to PromptContextResolver with garden context."""
        if self._prompt_resolver is None:
            self._prompt_resolver = create_prompt_resolver()

        # Inject garden context
        kwargs["garden_context"] = {
            "season": self._garden.season,
            "active_plot": self._garden.active_plot,
            "plasticity": self._garden.season.plasticity,
        }

        return await self._prompt_resolver.resolve("prompt", [sub_aspect])._invoke_aspect(
            sub_aspect, observer, **kwargs
        )
```

### 5.2 Garden-Aware TextGRAD

When watering prompts, use garden context:

```python
async def _handle_water(garden: GardenState, gesture: TendingGesture) -> TendingResult:
    if gesture.target.startswith("concept.prompt"):
        # Learning rate adjusted by season plasticity
        learning_rate = gesture.tone * garden.season.plasticity

        # Invoke TextGRAD with garden-aware parameters
        result = await invoke_textgrad(
            target=gesture.target,
            feedback=gesture.reasoning,
            learning_rate=learning_rate,
        )
```

**Deliverables:**
- [x] Prompt delegation in GardenerLogosNode (`_delegate_to_prompt()`, `_get_prompt_resolver()`)
- [x] Garden context injection (season, active_plot, plasticity, entropy_multiplier)
- [x] Season-aware TextGRAD (`learning_rate = tone × season.plasticity`)
- [x] Tests for delegation (19 tests in `test_prompt_delegation.py`)

**Implementation Notes (Session 2025-12-16):**
- GardenerLogosNode now handles `prompt.*` aspects via delegation
- `_invoke_aspect` routes `prompt.*` to `_delegate_to_prompt()`
- `_delegate_to_prompt()` injects `garden_context` with season, plasticity, active_plot
- For `prompt.evolve`, learning_rate is adjusted: `base_rate × season.plasticity`
- `_handle_water` in tending.py invokes TextGRAD with garden-aware parameters
- Affordances updated: guest gets `prompt.manifest`, `prompt.history`; developer/meta get full prompt affordances
- Total: 178 tests passing in gardener_logos

---

## Phase 6: Synergy Bus Integration

**Goal:** Garden events flow through the Synergy Bus for cross-jewel coordination.

### 6.1 Garden Events

**File:** `impl/claude/protocols/synergy/events.py`

```python
@dataclass(frozen=True)
class GardenSeasonChanged(SynergyEvent):
    """Emitted when garden season transitions."""
    garden_id: str
    old_season: str
    new_season: str
    reason: str

@dataclass(frozen=True)
class GestureApplied(SynergyEvent):
    """Emitted when a tending gesture is applied."""
    garden_id: str
    verb: str
    target: str
    success: bool

@dataclass(frozen=True)
class PlotProgressUpdated(SynergyEvent):
    """Emitted when plot progress changes."""
    garden_id: str
    plot_name: str
    old_progress: float
    new_progress: float
```

### 6.2 Event Handlers

**File:** `impl/claude/protocols/synergy/handlers/garden_handlers.py`

```python
class GardenSynergyHandler(BaseSynergyHandler):
    """Handle cross-jewel garden events."""

    async def on_gestalt_analysis_complete(self, event: GestaltAnalysisComplete) -> None:
        """When Gestalt completes, update relevant plot."""
        plot = self._find_plot_for_module(event.module_path)
        if plot:
            gesture = observe(plot.path, f"Gestalt analysis: {event.summary}")
            await apply_gesture(self._garden, gesture)

    async def on_brain_crystal_created(self, event: CrystalCreated) -> None:
        """When Brain creates crystal, link to active plot."""
        if self._garden.active_plot:
            plot = self._garden.plots[self._garden.active_plot]
            # Link crystal to plot context
            ...
```

**Deliverables:**
- [x] Garden event types (SEASON_CHANGED, GESTURE_APPLIED, PLOT_PROGRESS_UPDATED)
- [x] Factory functions for events (create_season_changed_event, create_gesture_applied_event, create_plot_progress_event)
- [x] Event emission in garden.py (transition_season) and tending.py (apply_gesture)
- [x] GardenToBrainHandler (auto-capture season transitions and significant gestures)
- [x] GestaltToGardenHandler (update plots when Gestalt analyzes relevant modules)
- [x] Handler registration in bus.py (Wave 4 handlers)
- [x] 22 tests for synergy (test_garden_handlers.py)

**Implementation Notes (Session 2025-12-16):**
- Added 3 new event types to SynergyEventType enum
- Garden operations emit events automatically (emit_event parameter controls this)
- GardenToBrainHandler captures season transitions, significant gestures, and milestone progress
- GestaltToGardenHandler observes plots when Gestalt analyzes matching paths
- Path matching uses crown_jewel mapping, plan_path overlap, and plot name matching
- 92 total synergy tests passing

---

## Phase 7: Web Visualization

**Goal:** React component for garden visualization.

### 7.1 Garden Component

**File:** `impl/claude/web/src/components/garden/GardenVisualization.tsx`

```tsx
interface GardenVisualizationProps {
  garden: GardenState;
  onTend?: (gesture: TendingGesture) => void;
  onPlotSelect?: (plotName: string) => void;
}

export function GardenVisualization({ garden, onTend, onPlotSelect }: GardenVisualizationProps) {
  return (
    <div className="garden-container">
      <GardenHeader season={garden.season} health={garden.metrics.health_score} />
      <PlotGrid plots={garden.plots} activePlot={garden.active_plot} onSelect={onPlotSelect} />
      <GestureHistory gestures={garden.recent_gestures} />
      <SeasonIndicator season={garden.season} plasticity={garden.season.plasticity} />
    </div>
  );
}
```

### 7.2 3D Garden (Optional)

Using Three.js for immersive garden view:

```tsx
export function Garden3D({ garden }: { garden: GardenState }) {
  return (
    <Canvas>
      <SceneLighting season={garden.season} />
      <GardenGround season={garden.season} />
      {Object.entries(garden.plots).map(([name, plot]) => (
        <PlotMesh key={name} plot={plot} isActive={name === garden.active_plot} />
      ))}
      <SeasonParticles season={garden.season} />
    </Canvas>
  );
}
```

### 7.3 API Endpoint

**File:** `impl/claude/protocols/api/garden.py`

```python
@router.get("/garden")
async def get_garden() -> dict:
    """Get current garden state."""
    garden = await get_default_garden()
    return project_garden_to_json(garden)

@router.post("/garden/tend")
async def apply_tend(request: TendRequest) -> TendingResult:
    """Apply a tending gesture."""
    gesture = TendingGesture(
        verb=TendingVerb[request.verb],
        target=request.target,
        tone=request.tone,
        reasoning=request.reasoning,
        entropy_cost=TendingVerb[request.verb].base_entropy_cost,
    )
    garden = await get_default_garden()
    return await apply_gesture(garden, gesture)
```

**Deliverables:**
- [ ] `GardenVisualization.tsx` — Main component
- [ ] `PlotCard.tsx` — Individual plot display
- [ ] `SeasonIndicator.tsx` — Season visual
- [ ] `GestureHistory.tsx` — Recent gestures
- [ ] API endpoints
- [ ] Optional 3D view

---

## Phase 8: Auto-Inducer (Season Transitions)

**Goal:** Garden automatically transitions seasons based on signals.

### 8.1 Transition Signals

**File:** `impl/claude/protocols/gardener_logos/seasons.py`

```python
@dataclass
class TransitionSignals:
    """Accumulated signals for season transition."""

    # Activity signals
    gesture_frequency: float  # Gestures per hour
    gesture_diversity: float  # How many different verbs used

    # Progress signals
    plot_progress_delta: float  # How much progress changed
    artifacts_created: int  # Session artifacts

    # Time signals
    time_in_season: timedelta
    session_phase: SessionPhase | None

    # Entropy signals
    entropy_spent_ratio: float  # spent / budget

    @classmethod
    async def gather(cls, garden: GardenState) -> "TransitionSignals":
        """Gather current transition signals."""
        ...

async def evaluate_season_transition(garden: GardenState) -> SeasonTransition | None:
    """Evaluate whether garden should transition seasons."""
    signals = await TransitionSignals.gather(garden)

    # DORMANT → SPROUTING: New activity detected
    if garden.season == GardenSeason.DORMANT:
        if signals.gesture_frequency > 2.0 and signals.entropy_spent_ratio < 0.5:
            return SeasonTransition(
                from_season=GardenSeason.DORMANT,
                to_season=GardenSeason.SPROUTING,
                reason="Increased activity detected",
                confidence=min(1.0, signals.gesture_frequency / 5.0),
            )

    # SPROUTING → BLOOMING: Ideas crystallizing
    elif garden.season == GardenSeason.SPROUTING:
        if signals.plot_progress_delta > 0.2 and signals.time_in_season > timedelta(hours=2):
            return SeasonTransition(
                from_season=GardenSeason.SPROUTING,
                to_season=GardenSeason.BLOOMING,
                reason="Progress indicates crystallization",
                confidence=signals.plot_progress_delta,
            )

    # ... etc for other transitions

    return None
```

### 8.2 Auto-Inducer Hook

Check for transitions on gesture application:

```python
async def apply_gesture(garden: GardenState, gesture: TendingGesture, ...) -> TendingResult:
    result = await _apply_gesture_internal(garden, gesture)

    # Check for auto-induced season transition
    transition = await evaluate_season_transition(garden)
    if transition and transition.confidence > 0.7:
        # Emit event but don't auto-apply (let user confirm)
        result.suggested_transition = transition

    return result
```

**Deliverables:**
- [ ] `seasons.py` — Transition logic
- [ ] TransitionSignals gathering
- [ ] Auto-inducer integration
- [ ] Tests for each transition type

---

## Implementation Order

```
Phase 1 (AGENTESE)     ██████████ 100% ✅
Phase 2 (CLI)          ██████████ 100% ✅
Phase 3 (Persistence)  ██████████ 100% ✅
Phase 4 (Session)      ██████████ 100% ✅
Phase 5 (Prompt)       ██████████ 100% ✅
Phase 6 (Synergy)      ██████████ 100% ✅
Phase 7 (Web)          ░░░░░░░░░░  0%  ← Next
Phase 8 (Auto-Inducer) ░░░░░░░░░░  0%
```

**Recommended execution:**
1. Phase 1 + 2 together (AGENTESE + CLI) — Makes garden usable
2. Phase 3 (Persistence) — Makes garden durable
3. Phase 4 (Session) — Unifies with existing work
4. Phase 5 + 6 (Prompt + Synergy) — Full integration
5. Phase 7 (Web) — Visual delight
6. Phase 8 (Auto-Inducer) — Autopoietic completion

---

## Success Criteria

### The Garden Test
- [ ] `kg garden` shows beautiful ASCII garden
- [ ] `kg tend observe concept.gardener` works
- [ ] `kg tend water concept.prompt.task.X` triggers TextGRAD
- [ ] Garden state persists across sessions

### The Integration Test
- [ ] Session phase changes sync with garden season
- [ ] Gestalt analysis updates relevant plots
- [ ] Brain crystals link to active plot

### The Joy Test
- [ ] Greetings feel personal and contextual
- [ ] Season transitions feel meaningful
- [ ] The garden metaphor clarifies rather than obscures

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Metaphor overload | Medium | High | Keep tending verbs to exactly 6, no more |
| Performance (gesture logging) | Low | Medium | Batch writes, limit stored gestures |
| Season confusion | Medium | Medium | Clear visual indicators, explicit transitions |
| Complexity creep | High | High | Strict phase gates, defer Phase 7-8 if needed |

---

## Dependencies

- `protocols/agentese/` — Logos, context resolution
- `protocols/prompt/` — PromptContextResolver, TextGRAD
- `agents/gardener/` — Existing session implementation
- `protocols/synergy/` — Event bus
- `protocols/api/` — REST endpoints
- `web/` — React components

---

*Plan created: 2025-12-16*
*Last updated: 2025-12-16*
*Phase 6 completed: 2025-12-16 (Synergy Bus Integration)*
