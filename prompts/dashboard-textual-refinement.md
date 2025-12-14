# Dashboard Textual Architecture Refinement

> *"Keys are being eaten. Services are tangled. The future demands clarity."*

**Principle**: Port battle-tested patterns from zenportal for AI-agent-friendly development.
**Prerequisites**: Read `~/git/zenportal/zen_portal/services/events.py` and `~/git/zenportal/zen_portal/screens/main.py`

---

## Design Philosophy: The Gentle Eye

> *"Guide the eye where it needs to go, sans screen violence."*

The dashboard should model the user's eye movement and lead it gently. No jarring transitions. No cognitive whiplash. The screen should breathe.

### The Eye Movement Model

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. ANCHOR POINT                                               │
│      The eye lands here first.                                  │
│      Status bar, breadcrumb, or focused element.                │
│      Never move this during transitions.                        │
│                                                                 │
│   2. PRIMARY SCAN PATH                                          │
│      F-pattern for lists, Z-pattern for dashboards.             │
│      Content should flow WITH this pattern, not against it.     │
│                                                                 │
│   3. PERIPHERAL AWARENESS                                       │
│      Subtle indicators at edges.                                │
│      The eye notices change without looking directly.           │
│      Use color temperature shifts, not flashing.                │
│                                                                 │
│   4. FOCUS INVITATION                                           │
│      When attention is needed, don't grab—invite.               │
│      Gentle luminance increase > sudden appearance.             │
│      Animation duration: 150-300ms (perceptible but not slow).  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen Violence (Anti-Patterns)

| Violence | Symptom | Gentle Alternative |
|----------|---------|-------------------|
| Flash | Sudden bright element | Fade in over 200ms |
| Jump | Content shifts position | Crossfade in place |
| Overwhelm | Too much changes at once | Stagger updates 50ms apart |
| Orphan | Eye has nowhere to rest | Always maintain anchor |
| Trap | Modal blocks all context | Overlay preserves peripheral |

### Implementation: Transition Choreography

```python
# agents/i/screens/transitions.py

from enum import Enum
from dataclasses import dataclass

class TransitionStyle(Enum):
    """How screens transition."""
    CROSSFADE = "crossfade"      # Old fades out as new fades in (default)
    SLIDE_LEFT = "slide_left"    # Drill down (more detail)
    SLIDE_RIGHT = "slide_right"  # Drill up (less detail)
    MORPH = "morph"              # Element expands into screen

@dataclass
class ScreenTransition:
    """Choreographed screen transition."""
    style: TransitionStyle
    duration_ms: int = 200
    anchor_element: str | None = None  # Element that stays fixed
    stagger_ms: int = 50  # Delay between element animations

class GentleNavigator:
    """Navigate between screens without violence."""

    def transition_to(
        self,
        target: str,
        style: TransitionStyle = TransitionStyle.CROSSFADE,
        anchor: str | None = None,
    ) -> None:
        """
        Transition to target screen with choreography.

        The anchor element (if specified) remains visually stable
        while the rest of the screen transforms around it.
        """
        ...
```

### The Anchor Principle

Every screen must declare its **anchor**—the stable point the eye can trust:

```python
class CockpitScreen(KgentsScreen):
    """Single agent operational view."""

    # The agent name header is the anchor
    # It never moves, never flashes, always readable
    ANCHOR = "#agent-header"

    # When transitioning FROM this screen, the anchor
    # morphs into the destination's anchor (if compatible)
    ANCHOR_MORPHS_TO = {
        "observatory": "#agent-card",  # Header shrinks into card
        "mri": "#agent-header",        # Header stays (same position)
    }
```

### Peripheral Awareness Zones

