"""
S-gents: State Agents for state threading.

This package provides the categorical State Monad lifted to the agent domain.

Core Insight:
    State is orthogonal to persistence.
    - D-gent: WHERE state lives (memory, file, database)
    - S-gent: HOW state threads through computation

The Symbiont pattern is S >> D: state threading backed by persistence.

Architecture:
    - StateBackend[S]: Minimal protocol (load/save only)
    - StateFunctor: UniversalFunctor for state threading
    - StatefulAgent: Agent with transparent state management
    - Adapters: Bridge to existing storage (VolatileAgent, DgentProtocol)

Usage:
    # Create state backend
    backend = MemoryStateBackend(initial={"count": 0})

    # Create functor
    state_functor = StateFunctor.create(backend=backend)

    # Lift pure logic to stateful agent
    def counter_logic(input: str, state: dict) -> tuple[str, dict]:
        count = state["count"]
        return f"Count: {count}", {"count": count + 1}

    counter = state_functor.lift_logic(counter_logic)

    # Use the agent
    result = await counter.invoke("tick")  # "Count: 0"
    result = await counter.invoke("tick")  # "Count: 1"

Composition with Flux:
    FluxState = StateFunctor.compose_flux(backend)
    flux_counter = FluxState(counter_agent)

    async for result in flux_counter.start(events):
        print(result)  # Each event with state threading

See Also:
    - spec/s-gents/README.md — S-gent specification
    - spec/s-gents/state-functor.md — StateFunctor spec
    - spec/s-gents/composition.md — Composition patterns
    - spec/s-gents/laws.md — Functor laws
"""

# Protocol
# Adapters
from .adapters import (
    DataAgentBackend,
    DgentStateBackend,
    MemoryStateBackend,
)

# Config
from .config import StateConfig
from .protocol import StateBackend

# Core
from .state_functor import StatefulAgent, StateFunctor

__all__ = [
    # Protocol
    "StateBackend",
    # Config
    "StateConfig",
    # Core
    "StateFunctor",
    "StatefulAgent",
    # Adapters
    "MemoryStateBackend",
    "DataAgentBackend",
    "DgentStateBackend",
]
