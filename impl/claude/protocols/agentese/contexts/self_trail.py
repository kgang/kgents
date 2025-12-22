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
    "load",      # Load trail by ID
    "graph",     # Get trail as react-flow graph data
    "fork",      # Fork a trail
    "create",    # Create a new trail
    "status",    # Trail storage status
)


# === Demo Trail ===

DEMO_TRAIL: dict[str, Any] = {
    "trail_id": "demo",
    "name": "Discovering the Witness Crown Jewel",
    "steps": [
        {
            "index": 0,
            "source_path": "spec/services/witness.md",
            "edge": None,
            "destination_paths": ["spec/services/witness.md"],
            "reasoning": "Beginning exploration at the Witness spec. The proof IS the decision. The mark IS the witness.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:00:00Z",
        },
        {
            "index": 1,
            "source_path": "services/witness/__init__.py",
            "edge": "implements",
            "destination_paths": ["services/witness/__init__.py"],
            "reasoning": "Following the spec to implementation. The Witness Crown Jewel exports: WitnessBus, Mark, FusionMark. These are the core primitives.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:02:15Z",
        },
        {
            "index": 2,
            "source_path": "services/witness/bus.py",
            "edge": "contains",
            "destination_paths": ["services/witness/bus.py"],
            "reasoning": "The WitnessBus is the heart. It's an event bus that records marks - discrete moments of witnessed action. Every action leaves a trace.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:05:30Z",
        },
        {
            "index": 3,
            "source_path": "models/witness.py",
            "edge": "imports",
            "destination_paths": ["models/witness.py"],
            "reasoning": "The Mark model: id, action, reasoning, principles, timestamp. A mark is not just logging - it's JUSTIFIED action. The reasoning field is mandatory.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:08:45Z",
        },
        {
            "index": 4,
            "source_path": "protocols/agentese/contexts/self_trail.py",
            "edge": "semantic:similar_to",
            "destination_paths": ["protocols/agentese/contexts/self_trail.py"],
            "reasoning": "Semantic leap! Trails and Marks are isomorphic - both capture justified exploration. A Trail is a sequence of Marks through conceptual space.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:12:00Z",
        },
        {
            "index": 5,
            "source_path": "spec/protocols/trail-protocol.md",
            "edge": "specifies",
            "destination_paths": ["spec/protocols/trail-protocol.md"],
            "reasoning": "The Trail Protocol spec reveals the deeper pattern: trails are first-class knowledge artifacts. They persist understanding, not just history.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:15:30Z",
        },
        {
            "index": 6,
            "source_path": "services/witness/trail_bridge.py",
            "edge": "implements",
            "destination_paths": ["services/witness/trail_bridge.py"],
            "reasoning": "The bridge! TrailBridge converts trails to marks. Every significant exploration step becomes witnessed evidence. The two systems unify.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:18:45Z",
        },
        {
            "index": 7,
            "source_path": "protocols/trail/storage.py",
            "edge": "contains",
            "destination_paths": ["protocols/trail/storage.py"],
            "reasoning": "TrailStorageAdapter uses Postgres + pgvector. Trails are searchable by semantic similarity. You can find trails that explored similar concepts.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:22:00Z",
        },
        {
            "index": 8,
            "source_path": "spec/principles.md",
            "edge": "semantic:grounds",
            "destination_paths": ["spec/principles.md"],
            "reasoning": "Grounding in first principles. Witness embodies Principle 7: Generative. The proof IS the decision. Marks are compressed understanding.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:25:15Z",
        },
        {
            "index": 9,
            "source_path": "services/fusion/cli.py",
            "edge": "uses",
            "destination_paths": ["services/fusion/cli.py"],
            "reasoning": "Fusion uses Witness! When Kent and Claude reach decisions, FusionMark captures the dialectic: thesis, antithesis, synthesis. Decisions become artifacts.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:28:30Z",
        },
        {
            "index": 10,
            "source_path": "CLAUDE.md",
            "edge": "semantic:encodes",
            "destination_paths": ["CLAUDE.md"],
            "reasoning": "The CLAUDE.md encodes witness philosophy: 'kg decide' captures reasoning traces. Philosophy becomes tooling. The constitution is alive.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:31:45Z",
        },
        {
            "index": 11,
            "source_path": "web/src/pages/Trail.tsx",
            "edge": "projects",
            "destination_paths": ["web/src/pages/Trail.tsx"],
            "reasoning": "Full circle! This very visualization is the projection surface for trails. Bush's Memex realized. The trail becomes visible.",
            "loop_status": "OK",
            "created_at": "2025-12-22T09:35:00Z",
        },
    ],
    "annotations": {
        0: "Entry point - always start with the spec",
        4: "Key insight: structural similarity reveals deeper patterns",
        8: "Grounding moment - connect implementation to philosophy",
        11: "Closure - the visualization visualizes itself",
    },
    "version": 1,
    "created_at": "2025-12-22T09:00:00Z",
    "updated_at": "2025-12-22T09:35:00Z",
    "forked_from_id": None,
    "topics": ["witness", "trail", "crown-jewel", "meta", "philosophy", "visualization"],
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
    edges = {s.get("edge", s.get("edge_type", "")) for s in steps if s.get("edge") or s.get("edge_type")}

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
        observer: "Umwelt[Any, Any] | Observer",
        limit: int = 50,
        response_format: str = "cli",
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
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

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

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

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
                    lines.append(f"      {DIM}{reasoning[:60]}...{RESET}" if len(reasoning) > 60 else f"      {DIM}{reasoning}{RESET}")

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

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

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
                    content=f"{YELLOW}Trail not found: {trail_id}{RESET}" if response_format == "cli" else "",
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

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

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

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        if not name or not name.strip():
            return BasicRendering(
                summary="Trail name is required",
                content=f"{YELLOW}Error: Trail name is required{RESET}" if response_format == "cli" else "",
                metadata={"error": "name_required"},
            )

        if not steps or len(steps) == 0:
            return BasicRendering(
                summary="At least one step is required",
                content=f"{YELLOW}Error: At least one step is required{RESET}" if response_format == "cli" else "",
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
                        content=f"{YELLOW}Error: Step {i + 1} missing path{RESET}" if response_format == "cli" else "",
                        metadata={"error": "step_missing_path", "step_index": i},
                    )

                # Validate parent_index for branching trails
                parent_idx = step.get("parent_index")
                if parent_idx is not None:
                    if not isinstance(parent_idx, int) or parent_idx < 0 or parent_idx >= i:
                        return BasicRendering(
                            summary=f"Invalid parent_index at step {i + 1}",
                            content=f"{YELLOW}Error: parent_index {parent_idx} invalid at step {i + 1} (must be 0..{i-1}){RESET}" if response_format == "cli" else "",
                            metadata={"error": "invalid_parent_index", "step_index": i, "parent_index": parent_idx},
                        )

                validated_steps.append({
                    "index": i,
                    "parent_index": parent_idx,  # For branching trails
                    "source_path": step_path,
                    "edge": step.get("edge") if i > 0 else None,  # First step has no edge
                    "destination_paths": [step_path],
                    "reasoning": step.get("reasoning", ""),
                    "loop_status": "OK",
                    "created_at": datetime.utcnow().isoformat() + "Z",
                })

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
                limit = kwargs.get("limit", 50)
                return await self.manifest(observer, limit, response_format)
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
