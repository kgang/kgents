"""
AGENTESE Time Trace WARP Context: TraceNode and Walk Primitives.

Provides AGENTESE paths for WARP Phase 1 primitives:
- time.trace.node.* - TraceNode operations
- time.walk.* - Walk (durable work stream) operations

The Insight (from spec/protocols/warp-primitives.md):
    "Every action is a TraceNode. Every session is a Walk. Every workflow is a Ritual."

AGENTESE Paths:
    time.trace.node.manifest - View TraceNode store status
    time.trace.node.capture - Emit a new TraceNode
    time.trace.node.query - Query traces by criteria
    time.trace.node.get - Get a specific trace by ID

    time.walk.manifest - View active Walks
    time.walk.create - Create a new Walk
    time.walk.advance - Add a TraceNode to a Walk
    time.walk.transition - Transition Walk phase
    time.walk.complete - Mark Walk complete

See: spec/protocols/warp-primitives.md
See: impl/claude/services/witness/trace_node.py
See: impl/claude/services/witness/walk.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# TraceNode AGENTESE Node
# =============================================================================


@node(
    "time.trace.node",
    description="WARP TraceNode operations - atomic execution artifacts",
)
@dataclass
class TraceNodeLogosNode(BaseLogosNode):
    """
    time.trace.node - WARP TraceNode operations.

    Provides AGENTESE access to the TraceNodeStore.

    Aspects:
        manifest - View store status
        capture - Emit a new TraceNode
        query - Query traces by criteria
        get - Get a specific trace by ID
        replay - Replay a sequence of traces
    """

    _handle: str = "time.trace.node"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """TraceNode affordances."""
        return ("manifest", "capture", "query", "get", "replay")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View TraceNode store status."""
        from services.witness import get_trace_store

        store = get_trace_store()
        stats = store.stats()

        return BasicRendering(
            summary="TraceNode Store (WARP)",
            content=f"Total traces: {stats['total_nodes']}, Links: {stats['total_links']}",
            metadata={
                "total_nodes": stats["total_nodes"],
                "total_links": stats["total_links"],
                "by_origin": stats["by_origin"],
                "by_phase": stats["by_phase"],
                "walks": stats["walks"],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle TraceNode aspects."""
        match aspect:
            case "capture":
                return await self._capture(observer, **kwargs)
            case "query":
                return await self._query(observer, **kwargs)
            case "get":
                return await self._get(observer, **kwargs)
            case "replay":
                return await self._replay(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _capture(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Capture (emit) a new TraceNode.

        Args:
            content: The thought/event content
            source: Event source (git, file, test, etc.)
            origin: Emitting jewel/agent (default: agentese)
            tags: Optional tags
            phase: Optional N-Phase
            walk_id: Optional Walk to attach to

        Returns:
            Created TraceNode info
        """
        from services.witness import (
            NPhase,
            TraceNode,
            WalkId,
            get_trace_store,
            get_walk_store,
        )

        content = kwargs.get("content", "")
        source = kwargs.get("source", "agentese")
        origin = kwargs.get("origin", "agentese")
        tags = tuple(kwargs.get("tags", []))
        phase_str = kwargs.get("phase")
        walk_id_str = kwargs.get("walk_id")

        # Parse phase
        phase = NPhase(phase_str) if phase_str else None

        # Create TraceNode
        node = TraceNode.from_thought(
            content=content,
            source=source,
            tags=tags,
            origin=origin,
            phase=phase,
        )

        # If walk_id provided, add walk binding
        if walk_id_str:
            walk_id = WalkId(walk_id_str)
            # Re-create with walk_id (frozen dataclass)
            node = TraceNode(
                id=node.id,
                origin=node.origin,
                stimulus=node.stimulus,
                response=node.response,
                umwelt=node.umwelt,
                links=node.links,
                timestamp=node.timestamp,
                phase=node.phase,
                walk_id=walk_id,
                tags=node.tags,
                metadata=node.metadata,
            )

            # Also add to Walk
            walk_store = get_walk_store()
            walk = walk_store.get(walk_id)
            if walk:
                walk.advance(node)

        # Append to store
        store = get_trace_store()
        store.append(node)

        return {
            "id": str(node.id),
            "origin": node.origin,
            "content": content,
            "tags": list(tags),
            "phase": phase.value if phase else None,
            "walk_id": walk_id_str,
            "timestamp": node.timestamp.isoformat(),
            "status": "captured",
        }

    async def _query(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Query traces by criteria.

        Args:
            origins: Filter by origins
            phases: Filter by N-Phases
            tags: Filter by tags (any match)
            walk_id: Filter by Walk
            after: Filter by time (after)
            before: Filter by time (before)
            limit: Max results
            offset: Skip first N results

        Returns:
            Matching traces
        """
        from services.witness import NPhase, TraceQuery, WalkId, get_trace_store

        store = get_trace_store()

        # Build query
        origins = tuple(kwargs.get("origins", [])) or None
        phases_str = kwargs.get("phases", [])
        phases = tuple(NPhase(p) for p in phases_str) if phases_str else None
        tags = tuple(kwargs.get("tags", [])) or None
        walk_id_str = kwargs.get("walk_id")
        walk_id = WalkId(walk_id_str) if walk_id_str else None

        after_str = kwargs.get("after")
        before_str = kwargs.get("before")
        after = datetime.fromisoformat(after_str) if after_str else None
        before = datetime.fromisoformat(before_str) if before_str else None

        limit = kwargs.get("limit", 50)
        offset = kwargs.get("offset", 0)

        query = TraceQuery(
            origins=origins,
            phases=phases,
            tags=tags,
            walk_id=walk_id,
            after=after,
            before=before,
            limit=limit,
            offset=offset,
        )

        results = list(store.query(query))

        return {
            "count": len(results),
            "limit": limit,
            "offset": offset,
            "traces": [
                {
                    "id": str(node.id),
                    "origin": node.origin,
                    "content": node.response.content,
                    "phase": node.phase.value if node.phase else None,
                    "walk_id": str(node.walk_id) if node.walk_id else None,
                    "timestamp": node.timestamp.isoformat(),
                    "tags": list(node.tags),
                }
                for node in results
            ],
        }

    async def _get(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get a specific TraceNode by ID.

        Args:
            id: TraceNode ID

        Returns:
            Full TraceNode data
        """
        from services.witness import TraceNodeId, get_trace_store

        trace_id = kwargs.get("id", "")
        if not trace_id:
            return {"error": "id is required"}

        store = get_trace_store()
        node = store.get(TraceNodeId(trace_id))

        if node is None:
            return {"error": f"Trace {trace_id} not found"}

        return node.to_dict()

    async def _replay(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Replay traces from a Walk or time range.

        Args:
            walk_id: Walk to replay
            start: Start index
            end: End index

        Returns:
            Ordered traces for replay
        """
        from services.witness import WalkId, get_trace_store

        store = get_trace_store()
        walk_id_str = kwargs.get("walk_id")
        start = kwargs.get("start", 0)
        end = kwargs.get("end")

        if walk_id_str:
            walk_id = WalkId(walk_id_str)
            traces = store.get_walk_traces(walk_id)
        else:
            traces = list(store.all())

        if end is not None:
            traces = traces[start:end]
        else:
            traces = traces[start:]

        return {
            "count": len(traces),
            "start": start,
            "end": end,
            "traces": [
                {
                    "id": str(node.id),
                    "origin": node.origin,
                    "stimulus": node.stimulus.to_dict(),
                    "response": node.response.to_dict(),
                    "timestamp": node.timestamp.isoformat(),
                }
                for node in traces
            ],
        }


# =============================================================================
# Walk AGENTESE Node
# =============================================================================


@node(
    "time.walk",
    description="WARP Walk operations - durable work streams tied to Forest plans",
)
@dataclass
class WalkLogosNode(BaseLogosNode):
    """
    time.walk - WARP Walk (durable work stream) operations.

    Provides AGENTESE access to Walk management.

    Aspects:
        manifest - View active Walks
        create - Create a new Walk
        get - Get a specific Walk
        advance - Add a TraceNode to a Walk
        transition - Transition Walk phase
        pause - Pause a Walk
        resume - Resume a Walk
        complete - Mark Walk complete
    """

    _handle: str = "time.walk"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Walk affordances."""
        return ("manifest", "list", "create", "get", "advance", "transition", "pause", "resume", "complete")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View active Walks."""
        from services.witness import get_walk_store

        store = get_walk_store()
        active = store.active_walks()
        recent = store.recent_walks(limit=5)

        return BasicRendering(
            summary="Walk Store (WARP)",
            content=f"Active walks: {len(active)}, Total: {len(store)}",
            metadata={
                "active_count": len(active),
                "total_count": len(store),
                "recent": [
                    {
                        "id": str(w.id),
                        "name": w.name,
                        "goal": w.goal.description if w.goal else None,
                        "phase": w.phase.value,
                        "status": w.status.name,
                        "trace_count": w.trace_count(),
                    }
                    for w in recent
                ],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Walk aspects."""
        match aspect:
            case "list":
                return await self._list(observer, **kwargs)
            case "create":
                return await self._create(observer, **kwargs)
            case "get":
                return await self._get(observer, **kwargs)
            case "advance":
                return await self._advance(observer, **kwargs)
            case "transition":
                return await self._transition(observer, **kwargs)
            case "pause":
                return await self._pause(observer, **kwargs)
            case "resume":
                return await self._resume(observer, **kwargs)
            case "complete":
                return await self._complete(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List Walks as SceneGraph for React rendering.

        Args:
            limit: Max walks to return (default: 20)
            active_only: Only return active walks (default: False)

        Returns:
            SceneGraph JSON for ServoSceneRenderer
        """
        from protocols.agentese.projection.warp_converters import walk_dashboard_to_scene
        from services.witness import get_walk_store

        limit = kwargs.get("limit", 20)
        active_only = kwargs.get("active_only", False)

        store = get_walk_store()

        if active_only:
            walks = store.active_walks()[:limit]
        else:
            walks = store.recent_walks(limit=limit)

        # Convert to SceneGraph and serialize
        scene = walk_dashboard_to_scene(walks, title="Witness Dashboard")
        return scene.to_dict()

    async def _create(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Create a new Walk.

        Args:
            goal: Goal description
            root_plan: Optional plan path (e.g., "plans/warp-phase1.md")
            name: Optional walk name
            phase: Initial N-Phase (default: SENSE)

        Returns:
            Created Walk info
        """
        from services.witness import NPhase, PlanPath, Walk, get_walk_store

        goal = kwargs.get("goal", "")
        if not goal:
            return {"error": "goal is required"}

        root_plan_str = kwargs.get("root_plan")
        root_plan = PlanPath(root_plan_str) if root_plan_str else None
        name = kwargs.get("name", "")
        phase_str = kwargs.get("phase", "SENSE")
        initial_phase = NPhase(phase_str)

        walk = Walk.create(
            goal=goal,
            root_plan=root_plan,
            name=name,
            initial_phase=initial_phase,
        )

        # Add to store
        store = get_walk_store()
        store.add(walk)

        return {
            "id": str(walk.id),
            "name": walk.name,
            "goal": walk.goal.description if walk.goal else None,
            "root_plan": str(walk.root_plan) if walk.root_plan else None,
            "phase": walk.phase.value,
            "status": walk.status.name,
            "started_at": walk.started_at.isoformat(),
        }

    async def _get(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get a specific Walk by ID.

        Args:
            id: Walk ID

        Returns:
            Full Walk data
        """
        from services.witness import WalkId, get_walk_store

        walk_id = kwargs.get("id", "")
        if not walk_id:
            return {"error": "id is required"}

        store = get_walk_store()
        walk = store.get(WalkId(walk_id))

        if walk is None:
            return {"error": f"Walk {walk_id} not found"}

        return walk.to_dict()

    async def _advance(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Add a TraceNode to a Walk.

        Args:
            walk_id: Walk ID
            trace_id: TraceNode ID to add

        Returns:
            Updated Walk info
        """
        from services.witness import TraceNodeId, WalkId, get_trace_store, get_walk_store

        walk_id_str = kwargs.get("walk_id", "")
        trace_id_str = kwargs.get("trace_id", "")

        if not walk_id_str or not trace_id_str:
            return {"error": "walk_id and trace_id are required"}

        walk_store = get_walk_store()
        trace_store = get_trace_store()

        walk = walk_store.get(WalkId(walk_id_str))
        if walk is None:
            return {"error": f"Walk {walk_id_str} not found"}

        trace = trace_store.get(TraceNodeId(trace_id_str))
        if trace is None:
            return {"error": f"Trace {trace_id_str} not found"}

        walk.advance(trace)

        return {
            "walk_id": walk_id_str,
            "trace_id": trace_id_str,
            "trace_count": walk.trace_count(),
            "status": "advanced",
        }

    async def _transition(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Transition Walk to a new N-Phase.

        Args:
            walk_id: Walk ID
            phase: Target phase

        Returns:
            Transition result
        """
        from services.witness import NPhase, WalkId, get_walk_store

        walk_id_str = kwargs.get("walk_id", "")
        phase_str = kwargs.get("phase", "")

        if not walk_id_str or not phase_str:
            return {"error": "walk_id and phase are required"}

        store = get_walk_store()
        walk = store.get(WalkId(walk_id_str))

        if walk is None:
            return {"error": f"Walk {walk_id_str} not found"}

        try:
            target_phase = NPhase(phase_str)
        except ValueError:
            return {"error": f"Invalid phase: {phase_str}"}

        success = walk.transition_phase(target_phase)

        return {
            "walk_id": walk_id_str,
            "from_phase": walk.phase_history[-2][0].value if len(walk.phase_history) > 1 else None,
            "to_phase": walk.phase.value,
            "success": success,
        }

    async def _pause(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Pause a Walk."""
        from services.witness import WalkId, get_walk_store

        walk_id_str = kwargs.get("walk_id", "")
        if not walk_id_str:
            return {"error": "walk_id is required"}

        store = get_walk_store()
        walk = store.get(WalkId(walk_id_str))

        if walk is None:
            return {"error": f"Walk {walk_id_str} not found"}

        walk.pause()
        return {"walk_id": walk_id_str, "status": walk.status.name}

    async def _resume(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Resume a paused Walk."""
        from services.witness import WalkId, get_walk_store

        walk_id_str = kwargs.get("walk_id", "")
        if not walk_id_str:
            return {"error": "walk_id is required"}

        store = get_walk_store()
        walk = store.get(WalkId(walk_id_str))

        if walk is None:
            return {"error": f"Walk {walk_id_str} not found"}

        walk.resume()
        return {"walk_id": walk_id_str, "status": walk.status.name}

    async def _complete(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Mark a Walk as complete."""
        from services.witness import WalkId, get_walk_store

        walk_id_str = kwargs.get("walk_id", "")
        if not walk_id_str:
            return {"error": "walk_id is required"}

        store = get_walk_store()
        walk = store.get(WalkId(walk_id_str))

        if walk is None:
            return {"error": f"Walk {walk_id_str} not found"}

        walk.complete()
        return {
            "walk_id": walk_id_str,
            "status": walk.status.name,
            "trace_count": walk.trace_count(),
            "duration_seconds": walk.duration_seconds,
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_trace_node_logos() -> TraceNodeLogosNode:
    """Create a TraceNodeLogosNode instance."""
    return TraceNodeLogosNode()


def create_walk_logos() -> WalkLogosNode:
    """Create a WalkLogosNode instance."""
    return WalkLogosNode()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "TraceNodeLogosNode",
    "WalkLogosNode",
    "create_trace_node_logos",
    "create_walk_logos",
]
