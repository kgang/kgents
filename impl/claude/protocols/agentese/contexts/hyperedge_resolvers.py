"""
Hyperedge Resolvers for the Typed-Hypergraph.

This module provides the actual logic for resolving hyperedges—
finding the nodes connected by each edge type.

Each resolver is a function that takes a source node and returns
a list of destination nodes. Resolvers are observer-independent;
the filtering happens in ContextNode.edges().

Spec: spec/protocols/typed-hypergraph.md §4

Teaching:
    gotcha: Resolvers are async because they may need to read files,
            query databases, or compute embeddings. Always await them.
            (Evidence: test_hyperedge_resolvers.py::test_resolver_async)

    gotcha: Resolvers return ContextNode instances, not paths. This enables
            lazy content loading and preserves the hypergraph structure.
            (Evidence: test_hyperedge_resolvers.py::test_resolver_returns_nodes)
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable

if TYPE_CHECKING:
    from .self_context import ContextNode

# Type alias for resolver functions
HyperedgeResolver = Callable[["ContextNode", Path], Awaitable[list["ContextNode"]]]


# === Project Root Discovery ===

_PROJECT_ROOT: Path | None = None


def _get_project_root() -> Path:
    """
    Get the project root, cached for performance.

    Discovery pattern follows kgents idiom (see conftest.py).
    This module is at: impl/claude/protocols/agentese/contexts/hyperedge_resolvers.py
    Project root is 6 levels up:
        contexts/ → agentese/ → protocols/ → claude/ → impl/ → kgents/

    Teaching:
        gotcha: This returns the kgents repo root, not impl/claude.
                Resolvers need the repo root to find spec/, services/, etc.
                (Evidence: test_hyperedge_resolvers.py::test_project_root_discovery)
    """
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        # impl/claude/protocols/agentese/contexts/hyperedge_resolvers.py → kgents/
        # .parent = contexts/, .parent.parent = agentese/, etc.
        _PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
    return _PROJECT_ROOT


def _set_project_root(root: Path | None) -> None:
    """
    Set project root for testing.

    Teaching:
        gotcha: Use this in tests to inject a temp directory.
                Remember to reset to None after the test!
                (Evidence: test_hyperedge_resolvers.py::test_with_temp_project)
    """
    global _PROJECT_ROOT
    _PROJECT_ROOT = root


# === Resolver Registry ===


@dataclass
class ResolverRegistry:
    """
    Registry of hyperedge resolvers.

    Resolvers are registered by edge type and can be looked up
    to find connections for any node.

    Teaching:
        gotcha: Resolvers are registered globally at import time.
                Use @register_resolver decorator or register() method.
                (Evidence: test_hyperedge_resolvers.py::test_resolver_registration)
    """

    _resolvers: dict[str, HyperedgeResolver] = field(default_factory=dict)
    _reverse_map: dict[str, str] = field(default_factory=dict)

    def register(
        self,
        edge_type: str,
        resolver: HyperedgeResolver,
        reverse_edge: str | None = None,
    ) -> None:
        """Register a resolver for an edge type."""
        self._resolvers[edge_type] = resolver
        if reverse_edge:
            self._reverse_map[edge_type] = reverse_edge
            self._reverse_map[reverse_edge] = edge_type

    def get(self, edge_type: str) -> HyperedgeResolver | None:
        """Get resolver for an edge type."""
        return self._resolvers.get(edge_type)

    def get_reverse(self, edge_type: str) -> str | None:
        """Get reverse edge type."""
        return self._reverse_map.get(edge_type)

    def list_edge_types(self) -> list[str]:
        """List all registered edge types."""
        return list(self._resolvers.keys())


# Global registry
_registry = ResolverRegistry()


def get_resolver_registry() -> ResolverRegistry:
    """Get the global resolver registry."""
    return _registry


def register_resolver(
    edge_type: str,
    reverse_edge: str | None = None,
) -> Callable[[HyperedgeResolver], HyperedgeResolver]:
    """
    Decorator to register a hyperedge resolver.

    Usage:
        @register_resolver("tests", reverse_edge="tested_by")
        async def resolve_tests(node: ContextNode, root: Path) -> list[ContextNode]:
            ...
    """

    def decorator(fn: HyperedgeResolver) -> HyperedgeResolver:
        _registry.register(edge_type, fn, reverse_edge)
        return fn

    return decorator


# === Path Utilities ===


def agentese_path_to_file(path: str, root: Path) -> Path | None:
    """
    Convert an AGENTESE path to a file path.

    world.auth_middleware → impl/claude/services/auth/middleware.py (or similar)
    brain → impl/claude/services/brain/node.py (shorthand)

    Returns None if no file mapping exists.

    Teaching:
        gotcha: The impl/claude/ prefix is required for resolution. All kgents
                Python code lives under impl/claude/, not at the repo root.
                (Evidence: test_hyperedge_resolvers.py::test_path_resolution_with_impl)
    """
    # Normalize path - strip world. prefix if present
    if path.startswith("world."):
        file_path = path[6:]
    else:
        file_path = path

    # The impl_root is where all Python code lives
    impl_root = root / "impl" / "claude"

    # Try common patterns - ordered by specificity
    patterns = [
        # Services: brain → services/brain/node.py (AGENTESE node)
        impl_root / "services" / file_path.replace(".", "/") / "node.py",
        # Services: brain → services/brain/core.py
        impl_root / "services" / file_path.replace(".", "/") / "core.py",
        # Services: brain → services/brain/__init__.py
        impl_root / "services" / file_path.replace(".", "/") / "__init__.py",
        # Services nested: brain.persistence → services/brain/persistence.py
        impl_root / "services" / f"{file_path.replace('.', '/')}.py",
        # Protocols: agentese → protocols/agentese/__init__.py
        impl_root / "protocols" / file_path.replace(".", "/") / "__init__.py",
        # Protocols nested: agentese.parser → protocols/agentese/parser.py
        impl_root / "protocols" / f"{file_path.replace('.', '/')}.py",
        # Agents: poly → agents/poly/__init__.py
        impl_root / "agents" / file_path.replace(".", "/") / "__init__.py",
        # Agents nested: poly.core → agents/poly/core.py
        impl_root / "agents" / f"{file_path.replace('.', '/')}.py",
        # Direct module at impl root: foo → foo.py
        impl_root / f"{file_path.replace('.', '/')}.py",
        # Fallback: check if path is a spec file
        root / "spec" / f"{file_path.replace('.', '/')}.md",
        root / "spec" / "protocols" / f"{file_path.replace('.', '/')}.md",
        root / "spec" / "services" / f"{file_path.replace('.', '/')}.md",
    ]

    for p in patterns:
        if p.exists():
            return p

    return None


def file_to_agentese_path(file_path: Path, root: Path) -> str:
    """
    Convert a file path to an AGENTESE path.

    impl/claude/services/brain/core.py → world.brain
    impl/claude/services/brain/persistence.py → world.brain.persistence

    Teaching:
        gotcha: This strips impl/claude/ prefix automatically. The returned
                path is the canonical AGENTESE form starting with 'world.'.
                (Evidence: test_hyperedge_resolvers.py::test_file_to_agentese_with_impl)
    """
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return f"world.{file_path.stem}"

    parts = list(rel.parts)

    # Remove impl/claude prefix (kgents structure)
    if len(parts) >= 2 and parts[0] == "impl" and parts[1] == "claude":
        parts = parts[2:]

    # Remove common prefixes (services, protocols, agents)
    if parts and parts[0] in ("services", "protocols", "agents"):
        parts = parts[1:]

    # Remove file extension
    if parts:
        last = parts[-1]
        if last.endswith(".py"):
            parts[-1] = last[:-3]
        elif last.endswith(".md"):
            parts[-1] = last[:-3]

    # Remove common suffixes like core, __init__, node (collapse to parent)
    if parts and parts[-1] in ("core", "__init__", "node"):
        parts = parts[:-1]

    if not parts:
        return "world"

    return "world." + ".".join(parts)


# === Structural Resolvers ===


@register_resolver("contains", reverse_edge="contained_in")
async def resolve_contains(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find children/submodules of a node.

    For file-based nodes: list files in directory
    For module nodes: find submodules
    """
    from .self_context import ContextNode

    file_path = agentese_path_to_file(node.path, root)
    if file_path is None:
        return []

    results: list[ContextNode] = []

    # If it's a directory or __init__.py, find children
    if file_path.name == "__init__.py":
        parent_dir = file_path.parent
    elif file_path.is_dir():
        parent_dir = file_path
    else:
        # Regular file - no children
        return []

    # Find Python files in directory
    for child in parent_dir.iterdir():
        if child.name.startswith("_") and child.name != "__init__.py":
            continue

        if child.is_file() and child.suffix == ".py":
            child_path = file_to_agentese_path(child, root)
            results.append(
                ContextNode(
                    path=child_path,
                    holon=child.stem,
                )
            )
        elif child.is_dir() and (child / "__init__.py").exists():
            child_path = file_to_agentese_path(child / "__init__.py", root)
            results.append(
                ContextNode(
                    path=child_path,
                    holon=child.name,
                )
            )

    return results


