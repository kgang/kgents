"""
Reactive Wiring: Reality connections for the reactive substrate.

Wave 5 - Reality Wiring:
- Clock: Central time synchronization
- Subscriptions: Throttled reactive updates
- Adapters: Transform runtime data to widget states
- Bindings: AGENTESE path connections

Wave 6 - Interactive Behaviors:
- Focus: Track focused widget with tab navigation
- Keyboard: Arrow keys, hotkeys, and key bindings
- Selection: Single/multi-select with bulk actions
- Interactions: Bidirectional widget-parent communication

"The screen is the story. Interaction is dialogue."
"""

from agents.i.reactive.wiring.adapters import (
    AgentRuntimeAdapter,
    SoulAdapter,
    YieldAdapter,
    create_dashboard_state,
)
from agents.i.reactive.wiring.bindings import (
    AGENTESEBinding,
    BindingConfig,
    PathBinding,
    create_binding,
)
from agents.i.reactive.wiring.clock import (
    Clock,
    ClockConfig,
    ClockState,
    create_clock,
)
from agents.i.reactive.wiring.interactions import (
    FocusableItem,
    FocusDirection,
    FocusState,
    Interaction,
    InteractionHandler,
    InteractionType,
    InteractiveDashboardState,
    InteractiveEventType,
    KeyBinding,
    KeyboardNav,
    KeyCode,
    KeyEvent,
    KeyModifiers,
    SelectionMode,
    SelectionState,
    create_focus_state,
    create_interaction_handler,
    create_interactive_dashboard,
    create_keyboard_nav,
    create_selection_state,
)
from agents.i.reactive.wiring.subscriptions import (
    EventBus,
    Subscription,
    ThrottledSignal,
    create_event_bus,
)

__all__ = [
    # Clock
    "Clock",
    "ClockConfig",
    "ClockState",
    "create_clock",
    # Subscriptions
    "EventBus",
    "Subscription",
    "ThrottledSignal",
    "create_event_bus",
    # Adapters
    "AgentRuntimeAdapter",
    "SoulAdapter",
    "YieldAdapter",
    "create_dashboard_state",
    # Bindings
    "AGENTESEBinding",
    "BindingConfig",
    "PathBinding",
    "create_binding",
    # Focus (Wave 6)
    "FocusDirection",
    "FocusState",
    "FocusableItem",
    "create_focus_state",
    # Keyboard (Wave 6)
    "KeyBinding",
    "KeyCode",
    "KeyEvent",
    "KeyModifiers",
    "KeyboardNav",
    "create_keyboard_nav",
    # Selection (Wave 6)
    "SelectionMode",
    "SelectionState",
    "create_selection_state",
    # Interactions (Wave 6)
    "Interaction",
    "InteractionHandler",
    "InteractionType",
    "InteractiveEventType",
    "create_interaction_handler",
    # Interactive Dashboard (Wave 6)
    "InteractiveDashboardState",
    "create_interactive_dashboard",
]
