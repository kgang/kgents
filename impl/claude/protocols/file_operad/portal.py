"""
Portal Tokens: Expandable Cross-Operad Links

"You don't go to the document. The document comes to you."

Portal tokens transform static "Wires To" sections into live, expandable
hyperedges. Instead of navigating away, the linked content appears inline.

The tree of expansions IS:
- The current view (what's visible)
- The trail (how we got here)
- The context (what's "open")
- The evidence (what we explored)

See: spec/protocols/portal-token.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Callable

    from protocols.exploration.types import Trail
    from .context_bridge import ContextEvent


# =============================================================================
# Constants
# =============================================================================

# Default operad root directory
OPERADS_ROOT = Path.home() / ".kgents" / "operads"

# Portal link pattern: [edge_type] `OPERAD_NAME/operation` (optional note)
# Examples:
#   - [enables] `WITNESS_OPERAD/walk` (traverse marks)
#   - [feeds] `ASHC` (evidence for proof compilation)
#   - [triggered_by] `AGENT_OPERAD/branch` (records alternatives)
PORTAL_LINK_PATTERN = re.compile(
    r"^\s*-\s*\[(?P<edge_type>\w+)\]\s*`(?P<path>[^`]+)`(?:\s*\((?P<note>[^)]+)\))?\s*$"
)


# =============================================================================
# Types
# =============================================================================


class PortalState(Enum):
    """Portal token states."""

    COLLAPSED = "collapsed"
    LOADING = "loading"
    EXPANDED = "expanded"
    ERROR = "error"


class EdgeType(Enum):
    """Semantic edge types for portal links."""

    ENABLES = "enables"
    FEEDS = "feeds"
    REFINES = "refines"
    TRIGGERED_BY = "triggered_by"
    EXTENDS = "extends"
    CONFLICTS = "conflicts"
    RELATED = "related"


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class PortalLink:
    """
    A parsed portal link from a "Wires To" section.

    Example markdown:
        - [enables] `WITNESS_OPERAD/walk` (traverse marks)

    Parses to:
        PortalLink(
            edge_type="enables",
            path="WITNESS_OPERAD/walk",
            note="traverse marks"
        )
    """

    edge_type: str
    path: str  # e.g., "WITNESS_OPERAD/walk" or "ASHC"
    note: str | None = None

    @property
    def operad_name(self) -> str | None:
        """Extract operad name from path (e.g., 'WITNESS_OPERAD')."""
        if "/" in self.path:
            return self.path.split("/")[0]
        return None

    @property
    def operation_name(self) -> str | None:
        """Extract operation name from path (e.g., 'walk')."""
        if "/" in self.path:
            return self.path.split("/", 1)[1]
        return None

    @property
    def file_path(self) -> Path | None:
        """Resolve to filesystem path (e.g., ~/.kgents/operads/WITNESS_OPERAD/walk.op)."""
        if "/" not in self.path:
            # External reference (e.g., "ASHC")
            return None
        parts = self.path.split("/", 1)
        operad = parts[0]
        operation = parts[1]
        return OPERADS_ROOT / operad / f"{operation}.op"

    def exists(self) -> bool:
        """Check if the linked file exists."""
        fp = self.file_path
        return fp is not None and fp.exists()


@dataclass
class PortalToken:
    """
    A meaning token representing an expandable hyperedge.

    When COLLAPSED: Shows edge type and destination summary
    When EXPANDED: Renders destination document inline

    This is the UX projection of the typed-hypergraph.

    Implements: protocols.portal_protocol.PortalTokenProtocol
               protocols.portal_protocol.ExpandableTokenProtocol

    Teaching:
        gotcha: This class implements both PortalTokenProtocol and
                ExpandableTokenProtocol via structural typing. The properties
                'edge_type', 'path', and 'is_expanded' provide compliance.
                (Evidence: test_portal_protocol.py::test_file_operad_satisfies_protocol)
    """

    link: PortalLink
    state: PortalState = PortalState.COLLAPSED
    depth: int = 0

    # Lazy-loaded content
    _content: str | None = field(default=None, repr=False)
    _nested_links: list["PortalLink"] = field(default_factory=list, repr=False)
    _load_error: str | None = field(default=None, repr=False)

    # =========================================================================
    # PortalTokenProtocol Implementation (structural typing)
    # =========================================================================

    @property
    def edge_type(self) -> str:
        """
        The hyperedge type (protocol compliance).

        Delegates to link.edge_type.
        """
        return self.link.edge_type

    @property
    def path(self) -> str:
        """
        The destination path (protocol compliance).

        Delegates to link.path.
        """
        return self.link.path

    @property
    def is_expanded(self) -> bool:
        """
        Whether the portal is currently expanded (protocol compliance).

        True when state is EXPANDED.
        """
        return self.state == PortalState.EXPANDED

    def to_dict(self) -> dict[str, Any]:
        """
        JSON-serializable representation (protocol compliance).

        Returns:
            Dict with all portal state for API/frontend consumption
        """
        return {
            "edge_type": self.edge_type,  # Protocol field
            "path": self.path,  # Protocol field
            "is_expanded": self.is_expanded,  # Protocol field
            "depth": self.depth,
            "state": self.state.value,
            "link": {
                "edge_type": self.link.edge_type,
                "path": self.link.path,
                "note": self.link.note,
                "operad_name": self.link.operad_name,
                "operation_name": self.link.operation_name,
            },
            "has_content": self._content is not None,
            "error": self._load_error,
        }

    # =========================================================================
    # Original Properties
    # =========================================================================

    @property
    def content(self) -> str | None:
        """Get loaded content (None if not expanded)."""
        return self._content

    @property
    def nested_links(self) -> list["PortalLink"]:
        """Get nested portal links discovered in content."""
        return self._nested_links

    def load(self) -> bool:
        """
        Load the destination content.

        Returns True if successful, False otherwise.
        Sets state to EXPANDED on success, ERROR on failure.
        """
        self.state = PortalState.LOADING

        fp = self.link.file_path
        if fp is None:
            self._load_error = f"External reference: {self.link.path}"
            self.state = PortalState.ERROR
            return False

        if not fp.exists():
            self._load_error = f"File not found: {fp}"
            self.state = PortalState.ERROR
            return False

        try:
            self._content = fp.read_text()
            # Parse nested links
            self._nested_links = parse_wires_to(self._content)
            self.state = PortalState.EXPANDED
            return True
        except Exception as e:
            self._load_error = str(e)
            self.state = PortalState.ERROR
            return False

    def collapse(self) -> None:
        """Collapse this portal, hiding content."""
        self.state = PortalState.COLLAPSED
        # Keep content cached for quick re-expansion
        # self._content = None

    def render_collapsed(self) -> str:
        """Render collapsed state."""
        edge = self.link.edge_type
        path = self.link.path
        exists = "1 file" if self.link.exists() else "external"
        return f"\u25b6 [{edge}] {path} \u2500\u2500\u2192 {exists}"

    def render_expanded_header(self) -> str:
        """Render expanded header (before content)."""
        edge = self.link.edge_type
        path = self.link.path
        return f"\u25bc [{edge}] {path}"

    def render_error(self) -> str:
        """Render error state."""
        return f"\u2717 [{self.link.edge_type}] {self.link.path} \u2500 Error: {self._load_error}"


@dataclass
class PortalNode:
    """
    A node in the portal expansion tree.

    The tree structure IS the trail of exploration.
    """

    path: str
    edge_type: str | None = None  # None for root
    expanded: bool = False
    children: list["PortalNode"] = field(default_factory=list)
    depth: int = 0
    state: PortalState = PortalState.COLLAPSED
    content: str | None = None  # Loaded content when expanded
    error: str | None = None  # Error message if loading failed

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to JSON-compatible dict for frontend API.

        Matches the TypeScript PortalNode interface in web/src/api/portal.ts.

        Returns:
            Dict with: path, edge_type, expanded, children, depth, state, error, content
        """
        return {
            "path": self.path,
            "edge_type": self.edge_type,
            "expanded": self.expanded,
            "children": [child.to_dict() for child in self.children],
            "depth": self.depth,
            "state": self.state.value if self.state else "collapsed",
            "error": self.error,
            "content": self.content,
        }


