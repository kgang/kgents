---
path: plans/dashboard-textual-refactor
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Dashboard Textual Architecture Refactor - Implementation Plan

> **Status**: In Progress
> **Created**: 2025-12-13
> **Based on**: HYDRATE.md (Dashboard Textual Architecture Refinement)

---

## Executive Summary

Port battle-tested patterns from zenportal to kgents dashboard:
- EventBus for decoupled communication
- Base screen with key passthrough
- Mixin decomposition for maintainability
- Service container for dependency injection
- Gentle Eye transitions for non-violent UX

**Current State**:
- 9 main screens (~6,500 LOC)
- No base screen class (all inherit `Screen[None]`)
- NavigationController exists (351 LOC) - LOD-based zoom
- No EventBus - direct calls and Observable pattern
- Only HeartbeatMixin exists as composition pattern

---

## Phase 1: EventBus Foundation

**Goal**: Create decoupled event system for screen-to-screen communication

**Files to Create**:
- `impl/claude/agents/i/services/events.py` (~150 LOC)
- `impl/claude/agents/i/services/_tests/test_events.py` (~200 LOC)
- `impl/claude/agents/i/services/__init__.py`

**EventBus Features**:
- Singleton pattern with `get()` and `reset()` (for testing)
- Strong + weak reference subscriptions
- Error isolation (one handler's exception doesn't affect others)
- Type-safe event hierarchy

**Event Types**:
```python
@dataclass
class Event:
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ScreenNavigationEvent(Event):
    target_screen: str = ""
    source_screen: str = ""
    focus_element: str | None = None

@dataclass
class AgentFocusedEvent(Event):
    agent_id: str = ""

@dataclass
class MetricsUpdatedEvent(Event):
    metrics: "DashboardMetrics | None" = None

@dataclass
class LODChangedEvent(Event):
    old_lod: int = 0
    new_lod: int = 0
```

**Estimated**: 1 agent, ~30 min

---

## Phase 2: Base Screen with Key Passthrough

**Goal**: Fix keybinding issues where number keys get eaten by nested screens

**Files to Create**:
- `impl/claude/agents/i/screens/base.py` (~200 LOC)
- `impl/claude/agents/i/screens/_tests/test_base.py` (~150 LOC)

**KgentsScreen Features**:
```python
class KgentsScreen(Screen):
    """Base screen with notification rack and key passthrough."""

    # Keys that should ALWAYS bubble to parent App
    PASSTHROUGH_KEYS = {"1", "2", "3", "4", "5", "6", "tab", "f", "d", "m", "?", "q"}

    # Anchor element for gentle eye transitions
    ANCHOR: ClassVar[str] = ""
    ANCHOR_MORPHS_TO: ClassVar[dict[str, str]] = {}

    def on_key(self, event: Key) -> None:
        """Pass global navigation keys to parent app."""
        if event.key in self.PASSTHROUGH_KEYS:
            # Don't stop - let it bubble UP to App
            return
        super().on_key(event)
```

**KgentsModalScreen Features**:
- Auto-dismiss with configurable delay
- Escape binding for cancel
- Typed result pattern

**Estimated**: 1 agent, ~20 min

---

## Phase 3: Mixin Decomposition

**Goal**: Break DashboardApp (~937 LOC) into focused, testable mixins

**Files to Create**:
- `impl/claude/agents/i/screens/dashboard_navigation.py` (~150 LOC)
- `impl/claude/agents/i/screens/dashboard_screens.py` (~200 LOC)
- `impl/claude/agents/i/screens/dashboard_help.py` (~100 LOC)

**Mixin Strategy**:
```python
class DashboardNavigationMixin:
    """Navigation actions - keybindings and screen transitions."""
    _SCREEN_ORDER = ["observatory", "dashboard", "cockpit", "flux", "loom", "mri"]

    def action_go_screen_1(self) -> None: ...
    def action_cycle_next(self) -> None: ...
    def _navigate_to(self, screen_name: str) -> None: ...

class DashboardScreensMixin:
    """Screen factory methods."""
    def _create_observatory(self) -> None: ...
    def _create_cockpit(self) -> None: ...

class DashboardHelpMixin:
    """Help and documentation overlays."""
    def action_show_help(self) -> None: ...
```

**Estimated**: 1 agent, ~45 min

---

## Phase 4: Service Container

**Goal**: Centralize service creation and dependency injection

**Files to Create**:
- `impl/claude/agents/i/services/container.py` (~100 LOC)
- Update `impl/claude/agents/i/services/__init__.py`

