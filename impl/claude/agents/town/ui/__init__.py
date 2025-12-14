"""
Agent Town UI: THE MESA Viewing Modes.

The control room isn't about control. It's a seance table
where we glimpse what we've summoned.

Design Philosophy (from three traditions):
1. Immersive Theater (MIT/Punchdrunk): Emergent discovery, masked wandering
2. AI Agent Observability (OpenTelemetry): Real-time traces, memory inspection
3. Narrative Visualization (WhatIF): Story graphs, branching paths

The Inversion: Unlike Westworld's God's-eye control room,
our MESA respects Glissant's opacity. You cannot see everything.
Citizens have the right to remain mysterious.

Components:
- mesa.py: Town overview (Rich-based terminal UI)
- lens.py: LOD zoom per citizen
- trace.py: OpenTelemetry span visualization
- widgets.py: Shared Rich widgets
"""

from .lens import LensView, render_lens
from .mesa import MesaView, render_mesa
from .trace import TraceView, render_trace

__all__ = [
    "MesaView",
    "render_mesa",
    "LensView",
    "render_lens",
    "TraceView",
    "render_trace",
]
