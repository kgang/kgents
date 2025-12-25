"""
W-gents: The Wire Agents (Radical Refinement Edition - 2025-12)

DEPRECATION NOTICE:
    Most of W-gent's functionality has been superseded by modern architecture:

    - MiddlewareBus → replaced by AGENTESE protocol
    - Interceptors → replaced by Witness Grant/Scope/Mark
    - Value Dashboard → replaced by Witness Garden
    - Cortex Dashboard → replaced by K-Block timeline
    - Agent Registry → replaced by @node decorator

    W-gent now has ONE purpose: Real-time process visualization for
    non-AGENTESE agents that emit to stdout/stderr.

Core Philosophy:
    Wire agents render invisible computation visible. They act as projection
    layers between external process streams and human observation.

Three Virtues:
    1. Transparency: Show what IS, not what we wish to see
    2. Ephemerality: Exist only during observation, leave no trace
    3. Non-Intrusion: Observe without affecting the observed

Usage:
    >>> from agents.w import observe_subprocess
    >>>
    >>> async for event in observe_subprocess(["python", "script.py"]):
    ...     print(f"[{event.level}] {event.message}")
"""

from .bridge import bridge_to_witness
from .observer import ProcessObserver, WireEvent, observe_subprocess
from .protocol import WireObservable  # Compatibility shim for O-gent

__all__ = [
    "ProcessObserver",
    "WireEvent",
    "observe_subprocess",
    "bridge_to_witness",
    "WireObservable",  # Deprecated - for O-gent compatibility only
]
