"""
Terrarium: The Agent Server Web Gateway.

The terrarium is not a cage. It is a window into life.
The mirror shows without disturbing.

The Mirror Protocol:
- /perturb (The Beam): High entropy, auth required, injects Perturbation
- /observe (The Reflection): Zero entropy to agent, broadcast mirror

The agent emits to a HolographicBuffer once. The buffer broadcasts to N clients.
Slow clients don't slow the agent.

Usage:
    from protocols.terrarium import Terrarium, HolographicBuffer

    # Create gateway
    terrarium = Terrarium()

    # Register an agent with its mirror
    terrarium.register_agent(agent_id, flux_agent)

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
from .mirror import HolographicBuffer

__all__ = [
    # Core
    "Terrarium",
    "HolographicBuffer",
    "TerrariumConfig",
    # Events
    "EventType",
    "TerriumEvent",
    "SemaphoreEvent",
    "make_result_event",
    "make_error_event",
    "make_metabolism_event",
]
