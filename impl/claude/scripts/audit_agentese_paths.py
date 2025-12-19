#!/usr/bin/env python3
"""
AGENTESE Path Audit Script

Tests every discovered path to verify it responds correctly.
Use this to catch broken paths before they reach production.

Usage:
    cd impl/claude
    uv run python scripts/audit_agentese_paths.py

Output:
    - Working paths (green)
    - Missing node paths (yellow)
    - Aspect error paths (red)
    - Summary statistics

Exit codes:
    0 - All paths working
    1 - Some paths failing
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from typing import Any

# Add impl/claude to path for imports
sys.path.insert(0, ".")


@dataclass
class AuditResult:
    """Result of auditing a single path."""

    path: str
    status: str  # "working", "missing_node", "needs_container", "aspect_error", "import_error"
    error: str | None = None
    response: Any = None


@dataclass
class AuditReport:
    """Aggregated audit results."""

    working: list[str] = field(default_factory=list)
    needs_container: list[AuditResult] = field(default_factory=list)  # Expected: require DI
    missing_node: list[AuditResult] = field(default_factory=list)
    aspect_error: list[AuditResult] = field(default_factory=list)
    import_error: list[AuditResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (
            len(self.working)
            + len(self.needs_container)
            + len(self.missing_node)
            + len(self.aspect_error)
            + len(self.import_error)
        )

    @property
    def success_rate(self) -> float:
        """Success = working + needs_container (since container paths work in production)."""
        if self.total == 0:
            return 0.0
        # Count needs_container as success since they work with DI
        working_count = len(self.working) + len(self.needs_container)
        return working_count / self.total * 100

    @property
    def fully_working(self) -> float:
        """Paths that work without any container."""
        if self.total == 0:
            return 0.0
        return len(self.working) / self.total * 100


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


async def audit_path(path: str) -> AuditResult:
    """Test a single AGENTESE path by invoking its manifest aspect."""
    from protocols.agentese.gateway import _import_node_modules
    from protocols.agentese.node import Observer
    from protocols.agentese.registry import get_registry

    # Ensure nodes are imported
    _import_node_modules()
    registry = get_registry()

    # Check if path is registered
    if not registry.has(path):
        return AuditResult(
            path=path,
            status="missing_node",
            error=f"Path '{path}' not found in registry",
        )

    # Try to resolve the node
    try:
        node = await registry.resolve(path, container=None)
        if node is None:
            # Check if this is a "needs container" case vs actual missing
            # Registry logs "Cannot instantiate X without container" for DI nodes
            return AuditResult(
                path=path,
                status="needs_container",
                error="Requires DI container (expected for service nodes)",
            )
    except ImportError as e:
        return AuditResult(
            path=path,
            status="import_error",
            error=str(e),
        )
    except Exception as e:
        return AuditResult(
            path=path,
            status="aspect_error",
            error=f"Failed to resolve node: {e}",
        )

    # Try to invoke manifest aspect
    try:
        observer = Observer.guest()
        result = await node.invoke("manifest", observer)
        return AuditResult(
            path=path,
            status="working",
            response=result,
        )
    except Exception as e:
        return AuditResult(
            path=path,
            status="aspect_error",
            error=f"manifest aspect failed: {e}",
        )


async def run_audit() -> AuditReport:
    """Run full audit of all registered paths."""
    from protocols.agentese.gateway import _import_node_modules
    from protocols.agentese.registry import get_registry

    print_colored("\n=== AGENTESE Path Audit ===\n", "bold")

    # Import all node modules
    print("Importing node modules...")
    _import_node_modules()

    # Get all registered paths
    registry = get_registry()
    paths = registry.list_paths()
    print(f"Found {len(paths)} registered paths\n")

    report = AuditReport()

    # Test each path
    for i, path in enumerate(sorted(paths), 1):
        print(f"[{i}/{len(paths)}] Testing: {path}...", end=" ", flush=True)

        result = await audit_path(path)

        if result.status == "working":
            print_colored("OK", "green")
            report.working.append(path)
        elif result.status == "needs_container":
            print_colored("NEEDS DI (OK in production)", "blue")
            report.needs_container.append(result)
        elif result.status == "missing_node":
            print_colored(f"MISSING: {result.error}", "yellow")
            report.missing_node.append(result)
        elif result.status == "import_error":
            print_colored(f"IMPORT ERROR: {result.error}", "red")
            report.import_error.append(result)
        else:
            print_colored(f"ERROR: {result.error}", "red")
            report.aspect_error.append(result)

    return report


def print_report(report: AuditReport) -> None:
    """Print the audit summary report."""
    print_colored("\n=== Audit Summary ===\n", "bold")

    print(f"Total paths: {report.total}")
    print_colored(f"Working (no DI): {len(report.working)} ({report.fully_working:.1f}%)", "green")

    if report.needs_container:
        print_colored(
            f"Needs DI container: {len(report.needs_container)} (OK in production)", "blue"
        )
        for result in report.needs_container[:5]:
            print(f"  - {result.path}")
        if len(report.needs_container) > 5:
            print(f"  ... and {len(report.needs_container) - 5} more")

    if report.missing_node:
        print_colored(f"Missing node: {len(report.missing_node)}", "yellow")
        for result in report.missing_node[:5]:
            print(f"  - {result.path}")
        if len(report.missing_node) > 5:
            print(f"  ... and {len(report.missing_node) - 5} more")

    if report.aspect_error:
        print_colored(f"Aspect errors: {len(report.aspect_error)}", "red")
        for result in report.aspect_error[:5]:
            print(f"  - {result.path}: {result.error}")
        if len(report.aspect_error) > 5:
            print(f"  ... and {len(report.aspect_error) - 5} more")

    if report.import_error:
        print_colored(f"Import errors: {len(report.import_error)}", "red")
        for result in report.import_error[:5]:
            print(f"  - {result.path}: {result.error}")
        if len(report.import_error) > 5:
            print(f"  ... and {len(report.import_error) - 5} more")

    # CI gate - consider needs_container as passing
    print()
    working_total = len(report.working) + len(report.needs_container)
    broken_count = len(report.missing_node) + len(report.aspect_error) + len(report.import_error)

    if broken_count == 0:
        print_colored(
            f"AUDIT PASSED: {working_total}/{report.total} paths functional ({report.success_rate:.1f}%)",
            "green",
        )
    else:
        print_colored(f"AUDIT FAILED: {broken_count} paths broken", "red")


async def main() -> int:
    """Main entry point."""
    report = await run_audit()
    print_report(report)

    # Return exit code - pass if no broken paths (needs_container is OK)
    broken_count = len(report.missing_node) + len(report.aspect_error) + len(report.import_error)
    return 0 if broken_count == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