class ExpandErrorCode(Enum):
    """Error codes for portal expansion failures."""

    PATH_NOT_FOUND = "path_not_found"
    DEPTH_LIMIT_REACHED = "depth_limit_reached"
    FILE_NOT_FOUND = "file_not_found"
    FILE_NOT_READABLE = "file_not_readable"
    NO_PORTALS_DISCOVERED = "no_portals_discovered"


@dataclass
class ExpandResult:
    """
    Structured result from portal expansion.

    Returns success/failure with sympathetic error messaging.

    Design: The error messages are written to be helpful, not accusatory.
    We explain what happened AND what the user can do about it.
    """

    success: bool
    error_code: ExpandErrorCode | None = None
    error_message: str | None = None
    suggestion: str | None = None
    depth: int = 0
    max_depth: int = 40

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable representation."""
        result: dict[str, Any] = {"success": self.success}
        if self.error_code:
            result["error_code"] = self.error_code.value
        if self.error_message:
            result["error_message"] = self.error_message
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if not self.success:
            result["depth"] = self.depth
            result["max_depth"] = self.max_depth
        return result

    @classmethod
    def ok(cls) -> "ExpandResult":
        """Expansion succeeded."""
        return cls(success=True)

    @classmethod
    def depth_limit(cls, current_depth: int, max_depth: int) -> "ExpandResult":
        """
        Expansion failed due to depth limit.

        This is the MOST IMPORTANT error to make clear - users need to know
        exactly when the depth limit is hit vs. other failures.
        """
        return cls(
            success=False,
            error_code=ExpandErrorCode.DEPTH_LIMIT_REACHED,
            error_message=(
                f"Reached maximum expansion depth ({max_depth} levels). "
                f"Current depth: {current_depth}."
            ),
            suggestion=(
                "This is a safety limit to prevent infinite expansion. "
                "You can try: (1) collapse some expanded portals to explore other branches, "
                "or (2) start from a different file closer to what you're looking for."
            ),
            depth=current_depth,
            max_depth=max_depth,
        )

    @classmethod
    def path_not_found(cls, portal_path: list[str]) -> "ExpandResult":
        """Path through the tree could not be found."""
        path_str = " → ".join(portal_path) if portal_path else "(empty path)"
        return cls(
            success=False,
            error_code=ExpandErrorCode.PATH_NOT_FOUND,
            error_message=f"Could not find the portal at: {path_str}",
            suggestion=(
                "The path might have changed, or you may need to expand parent nodes first. "
                "Try using 'available' to see which portals can be expanded."
            ),
        )

    @classmethod
    def file_not_found(cls, file_path: str) -> "ExpandResult":
        """Source file does not exist."""
        return cls(
            success=False,
            error_code=ExpandErrorCode.FILE_NOT_FOUND,
            error_message=f"File not found: {file_path}",
            suggestion=(
                "The file may have been moved, renamed, or deleted. "
                "Check if the file exists at the expected location."
            ),
        )

    @classmethod
    def file_not_readable(cls, file_path: str, error: str) -> "ExpandResult":
        """File exists but couldn't be read/parsed."""
        return cls(
            success=False,
            error_code=ExpandErrorCode.FILE_NOT_READABLE,
            error_message=f"Could not read file: {file_path}",
            suggestion=f"Error details: {error}. The file may have syntax errors or encoding issues.",
        )

    @classmethod
    def no_portals(cls, file_path: str) -> "ExpandResult":
        """File exists but has no discoverable portals."""
        return cls(
            success=False,
            error_code=ExpandErrorCode.NO_PORTALS_DISCOVERED,
            error_message=f"No portals discovered in: {file_path}",
            suggestion=(
                "This file has no imports, tests, or other connections we can discover. "
                "It may be a standalone utility or configuration file."
            ),
        )


