"""
Differance AGENTESE Contract Definitions.

Defines request and response types for time.differance and time.branch @node contracts.
These enable BE/FE contract synchronization via AGENTESE discovery.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest)
- Contract() for query aspects (heritage, why, ghosts, at, replay)

Types here are used by:
1. @node(contracts={...}) in time_differance.py
2. /discover?include_schemas=true endpoint
3. web/scripts/sync-types.ts for FE type generation

The Ghost Heritage Graph: seeing what almost was alongside what is.

See: spec/protocols/differance.md
See: plans/differance-cultivation.md (Phase 5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# =============================================================================
# Manifest Types
# =============================================================================


@dataclass(frozen=True)
class DifferanceManifestResponse:
    """Differance Engine status manifest."""

    trace_count: int
    store_connected: bool
    monoid_available: bool
    route: str = "/differance"


@dataclass(frozen=True)
class BranchManifestResponse:
    """Branch operations manifest."""

    branch_count: int
    branch_ids: list[str]


# =============================================================================
# Heritage Types (the crown jewel)
# =============================================================================


@dataclass(frozen=True)
class HeritageRequest:
    """Request for ghost heritage DAG."""

    output_id: str
    depth: int = 10


@dataclass(frozen=True)
class HeritageNodeResponse:
    """A node in the heritage graph."""

    id: str
    type: Literal["chosen", "ghost", "deferred", "spec", "impl"]
    operation: str
    timestamp: str
    depth: int
    output: Any | None = None
    reason: str | None = None
    explorable: bool = False
    inputs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class HeritageEdgeResponse:
    """An edge in the heritage graph."""

    source: str
    target: str
    type: Literal["produced", "ghosted", "deferred", "concretized"]


@dataclass(frozen=True)
class HeritageResponse:
    """Complete ghost heritage DAG response."""

    output_id: str
    root_id: str
    chosen_path: list[str]
    ghost_paths: list[list[str]]
    node_count: int
    edge_count: int
    max_depth: int
    nodes: dict[str, HeritageNodeResponse]
    edges: list[HeritageEdgeResponse]


# =============================================================================
# Why Types (explainability)
# =============================================================================


@dataclass(frozen=True)
class WhyRequest:
    """Request for 'why did this happen?' explanation."""

    output_id: str
    format: Literal["summary", "full", "cli"] = "summary"


@dataclass(frozen=True)
class WhyChosenStepResponse:
    """A single step in the chosen path (for full format)."""

    id: str
    operation: str
    inputs: list[str]
    output: Any | None
    ghosts: list[dict[str, Any]]


@dataclass(frozen=True)
class WhyResponse:
    """Explanation of why an output exists."""

    output_id: str
    lineage_length: int
    decisions_made: int
    alternatives_considered: int
    summary: str | None = None
    cli_output: str | None = None
    chosen_path: list[WhyChosenStepResponse] | None = None
    error: str | None = None


# =============================================================================
# Ghosts Types
# =============================================================================


@dataclass(frozen=True)
class GhostsRequest:
    """Request for unexplored alternatives (ghosts)."""

    explorable_only: bool = True
    limit: int = 50


@dataclass(frozen=True)
class GhostItemResponse:
    """A single ghost (road not taken)."""

    operation: str
    inputs: list[str]
    reason_rejected: str
    could_revisit: bool


@dataclass(frozen=True)
class GhostsResponse:
    """List of ghost alternatives."""

    ghosts: list[GhostItemResponse]
    count: int
    explorable_only: bool


# =============================================================================
# At (Navigate) Types
# =============================================================================


@dataclass(frozen=True)
class AtRequest:
    """Request to navigate to specific trace."""

    trace_id: str


@dataclass(frozen=True)
class AtAlternativeResponse:
    """Alternative considered at a trace point."""

    operation: str
    inputs: list[str]
    reason: str
    could_revisit: bool


@dataclass(frozen=True)
class AtResponse:
    """Full trace details response."""

    trace_id: str
    timestamp: str
    operation: str
    inputs: list[str]
    output: Any
    context: str
    alternatives: list[AtAlternativeResponse]
    parent_trace_id: str | None
    positions_before: dict[str, list[str]]
    positions_after: dict[str, list[str]]


# =============================================================================
# Replay Types
# =============================================================================


@dataclass(frozen=True)
class ReplayRequest:
    """Request to replay from trace point."""

    from_id: str
    include_ghosts: bool = True


@dataclass(frozen=True)
class ReplayStepResponse:
    """A single step in replay sequence."""

    trace_id: str
    operation: str
    inputs: list[str]
    output: Any
    context: str
    alternatives: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class ReplayResponse:
    """Replay sequence response."""

    from_id: str
    steps: list[ReplayStepResponse]
    step_count: int


# =============================================================================
# Branch Types
# =============================================================================


@dataclass(frozen=True)
class BranchCreateRequest:
    """Request to create speculative branch."""

    from_trace_id: str
    name: str | None = None
    hypothesis: str = ""


@dataclass(frozen=True)
class BranchCreateResponse:
    """Response after creating branch."""

    branch_id: str
    name: str
    from_trace_id: str
    status: str


@dataclass(frozen=True)
class BranchExploreRequest:
    """Request to explore a ghost alternative."""

    ghost_id: str
    branch_id: str | None = None


@dataclass(frozen=True)
class BranchExploreResponse:
    """Response from exploring ghost."""

    ghost_id: str
    branch_id: str | None
    status: str
    note: str


@dataclass(frozen=True)
class BranchCompareRequest:
    """Request to compare two branches."""

    a: str
    b: str


@dataclass(frozen=True)
class BranchCompareResponse:
    """Response comparing branches."""

    a: str
    b: str
    a_info: dict[str, Any] | None
    b_info: dict[str, Any] | None
    comparison: dict[str, Any]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Manifest
    "DifferanceManifestResponse",
    "BranchManifestResponse",
    # Heritage (the crown jewel)
    "HeritageRequest",
    "HeritageNodeResponse",
    "HeritageEdgeResponse",
    "HeritageResponse",
    # Why (explainability)
    "WhyRequest",
    "WhyChosenStepResponse",
    "WhyResponse",
    # Ghosts
    "GhostsRequest",
    "GhostItemResponse",
    "GhostsResponse",
    # At (navigate)
    "AtRequest",
    "AtAlternativeResponse",
    "AtResponse",
    # Replay
    "ReplayRequest",
    "ReplayStepResponse",
    "ReplayResponse",
    # Branch
    "BranchCreateRequest",
    "BranchCreateResponse",
    "BranchExploreRequest",
    "BranchExploreResponse",
    "BranchCompareRequest",
    "BranchCompareResponse",
]
