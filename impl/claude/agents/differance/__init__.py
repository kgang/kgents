"""
Différance Engine: Traced Wiring Diagrams with Ghost Heritage.

Every kgents output has a lineage—decisions made, alternatives rejected, paths
not taken. The Différance Engine makes this lineage visible, navigable, and
generative.

Core Insight:
    Différance = difference + deferral. Every wiring decision simultaneously:
    1. Creates a difference (this path, not that one)
    2. Creates a deferral (the ghost path remains potentially explorable)

The trace monoid records both: what was chosen AND what was deferred.

Phase 1 (SPROUTING): Core types + monoid laws
Phase 2 (SPROUTING): TRACED_OPERAD + semantic preservation
Phase 3 (BLOOMING): GhostHeritageDAG + query methods

See: spec/protocols/differance.md
"""

from __future__ import annotations

from .contracts import (
    AtAlternativeResponse,
    # At
    AtRequest,
    AtResponse,
    BranchCompareRequest,
    BranchCompareResponse,
    # Branch
    BranchCreateRequest,
    BranchCreateResponse,
    BranchExploreRequest,
    BranchExploreResponse,
    BranchManifestResponse,
    # Manifest
    DifferanceManifestResponse,
    GhostItemResponse,
    # Ghosts
    GhostsRequest,
    GhostsResponse,
    HeritageEdgeResponse,
    HeritageNodeResponse,
    # Heritage
    HeritageRequest,
    HeritageResponse,
    # Replay
    ReplayRequest,
    ReplayResponse,
    ReplayStepResponse,
    WhyChosenStepResponse,
    # Why
    WhyRequest,
    WhyResponse,
)
from .heritage import (
    EdgeType,
    GhostHeritageDAG,
    HeritageEdge,
    HeritageNode,
    NodeType,
    build_heritage_dag,
    build_heritage_dag_from_traces,
)
from .integration import (
    DifferanceIntegration,
    TraceContext,
    clear_trace_buffer,
    get_differance_store,
    get_trace_buffer,
    get_trace_context,
    get_trace_monoid,
    record_trace,
    record_trace_sync,
    set_differance_store,
    set_trace_monoid,
)
from .operad import (
    TRACED_OPERAD,
    TracedAgent,
    TracedOperation,
    create_traced_operad,
    traced_par,
    traced_seq,
)
from .store import DifferanceStore
from .trace import (
    Alternative,
    TraceMonoid,
    WiringTrace,
)

__all__ = [
    # Core Types (Phase 1)
    "Alternative",
    "WiringTrace",
    "TraceMonoid",
    # Storage (Phase 1)
    "DifferanceStore",
    # Traced Operad (Phase 2)
    "TRACED_OPERAD",
    "TracedAgent",
    "TracedOperation",
    "create_traced_operad",
    "traced_seq",
    "traced_par",
    # Heritage DAG (Phase 3)
    "NodeType",
    "EdgeType",
    "HeritageNode",
    "HeritageEdge",
    "GhostHeritageDAG",
    "build_heritage_dag",
    "build_heritage_dag_from_traces",
    # Contracts (Phase 5)
    "DifferanceManifestResponse",
    "BranchManifestResponse",
    "HeritageRequest",
    "HeritageNodeResponse",
    "HeritageEdgeResponse",
    "HeritageResponse",
    "WhyRequest",
    "WhyChosenStepResponse",
    "WhyResponse",
    "GhostsRequest",
    "GhostItemResponse",
    "GhostsResponse",
    "AtRequest",
    "AtAlternativeResponse",
    "AtResponse",
    "ReplayRequest",
    "ReplayStepResponse",
    "ReplayResponse",
    "BranchCreateRequest",
    "BranchCreateResponse",
    "BranchExploreRequest",
    "BranchExploreResponse",
    "BranchCompareRequest",
    "BranchCompareResponse",
    # Integration (Phase 5)
    "DifferanceIntegration",
    "record_trace",
    "record_trace_sync",
    "get_trace_context",
    "TraceContext",
    "get_differance_store",
    "set_differance_store",
    "get_trace_monoid",
    "set_trace_monoid",
    "get_trace_buffer",
    "clear_trace_buffer",
]
