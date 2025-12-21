"""
Projection Protocol: AGENTESE Projection Abstractions.

This module provides target-agnostic scene graph primitives that enable
unified projection to React (now) and Servo (future).

Architecture:
    SceneNode - Atomic visual element (PANEL, TRACE, INTENT, etc.)
    SceneGraph - Composable scene structure with category laws
    LayoutDirective - Elastic layout specification
    TerrariumView - Observer-dependent lens over Mark streams

Key Insight (from spec/protocols/servo-substrate.md):
    "Servo is not 'a browser' inside kgents. It is the projection substrate
    that renders the ontology."

The SceneGraph is the ontology. The projection target is the substrate.

Category Laws:
    SceneGraph >> SceneGraph -> SceneGraph  (composition)
    SceneGraph.empty() >> G ≡ G ≡ G >> SceneGraph.empty()  (identity)
    (A >> B) >> C ≡ A >> (B >> C)  (associativity)

Usage:
    from protocols.agentese.projection import (
        SceneGraph,
        SceneNode,
        SceneNodeKind,
        LayoutDirective,
    )

    # Create a scene
    scene = SceneGraph(
        nodes=[
            SceneNode(kind=SceneNodeKind.PANEL, content="Dashboard"),
            SceneNode(kind=SceneNodeKind.TRACE, content=trace_node),
        ],
        layout=LayoutDirective.vertical(),
    )

    # Compose scenes
    combined = header_scene >> body_scene >> footer_scene
"""

from protocols.agentese.projection.scene import (
    LayoutDirective,
    LayoutMode,
    SceneEdge,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
    compose_scenes,
)
from protocols.agentese.projection.terrarium_view import (
    LensConfig,
    LensMode,
    SelectionOperator,
    SelectionPredicate,
    SelectionQuery,
    TerrariumView,
    TerrariumViewStore,
    ViewStatus,
)

__all__ = [
    # Node types
    "SceneNode",
    "SceneNodeKind",
    "SceneEdge",
    # Graph
    "SceneGraph",
    "compose_scenes",
    # Layout
    "LayoutDirective",
    "LayoutMode",
    # TerrariumView
    "TerrariumView",
    "TerrariumViewStore",
    "ViewStatus",
    "SelectionQuery",
    "SelectionPredicate",
    "SelectionOperator",
    "LensConfig",
    "LensMode",
]
