"""
AGENTESE Differance Time Context.

time.differance.* paths for the Differance Engine heritage DAG.

The Ghost Heritage Graph: seeing what almost was alongside what is.

AGENTESE Paths:
- time.differance.manifest  - View current trace state
- time.differance.heritage  - Build GhostHeritageDAG for an output
- time.differance.ghosts    - List all unexplored alternatives
- time.differance.at        - Navigate to specific trace
- time.differance.why       - "Why did this happen?" (key path!)
- time.differance.replay    - Re-execute from trace point

Branch Operations:
- time.branch.manifest  - View active branches
- time.branch.create    - Create speculative branch
- time.branch.explore   - Execute a ghost alternative
- time.branch.compare   - Side-by-side comparison

See: spec/protocols/differance.md
See: plans/differance-cultivation.md (Phase 5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from agents.differance import (
        DifferanceStore,
        GhostHeritageDAG,
        TraceMonoid,
        WiringTrace,
    )
    from bootstrap.umwelt import Umwelt

# Import contract types
from agents.differance.contracts import (
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
    # Ghosts
    GhostsRequest,
    GhostsResponse,
    # Heritage
    HeritageRequest,
    HeritageResponse,
    # Recent
    RecentTracesRequest,
    RecentTracesResponse,
    # Replay
    ReplayRequest,
    ReplayResponse,
    # Why
    WhyRequest,
    WhyResponse,
)

# === Affordances ===

DIFFERANCE_TRACE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "heritage",
    "ghosts",
    "at",
    "replay",
    "why",
    "recent",  # Recent traces for RecentTracesPanel
)

DIFFERANCE_BRANCH_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "create",
    "explore",
    "compare",
)


# === DifferanceMark ===


@node(
    "time.differance",
    description="Ghost Heritage DAG tracing",
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(DifferanceManifestResponse),
        # Query aspects (Contract - request + response)
        "heritage": Contract(HeritageRequest, HeritageResponse),
        "why": Contract(WhyRequest, WhyResponse),
        "ghosts": Contract(GhostsRequest, GhostsResponse),
        "at": Contract(AtRequest, AtResponse),
        "replay": Contract(ReplayRequest, ReplayResponse),
        "recent": Contract(RecentTracesRequest, RecentTracesResponse),
    },
)
@dataclass
class DifferanceMark(BaseLogosNode):
    """
    time.differance - Ghost Heritage DAG operations.

    The Différance Engine's trace visualization and navigation.

    AGENTESE paths:
    - time.differance.manifest   # View current trace state
    - time.differance.heritage   # Build heritage DAG for output
    - time.differance.ghosts     # All unexplored alternatives
    - time.differance.at         # Navigate to specific trace
    - time.differance.why        # "Why did this happen?" (key path!)
    - time.differance.replay     # Re-execute from trace point
    """

    _handle: str = "time.differance"

    # Différance store for trace persistence
    _store: DifferanceStore | None = None

    # In-memory monoid for operations without persistence
    _monoid: TraceMonoid | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Differance trace affordances."""
        return DIFFERANCE_TRACE_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View trace state summary",
    )
    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current trace state."""
        mark_count = await self._get_mark_count()
        has_store = self._store is not None
        has_monoid = self._monoid is not None

        return BasicRendering(
            summary="Différance Engine",
            content=f"Wiring traces: {mark_count}",
            metadata={
                "mark_count": mark_count,
                "store_connected": has_store,
                "monoid_available": has_monoid,
                "route": "/differance",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle differance trace aspects."""
        match aspect:
            case "heritage":
                return await self._heritage(observer, **kwargs)
            case "ghosts":
                return await self._ghosts(observer, **kwargs)
            case "at":
                return await self._at(observer, **kwargs)
            case "why":
                return await self._why(observer, **kwargs)
            case "replay":
                return await self._replay(observer, **kwargs)
            case "recent":
                return await self._recent(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _heritage(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build GhostHeritageDAG for an output.

        AGENTESE: time.differance.heritage

        Args:
            output_id: ID of the trace/output to get heritage for
            depth: Maximum depth to traverse (default: 10)

        Returns:
            Heritage DAG as dict with chosen_path, ghost_paths, nodes
        """
        output_id = kwargs.get("output_id")
        if not output_id:
            return {"error": "output_id is required", "aspect": "heritage"}

        depth = kwargs.get("depth", 10)

        try:
            dag = await self._build_dag(output_id, depth)
            if dag is None or not dag.root_id:
                return {
                    "output_id": output_id,
                    "error": "No heritage found for this output",
                    "aspect": "heritage",
                }

            return {
                "output_id": output_id,
                "root_id": dag.root_id,
                "chosen_path": list(dag.chosen_path()),
                "ghost_paths": [list(p) for p in dag.ghost_paths()],
                "node_count": dag.node_count,
                "edge_count": dag.edge_count,
                "max_depth": dag.max_depth,
                "nodes": {
                    nid: {
                        "id": n.id,
                        "type": n.node_type,
                        "operation": n.operation,
                        "timestamp": n.timestamp.isoformat(),
                        "depth": n.depth,
                        "output": n.output,
                        "reason": n.reason,
                        "explorable": n.explorable,
                        "inputs": list(n.inputs),
                    }
                    for nid, n in dag.nodes.items()
                },
                "edges": [
                    {
                        "source": e.source,
                        "target": e.target,
                        "type": e.edge_type,
                    }
                    for e in dag.edges
                ],
            }
        except Exception as e:
            return {"error": str(e), "aspect": "heritage"}

    async def _ghosts(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List all unexplored alternatives (ghosts).

        AGENTESE: time.differance.ghosts

        Args:
            explorable_only: Only return ghosts that can be revisited (default: True)
            limit: Maximum ghosts to return (default: 50)

        Returns:
            List of ghost alternatives with context
        """
        explorable_only = kwargs.get("explorable_only", True)
        limit = kwargs.get("limit", 50)

        ghosts: list[dict[str, Any]] = []

        try:
            monoid = await self._get_monoid()
            if monoid is None:
                return {
                    "ghosts": [],
                    "count": 0,
                    "note": "No traces available",
                }

            all_ghosts = monoid.ghosts()
            for alt in all_ghosts[:limit]:
                if explorable_only and not alt.could_revisit:
                    continue

                ghosts.append(
                    {
                        "operation": alt.operation,
                        "inputs": list(alt.inputs),
                        "reason_rejected": alt.reason_rejected,
                        "could_revisit": alt.could_revisit,
                    }
                )

            return {
                "ghosts": ghosts,
                "count": len(ghosts),
                "explorable_only": explorable_only,
            }
        except Exception as e:
            return {"error": str(e), "aspect": "ghosts"}

    async def _at(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Navigate to specific trace.

        AGENTESE: time.differance.at

        Args:
            trace_id: ID of the trace to navigate to

        Returns:
            Full trace details
        """
        trace_id = kwargs.get("trace_id")
        if not trace_id:
            return {"error": "trace_id is required", "aspect": "at"}

        try:
            trace = await self._get_trace(trace_id)
            if trace is None:
                return {
                    "trace_id": trace_id,
                    "error": f"Trace {trace_id} not found",
                    "aspect": "at",
                }

            return {
                "trace_id": trace.trace_id,
                "timestamp": trace.timestamp.isoformat(),
                "operation": trace.operation,
                "inputs": list(trace.inputs),
                "output": trace.output,
                "context": trace.context,
                "alternatives": [
                    {
                        "operation": alt.operation,
                        "inputs": list(alt.inputs),
                        "reason": alt.reason_rejected,
                        "could_revisit": alt.could_revisit,
                    }
                    for alt in trace.alternatives
                ],
                "parent_trace_id": trace.parent_trace_id,
                "positions_before": {k: list(v) for k, v in trace.positions_before.items()},
                "positions_after": {k: list(v) for k, v in trace.positions_after.items()},
            }
        except Exception as e:
            return {"error": str(e), "aspect": "at"}

    async def _why(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        "Why did this happen?" - The key explainability path.

        AGENTESE: time.differance.why

        This is the crown jewel of the Différance Engine: given an output ID,
        explain why it exists by showing the lineage of decisions and what
        alternatives were considered.

        Args:
            output_id: ID of the output to explain
            format: Output format - "summary", "full", "cli" (default: "summary")

        Returns:
            Explanation of why this output exists, including alternatives
        """
        output_id = kwargs.get("output_id")
        if not output_id:
            return {"error": "output_id is required", "aspect": "why"}

        fmt = kwargs.get("format", "summary")

        try:
            dag = await self._build_dag(output_id, depth=10)
            if dag is None or not dag.root_id:
                return {
                    "output_id": output_id,
                    "error": "No heritage found",
                    "aspect": "why",
                }

            chosen = dag.chosen_path()
            ghosts = dag.ghost_paths()

            # Build explanation
            explanation: dict[str, Any] = {
                "output_id": output_id,
                "lineage_length": len(chosen),
                "decisions_made": len(chosen),
                "alternatives_considered": len(ghosts),
            }

            if fmt == "cli":
                # ASCII format for CLI
                lines = [f"▶ {output_id}"]
                for trace_id in chosen:
                    node = dag.get_node(trace_id)
                    if node:
                        lines.append(f"│ {node.operation}({', '.join(node.inputs)})")
                        # Show ghosts at this level
                        for ghost in dag.ghosts_of(trace_id):
                            symbol = "░" if ghost.explorable else "×"
                            lines.append(f"├── {symbol} {ghost.operation} [GHOST: {ghost.reason}]")

                explanation["cli_output"] = "\n".join(lines)

            elif fmt == "full":
                # Full details
                explanation["chosen_path"] = []
                for trace_id in chosen:
                    node = dag.get_node(trace_id)
                    if node:
                        explanation["chosen_path"].append(
                            {
                                "id": trace_id,
                                "operation": node.operation,
                                "inputs": list(node.inputs),
                                "output": node.output,
                                "ghosts": [
                                    {
                                        "operation": g.operation,
                                        "reason": g.reason,
                                        "explorable": g.explorable,
                                    }
                                    for g in dag.ghosts_of(trace_id)
                                ],
                            }
                        )

            else:  # summary
                # Brief summary
                if chosen:
                    first_node = dag.get_node(chosen[0])
                    last_node = dag.get_node(chosen[-1]) if len(chosen) > 1 else first_node
                    explanation["summary"] = (
                        f"Output {output_id} resulted from {len(chosen)} decisions, "
                        f"starting with {first_node.operation if first_node else 'unknown'} "
                        f"and ending with {last_node.operation if last_node else 'unknown'}. "
                        f"{len(ghosts)} alternatives were considered but not taken."
                    )

            return explanation

        except Exception as e:
            return {"error": str(e), "aspect": "why"}

    async def _replay(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Re-execute from trace point.

        AGENTESE: time.differance.replay

        Args:
            from_id: Trace ID to replay from
            include_ghosts: Whether to show ghost options (default: True)

        Returns:
            Replay sequence
        """
        from_id = kwargs.get("from_id")
        if not from_id:
            return {"error": "from_id is required", "aspect": "replay"}

        include_ghosts = kwargs.get("include_ghosts", True)

        try:
            # Get causal chain from this trace
            chain = await self._get_causal_chain(from_id)
            if not chain:
                return {
                    "from_id": from_id,
                    "error": "Trace not found",
                    "aspect": "replay",
                }

            replay_steps: list[dict[str, Any]] = []
            for trace in chain:
                step: dict[str, Any] = {
                    "trace_id": trace.trace_id,
                    "operation": trace.operation,
                    "inputs": list(trace.inputs),
                    "output": trace.output,
                    "context": trace.context,
                }

                if include_ghosts:
                    step["alternatives"] = [
                        {
                            "operation": alt.operation,
                            "reason": alt.reason_rejected,
                            "explorable": alt.could_revisit,
                        }
                        for alt in trace.alternatives
                    ]

                replay_steps.append(step)

            return {
                "from_id": from_id,
                "steps": replay_steps,
                "step_count": len(replay_steps),
            }
        except Exception as e:
            return {"error": str(e), "aspect": "replay"}

    async def _recent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get recent traces from store/buffer.

        AGENTESE: time.differance.recent

        This powers the RecentTracesPanel in the Cockpit, showing
        the most recent wiring operations with jewel attribution.

        Prefers store (Postgres) when available; falls back to in-memory buffer.

        Args:
            limit: Max traces to return (default: 10)
            jewel_filter: Optional filter by crown jewel name (brain, gardener, etc.)

        Returns:
            Recent traces with previews for UI display
        """
        from agents.differance.integration import get_trace_buffer

        limit = kwargs.get("limit", 10)
        jewel_filter = kwargs.get("jewel_filter")

        traces: list[dict[str, Any]] = []
        total_traces = 0
        source = "buffer"

        # Prefer store over buffer when available
        if self._store is not None:
            try:
                # Query store for recent traces
                raw_traces: list["WiringTrace"] = []
                async for trace in self._store.query(limit=limit * 2):  # Fetch extra for filtering
                    raw_traces.append(trace)

                # Sort by timestamp descending
                raw_traces.sort(key=lambda t: t.timestamp, reverse=True)

                store_count = await self._store.count()
                total_traces = store_count
                source = "postgres"

                for trace in raw_traces:
                    # Extract jewel from context
                    jewel: str | None = None
                    if trace.context.startswith("["):
                        bracket_end = trace.context.find("]")
                        if bracket_end > 1:
                            jewel = trace.context[1:bracket_end]

                    # Apply jewel filter
                    if jewel_filter and jewel != jewel_filter:
                        continue

                    traces.append(
                        {
                            "id": trace.trace_id,
                            "operation": trace.operation,
                            "context": trace.context,
                            "timestamp": trace.timestamp.isoformat(),
                            "ghost_count": len(trace.alternatives),
                            "output_preview": (str(trace.output)[:50] if trace.output else None),
                            "jewel": jewel,
                        }
                    )

                    if len(traces) >= limit:
                        break
            except Exception:
                # Fall back to buffer on store error
                pass

        # Fall back to buffer if no store or store empty
        if not traces:
            buffer = get_trace_buffer()
            total_traces = len(buffer)
            source = "buffer"

            for trace in reversed(buffer):
                # Extract jewel from context
                jewel = None
                if trace.context.startswith("["):
                    bracket_end = trace.context.find("]")
                    if bracket_end > 1:
                        jewel = trace.context[1:bracket_end]

                # Apply jewel filter
                if jewel_filter and jewel != jewel_filter:
                    continue

                traces.append(
                    {
                        "id": trace.trace_id,
                        "operation": trace.operation,
                        "context": trace.context,
                        "timestamp": trace.timestamp.isoformat(),
                        "ghost_count": len(trace.alternatives),
                        "output_preview": (str(trace.output)[:50] if trace.output else None),
                        "jewel": jewel,
                    }
                )

                if len(traces) >= limit:
                    break

        return {
            "traces": traces,
            "total": total_traces,
            "source": source,
            "store_connected": self._store is not None,
        }

    # === Helper Methods ===

    async def _get_mark_count(self) -> int:
        """Get count of traces."""
        if self._store:
            return await self._store.count()
        if self._monoid:
            return len(self._monoid)
        return 0

    async def _get_monoid(self) -> TraceMonoid | None:
        """Get or build TraceMonoid."""
        if self._monoid:
            return self._monoid
        if self._store:
            return await self._store.to_monoid()
        return None

    async def _get_trace(self, trace_id: str) -> WiringTrace | None:
        """Get a single trace by ID."""
        if self._store:
            return await self._store.get(trace_id)
        if self._monoid:
            for trace in self._monoid.traces:
                if trace.trace_id == trace_id:
                    return trace
        return None

    async def _get_causal_chain(self, trace_id: str) -> list[WiringTrace]:
        """Get causal chain for a trace."""
        if self._store:
            return await self._store.causal_chain(trace_id)
        if self._monoid:
            return list(self._monoid.causal_chain(trace_id))
        return []

    async def _build_dag(
        self,
        output_id: str,
        depth: int = 10,
    ) -> GhostHeritageDAG | None:
        """Build heritage DAG for an output."""
        from agents.differance import build_heritage_dag

        if self._store:
            return await self._store.heritage_dag(output_id, depth)
        if self._monoid:
            return build_heritage_dag(self._monoid, output_id, depth)
        return None

    def set_store(self, store: DifferanceStore) -> None:
        """Set the DifferanceStore for persistence."""
        self._store = store

    def set_monoid(self, monoid: TraceMonoid) -> None:
        """Set an in-memory TraceMonoid."""
        self._monoid = monoid


# === BranchNode ===


@node(
    "time.branch",
    description="Speculative branch operations",
    contracts={
        # Perception aspects
        "manifest": Response(BranchManifestResponse),
        # Mutation aspects
        "create": Contract(BranchCreateRequest, BranchCreateResponse),
        "explore": Contract(BranchExploreRequest, BranchExploreResponse),
        "compare": Contract(BranchCompareRequest, BranchCompareResponse),
    },
)
@dataclass
class BranchNode(BaseLogosNode):
    """
    time.branch - Speculative branch operations.

    Create, explore, and compare alternative wiring paths.

    AGENTESE paths:
    - time.branch.manifest  # View current branches
    - time.branch.create    # Create speculative branch
    - time.branch.explore   # Execute a ghost alternative
    - time.branch.compare   # Side-by-side comparison
    """

    _handle: str = "time.branch"

    # Active speculative branches
    _branches: dict[str, dict[str, Any]] = field(default_factory=dict)
    _next_id: int = 0

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Branch affordances."""
        return DIFFERANCE_BRANCH_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View active branches",
    )
    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current branches."""
        return BasicRendering(
            summary="Speculative Branches",
            content=f"Active branches: {len(self._branches)}",
            metadata={
                "branch_count": len(self._branches),
                "branch_ids": list(self._branches.keys()),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle branch aspects."""
        match aspect:
            case "create":
                return await self._create(observer, **kwargs)
            case "explore":
                return await self._explore(observer, **kwargs)
            case "compare":
                return await self._compare(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _create(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create speculative branch.

        AGENTESE: time.branch.create

        Args:
            from_trace_id: Trace to branch from
            name: Optional branch name
            hypothesis: What we're exploring

        Returns:
            Branch ID and metadata
        """
        from_trace_id = kwargs.get("from_trace_id")
        if not from_trace_id:
            return {"error": "from_trace_id is required", "aspect": "create"}

        name = kwargs.get("name", f"branch_{self._next_id}")
        hypothesis = kwargs.get("hypothesis", "")

        branch_id = f"branch_{self._next_id}"
        self._next_id += 1

        self._branches[branch_id] = {
            "id": branch_id,
            "name": name,
            "from_trace_id": from_trace_id,
            "hypothesis": hypothesis,
            "created_at": datetime.now().isoformat(),
            "traces": [],
            "status": "active",
        }

        return {
            "branch_id": branch_id,
            "name": name,
            "from_trace_id": from_trace_id,
            "status": "created",
        }

    async def _explore(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a ghost alternative.

        AGENTESE: time.branch.explore

        Args:
            ghost_id: Ghost node ID to explore
            branch_id: Branch to add exploration to

        Returns:
            Exploration result
        """
        ghost_id = kwargs.get("ghost_id")
        if not ghost_id:
            return {"error": "ghost_id is required", "aspect": "explore"}

        branch_id = kwargs.get("branch_id")

        # For now, exploration is deferred (needs full agent execution context)
        return {
            "ghost_id": ghost_id,
            "branch_id": branch_id,
            "status": "deferred",
            "note": "Ghost exploration requires full agent execution context. "
            "The ghost has been marked for future exploration.",
        }

    async def _compare(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Side-by-side comparison of branches.

        AGENTESE: time.branch.compare

        Args:
            a: First trace/branch ID
            b: Second trace/branch ID

        Returns:
            Comparison showing differences
        """
        a = kwargs.get("a")
        b = kwargs.get("b")

        if not a or not b:
            return {"error": "Both 'a' and 'b' are required", "aspect": "compare"}

        # Get branch info
        branch_a = self._branches.get(a)
        branch_b = self._branches.get(b)

        return {
            "a": a,
            "b": b,
            "a_info": branch_a,
            "b_info": branch_b,
            "comparison": {
                "both_exist": branch_a is not None and branch_b is not None,
                "note": "Full comparison requires implementation of branch execution",
            },
        }

    def get_branch(self, branch_id: str) -> dict[str, Any] | None:
        """Get branch by ID."""
        return self._branches.get(branch_id)


# === Factory Functions ===

_differance_node: DifferanceMark | None = None
_branch_node: BranchNode | None = None


def get_differance_node() -> DifferanceMark:
    """Get the singleton DifferanceMark."""
    global _differance_node
    if _differance_node is None:
        _differance_node = DifferanceMark()
    return _differance_node


def set_differance_node(node: DifferanceMark | None) -> None:
    """Set or clear the singleton DifferanceMark."""
    global _differance_node
    _differance_node = node


def get_branch_node() -> BranchNode:
    """Get the singleton BranchNode."""
    global _branch_node
    if _branch_node is None:
        _branch_node = BranchNode()
    return _branch_node


def create_differance_node(
    store: DifferanceStore | None = None,
    monoid: TraceMonoid | None = None,
) -> DifferanceMark:
    """
    Create a DifferanceMark with optional store.

    Args:
        store: DifferanceStore for persistence
        monoid: In-memory TraceMonoid

    Returns:
        Configured DifferanceMark
    """
    node = DifferanceMark()
    if store:
        node.set_store(store)
    if monoid:
        node.set_monoid(monoid)
    return node


__all__ = [
    # Affordances
    "DIFFERANCE_TRACE_AFFORDANCES",
    "DIFFERANCE_BRANCH_AFFORDANCES",
    # Nodes
    "DifferanceMark",
    "BranchNode",
    # Factories
    "get_differance_node",
    "set_differance_node",
    "get_branch_node",
    "create_differance_node",
]