@register_resolver("parent", reverse_edge="children")
async def resolve_parent(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """Find parent module of a node."""
    from .self_context import ContextNode

    # Parse path to find parent
    parts = node.path.split(".")
    if len(parts) <= 2:  # e.g., "world.foo" has no parent
        return []

    parent_path = ".".join(parts[:-1])
    parent_holon = parts[-2]

    return [
        ContextNode(
            path=parent_path,
            holon=parent_holon,
        )
    ]


@register_resolver("imports", reverse_edge="imported_by")
async def resolve_imports(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find imports/dependencies of a Python file.

    Uses AST to parse import statements.
    """
    from .self_context import ContextNode

    file_path = agentese_path_to_file(node.path, root)
    if file_path is None or not file_path.exists():
        return []

    results: list[ContextNode] = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    # Convert import to AGENTESE path
                    agentese_path = f"world.{alias.name}"
                    results.append(
                        ContextNode(
                            path=agentese_path,
                            holon=alias.name.split(".")[-1],
                        )
                    )
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module:
                    agentese_path = f"world.{stmt.module}"
                    results.append(
                        ContextNode(
                            path=agentese_path,
                            holon=stmt.module.split(".")[-1],
                        )
                    )
    except (SyntaxError, OSError):
        pass

    return results


@register_resolver("calls", reverse_edge="called_by")
async def resolve_calls(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find functions called by this module.

    Uses AST to find function calls.
    """
    from .self_context import ContextNode

    file_path = agentese_path_to_file(node.path, root)
    if file_path is None or not file_path.exists():
        return []

    results: list[ContextNode] = []
    seen: set[str] = set()

    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.Call):
                # Get function name
                func_name = None
                if isinstance(stmt.func, ast.Name):
                    func_name = stmt.func.id
                elif isinstance(stmt.func, ast.Attribute):
                    func_name = stmt.func.attr

                if func_name and func_name not in seen:
                    seen.add(func_name)
                    # Create a reference node
                    results.append(
                        ContextNode(
                            path=f"{node.path}.{func_name}",
                            holon=func_name,
                        )
                    )
    except (SyntaxError, OSError):
        pass

    return results[:20]  # Limit to prevent explosion


# === Testing Resolvers ===


@register_resolver("tests", reverse_edge="tested_by")
async def resolve_tests(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find test files for a module.

    Naming conventions:
    - foo.py → _tests/test_foo.py
    - foo.py → tests/test_foo.py
    - foo/ → foo/_tests/
    """
    from .self_context import ContextNode

    file_path = agentese_path_to_file(node.path, root)
    if file_path is None:
        return []

    results: list[ContextNode] = []
    module_name = file_path.stem

    # Look for test files in various locations
    test_patterns = [
        file_path.parent / "_tests" / f"test_{module_name}.py",
        file_path.parent / "tests" / f"test_{module_name}.py",
        file_path.parent.parent / "_tests" / f"test_{module_name}.py",
        file_path.parent.parent / "tests" / f"test_{module_name}.py",
    ]

    for test_path in test_patterns:
        if test_path.exists():
            test_agentese = file_to_agentese_path(test_path, root)
            results.append(
                ContextNode(
                    path=test_agentese,
                    holon=test_path.stem,
                )
            )

    return results


@register_resolver("covers", reverse_edge="covered_by")
async def resolve_covers(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find code paths covered by this test.

    Inverse of tests - finds what a test file tests.
    """
    from .self_context import ContextNode

    if not node.path.endswith("test_") and "test" not in node.holon:
        return []

    # Extract module name from test name
    # test_foo → foo
    module_name = node.holon.replace("test_", "")

    results: list[ContextNode] = []

    # Look for the tested module
    file_path = agentese_path_to_file(node.path, root)
    if file_path:
        parent = file_path.parent
        if parent.name in ("_tests", "tests"):
            # Go up and look for module
            module_path = parent.parent / f"{module_name}.py"
            if module_path.exists():
                module_agentese = file_to_agentese_path(module_path, root)
                results.append(
                    ContextNode(
                        path=module_agentese,
                        holon=module_name,
                    )
                )

    return results


# === Specification Resolvers ===


@register_resolver("implements", reverse_edge="implemented_by")
async def resolve_implements(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find specifications implemented by this module.

    Looks for:
    - Docstring references to specs
    - Comments mentioning spec files
    - Naming patterns (foo_spec.md → foo.py)
    """
    from .self_context import ContextNode

    file_path = agentese_path_to_file(node.path, root)
    if file_path is None or not file_path.exists():
        return []

    results: list[ContextNode] = []

    # Look for corresponding spec file
    module_name = file_path.stem
    spec_patterns = [
        root / "spec" / f"{module_name}.md",
        root / "spec" / "protocols" / f"{module_name}.md",
        root / "spec" / "services" / f"{module_name}.md",
        root / "spec" / "agents" / f"{module_name}.md",
    ]

    for spec_path in spec_patterns:
        if spec_path.exists():
            spec_agentese = f"concept.spec.{spec_path.stem}"
            results.append(
                ContextNode(
                    path=spec_agentese,
                    holon=spec_path.stem,
                )
            )

    # Also check docstring for spec references
    try:
        content = file_path.read_text()
        # Look for "Spec: ..." patterns
        spec_refs = re.findall(r"Spec:\s*([^\n]+)", content)
        for ref in spec_refs:
            ref = ref.strip()
            if ref:
                results.append(
                    ContextNode(
                        path=f"concept.spec.{ref.replace('/', '.')}",
                        holon=ref.split("/")[-1].replace(".md", ""),
                    )
                )
    except OSError:
        pass

    return results


@register_resolver("derives_from", reverse_edge="derived_by")
async def resolve_derives_from(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find parent specifications this derives from.

    Looks for "Derives From:" in spec files.
    """
    from .self_context import ContextNode

    # Only applies to spec nodes
    if not node.path.startswith("concept.spec"):
        return []

    # Try to find the spec file
    spec_name = node.holon
    spec_patterns = [
        root / "spec" / f"{spec_name}.md",
        root / "spec" / "protocols" / f"{spec_name}.md",
    ]

    for spec_path in spec_patterns:
        if spec_path.exists():
            try:
                content = spec_path.read_text()
                # Look for "Derives From:" pattern
                derives = re.findall(r"Derives From:\s*`([^`]+)`", content)
                results: list[ContextNode] = []
                for ref in derives:
                    results.append(
                        ContextNode(
                            path=f"concept.spec.{ref.replace('/', '.')}",
                            holon=ref.split("/")[-1].replace(".md", ""),
                        )
                    )
                return results
            except OSError:
                pass

    return []


# === Reverse Edge Resolvers ===
# Law 10.2: A ──[e]──→ B  ⟺  B ──[reverse(e)]──→ A


@register_resolver("contained_in", reverse_edge="contains")
async def resolve_contained_in(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find parent container of a node (reverse of contains).

    Teaching:
        gotcha: This is the reverse of contains. It finds the parent
                module that contains this node.
                (Evidence: test_hyperedge_resolvers.py::test_contained_in_resolver)
    """
    # Delegate to parent resolver - same logic
    return await resolve_parent(node, root)


@register_resolver("imported_by")
async def resolve_imported_by(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find modules that import this node (reverse of imports).

    Note: This is computationally expensive as it requires scanning
    all Python files. For now, returns empty list (placeholder).

    Teaching:
        gotcha: Full reverse import resolution requires a project index.
                This is a placeholder that documents the expected behavior.
                (Evidence: test_hyperedge_resolvers.py::test_imported_by_placeholder)
    """
    # TODO: Implement when we have a project index
    # Would require: scan all .py files, parse imports, check if they import node
    return []


@register_resolver("called_by")
async def resolve_called_by(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find functions that call this node (reverse of calls).

    Note: This is computationally expensive. Returns empty list (placeholder).
    """
    # TODO: Implement with AST indexing
    return []


@register_resolver("tested_by")
async def resolve_tested_by(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find the module tested by this test file (reverse of tests).

    For test files, finds the corresponding implementation module.

    Teaching:
        gotcha: This resolver reverses the tests relationship.
                test_foo.py ──[tested_by]──→ foo.py
                (Evidence: test_hyperedge_resolvers.py::test_tested_by_resolver)
    """
    # Delegate to covers resolver - same logic
    return await resolve_covers(node, root)


@register_resolver("implemented_by")
async def resolve_implemented_by(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find implementation modules for a spec (reverse of implements).

    Given a spec node, finds the Python modules that implement it.
    """
    from .self_context import ContextNode

    if not node.path.startswith("concept.spec"):
        return []

    spec_name = node.holon
    results: list[ContextNode] = []
    impl_root = root / "impl" / "claude"

    # Search for implementations in services/
    services = impl_root / "services"
    if services.exists():
        for service_dir in services.iterdir():
            if service_dir.is_dir() and service_dir.name == spec_name:
                # Found matching service
                impl_file = service_dir / "core.py"
                if impl_file.exists():
                    results.append(
                        ContextNode(
                            path=f"world.{spec_name}",
                            holon=spec_name,
                        )
                    )

    # Search in protocols/
    protocols = impl_root / "protocols"
    if protocols.exists():
        for proto_dir in protocols.iterdir():
            if proto_dir.is_dir() and proto_dir.name == spec_name:
                results.append(
                    ContextNode(
                        path=f"world.{spec_name}",
                        holon=spec_name,
                    )
                )

    return results


@register_resolver("derived_by")
async def resolve_derived_by(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find specs that derive from this spec (reverse of derives_from).

    Note: Requires scanning spec files. Returns empty list (placeholder).
    """
    # TODO: Implement by scanning spec files for "Derives From:" references
    return []


# === Semantic Resolvers ===


@register_resolver("related")
async def resolve_related(node: "ContextNode", root: Path) -> list["ContextNode"]:
    """
    Find loosely related nodes.

    Uses naming similarity and directory proximity.
    """
    from .self_context import ContextNode

    # Simple implementation: find siblings
    parent_path = ".".join(node.path.split(".")[:-1])
    if not parent_path:
        return []

    file_path = agentese_path_to_file(parent_path, root)
    if file_path is None:
        return []

    results: list[ContextNode] = []

    # Find files in same directory
    if file_path.is_file():
        parent_dir = file_path.parent
    else:
        parent_dir = file_path

    for sibling in parent_dir.iterdir():
        if sibling.suffix == ".py" and sibling.stem != node.holon:
            if not sibling.name.startswith("_") or sibling.name == "__init__.py":
                sib_path = file_to_agentese_path(sibling, root)
                if sib_path != node.path:
                    results.append(
                        ContextNode(
                            path=sib_path,
                            holon=sibling.stem,
                        )
                    )

    return results[:10]  # Limit siblings


# === Main Resolution Function ===


async def resolve_hyperedge(
    node: "ContextNode",
    edge_type: str,
    root: Path,
) -> list["ContextNode"]:
    """
    Resolve a hyperedge from a node.

    Uses the registered resolver for the edge type.
    Returns empty list if no resolver is registered.
    """
    resolver = _registry.get(edge_type)
    if resolver is None:
        return []

    return await resolver(node, root)


async def resolve_all_edges(
    node: "ContextNode",
    root: Path,
) -> dict[str, list["ContextNode"]]:
    """
    Resolve all registered hyperedges for a node.

    Returns {edge_type: [destination_nodes]}.
    """
    results: dict[str, list["ContextNode"]] = {}

    for edge_type in _registry.list_edge_types():
        destinations = await resolve_hyperedge(node, edge_type, root)
        if destinations:
            results[edge_type] = destinations

    return results


__all__ = [
    # Project root
    "_get_project_root",
    "_set_project_root",
    # Registry
    "ResolverRegistry",
    "get_resolver_registry",
    "register_resolver",
    # Path utilities
    "agentese_path_to_file",
    "file_to_agentese_path",
    # Resolution
    "resolve_hyperedge",
    "resolve_all_edges",
    # Resolvers are auto-registered via decorator
]
