"""
S-gents: State Agents for state threading.

DEPRECATED: This module has been conceptually consolidated into D-gent.
The State Functor is now documented as part of the C-gent functor catalog.

The preferred pattern is to use Symbiont (from agents.d):
    from agents.d import Symbiont, VolatileAgent

    def counter_logic(input: str, state: dict) -> tuple[str, dict]:
        count = state["count"]
        return f"Count: {count}", {"count": count + 1}

    memory = VolatileAgent(_state={"count": 0})
    counter = Symbiont(logic=counter_logic, memory=memory)
    result = await counter.invoke("tick")  # "Count: 0"

For backwards compatibility, all exports from this module remain available.
New code should use agents.d directly.

See Also:
    - spec/agents/functor-catalog.md §14 — State Functor specification
    - spec/d-gents/symbiont.md — Symbiont pattern documentation
    - agents.d.Symbiont — The canonical state+persistence pattern
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