```
┌─────────────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░                         HEADER                              ░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░ P ░                                                     ░ P ░ │
│ ░ E ░                                                     ░ E ░ │
│ ░ R ░                    FOCUS ZONE                       ░ R ░ │
│ ░ I ░                                                     ░ I ░ │
│ ░ P ░              (primary content here)                 ░ P ░ │
│ ░ H ░                                                     ░ H ░ │
│ ░ E ░                                                     ░ E ░ │
│ ░ R ░                                                     ░ R ░ │
│ ░ A ░                                                     ░ A ░ │
│ ░ L ░                                                     ░ L ░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░                        STATUS BAR                           ░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────────────────────────────┘

PERIPHERAL ZONES (░):
- Changes here are noticed without direct attention
- Use for: navigation hints, status indicators, key reminders
- Color temperature shifts (warm → cool) signal state changes
- Never use motion in periphery (too distracting)

FOCUS ZONE:
- Primary content lives here
- Changes should be intentional and choreographed
- If multiple things update, stagger them
```

### Color Temperature for State

Instead of jarring color changes, shift **temperature**:

```python
# agents/i/theme/temperature.py

class TemperatureShift:
    """Subtle color temperature shifts for state changes."""

    # Base palette (neutral)
    NEUTRAL = "#f5f0e6"  # Warm white

    # Temperature shifts (same luminance, different hue)
    COOL = "#e6f0f5"     # Slightly blue - calm, waiting
    WARM = "#f5e6e0"     # Slightly red - active, processing

    # The eye perceives these as "mood" not "alert"
    # Use for background tints, not foreground elements

STATE_TEMPERATURES = {
    "idle": TemperatureShift.COOL,
    "processing": TemperatureShift.WARM,
    "success": TemperatureShift.NEUTRAL,  # Return to baseline
    "error": TemperatureShift.WARM,       # Warm, not red flash
}
```

### The Breath Pattern

Screens should "breathe"—subtle rhythmic indication of life without distraction:

```python
class BreathingIndicator(Static):
    """Subtle life indicator that doesn't demand attention."""

    DEFAULT_CSS = """
    BreathingIndicator {
        /* Opacity oscillates 0.3 → 0.6 over 4 seconds */
        /* Slow enough to be subliminal, fast enough to show life */
        animation: breathe 4s ease-in-out infinite;
    }

    @keyframes breathe {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    """
```

---

## The Problem

The kgents dashboard has keybinding issues and architectural friction:

1. **Keybindings eaten**: Number keys (1-6) and special keys get consumed by nested screens before reaching DashboardApp
2. **Tight coupling**: Screens directly call each other's methods
3. **No event bus**: State changes require manual refresh cascades
4. **Monolithic screens**: DashboardApp is 1000+ lines with growing complexity
5. **No base screen**: Each screen reinvents notification, focus, lifecycle

---

## The Solution: Port zenportal Patterns

### Pattern 1: EventBus for Decoupled Communication

**From zenportal**: `services/events.py`

```python
# services/events.py - Central event bus
@dataclass
class Event:
    """Base class for all domain events."""
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ScreenNavigationEvent(Event):
    """Emitted when screen navigation is requested."""
    target_screen: str = ""  # "observatory", "cockpit", etc.
    source_screen: str = ""

@dataclass
class AgentFocusedEvent(Event):
    """Emitted when an agent is focused for drill-down."""
    agent_id: str = ""

class EventBus:
    """Singleton event bus for service-to-UI communication."""
    _instance: "EventBus | None" = None

    def subscribe(self, event_type: type[E], handler: Callable[[E], None]) -> None: ...
    def emit(self, event: Event) -> None: ...
```

**Benefits**:
- Screens emit events instead of calling methods directly
- Any screen can subscribe to navigation events
- DashboardApp becomes the single navigation controller
- Easy to add telemetry/logging for all events

### Pattern 2: Base Screen with Focus Management

**From zenportal**: `screens/base.py`

