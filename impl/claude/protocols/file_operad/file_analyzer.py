"""
File Analyzer: Extract Portal Edges from Source Files.

Analyzes Python files to discover:
- imports (dependencies)
- tests (test files that cover this module)
- specs (specification files that describe this module)
- implements (what this file implements from specs)

The analyzer populates PortalNode.children with discovered edges,
enabling the frontend to show expandable portal trees.

Teaching:
    gotcha: AST parsing can fail on syntax errors. Always catch SyntaxError
            and return partial results. A file with bad syntax still has
            a filename and path that can be used.
            (Evidence: test_file_analyzer.py::test_syntax_error_graceful)

    gotcha: Test file discovery uses heuristics (naming conventions), not
            coverage data. This is intentional - coverage data requires
            running tests, but we want instant discovery.
            (Evidence: test_file_analyzer.py::test_discovers_test_files)
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .portal import PortalNode, PortalState


@dataclass
class FilePortals:
    """
    Discovered portal edges for a file.

    Each edge type maps to a list of destinations (file paths or module names).
    """

    file_path: str
    imports: list[str] = field(default_factory=list)  # Import dependencies
    tests: list[str] = field(default_factory=list)  # Test files for this module
    specs: list[str] = field(default_factory=list)  # Related spec files
    implements: list[str] = field(default_factory=list)  # Specs this implements
    related: list[str] = field(default_factory=list)  # Semantically related files

    def to_portal_nodes(self, depth: int = 1) -> list[PortalNode]:
        """
        Convert discovered portals to PortalNode children.

        Creates GROUPED nodes - one container per edge type with children inside.
        This matches the structure expected by the portal UI.

        Returns:
            List of PortalNode container objects, each with children
        """
        nodes: list[PortalNode] = []

        # Add imports as a grouped container
        if self.imports:
            import_children = [
                PortalNode(
                    path=imp,
                    edge_type=None,  # Child nodes don't repeat edge_type
                    depth=depth + 1,
                    state=PortalState.COLLAPSED,
                )
                for imp in self.imports
            ]
            nodes.append(
                PortalNode(
                    path=f"{len(self.imports)} imports",
                    edge_type="imports",
                    depth=depth,
                    state=PortalState.COLLAPSED,
                    children=import_children,
                )
            )

        # Add tests as a grouped container
        if self.tests:
            test_children = [
                PortalNode(
                    path=test,
                    edge_type=None,
                    depth=depth + 1,
                    state=PortalState.COLLAPSED,
                )
                for test in self.tests
            ]
            nodes.append(
                PortalNode(
                    path=f"{len(self.tests)} tests",
                    edge_type="tests",
                    depth=depth,
                    state=PortalState.COLLAPSED,
                    children=test_children,
                )
            )

        # Add specs as a grouped container
        if self.specs:
            spec_children = [
                PortalNode(
                    path=spec,
                    edge_type=None,
                    depth=depth + 1,
                    state=PortalState.COLLAPSED,
                )
                for spec in self.specs
            ]
            nodes.append(
                PortalNode(
                    path=f"{len(self.specs)} specs",
                    edge_type="spec",
                    depth=depth,
                    state=PortalState.COLLAPSED,
                    children=spec_children,
                )
            )

        # Add implements as a grouped container
        if self.implements:
            impl_children = [
                PortalNode(
                    path=impl,
                    edge_type=None,
                    depth=depth + 1,
                    state=PortalState.COLLAPSED,
                )
                for impl in self.implements
            ]
            nodes.append(
                PortalNode(
                    path=f"{len(self.implements)} implements",
                    edge_type="implements",
                    depth=depth,
                    state=PortalState.COLLAPSED,
                    children=impl_children,
                )
            )

        # Add related as a grouped container
        if self.related:
            rel_children = [
                PortalNode(
                    path=rel,
                    edge_type=None,
                    depth=depth + 1,
                    state=PortalState.COLLAPSED,
                )
                for rel in self.related
            ]
            nodes.append(
                PortalNode(
                    path=f"{len(self.related)} related",
                    edge_type="related",
                    depth=depth,
                    state=PortalState.COLLAPSED,
                    children=rel_children,
                )
            )

        return nodes


def analyze_python_file(file_path: str | Path, project_root: str | Path | None = None) -> FilePortals:
    """
    Analyze a Python file and extract portal edges.

    Args:
        file_path: Path to the Python file
        project_root: Optional project root for relative path resolution

    Returns:
        FilePortals with discovered imports, tests, specs, etc.
    """
    file_path = Path(file_path)
    project_root = Path(project_root) if project_root else _find_project_root(file_path)

    portals = FilePortals(file_path=str(file_path))

    if not file_path.exists():
        return portals

    if not file_path.suffix == ".py":
        return portals

    # Extract imports from AST
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        portals.imports = _extract_imports(tree, file_path, project_root)
    except SyntaxError:
        # Graceful degradation: return what we have
        pass

    # Find test files (heuristic-based)
    portals.tests = _find_test_files(file_path, project_root)

    # Find spec files (convention-based)
    portals.specs = _find_spec_files(file_path, project_root)

    return portals


def _extract_imports(tree: ast.Module, file_path: Path, project_root: Path) -> list[str]:
    """
    Extract import statements from AST and resolve to file paths.

    Handles:
    - import foo
    - from foo import bar
    - from . import relative
    - from ..sibling import thing
    """
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                resolved = _resolve_import(alias.name, file_path, project_root)
                if resolved:
                    imports.append(resolved)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # from X import Y
                module = node.module
                if node.level > 0:
                    # Relative import
                    module = _resolve_relative_import(
                        node.module, node.level, file_path, project_root
                    )
                resolved = _resolve_import(module, file_path, project_root)
                if resolved:
                    imports.append(resolved)

    # Deduplicate while preserving order
    seen = set()
    unique_imports = []
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)

    return unique_imports


def _resolve_import(module_name: str, file_path: Path, project_root: Path) -> str | None:
    """
    Resolve a module name to a file path within the project.

    Returns None if the import is external (not in project).
    """
    # Convert module.path to module/path.py
    parts = module_name.split(".")

    # Try as package (directory with __init__.py)
    package_path = project_root / "/".join(parts) / "__init__.py"
    if package_path.exists():
        return str(package_path.relative_to(project_root))

    # Try as module (file.py)
    module_path = project_root / "/".join(parts[:-1]) / f"{parts[-1]}.py" if len(parts) > 1 else project_root / f"{parts[0]}.py"
    if module_path.exists():
        return str(module_path.relative_to(project_root))

    # Try directly
    direct_path = project_root / "/".join(parts)
    if direct_path.with_suffix(".py").exists():
        return str(direct_path.with_suffix(".py").relative_to(project_root))

    return None  # External import


def _resolve_relative_import(
    module: str | None, level: int, file_path: Path, project_root: Path
) -> str:
    """
    Resolve a relative import to absolute module path.

    level=1 means current package (.)
    level=2 means parent package (..)
    """
    # Start from the file's directory
    current = file_path.parent

    # Go up 'level' directories
    for _ in range(level - 1):
        current = current.parent

    # Build module path
    if module:
        return ".".join(current.relative_to(project_root).parts) + "." + module
    return ".".join(current.relative_to(project_root).parts)


def _find_test_files(file_path: Path, project_root: Path) -> list[str]:
    """
    Find test files that likely test this module.

    Uses naming conventions:
    - _tests/test_<module>.py (kgents pattern)
    - tests/test_<module>.py
    - <module>_test.py
    """
    tests: list[str] = []
    module_name = file_path.stem

    # Check for _tests directory (kgents pattern)
    tests_dir = file_path.parent / "_tests"
    if tests_dir.exists():
        test_file = tests_dir / f"test_{module_name}.py"
        if test_file.exists():
            tests.append(str(test_file.relative_to(project_root)))

    # Check for tests directory
    tests_dir = file_path.parent / "tests"
    if tests_dir.exists():
        test_file = tests_dir / f"test_{module_name}.py"
        if test_file.exists():
            tests.append(str(test_file.relative_to(project_root)))

    # Check for co-located test file
    colocated = file_path.parent / f"{module_name}_test.py"
    if colocated.exists():
        tests.append(str(colocated.relative_to(project_root)))

    # Check root tests directory
    root_tests = project_root / "tests" / f"test_{module_name}.py"
    if root_tests.exists():
        tests.append(str(root_tests.relative_to(project_root)))

    return tests


def _find_spec_files(file_path: Path, project_root: Path) -> list[str]:
    """
    Find spec files related to this module.

    Looks in:
    - spec/<module_name>.md
    - spec/**/<module_name>.md
    - spec/services/<jewel>/*.md (for Crown Jewels)
    """
    specs: list[str] = []
    module_name = file_path.stem

    # Direct spec file
    spec_dir = project_root / "spec"
    if spec_dir.exists():
        # Direct match
        direct_spec = spec_dir / f"{module_name}.md"
        if direct_spec.exists():
            specs.append(str(direct_spec.relative_to(project_root)))

        # Search in subdirectories
        for spec_file in spec_dir.rglob(f"{module_name}.md"):
            rel_path = str(spec_file.relative_to(project_root))
            if rel_path not in specs:
                specs.append(rel_path)

        # For services, look for service-specific specs
        if "services" in file_path.parts:
            # Find service name (e.g., "brain" from services/brain/core.py)
            try:
                services_idx = list(file_path.parts).index("services")
                if services_idx + 1 < len(file_path.parts):
                    service_name = file_path.parts[services_idx + 1]
                    service_spec = spec_dir / "services" / f"{service_name}.md"
                    if service_spec.exists():
                        rel = str(service_spec.relative_to(project_root))
                        if rel not in specs:
                            specs.append(rel)
            except (ValueError, IndexError):
                pass

    return specs


def _find_project_root(file_path: Path) -> Path:
    """
    Find the project root by looking for markers.

    Looks for: pyproject.toml, .git, setup.py
    """
    current = file_path.parent

    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        if (current / ".git").exists():
            return current
        if (current / "setup.py").exists():
            return current
        current = current.parent

    # Fallback to file's parent
    return file_path.parent


def create_file_portal_tree(
    file_path: str | Path,
    project_root: str | Path | None = None,
    max_depth: int = 3,
) -> dict[str, Any]:
    """
    Create a complete PortalTree for a file, suitable for API response.

    This is the main entry point for the portal API.

    Args:
        file_path: Path to the source file
        project_root: Optional project root
        max_depth: Maximum expansion depth

    Returns:
        Dict matching the PortalTree TypeScript interface:
        {
            "root": PortalNode dict,
            "max_depth": int
        }
    """
    from .portal import PortalTree

    file_path = Path(file_path)
    project_root = Path(project_root) if project_root else _find_project_root(file_path)

    # Analyze the file
    portals = analyze_python_file(file_path, project_root)

    # Create root node
    root = PortalNode(
        path=str(file_path),
        edge_type=None,  # Root has no edge
        expanded=True,  # Root is always expanded
        depth=0,
        state=PortalState.EXPANDED,
        children=portals.to_portal_nodes(depth=1),
    )

    # Create tree
    tree = PortalTree(root=root, max_depth=max_depth)

    return tree.to_dict()


__all__ = [
    "FilePortals",
    "analyze_python_file",
    "create_file_portal_tree",
]