@dataclass
class PortalTree:
    """
    The tree of expanded portals IS the agent's current view.

    Root: The starting document
    Children: Expanded portals within it
    Grandchildren: Portals expanded within those

    The tree structure IS the trail.
    """

    root: PortalNode
    max_depth: int = 40  # Allow deep exploration (was 5)

    # Track all tokens for state management
    tokens: dict[str, PortalToken] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to JSON-compatible dict for frontend API.

        Matches the TypeScript PortalTree interface in web/src/api/portal.ts.

        Returns:
            Dict with: root (PortalNode), max_depth
        """
        return {
            "root": self.root.to_dict(),
            "max_depth": self.max_depth,
        }

    def expand(self, portal_path: list[str]) -> ExpandResult:
        """
        Expand a portal at the given path.

        portal_path = ["tests", "covers"] means:
        - From root, expand "tests" portal
        - Within that, expand "covers" portal

        Returns:
            ExpandResult with success/failure and sympathetic error messages.

        Design: We return structured errors so the frontend/CLI can:
        1. Show the SPECIFIC reason for failure (not just "failed")
        2. Highlight depth limit separately (it's a feature, not a bug)
        3. Suggest what the user can do next
        """
        # Find the node to expand
        node = self._find_node(portal_path)
        if node is None:
            return ExpandResult.path_not_found(portal_path)

        # Check depth BEFORE attempting expansion - this makes the limit clear
        if node.depth >= self.max_depth:
            return ExpandResult.depth_limit(node.depth, self.max_depth)

        # For container nodes (e.g., edge type nodes in source portals),
        # just mark as expanded if they have children. These nodes don't
        # need tokens - they're just organizational containers.
        if node.children:
            node.expanded = True
            return ExpandResult.ok()

        # For leaf nodes that are Python files, analyze them to get their portals
        # This enables recursive portal expansion for source file trees
        if node.path.endswith(".py"):
            from pathlib import Path
            node_path = Path(node.path)
            original_path = node.path  # Keep for error messages

            # Try to find the file (might be relative to project root or parent dir)
            if not node_path.is_absolute() or not node_path.exists():
                resolved = None

                # Strategy 1: Direct from cwd and parents
                for base in [Path.cwd()] + list(Path.cwd().parents):
                    candidate = base / node.path
                    if candidate.exists():
                        resolved = candidate
                        break

                # Strategy 2: Find the parent file and look relative to it
                if resolved is None and self.root.path:
                    root_path = Path(self.root.path)
                    if not root_path.is_absolute():
                        for base in [Path.cwd()] + list(Path.cwd().parents):
                            if (base / root_path).exists():
                                root_path = base / root_path
                                break
                    if root_path.exists():
                        # Try same directory as root file
                        candidate = root_path.parent / node.path
                        if candidate.exists():
                            resolved = candidate

                if resolved:
                    node_path = resolved

            if not node_path.exists():
                return ExpandResult.file_not_found(original_path)

            try:
                from .file_analyzer import analyze_python_file

                portals = analyze_python_file(str(node_path))
                children = portals.to_portal_nodes(depth=node.depth + 1)

                # Update node with analysis results
                node.children = children
                node.expanded = True
                node.state = PortalState.EXPANDED
                return ExpandResult.ok()

            except Exception as e:
                return ExpandResult.file_not_readable(original_path, str(e))

        # Fallback: try token-based expansion (for .op files)
        token_key = "/".join(portal_path) if portal_path else self.root.path
        if token_key not in self.tokens:
            # Also try edge_type as key (source portals)
            if portal_path and portal_path[-1] in self.tokens:
                token_key = portal_path[-1]
            else:
                return ExpandResult.path_not_found(portal_path)

        token = self.tokens[token_key]
        if token.load():
            node.expanded = True
            return ExpandResult.ok()

        # Token failed to load - check for specific error
        if token._load_error:
            return ExpandResult.file_not_readable(token.link.path, token._load_error)
        return ExpandResult.path_not_found(portal_path)

    def collapse(self, portal_path: list[str]) -> bool:
        """Collapse a portal, hiding children."""
        node = self._find_node(portal_path)
        if node is None:
            return False

        token_key = "/".join(portal_path) if portal_path else self.root.path
        if token_key in self.tokens:
            self.tokens[token_key].collapse()

        node.expanded = False
        return True

    def _find_node(self, path: list[str]) -> PortalNode | None:
        """Find a node by path through the tree.

        Matches on path OR edge_type (for source portals where edge_type
        nodes have path="N items" but edge_type="tests").
        """
        if not path:
            return self.root

        current = self.root
        for segment in path:
            found = None
            for child in current.children:
                # Match on path OR edge_type (source portals use edge_type for navigation)
                if child.path == segment or child.edge_type == segment:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current

    def to_trail(self, name: str = "", created_by: str = "") -> "Trail":
        """
        Convert expansion tree to Trail artifact.

        DFS of expanded nodes = trail of exploration.
        The tree structure IS the trail.

        Args:
            name: Optional trail name
            created_by: Optional observer ID

        Returns:
            Trail with steps for each expanded node in DFS order
        """
        from protocols.exploration.types import Trail, TrailStep

        steps: list[TrailStep] = []

        def dfs(node: PortalNode) -> None:
            """Depth-first traversal, collecting expanded nodes."""
            step = TrailStep(
                node=node.path,
                edge_taken=node.edge_type,
            )
            steps.append(step)

            # Only recurse into expanded nodes
            if node.expanded:
                for child in node.children:
                    dfs(child)

        dfs(self.root)
        return Trail(
            name=name,
            created_by=created_by,
            steps=tuple(steps),
        )

    def render(self, max_depth: int | None = None) -> str:
        """
        Render full tree as nested collapsible structure.

        Uses box-drawing characters for CLI output.
        Shows expand/collapse state with triangle markers.

        Args:
            max_depth: Maximum depth to render (None uses self.max_depth)

        Returns:
            Formatted string with tree structure
        """
        depth_limit = max_depth if max_depth is not None else self.max_depth
        lines: list[str] = []

        def render_node(
            node: PortalNode,
            prefix: str = "",
            is_last: bool = True,
        ) -> None:
            """Recursively render a node and its children."""
            if node.depth > depth_limit:
                return

            # Box-drawing connectors
            connector = "\u2514\u2500" if is_last else "\u251c\u2500"
            expand_marker = "\u25bc" if node.expanded else "\u25b6"

            # Render this node
            if node.edge_type:
                # Child node with edge type
                lines.append(f"{prefix}{connector} {expand_marker} [{node.edge_type}] {node.path}")
            else:
                # Root node (no edge type)
                lines.append(f"{prefix}{node.path}")

            # Recurse into children if expanded
            if node.expanded:
                child_prefix = prefix + ("   " if is_last else "\u2502  ")
                for i, child in enumerate(node.children):
                    render_node(child, child_prefix, i == len(node.children) - 1)

        render_node(self.root)
        return "\n".join(lines)

    @classmethod
    def from_file(
        cls,
        path: Path | str,
        max_depth: int = 5,
        expand_all: bool = True,
    ) -> "PortalTree":
        """
        Build a PortalTree from an .op file.

        Parses the file, discovers portal links, and optionally expands them.

        Args:
            path: Path to the .op file
            max_depth: Maximum expansion depth
            expand_all: If True, expand all portals up to max_depth

        Returns:
            PortalTree rooted at the given file

        Example:
            tree = PortalTree.from_file("~/.kgents/operads/WITNESS_OPERAD/mark.op")
            print(tree.render())
        """
        path = Path(path)
        root = PortalNode(path=str(path), depth=0)
        tree = cls(root=root, max_depth=max_depth)

        if not path.exists():
            return tree

        content = path.read_text()
        links = parse_wires_to(content)

        # Create child nodes for each link
        for link in links:
            child = PortalNode(
                path=link.path,
                edge_type=link.edge_type,
                depth=1,
            )
            root.children.append(child)

            # Register token
            tree.tokens[link.path] = PortalToken(link, depth=1)

            # Optionally expand
            if expand_all and link.exists():
                tree._expand_recursive(child, link.file_path, current_depth=1)

        if expand_all and links:
            root.expanded = True

        return tree

    def _expand_recursive(
        self,
        node: PortalNode,
        file_path: Path | None,
        current_depth: int,
    ) -> None:
        """Recursively expand a node and its children."""
        if file_path is None or not file_path.exists():
            return

        if current_depth >= self.max_depth:
            return

        # Load content and mark expanded
        token = self.tokens.get(node.path)
        if token:
            token.load()
            node.expanded = True

        # Parse child links
        content = file_path.read_text()
        links = parse_wires_to(content)

        for link in links:
            child = PortalNode(
                path=link.path,
                edge_type=link.edge_type,
                depth=current_depth + 1,
            )
            node.children.append(child)

            # Register token with unique key
            token_key = f"{node.path}/{link.path}"
            self.tokens[token_key] = PortalToken(link, depth=current_depth + 1)

            # Recurse if exists
            if link.exists() and link.file_path:
                self._expand_recursive(child, link.file_path, current_depth + 1)


# =============================================================================
# Parsing
# =============================================================================


def parse_portal_link(line: str) -> PortalLink | None:
    """
    Parse a single portal link from a markdown line.

    Example:
        "- [enables] `WITNESS_OPERAD/walk` (traverse marks)"
        -> PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk", note="traverse marks")
    """
    match = PORTAL_LINK_PATTERN.match(line)
    if not match:
        return None

    return PortalLink(
        edge_type=match.group("edge_type"),
        path=match.group("path"),
        note=match.group("note"),
    )


def parse_wires_to(content: str) -> list[PortalLink]:
    """
    Parse all portal links from the "Wires To" section of an .op file.

    Returns list of PortalLink objects.
    """
    links: list[PortalLink] = []
    in_wires_section = False

    for line in content.splitlines():
        stripped = line.strip()

        # Detect "## Wires To" section
        if stripped.startswith("## Wires To"):
            in_wires_section = True
            continue

        # Exit section on next heading
        if in_wires_section and stripped.startswith("## "):
            break

        # Parse links in section
        if in_wires_section:
            link = parse_portal_link(line)
            if link:
                links.append(link)

    return links


# =============================================================================
# Rendering
# =============================================================================


class PortalRenderer:
    """
    Renders the portal tree for different projection surfaces.

    Supports:
    - CLI: Unicode box-drawing, collapsible
    - Markdown: Nested blockquotes
    - LLM: XML-style with metadata
    """

    # Box drawing characters
    BOX_VERTICAL = "\u2502"
    BOX_CORNER = "\u2514"
    BOX_TEE = "\u251c"
    BOX_HORIZONTAL = "\u2500"

    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size

    def render_cli(
        self,
        token: PortalToken,
        show_nested: bool = True,
        max_lines: int | None = None,
    ) -> str:
        """
        Render a portal token for CLI output.

        Returns a formatted string with box-drawing characters.
        """
        if token.state == PortalState.COLLAPSED:
            return token.render_collapsed()

        if token.state == PortalState.ERROR:
            return token.render_error()

        if token.state != PortalState.EXPANDED:
            return f"[{token.state.value}] {token.link.path}"

        # Expanded state
        lines = [token.render_expanded_header()]

        # Draw content box
        content = token.content or ""
        content_lines = content.splitlines()

        if max_lines and len(content_lines) > max_lines:
            content_lines = content_lines[:max_lines]
            content_lines.append(f"... ({len(content.splitlines()) - max_lines} more lines)")

        # Add box around content
        indent = " " * (self.indent_size * (token.depth + 1))
        box_indent = " " * (self.indent_size * token.depth)

        lines.append(f"{box_indent}\u250c" + "\u2500" * 60)
        for cl in content_lines:
            lines.append(f"{box_indent}\u2502 {cl}")
        lines.append(f"{box_indent}\u2514" + "\u2500" * 60)

        # Render nested portals if any
        if show_nested and token.nested_links:
            lines.append("")
            lines.append(f"{indent}Nested portals ({len(token.nested_links)}):")
            for link in token.nested_links:
                nested_token = PortalToken(link, depth=token.depth + 1)
                lines.append(f"{indent}  {nested_token.render_collapsed()}")

        return "\n".join(lines)

    def render_markdown(self, token: PortalToken) -> str:
        """Render for markdown output (nested blockquotes)."""
        if token.state == PortalState.COLLAPSED:
            return f"> {token.render_collapsed()}"

        if token.state != PortalState.EXPANDED:
            return f"> {token.render_error()}"

        # Expanded
        lines = [f"> {token.render_expanded_header()}"]
        for line in (token.content or "").splitlines():
            lines.append(f"> > {line}")
        return "\n".join(lines)

    def render_llm(self, token: PortalToken) -> str:
        """Render for LLM context (XML-style with metadata)."""
        if token.state != PortalState.EXPANDED:
            return f"<!-- PORTAL: {token.link.path} ({token.state.value}) -->"

        return f"""<!-- PORTAL: {token.link.edge_type} → {token.link.path} (EXPANDED, depth={token.depth}) -->
<file path="{token.link.file_path}">
{token.content}
</file>
<!-- END PORTAL -->"""

    def render_html(
        self,
        token: PortalToken,
        lazy_load: bool = True,
        max_lines: int | None = None,
    ) -> str:
        """
        Render a portal token as HTML with <details> element.

        Uses semantic HTML for collapsible content:
        - <details> for collapse/expand behavior
        - data-* attributes for JS integration
        - Lazy loading support via empty content div

        From spec/protocols/portal-token.md section 8.2:
            <details data-portal-path="..." data-edge-type="..." data-depth="...">
                <summary>▶ [tests] ──→ 3 files</summary>
                <div class="portal-content">
                    <!-- Lazy loaded -->
                </div>
            </details>

        Args:
            token: The portal token to render
            lazy_load: If True, content is not included (for JS fetching)
            max_lines: Maximum lines to include when not lazy loading

        Returns:
            HTML string with <details> element
        """
        import html

        portal_path = html.escape(token.link.path)
        edge_type = html.escape(token.link.edge_type)
        state = token.state.value

        # Build data attributes
        data_attrs = (
            f'data-portal-path="{portal_path}" '
            f'data-edge-type="{edge_type}" '
            f'data-depth="{token.depth}" '
            f'data-state="{state}"'
        )

        # Determine open state
        open_attr = " open" if token.state == PortalState.EXPANDED else ""

        if token.state == PortalState.COLLAPSED:
            # Collapsed: show summary with expand affordance
            summary = html.escape(token.render_collapsed())
            return f"""<details {data_attrs}{open_attr}>
    <summary>{summary}</summary>
    <div class="portal-content portal-loading">
        <!-- Content loaded on expand -->
    </div>
</details>"""

        elif token.state == PortalState.ERROR:
            # Error state
            error_msg = html.escape(token._load_error or "Unknown error")
            return f"""<details {data_attrs} class="portal-error">
    <summary>✗ [{edge_type}] {portal_path} — Error</summary>
    <div class="portal-content portal-error-content">
        <span class="error-message">{error_msg}</span>
    </div>
</details>"""

        elif token.state == PortalState.LOADING:
            # Loading state
            summary = f"⏳ [{edge_type}] {portal_path}"
            return f"""<details {data_attrs}{open_attr} class="portal-loading">
    <summary>{summary}</summary>
    <div class="portal-content">
        <span class="loading-spinner">Loading...</span>
    </div>
</details>"""

        else:
            # Expanded state
            summary = html.escape(token.render_expanded_header())

            if lazy_load:
                # Lazy load: content will be fetched via JS
                content_div = '<div class="portal-content portal-lazy"></div>'
            else:
                # Render content inline
                content = token.content or ""
                if max_lines:
                    lines = content.splitlines()
                    if len(lines) > max_lines:
                        content = "\n".join(lines[:max_lines])
                        content += f"\n... ({len(lines) - max_lines} more lines)"

                escaped_content = html.escape(content)
                # Preserve whitespace and line breaks
                content_html = f'<pre class="portal-file-content">{escaped_content}</pre>'

                # Render nested portals if any
                nested_html = ""
                if token.nested_links:
                    nested_items = []
                    for nested_link in token.nested_links:
                        nested_token = PortalToken(nested_link, depth=token.depth + 1)
                        nested_items.append(
                            f'<li>{self.render_html(nested_token, lazy_load=True)}</li>'
                        )
                    if nested_items:
                        nested_html = (
                            '<ul class="portal-nested-links">'
                            + "".join(nested_items)
                            + "</ul>"
                        )

                content_div = f'<div class="portal-content">{content_html}{nested_html}</div>'

            return f"""<details {data_attrs}{open_attr}>
    <summary>{summary}</summary>
    {content_div}
</details>"""

    def render_tree_html(
        self,
        tree: "PortalTree",
        lazy_load: bool = True,
    ) -> str:
        """
        Render an entire PortalTree as nested HTML.

        Args:
            tree: The portal tree to render
            lazy_load: If True, unexpanded portals have empty content

        Returns:
            HTML string with nested <details> elements
        """
        import html

        def render_node(node: "PortalNode", depth: int = 0) -> str:
            """Recursively render a node and its children."""
            # Get token if exists
            token_key = node.path
            token = tree.tokens.get(token_key)

            if token:
                # Render via token
                node_html = self.render_html(token, lazy_load=lazy_load)
            else:
                # Render basic node
                escaped_path = html.escape(node.path)
                edge = html.escape(node.edge_type or "")
                marker = "▼" if node.expanded else "▶"

                if node.edge_type:
                    summary = f"{marker} [{edge}] {escaped_path}"
                else:
                    summary = escaped_path

                open_attr = " open" if node.expanded else ""
                node_html = f"""<details data-depth="{depth}"{open_attr}>
    <summary>{summary}</summary>
    <div class="portal-content"></div>
</details>"""

            # If expanded, render children
            if node.expanded and node.children:
                children_html = "\n".join(
                    render_node(child, depth + 1) for child in node.children
                )
                # Insert children into the content div
                # This is a simplified approach - real impl would be more sophisticated
                return node_html.replace(
                    '<div class="portal-content"></div>',
                    f'<div class="portal-content">{children_html}</div>',
                )

            return node_html

        return render_node(tree.root)


# =============================================================================
# Interactive Expansion
# =============================================================================


@dataclass
class PortalOpenSignal:
    """
    Signal emitted when a portal expands.

    Tells the system:
    1. Which file(s) are now "open"
    2. The edge type that led here
    3. The nesting depth
    4. The parent context
    """

    paths_opened: list[str]
    edge_type: str
    parent_path: str
    depth: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_context_event(self) -> "ContextEvent":
        """
        Convert this signal to a ContextEvent for agent context updates.

        The ContextEvent updates the agent's understanding of what files
        are currently "open" or in focus.

        Returns:
            ContextEvent with type="files_opened"
        """
        from .context_bridge import ContextEvent

        return ContextEvent.from_portal_signal(self)


def interactive_expand(
    content: str,
    on_expand: "Callable[[PortalOpenSignal], None] | None" = None,
    max_depth: int = 5,
) -> str:
    """
    Interactively expand portal tokens in content.

    This is the main entry point for portal expansion.

    Args:
        content: The .op file content
        on_expand: Callback when a portal expands (for trail/evidence)
        max_depth: Maximum expansion depth

    Returns:
        Content with expanded portals rendered inline
    """
    links = parse_wires_to(content)
    if not links:
        return content

    renderer = PortalRenderer()
    expanded_sections = []

    for link in links:
        token = PortalToken(link)
        if token.load():
            if on_expand:
                signal = PortalOpenSignal(
                    paths_opened=[str(link.file_path)] if link.file_path else [link.path],
                    edge_type=link.edge_type,
                    parent_path="root",
                    depth=0,
                )
                on_expand(signal)

            expanded_sections.append(renderer.render_cli(token, max_lines=30))
        else:
            expanded_sections.append(token.render_error())

    return "\n\n".join(expanded_sections)


# =============================================================================
# Convenience Functions
# =============================================================================


def expand_file(path: Path | str, max_depth: int = 5) -> str:
    """
    Expand all portal tokens in a file.

    Args:
        path: Path to .op file
        max_depth: Maximum expansion depth

    Returns:
        Rendered content with expansions
    """
    path = Path(path)
    if not path.exists():
        return f"Error: File not found: {path}"

    content = path.read_text()
    return interactive_expand(content, max_depth=max_depth)


def show_portals(path: Path | str) -> list[PortalLink]:
    """
    List all portal links in a file without expanding.

    Args:
        path: Path to .op file

    Returns:
        List of PortalLink objects
    """
    path = Path(path)
    if not path.exists():
        return []

    content = path.read_text()
    return parse_wires_to(content)


__all__ = [
    "PortalState",
    "EdgeType",
    "PortalLink",
    "PortalToken",
    "PortalNode",
    "PortalTree",
    "PortalRenderer",
    "PortalOpenSignal",
    "ExpandErrorCode",
    "ExpandResult",
    "parse_portal_link",
    "parse_wires_to",
    "interactive_expand",
    "expand_file",
    "show_portals",
    "OPERADS_ROOT",
]
