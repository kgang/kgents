"""
The Weave - Concurrent History via Trace Monoids.

This module replaces linear ContextWindow with TraceMonoid-backed
concurrent history that captures independent vs dependent events.

Core Components:
- Event: A single event in the Weave
- TraceMonoid: Mathematical foundation for concurrent history
- DependencyGraph: Graph utilities for dependency analysis
- TheWeave: High-level API for Weave operations
- StaticCallGraph: AST-based call graph analysis

Mathematical Foundation:
A Trace Monoid captures concurrent history where:
- Independent events (a, b) can commute: ab = ba
- Dependent events must maintain order: ab != ba

This enables:
- Multi-agent concurrent execution
- Subjective time perspectives per agent
- Synchronization points (knots)
"""

from .dependency import DependencyGraph
from .event import Event
from .runtime_trace import TraceCollector, TraceEvent, TraceFilter, trace_function
from .static_trace import CallSite, FunctionDef, StaticCallGraph
from .trace_monoid import TraceMonoid
from .trace_renderer import (
    RenderConfig,
    TraceRenderer,
    render_diff,
    render_graph,
    render_trace,
)
from .weave import TheWeave

__all__ = [
    "Event",
    "TraceMonoid",
    "DependencyGraph",
    "TheWeave",
    "StaticCallGraph",
    "CallSite",
    "FunctionDef",
    "TraceCollector",
    "TraceEvent",
    "TraceFilter",
    "trace_function",
    "TraceRenderer",
    "RenderConfig",
    "render_graph",
    "render_trace",
    "render_diff",
]