```python
# agents/i/screens/base.py
class KgentsScreen(Screen):
    """Base screen with notification rack and key passthrough."""

    DEFAULT_CSS = """
    KgentsScreen {
        layers: base overlay notification;
    }
    """

    # Keys that should ALWAYS bubble to parent App
    PASSTHROUGH_KEYS = {"1", "2", "3", "4", "5", "6", "tab", "f", "d", "m", "?", "q"}

    def on_key(self, event: Key) -> None:
        """Pass global navigation keys to parent app."""
        if event.key in self.PASSTHROUGH_KEYS:
            event.stop()  # Stop propagation to children
            # Let it bubble UP to App
            return
        # Handle screen-specific keys
        super().on_key(event)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield KgentsNotificationRack(id="notifications")
```

**Benefits**:
- All screens get consistent key passthrough
- Notification system is automatic
- Focus management is centralized

### Pattern 3: Screen Mixins for Maintainability

**From zenportal**: `screens/main_actions.py`, `screens/main_templates.py`

```python
# agents/i/screens/dashboard_navigation.py
class DashboardNavigationMixin:
    """Navigation actions for DashboardApp."""

    _SCREEN_ORDER = ["observatory", "dashboard", "cockpit", "flux", "loom", "mri"]
    _current_screen_idx: int = 1

    def action_go_screen_1(self) -> None: self._navigate_to("observatory")
    def action_go_screen_2(self) -> None: self._navigate_to("dashboard")
    # ... etc

    def action_cycle_next(self) -> None:
        self._current_screen_idx = (self._current_screen_idx + 1) % len(self._SCREEN_ORDER)
        self._navigate_to(self._SCREEN_ORDER[self._current_screen_idx])

    def _navigate_to(self, screen_name: str) -> None:
        from services.events import EventBus, ScreenNavigationEvent
        EventBus.get().emit(ScreenNavigationEvent(target_screen=screen_name))

# agents/i/screens/dashboard_screens.py
class DashboardScreensMixin:
    """Screen factory methods for DashboardApp."""

    def _create_observatory(self) -> None: ...
    def _create_cockpit(self) -> None: ...
    def _create_flux(self) -> None: ...
```

**Then compose**:
```python
class DashboardApp(DashboardNavigationMixin, DashboardScreensMixin, App):
    """Main dashboard application."""
    ...
```

**Benefits**:
- Each concern in its own file
- AI agents can modify one mixin without touching others
- Clear boundaries for testing

### Pattern 4: Service Container for Dependency Injection

**From zenportal**: `app.py:Services`

```python
# agents/i/services/__init__.py
@dataclass
class DashboardServices:
    """Service container for dependency injection."""

    state_manager: StateManager
    nav_controller: NavigationController
    hotdata: HotDataRegistry
    event_bus: EventBus

    @classmethod
    def create(cls, demo_mode: bool = False) -> "DashboardServices":
        event_bus = EventBus.get()
        state_manager = StateManager()
        nav_controller = NavigationController()

        if demo_mode:
            load_all_demo_fixtures()

        return cls(
            state_manager=state_manager,
            nav_controller=nav_controller,
            hotdata=get_hotdata_registry(),
            event_bus=event_bus,
        )
```

**Benefits**:
- All services created in one place
- Easy to swap implementations for testing
- Demo mode is a configuration, not scattered conditionals

---

## Implementation Steps

### Phase 1: EventBus Foundation

1. Create `agents/i/services/events.py` with:
   - `Event` base class
   - `ScreenNavigationEvent`
   - `AgentFocusedEvent`
   - `MetricsUpdatedEvent`
   - `EventBus` singleton

2. Add tests in `agents/i/services/_tests/test_events.py`

### Phase 2: Base Screen

1. Create `agents/i/screens/base.py` with:
   - `KgentsScreen` with `PASSTHROUGH_KEYS`
   - `KgentsModalScreen` for modals
   - Notification integration
   - `ANCHOR` class attribute for eye stability

2. Migrate existing screens to inherit from `KgentsScreen`

### Phase 3: Mixin Decomposition

1. Extract from `DashboardApp`:
   - `DashboardNavigationMixin` → `dashboard_navigation.py`
   - `DashboardScreensMixin` → `dashboard_screens.py`
   - `DashboardHelpMixin` → `dashboard_help.py`

