"""
Reactive Wiring: Reality connections for the reactive substrate.

Wave 5 - Reality Wiring:
- Clock: Central time synchronization
- Subscriptions: Throttled reactive updates
- Adapters: Transform runtime data to widget states
- Bindings: AGENTESE path connections

"The screen is the story. Reality wiring makes the story live."
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
]
