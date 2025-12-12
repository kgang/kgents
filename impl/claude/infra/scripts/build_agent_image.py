#!/usr/bin/env python3
"""
Build Agent Image Script - Validates/generates Dockerfile COPY statements.

Reads __deps__.py manifests from kgents modules and ensures Dockerfiles
include all required internal dependencies (transitively resolved).

Usage:
    python build_agent_image.py agents.l --validate
    python build_agent_image.py agents.l --generate
    python build_agent_image.py agents.l --show-deps

AGENTESE: world.container.build
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import NamedTuple


class ModuleDeps(NamedTuple):
    """Dependency manifest for a module."""

    internal_deps: list[str]
    pip_deps: list[str]


def load_deps(module_path: str, impl_root: Path) -> ModuleDeps | None:
    """Load __deps__.py from a module path like 'agents.l' or 'bootstrap'."""
    # Convert module path to filesystem path
    parts = module_path.split(".")
    deps_file = impl_root / "/".join(parts) / "__deps__.py"

    if not deps_file.exists():
        return None

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location("deps", deps_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return ModuleDeps(
        internal_deps=getattr(module, "INTERNAL_DEPS", []),
        pip_deps=getattr(module, "PIP_DEPS", []),
    )


def resolve_transitive_deps(
    module_path: str, impl_root: Path, seen: set[str] | None = None
) -> set[str]:
    """
    Resolve all transitive internal dependencies for a module.

    Returns a set of all module paths required (including the module itself).
    """
    if seen is None:
        seen = set()

    if module_path in seen:
        return seen

    seen.add(module_path)

    deps = load_deps(module_path, impl_root)
    if deps is None:
        # Module has no __deps__.py - treat as having no dependencies
        return seen

    for dep in deps.internal_deps:
        resolve_transitive_deps(dep, impl_root, seen)

    return seen


def module_to_copy_path(module_path: str) -> str:
    """Convert module path to Dockerfile COPY source path."""
    # agents.l -> impl/claude/agents/l/
    # bootstrap -> impl/claude/bootstrap/
    parts = module_path.split(".")
    return "impl/claude/" + "/".join(parts) + "/"


def module_to_dest_path(module_path: str) -> str:
    """Convert module path to Dockerfile COPY destination path."""
    # agents.l -> /app/agents/l/
    # bootstrap -> /app/bootstrap/
    parts = module_path.split(".")
    return "/app/" + "/".join(parts) + "/"


def parse_dockerfile_copies(dockerfile_path: Path) -> set[str]:
    """
    Extract COPY source paths from Dockerfile.

    Returns set of paths like 'impl/claude/agents/l/'
    """
    if not dockerfile_path.exists():
        return set()

    content = dockerfile_path.read_text()
    copies = set()

    # Match COPY impl/claude/... /app/...
    pattern = r"COPY\s+(impl/claude/[\w/]+/)\s+"
    for match in re.finditer(pattern, content):
        copies.add(match.group(1))

    return copies


def validate_dockerfile(
    module_path: str, dockerfile_path: Path, impl_root: Path
) -> tuple[bool, list[str]]:
    """
    Validate that Dockerfile has all required COPY statements.

    Returns (is_valid, missing_copies).
    """
    required_deps = resolve_transitive_deps(module_path, impl_root)
    required_copies = {module_to_copy_path(dep) for dep in required_deps}

    actual_copies = parse_dockerfile_copies(dockerfile_path)

    missing = required_copies - actual_copies
    return len(missing) == 0, sorted(missing)


def generate_copy_statements(module_path: str, impl_root: Path) -> list[str]:
    """Generate COPY statements for all required dependencies."""
    required_deps = resolve_transitive_deps(module_path, impl_root)

    statements = []
    for dep in sorted(required_deps):
        src = module_to_copy_path(dep)
        dest = module_to_dest_path(dep)

        # Add descriptive comment
        if dep == module_path:
            comment = f"# Copy {dep} package (target module)"
        else:
            comment = f"# Copy {dep} (dependency)"

        statements.append(f"{comment}\nCOPY {src} {dest}")

    return statements


def collect_pip_deps(module_path: str, impl_root: Path) -> list[str]:
    """Collect all pip dependencies (transitive)."""
    required_deps = resolve_transitive_deps(module_path, impl_root)

    all_pip_deps: set[str] = set()
    for dep in required_deps:
        deps = load_deps(dep, impl_root)
        if deps:
            all_pip_deps.update(deps.pip_deps)

    return sorted(all_pip_deps)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or generate Dockerfile COPY statements from __deps__.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s agents.l --validate     # Check Dockerfile has all required COPYs
  %(prog)s agents.l --generate     # Output COPY statements for module
  %(prog)s agents.l --show-deps    # Show resolved dependency tree
  %(prog)s agents.l --show-pip     # Show pip dependencies
""",
    )
    parser.add_argument(
        "module",
        help="Module path (e.g., agents.l, agents.d, bootstrap)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate Dockerfile has all required COPY statements",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate COPY statements for the module",
    )
    parser.add_argument(
        "--show-deps",
        action="store_true",
        help="Show resolved dependency tree",
    )
    parser.add_argument(
        "--show-pip",
        action="store_true",
        help="Show pip dependencies",
    )
    parser.add_argument(
        "--dockerfile",
        type=Path,
        help="Path to Dockerfile (default: impl/claude/{module}/Dockerfile)",
    )
    parser.add_argument(
        "--impl-root",
        type=Path,
        default=None,
        help="Path to impl/claude directory",
    )

    args = parser.parse_args()

    # Find impl root
    if args.impl_root:
        impl_root = args.impl_root
    else:
        # Try to find it relative to this script
        script_dir = Path(__file__).parent
        impl_root = script_dir.parent.parent  # impl/claude/infra/scripts -> impl/claude
        if not (impl_root / "bootstrap").exists():
            # Try from current directory
            impl_root = Path.cwd()
            while impl_root.parent != impl_root:
                if (impl_root / "impl/claude/bootstrap").exists():
                    impl_root = impl_root / "impl/claude"
                    break
                impl_root = impl_root.parent

    if not (impl_root / "bootstrap").exists():
        print(f"Error: Could not find impl/claude root (tried {impl_root})", file=sys.stderr)
        return 1

    # Check module exists
    deps = load_deps(args.module, impl_root)
    if deps is None:
        module_parts = args.module.split(".")
        module_dir = impl_root / "/".join(module_parts)
        if not module_dir.exists():
            print(f"Error: Module {args.module} not found at {module_dir}", file=sys.stderr)
            return 1
        print(
            f"Warning: Module {args.module} has no __deps__.py, treating as no dependencies",
            file=sys.stderr,
        )

    # Default Dockerfile path
    if args.dockerfile:
        dockerfile_path = args.dockerfile
    else:
        module_parts = args.module.split(".")
        dockerfile_path = impl_root / "/".join(module_parts) / "Dockerfile"

    if args.show_deps:
        all_deps = resolve_transitive_deps(args.module, impl_root)
        print(f"Dependencies for {args.module}:")
        for dep in sorted(all_deps):
            marker = "*" if dep == args.module else " "
            print(f"  {marker} {dep}")
        return 0

    if args.show_pip:
        pip_deps = collect_pip_deps(args.module, impl_root)
        print(f"Pip dependencies for {args.module}:")
        for dep in pip_deps:
            print(f"  {dep}")
        return 0

    if args.generate:
        statements = generate_copy_statements(args.module, impl_root)
        print("# Generated COPY statements for", args.module)
        print("# Add these to your Dockerfile:\n")
        print("\n\n".join(statements))
        return 0

    if args.validate:
        if not dockerfile_path.exists():
            print(f"Error: Dockerfile not found at {dockerfile_path}", file=sys.stderr)
            return 1

        is_valid, missing = validate_dockerfile(args.module, dockerfile_path, impl_root)
        if is_valid:
            print(f"✓ Dockerfile {dockerfile_path} has all required COPY statements")
            return 0
        else:
            print(f"✗ Dockerfile {dockerfile_path} is missing COPY statements:")
            for path in missing:
                print(f"  - {path}")
            print("\nRun with --generate to see required COPY statements")
            return 1

    # Default: show usage
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
