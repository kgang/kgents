"""
Domain Dependency Manifest for Compartmentalized CI.

This module defines the dependency relationships between test domains,
enabling smart CI triggering where only affected domains are tested.

Architecture:
    Foundation (poly, operad, sheaf)
         ↓
    AGENTESE (protocol layer)
         ↓
    Crown Jewels (services) ← CLI (handlers)
         ↓
    Agents (core + aux)
         ↓
    API (external interface)

Usage:
    from testing.domain_deps import get_affected_domains

    # When agentese changes, what else needs testing?
    affected = get_affected_domains("domain_agentese")
    # Returns: {"domain_agentese", "domain_crown", "domain_cli", "domain_agents_core"}
"""

from __future__ import annotations

# =============================================================================
# Domain Dependency Graph
# =============================================================================
#
# Key: domain that changed
# Value: domains that depend on it (need re-testing when key changes)
#
# This is a REVERSE dependency graph:
# - If "foundation" changes, everything depending on it needs testing
# - The graph is transitive: foundation → agentese → crown means
#   foundation change triggers both agentese AND crown tests
#
# =============================================================================

DOMAIN_DEPENDENCIES: dict[str, list[str]] = {
    # Foundation is the base - everything depends on it
    "domain_foundation": [
        "domain_agentese",
        "domain_crown",
        "domain_agents_core",
        "domain_agents_aux",
    ],
    # AGENTESE protocol - services and CLI depend on it
    "domain_agentese": [
        "domain_crown",
        "domain_cli",
        "domain_agents_core",
    ],
    # Crown Jewels - CLI handlers depend on services
    "domain_crown": [
        "domain_cli",
        "domain_api",
    ],
    # CLI - API depends on CLI for some handlers
    "domain_cli": [
        "domain_api",
    ],
    # API - leaf node, nothing depends on it
    "domain_api": [],
    # Core agents - some aux agents depend on core
    "domain_agents_core": [
        "domain_agents_aux",
    ],
    # Aux agents - leaf node
    "domain_agents_aux": [],
    # Infrastructure - many things depend on it
    "domain_infra": [
        "domain_foundation",
        "domain_agentese",
        "domain_crown",
        "domain_cli",
    ],
}

# Domains that should ALWAYS run (critical path)
ALWAYS_RUN_DOMAINS: set[str] = {
    "domain_foundation",  # Category laws must always pass
}

# Domains that can be skipped on quick iterations
SKIPPABLE_DOMAINS: set[str] = {
    "domain_agents_aux",  # Large, slow, often unchanged
    "domain_api",  # External interface, usually stable
}


def get_affected_domains(changed_domain: str) -> set[str]:
    """
    Get all domains that need testing when a specific domain changes.

    This performs transitive closure over the dependency graph.
    If A → B → C, then changing A triggers tests for A, B, AND C.

    Args:
        changed_domain: The domain that has changes (e.g., "domain_foundation")

    Returns:
        Set of all domains that need testing, including the changed domain itself

    Example:
        >>> get_affected_domains("domain_foundation")
        {"domain_foundation", "domain_agentese", "domain_crown", "domain_cli",
         "domain_agents_core", "domain_agents_aux", "domain_api"}
    """
    affected: set[str] = {changed_domain}
    queue = [changed_domain]

    while queue:
        current = queue.pop(0)
        dependents = DOMAIN_DEPENDENCIES.get(current, [])
        for dep in dependents:
            if dep not in affected:
                affected.add(dep)
                queue.append(dep)

    return affected


def get_minimal_test_set(changed_files: list[str]) -> set[str]:
    """
    Given a list of changed files, determine the minimal set of domains to test.

    Args:
        changed_files: List of file paths relative to impl/claude/

    Returns:
        Set of domain markers to run

    Example:
        >>> get_minimal_test_set(["agents/poly/types.py", "protocols/cli/main.py"])
        {"domain_foundation", "domain_agentese", "domain_crown", "domain_cli",
         "domain_agents_core", "domain_agents_aux", "domain_api"}
    """
    # Import here to avoid circular dependency with conftest
    from conftest import _DOMAIN_RULES

    triggered_domains: set[str] = set()

    for file_path in changed_files:
        for marker_name, patterns in _DOMAIN_RULES:
            if any(pattern in file_path for pattern in patterns):
                triggered_domains.add(marker_name)
                break

    # Expand to include all affected domains
    all_affected: set[str] = set()
    for domain in triggered_domains:
        all_affected.update(get_affected_domains(domain))

    # Always include critical domains
    all_affected.update(ALWAYS_RUN_DOMAINS)

    return all_affected


def get_domain_for_path(file_path: str) -> str | None:
    """
    Get the domain marker for a given file path.

    Args:
        file_path: File path relative to impl/claude/

    Returns:
        Domain marker name or None if no match
    """
    # Import here to avoid circular dependency with conftest
    from conftest import _DOMAIN_RULES

    for marker_name, patterns in _DOMAIN_RULES:
        if any(pattern in file_path for pattern in patterns):
            return marker_name
    return None


def print_domain_stats() -> None:
    """Print statistics about domain coverage (for debugging)."""
    print("Domain Dependency Graph:")
    print("=" * 60)
    for domain, deps in DOMAIN_DEPENDENCIES.items():
        affected = get_affected_domains(domain)
        print(f"{domain}:")
        print(f"  Direct deps: {deps}")
        print(f"  All affected: {affected}")
        print()


if __name__ == "__main__":
    # Quick test of the dependency graph
    print_domain_stats()

    print("\nExample: What needs testing if foundation changes?")
    print(get_affected_domains("domain_foundation"))

    print("\nExample: What needs testing if CLI changes?")
    print(get_affected_domains("domain_cli"))
