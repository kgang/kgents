"""I-gent v2.5 Data - State, Registry, O-gent Polling, Visual Hints, Cognitive Loom, Dashboard Collectors, Pheromone Trails, and Weather."""

from .core_types import Phase
from .dashboard_collectors import (
    DashboardMetrics,
    FluxMetrics,
    KgentMetrics,
    MetabolismMetrics,
    MetricsObservable,
    TraceEntry,
    TriadMetrics,
    collect_metrics,
    create_demo_metrics,
    create_random_metrics,
)
from .hint_registry import HintRegistry, get_hint_registry, reset_hint_registry
from .hints import VisualHint, validate_hint
from .loom import CognitiveBranch, CognitiveTree
from .ogent import (
    HealthLevel,
    OgentPoller,
    XYZHealth,
    create_mock_health,
    render_xyz_bar,
    render_xyz_compact,
    value_to_health_level,
)
from .pheromone import (
    MESSAGE_COLORS,
    MessageType,
    PheromoneEmission,
    PheromoneManager,
    PheromoneTrail,
    create_demo_trails,
)
from .registry import (
    AgentObservable,
    AgentRegistry,
    AgentStatus,
    MemoryRegistry,
    MockObservable,
    RegisteredAgent,
    RegistryCallback,
    RegistryEvent,
    RegistryEventType,
    create_demo_registry,
    create_demo_registry_async,
)
from .state import AgentSnapshot, FluxState, SessionState, create_demo_flux_state
from .weather import (
    OBLIQUE_STRATEGIES,
    Forecast,
    PressureLevel,
    SystemMetrics,
    Weather,
    WeatherCondition,
    WeatherEngine,
    WindDirection,
    create_demo_weather,
)

__all__ = [
    # Types
    "Phase",
    # State
    "FluxState",
    "AgentSnapshot",
    "SessionState",
    "create_demo_flux_state",
    # Registry
    "AgentObservable",
    "AgentRegistry",
    "AgentStatus",
    "MemoryRegistry",
    "MockObservable",
    "RegisteredAgent",
    "RegistryCallback",
    "RegistryEvent",
    "RegistryEventType",
    "create_demo_registry",
    "create_demo_registry_async",
    # O-gent Polling
    "HealthLevel",
    "OgentPoller",
    "XYZHealth",
    "create_mock_health",
    "render_xyz_bar",
    "render_xyz_compact",
    "value_to_health_level",
    # Visual Hints (Track C: Heterarchical UI)
    "VisualHint",
    "validate_hint",
    "HintRegistry",
    "get_hint_registry",
    "reset_hint_registry",
    # Cognitive Loom (Track B: Temporal Topology)
    "CognitiveBranch",
    "CognitiveTree",
    # Dashboard Collectors
    "DashboardMetrics",
    "KgentMetrics",
    "MetabolismMetrics",
    "TriadMetrics",
    "FluxMetrics",
    "TraceEntry",
    "collect_metrics",
    "create_demo_metrics",
    "create_random_metrics",
    "MetricsObservable",
    # Pheromone Trails (Stigmergic Communication)
    "PheromoneTrail",
    "PheromoneManager",
    "PheromoneEmission",
    "MessageType",
    "MESSAGE_COLORS",
    "create_demo_trails",
    # Weather (System State Metaphor)
    "Weather",
    "WeatherEngine",
    "WeatherCondition",
    "PressureLevel",
    "WindDirection",
    "SystemMetrics",
    "Forecast",
    "OBLIQUE_STRATEGIES",
    "create_demo_weather",
]