**DashboardServices**:
```python
@dataclass
class DashboardServices:
    """Service container for dependency injection."""
    state_manager: StateManager
    nav_controller: NavigationController
    event_bus: EventBus
    metrics_collector: MetricsCollector | None = None

    @classmethod
    def create(cls, app: App, demo_mode: bool = False) -> "DashboardServices":
        event_bus = EventBus.get()
        state_manager = StateManager()
        nav_controller = NavigationController(app, state_manager)

        return cls(
            state_manager=state_manager,
            nav_controller=nav_controller,
            event_bus=event_bus,
        )
```

**Estimated**: 1 agent, ~20 min

---

## Phase 5: The Gentle Eye

**Goal**: Non-violent screen transitions and visual polish

**Files to Create**:
- `impl/claude/agents/i/screens/transitions.py` (~150 LOC)
- `impl/claude/agents/i/theme/temperature.py` (~80 LOC)
- Update existing screens to declare ANCHOR

**TransitionStyle**:
```python
class TransitionStyle(Enum):
    CROSSFADE = "crossfade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    MORPH = "morph"

class GentleNavigator:
    def transition_to(
        self,
        target: str,
        style: TransitionStyle = TransitionStyle.CROSSFADE,
        anchor: str | None = None,
    ) -> None: ...
```

**Temperature System**:
```python
class TemperatureShift:
    NEUTRAL = "#f5f0e6"  # Warm white
    COOL = "#e6f0f5"     # Calm, waiting
    WARM = "#f5e6e0"     # Active, processing

STATE_TEMPERATURES = {
    "idle": TemperatureShift.COOL,
    "processing": TemperatureShift.WARM,
    "success": TemperatureShift.NEUTRAL,
}
```

**Estimated**: 1 agent, ~40 min

---

## Phase 6: Integration & Migration

**Goal**: Wire everything together and migrate existing screens

**Steps**:
1. Update DashboardApp to use mixins
2. Update existing screens to inherit from KgentsScreen
3. Wire EventBus subscriptions in on_mount()
4. Add ANCHOR declarations to all screens
5. Run full test suite

**Files to Modify**:
- `impl/claude/agents/i/screens/dashboard.py`
- `impl/claude/agents/i/screens/cockpit.py`
- `impl/claude/agents/i/screens/observatory.py`
- `impl/claude/agents/i/screens/flux.py`
- `impl/claude/agents/i/screens/terrarium.py`
- `impl/claude/agents/i/screens/mri.py`
- `impl/claude/agents/i/screens/loom.py`

**Estimated**: 1-2 agents, ~60 min

---

## Execution Strategy

### Parallel Opportunities

**Wave 1** (can run in parallel):
- Phase 1: EventBus Foundation
- Phase 2: Base Screen

**Wave 2** (depends on Wave 1):
- Phase 3: Mixin Decomposition (needs base screen)
- Phase 4: Service Container (needs EventBus)

**Wave 3** (depends on Wave 2):
- Phase 5: Gentle Eye (can start after Phase 2)
- Phase 6: Integration (needs all previous phases)

### Stopping Points

1. **After Wave 1**: EventBus + Base Screen complete
   - Tests pass, patterns established
   - Showcase: New files, test coverage

2. **After Wave 2**: Mixins + Service Container complete
   - DashboardApp decomposed
   - Showcase: Cleaner architecture, better testability

3. **After Wave 3**: Full integration
   - All screens migrated
   - Showcase: Working dashboard with all features

---

## Verification Commands

```bash
# After each phase
cd impl/claude && uv run pytest agents/i/services/_tests/ -v
cd impl/claude && uv run pytest agents/i/screens/_tests/ -v
cd impl/claude && uv run mypy agents/i/

# Integration test
kg dashboard --demo
# Press 1-6, Tab, f, d, m, ?
# All keys should work regardless of active screen
```

---

## Risk Mitigation

1. **Backward Compatibility**: Keep old patterns working during migration
2. **Incremental Testing**: Test each phase before moving on
3. **Fallback**: If EventBus causes issues, screens can still use direct calls

---

## Success Criteria

- [ ] EventBus singleton with full test coverage
- [ ] KgentsScreen base with key passthrough working
- [ ] DashboardApp < 400 LOC (down from 937)
- [ ] All keybindings work from any screen
- [ ] Mypy clean
- [ ] All existing tests pass
- [ ] Manual verification: kg dashboard --demo
