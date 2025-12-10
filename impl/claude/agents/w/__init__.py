"""
W-gents: The Wire Agents.

Wire agents render invisible computation visible. They act as projection layers
between an agent's internal execution stream and human observation.

Core concepts:
- Wire Protocol: How agents expose state (files, sockets, HTTP, stdout)
- Fidelity Levels: Teletype (raw), Documentarian (rendered), LiveWire (dashboard)
- Non-Intrusion: Zero performance impact, read-only observation

Three Virtues:
1. Transparency: Show what IS, not what we wish to see
2. Ephemerality: Exist only during observation, leave no trace
3. Non-Intrusion: Observe without affecting the observed

Example:
    >>> from agents.w import WireObservable, WireServer, Fidelity
    >>>
    >>> # Make an agent observable
    >>> class MyAgent(WireObservable):
    ...     def __init__(self):
    ...         super().__init__("my-agent")
    ...
    ...     def process(self):
    ...         self.update_state(phase="active", progress=0.5)
    ...         self.log_event("INFO", "process", "Working...")
    >>>
    >>> # Start observation server
    >>> server = WireServer("my-agent", port=8000)
    >>> await server.start()
    >>> # Browser opens to localhost:8000
"""

from .protocol import (
    WireObservable,
    WireState,
    WireEvent,
    WireMetrics,
    WireReader,
)
from .fidelity import (
    Fidelity,
    FidelityAdapter,
    TeletypeAdapter,
    DocumentarianAdapter,
    LiveWireAdapter,
    detect_fidelity,
    get_adapter,
)
from .server import WireServer, serve_agent

# Value Dashboard (B-gent economics visualization)
from .value_dashboard import (
    DashboardPanel,
    TokenSnapshot,
    TensorSnapshot,
    VoISnapshot,
    RoCSnapshot,
    DashboardState,
    ValueDashboard,
    create_value_dashboard,
    create_minimal_dashboard,
)

__all__ = [
    # Protocol
    "WireObservable",
    "WireState",
    "WireEvent",
    "WireMetrics",
    "WireReader",
    # Fidelity
    "Fidelity",
    "FidelityAdapter",
    "TeletypeAdapter",
    "DocumentarianAdapter",
    "LiveWireAdapter",
    "detect_fidelity",
    "get_adapter",
    # Server
    "WireServer",
    "serve_agent",
    # Value Dashboard
    "DashboardPanel",
    "TokenSnapshot",
    "TensorSnapshot",
    "VoISnapshot",
    "RoCSnapshot",
    "DashboardState",
    "ValueDashboard",
    "create_value_dashboard",
    "create_minimal_dashboard",
]
