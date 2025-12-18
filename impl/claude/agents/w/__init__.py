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

# Middleware Bus (Phase 0 cross-pollination)
from .bus import (
    AgentRegistry,
    BaseInterceptor,
    BlockingInterceptor,
    BusMessage,
    DispatchResult,
    Interceptor,
    InterceptorResult,
    LoggingInterceptor,
    MessagePriority,
    MiddlewareBus,
    PassthroughInterceptor,
    create_bus,
)

# Cortex Dashboard (Instance DB Phase 6)
from .cortex_dashboard import (
    CortexDashboard,
    CortexDashboardConfig,
    DashboardPanel as CortexDashboardPanel,
    SparklineData,
    create_cortex_dashboard,
    create_minimal_dashboard as create_minimal_cortex_dashboard,
)
from .fidelity import (
    DocumentarianAdapter,
    Fidelity,
    FidelityAdapter,
    LiveWireAdapter,
    TeletypeAdapter,
    detect_fidelity,
    get_adapter,
)

# Core Interceptors (Phase 1 cross-pollination)
from .interceptors import (
    CostOracle,
    EntropyChecker,
    InMemoryObservationSink,
    InMemoryTreasury,
    MeteringInterceptor,
    # Telemetry (O-gent)
    Observation,
    ObservationSink,
    PersonaInterceptor,
    # Persona (K-gent)
    PersonaPriors,
    SafetyInterceptor,
    # Safety (J-gent)
    SafetyThresholds,
    SimpleCostOracle,
    SimpleEntropyChecker,
    TelemetryInterceptor,
    # Metering (B-gent)
    TokenCost,
    Treasury,
    # Factory
    create_standard_interceptors,
)
from .protocol import (
    WireEvent,
    WireMetrics,
    WireObservable,
    WireReader,
    WireState,
)
from .server import WireServer, serve_agent

# Value Dashboard (B-gent economics visualization)
from .value_dashboard import (
    DashboardPanel,
    DashboardState,
    RoCSnapshot,
    TensorSnapshot,
    TokenSnapshot,
    ValueDashboard,
    VoISnapshot,
    create_minimal_dashboard,
    create_value_dashboard,
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
    # Middleware Bus
    "BusMessage",
    "InterceptorResult",
    "Interceptor",
    "BaseInterceptor",
    "PassthroughInterceptor",
    "LoggingInterceptor",
    "BlockingInterceptor",
    "AgentRegistry",
    "DispatchResult",
    "MiddlewareBus",
    "MessagePriority",
    "create_bus",
    # Core Interceptors
    "TokenCost",
    "CostOracle",
    "Treasury",
    "InMemoryTreasury",
    "SimpleCostOracle",
    "MeteringInterceptor",
    "SafetyThresholds",
    "EntropyChecker",
    "SimpleEntropyChecker",
    "SafetyInterceptor",
    "Observation",
    "ObservationSink",
    "InMemoryObservationSink",
    "TelemetryInterceptor",
    "PersonaPriors",
    "PersonaInterceptor",
    "create_standard_interceptors",
    # Cortex Dashboard (Instance DB Phase 6)
    "CortexDashboardPanel",
    "SparklineData",
    "CortexDashboardConfig",
    "CortexDashboard",
    "create_cortex_dashboard",
    "create_minimal_cortex_dashboard",
]