2. Compose `DashboardApp` from mixins

### Phase 4: Service Container

1. Create `agents/i/services/__init__.py` with `DashboardServices`

2. Inject services into `DashboardApp.__init__()`

3. Wire EventBus subscriptions in `on_mount()`

### Phase 5: The Gentle Eye

1. Create `agents/i/screens/transitions.py` with:
   - `TransitionStyle` enum
   - `ScreenTransition` dataclass
   - `GentleNavigator` for choreographed transitions

2. Create `agents/i/theme/temperature.py` with:
   - `TemperatureShift` color constants
   - `STATE_TEMPERATURES` mapping

3. Update each screen to declare:
   - `ANCHOR` - the stable element
   - `ANCHOR_MORPHS_TO` - transition mapping

4. Add `BreathingIndicator` widget for subtle life indication

5. Audit all screens for screen violence:
   - Replace flashes with fades
   - Replace jumps with crossfades
   - Add stagger to bulk updates
   - Ensure peripheral zones don't use motion

---

## Key Insight: Keybinding Flow

The current problem:

```
DashboardApp.BINDINGS defines "1" → action_go_screen_1
    ↓ push_screen()
DashboardScreen.on_key() catches "1" for panel focus
    ↓ event.stop()
Key never reaches DashboardApp
```

The fix:

```
DashboardApp.BINDINGS defines "1" → action_go_screen_1
    ↓ push_screen()
DashboardScreen(KgentsScreen)
    ↓ on_key() checks PASSTHROUGH_KEYS
    ↓ if "1" in PASSTHROUGH_KEYS: return (don't stop)
    ↓ else: handle locally
Key bubbles UP to DashboardApp → action_go_screen_1 fires
```

Alternative: Use Textual's `priority_bindings`:

```python
class DashboardApp(App):
    BINDINGS = [
        Binding("1", "go_screen_1", "Observatory", priority=True),  # priority=True!
        ...
    ]
```

---

## AI Agent Development Benefits

After refactoring:

1. **Adding a new screen**:
   - Add event type to `services/events.py`
   - Add factory method to `DashboardScreensMixin`
   - Add keybinding to `DashboardNavigationMixin`
   - AI agent touches 3 small files, not 1 giant file

2. **Fixing navigation bugs**:
   - Check `KgentsScreen.PASSTHROUGH_KEYS`
   - Check `EventBus` subscription in `on_mount`
   - Clear debugging path

3. **Adding telemetry**:
   - Subscribe to `EventBus` in a new `TelemetryService`
   - No changes to existing screens

---

## Verification

```bash
# All tests pass
cd impl/claude && uv run pytest agents/i/ -v

# Mypy clean
cd impl/claude && uv run mypy agents/i/screens/

# Manual test
kg dashboard --demo
# Press 1-6, Tab, f, d, m, ?
# All keys should work regardless of active screen
```

---

## References

- zenportal EventBus: `~/git/zenportal/zen_portal/services/events.py`
- zenportal MainScreen: `~/git/zenportal/zen_portal/screens/main.py`
- zenportal Base: `~/git/zenportal/zen_portal/screens/base.py`
- zenportal Tests: `~/git/zenportal/zen_portal/tests/test_events.py`

---

## The Mantra

> *"Services emit, screens subscribe, the bus delivers. Keys bubble up, never get eaten."*

> *"Guide the eye gently. The screen breathes. No violence."*

---

## The Zen of Dashboard Development

```
The screen is not a battleground.
It is a garden.

Elements do not fight for attention—
they take turns speaking.

The eye is not grabbed—
it is invited.

Transitions do not jar—
they flow.

The anchor holds steady
while the world transforms around it.

When something must change,
it fades in like morning light,
not like a slap.

The peripheral whispers.
The focus zone speaks clearly.
Nothing shouts.

This is the way.
```

---

*Execute /hydrate before each session to maintain context.*
