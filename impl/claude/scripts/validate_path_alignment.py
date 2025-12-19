#!/usr/bin/env python3
"""
AGENTESE Path Alignment Validator

Validates that frontend AGENTESE paths are registered in the backend.
The AGENTESE registry (@node decorator) is the SINGLE SOURCE OF TRUTH.

Usage:
    cd impl/claude
    uv run python scripts/validate_path_alignment.py

What it checks:
    1. All paths in NavigationTree.tsx have @node registrations
    2. All paths in Cockpit.tsx have @node registrations
    3. All hardcoded AGENTESE paths in frontend match backend

Exit codes:
    0 - All frontend paths are registered
    1 - Some frontend paths are missing from registry

CI Integration:
    Add to .github/workflows/ci.yml:

    - name: Validate AGENTESE path alignment
      run: cd impl/claude && uv run python scripts/validate_path_alignment.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, ".")


# Frontend-only paths that don't require backend @node registration.
# These are UI composition paths that combine other AGENTESE nodes.
# Each entry must have a comment explaining WHY it's frontend-only.
FRONTEND_ONLY_PATHS = {
    # Cockpit is a pure frontend dashboard that displays multiple AGENTESE paths
    "self.cockpit",
    # Town simulation page composes world.town with a townId query param
    "world.town.simulation",
    # Inhabit page composes world.town.citizen with a citizenId query param
    "world.town.inhabit",
}


@dataclass
class ValidationReport:
    """Validation results."""

    registered_paths: set[str] = field(default_factory=set)
    frontend_paths: dict[str, set[str]] = field(default_factory=dict)  # file -> paths
    missing_paths: dict[str, set[str]] = field(default_factory=dict)  # file -> paths
    valid_paths: dict[str, set[str]] = field(default_factory=dict)  # file -> paths
    frontend_only: dict[str, set[str]] = field(default_factory=dict)  # file -> paths


def get_registered_paths() -> set[str]:
    """Get all paths registered in the AGENTESE registry."""
    from protocols.agentese.gateway import _import_node_modules
    from protocols.agentese.registry import get_registry

    _import_node_modules()
    registry = get_registry()
    return set(registry.list_paths())


def extract_agentese_paths_from_file(file_path: Path) -> set[str]:
    """
    Extract AGENTESE paths from a TypeScript/TSX file.

    Looks for patterns like:
    - path: 'world.town'
    - path: "self.memory"
    - '/world.town'
    - "/self.memory"
    - navigate('/world.codebase')
    - ['self.memory.*', { component: ... }]  (registry.tsx format)
    """
    content = file_path.read_text()
    paths: set[str] = set()

    # Pattern: path: 'context.holon.aspect' or path: "context.holon.aspect"
    path_property = re.findall(r"path:\s*['\"]([a-z]+\.[a-z_.]+)['\"]", content)
    paths.update(path_property)

    # Pattern: '/context.holon' or "/context.holon" (route paths)
    route_paths = re.findall(r"['\"]\/([a-z]+\.[a-z_.]+)['\"]", content)
    paths.update(route_paths)

    # Pattern: ['context.holon.*', ... (registry.tsx MAP entries)
    # Captures patterns with wildcards, strips the wildcard for validation
    registry_patterns = re.findall(r"\['([a-z]+\.[a-z_.]+)\*?'\s*,", content)
    paths.update(registry_patterns)

    # Filter to only valid AGENTESE contexts
    valid_contexts = {"world", "self", "concept", "void", "time"}

    # Normalize: remove trailing wildcards (e.g., "self.memory.*" → "self.memory")
    normalized = set()
    for p in paths:
        clean = p.rstrip("*").rstrip(".")
        if clean.split(".")[0] in valid_contexts:
            normalized.add(clean)

    return normalized


def print_colored(text: str, color: str) -> None:
    """Print colored text to terminal."""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def validate() -> ValidationReport:
    """Run validation against frontend files."""
    report = ValidationReport()

    # Get registered paths from backend
    print_colored("\n=== AGENTESE Path Alignment Validator ===\n", "bold")
    print("Loading backend registry...")
    report.registered_paths = get_registered_paths()
    print(f"Found {len(report.registered_paths)} registered paths\n")

    # Frontend files to check
    # These contain hardcoded AGENTESE paths that MUST match backend registry
    web_src = Path("web/src")
    files_to_check = [
        web_src / "shell" / "NavigationTree.tsx",
        web_src / "shell" / "projections" / "registry.tsx",  # PATH_REGISTRY
        web_src / "pages" / "Cockpit.tsx",
        web_src / "constants" / "jewels.ts",
    ]

    # Check each file
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"Skipping {file_path} (not found)")
            continue

        print(f"Checking {file_path}...")
        frontend_paths = extract_agentese_paths_from_file(file_path)
        report.frontend_paths[str(file_path)] = frontend_paths

        # Separate frontend-only paths from truly missing
        frontend_only = frontend_paths & FRONTEND_ONLY_PATHS
        need_backend = frontend_paths - FRONTEND_ONLY_PATHS

        # Find missing paths (excluding frontend-only)
        missing = need_backend - report.registered_paths
        valid = need_backend & report.registered_paths

        report.missing_paths[str(file_path)] = missing
        report.valid_paths[str(file_path)] = valid
        report.frontend_only[str(file_path)] = frontend_only

        if missing:
            print_colored(f"  MISSING: {len(missing)} paths not in registry", "red")
            for p in sorted(missing):
                print(f"    - {p}")
        else:
            total = len(valid) + len(frontend_only)
            suffix = f" ({len(frontend_only)} frontend-only)" if frontend_only else ""
            print_colored(f"  OK: All {total} paths valid{suffix}", "green")

    return report


def print_report(report: ValidationReport) -> None:
    """Print validation summary."""
    print_colored("\n=== Validation Summary ===\n", "bold")

    total_frontend = sum(len(paths) for paths in report.frontend_paths.values())
    total_missing = sum(len(paths) for paths in report.missing_paths.values())
    total_valid = sum(len(paths) for paths in report.valid_paths.values())
    total_frontend_only = sum(len(paths) for paths in report.frontend_only.values())

    print(f"Backend registry: {len(report.registered_paths)} paths")
    print(f"Frontend references: {total_frontend} paths")
    print_colored(f"  Registered in backend: {total_valid}", "green")
    if total_frontend_only > 0:
        print_colored(f"  Frontend-only (allowed): {total_frontend_only}", "blue")

    if total_missing > 0:
        print_colored(f"  Missing: {total_missing}", "red")
        print()
        print_colored("FAILED: Frontend references paths not in backend registry", "red")
        print()
        print("To fix:")
        print("  1. Add @node decorator to register the path, OR")
        print("  2. Add to FRONTEND_ONLY_PATHS in this script (with justification), OR")
        print("  3. Remove the path from frontend if not needed")
        print()
        print("The registry is the single source of truth.")
    else:
        print()
        print_colored("PASSED: All frontend paths are valid", "green")


def main() -> int:
    """Main entry point."""
    report = validate()
    print_report(report)

    total_missing = sum(len(paths) for paths in report.missing_paths.values())
    return 1 if total_missing > 0 else 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
