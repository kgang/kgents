"""
AGENTESE Trail Context.

self.trail.* paths for persisted trail management and visualization.

This node exposes the TrailStorageAdapter (Postgres persistence) for:
- Listing saved trails (manifest)
- Loading trail by ID (load)
- Getting trail as react-flow graph data (graph)
- Forking trails (fork)
- Trail status (status)

AGENTESE Principle: "Trails are first-class knowledge artifacts."

Spec: spec/protocols/trail-protocol.md
See: protocols/trail/storage.py

Teaching:
    gotcha: This node uses TrailStorageAdapter (Postgres), NOT file_persistence.py.
            For file-based trails, use self.portal.* (save_trail, load_trail, etc.).

    gotcha: The graph aspect converts trail data to react-flow format for
            the Visual Trail Graph frontend visualization.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# === Affordances ===

TRAIL_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # List saved trails
    "load",  # Load trail by ID
    "graph",  # Get trail as react-flow graph data
    "fork",  # Fork a trail
    "create",  # Create a new trail
    "status",  # Trail storage status
    "suggest",  # AI-suggested connections (Visual Trail Graph Session 3)
)


# === Demo Trail ===
#
# A comprehensive, branching exploration of the kgents architecture.
# Demonstrates:
# - 30 steps across multiple subsystems
# - Branching exploration (parent_index for tree structure)
# - Multiple edge types (structural, semantic, implementation)
# - Rich reasoning traces showing discovery narrative
# - Scale that tests the graph visualization
#

DEMO_TRAIL: dict[str, Any] = {
    "trail_id": "demo",
    "name": "The Kgents Architecture: A Branching Exploration",
    "steps": [
        # === ROOT: Starting from principles ===
        {
            "index": 0,
            "parent_index": None,
            "source_path": "spec/principles.md",
            "edge": None,
            "destination_paths": ["spec/principles.md"],
            "reasoning": "Begin at the source: the seven principles. Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:00:00Z",
        },
        # === BRANCH 1: Categorical Foundations (from principles) ===
        {
            "index": 1,
            "parent_index": 0,
            "source_path": "agents/poly/base.py",
            "edge": "implements",
            "destination_paths": ["agents/poly/base.py"],
            "reasoning": "Principle 5 (Composable) leads to PolyAgent. State × Input → Output. The polynomial functor is the foundation.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:02:00Z",
        },
        {
            "index": 2,
            "parent_index": 1,
            "source_path": "agents/operad/core.py",
            "edge": "contains",
            "destination_paths": ["agents/operad/core.py"],
            "reasoning": "Operads define composition grammar. An Operad(n) takes n inputs and produces one output. Composition IS the API.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:04:00Z",
        },
        {
            "index": 3,
            "parent_index": 2,
            "source_path": "agents/sheaf/gluing.py",
            "edge": "contains",
            "destination_paths": ["agents/sheaf/gluing.py"],
            "reasoning": "Sheaf gluing = emergence. Local consistency → global coherence. This is how agents coordinate without central control.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:06:00Z",
        },
        {
            "index": 4,
            "parent_index": 3,
            "source_path": "spec/agents/bootstrap.md",
            "edge": "specifies",
            "destination_paths": ["spec/agents/bootstrap.md"],
            "reasoning": "The bootstrap equations: PolyAgent → Operad → Sheaf. Each agent genus has generating equations.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:08:00Z",
        },
        # === BRANCH 2: Witness Crown Jewel (from principles) ===
        {
            "index": 5,
            "parent_index": 0,
            "source_path": "spec/services/witness.md",
            "edge": "implements",
            "destination_paths": ["spec/services/witness.md"],
            "reasoning": "Principle 7 (Generative) leads to Witness. The proof IS the decision. Every action must justify itself.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:10:00Z",
        },
        {
            "index": 6,
            "parent_index": 5,
            "source_path": "services/witness/bus.py",
            "edge": "contains",
            "destination_paths": ["services/witness/bus.py"],
            "reasoning": "WitnessBus is the heart - an event bus that records Marks. Every action leaves a trace.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:12:00Z",
        },
        {
            "index": 7,
            "parent_index": 6,
            "source_path": "models/witness.py",
            "edge": "imports",
            "destination_paths": ["models/witness.py"],
            "reasoning": "Mark model: id, action, reasoning, principles, timestamp. Reasoning is MANDATORY. This is not logging.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:14:00Z",
        },
        # === SUB-BRANCH 2a: Trail subsystem (from Witness) ===
        {
            "index": 8,
            "parent_index": 6,
            "source_path": "protocols/trail/storage.py",
            "edge": "contains",
            "destination_paths": ["protocols/trail/storage.py"],
            "reasoning": "Trails are sequences of Marks through conceptual space. TrailStorageAdapter persists to Postgres + pgvector.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:16:00Z",
        },
        {
            "index": 9,
            "parent_index": 8,
            "source_path": "services/witness/trail_bridge.py",
            "edge": "implements",
            "destination_paths": ["services/witness/trail_bridge.py"],
            "reasoning": "TrailBridge converts trails ↔ marks. The two systems unify. Exploration becomes evidence.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:18:00Z",
        },
        {
            "index": 10,
            "parent_index": 9,
            "source_path": "protocols/agentese/contexts/self_trail.py",
            "edge": "implements",
            "destination_paths": ["protocols/agentese/contexts/self_trail.py"],
            "reasoning": "self.trail.* AGENTESE paths expose trails. This is the API for the Visual Trail Graph frontend.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:20:00Z",
        },
        # === SUB-BRANCH 2b: Fusion (from Mark model) ===
        {
            "index": 11,
            "parent_index": 7,
            "source_path": "services/fusion/core.py",
            "edge": "uses",
            "destination_paths": ["services/fusion/core.py"],
            "reasoning": "FusionMark captures dialectic: Kent's view + Claude's view → synthesis. Decisions as artifacts.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:22:00Z",
        },
        {
            "index": 12,
            "parent_index": 11,
            "source_path": "services/fusion/cli.py",
            "edge": "contains",
            "destination_paths": ["services/fusion/cli.py"],
            "reasoning": "'kg decide' command captures reasoning. Philosophy becomes tooling.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:24:00Z",
        },
        # === BRANCH 3: Brain Crown Jewel (from principles) ===
        {
            "index": 13,
            "parent_index": 0,
            "source_path": "services/brain/__init__.py",
            "edge": "implements",
            "destination_paths": ["services/brain/__init__.py"],
            "reasoning": "Principle 2 (Curated) leads to Brain. The spatial cathedral of memory. Intentional over exhaustive.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:26:00Z",
        },
        {
            "index": 14,
            "parent_index": 13,
            "source_path": "services/brain/core.py",
            "edge": "contains",
            "destination_paths": ["services/brain/core.py"],
            "reasoning": "BrainService orchestrates: capture, search, relate. Memory as spatial navigation.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:28:00Z",
        },
        {
            "index": 15,
            "parent_index": 14,
            "source_path": "services/brain/adapters/postgres.py",
            "edge": "contains",
            "destination_paths": ["services/brain/adapters/postgres.py"],
            "reasoning": "PostgresAdapter with pgvector. Semantic search via <=> operator. Thoughts have proximity.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:30:00Z",
        },
        # === SUB-BRANCH 3a: Crystals (from Brain) ===
        {
            "index": 16,
            "parent_index": 14,
            "source_path": "agents/m/crystal.py",
            "edge": "uses",
            "destination_paths": ["agents/m/crystal.py"],
            "reasoning": "ExperienceCrystal: compressed understanding. Born → grows → dies or fossilizes. Memory has lifecycle.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:32:00Z",
        },
        {
            "index": 17,
            "parent_index": 16,
            "source_path": "agents/m/cartography.py",
            "edge": "contains",
            "destination_paths": ["agents/m/cartography.py"],
            "reasoning": "Memory cartography: navigable maps of thought-space. Spatial > hierarchical for organic memory.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:34:00Z",
        },
        # === BRANCH 4: AGENTESE Protocol (from principles) ===
        {
            "index": 18,
            "parent_index": 0,
            "source_path": "protocols/agentese/parser.py",
            "edge": "implements",
            "destination_paths": ["protocols/agentese/parser.py"],
            "reasoning": "Principle 6 (Heterarchical) leads to AGENTESE. Verb-first ontology. world.house.manifest.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:36:00Z",
        },
        {
            "index": 19,
            "parent_index": 18,
            "source_path": "protocols/agentese/gateway.py",
            "edge": "contains",
            "destination_paths": ["protocols/agentese/gateway.py"],
            "reasoning": "Logos gateway: invoke(path, observer) → Renderable. Observer determines what is perceived.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:38:00Z",
        },
        {
            "index": 20,
            "parent_index": 19,
            "source_path": "protocols/agentese/node.py",
            "edge": "contains",
            "destination_paths": ["protocols/agentese/node.py"],
            "reasoning": "@node decorator registers paths. Aspects are actions: manifest, witness, refine, sip, tithe.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:40:00Z",
        },
        # === SUB-BRANCH 4a: Five Contexts ===
        {
            "index": 21,
            "parent_index": 19,
            "source_path": "protocols/agentese/contexts/world_context.py",
            "edge": "contains",
            "destination_paths": ["protocols/agentese/contexts/world_context.py"],
            "reasoning": "world.* - The External. Entities, environments, tools. What exists outside the agent.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:42:00Z",
        },
        {
            "index": 22,
            "parent_index": 19,
            "source_path": "protocols/agentese/contexts/self_context.py",
            "edge": "contains",
            "destination_paths": ["protocols/agentese/contexts/self_context.py"],
            "reasoning": "self.* - The Internal. Memory, capability, state. The agent's introspection.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:44:00Z",
        },
        {
            "index": 23,
            "parent_index": 19,
            "source_path": "protocols/agentese/contexts/time_context.py",
            "edge": "contains",
            "destination_paths": ["protocols/agentese/contexts/time_context.py"],
            "reasoning": "time.* - The Temporal. Traces, forecasts, schedules. Time is not just a dimension.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:46:00Z",
        },
        # === BRANCH 5: Frontend Visualization (from Trail) ===
        {
            "index": 24,
            "parent_index": 10,
            "source_path": "web/src/pages/Trail.tsx",
            "edge": "projects",
            "destination_paths": ["web/src/pages/Trail.tsx"],
            "reasoning": "React frontend for Visual Trail Graph. Bush's Memex realized as force-directed graph.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:48:00Z",
        },
        {
            "index": 25,
            "parent_index": 24,
            "source_path": "web/src/components/trail/TrailGraph.tsx",
            "edge": "contains",
            "destination_paths": ["web/src/components/trail/TrailGraph.tsx"],
            "reasoning": "react-flow + d3-force. Nodes repel, edges act as springs. Knowledge topology emerges.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:50:00Z",
        },
        {
            "index": 26,
            "parent_index": 25,
            "source_path": "web/src/components/trail/ContextNode.tsx",
            "edge": "contains",
            "destination_paths": ["web/src/components/trail/ContextNode.tsx"],
            "reasoning": "Custom react-flow node. Hover reveals reasoning tooltip. Spring animations for joy.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:52:00Z",
        },
        {
            "index": 27,
            "parent_index": 25,
            "source_path": "web/src/hooks/useForceLayout.ts",
            "edge": "uses",
            "destination_paths": ["web/src/hooks/useForceLayout.ts"],
            "reasoning": "d3-force physics: charge repulsion, link springs, collision detection. Semantic edges = longer springs.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:54:00Z",
        },
        # === CONVERGENCE: Back to meta-circularity ===
        {
            "index": 28,
            "parent_index": 4,
            "source_path": "CLAUDE.md",
            "edge": "semantic:encodes",
            "destination_paths": ["CLAUDE.md"],
            "reasoning": "Meta-circularity! CLAUDE.md encodes the principles that create the tools that modify CLAUDE.md.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:56:00Z",
        },
        {
            "index": 29,
            "parent_index": 28,
            "source_path": "spec/constitution.md",
            "edge": "semantic:grounds",
            "destination_paths": ["spec/constitution.md"],
            "reasoning": "The Constitution: 7 principles + 7 articles. Ontology (what agents are) + Governance (how they relate).",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:58:00Z",
        },
    ],
    "annotations": {
        0: "Root: All paths lead from principles",
        4: "Categorical: The mathematical foundation",
        10: "Trail: Meta-circularity begins here",
        19: "AGENTESE: The universal protocol",
        24: "Frontend: Where exploration becomes visible",
        29: "Constitution: The ground beneath the ground",
    },
    "version": 2,
    "created_at": "2025-12-22T09:00:00Z",
    "updated_at": "2025-12-22T09:58:00Z",
    "forked_from_id": None,
    "topics": [
        "kgents",
        "architecture",
        "categorical",
        "witness",
        "brain",
        "agentese",
        "trail",
        "frontend",
        "meta",
        "philosophy",
        "branching",
        "exploration",
    ],
}


def get_demo_trail() -> dict[str, Any]:
    """
    Return the demo trail.

    This is a comprehensive exploration of the Witness Crown Jewel,
    demonstrating:
    - Multiple edge types (implements, contains, imports, semantic, uses, projects)
    - Rich reasoning traces with philosophical grounding
    - A coherent narrative arc (spec → impl → unification → projection)
    - Evidence that builds to "definitive" strength
    - Meta-circularity (the trail explores the system that creates trails)
    """
    return DEMO_TRAIL.copy()


# === React Flow Data Helpers ===


def trail_to_react_flow(
    trail_data: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Convert a trail to react-flow compatible nodes and edges.

    Layout Strategy: Hierarchical tree with automatic positioning.
    - Root at top, branches spread horizontally
    - Each step becomes a node
    - Edges connect based on parent_index (branching) or sequential (linear)

    Args:
        trail_data: Trail data dict with 'steps' list

    Returns:
        Tuple of (nodes, edges) for react-flow
    """
    from collections import defaultdict

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    steps = trail_data.get("steps", [])
    if not steps:
        return nodes, edges

    # Layout constants
    X_SPACING = 250  # Horizontal spacing between sibling nodes
    Y_SPACING = 120  # Vertical spacing between levels

    # Build parent-child map for branching layout
    children_map: dict[int, list[int]] = defaultdict(list)
    has_branching = False
    for i, step in enumerate(steps):
        parent_idx = step.get("parent_index")
        if parent_idx is not None:
            children_map[parent_idx].append(i)
            # Detect branching: any parent has >1 child
            if len(children_map[parent_idx]) > 1:
                has_branching = True

    # Calculate positions with tree layout for branching trails
    positions: dict[int, tuple[int, int]] = {}

    def calculate_subtree_width(idx: int) -> int:
        """Calculate the width needed for a subtree."""
        children = children_map.get(idx, [])
        if not children:
            return X_SPACING
        return sum(calculate_subtree_width(c) for c in children)

    def position_node(idx: int, depth: int, x_start: int) -> None:
        """Position a node and its descendants."""
        children = children_map.get(idx, [])
        if not children:
            # Leaf node
            positions[idx] = (x_start, depth * Y_SPACING + 50)
        else:
            # Position children first, then center parent
            current_x = x_start
            for child in children:
                child_width = calculate_subtree_width(child)
                position_node(child, depth + 1, current_x)
                current_x += child_width

            # Center parent over children
            first_child_x = positions[children[0]][0]
            last_child_x = positions[children[-1]][0]
            parent_x = (first_child_x + last_child_x) // 2
            positions[idx] = (parent_x, depth * Y_SPACING + 50)

    if has_branching:
        # Find root nodes (no parent_index)
        roots = [i for i, step in enumerate(steps) if step.get("parent_index") is None]
        current_x = 100
        for root in roots:
            width = calculate_subtree_width(root)
            position_node(root, 0, current_x)
            current_x += width
    else:
        # Linear layout: simple vertical stack
        for i in range(len(steps)):
            positions[i] = (400, i * Y_SPACING + 50)

    # Create nodes
    for i, step in enumerate(steps):
        node_id = f"step-{i}"
        source_path = step.get("source_path", step.get("node_path", f"step-{i}"))
        edge_type = step.get("edge", step.get("edge_type"))
        reasoning = step.get("reasoning", step.get("annotation", ""))
        parent_idx = step.get("parent_index")

        # Extract holon name from path (filename without extension)
        path_parts = source_path.replace("\\", "/").split("/")
        filename = path_parts[-1] if path_parts else source_path
        holon = filename.rsplit(".", 1)[0] if "." in filename else filename

        # Get calculated position
        x, y = positions.get(i, (400, i * Y_SPACING + 50))

        # Create node
        node: dict[str, Any] = {
            "id": node_id,
            "type": "context",  # Custom node type for TrailGraph
            "position": {"x": x, "y": y},
            "data": {
                "path": source_path,
                "holon": holon,
                "step_index": i,
                "edge_type": edge_type,
                "reasoning": reasoning,
                "is_current": i == len(steps) - 1,
                "parent_index": parent_idx,  # Include for frontend
            },
        }
        nodes.append(node)

        # Create edge from parent
        # For branching trails: use parent_index
        # For linear trails: use previous step (i-1)
        source_idx = parent_idx if parent_idx is not None else (i - 1 if i > 0 else None)
        if source_idx is not None and source_idx >= 0:
            source_id = f"step-{source_idx}"
            edge_id = f"edge-{source_idx}-{i}"

            # Determine edge style based on type
            is_semantic = edge_type in ("semantic", "similar_to", "type_of", "pattern")

            edge: dict[str, Any] = {
                "id": edge_id,
                "source": source_id,
                "target": node_id,
                "label": edge_type or "",
                "type": "semantic" if is_semantic else "structural",
                "animated": is_semantic,
                "style": {
                    "strokeDasharray": "5,5" if is_semantic else "0",
                },
            }
            edges.append(edge)

    return nodes, edges


