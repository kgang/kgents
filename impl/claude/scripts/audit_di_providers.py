#!/usr/bin/env python3
"""
DI Provider Audit Script: Prevent the Silent Skip Problem

This script validates that every @node dependency declaration has a matching
provider registered in the container. The container SILENTLY SKIPS unregistered
dependencies at DEBUG level, causing cryptic TypeError messages at runtime.

The Silent Skip Problem:
------------------------
1. @node(dependencies=("foo",)) declares a dependency
2. Container checks has("foo") → False (not registered!)
3. Container logs at DEBUG and SKIPS (silent!)
4. cls() called without the dependency → TypeError: missing argument

Usage:
    cd impl/claude
    uv run python scripts/audit_di_providers.py

Exit codes:
    0 - All dependencies have matching providers
    1 - Missing providers found (lists them)

See: docs/skills/agentese-node-registration.md → "The Silent Skip Problem"
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple


class NodeDeclaration(NamedTuple):
    """A @node decorator found in the codebase."""

    file: Path
    line: int
    path: str  # AGENTESE path like "world.town.inhabit"
    dependencies: tuple[str, ...]
    class_name: str


class ProviderRegistration(NamedTuple):
    """A container.register() call found in providers.py."""

    name: str
    line: int


def find_node_declarations(root: Path) -> list[NodeDeclaration]:
    """
    Find all @node decorators and extract their dependencies.

    Parses Python files looking for:
        @node("path", dependencies=("foo", "bar"))
        class SomeNode: ...
    """
    declarations: list[NodeDeclaration] = []

    # Search in all relevant directories
    search_dirs = [
        root / "protocols" / "agentese" / "contexts",
        root / "services",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        for py_file in search_dir.rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue

            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                for decorator in node.decorator_list:
                    decl = _parse_node_decorator(decorator, py_file, node.name)
                    if decl:
                        declarations.append(decl)

    return declarations


def _parse_node_decorator(
    decorator: ast.expr, file: Path, class_name: str
) -> NodeDeclaration | None:
    """Parse a @node(...) decorator and extract path + dependencies."""

    # Handle @node("path", ...) form
    if isinstance(decorator, ast.Call):
        func = decorator.func
        if isinstance(func, ast.Name) and func.id == "node":
            pass
        elif isinstance(func, ast.Attribute) and func.attr == "node":
            pass
        else:
            return None

        # Extract path (first positional arg)
        path = ""
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            path = decorator.args[0].value

        # Extract dependencies keyword arg
        dependencies: tuple[str, ...] = ()
        for kw in decorator.keywords:
            if kw.arg == "dependencies":
                if isinstance(kw.value, ast.Tuple):
                    deps = []
                    for elt in kw.value.elts:
                        if isinstance(elt, ast.Constant):
                            deps.append(elt.value)
                    dependencies = tuple(deps)

        if path:
            return NodeDeclaration(
                file=file,
                line=decorator.lineno,
                path=path,
                dependencies=dependencies,
                class_name=class_name,
            )

    return None


def find_provider_registrations(providers_file: Path) -> list[ProviderRegistration]:
    """
    Find all container.register("name", ...) calls in providers.py.
    """
    registrations: list[ProviderRegistration] = []

    if not providers_file.exists():
        return registrations

    try:
        tree = ast.parse(providers_file.read_text())
    except SyntaxError:
        return registrations

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # Look for container.register(...) or self.register(...)
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "register":
            if node.args and isinstance(node.args[0], ast.Constant):
                name = node.args[0].value
                if isinstance(name, str):
                    registrations.append(
                        ProviderRegistration(
                            name=name,
                            line=node.lineno,
                        )
                    )

    return registrations


def audit_di_providers(root: Path) -> tuple[list[str], list[str]]:
    """
    Audit all @node dependencies against registered providers.

    Returns:
        (missing, warnings) - Lists of issues found
    """
    providers_file = root / "services" / "providers.py"

    # Find all declarations and registrations
    declarations = find_node_declarations(root)
    registrations = find_provider_registrations(providers_file)

    registered_names = {r.name for r in registrations}

    missing: list[str] = []
    warnings: list[str] = []

    for decl in declarations:
        for dep in decl.dependencies:
            if dep not in registered_names:
                missing.append(
                    f"  {decl.path} ({decl.class_name})\n"
                    f"    → Missing provider: '{dep}'\n"
                    f"    → File: {decl.file.relative_to(root)}:{decl.line}\n"
                    f"    → Fix: Add get_{dep}() to services/providers.py and register it"
                )

    # Check for unused providers (informational)
    declared_deps = set()
    for decl in declarations:
        declared_deps.update(decl.dependencies)

    for reg in registrations:
        # Skip infrastructure providers that might be used elsewhere
        infra_providers = {
            "session_factory",
            "dgent",
            "kgent_soul",
            "differance_store",
            "morpheus_persistence",
            "chat_factory",
            "chat_persistence",
        }
        if reg.name not in declared_deps and reg.name not in infra_providers:
            # Check if it ends with _persistence (Crown Jewel pattern)
            if not reg.name.endswith("_persistence"):
                warnings.append(
                    f"  Provider '{reg.name}' registered but not declared as dependency"
                )

    return missing, warnings


def main() -> int:
    """Run the audit and report results."""
    root = Path(__file__).parent.parent  # impl/claude

    print("=" * 60)
    print("DI Provider Audit: Checking for Silent Skip Problems")
    print("=" * 60)
    print()

    missing, warnings = audit_di_providers(root)

    if missing:
        print("❌ MISSING PROVIDERS (will cause TypeError at runtime):")
        print()
        for m in missing:
            print(m)
        print()
        print("The container SILENTLY SKIPS these at DEBUG level!")
        print("See: docs/skills/agentese-node-registration.md")
        print()
        return 1
    else:
        print("✅ All @node dependencies have matching providers")
        print()

    if warnings:
        print("⚠️  WARNINGS (informational):")
        print()
        for w in warnings:
            print(w)
        print()

    # Print summary
    declarations = find_node_declarations(root)
    registrations = find_provider_registrations(root / "services" / "providers.py")

    total_deps = sum(len(d.dependencies) for d in declarations)

    print("-" * 60)
    print("Summary:")
    print(f"  @node declarations: {len(declarations)}")
    print(f"  Total dependencies: {total_deps}")
    print(f"  Registered providers: {len(registrations)}")
    print("-" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
