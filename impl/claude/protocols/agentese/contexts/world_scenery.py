"""
AGENTESE World Scenery Context: SceneGraph Projection Endpoint.

SceneGraph-related nodes for world.scenery.* paths:
- SceneryNode: Exposes SceneGraph to React/Servo projection layers

This node bridges the SceneGraph ontology to external projection surfaces.
The SceneGraph IS the API - React components consume this directly.

AGENTESE Paths:
    world.scenery.manifest  - Get current scene graph state
    world.scenery.stream    - SSE stream of scene graph updates
    world.scenery.project   - Project traces through a TerrariumView

Laws (from projection/scene.py):
    Law 1 (Identity): SceneGraph.empty() >> G == G == G >> SceneGraph.empty()
    Law 2 (Associativity): (A >> B) >> C == A >> (B >> C)
    Law 3 (Immutability): SceneGraph and SceneNode are frozen

See: protocols/agentese/projection/scene.py
See: protocols/agentese/projection/terrarium_view.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..projection import (
    LayoutDirective,
    LensConfig,
    LensMode,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
    SelectionQuery,
    TerrariumView,
    TerrariumViewStore,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# Global Stores
# =============================================================================

# Module-level view store for persistence across invocations
_view_store: TerrariumViewStore | None = None


def _get_view_store() -> TerrariumViewStore:
    """Get or create the global TerrariumViewStore."""
    global _view_store
    if _view_store is None:
        _view_store = TerrariumViewStore()
    return _view_store


# =============================================================================
# SceneryNode: AGENTESE Interface to SceneGraph
# =============================================================================

# Scenery affordances
SCENERY_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "stream",
    "project",
    "create_view",
    "list_views",
)


@node(
    "world.scenery",
    description="SceneGraph projection endpoint for React/Servo",
)
@dataclass
class SceneryNode(BaseLogosNode):
    """
    world.scenery - SceneGraph projection endpoint.

    The SceneGraph is the ontology. This node exposes it to projection surfaces
    (React now, Servo future). Components consume the SceneGraph and render
    according to their target capabilities.

    Philosophy (from spec/protocols/servo-substrate.md):
        "Servo is not 'a browser' inside kgents. It is the projection substrate
        that renders the ontology."

    AGENTESE: world.scenery.*
    """

    _handle: str = "world.scenery"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Scenery affordances available to all archetypes."""
        return SCENERY_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Get current SceneGraph state.

        Returns a demonstration SceneGraph that shows the structure.
        In production, this would aggregate from various sources.
        """
        scene = self._build_demo_scene()
        view_store = _get_view_store()

        manifest_data = {
            "path": self.handle,
            "description": "SceneGraph projection endpoint",
            "scene": scene.to_dict(),
            "views": {
                "total": view_store.count(),
                "active": len(view_store.active()),
            },
            "node_kinds": [k.name for k in SceneNodeKind],
            "lens_modes": [m.name for m in LensMode],
            "laws": [
                "Law 1: SceneGraph.empty() >> G == G == G >> SceneGraph.empty()",
                "Law 2: (A >> B) >> C == A >> (B >> C)",
                "Law 3: SceneGraph and SceneNode are immutable",
            ],
        }

        return BasicRendering(
            summary=f"SceneGraph ({scene.node_count()} nodes)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Scenery-specific aspects."""
        match aspect:
            case "stream":
                return self._stream_scene(**kwargs)
            case "project":
                return self._project_traces(**kwargs)
            case "create_view":
                return self._create_view(**kwargs)
            case "list_views":
                return self._list_views()
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Streaming Aspect
    # ==========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        streaming=True,
        idempotent=True,
        help="Stream SceneGraph updates via SSE",
    )
    async def _stream_scene(
        self,
        poll_interval: float = 1.0,
        max_events: int = 0,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream SceneGraph updates.

        Args:
            poll_interval: Seconds between updates (default: 1.0)
            max_events: Maximum events to emit (0 = unlimited)

        Yields:
            SceneGraph dicts for SSE consumption
        """
        event_count = 0

        while True:
            # Build current scene
            scene = self._build_demo_scene()

            yield {
                "type": "scene",
                "graph": scene.to_dict(),
                "timestamp": datetime.now().isoformat(),
                "event_count": event_count,
            }

            event_count += 1

            # Check limit
            if max_events > 0 and event_count >= max_events:
                break

            await asyncio.sleep(poll_interval)

    # ==========================================================================
    # TerrariumView Management
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Create a new TerrariumView",
    )
    def _create_view(
        self,
        name: str = "Unnamed View",
        lens_mode: str = "timeline",
        origin_filter: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Create a new TerrariumView.

        Args:
            name: View name
            lens_mode: Lens mode (timeline, graph, summary, detail)
            origin_filter: Filter by origin (optional)
            limit: Maximum traces to show

        Returns:
            Created view metadata
        """
        store = _get_view_store()

        # Build selection query
        if origin_filter:
            selection = SelectionQuery.by_origin(origin_filter).with_limit(limit)
        else:
            selection = SelectionQuery.recent(limit)

        # Build lens config
        mode_map = {
            "timeline": LensMode.TIMELINE,
            "graph": LensMode.GRAPH,
            "summary": LensMode.SUMMARY,
            "detail": LensMode.DETAIL,
        }
        lens = LensConfig(mode=mode_map.get(lens_mode, LensMode.TIMELINE))

        # Create view
        view = TerrariumView(
            name=name,
            selection=selection,
            lens=lens,
        )

        # Add to store
        store.add(view)

        return {
            "created": True,
            "view": view.to_dict(),
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="List all TerrariumViews",
    )
    def _list_views(self) -> dict[str, Any]:
        """List all registered TerrariumViews."""
        store = _get_view_store()
        views = store.all()

        return {
            "count": len(views),
            "views": [v.to_dict() for v in views],
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        idempotent=True,
        help="Project traces through a TerrariumView lens",
    )
    def _project_traces(
        self,
        view_id: str | None = None,
        traces: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Project traces through a TerrariumView.

        Args:
            view_id: View to use (or default if None)
            traces: Traces to project (or demo traces if None)

        Returns:
            Projected SceneGraph
        """
        store = _get_view_store()

        # Get or create view
        view: TerrariumView
        if view_id:
            from ..projection.terrarium_view import TerrariumViewId

            found = store.get(TerrariumViewId(view_id))
            if found is None:
                return {"error": "view_not_found", "view_id": view_id}
            view = found
        else:
            # Use default timeline view
            view = TerrariumView.timeline("Default", limit=50)

        # Use demo traces if none provided
        if traces is None:
            traces = self._get_demo_traces()

        # Project through view
        scene = view.project(traces)

        return {
            "view_id": str(view.id),
            "view_name": view.name,
            "lens_mode": view.lens.mode.name,
            "scene": scene.to_dict(),
        }

    # ==========================================================================
    # Demo Scene Builder
    # ==========================================================================

    def _build_demo_scene(self) -> SceneGraph:
        """
        Build a demonstration SceneGraph.

        Shows the structure for React consumption.
        """
        # Header panel
        header = SceneNode.panel(
            "Scene Dashboard",
        )

        # Text nodes
        welcome = SceneNode.text(
            "Welcome to the SceneGraph projection layer",
            label="Welcome",
        )

        status = SceneNode.text(
            f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            label="Status",
        )

        # Compose scene
        scene = SceneGraph(
            nodes=(header, welcome, status),
            layout=LayoutDirective.vertical(gap=1.5),
            title="Demo Scene",
            metadata={
                "demo": True,
                "built_at": datetime.now().isoformat(),
            },
        )

        return scene

    def _get_demo_traces(self) -> list[dict[str, Any]]:
        """Get demo traces for projection testing."""
        return [
            {
                "id": "trace-001",
                "origin": "witness",
                "timestamp": datetime.now().isoformat(),
                "stimulus": {"kind": "thought", "content": "Hello world"},
            },
            {
                "id": "trace-002",
                "origin": "brain",
                "timestamp": datetime.now().isoformat(),
                "stimulus": {"kind": "memory", "content": "Remembered item"},
            },
            {
                "id": "trace-003",
                "origin": "gardener",
                "timestamp": datetime.now().isoformat(),
                "stimulus": {"kind": "gesture", "content": "Transition suggested"},
            },
        ]

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        scene = data["scene"]
        views = data["views"]

        lines = [
            "SceneGraph Projection Endpoint",
            "=" * 40,
            "",
            f"Scene: {scene['title']} ({len(scene['nodes'])} nodes)",
            f"Layout: {scene['layout']['direction']}",
            "",
            f"Views: {views['total']} total, {views['active']} active",
            "",
            "Node Kinds:",
        ]

        for kind in data["node_kinds"][:5]:
            lines.append(f"  - {kind}")

        lines.append("")
        lines.append("Lens Modes:")
        for mode in data["lens_modes"]:
            lines.append(f"  - {mode}")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SceneryNode",
]