def analyze_trail_evidence(trail_data: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze a trail to compute evidence metrics.

    Args:
        trail_data: Trail data dict with 'steps' list

    Returns:
        Evidence metrics dict
    """
    steps = trail_data.get("steps", [])

    # Count unique paths and edges
    paths = {s.get("source_path", s.get("node_path", "")) for s in steps}
    edges = {
        s.get("edge", s.get("edge_type", "")) for s in steps if s.get("edge") or s.get("edge_type")
    }

    # Determine evidence strength based on trail characteristics
    step_count = len(steps)
    unique_count = len(paths)

    if step_count >= 10 and unique_count >= 8:
        strength = "definitive"
    elif step_count >= 5 and unique_count >= 4:
        strength = "strong"
    elif step_count >= 3 and unique_count >= 2:
        strength = "moderate"
    else:
        strength = "weak"

    return {
        "step_count": step_count,
        "unique_paths": unique_count,
        "unique_edges": len(edges),
        "evidence_strength": strength,
    }


# === AGENTESE Node ===


@node(
    "self.trail",
    description="Trail management and visualization (Postgres persistence)",
)
@dataclass
class TrailNode(BaseLogosNode):
    """
    self.trail - Persisted trail management.

    This node provides access to trails stored in Postgres via TrailStorageAdapter.
    Use this for the Visual Trail Graph frontend visualization.

    For file-based trails (transient exploration), use self.portal.* instead.

    Aspects:
        manifest — List saved trails (returns trail summaries)
        load — Load trail by ID (returns full trail data)
        graph — Get trail as react-flow graph data (nodes + edges)
        fork — Fork a trail at a specific point
        status — Trail storage health status

    Usage:
        kg op self.trail.manifest              # List trails
        kg op self.trail.load trail-abc123     # Load specific trail
        kg op self.trail.graph trail-abc123    # Get react-flow data
        kg op self.trail.status                # Storage health
    """

    _handle: str = "self.trail"

    # Storage adapter (lazy-initialized)
    _storage: Any | None = field(default=None, repr=False)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return TRAIL_AFFORDANCES

    async def _ensure_storage(self) -> Any:
        """
        Ensure we have an initialized TrailStorageAdapter.

        Lazily imports and creates the adapter to avoid circular dependencies.
        """
        if self._storage is None:
            try:
                from protocols.trail.storage import TrailStorageAdapter
                from services.bootstrap import get_registry

                registry = get_registry()
                session_factory = registry.session_factory
                self._storage = TrailStorageAdapter(session_factory=session_factory)
            except (ImportError, RuntimeError) as e:
                logger.warning(f"TrailStorageAdapter not available: {e}")
                raise RuntimeError("Trail storage not available") from e
        return self._storage

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List saved trails with optional filters",
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        List saved trails.

        AGENTESE: self.trail.manifest

        Args:
            limit: Maximum trails to return (default 50)
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Colored list of trails
            For JSON: {trails: [...], count: N} in metadata
        """
        # Extract parameters from kwargs with defaults
        limit: int = kwargs.get("limit", 50)
        response_format: str = kwargs.get("response_format", "cli")

        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        # Always include the demo trail at the top of the list
        demo = get_demo_trail()
        demo_summary = {
            "trail_id": demo["trail_id"],
            "name": demo["name"],
            "step_count": len(demo["steps"]),
            "version": demo["version"],
            "created_at": demo["created_at"],
            "updated_at": demo["updated_at"],
            "forked_from_id": demo["forked_from_id"],
            "topics": demo["topics"],
        }

        try:
            storage = await self._ensure_storage()
            trails = await storage.list_trails(limit=limit - 1)  # Reserve one slot for demo

            # Convert to dict format for JSON response
            trails_data = [demo_summary] + [
                {
                    "trail_id": t.trail_id,
                    "name": t.name,
                    "step_count": len(t.steps),
                    "version": t.version,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                    "forked_from_id": t.forked_from_id,
                    "topics": t.topics,
                }
                for t in trails
            ]

            if response_format == "json":
                return BasicRendering(
                    summary=f"Found {len(trails_data)} trails",
                    content="",
                    metadata={
                        "trails": trails_data,
                        "count": len(trails_data),
                        "route": "/trail",
                    },
                )

            # CLI format - always show demo trail first
            lines = [f"{BOLD}Saved Trails ({len(trails_data)}){RESET}\n"]

            # Show demo trail with special marker
            lines.append(
                f"  {CYAN}★{RESET} {demo_summary['name']} "
                f"{DIM}({demo_summary['step_count']} steps, demo){RESET}"
            )
            lines.append(f"    {DIM}ID: demo{RESET}")
            lines.append(f"    {DIM}Topics: {', '.join(demo_summary['topics'][:5])}{RESET}")

            for t in trails:
                created = t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "unknown"
                step_count = len(t.steps)

                lines.append(
                    f"  {CYAN}●{RESET} {t.name or '(untitled)'} "
                    f"{DIM}({step_count} steps, {created}){RESET}"
                )
                lines.append(f"    {DIM}ID: {t.trail_id}{RESET}")
                if t.topics:
                    lines.append(f"    {DIM}Topics: {', '.join(t.topics[:5])}{RESET}")

            lines.append(f"\n{DIM}Load: kg op self.trail.load <trail_id>{RESET}")
            lines.append(f"{DIM}Graph: kg op self.trail.graph <trail_id>{RESET}")

            return BasicRendering(
                summary=f"Found {len(trails_data)} trails",
                content="\n".join(lines),
                metadata={"trails": trails_data, "count": len(trails_data)},
            )

        except Exception as e:
            logger.warning(f"Storage failed, returning demo trail only: {e}")
            # Even if storage fails, we can still show the demo trail
            if response_format == "json":
                return BasicRendering(
                    summary="Found 1 trail (demo only)",
                    content="",
                    metadata={
                        "trails": [demo_summary],
                        "count": 1,
                        "route": "/trail",
                        "warning": f"Storage unavailable: {e}",
                    },
                )

            lines = [f"{BOLD}Saved Trails (demo only){RESET}\n"]
            lines.append(f"{YELLOW}⚠ Storage unavailable - showing demo only{RESET}\n")
            lines.append(
                f"  {CYAN}★{RESET} {demo_summary['name']} "
                f"{DIM}({demo_summary['step_count']} steps, demo){RESET}"
            )
            lines.append(f"    {DIM}ID: demo{RESET}")
            lines.append(f"    {DIM}Topics: {', '.join(demo_summary['topics'][:5])}{RESET}")
            lines.append(f"\n{DIM}Load: kg op self.trail.load demo{RESET}")

            return BasicRendering(
                summary="Found 1 trail (demo only)",
                content="\n".join(lines),
                metadata={"trails": [demo_summary], "count": 1, "warning": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Load a trail by ID",
    )
    async def load(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Load a trail by ID.

        AGENTESE: self.trail.load

        Special IDs:
        - "demo" — Returns comprehensive demo trail (no DB required)

        Args:
            trail_id: Trail ID to load
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Formatted trail display
            For JSON: {trail: {...}, evidence: {...}} in metadata
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        # Handle demo trail specially (no DB required)
        if trail_id == "demo":
            trail_dict = get_demo_trail()
            evidence = analyze_trail_evidence(trail_dict)

            if response_format == "json":
                return BasicRendering(
                    summary=f"Trail: {trail_dict['name']}",
                    content="",
                    metadata={
                        "trail": trail_dict,
                        "evidence": evidence,
                        "route": f"/trail/{trail_id}",
                    },
                )

            # CLI format for demo
            lines = [f"{BOLD}Trail: {trail_dict['name']}{RESET}\n"]
            lines.append(f"{BOLD}ID:{RESET} {trail_dict['trail_id']}")
            lines.append(f"{BOLD}Version:{RESET} {trail_dict['version']}")
            lines.append(f"{BOLD}Steps:{RESET} {len(trail_dict['steps'])}")
            lines.append(f"{BOLD}Evidence:{RESET} {evidence['evidence_strength']}")
            lines.append(f"{BOLD}Topics:{RESET} {', '.join(trail_dict['topics'])}")
            lines.append("")
            lines.append(f"{BOLD}Steps:{RESET}")

            for step in trail_dict["steps"]:
                edge = step.get("edge", "")
                source = step.get("source_path", "?")
                reasoning = step.get("reasoning", "")
                i = step.get("index", 0)

                if edge:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {GREEN}──[{edge}]──>{RESET}")
                else:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {DIM}(start){RESET}")

                if reasoning:
                    display = f"{reasoning[:60]}..." if len(reasoning) > 60 else reasoning
                    lines.append(f"      {DIM}{display}{RESET}")

            return BasicRendering(
                summary=f"Trail: {trail_dict['name']}",
                content="\n".join(lines),
                metadata={"trail": trail_dict, "evidence": evidence},
            )

        try:
            storage = await self._ensure_storage()
            trail = await storage.load_trail(trail_id)

            if trail is None:
                if response_format == "json":
                    return BasicRendering(
                        summary=f"Trail not found: {trail_id}",
                        content="",
                        metadata={"error": "not_found", "trail_id": trail_id},
                    )

                return BasicRendering(
                    summary=f"Trail not found: {trail_id}",
                    content=f"{YELLOW}Trail not found: {trail_id}{RESET}",
                    metadata={"error": "not_found", "trail_id": trail_id},
                )

            # Convert to dict
            trail_dict = {
                "trail_id": trail.trail_id,
                "name": trail.name,
                "steps": trail.steps,
                "annotations": trail.annotations,
                "version": trail.version,
                "created_at": trail.created_at.isoformat() if trail.created_at else None,
                "updated_at": trail.updated_at.isoformat() if trail.updated_at else None,
                "forked_from_id": trail.forked_from_id,
                "topics": trail.topics,
            }

            # Analyze evidence
            evidence = analyze_trail_evidence(trail_dict)

            if response_format == "json":
                return BasicRendering(
                    summary=f"Trail: {trail.name}",
                    content="",
                    metadata={
                        "trail": trail_dict,
                        "evidence": evidence,
                        "route": f"/trail/{trail_id}",
                    },
                )

            # CLI format
            lines = [f"{BOLD}Trail: {trail.name or '(untitled)'}{RESET}\n"]
            lines.append(f"{BOLD}ID:{RESET} {trail.trail_id}")
            lines.append(f"{BOLD}Version:{RESET} {trail.version}")
            lines.append(f"{BOLD}Steps:{RESET} {len(trail.steps)}")
            lines.append(f"{BOLD}Evidence:{RESET} {evidence['evidence_strength']}")

            if trail.forked_from_id:
                lines.append(f"{BOLD}Forked from:{RESET} {trail.forked_from_id}")

            if trail.topics:
                lines.append(f"{BOLD}Topics:{RESET} {', '.join(trail.topics)}")

            lines.append("")
            lines.append(f"{BOLD}Steps:{RESET}")

            for i, step in enumerate(trail.steps):
                edge = step.get("edge") or step.get("edge_type", "")
                source = step.get("source_path", "?")
                reasoning = step.get("reasoning", "")

                if edge:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {GREEN}──[{edge}]──>{RESET}")
                else:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {DIM}(start){RESET}")

                if reasoning:
                    lines.append(
                        f"      {DIM}{reasoning[:60]}...{RESET}"
                        if len(reasoning) > 60
                        else f"      {DIM}{reasoning}{RESET}"
                    )

            return BasicRendering(
                summary=f"Trail: {trail.name}",
                content="\n".join(lines),
                metadata={"trail": trail_dict, "evidence": evidence},
            )

        except Exception as e:
            logger.exception("Failed to load trail")
            return BasicRendering(
                summary="Failed to load trail",
                content=f"Error: {e}",
                metadata={"error": str(e), "trail_id": trail_id},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get trail as react-flow graph data for visualization",
    )
    async def graph(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        response_format: str = "json",
    ) -> Renderable:
        """
        Get trail as react-flow compatible graph data.

        AGENTESE: self.trail.graph

        This aspect is specifically designed for the Visual Trail Graph frontend.
        It converts the trail to nodes and edges that react-flow can render.

        Args:
            trail_id: Trail ID to convert to graph
            response_format: Always "json" for frontend (CLI shows summary)

        Returns:
            {nodes: [...], edges: [...], trail: {...}, evidence: {...}} in metadata
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        # Handle demo trail specially (no DB required)
        if trail_id == "demo":
            trail_dict = get_demo_trail()
            nodes, edges = trail_to_react_flow(trail_dict)
            evidence = analyze_trail_evidence(trail_dict)

            if response_format == "cli":
                lines = [f"{BOLD}Trail Graph: {trail_dict['name']}{RESET}\n"]
                lines.append(f"{BOLD}Nodes:{RESET} {len(nodes)}")
                lines.append(f"{BOLD}Edges:{RESET} {len(edges)}")
                lines.append(f"{BOLD}Evidence:{RESET} {evidence['evidence_strength']}")
                lines.append(f"\n{DIM}Use response_format=json for full graph data.{RESET}")

                return BasicRendering(
                    summary=f"Trail graph: {len(nodes)} nodes, {len(edges)} edges",
                    content="\n".join(lines),
                    metadata={
                        "nodes": nodes,
                        "edges": edges,
                        "trail": trail_dict,
                        "evidence": evidence,
                    },
                )

            return BasicRendering(
                summary=f"Trail graph: {len(nodes)} nodes, {len(edges)} edges",
                content="",
                metadata={
                    "nodes": nodes,
                    "edges": edges,
                    "trail": trail_dict,
                    "evidence": evidence,
                    "route": f"/trail/{trail_id}",
                },
            )

        try:
            storage = await self._ensure_storage()
            trail = await storage.load_trail(trail_id)

            if trail is None:
                return BasicRendering(
                    summary=f"Trail not found: {trail_id}",
                    content=f"{YELLOW}Trail not found: {trail_id}{RESET}"
                    if response_format == "cli"
                    else "",
                    metadata={"error": "not_found", "trail_id": trail_id},
                )

            # Convert to dict
            trail_dict = {
                "trail_id": trail.trail_id,
                "name": trail.name,
                "steps": trail.steps,
                "annotations": trail.annotations,
                "version": trail.version,
                "created_at": trail.created_at.isoformat() if trail.created_at else None,
                "updated_at": trail.updated_at.isoformat() if trail.updated_at else None,
                "forked_from_id": trail.forked_from_id,
                "topics": trail.topics,
            }

            # Convert to react-flow format
            nodes, edges = trail_to_react_flow(trail_dict)

            # Analyze evidence
            evidence = analyze_trail_evidence(trail_dict)

            if response_format == "cli":
                lines = [f"{BOLD}Trail Graph: {trail.name}{RESET}\n"]
                lines.append(f"{BOLD}Nodes:{RESET} {len(nodes)}")
                lines.append(f"{BOLD}Edges:{RESET} {len(edges)}")
                lines.append(f"{BOLD}Evidence:{RESET} {evidence['evidence_strength']}")
                lines.append(f"\n{DIM}Use response_format=json for full graph data.{RESET}")

                return BasicRendering(
                    summary=f"Trail graph: {len(nodes)} nodes, {len(edges)} edges",
                    content="\n".join(lines),
                    metadata={
                        "nodes": nodes,
                        "edges": edges,
                        "trail": trail_dict,
                        "evidence": evidence,
                    },
                )

            return BasicRendering(
                summary=f"Trail graph: {len(nodes)} nodes, {len(edges)} edges",
                content="",
                metadata={
                    "nodes": nodes,
                    "edges": edges,
                    "trail": trail_dict,
                    "evidence": evidence,
                    "route": f"/trail/{trail_id}",
                },
            )

        except Exception as e:
            logger.exception("Failed to get trail graph")
            return BasicRendering(
                summary="Failed to get trail graph",
                content=f"Error: {e}",
                metadata={"error": str(e), "trail_id": trail_id},
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("trail_storage")],
        help="Fork a trail at a specific point",
    )
    async def fork(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        name: str,
        fork_point: int | None = None,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Fork a trail at a specific point.

        AGENTESE: self.trail.fork

        Creates an independent copy of the trail up to fork_point.
        Changes to the fork don't affect the parent.

        Args:
            trail_id: Trail to fork
            name: Name for the forked trail
            fork_point: Step index to fork at (default: current end)
            response_format: "cli" or "json"

        Returns:
            Forked trail metadata
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        try:
            storage = await self._ensure_storage()

            # Create observer object for storage
            from protocols.exploration.types import Observer as ExplorationObserver

            exploration_obs = ExplorationObserver(
                id=obs.id if hasattr(obs, "id") else "unknown",
                archetype=obs.archetype,
            )

            result = await storage.fork_trail(
                trail_id=trail_id,
                new_name=name,
                fork_point=fork_point,
                observer=exploration_obs,
            )

            if response_format == "json":
                return BasicRendering(
                    summary=f"Forked trail: {result.trail_id}",
                    content="",
                    metadata={
                        "trail_id": result.trail_id,
                        "name": result.name,
                        "step_count": result.step_count,
                        "forked_from": trail_id,
                        "fork_point": fork_point,
                        "route": f"/trail/{result.trail_id}",
                    },
                )

            lines = [f"{GREEN}✓ Trail forked{RESET}\n"]
            lines.append(f"{BOLD}New Trail ID:{RESET} {result.trail_id}")
            lines.append(f"{BOLD}Name:{RESET} {result.name}")
            lines.append(f"{BOLD}Steps:{RESET} {result.step_count}")
            lines.append(f"{BOLD}Forked from:{RESET} {trail_id}")
            if fork_point is not None:
                lines.append(f"{BOLD}Fork point:{RESET} step {fork_point}")

            return BasicRendering(
                summary=f"Forked trail: {result.trail_id}",
                content="\n".join(lines),
                metadata={
                    "trail_id": result.trail_id,
                    "name": result.name,
                    "step_count": result.step_count,
                    "forked_from": trail_id,
                    "fork_point": fork_point,
                },
            )

        except Exception as e:
            logger.exception("Failed to fork trail")
            return BasicRendering(
                summary="Failed to fork trail",
                content=f"{YELLOW}Error: {e}{RESET}" if response_format == "cli" else "",
                metadata={"error": str(e), "trail_id": trail_id},
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("trail_storage")],
        help="Create a new trail",
    )
    async def create(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        name: str,
        steps: list[dict[str, Any]],
        topics: list[str] | None = None,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Create a new trail.

        AGENTESE: self.trail.create

        This aspect is used by the Trail Builder UI to create new trails.

        Args:
            name: Trail name
            steps: List of step dicts with {path, edge, reasoning}
            topics: Optional topic tags
            response_format: "cli" or "json"

        Returns:
            Created trail metadata with trail_id
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        if not name or not name.strip():
            return BasicRendering(
                summary="Trail name is required",
                content=f"{YELLOW}Error: Trail name is required{RESET}"
                if response_format == "cli"
                else "",
                metadata={"error": "name_required"},
            )

        if not steps or len(steps) == 0:
            return BasicRendering(
                summary="At least one step is required",
                content=f"{YELLOW}Error: At least one step is required{RESET}"
                if response_format == "cli"
                else "",
                metadata={"error": "steps_required"},
            )

        try:
            storage = await self._ensure_storage()

            # Validate and format steps
            validated_steps: list[dict[str, Any]] = []
            for i, step in enumerate(steps):
                step_path = step.get("path", "")
                if not step_path:
                    return BasicRendering(
                        summary=f"Step {i + 1} missing path",
                        content=f"{YELLOW}Error: Step {i + 1} missing path{RESET}"
                        if response_format == "cli"
                        else "",
                        metadata={"error": "step_missing_path", "step_index": i},
                    )

                # Validate parent_index for branching trails
                parent_idx = step.get("parent_index")
                if parent_idx is not None:
                    if not isinstance(parent_idx, int) or parent_idx < 0 or parent_idx >= i:
                        return BasicRendering(
                            summary=f"Invalid parent_index at step {i + 1}",
                            content=f"{YELLOW}Error: parent_index {parent_idx} invalid at step {i + 1} (must be 0..{i - 1}){RESET}"
                            if response_format == "cli"
                            else "",
                            metadata={
                                "error": "invalid_parent_index",
                                "step_index": i,
                                "parent_index": parent_idx,
                            },
                        )

                validated_steps.append(
                    {
                        "index": i,
                        "parent_index": parent_idx,  # For branching trails
                        "source_path": step_path,
                        "edge": step.get("edge") if i > 0 else None,  # First step has no edge
                        "destination_paths": [step_path],
                        "reasoning": step.get("reasoning", ""),
                        "loop_status": "OK",
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    }
                )

            # Create observer for storage
            from protocols.exploration.types import Observer as ExplorationObserver

            exploration_obs = ExplorationObserver(
                id=obs.id if hasattr(obs, "id") else "unknown",
                archetype=obs.archetype,
            )

            # Create the trail
            result = await storage.create_trail(
                name=name.strip(),
                steps=validated_steps,
                topics=topics or [],
                observer=exploration_obs,
            )

            if response_format == "json":
                return BasicRendering(
                    summary=f"Created trail: {result.trail_id}",
                    content="",
                    metadata={
                        "trail_id": result.trail_id,
                        "name": result.name,
                        "step_count": result.step_count,
                        "route": f"/trail/{result.trail_id}",
                    },
                )

            lines = [f"{GREEN}✓ Trail created{RESET}\n"]
            lines.append(f"{BOLD}Trail ID:{RESET} {result.trail_id}")
            lines.append(f"{BOLD}Name:{RESET} {result.name}")
            lines.append(f"{BOLD}Steps:{RESET} {result.step_count}")
            if topics:
                lines.append(f"{BOLD}Topics:{RESET} {', '.join(topics)}")
            lines.append(f"\n{BOLD}View:{RESET} kg op self.trail.load {result.trail_id}")

            return BasicRendering(
                summary=f"Created trail: {result.trail_id}",
                content="\n".join(lines),
                metadata={
                    "trail_id": result.trail_id,
                    "name": result.name,
                    "step_count": result.step_count,
                },
            )

        except Exception as e:
            logger.exception("Failed to create trail")
            return BasicRendering(
                summary="Failed to create trail",
                content=f"{YELLOW}Error: {e}{RESET}" if response_format == "cli" else "",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get trail storage health status",
    )
    async def status(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        response_format: str = "cli",
    ) -> Renderable:
        """
        Get trail storage health status.

        AGENTESE: self.trail.status

        Returns:
            Storage health metrics
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        GREEN = "\033[32m"
        RESET = "\033[0m"

        try:
            storage = await self._ensure_storage()
            status = await storage.manifest()

            status_dict = {
                "total_trails": status.total_trails,
                "total_steps": status.total_steps,
                "active_trails": status.active_trails,
                "forked_trails": status.forked_trails,
                "storage_backend": status.storage_backend,
            }

            if response_format == "json":
                return BasicRendering(
                    summary="Trail storage status",
                    content="",
                    metadata={"status": status_dict},
                )

            lines = [f"{BOLD}Trail Storage Status{RESET}\n"]
            lines.append(f"{BOLD}Total Trails:{RESET} {status.total_trails}")
            lines.append(f"{BOLD}Active Trails:{RESET} {status.active_trails}")
            lines.append(f"{BOLD}Forked Trails:{RESET} {status.forked_trails}")
            lines.append(f"{BOLD}Total Steps:{RESET} {status.total_steps}")
            lines.append(f"{BOLD}Backend:{RESET} {GREEN}{status.storage_backend}{RESET}")

            return BasicRendering(
                summary="Trail storage status",
                content="\n".join(lines),
                metadata={"status": status_dict},
            )

        except Exception as e:
            logger.exception("Failed to get trail status")
            return BasicRendering(
                summary="Failed to get trail status",
                content=f"Error: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get AI-suggested connections for a trail step",
    )
    async def suggest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        step_index: int = -1,
        response_format: str = "json",
    ) -> Renderable:
        """
        Get AI-suggested next steps for a trail.

        AGENTESE: self.trail.suggest

        Visual Trail Graph Session 3: Intelligence

        Args:
            trail_id: Trail to get suggestions for
            step_index: Step to suggest from (-1 = last step)
            response_format: "cli" or "json"

        Returns:
            - related_trails: Semantically similar trails
            - suggested_files: Files to explore next (based on patterns)
            - inferred_edges: Suggested edge types with confidence
            - reasoning_prompts: Questions to consider
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

        # Handle demo trail specially
        if trail_id == "demo":
            trail_dict = get_demo_trail()
            steps = trail_dict.get("steps", [])
        else:
            try:
                storage = await self._ensure_storage()
                trail = await storage.load_trail(trail_id)

                if trail is None:
                    return BasicRendering(
                        summary=f"Trail not found: {trail_id}",
                        metadata={"error": "not_found", "trail_id": trail_id},
                    )

                steps = trail.steps
                trail_dict = {
                    "trail_id": trail.trail_id,
                    "name": trail.name,
                    "steps": steps,
                    "topics": trail.topics,
                }
            except Exception as e:
                logger.warning(f"Storage failed: {e}")
                return BasicRendering(
                    summary="Storage unavailable",
                    metadata={"error": str(e)},
                )

        if not steps:
            return BasicRendering(
                summary="Trail has no steps",
                metadata={"suggestions": []},
            )

        # Get target step
        target_idx = step_index if step_index >= 0 else len(steps) - 1
        if target_idx >= len(steps):
            target_idx = len(steps) - 1

        current_step = steps[target_idx]

        # Generate suggestions
        suggestions = await self._generate_suggestions(trail_dict, current_step, target_idx)

        if response_format == "cli":
            lines = [f"{BOLD}AI Suggestions for step {target_idx + 1}{RESET}\n"]

            if suggestions.get("related_trails"):
                lines.append(f"{BOLD}Related Trails:{RESET}")
                for t in suggestions["related_trails"][:3]:
                    lines.append(f"  {CYAN}●{RESET} {t['name']} ({int(t['score'] * 100)}% similar)")

            if suggestions.get("suggested_files"):
                lines.append(f"\n{BOLD}Explore Next:{RESET}")
                for f in suggestions["suggested_files"][:3]:
                    lines.append(f"  {DIM}→{RESET} {f['path']}")
                    lines.append(f"    {DIM}{f['reason']}{RESET}")

            if suggestions.get("reasoning_prompts"):
                lines.append(f"\n{BOLD}Questions to Consider:{RESET}")
                for p in suggestions["reasoning_prompts"][:3]:
                    lines.append(f"  {DIM}?{RESET} {p}")

            return BasicRendering(
                summary=f"Suggestions for step {target_idx + 1}",
                content="\n".join(lines),
                metadata={
                    "trail_id": trail_id,
                    "step_index": target_idx,
                    **suggestions,
                },
            )

        return BasicRendering(
            summary=f"Suggestions for step {target_idx + 1}",
            content="",
            metadata={
                "trail_id": trail_id,
                "step_index": target_idx,
                **suggestions,
            },
        )

    async def _generate_suggestions(
        self,
        trail_dict: dict[str, Any],
        current_step: dict[str, Any],
        step_index: int,
    ) -> dict[str, Any]:
        """
        Generate full intelligence suggestions.

        Returns dict with:
        - related_trails: Semantically similar trails
        - suggested_files: Files based on path patterns
        - inferred_edges: Edge types with confidence
        - reasoning_prompts: Questions to explore
        """
        related_trails: list[dict[str, Any]] = []
        suggested_files: list[dict[str, Any]] = []
        inferred_edges: list[dict[str, Any]] = []
        reasoning_prompts: list[str] = []

        # Try semantic search if embedder available
        try:
            from services.providers import get_embedder

            embedder = await get_embedder()

            if embedder and current_step.get("reasoning"):
                # Embed current step's context
                text = f"{current_step.get('source_path', '')} {current_step.get('reasoning', '')}"
                embedding = await embedder.embed(text)

                # Search for similar trails
                try:
                    storage = await self._ensure_storage()
                    results = await storage.search_semantic(embedding, limit=5)
                    related_trails = [
                        {
                            "trail_id": r.trail_id,
                            "name": r.name,
                            "score": round(r.score, 3),
                            "step_count": r.step_count,
                        }
                        for r in results
                        if r.trail_id != trail_dict.get("trail_id")  # Exclude self
                    ]
                except Exception as e:
                    logger.debug(f"Semantic search failed: {e}")
        except Exception as e:
            logger.debug(f"Embedder not available: {e}")

        # Suggest files based on path patterns
        suggested_files = self._suggest_files(current_step)

        # Infer edge types
        inferred_edges = self._infer_edges(current_step, suggested_files)

        # Generate reasoning prompts
        reasoning_prompts = self._generate_prompts(trail_dict, current_step)

        return {
            "related_trails": related_trails,
            "suggested_files": suggested_files,
            "inferred_edges": inferred_edges,
            "reasoning_prompts": reasoning_prompts,
        }

    def _suggest_files(self, current_step: dict[str, Any]) -> list[dict[str, Any]]:
        """Suggest files based on path patterns."""
        path = current_step.get("source_path", "")
        suggestions: list[dict[str, Any]] = []

        # Pattern: spec → impl
        if path.startswith("spec/"):
            impl_path = path.replace("spec/", "impl/claude/").replace(".md", ".py")
            suggestions.append(
                {
                    "path": impl_path,
                    "reason": "Implementation of this spec",
                    "confidence": 0.8,
                }
            )

        # Pattern: impl → test
        if ".py" in path and "_tests" not in path:
            # Build test path
            parts = path.rsplit("/", 1)
            if len(parts) == 2:
                dir_path, filename = parts
                test_filename = f"test_{filename}"
                test_path = f"{dir_path}/_tests/{test_filename}"
                suggestions.append(
                    {
                        "path": test_path,
                        "reason": "Tests for this module",
                        "confidence": 0.7,
                    }
                )

        # Pattern: service → model
        if "/services/" in path:
            model_name = path.split("/")[-1].replace(".py", "")
            suggestions.append(
                {
                    "path": f"models/{model_name}.py",
                    "reason": "Data model for this service",
                    "confidence": 0.6,
                }
            )

        # Pattern: context node → protocol
        if "/agentese/contexts/" in path:
            suggestions.append(
                {
                    "path": "spec/protocols/agentese.md",
                    "reason": "AGENTESE protocol specification",
                    "confidence": 0.5,
                }
            )

        # Pattern: any .py → principles
        if path.endswith(".py"):
            suggestions.append(
                {
                    "path": "spec/principles.md",
                    "reason": "Ground in first principles",
                    "confidence": 0.4,
                }
            )

        return suggestions[:3]  # Limit to top 3

    def _infer_edges(
        self, current_step: dict[str, Any], suggested_files: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Infer edge types for suggestions."""
        edges: list[dict[str, Any]] = []

        for f in suggested_files:
            path = f["path"]

            if "impl" in path and "spec" in current_step.get("source_path", ""):
                edge_type = "implements"
            elif "test" in path:
                edge_type = "tests"
            elif "model" in path:
                edge_type = "imports"
            elif "principles" in path:
                edge_type = "semantic:grounds"
            elif "spec" in path:
                edge_type = "specifies"
            else:
                edge_type = "uses"

            edges.append(
                {
                    "edge_type": edge_type,
                    "target_path": path,
                    "confidence": f["confidence"],
                }
            )

        return edges

    def _generate_prompts(
        self, trail_dict: dict[str, Any], current_step: dict[str, Any]
    ) -> list[str]:
        """Generate reasoning prompts based on context."""
        prompts: list[str] = []

        # Core prompts
        prompts.append("What principles from spec/principles.md apply here?")
        prompts.append("Are there similar patterns elsewhere in the codebase?")

        # Edge-specific prompts
        edge = current_step.get("edge")
        if edge == "implements":
            prompts.append("Does this implementation match the spec completely?")
        elif edge == "tests":
            prompts.append("What edge cases does this test miss?")
        elif edge and edge.startswith("semantic:"):
            prompts.append("What makes this semantic connection meaningful?")

        # Path-specific prompts
        path = current_step.get("source_path", "")
        if "/services/" in path:
            prompts.append("Is this service following the Crown Jewel pattern?")
        elif "/agents/" in path:
            prompts.append("Does this agent satisfy the category laws?")

        # Trail-specific prompts
        topics = trail_dict.get("topics", [])
        if "witness" in topics:
            prompts.append("How does this connect to the Witness architecture?")
        if "trail" in topics:
            prompts.append("Is this step part of the trail-as-evidence pattern?")

        return prompts[:3]  # Limit to top 3

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect methods."""
        response_format = kwargs.get("response_format", "cli")

        match aspect:
            case "manifest":
                return await self.manifest(observer, **kwargs)
            case "load":
                trail_id = kwargs.get("trail_id", "")
                return await self.load(observer, trail_id, response_format)
            case "graph":
                trail_id = kwargs.get("trail_id", "")
                return await self.graph(observer, trail_id, response_format)
            case "fork":
                trail_id = kwargs.get("trail_id", "")
                name = kwargs.get("name", "Forked Trail")
                fork_point = kwargs.get("fork_point")
                return await self.fork(observer, trail_id, name, fork_point, response_format)
            case "create":
                name = kwargs.get("name", "")
                steps = kwargs.get("steps", [])
                topics = kwargs.get("topics")
                return await self.create(observer, name, steps, topics, response_format)
            case "status":
                return await self.status(observer, response_format)
            case "suggest":
                trail_id = kwargs.get("trail_id", "")
                step_index = kwargs.get("step_index", -1)
                return await self.suggest(observer, trail_id, step_index, response_format)
            case _:
                return BasicRendering(
                    summary=f"Unknown aspect: {aspect}",
                    content=f"Available aspects: {', '.join(TRAIL_AFFORDANCES)}",
                    metadata={"error": "unknown_aspect"},
                )


# === Factory Functions ===

_node: TrailNode | None = None


def get_trail_node() -> TrailNode:
    """Get the singleton TrailNode."""
    global _node
    if _node is None:
        _node = TrailNode()
    return _node


def set_trail_node(node: TrailNode | None) -> None:
    """Set the singleton TrailNode (for testing)."""
    global _node
    _node = node


__all__ = [
    "TRAIL_AFFORDANCES",
    "TrailNode",
    "get_trail_node",
    "set_trail_node",
    "trail_to_react_flow",
    "analyze_trail_evidence",
]
