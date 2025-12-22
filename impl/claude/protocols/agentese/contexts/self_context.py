"""
AGENTESE Typed-Hypergraph Context.

self.context.* paths for navigating the typed-hypergraph.

The typed-hypergraph is kgents' model for agent context:
- Nodes are holons (files, functions, claims, evidence, concepts)
- Hyperedges are AGENTESE aspects that connect one node to *many* nodes
- Traversal is lazy and observer-dependent
- Trails persist navigation history as replayable, shareable artifacts

AGENTESE Principle: "The lens was a lie. There is only the link."

Spec: spec/protocols/typed-hypergraph.md

Teaching:
    gotcha: ContextNode content is lazy-loaded. Call await node.content() only when
            you need the actual content—this respects the Minimal Output Principle.
            (Evidence: test_self_context.py::test_lazy_content_loading)

    gotcha: Different observers see different hyperedges from the same node.
            This is the Umwelt principle: "what exists depends on who's looking."
            (Evidence: test_self_context.py::test_observer_dependent_edges)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Core Data Structures ===


@dataclass(frozen=True)
class TrailStep:
    """
    A single step in a navigation trail.

    Records what node was visited and which hyperedge was followed.

    Teaching:
        gotcha: TrailStep is frozen (immutable). Trails are append-only structures.
                To modify, create a new trail with additional steps.
                (Evidence: test_self_context.py::test_trail_immutability)
    """

    node_path: str  # The node visited
    edge_type: str | None  # The hyperedge followed to get here (None for start)
    timestamp: datetime = field(default_factory=datetime.now)
    annotations: str = ""  # Optional annotation at this step


@dataclass(eq=False)
class ContextNode:
    """
    A node in the typed-hypergraph.

    The atomic unit of navigation. Each node represents a holon (file, function,
    claim, evidence, concept) that can be connected to other nodes via hyperedges.

    AGENTESE paths ARE nodes:
        world.auth_middleware → ContextNode(path="world.auth_middleware")

    Teaching:
        gotcha: content is lazy-loaded via async content() method. The _content
                field is private and should not be accessed directly.
                (Evidence: test_self_context.py::test_lazy_content_loading)

        gotcha: edges() returns observer-dependent hyperedges. A developer sees
                different edges than a security auditor.
                (Evidence: test_self_context.py::test_observer_dependent_edges)
    """

    path: str  # AGENTESE path (e.g., "world.auth_middleware")
    holon: str  # Entity name (e.g., "auth_middleware")
    _content: str | None = field(default=None, repr=False)
    _content_loaded: bool = field(default=False, repr=False)

    # Cached edges (populated on first edges() call)
    _edges_cache: dict[str, list["ContextNode"]] | None = field(
        default=None, repr=False
    )

    def __hash__(self) -> int:
        """Hash by path for set membership."""
        return hash(self.path)

    def __eq__(self, other: object) -> bool:
        """Two nodes are equal if they have the same path."""
        if not isinstance(other, ContextNode):
            return NotImplemented
        return self.path == other.path

    def edges(self, observer: Observer) -> dict[str, list["ContextNode"]]:
        """
        Available hyperedges from this node.

        Observer-dependent: different observers see different edges.
        Returns: {edge_type: [destination_nodes]}

        The edge types returned depend on observer archetype:
        - developer: tests, imports, calls, implements
        - security_auditor: auth_flows, data_flows, vulnerabilities, evidence
        - architect: dependencies, dependents, patterns, violations
        - newcomer: docs, examples, related
        """
        # Use cached edges if available (for same observer)
        # Note: In production, we'd cache per-observer
        if self._edges_cache is not None:
            return self._edges_cache

        # Compute edges based on observer archetype
        edges = self._compute_edges_for_observer(observer)
        object.__setattr__(self, "_edges_cache", edges)
        return edges

    def _compute_edges_for_observer(
        self, observer: Observer
    ) -> dict[str, list["ContextNode"]]:
        """
        Compute hyperedges for a specific observer.

        This is where the Umwelt principle is implemented:
        what exists depends on who's looking.
        """
        # Standard edges available to all observers
        edges: dict[str, list[ContextNode]] = {
            "contains": [],  # Children
            "parent": [],  # Parent node
        }

        match observer.archetype:
            case "developer" | "test":
                # Developers see code relationships
                edges.update(
                    {
                        "tests": [],  # Test files
                        "imports": [],  # Dependencies
                        "calls": [],  # Functions called
                        "implements": [],  # Specs implemented
                    }
                )
            case "security_auditor":
                edges.update(
                    {
                        "auth_flows": [],
                        "data_flows": [],
                        "vulnerabilities": [],
                        "evidence": [],
                    }
                )
            case "architect":
                edges.update(
                    {
                        "dependencies": [],
                        "dependents": [],
                        "patterns": [],
                        "violations": [],
                    }
                )
            case "newcomer" | "guest":
                edges.update(
                    {
                        "docs": [],
                        "examples": [],
                        "related": [],
                    }
                )
            case _:
                # Default: minimal edges
                edges.update({"related": []})

        return edges

    async def content(self) -> str:
        """
        Load content only when needed (lazy loading).

        The Minimal Output Principle: return a handle, not a haystack.
        """
        if self._content_loaded:
            return self._content or ""

        # Try to load content based on path type
        loaded = await self._load_content()
        object.__setattr__(self, "_content", loaded)
        object.__setattr__(self, "_content_loaded", True)
        return loaded

    async def _load_content(self) -> str:
        """
        Load content for this node based on its path.

        Different node types have different content sources:
        - world.* → file content
        - concept.* → definition
        - self.* → state representation
        """
        # For file-based nodes, try to load from filesystem
        if self.path.startswith("world."):
            # Try to resolve to a file path
            # This is a simplified implementation
            return f"[Content for {self.path}]"

        return f"[{self.holon}]"

    async def follow(
        self, edge_type: str, observer: Observer
    ) -> list["ContextNode"]:
        """
        Traverse a hyperedge using resolvers.

        Equivalent to: logos(f"{self.path}.{edge_type}", observer)

        The Umwelt principle: different observers see different edges.
        If the observer can't see this edge type, returns empty list.

        Teaching:
            gotcha: follow() respects observer visibility BEFORE calling resolvers.
                    This prevents information leakage—guest can't discover tests
                    just by asking for them.
                    (Evidence: test_self_context.py::test_observer_filters_edges)
        """
        # Check if observer can see this edge type (Umwelt principle)
        visible_edges = self.edges(observer)
        if edge_type not in visible_edges:
            return []  # Observer can't see this edge

        # Import here to avoid circular dependency
        from .hyperedge_resolvers import resolve_hyperedge, _get_project_root

        # Invoke the resolver
        root = _get_project_root()
        return await resolve_hyperedge(self, edge_type, root)


@dataclass
class Trail:
    """
    Replayable path through the hypergraph.

    Inspired by Vannevar Bush's Memex trails.

    A trail records the sequence of navigation steps taken through
    the typed-hypergraph, enabling:
    - Replay: Re-traverse the same path
    - Sharing: Share exploration with others
    - Evidence: Trail as proof of investigation

    Teaching:
        gotcha: Trail is mutable (steps can be appended). But TrailSteps are
                immutable. This allows building trails incrementally while
                preserving step integrity.
                (Evidence: test_self_context.py::test_trail_append)
    """

    id: str
    name: str
    created_by: Observer
    steps: list[TrailStep] = field(default_factory=list)
    annotations: dict[int, str] = field(default_factory=dict)  # step_index → annotation
    created_at: datetime = field(default_factory=datetime.now)

    async def replay(self, observer: Observer) -> "ContextGraph":
        """Replay this trail, ending at final position."""
        # Start with empty graph
        focus: set[ContextNode] = set()

        # Replay each step
        for step in self.steps:
            node = ContextNode(
                path=step.node_path,
                holon=step.node_path.split(".")[-1],
            )
            focus = {node}

        return ContextGraph(
            focus=focus,
            trail=self.steps.copy(),
            observer=observer,
        )

    def annotate(self, step_index: int, text: str) -> "Trail":
        """Add annotation at a step."""
        self.annotations[step_index] = text
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_by": self.created_by.archetype,
            "steps": [
                {
                    "node_path": s.node_path,
                    "edge_type": s.edge_type,
                    "timestamp": s.timestamp.isoformat(),
                    "annotations": s.annotations,
                }
                for s in self.steps
            ],
            "annotations": self.annotations,
            "created_at": self.created_at.isoformat(),
        }

    def as_outline(self) -> str:
        """
        Render trail as a readable outline (§10.1).

        The trail becomes a document that can be shared, annotated,
        and used as evidence for claims.

        Returns:
            Formatted outline text with trail steps and annotations

        Example output:
            📍 Trail: "Auth Bug Investigation"
               Created by: Kent + Claude
               Steps: 7

               1. Started at auth_middleware.py
               2. Expanded [tests] → found 3 test files
               3. 💭 "Bug is here—< instead of <="
        """
        lines = [f"📍 Trail: \"{self.name}\""]
        lines.append(f"   Created by: {self.created_by.archetype}")
        lines.append(f"   Created at: {self.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"   Steps: {len(self.steps)}")
        lines.append("")

        for i, step in enumerate(self.steps):
            # Step number and node
            step_num = i + 1

            if step.edge_type:
                # Navigation step
                lines.append(f"   {step_num}. ──[{step.edge_type}]──→ {step.node_path}")
            else:
                # Start or focus step
                lines.append(f"   {step_num}. Started at {step.node_path}")

            # Inline annotation from step
            if step.annotations:
                lines.append(f"      💭 \"{step.annotations}\"")

            # Trail-level annotation for this step
            if i in self.annotations:
                lines.append(f"      📝 {self.annotations[i]}")

        return "\n".join(lines)

    def share(self) -> dict[str, Any]:
        """
        Export trail as shareable artifact (§10.1).

        Returns a complete, self-contained representation that can be:
        - Saved to file
        - Sent to another agent
        - Used as evidence in ASHC

        Includes metadata for replay and verification.

        Returns:
            Complete shareable dictionary with version and checksums
        """
        import hashlib
        import json

        # Build base data
        data = self.to_dict()

        # Add sharing metadata
        data["version"] = "1.0"
        data["format"] = "kgents.trail.v1"

        # Add step count for quick validation
        data["step_count"] = len(self.steps)

        # Compute content hash for integrity verification
        # Hash the steps content (not timestamps, for stability)
        step_content = json.dumps(
            [{"path": s.node_path, "edge": s.edge_type} for s in self.steps],
            sort_keys=True,
        )
        data["content_hash"] = hashlib.sha256(step_content.encode()).hexdigest()[:16]

        # Add evidence metadata
        data["evidence"] = {
            "type": "exploration_trail",
            "strength": self._compute_evidence_strength(),
            "verifiable": True,
        }

        return data

    def _compute_evidence_strength(self) -> str:
        """
        Compute evidence strength based on trail characteristics.

        From spec §10.2: Evidence strength computed from trail diversity.

        Returns:
            "weak" | "moderate" | "strong" | "definitive"
        """
        step_count = len(self.steps)
        annotation_count = len(self.annotations) + sum(
            1 for s in self.steps if s.annotations
        )
        unique_paths = len({s.node_path for s in self.steps})
        unique_edges = len({s.edge_type for s in self.steps if s.edge_type})

        # Scoring heuristic
        score = 0

        # Steps contribute
        if step_count >= 3:
            score += 1
        if step_count >= 7:
            score += 1

        # Annotations show intentionality
        if annotation_count >= 1:
            score += 1
        if annotation_count >= 3:
            score += 1

        # Diversity shows thorough exploration
        if unique_paths >= 3:
            score += 1
        if unique_edges >= 2:
            score += 1

        # Map score to strength
        if score >= 5:
            return "definitive"
        elif score >= 3:
            return "strong"
        elif score >= 1:
            return "moderate"
        else:
            return "weak"

    @classmethod
    def from_dict(cls, data: dict[str, Any], observer: "Observer | None" = None) -> "Trail":
        """
        Reconstruct trail from shared dictionary.

        Used to load saved trails or receive shared trails from other agents.

        Args:
            data: Dictionary from share() or to_dict()
            observer: Observer to use (defaults to generic if not provided)

        Returns:
            Reconstructed Trail instance
        """
        from ..node import Observer

        # Parse observer
        if observer is None:
            observer = Observer(archetype=data.get("created_by", "guest"))

        # Parse steps
        steps = [
            TrailStep(
                node_path=s["node_path"],
                edge_type=s.get("edge_type"),
                timestamp=datetime.fromisoformat(s["timestamp"]),
                annotations=s.get("annotations", ""),
            )
            for s in data.get("steps", [])
        ]

        # Parse annotations
        annotations = {
            int(k): v for k, v in data.get("annotations", {}).items()
        }

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Imported Trail"),
            created_by=observer,
            steps=steps,
            annotations=annotations,
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(),
        )


@dataclass
class ContextGraph:
    """
    The navigable typed-hypergraph.

    Not a pre-loaded structure—a navigation protocol.

    The ContextGraph maintains:
    - focus: Current position(s) in the graph (can be multiple nodes)
    - trail: Navigation history (how we got here)
    - observer: Determines edge visibility (Umwelt principle)

    Teaching:
        gotcha: focus is a SET of nodes. Following a hyperedge from multiple
                focused nodes returns the union of all destinations.
                (Evidence: test_self_context.py::test_multi_focus_navigation)

        gotcha: navigate() returns a NEW ContextGraph. The original is unchanged.
                This enables backtracking and branching exploration.
                (Evidence: test_self_context.py::test_navigate_immutability)
    """

    focus: set[ContextNode]  # Current position(s)
    trail: list[TrailStep]  # Navigation history
    observer: Observer  # Determines edge visibility

    async def navigate(self, edge_type: str) -> "ContextGraph":
        """
        Follow a hyperedge from all focused nodes.

        Returns a new ContextGraph with updated focus and trail.
        """
        # Collect all destinations from all focused nodes
        new_focus: set[ContextNode] = set()
        for node in self.focus:
            destinations = await node.follow(edge_type, self.observer)
            new_focus.update(destinations)

        # Record the navigation in trail
        new_trail = self.trail.copy()
        for node in self.focus:
            new_trail.append(
                TrailStep(
                    node_path=node.path,
                    edge_type=edge_type,
                )
            )

        return ContextGraph(
            focus=new_focus,
            trail=new_trail,
            observer=self.observer,
        )

    async def affordances(self, resolve: bool = True) -> dict[str, int]:
        """
        What hyperedges can we follow?

        Returns {edge_type: destination_count} aggregated across all focused nodes.

        Args:
            resolve: If True, actually resolve edges to get real counts.
                     If False, just return available edge types with 0 counts (faster).

        Teaching:
            gotcha: With resolve=True (default), this calls hyperedge resolvers
                    which may read files. For large focus sets, consider resolve=False.
                    (Evidence: test_self_context.py::test_affordances_with_resolution)
        """
        result: dict[str, int] = {}

        for node in self.focus:
            # Get visible edge types for this observer
            visible_edges = node.edges(self.observer)

            if resolve:
                # Actually resolve each edge to get real counts
                for edge_type in visible_edges:
                    destinations = await node.follow(edge_type, self.observer)
                    result[edge_type] = result.get(edge_type, 0) + len(destinations)
            else:
                # Just mark edge types as available (fast path)
                for edge_type in visible_edges:
                    result[edge_type] = result.get(edge_type, 0)

        return result

    def backtrack(self) -> "ContextGraph":
        """Go back along the trail."""
        if not self.trail:
            return self

        # Get the previous step
        prev_trail = self.trail[:-1]

        # Reconstruct focus from previous position
        if prev_trail:
            last_step = prev_trail[-1]
            prev_node = ContextNode(
                path=last_step.node_path,
                holon=last_step.node_path.split(".")[-1],
            )
            prev_focus = {prev_node}
        else:
            prev_focus = set()

        return ContextGraph(
            focus=prev_focus,
            trail=prev_trail,
            observer=self.observer,
        )

    def to_trail(self) -> Trail:
        """Convert current navigation to a Trail object."""
        import uuid

        return Trail(
            id=str(uuid.uuid4()),
            name="Exploration",
            created_by=self.observer,
            steps=self.trail.copy(),
        )


# === Standard Hyperedge Types ===

# Structural hyperedges
STRUCTURAL_EDGES = frozenset(
    {
        "contains",  # Submodules/children
        "parent",  # Parent module
        "imports",  # Dependencies
        "calls",  # Functions called
    }
)

# Testing hyperedges
TESTING_EDGES = frozenset(
    {
        "tests",  # Test files
        "covers",  # Code paths covered
    }
)

# Specification hyperedges
SPEC_EDGES = frozenset(
    {
        "implements",  # Specs implemented
        "derives_from",  # Parent specs
    }
)

# Evidence hyperedges (ASHC integration)
EVIDENCE_EDGES = frozenset(
    {
        "evidence",  # Supporting evidence
        "supports",  # Claims supported
        "refutes",  # Claims contradicted
    }
)

# Temporal hyperedges
TEMPORAL_EDGES = frozenset(
    {
        "evolved_from",  # Previous version
        "supersedes",  # What this replaces
    }
)

# Semantic hyperedges
SEMANTIC_EDGES = frozenset(
    {
        "related",  # Loose semantic similarity
        "similar",  # High embedding similarity
        "contrasts",  # Semantic opposition
    }
)

# All standard edges
ALL_STANDARD_EDGES = (
    STRUCTURAL_EDGES
    | TESTING_EDGES
    | SPEC_EDGES
    | EVIDENCE_EDGES
    | TEMPORAL_EDGES
    | SEMANTIC_EDGES
)

# Reverse edge mapping (bidirectional consistency)
# Law 10.2: A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A
# Every edge has BOTH directions mapped
REVERSE_EDGES: dict[str, str] = {
    # Structural
    "contains": "contained_in",
    "contained_in": "contains",
    "parent": "children",
    "children": "parent",
    "imports": "imported_by",
    "imported_by": "imports",
    "calls": "called_by",
    "called_by": "calls",
    # Testing
    "tests": "tested_by",
    "tested_by": "tests",
    "covers": "covered_by",
    "covered_by": "covers",
    # Specification
    "implements": "implemented_by",
    "implemented_by": "implements",
    "derives_from": "derived_by",
    "derived_by": "derives_from",
    # Evidence
    "evidence": "evidences",
    "evidences": "evidence",
    "supports": "supported_by",
    "supported_by": "supports",
    "refutes": "refuted_by",
    "refuted_by": "refutes",
    # Temporal
    "evolved_from": "evolved_to",
    "evolved_to": "evolved_from",
    "supersedes": "superseded_by",
    "superseded_by": "supersedes",
}


def get_reverse_edge(edge_type: str) -> str | None:
    """
    Get the reverse edge type for bidirectional navigation.

    Law 10.2: A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A
    """
    return REVERSE_EDGES.get(edge_type)


# === AGENTESE Affordances ===

CONTEXT_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Current focus, trail length, affordances
    "navigate",  # Follow a hyperedge
    "focus",  # Jump to a specific node
    "backtrack",  # Go back one step
    "trail",  # Get current trail
    "subgraph",  # Extract reachable subgraph
    # Phase 2: Context Perception integration
    "outline",  # Render as editable outline
    "copy",  # Copy with provenance (Law 11.3)
    "paste",  # Paste with link creation (Law 11.4)
    "lens",  # Create semantic lens into file
    # Phase 4: Witness integration
    "emit_trail",  # Convert trail to Witness mark
)


# === AGENTESE Node ===


@node(
    "self.context",
    description="Typed-hypergraph navigation for agent context",
)
@dataclass
class ContextNavNode(BaseLogosNode):
    """
    self.context - Navigate the typed-hypergraph.

    The typed-hypergraph is kgents' model for agent context:
    - AGENTESE aspects ARE hyperedge types
    - Navigation is lazy and observer-dependent
    - Trails persist as replayable evidence

    Phase 2 additions (Context Perception integration):
    - outline: Render as editable outline
    - copy: Copy with provenance (Law 11.3)
    - paste: Paste with link creation (Law 11.4)
    - lens: Create semantic lens into file

    Usage:
        kg context manifest        # Where am I?
        kg context navigate tests  # Follow [tests] hyperedge
        kg context backtrack       # Go back
        kg context trail save "investigation"  # Save trail
        kg context outline         # Render as outline
        kg context lens <file> <focus>  # Create semantic lens
    """

    _handle: str = "self.context"

    # Current graph state (session-scoped)
    _graph: ContextGraph | None = field(default=None, repr=False)

    # Portal bridge for Context Perception integration (Phase 2)
    _portal_bridge: Any = field(default=None, repr=False)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return CONTEXT_AFFORDANCES

    def _ensure_graph(self, observer: Observer) -> ContextGraph:
        """Ensure we have an initialized graph."""
        if self._graph is None:
            self._graph = ContextGraph(
                focus=set(),
                trail=[],
                observer=observer,
            )
        return self._graph

    @property
    def _current_trail(self) -> Trail | None:
        """
        Get the current trail as a Trail object.

        Used by CLI handlers for trail save/load/share/witness commands.
        Returns None if no graph or no trail steps.
        """
        if self._graph is None:
            return None
        return self._graph.to_trail()

    @_current_trail.setter
    def _current_trail(self, trail: Trail | None) -> None:
        """
        Set the current trail (e.g., when loading from file).

        Replaces the graph's trail with the loaded trail steps.
        """
        if trail is not None and self._graph is not None:
            self._graph.trail = list(trail.steps)

    async def _maybe_auto_witness(self, graph: "ContextGraph") -> None:
        """
        Auto-emit trail as witness mark when threshold is met.

        Phase 5B: Trail → Witness integration.

        Thresholds (from plan):
        - Trail has 5+ steps, OR
        - Trail has 2+ annotations

        Only emits once per threshold crossing (tracks last witnessed count).
        """
        trail = graph.to_trail()
        step_count = len(trail.steps)
        annotation_count = sum(1 for s in trail.steps if s.annotations) + len(trail.annotations)

        # Check if threshold is newly crossed
        # (we haven't witnessed this step count or higher)
        threshold_met = step_count >= 5 or annotation_count >= 2
        already_witnessed = step_count <= getattr(self, "_last_witnessed_step_count", 0)

        if threshold_met and not already_witnessed:
            try:
                from services.witness.trail_bridge import emit_trail_as_mark

                await emit_trail_as_mark(trail)

                # Update last witnessed count
                object.__setattr__(self, "_last_witnessed_step_count", step_count)

                # Log for debugging (not visible to user)
                import logging
                logging.getLogger(__name__).debug(
                    f"Auto-witnessed trail: {step_count} steps, {annotation_count} annotations"
                )
            except Exception:
                # Don't break navigation if witnessing fails
                pass

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current position in the typed-hypergraph",
    )
    async def manifest(self, observer: "Umwelt[Any, Any] | Observer") -> Renderable:
        """Collapse to observer-appropriate representation."""
        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        # Get affordances (available hyperedges)
        affordances = await graph.affordances()

        return BasicRendering(
            summary="Typed-Hypergraph Context",
            content=self._format_manifest(graph, affordances),
            metadata={
                "focus": [n.path for n in graph.focus],
                "trail_length": len(graph.trail),
                "affordances": affordances,
                "observer": obs.archetype,
                "route": "/context",
            },
        )

    def _format_manifest(
        self, graph: ContextGraph, affordances: dict[str, int]
    ) -> str:
        """Format the manifest content with ANSI colors for CLI."""
        # ANSI color codes
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        RESET = "\033[0m"

        lines = [f"{BOLD}📍 Current Context{RESET}\n"]

        # Focus - the current position(s)
        if graph.focus:
            lines.append(f"{BOLD}Focus:{RESET}")
            for node in sorted(graph.focus, key=lambda n: n.path):
                lines.append(f"  {CYAN}●{RESET} {node.path}")
            lines.append("")
        else:
            lines.append(f"{BOLD}Focus:{RESET} {DIM}(none - use 'focus <path>' to start){RESET}\n")
            lines.append(f"{DIM}Try: kg context focus brain{RESET}")
            lines.append(f"{DIM}     kg context focus agentese.parser{RESET}\n")

        # Affordances - available hyperedges to follow
        if affordances:
            # Split into edges with destinations vs empty
            active_edges = {k: v for k, v in affordances.items() if v > 0}
            empty_edges = {k: v for k, v in affordances.items() if v == 0}

            if active_edges:
                lines.append(f"{BOLD}Navigate via:{RESET}")
                for edge_type, count in sorted(active_edges.items(), key=lambda x: -x[1]):
                    lines.append(f"  {GREEN}▶{RESET} {edge_type} {DIM}→ {count} node{'s' if count != 1 else ''}{RESET}")
                lines.append("")

            if empty_edges:
                lines.append(f"{DIM}Also available (0 results):{RESET}")
                edge_list = ", ".join(sorted(empty_edges.keys()))
                lines.append(f"  {DIM}{edge_list}{RESET}")
                lines.append("")
        else:
            if graph.focus:
                lines.append(f"{DIM}No hyperedges available from current focus.{RESET}\n")

        # Trail - navigation history
        if graph.trail:
            lines.append(f"{BOLD}Trail:{RESET} {DIM}({len(graph.trail)} step{'s' if len(graph.trail) != 1 else ''}){RESET}")
            # Show last 5 steps
            start = max(0, len(graph.trail) - 5)
            for i, step in enumerate(graph.trail[start:], start=start):
                if step.edge_type:
                    lines.append(f"  {DIM}{i}.{RESET} {step.node_path} {YELLOW}─[{step.edge_type}]→{RESET}")
                else:
                    lines.append(f"  {DIM}{i}.{RESET} {step.node_path} {MAGENTA}(start){RESET}")
            if start > 0:
                lines.append(f"  {DIM}... {start} earlier steps{RESET}")
            lines.append("")

        # Quick commands
        lines.append(f"{DIM}Commands: navigate <edge> | backtrack | trail | subgraph{RESET}")

        return "\n".join(lines)

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("graph_state")],
        help="Follow a hyperedge from current focus",
    )
    async def navigate(
        self, observer: "Umwelt[Any, Any] | Observer", edge_type: str
    ) -> Renderable:
        """Follow a hyperedge from all focused nodes."""
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        if not graph.focus:
            return BasicRendering(
                summary="No focus set",
                content=f"{DIM}Set a focus first: kg context focus <path>{RESET}",
                metadata={"error": "no_focus"},
            )

        # Navigate
        new_graph = await graph.navigate(edge_type)
        self._graph = new_graph

        # Phase 5B: Auto-emit trail as witness mark when threshold met
        await self._maybe_auto_witness(new_graph)

        # Format result
        if new_graph.focus:
            lines = [f"{BOLD}Navigated via [{edge_type}]{RESET}\n"]
            lines.append(f"{BOLD}Now at:{RESET}")
            for node in sorted(new_graph.focus, key=lambda n: n.path):
                lines.append(f"  {CYAN}●{RESET} {node.path}")
            content = "\n".join(lines)
        else:
            content = f"{YELLOW}No destinations found via [{edge_type}]{RESET}"

        return BasicRendering(
            summary=f"Navigated via [{edge_type}]",
            content=content,
            metadata={
                "edge_type": edge_type,
                "new_focus": [n.path for n in new_graph.focus],
                "trail_length": len(new_graph.trail),
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("graph_state")],
        help="Jump to a specific node in the hypergraph",
    )
    async def focus(
        self, observer: "Umwelt[Any, Any] | Observer", path: str
    ) -> Renderable:
        """Jump to a specific node."""
        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )

        # Create node from path
        holon = path.split(".")[-1]
        node = ContextNode(path=path, holon=holon)

        # Update graph with new focus
        self._graph = ContextGraph(
            focus={node},
            trail=[TrailStep(node_path=path, edge_type=None)],
            observer=obs,
        )

        return BasicRendering(
            summary=f"Focused on {path}",
            content=f"Now focused on: {path}",
            metadata={
                "path": path,
                "holon": holon,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("graph_state")],
        help="Go back one step in the trail",
    )
    async def backtrack(
        self, observer: "Umwelt[Any, Any] | Observer"
    ) -> Renderable:
        """Go back along the trail."""
        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        if not graph.trail:
            return BasicRendering(
                summary="Cannot backtrack",
                content="Trail is empty - nowhere to go back to",
                metadata={"error": "empty_trail"},
            )

        # Backtrack
        new_graph = graph.backtrack()
        self._graph = new_graph

        return BasicRendering(
            summary="Backtracked",
            content=f"Returned to previous position (trail: {len(new_graph.trail)} steps)",
            metadata={
                "new_focus": [n.path for n in new_graph.focus],
                "trail_length": len(new_graph.trail),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Get the current navigation trail",
    )
    async def trail(
        self, observer: "Umwelt[Any, Any] | Observer"
    ) -> Renderable:
        """Get current trail."""
        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        trail_obj = graph.to_trail()

        return BasicRendering(
            summary=f"Trail: {len(trail_obj.steps)} steps",
            content=self._format_trail(trail_obj),
            metadata={
                "trail": trail_obj.to_dict(),
            },
        )

    def _format_trail(self, trail: Trail) -> str:
        """Format trail for display."""
        lines = [f"# Trail: {trail.name}\n"]
        lines.append(f"Created by: {trail.created_by.archetype}")
        lines.append(f"Created at: {trail.created_at.isoformat()}")
        lines.append(f"Steps: {len(trail.steps)}\n")

        for i, step in enumerate(trail.steps):
            edge_str = f" ──[{step.edge_type}]──→" if step.edge_type else " (start)"
            lines.append(f"{i + 1}. {step.node_path}{edge_str}")
            if step.annotations:
                lines.append(f"   📝 {step.annotations}")

        return "\n".join(lines)

    @aspect(
        category=AspectCategory.COMPOSITION,
        effects=[],
        help="Extract reachable subgraph from current focus",
    )
    async def subgraph(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        max_depth: int = 3,
    ) -> Renderable:
        """Extract reachable subgraph from current focus."""
        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        # BFS to find reachable nodes
        visited: set[str] = set()
        edges_found: list[tuple[str, str, str]] = []  # (source, edge, dest)

        to_visit = [(n, 0) for n in graph.focus]

        while to_visit:
            node, depth = to_visit.pop(0)
            if node.path in visited or depth >= max_depth:
                continue

            visited.add(node.path)
            edges = node.edges(obs)

            for edge_type, destinations in edges.items():
                for dest in destinations:
                    edges_found.append((node.path, edge_type, dest.path))
                    if dest.path not in visited:
                        to_visit.append((dest, depth + 1))

        return BasicRendering(
            summary=f"Subgraph: {len(visited)} nodes, {len(edges_found)} edges",
            content=self._format_subgraph(visited, edges_found),
            metadata={
                "nodes": list(visited),
                "edges": edges_found,
                "max_depth": max_depth,
            },
        )

    def _format_subgraph(
        self, nodes: set[str], edges: list[tuple[str, str, str]]
    ) -> str:
        """Format subgraph for display."""
        lines = ["# Reachable Subgraph\n"]
        lines.append(f"Nodes: {len(nodes)}")
        lines.append(f"Edges: {len(edges)}\n")

        lines.append("## Nodes")
        for node in sorted(nodes):
            lines.append(f"  - {node}")

        if edges:
            lines.append("\n## Edges")
            for src, edge, dest in edges[:20]:  # Limit display
                lines.append(f"  {src} ──[{edge}]──→ {dest}")
            if len(edges) > 20:
                lines.append(f"  ... and {len(edges) - 20} more")

        return "\n".join(lines)

    # === Phase 2: Context Perception Integration ===

    def _ensure_portal_bridge(self, observer: Observer) -> Any:
        """
        Ensure we have an initialized portal bridge.

        The portal bridge connects the typed-hypergraph (ContextGraph)
        to the Context Perception layer (Outline model).
        """
        if self._portal_bridge is None:
            try:
                from protocols.context.portal_bridge import (
                    OutlinePortalBridge,
                    create_bridge,
                )
                self._portal_bridge = create_bridge(
                    observer_id=observer.archetype,
                )
            except ImportError:
                # Context Perception not available
                pass
        return self._portal_bridge

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Render current context as editable outline",
    )
    async def outline(
        self, observer: "Umwelt[Any, Any] | Observer"
    ) -> Renderable:
        """
        Render current context as an editable outline.

        The outline is the shared workspace for human+agent collaboration.
        It projects the typed-hypergraph into text.

        Spec: spec/protocols/context-perception.md §4
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        bridge = self._ensure_portal_bridge(obs)

        if bridge is None:
            return BasicRendering(
                summary="Outline (unavailable)",
                content=f"{DIM}Context Perception not available{RESET}",
                metadata={"error": "context_perception_unavailable"},
            )

        # Format outline for display
        outline = bridge.outline
        lines = [f"{BOLD}📄 Outline{RESET}\n"]

        # Render the outline tree
        def render_node(node: Any, depth: int = 0) -> None:
            indent = "  " * depth
            if node.snippet:
                lines.append(f"{indent}{node.snippet.visible_text}")
            elif node.portal:
                icon = "▼" if node.portal.expanded else "▶"
                lines.append(
                    f"{indent}{icon} [{node.portal.edge_type}] → "
                    f"{node.portal.summary}"
                )
            for child in node.children:
                render_node(child, depth + 1)

        render_node(outline.root)

        # Trail info
        if outline.trail_steps:
            lines.append(f"\n{DIM}Trail: {len(outline.trail_steps)} steps{RESET}")

        # Budget info
        if outline.is_budget_low:
            lines.append(f"\n{CYAN}⚠ Budget low: {outline.budget_remaining:.0%}{RESET}")

        return BasicRendering(
            summary=f"Outline ({len(outline.trail_steps)} steps)",
            content="\n".join(lines),
            metadata={
                "trail_steps": len(outline.trail_steps),
                "budget_remaining": outline.budget_remaining,
                "route": "/context/outline",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Copy text with provenance metadata (Law 11.3)",
    )
    async def copy(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        node_path: str,
        start_line: int = 0,
        start_col: int = 0,
        end_line: int = 0,
        end_col: int = 0,
    ) -> Renderable:
        """
        Copy text with invisible provenance metadata.

        Law 11.3: paste(copy(snippet)).source ≡ snippet.path

        The copied text carries invisible metadata:
        - source_path: Where it came from
        - copied_at: Timestamp
        - copied_by: Observer who copied

        Args:
            node_path: Path to the node to copy from
            start_line, start_col: Start of selection
            end_line, end_col: End of selection
        """
        DIM = "\033[2m"
        GREEN = "\033[32m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        bridge = self._ensure_portal_bridge(obs)

        if bridge is None:
            return BasicRendering(
                summary="Copy failed",
                content=f"{DIM}Context Perception not available{RESET}",
                metadata={"error": "context_perception_unavailable"},
            )

        try:
            from protocols.context.outline import Range

            selection = Range(
                start_line=start_line,
                start_col=start_col,
                end_line=end_line if end_line > 0 else start_line,
                end_col=end_col if end_col > 0 else start_col,
            )

            clipboard = await bridge._operations.copy(node_path, selection)

            return BasicRendering(
                summary=f"Copied from {node_path}",
                content=f"{GREEN}✓ Copied{RESET}\n\n"
                f"{DIM}Source: {clipboard.source_path}{RESET}\n"
                f"{DIM}Text: {clipboard.visible_text[:100]}...{RESET}",
                metadata={
                    "source_path": clipboard.source_path,
                    "copied_at": clipboard.copied_at.isoformat(),
                    "visible_text": clipboard.visible_text,
                },
            )
        except Exception as e:
            return BasicRendering(
                summary="Copy failed",
                content=f"Error: {e}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("outline_state")],
        help="Paste with bidirectional link creation (Law 11.4)",
    )
    async def paste(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        target_path: str,
        line: int = 0,
        col: int = 0,
    ) -> Renderable:
        """
        Paste with automatic link creation.

        Law 11.4: link(A, B) ⟹ ∃ reverse_link(B, A)

        When pasting content with provenance:
        - Creates link back to source
        - Records paste as evidence

        Args:
            target_path: Path to paste into
            line, col: Position within the node
        """
        DIM = "\033[2m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        bridge = self._ensure_portal_bridge(obs)

        if bridge is None:
            return BasicRendering(
                summary="Paste failed",
                content=f"{DIM}Context Perception not available{RESET}",
                metadata={"error": "context_perception_unavailable"},
            )

        # Note: In a real implementation, we'd retrieve the clipboard
        # For now, return a placeholder
        return BasicRendering(
            summary="Paste (no clipboard)",
            content=f"{YELLOW}No clipboard content available{RESET}\n\n"
            f"{DIM}Use 'copy' first to copy text with provenance.{RESET}",
            metadata={
                "target_path": target_path,
                "note": "Clipboard state not persisted between calls",
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Create semantic lens into a file",
    )
    async def file_lens(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        file_path: str,
        focus: str = "",
    ) -> Renderable:
        """
        Create a bidirectional lens into a file.

        Returns semantic names instead of line numbers:
        - auth_core:validate_token (not monolith.py:847-920)

        Args:
            file_path: Path to the file
            focus: Focus specifier:
                   - "function_name" → lens on function
                   - "class:ClassName" → lens on class
                   - "lines:start-end" → lens on line range

        Spec: spec/protocols/context-perception.md §8
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        bridge = self._ensure_portal_bridge(obs)

        if bridge is None:
            return BasicRendering(
                summary="Lens failed",
                content=f"{DIM}Context Perception not available{RESET}",
                metadata={"error": "context_perception_unavailable"},
            )

        lens = await bridge.create_lens(file_path, focus)

        if lens is None:
            return BasicRendering(
                summary=f"Lens failed: {file_path}",
                content=f"{YELLOW}Could not create lens{RESET}\n\n"
                f"File: {file_path}\n"
                f"Focus: {focus}\n\n"
                f"{DIM}Possible reasons:\n"
                f"  - File not found\n"
                f"  - Function/class not found\n"
                f"  - Invalid focus specifier{RESET}",
                metadata={"error": "lens_creation_failed"},
            )

        lines = [f"{BOLD}🔍 Lens: {lens.visible_name}{RESET}\n"]
        lines.append(f"{DIM}Source: {lens.source_path}{RESET}")
        lines.append(f"{DIM}Lines: {lens.line_range[0]}-{lens.line_range[1]}{RESET}\n")
        lines.append(f"{CYAN}```{RESET}")
        lines.append(lens.visible_content)
        lines.append(f"{CYAN}```{RESET}")

        return BasicRendering(
            summary=f"Lens: {lens.visible_name}",
            content="\n".join(lines),
            metadata={
                "source_path": lens.source_path,
                "visible_name": lens.visible_name,
                "line_range": list(lens.line_range),
                "route": f"/context/lens/{lens.visible_name}",
            },
        )

    # === Phase 4: Witness Integration ===

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("witness")],
        help="Convert current trail to Witness mark (evidence)",
    )
    async def emit_trail(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        name: str = "",
        claim: str | None = None,
    ) -> Renderable:
        """
        Convert the current navigation trail to a Witness mark.

        The trail becomes evidence that can be used in ASHC proofs.
        This implements the Trail → Witness integration from Phase 4.

        Args:
            name: Optional name for the trail (default: "Context Exploration")
            claim: Optional claim this trail supports

        Returns:
            Rendering with mark ID and evidence summary

        Spec: spec/protocols/context-perception.md §10
        """
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = (
            observer
            if isinstance(observer, Observer)
            else Observer.from_umwelt(observer)
        )
        graph = self._ensure_graph(obs)

        # Get current trail
        trail = graph.to_trail()

        if not trail.steps:
            return BasicRendering(
                summary="No trail to emit",
                content=f"{YELLOW}No trail steps recorded yet.{RESET}\n\n"
                f"Use 'focus <path>' and 'navigate <edge>' to build a trail first.",
                metadata={"error": "empty_trail"},
            )

        # Set trail name
        trail.name = name or "Context Exploration"

        try:
            from services.witness.trail_bridge import emit_trail_as_mark

            mark = await emit_trail_as_mark(trail, claim)

            lines = [f"{GREEN}✓ Trail emitted as Witness mark{RESET}\n"]
            lines.append(f"{BOLD}Mark ID:{RESET} {mark.id}")
            lines.append(f"{BOLD}Trail:{RESET} {mark.trail_name}")
            lines.append(f"{BOLD}Steps:{RESET} {mark.evidence.step_count}")
            lines.append(f"{BOLD}Evidence Strength:{RESET} {mark.evidence.evidence_strength}")

            if mark.evidence.principles_signaled:
                principles = ", ".join(p[0] for p in mark.evidence.principles_signaled)
                lines.append(f"{BOLD}Principles Signaled:{RESET} {principles}")

            if claim:
                lines.append(f"\n{BOLD}Claim:{RESET} {claim}")

            return BasicRendering(
                summary=f"Trail emitted: {mark.id}",
                content="\n".join(lines),
                metadata={
                    "mark_id": str(mark.id),
                    "trail_id": mark.trail_id,
                    "evidence": mark.evidence.to_dict(),
                },
            )
        except ImportError:
            return BasicRendering(
                summary="Witness integration unavailable",
                content=f"{YELLOW}Witness service not available.{RESET}\n\n"
                f"Trail created but not emitted to Witness ledger.",
                metadata={
                    "error": "witness_unavailable",
                    "trail": trail.to_dict(),
                },
            )
        except Exception as e:
            return BasicRendering(
                summary="Emit failed",
                content=f"{YELLOW}Failed to emit trail: {e}{RESET}",
                metadata={"error": str(e)},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect methods."""
        match aspect:
            case "navigate":
                edge_type = kwargs.get("edge_type", kwargs.get("edge", ""))
                return await self.navigate(observer, edge_type)
            case "focus":
                path = kwargs.get("path", "")
                return await self.focus(observer, path)
            case "backtrack":
                return await self.backtrack(observer)
            case "trail":
                return await self.trail(observer)
            case "subgraph":
                max_depth = kwargs.get("max_depth", 3)
                return await self.subgraph(observer, max_depth)
            # Phase 2: Context Perception aspects
            case "outline":
                return await self.outline(observer)
            case "copy":
                node_path = kwargs.get("node_path", kwargs.get("path", ""))
                start_line = kwargs.get("start_line", 0)
                start_col = kwargs.get("start_col", 0)
                end_line = kwargs.get("end_line", 0)
                end_col = kwargs.get("end_col", 0)
                return await self.copy(
                    observer, node_path, start_line, start_col, end_line, end_col
                )
            case "paste":
                target_path = kwargs.get("target_path", kwargs.get("path", ""))
                line = kwargs.get("line", 0)
                col = kwargs.get("col", 0)
                return await self.paste(observer, target_path, line, col)
            case "lens":
                file_path = kwargs.get("file_path", kwargs.get("file", ""))
                focus = kwargs.get("focus", "")
                return await self.file_lens(observer, file_path, focus)
            # Phase 4: Witness integration
            case "emit_trail":
                name = kwargs.get("name", "")
                claim = kwargs.get("claim")
                return await self.emit_trail(observer, name, claim)
            case _:
                return BasicRendering(
                    summary=f"Unknown aspect: {aspect}",
                    content=f"Available aspects: {', '.join(CONTEXT_AFFORDANCES)}",
                    metadata={"error": "unknown_aspect"},
                )


# === Factory Functions ===

_node: ContextNavNode | None = None


def get_context_nav_node() -> ContextNavNode:
    """Get the singleton ContextNavNode."""
    global _node
    if _node is None:
        _node = ContextNavNode()
    return _node


def set_context_nav_node(node: ContextNavNode | None) -> None:
    """Set the singleton ContextNavNode (for testing)."""
    global _node
    _node = node


def create_context_node(path: str) -> ContextNode:
    """Create a ContextNode for a given AGENTESE path."""
    holon = path.split(".")[-1]
    return ContextNode(path=path, holon=holon)


def create_context_graph(
    focus_paths: list[str],
    observer: Observer,
) -> ContextGraph:
    """Create a ContextGraph with initial focus."""
    nodes = {create_context_node(p) for p in focus_paths}
    return ContextGraph(
        focus=nodes,
        trail=[TrailStep(node_path=p, edge_type=None) for p in focus_paths],
        observer=observer,
    )


__all__ = [
    # Core data structures
    "ContextNode",
    "ContextGraph",
    "Trail",
    "TrailStep",
    # Edge types
    "STRUCTURAL_EDGES",
    "TESTING_EDGES",
    "SPEC_EDGES",
    "EVIDENCE_EDGES",
    "TEMPORAL_EDGES",
    "SEMANTIC_EDGES",
    "ALL_STANDARD_EDGES",
    "REVERSE_EDGES",
    "get_reverse_edge",
    # AGENTESE node
    "CONTEXT_AFFORDANCES",
    "ContextNavNode",
    "get_context_nav_node",
    "set_context_nav_node",
    # Factories
    "create_context_node",
    "create_context_graph",
]
