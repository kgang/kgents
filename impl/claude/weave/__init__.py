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

from .causal_cone import CausalCone, CausalConeStats, compute_cone_stats
from .dependency import DependencyGraph
from .economics import (
    BudgetConsumption,
    BudgetPolicy,
    BudgetStats,
    BudgetType,
    TurnBudgetTracker,
    create_default_tracker,
)
from .event import Event
from .metrics import (
    AgentCompressionStats,
    CompressionEvent,
    CompressionMetrics,
    estimate_tokens,
    get_events,
    get_metrics,
    log_compression,
    reset_metrics,
)
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
from .turn import Turn, TurnType, YieldTurn
from .weave import TheWeave
from .yield_handler import (
    ApprovalResult,
    ApprovalStatus,
    ApprovalStrategy,
    YieldHandler,
    compute_risk_score,
    should_yield,
)

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
    # Turn-gents Protocol
    "Turn",
    "TurnType",
    "YieldTurn",
    "CausalCone",
    "CausalConeStats",
    "compute_cone_stats",
    # Yield Governance
    "YieldHandler",
    "ApprovalStrategy",
    "ApprovalStatus",
    "ApprovalResult",
    "should_yield",
    "compute_risk_score",
    # Economics
    "TurnBudgetTracker",
    "BudgetType",
    "BudgetConsumption",
    "BudgetStats",
    "BudgetPolicy",
    "create_default_tracker",
    # Compression Metrics (H1 Validation)
    "CompressionEvent",
    "CompressionMetrics",
    "AgentCompressionStats",
    "log_compression",
    "get_metrics",
    "reset_metrics",
    "get_events",
    "estimate_tokens",
]
