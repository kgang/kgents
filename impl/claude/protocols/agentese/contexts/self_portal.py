"""
AGENTESE Portal Token Context.

self.portal.* paths for navigating portal tokens (expandable hyperedges).

Portal tokens are the UX projection of the typed-hypergraph:
- COLLAPSED: Shows edge type and destination count
- EXPANDED: Renders destination document inline
- Recursive: Expanded content reveals more portals

AGENTESE Principle: "Navigation is expansion. Expansion is navigation."

Spec: spec/protocols/portal-token.md

Teaching:
    gotcha: PortalTree.expand() returns bool, not the tree. The tree mutates
            in place (expand/collapse are stateful operations).
            (Evidence: test_self_portal.py::test_expand_returns_bool)

    gotcha: The trail conversion uses DFS order - expanded nodes first,
            then collapsed children at each level.
            (Evidence: test_self_portal.py::test_trail_dfs_order)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import BaseLogosNode, BasicRendering, Observer, Renderable
from ..registry import node
from .portal_response import PortalResponse

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Affordances ===

PORTAL_AFFORDANCES: tuple[str, ...] = (
    "manifest",  # Current portal tree state
    "expand",  # Expand a portal
    "collapse",  # Collapse a portal
    "tree",  # Render full tree
    "trail",  # Convert to trail
    "save_trail",  # Save trail to file with witness mark
    "load_trail",  # Load a saved trail
    "list_trails",  # List saved trails
    "replay",  # Replay a saved trail
    "available",  # Available portals to expand
)


# === AGENTESE Node ===


@node(
    "self.portal",
    description="Portal token navigation and expansion",
)
@dataclass
class PortalNavNode(BaseLogosNode):
    """
    self.portal - Navigate portal tokens.

    Portal tokens are expandable hyperedges in the typed-hypergraph.
    Instead of navigating away, linked content appears inline.

    The tree of expansions IS:
    - The current view (what's visible)
    - The trail (how we got here)
    - The context (what's "open")
    - The evidence (what we explored)

    Phase 2 Integration:
    - Syncs with Outline model via OutlinePortalBridge
    - Trail steps are recorded in both systems
    - ContextEvents are emitted for agent context updates

    Usage:
        kg op manifest           # Current portal tree
        kg op expand tests       # Expand [tests] portal
        kg op collapse tests     # Collapse [tests] portal
        kg op tree               # Render full tree
        kg op trail              # Convert to trail
    """

    _handle: str = "self.portal"

    # Current portal tree (session-scoped, lazy-initialized)
    _tree: Any | None = field(default=None, repr=False)

    # Portal bridge for Outline synchronization (Phase 2)
    _portal_bridge: Any | None = field(default=None, repr=False)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return PORTAL_AFFORDANCES

    def _ensure_tree(self, root_path: str | None = None, file_path: str | None = None) -> Any:
        """
        Ensure we have an initialized portal tree.

        Lazily imports PortalTree to avoid circular dependencies.

        Args:
            root_path: Deprecated - use file_path instead
            file_path: Path to source file to analyze (uses file_analyzer)
        """
        # Use file_path if provided, fallback to root_path for backwards compat
        target_path = file_path or root_path

        # Check if we need to create a new tree:
        # - Tree doesn't exist, OR
        # - We have a specific target_path AND it differs from current file
        current_file = getattr(self, "_current_file", None)
        need_new_tree = self._tree is None or (
            target_path is not None and target_path != current_file
        )

        if need_new_tree:
            from protocols.file_operad.portal import PortalNode, PortalState, PortalTree

            # Default to cwd if no path provided
            if target_path is None:
                target_path = str(Path.cwd())

            # Resolve relative paths from repo root
            target_file = Path(target_path)
            if not target_file.is_absolute():
                # Try to find repo root (look for .git or CLAUDE.md)
                cwd = Path.cwd()
                for parent in [cwd] + list(cwd.parents):
                    candidate = parent / target_path
                    if candidate.exists():
                        target_path = str(candidate)
                        target_file = candidate
                        break

            # Check if this is a Python file - use file analyzer
            if target_path.endswith(".py") and target_file.exists():
                from protocols.file_operad.file_analyzer import analyze_python_file

                portals = analyze_python_file(target_path)
                root = PortalNode(
                    path=target_path,
                    depth=0,
                    expanded=True,
                    state=PortalState.EXPANDED,
                    children=portals.to_portal_nodes(depth=1),
                )
                self._tree = PortalTree(root=root)
            else:
                # Fallback to basic tree
                root = PortalNode(path=target_path, depth=0)
                self._tree = PortalTree(root=root)

            self._current_file = target_path

            # Connect to portal bridge if available
            bridge = self._ensure_bridge()
            if bridge is not None:
                bridge.set_portal_tree(self._tree)

        return self._tree

    def _ensure_bridge(self) -> Any:
        """
        Ensure we have an initialized portal bridge.

        The bridge connects the PortalTree to the Outline model
        for synchronized state management.
        """
        if self._portal_bridge is None:
            try:
                from protocols.context.portal_bridge import create_bridge

                self._portal_bridge = create_bridge(observer_id="portal")
            except ImportError:
                # Context Perception not available
                pass
        return self._portal_bridge

    def _record_expansion(self, portal_path: str, edge_type: str | None = None) -> None:
        """
        Record a portal expansion in the Outline trail.

        This ensures trail steps are synced between PortalTree and Outline.
        """
        bridge = self._ensure_bridge()
        if bridge is not None:
            try:
                bridge.outline.record_step(
                    action="expand",
                    node_path=portal_path,
                    edge_type=edge_type,
                )
            except Exception:
                pass  # Don't break portal operation if bridge fails

    def _record_collapse(self, portal_path: str, edge_type: str | None = None) -> None:
        """
        Record a portal collapse in the Outline trail.
        """
        bridge = self._ensure_bridge()
        if bridge is not None:
            try:
                bridge.outline.record_step(
                    action="collapse",
                    node_path=portal_path,
                    edge_type=edge_type,
                )
            except Exception:
                pass

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View current portal tree state",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        root_path: str | None = None,
        file_path: str | None = None,
        max_depth: int = 5,
        expand_all: bool = False,
        response_format: str = "cli",
        **kwargs: Any,
    ) -> Renderable:
        """
        Manifest the current portal tree state.

        Args:
            root_path: Deprecated - use file_path instead
            file_path: Path to source file to analyze
            max_depth: Maximum expansion depth (default 5)
            expand_all: If True, expand all portals up to max_depth
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Colored text rendering
            For JSON: Structured PortalTree data in metadata
        """
        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path=root_path, file_path=file_path)
        # Only update max_depth if explicitly provided
        if max_depth != 5:  # 5 is the default
            tree.max_depth = max_depth

        # JSON response mode for frontend
        # Returns PortalResponse (canonical contract shape)
        if response_format == "json":
            return PortalResponse.manifest(
                tree=tree.to_dict(),
                observer=obs.archetype,
            )

        # CLI response mode (default)
        rendered = tree.render()

        return BasicRendering(
            summary="Portal Tree",
            content=self._format_manifest(tree, rendered),
            metadata={
                "root": tree.root.path,
                "expanded_count": self._count_expanded(tree.root),
                "max_depth": tree.max_depth,
                "observer": obs.archetype,
                "route": "/portal",
            },
        )

    def _format_manifest(self, tree: Any, rendered: str) -> str:
        """Format the manifest content with ANSI colors for CLI."""
        # ANSI color codes
        BOLD = "\033[1m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        RESET = "\033[0m"

        lines = [f"{BOLD}Portal Tree{RESET}\n"]

        # Tree info
        lines.append(f"{BOLD}Root:{RESET} {CYAN}{tree.root.path}{RESET}")
        lines.append(f"{BOLD}Expanded:{RESET} {self._count_expanded(tree.root)} nodes")
        lines.append(f"{BOLD}Max Depth:{RESET} {tree.max_depth}\n")

        # Tree structure
        if rendered.strip():
            lines.append(f"{BOLD}Structure:{RESET}")
            lines.append(rendered)
        else:
            lines.append(f"{DIM}(empty tree){RESET}")

        # Commands
        lines.append("")
        lines.append(f"{DIM}Commands: expand <path> | collapse <path> | tree | trail{RESET}")

        return "\n".join(lines)

    def _count_expanded(self, node: Any) -> int:
        """Count expanded nodes in tree."""
        count = 1 if node.expanded else 0
        for child in node.children:
            count += self._count_expanded(child)
        return count

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("portal_tree")],
        help="Expand a portal at the given path",
    )
    async def expand(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        portal_path: str,
        root_path: str | None = None,
        file_path: str | None = None,
        edge_type: str | None = None,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Expand a portal at the given path.

        Args:
            portal_path: JSON-encoded array or "/" separated path (e.g., '["imports", "foo.py"]')
            root_path: Deprecated - use file_path instead
            file_path: Path to source file
            edge_type: Optional edge type for filtering
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Colored text rendering with sympathetic error messages
            For JSON: PortalResponse with structured error info for frontend
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path=root_path, file_path=file_path)

        # Parse portal path into list
        # Try JSON first (from frontend), fallback to "/" split (for CLI)
        path_segments: list[str] = []
        if portal_path.startswith("["):
            import json

            try:
                path_segments = json.loads(portal_path)
            except json.JSONDecodeError:
                path_segments = [s.strip() for s in portal_path.split("/") if s.strip()]
        else:
            path_segments = [s.strip() for s in portal_path.split("/") if s.strip()]

        # Attempt expansion - now returns structured ExpandResult
        result = tree.expand(path_segments)

        if result.success:
            # Record in Outline trail (Phase 2 integration)
            self._record_expansion(portal_path, edge_type=edge_type or "expand")

            # Phase 2: Emit witness mark if significant (depth 2+)
            # Depth = number of path segments (root = 0, first child = 1, etc.)
            depth = len(path_segments)
            evidence_id: str | None = None
            if depth >= 2 or edge_type == "evidence":
                from services.witness.portal_marks import mark_portal_expansion

                evidence_id = await mark_portal_expansion(
                    file_path=self._current_file or "",
                    edge_type=edge_type or "expand",
                    portal_path=path_segments,
                    depth=depth,
                    observer_archetype=obs.archetype,
                )

            # JSON response mode for frontend
            # Returns PortalResponse (canonical contract shape)
            if response_format == "json":
                return PortalResponse.expand_success(
                    tree=tree.to_dict(),
                    expanded_path=portal_path,
                    evidence_id=evidence_id,
                )

            content = f"{GREEN}Expanded{RESET} [{portal_path}]\n\n{tree.render()}"
            return BasicRendering(
                summary=f"Expanded [{portal_path}]",
                content=content,
                metadata={
                    "success": True,
                    "portal_path": portal_path,
                    "expanded_count": self._count_expanded(tree.root),
                    "evidence_id": evidence_id,
                },
            )
        else:
            # Expansion failed - use structured error from ExpandResult
            # JSON response mode for frontend - includes all error details
            if response_format == "json":
                return PortalResponse.from_expand_result(
                    portal_path=portal_path,
                    result=result,
                    tree=tree.to_dict(),
                )

            # CLI response - sympathetic, human-readable error
            # Format based on error type
            error_code = result.error_code.value if result.error_code else "unknown"

            # Build the error display
            lines = []

            # Header with appropriate color based on error type
            if error_code == "depth_limit_reached":
                # Depth limit is a FEATURE, not a failure - show it distinctly
                lines.append(f"{YELLOW}⚠ Depth Limit Reached{RESET}\n")
                lines.append(
                    f"You've explored {result.depth} levels deep (max: {result.max_depth})."
                )
            else:
                lines.append(f"{YELLOW}Could not expand [{portal_path}]{RESET}\n")

            # Show the specific error
            if result.error_message:
                lines.append(f"{DIM}{result.error_message}{RESET}")

            # Show the suggestion
            if result.suggestion:
                lines.append("")
                lines.append(f"{BOLD}What you can try:{RESET}")
                lines.append(f"  {result.suggestion}")

            return BasicRendering(
                summary=f"Failed to expand [{portal_path}]",
                content="\n".join(lines),
                metadata={
                    "success": False,
                    "portal_path": portal_path,
                    "error": result.error_message,
                    "error_code": error_code,
                    "suggestion": result.suggestion,
                    "depth": result.depth,
                    "max_depth": result.max_depth,
                },
            )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("portal_tree")],
        help="Collapse a portal at the given path",
    )
    async def collapse(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        portal_path: str,
        root_path: str | None = None,
        file_path: str | None = None,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Collapse a portal, hiding children.

        Args:
            portal_path: Path to collapse
            root_path: Deprecated - use file_path instead
            file_path: Path to source file
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Colored text rendering
            For JSON: {success, tree} for frontend merging
        """
        BOLD = "\033[1m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path=root_path, file_path=file_path)

        # Parse portal path into list
        # Try JSON first (from frontend), fallback to "/" split (for CLI)
        path_segments: list[str] = []
        if portal_path.startswith("["):
            import json

            try:
                path_segments = json.loads(portal_path)
            except json.JSONDecodeError:
                path_segments = [s.strip() for s in portal_path.split("/") if s.strip()]
        else:
            path_segments = [s.strip() for s in portal_path.split("/") if s.strip()]

        # Attempt collapse
        success = tree.collapse(path_segments)

        if success:
            # Record in Outline trail (Phase 2 integration)
            self._record_collapse(portal_path, edge_type="collapse")

            # JSON response mode for frontend
            # Returns PortalResponse (canonical contract shape)
            if response_format == "json":
                return PortalResponse.collapse_success(
                    tree=tree.to_dict(),
                    collapsed_path=portal_path,
                )

            content = f"{DIM}Collapsed{RESET} [{portal_path}]\n\n{tree.render()}"
            return BasicRendering(
                summary=f"Collapsed [{portal_path}]",
                content=content,
                metadata={
                    "success": True,
                    "portal_path": portal_path,
                    "expanded_count": self._count_expanded(tree.root),
                },
            )
        else:
            # JSON response mode for frontend
            if response_format == "json":
                return PortalResponse.collapse_failure(
                    portal_path=portal_path,
                    error=f"Could not collapse [{portal_path}] - path not found",
                )

            return BasicRendering(
                summary=f"Failed to collapse [{portal_path}]",
                content=f"Could not collapse [{portal_path}] - path not found",
                metadata={
                    "success": False,
                    "portal_path": portal_path,
                    "error": "collapse_failed",
                },
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Render full portal tree",
    )
    async def tree(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        max_depth: int | None = None,
        root_path: str | None = None,
    ) -> Renderable:
        """Render the full portal tree."""
        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path)

        rendered = tree.render(max_depth=max_depth)

        return BasicRendering(
            summary=f"Portal Tree (depth: {max_depth or tree.max_depth})",
            content=rendered,
            metadata={
                "root": tree.root.path,
                "max_depth": max_depth or tree.max_depth,
                "expanded_count": self._count_expanded(tree.root),
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Convert portal tree to exploration trail",
    )
    async def trail(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        name: str = "Portal Exploration",
        root_path: str | None = None,
    ) -> Renderable:
        """Convert the portal tree to a Trail artifact."""
        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path)

        # Convert to trail
        trail = tree.to_trail(name=name, created_by=obs.id if hasattr(obs, "id") else "unknown")

        return BasicRendering(
            summary=f"Trail: {len(trail.steps)} steps",
            content=self._format_trail(trail),
            metadata={
                "trail_id": trail.id if hasattr(trail, "id") else None,
                "trail_name": trail.name,
                "step_count": len(trail.steps),
                "nodes_visited": [s.node for s in trail.steps],
            },
        )

    def _format_trail(self, trail: Any) -> str:
        """Format trail for display."""
        BOLD = "\033[1m"
        YELLOW = "\033[33m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        lines = [f"{BOLD}Trail: {trail.name}{RESET}\n"]
        lines.append(f"Steps: {len(trail.steps)}\n")

        for i, step in enumerate(trail.steps):
            if step.edge_taken:
                lines.append(
                    f"  {DIM}{i + 1}.{RESET} {step.node} {YELLOW}--[{step.edge_taken}]-->{RESET}"
                )
            else:
                lines.append(f"  {DIM}{i + 1}.{RESET} {step.node} {DIM}(start){RESET}")

        return "\n".join(lines)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List available portals that can be expanded",
    )
    async def available(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        root_path: str | None = None,
    ) -> Renderable:
        """List available portals that can be expanded."""
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path)

        # Collect expandable portals
        expandable = self._collect_expandable(tree.root, tree.max_depth)
        collapsible = self._collect_collapsible(tree.root)

        lines = [f"{BOLD}Portal Affordances{RESET}\n"]

        if expandable:
            lines.append(f"{BOLD}Can Expand:{RESET}")
            for path, edge_type, depth in expandable:
                lines.append(f"  {GREEN}+{RESET} [{edge_type}] {path} {DIM}(depth: {depth}){RESET}")
            lines.append("")

        if collapsible:
            lines.append(f"{BOLD}Can Collapse:{RESET}")
            for path, edge_type in collapsible:
                lines.append(f"  {DIM}-{RESET} [{edge_type}] {path}")
            lines.append("")

        if not expandable and not collapsible:
            lines.append(f"{DIM}No portals available{RESET}")

        return BasicRendering(
            summary=f"Affordances: {len(expandable)} expandable, {len(collapsible)} collapsible",
            content="\n".join(lines),
            metadata={
                "expandable": [{"path": p, "edge_type": e, "depth": d} for p, e, d in expandable],
                "collapsible": [{"path": p, "edge_type": e} for p, e in collapsible],
            },
        )

    def _collect_expandable(
        self, node: Any, max_depth: int, current_path: str = ""
    ) -> list[tuple[str, str, int]]:
        """Collect portals that can be expanded."""
        result: list[tuple[str, str, int]] = []

        for child in node.children:
            child_path = f"{current_path}/{child.path}" if current_path else child.path

            if not child.expanded and child.depth < max_depth:
                result.append((child_path, child.edge_type or "unknown", child.depth))

            # Recurse into expanded children
            if child.expanded:
                result.extend(self._collect_expandable(child, max_depth, child_path))

        return result

    def _collect_collapsible(self, node: Any, current_path: str = "") -> list[tuple[str, str]]:
        """Collect portals that can be collapsed."""
        result: list[tuple[str, str]] = []

        for child in node.children:
            child_path = f"{current_path}/{child.path}" if current_path else child.path

            if child.expanded:
                result.append((child_path, child.edge_type or "unknown"))
                # Recurse
                result.extend(self._collect_collapsible(child, child_path))

        return result

    # ==========================================================================
    # Phase 3: Trail Persistence & Replay
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("trail_file")],
        help="Save current portal exploration as a trail file",
    )
    async def save_trail(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        name: str = "Portal Exploration",
        root_path: str | None = None,
        file_path: str | None = None,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Save the current portal tree exploration as a trail.

        Persists to ~/.kgents/trails/<trail_id>.json and emits a witness mark.

        Args:
            name: Name for the saved trail
            root_path: Deprecated - use file_path instead
            file_path: Path to source file
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            For CLI: Success message with trail ID and file path
            For JSON: PortalResponse with trail_id and evidence_id

        Example:
            kg op save_trail "Auth Bug Investigation"
            # → Saved to ~/.kgents/trails/auth-bug-investigation_20251222_143021.json
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)
        tree = self._ensure_tree(root_path=root_path, file_path=file_path)

        # Convert tree to trail
        trail = tree.to_trail(name=name, created_by=obs.id if hasattr(obs, "id") else obs.archetype)

        if not trail.steps:
            if response_format == "json":
                return PortalResponse.save_trail_failure(
                    error="No exploration steps to save. Expand some portals first."
                )

            return BasicRendering(
                summary="No trail to save",
                content=f"{YELLOW}No exploration steps to save.{RESET}\n\n"
                f"Use 'expand <path>' to explore portals first.",
                metadata={"error": "empty_trail"},
            )

        try:
            from protocols.trail.file_persistence import save_trail as save_trail_to_file

            result = await save_trail_to_file(trail, name=name, emit_mark=True)

            if response_format == "json":
                return PortalResponse.save_trail_success(
                    trail_id=result.trail_id,
                    name=result.name,
                    step_count=result.step_count,
                    file_path=str(result.file_path),
                    evidence_id=result.mark_id,
                )

            lines = [f"{GREEN}✓ Trail saved{RESET}\n"]
            lines.append(f"{BOLD}Trail ID:{RESET} {result.trail_id}")
            lines.append(f"{BOLD}Name:{RESET} {result.name}")
            lines.append(f"{BOLD}Steps:{RESET} {result.step_count}")
            lines.append(f"{BOLD}File:{RESET} {result.file_path}")
            if result.mark_id:
                lines.append(f"{BOLD}Evidence:{RESET} {result.mark_id}")
            lines.append(f"\n{DIM}Replay: kg op replay {result.trail_id}{RESET}")

            return BasicRendering(
                summary=f"Trail saved: {result.trail_id}",
                content="\n".join(lines),
                metadata={
                    "trail_id": result.trail_id,
                    "name": result.name,
                    "step_count": result.step_count,
                    "file_path": str(result.file_path),
                    "evidence_id": result.mark_id,
                },
            )

        except Exception as e:
            if response_format == "json":
                return PortalResponse.save_trail_failure(error=str(e))

            return BasicRendering(
                summary="Save failed",
                content=f"{YELLOW}Failed to save trail: {e}{RESET}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Load a saved trail by ID",
    )
    async def load_trail(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Load a saved trail by ID.

        Args:
            trail_id: Trail ID to load
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            Trail data with metadata
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        try:
            from protocols.trail.file_persistence import load_trail as load_trail_from_file

            result = await load_trail_from_file(trail_id)

            if result is None:
                if response_format == "json":
                    return PortalResponse.load_trail_failure(
                        trail_id=trail_id,
                        error=f"Trail not found: {trail_id}",
                    )

                return BasicRendering(
                    summary=f"Trail not found: {trail_id}",
                    content=f"{YELLOW}Trail not found: {trail_id}{RESET}\n\n"
                    f"{DIM}Use 'list_trails' to see available trails.{RESET}",
                    metadata={"error": "not_found", "trail_id": trail_id},
                )

            if response_format == "json":
                return PortalResponse.load_trail_success(
                    trail_id=result.trail_id,
                    name=result.name,
                    step_count=len(result.steps),
                )

            lines = [f"{BOLD}Trail: {result.name}{RESET}\n"]
            lines.append(f"{BOLD}ID:{RESET} {result.trail_id}")
            lines.append(f"{BOLD}Created by:{RESET} {result.created_by}")
            lines.append(f"{BOLD}Created at:{RESET} {result.created_at.isoformat()}")
            lines.append(f"{BOLD}Steps:{RESET} {len(result.steps)}")
            lines.append(f"{BOLD}Evidence:{RESET} {result.evidence_strength}")
            lines.append("")

            # Show steps
            for i, step in enumerate(result.steps):
                edge = step.get("edge") or step.get("edge_type")
                source = step.get("source_path") or step.get("node_path", "?")
                if edge:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {GREEN}──[{edge}]──>{RESET}")
                else:
                    lines.append(f"  {DIM}{i + 1}.{RESET} {source} {DIM}(start){RESET}")

            lines.append(f"\n{DIM}Replay: kg op replay {result.trail_id}{RESET}")

            return BasicRendering(
                summary=f"Trail: {result.name}",
                content="\n".join(lines),
                metadata={
                    "trail_id": result.trail_id,
                    "name": result.name,
                    "steps": result.steps,
                    "evidence_strength": result.evidence_strength,
                },
            )

        except Exception as e:
            if response_format == "json":
                return PortalResponse.load_trail_failure(trail_id=trail_id, error=str(e))

            return BasicRendering(
                summary="Load failed",
                content=f"{YELLOW}Failed to load trail: {e}{RESET}",
                metadata={"error": str(e)},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all saved trails",
    )
    async def list_trails(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        limit: int = 20,
        response_format: str = "cli",
    ) -> Renderable:
        """
        List all saved trails.

        Args:
            limit: Maximum trails to return (default 20)
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            List of trails with metadata
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

        from protocols.trail.file_persistence import list_trails as list_trails_from_file

        entries = list_trails_from_file(limit=limit)

        if response_format == "json":
            trails = [
                {
                    "trail_id": e.trail_id,
                    "name": e.name,
                    "step_count": e.step_count,
                    "saved_at": e.saved_at.isoformat(),
                    "evidence_strength": e.evidence_strength,
                }
                for e in entries
            ]
            return PortalResponse.list_trails_success(trails)

        if not entries:
            return BasicRendering(
                summary="No saved trails",
                content=f"{DIM}No saved trails found.{RESET}\n\n"
                f'Save a trail: kg op save_trail "My Investigation"',
                metadata={"count": 0},
            )

        lines = [f"{BOLD}Saved Trails ({len(entries)}){RESET}\n"]

        for entry in entries:
            saved_date = entry.saved_at.strftime("%Y-%m-%d %H:%M")
            lines.append(
                f"  {CYAN}●{RESET} {entry.name} "
                f"{DIM}({entry.step_count} steps, {saved_date}){RESET}"
            )
            lines.append(f"    {DIM}ID: {entry.trail_id}{RESET}")

        lines.append(f"\n{DIM}Load: kg op load_trail <trail_id>{RESET}")
        lines.append(f"{DIM}Replay: kg op replay <trail_id>{RESET}")

        return BasicRendering(
            summary=f"Saved Trails ({len(entries)})",
            content="\n".join(lines),
            metadata={
                "count": len(entries),
                "trails": [
                    {
                        "trail_id": e.trail_id,
                        "name": e.name,
                        "step_count": e.step_count,
                        "saved_at": e.saved_at.isoformat(),
                    }
                    for e in entries
                ],
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("portal_tree")],
        help="Replay a saved trail, reconstructing the portal tree state",
    )
    async def replay(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        trail_id: str,
        response_format: str = "cli",
    ) -> Renderable:
        """
        Replay a saved trail, reconstructing the portal tree state.

        Loads the trail and re-expands portals to recreate the exact view.

        Args:
            trail_id: Trail ID to replay
            response_format: "cli" for colored text, "json" for structured data

        Returns:
            Reconstructed portal tree
        """
        BOLD = "\033[1m"
        GREEN = "\033[32m"
        DIM = "\033[2m"
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        obs = observer if isinstance(observer, Observer) else Observer.from_umwelt(observer)

        try:
            from protocols.file_operad.portal import PortalNode, PortalState, PortalTree
            from protocols.trail.file_persistence import load_trail as load_trail_from_file

            result = await load_trail_from_file(trail_id)

            if result is None:
                if response_format == "json":
                    return PortalResponse.replay_failure(
                        trail_id=trail_id,
                        error=f"Trail not found: {trail_id}",
                    )

                return BasicRendering(
                    summary=f"Trail not found: {trail_id}",
                    content=f"{YELLOW}Trail not found: {trail_id}{RESET}",
                    metadata={"error": "not_found", "trail_id": trail_id},
                )

            # Find the root path from the first step
            if not result.steps:
                if response_format == "json":
                    return PortalResponse.replay_failure(
                        trail_id=trail_id,
                        error="Trail has no steps to replay",
                    )

                return BasicRendering(
                    summary="Empty trail",
                    content=f"{YELLOW}Trail has no steps to replay.{RESET}",
                    metadata={"error": "empty_trail"},
                )

            # Get root path from first step
            first_step = result.steps[0]
            root_path = first_step.get("source_path") or first_step.get("node_path", ".")

            # Create new tree at root
            root = PortalNode(path=root_path, depth=0, expanded=True, state=PortalState.EXPANDED)
            tree = PortalTree(root=root)

            # Replay each step as an expansion
            # Steps after the first represent expansions
            for step in result.steps[1:]:
                edge = step.get("edge") or step.get("edge_type")
                dest = step.get("destination_paths", [])
                if edge and dest:
                    # Create child node for this expansion
                    child_path = dest[0] if dest else edge
                    child = PortalNode(
                        path=child_path,
                        edge_type=edge,
                        depth=1,  # Simplified - real impl would track actual depth
                        expanded=True,
                        state=PortalState.EXPANDED,
                    )
                    root.children.append(child)

            # Update the internal tree
            self._tree = tree
            self._current_file = root_path

            if response_format == "json":
                return PortalResponse.replay_success(
                    trail_id=result.trail_id,
                    name=result.name,
                    tree=tree.to_dict(),
                    step_count=len(result.steps),
                )

            lines = [f"{GREEN}✓ Trail replayed{RESET}\n"]
            lines.append(f"{BOLD}Trail:{RESET} {result.name}")
            lines.append(f"{BOLD}Steps replayed:{RESET} {len(result.steps)}")
            lines.append("")
            lines.append(f"{BOLD}Reconstructed Tree:{RESET}")
            lines.append(tree.render())

            return BasicRendering(
                summary=f"Replayed: {result.name}",
                content="\n".join(lines),
                metadata={
                    "trail_id": result.trail_id,
                    "name": result.name,
                    "step_count": len(result.steps),
                    "tree": tree.to_dict(),
                },
            )

        except Exception as e:
            if response_format == "json":
                return PortalResponse.replay_failure(trail_id=trail_id, error=str(e))

            return BasicRendering(
                summary="Replay failed",
                content=f"{YELLOW}Failed to replay trail: {e}{RESET}",
                metadata={"error": str(e)},
            )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to aspect methods."""
        # Common parameters
        root_path = kwargs.get("root_path")
        file_path = kwargs.get("file_path")
        response_format = kwargs.get("response_format", "cli")

        match aspect:
            case "manifest":
                max_depth = kwargs.get("max_depth", 5)
                expand_all = kwargs.get("expand_all", False)
                return await self.manifest(
                    observer, root_path, file_path, max_depth, expand_all, response_format
                )
            case "expand":
                portal_path = kwargs.get("portal_path", kwargs.get("path", ""))
                edge_type = kwargs.get("edge_type")
                return await self.expand(
                    observer, portal_path, root_path, file_path, edge_type, response_format
                )
            case "collapse":
                portal_path = kwargs.get("portal_path", kwargs.get("path", ""))
                return await self.collapse(
                    observer, portal_path, root_path, file_path, response_format
                )
            case "tree":
                max_depth = kwargs.get("max_depth")
                return await self.tree(observer, max_depth, root_path)
            case "trail":
                name = kwargs.get("name", "Portal Exploration")
                return await self.trail(observer, name, root_path)
            # Phase 3: Trail Persistence & Replay
            case "save_trail":
                name = kwargs.get("name", "Portal Exploration")
                return await self.save_trail(observer, name, root_path, file_path, response_format)
            case "load_trail":
                trail_id = kwargs.get("trail_id", "")
                return await self.load_trail(observer, trail_id, response_format)
            case "list_trails":
                limit = kwargs.get("limit", 20)
                return await self.list_trails(observer, limit, response_format)
            case "replay":
                trail_id = kwargs.get("trail_id", "")
                return await self.replay(observer, trail_id, response_format)
            case "available":
                return await self.available(observer, root_path)
            case _:
                return BasicRendering(
                    summary=f"Unknown aspect: {aspect}",
                    content=f"Available aspects: {', '.join(PORTAL_AFFORDANCES)}",
                    metadata={"error": "unknown_aspect"},
                )


# === Factory Functions ===

_node: PortalNavNode | None = None


def get_portal_nav_node() -> PortalNavNode:
    """Get the singleton PortalNavNode."""
    global _node
    if _node is None:
        _node = PortalNavNode()
    return _node


def set_portal_nav_node(node: PortalNavNode | None) -> None:
    """Set the singleton PortalNavNode (for testing)."""
    global _node
    _node = node


__all__ = [
    "PORTAL_AFFORDANCES",
    "PortalNavNode",
    "get_portal_nav_node",
    "set_portal_nav_node",
]
