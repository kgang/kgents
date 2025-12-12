"""
Terrarium: The Agent Server Web Gateway.

The terrarium is not a cage. It is a window into life.
The mirror shows without disturbing.

The Mirror Protocol:
- /perturb (The Beam): High entropy, auth required, injects Perturbation
- /observe (The Reflection): Zero entropy to agent, broadcast mirror

The agent emits to a HolographicBuffer once. The buffer broadcasts to N clients.
Slow clients don't slow the agent.

Phase 2 - Prism REST Bridge:
- PrismRestBridge auto-generates REST endpoints from CLICapable agents
- Uses Prism's introspection for type-safe JSON schemas

Phase 3 - I-gent Widget Metrics:
- MetricsManager emits live metabolism metrics to observers
- Metrics: pressure (backlog), flow (throughput), temperature (heat)
- /api/{agent_id}/metrics endpoint for REST access

Usage:
    from protocols.terrarium import Terrarium, HolographicBuffer, PrismRestBridge

    # Create gateway
    terrarium = Terrarium()

    # Register FluxAgent with mirror
    terrarium.register_agent(agent_id, flux_agent)

    # Start metrics emission when agent is running
    terrarium.start_agent_metrics(agent_id)

    # Mount CLICapable agent as REST
    bridge = PrismRestBridge()
    bridge.mount(terrarium.app, grammar_cli)

    # Run server
    import uvicorn
    uvicorn.run(terrarium.app, host="0.0.0.0", port=8080)

See: plans/agents/terrarium.md
"""

from __future__ import annotations

from .config import TerrariumConfig
from .events import (
    EventType,
    SemaphoreEvent,
    TerriumEvent,
    make_error_event,
    make_metabolism_event,
    make_result_event,
)
from .gateway import Terrarium
from .metrics import (
    MetricsManager,
    calculate_flow,
    calculate_pressure,
    calculate_temperature,
    emit_fever_alert,
    emit_metrics_loop,
)
from .mirror import HolographicBuffer
from .rest_bridge import PrismRestBridge

__all__ = [
    # Core
    "Terrarium",
    "HolographicBuffer",
    "TerrariumConfig",
    # Phase 2: REST Bridge
    "PrismRestBridge",
    # Phase 3: Metrics
    "MetricsManager",
    "emit_metrics_loop",
    "calculate_pressure",
    "calculate_flow",
    "calculate_temperature",
    "emit_fever_alert",
    # Events
    "EventType",
    "TerriumEvent",
    "SemaphoreEvent",
    "make_result_event",
    "make_error_event",
    "make_metabolism_event",
]
