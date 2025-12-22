"""
Source Portal Discovery: Extend Portal Tokens to Source Files.

"Portal tokens should work on real code, not just .op files."

This module bridges the gap between:
- The FILE_OPERAD portal tokens (for .op files)
- The hyperedge resolvers (for actual source code)

The key insight: hyperedge resolvers ALREADY exist for imports, tests, calls, etc.
This module wraps them to produce portal tokens for any source file.

See: spec/protocols/portal-token.md Phase 4
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from .portal import (
    PortalLink,
    PortalNode,
    PortalState,
    PortalToken,
    PortalTree,
)

if TYPE_CHECKING:
    from protocols.agentese.contexts.self_context import ContextNode
    from protocols.agentese.node import Observer


# =============================================================================
# Constants
# =============================================================================

# Supported file extensions for source portal discovery
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".md"}

# Edge types we can discover from source files
SOURCE_EDGE_TYPES = {
    "imports",      # What this file imports
    "tests",        # Test files for this module
    "implements",   # Specs this implements
    "contains",     # Submodules/children
    "calls",        # Functions called by this module
    "related",      # Sibling modules
}


# =============================================================================
# Source Portal Link (extends PortalLink for source files)
# =============================================================================


@dataclass
class SourcePortalLink(PortalLink):
    """
    A PortalLink that represents a hyperedge from a source file.

    Extends PortalLink with:
    - file_type: The type of source file (python, typescript, markdown)
    - source_file: The file this link was discovered from
    - context_node: Optional ContextNode for lazy resolution
    """

    file_type: str = "python"
    source_file: Path | None = None
    context_node: "ContextNode | None" = field(default=None, repr=False)

    @classmethod
    def from_hyperedge(
        cls,
        edge_type: str,
        destination: "ContextNode",
        source_file: Path | None = None,
    ) -> "SourcePortalLink":
        """
        Create a SourcePortalLink from a hyperedge resolution.

        This is the bridge between:
        - Hyperedge resolvers (return ContextNodes)
        - Portal tokens (use PortalLinks)

        Args:
            edge_type: The type of edge (imports, tests, calls, etc.)
            destination: The ContextNode destination
            source_file: The source file this link was discovered from

        Returns:
            A SourcePortalLink ready for portal token creation
        """
        # Determine file type from source file
        file_type = "python"
        if source_file:
            ext = source_file.suffix.lower()
            if ext in {".ts", ".tsx"}:
                file_type = "typescript"
            elif ext in {".js", ".jsx"}:
                file_type = "javascript"
            elif ext == ".md":
                file_type = "markdown"

        return cls(
            edge_type=edge_type,
            path=destination.path,
            note=f"from {source_file.name}" if source_file else None,
            file_type=file_type,
            source_file=source_file,
            context_node=destination,
        )

    @property
    def file_path(self) -> Path | None:
        """
        Resolve to filesystem path.

        For source portals, we need to resolve the AGENTESE path
        back to a file path using the hyperedge resolver utilities.
        """
        if self.context_node is None:
            return None

        # Use hyperedge resolver path utilities
        from protocols.agentese.contexts.hyperedge_resolvers import (
            agentese_path_to_file,
            _get_project_root,
        )

        return agentese_path_to_file(self.path, _get_project_root())

    def exists(self) -> bool:
        """Check if the linked file exists."""
        fp = self.file_path
        return fp is not None and fp.exists()


# =============================================================================
# Source Portal Discovery
# =============================================================================


@dataclass
class SourcePortalDiscovery:
    """
    Discovers portal links from source files using hyperedge resolvers.

    This is the main integration point between:
    - Source files (.py, .ts, .md)
    - Hyperedge resolvers (imports, tests, calls, etc.)
    - Portal tokens (expandable UI elements)

    Usage:
        discovery = SourcePortalDiscovery()
        links = await discovery.discover_portals(Path("my_module.py"))

    Teaching:
        gotcha: This class is ASYNC because hyperedge resolvers are async.
                Always await discover_portals().
                (Evidence: test_source_portals.py::test_discovery_async)
    """

    project_root: Path | None = None

    def __post_init__(self) -> None:
        """Initialize project root if not provided."""
        if self.project_root is None:
            from protocols.agentese.contexts.hyperedge_resolvers import (
                _get_project_root,
            )
            self.project_root = _get_project_root()

    async def discover_portals(
        self,
        file_path: Path,
        edge_types: set[str] | None = None,
        observer: "Observer | None" = None,
    ) -> list[SourcePortalLink]:
        """
        Discover portal links from a source file.

        Args:
            file_path: Path to the source file
            edge_types: Edge types to discover (default: all SOURCE_EDGE_TYPES)
            observer: Optional observer for visibility filtering

        Returns:
            List of SourcePortalLink objects for discovered edges

        Example:
            discovery = SourcePortalDiscovery()
            links = await discovery.discover_portals(
                Path("impl/claude/services/brain/core.py")
            )
            # Returns: [
            #   SourcePortalLink(edge_type="imports", path="world.pathlib", ...),
            #   SourcePortalLink(edge_type="tests", path="world.brain.test_core", ...),
            # ]
        """
        if not file_path.exists():
            return []

        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            return []

        # Get edge types to discover
        types_to_check = edge_types or SOURCE_EDGE_TYPES

        # Convert file path to ContextNode
        from protocols.agentese.contexts.hyperedge_resolvers import (
            file_to_agentese_path,
            resolve_hyperedge,
            _get_project_root,
        )
        from protocols.agentese.contexts.self_context import ContextNode

        # Ensure we have a valid project root
        project_root = self.project_root or _get_project_root()

        agentese_path = file_to_agentese_path(file_path, project_root)
        node = ContextNode(
            path=agentese_path,
            holon=file_path.stem,
        )

        # Get visible edges for observer
        if observer:
            visible_edges = set(node.edges(observer))
            types_to_check = types_to_check & visible_edges

        # Resolve each edge type
        links: list[SourcePortalLink] = []
        for edge_type in types_to_check:
            destinations = await resolve_hyperedge(
                node, edge_type, project_root
            )
            for dest in destinations:
                link = SourcePortalLink.from_hyperedge(
                    edge_type=edge_type,
                    destination=dest,
                    source_file=file_path,
                )
                links.append(link)

        return links

    async def discover_python_imports(
        self,
        file_path: Path,
    ) -> list[SourcePortalLink]:
        """
        Discover import portals specifically for Python files.

        Uses AST parsing to find import statements.
        More efficient than full discovery when only imports are needed.
        """
        if file_path.suffix != ".py" or not file_path.exists():
            return []

        links: list[SourcePortalLink] = []

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for stmt in ast.walk(tree):
                if isinstance(stmt, ast.Import):
                    for alias in stmt.names:
                        from protocols.agentese.contexts.self_context import (
                            ContextNode,
                        )
                        dest = ContextNode(
                            path=f"world.{alias.name}",
                            holon=alias.name.split(".")[-1],
                        )
                        links.append(
                            SourcePortalLink.from_hyperedge(
                                edge_type="imports",
                                destination=dest,
                                source_file=file_path,
                            )
                        )
                elif isinstance(stmt, ast.ImportFrom):
                    if stmt.module:
                        from protocols.agentese.contexts.self_context import (
                            ContextNode,
                        )
                        dest = ContextNode(
                            path=f"world.{stmt.module}",
                            holon=stmt.module.split(".")[-1],
                        )
                        links.append(
                            SourcePortalLink.from_hyperedge(
                                edge_type="imports",
                                destination=dest,
                                source_file=file_path,
                            )
                        )
        except (SyntaxError, OSError):
            pass

        return links

    async def find_test_files(
        self,
        file_path: Path,
    ) -> list[SourcePortalLink]:
        """
        Find test files for a source module.

        Naming conventions checked:
        - foo.py → _tests/test_foo.py
        - foo.py → tests/test_foo.py
        - foo/ → foo/_tests/
        """
        return await self.discover_portals(
            file_path,
            edge_types={"tests"},
        )

    async def find_implementing_specs(
        self,
        file_path: Path,
    ) -> list[SourcePortalLink]:
        """
        Find spec files this module implements.

        Checks:
        - Docstring "Spec:" references
        - Naming patterns (foo.py → spec/foo.md)
        """
        return await self.discover_portals(
            file_path,
            edge_types={"implements"},
        )


# =============================================================================
# Source Portal Tree
# =============================================================================


async def build_source_portal_tree(
    file_path: Path,
    observer: "Observer | None" = None,
    max_depth: int = 5,
    expand_all: bool = False,
) -> PortalTree:
    """
    Build a PortalTree from a source file.

    This is the main entry point for source file portal expansion.

    Args:
        file_path: Path to the source file
        observer: Optional observer for visibility filtering
        max_depth: Maximum expansion depth
        expand_all: Whether to expand all portals immediately

    Returns:
        A PortalTree rooted at the source file

    Example:
        tree = await build_source_portal_tree(
            Path("impl/claude/services/brain/core.py")
        )
        print(tree.render())
        # Output:
        # impl/claude/services/brain/core.py
        # └─ ▶ [imports] ──→ 5 modules
        # └─ ▶ [tests] ──→ 1 file
        # └─ ▶ [implements] ──→ brain-spec.md
    """
    discovery = SourcePortalDiscovery()
    links = await discovery.discover_portals(file_path, observer=observer)

    # Create root node
    root = PortalNode(
        path=str(file_path),
        depth=0,
    )

    # Create tree
    tree = PortalTree(root=root, max_depth=max_depth)

    # Group links by edge type for better display
    links_by_type: dict[str, list[SourcePortalLink]] = {}
    for link in links:
        links_by_type.setdefault(link.edge_type, []).append(link)

    # Create child nodes for each edge type group
    for edge_type, type_links in links_by_type.items():
        # Create a summary node for this edge type
        child = PortalNode(
            path=f"{len(type_links)} items",
            edge_type=edge_type,
            depth=1,
        )
        root.children.append(child)

        # Create individual destination nodes
        for link in type_links:
            dest_node = PortalNode(
                path=link.path,
                edge_type=None,  # Sub-item, no edge type display
                depth=2,
            )
            child.children.append(dest_node)

            # Register token for this destination
            token = SourcePortalToken(link, depth=2)
            tree.tokens[link.path] = token

        # Register summary token
        summary_token = create_summary_token(edge_type, type_links)
        tree.tokens[f"{edge_type}_summary"] = summary_token

    if expand_all:
        root.expanded = True
        for child in root.children:
            child.expanded = True

    return tree


# =============================================================================
# Source Portal Token (extends PortalToken for source files)
# =============================================================================


@dataclass
class SourcePortalToken(PortalToken):
    """
    A PortalToken backed by a source file.

    Extends PortalToken with source-file-aware loading.
    """

    link: SourcePortalLink = field(default_factory=lambda: SourcePortalLink(
        edge_type="unknown",
        path="unknown",
    ))

    def load(self) -> bool:
        """
        Load the destination content.

        For source files, resolves the AGENTESE path to a file
        and loads the content.
        """
        self.state = PortalState.LOADING

        fp = self.link.file_path
        if fp is None:
            self._load_error = f"Cannot resolve path: {self.link.path}"
            self.state = PortalState.ERROR
            return False

        if not fp.exists():
            self._load_error = f"File not found: {fp}"
            self.state = PortalState.ERROR
            return False

        try:
            self._content = fp.read_text()
            self.state = PortalState.EXPANDED
            return True
        except Exception as e:
            self._load_error = str(e)
            self.state = PortalState.ERROR
            return False


def create_summary_token(
    edge_type: str,
    links: list[SourcePortalLink],
) -> PortalToken:
    """
    Create a summary token for a group of links.

    Used when multiple destinations share an edge type.
    """
    count = len(links)
    noun = "item" if count == 1 else "items"

    summary_link = PortalLink(
        edge_type=edge_type,
        path=f"{count} {noun}",
        note=None,
    )

    return PortalToken(summary_link, depth=0)


# =============================================================================
# Convenience Functions
# =============================================================================


async def discover_portals(
    file_path: Path | str,
    observer: "Observer | None" = None,
) -> list[SourcePortalLink]:
    """
    Discover portal links from a source file.

    This is the main entry point for source portal discovery.

    Args:
        file_path: Path to the source file
        observer: Optional observer for visibility filtering

    Returns:
        List of SourcePortalLink objects

    Example:
        links = await discover_portals("impl/claude/services/brain/core.py")
        for link in links:
            print(f"[{link.edge_type}] → {link.path}")
    """
    discovery = SourcePortalDiscovery()
    return await discovery.discover_portals(Path(file_path), observer=observer)


def render_portals_cli(links: list[SourcePortalLink]) -> str:
    """
    Render portal links for CLI output.

    Args:
        links: List of SourcePortalLink objects

    Returns:
        Formatted string for CLI display
    """
    if not links:
        return "No portals discovered."

    lines = []

    # Group by edge type
    by_type: dict[str, list[SourcePortalLink]] = {}
    for link in links:
        by_type.setdefault(link.edge_type, []).append(link)

    for edge_type, type_links in sorted(by_type.items()):
        count = len(type_links)
        noun = "file" if count == 1 else "files"
        lines.append(f"▶ [{edge_type}] ──→ {count} {noun}")
        for link in type_links[:5]:  # Show first 5
            exists = "✓" if link.exists() else "✗"
            lines.append(f"   {exists} {link.path}")
        if len(type_links) > 5:
            lines.append(f"   ... and {len(type_links) - 5} more")

    return "\n".join(lines)


__all__ = [
    "SUPPORTED_EXTENSIONS",
    "SOURCE_EDGE_TYPES",
    "SourcePortalLink",
    "SourcePortalDiscovery",
    "SourcePortalToken",
    "build_source_portal_tree",
    "discover_portals",
    "render_portals_cli",
    "create_summary_token",
]
