"""
CI Gate: Projection Coverage for AGENTESE Paths.

This test ensures that high-value AGENTESE paths have corresponding
frontend projections registered in web/src/shell/projections/registry.tsx.

AD-010 (Habitat Guarantee): Every AGENTESE path gets a home, not just JSON.
ConceptHome is the universal fallback, but Crown Jewels deserve dedicated
projections that showcase their full capabilities.

The test:
1. Defines REQUIRED_PROJECTIONS (high-value paths that MUST have projections)
2. Reads registry.tsx to verify entries exist
3. Reports coverage percentage and missing projections

Run with:
    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_projection_coverage.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

# =============================================================================
# Required Projections
# =============================================================================

# These high-value paths MUST have dedicated frontend projections
# They are the Crown Jewels - users should get rich experiences, not JSON dumps
REQUIRED_PROJECTIONS = [
    "self.memory",  # Brain - spatial cathedral of memory
    "self.garden",  # Garden - cultivation practice for ideas
    "self.chat",  # Chat - conversational interface
    "self.soul",  # Soul - K-gent personality and dialogue
    "world.codebase",  # Gestalt - living garden where code breathes
    "world.forge",  # Forge - developer's workshop
    "world.town",  # Town - agent simulation
    "world.park",  # Park - Westworld where hosts can say no
    "concept.gardener",  # Gardener orchestrator
    "concept.design",  # Design Language System
]

# Optional but recommended projections
RECOMMENDED_PROJECTIONS = [
    "time.differance",  # Differance traces
    "self.differance",  # Self-context differance
    "world.gallery",  # Categorical showcase
    "world.workshop",  # Event-driven builder
    "world.emergence",  # Cymatics design experience
    "self.forest",  # Forest Protocol
]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def registry_tsx_content() -> str:
    """Read the projection registry file."""
    # Navigate from test file to registry.tsx
    registry_path = (
        Path(__file__).parent.parent.parent.parent
        / "web"
        / "src"
        / "shell"
        / "projections"
        / "registry.tsx"
    )

    if not registry_path.exists():
        pytest.skip(f"Registry file not found at {registry_path}")

    return registry_path.read_text()


def path_to_registry_pattern(path: str) -> list[str]:
    """
    Convert AGENTESE path to patterns that should appear in registry.

    Returns multiple patterns to check for both exact and wildcard matches.

    Example:
        "self.memory" -> ["self.memory", "self.memory.*", "'self.memory'"]
    """
    patterns = [
        f"'{path}'",  # Exact match in quotes
        f'"{path}"',  # Double quotes variant
        f"'{path}.*'",  # Wildcard pattern
        f'"{path}.*"',  # Wildcard double quotes
        f"'{path}.'",  # Prefix pattern
    ]
    return patterns


# =============================================================================
# Required Projection Tests
# =============================================================================


class TestRequiredProjectionCoverage:
    """
    Required projections MUST be registered.

    AD-010: The Habitat Guarantee ensures every path gets a home.
    Crown Jewels deserve dedicated projections, not just ConceptHome.
    """

    @pytest.mark.parametrize("path", REQUIRED_PROJECTIONS)
    def test_required_projection_registered(self, registry_tsx_content: str, path: str):
        """Each required path must have a projection entry."""
        patterns = path_to_registry_pattern(path)

        # Check if any pattern matches
        found = any(p in registry_tsx_content for p in patterns)

        assert found, (
            f"Required projection missing for '{path}'. "
            f"Add entry to web/src/shell/projections/registry.tsx "
            f"(PATH_REGISTRY or TYPE_REGISTRY)"
        )

    def test_all_required_projections_exist(self, registry_tsx_content: str):
        """Sanity check: at least 8 of 10 required projections must exist."""
        found_count = 0
        missing = []

        for path in REQUIRED_PROJECTIONS:
            patterns = path_to_registry_pattern(path)
            if any(p in registry_tsx_content for p in patterns):
                found_count += 1
            else:
                missing.append(path)

        coverage = found_count / len(REQUIRED_PROJECTIONS) * 100

        assert found_count >= 8, (
            f"Only {found_count}/{len(REQUIRED_PROJECTIONS)} required projections found "
            f"({coverage:.0f}%). Missing: {missing}"
        )


# =============================================================================
# Recommended Projection Tests
# =============================================================================


class TestRecommendedProjectionCoverage:
    """
    Recommended projections SHOULD be registered.

    These are not strictly required but enhance the user experience.
    """

    def test_recommended_projection_coverage(self, registry_tsx_content: str):
        """Report recommended projection coverage (advisory, not enforced)."""
        found_count = 0
        missing = []

        for path in RECOMMENDED_PROJECTIONS:
            patterns = path_to_registry_pattern(path)
            if any(p in registry_tsx_content for p in patterns):
                found_count += 1
            else:
                missing.append(path)

        coverage = found_count / len(RECOMMENDED_PROJECTIONS) * 100

        print("\n=== RECOMMENDED PROJECTION COVERAGE ===")
        print(f"Found: {found_count}/{len(RECOMMENDED_PROJECTIONS)} ({coverage:.0f}%)")

        if missing:
            print("Missing (consider adding):")
            for path in missing:
                print(f"  - {path}")

        # Advisory only - don't fail, just report
        # At least half should exist
        if coverage < 50:
            print(
                f"\n⚠️ Low coverage warning: Only {coverage:.0f}% of recommended projections exist"
            )


# =============================================================================
# Registry Structure Tests
# =============================================================================


class TestRegistryStructure:
    """
    Verify the projection registry has proper structure.
    """

    def test_has_path_registry(self, registry_tsx_content: str):
        """Registry must have PATH_REGISTRY map."""
        assert "PATH_REGISTRY" in registry_tsx_content, "Missing PATH_REGISTRY in registry.tsx"

    def test_has_type_registry(self, registry_tsx_content: str):
        """Registry must have TYPE_REGISTRY map."""
        assert "TYPE_REGISTRY" in registry_tsx_content, "Missing TYPE_REGISTRY in registry.tsx"

    def test_has_resolve_projection(self, registry_tsx_content: str):
        """Registry must have resolveProjection function."""
        assert "resolveProjection" in registry_tsx_content, (
            "Missing resolveProjection function in registry.tsx"
        )

    def test_has_concept_home_fallback(self, registry_tsx_content: str):
        """Registry must have ConceptHome as fallback (AD-010 Habitat Guarantee)."""
        assert "ConceptHome" in registry_tsx_content, (
            "Missing ConceptHomeProjection fallback (AD-010 requires every path gets a home)"
        )


# =============================================================================
# Coverage Statistics
# =============================================================================


class TestProjectionStatistics:
    """Informational statistics about projection coverage."""

    def test_print_projection_stats(self, registry_tsx_content: str):
        """Print projection coverage statistics."""
        # Count PATH_REGISTRY entries (approximate by counting pattern entries)
        path_entries = registry_tsx_content.count("{ component:")

        # Count lazy imports (projection components)
        lazy_imports = registry_tsx_content.count("lazy(() =>")

        print("\n=== PROJECTION REGISTRY STATS ===")
        print(f"Lazy-loaded projections: {lazy_imports}")
        print(f"Registry entries (approx): {path_entries}")

        # Check for all five contexts
        contexts = ["self.", "world.", "concept.", "time.", "void."]
        print("\nContexts covered:")
        for ctx in contexts:
            if f"'{ctx}" in registry_tsx_content or f'"{ctx}' in registry_tsx_content:
                print(f"  ✓ {ctx.rstrip('.')}")
            else:
                print(f"  ✗ {ctx.rstrip('.')}")

        # Combined coverage
        all_paths = REQUIRED_PROJECTIONS + RECOMMENDED_PROJECTIONS
        covered = 0
        for path in all_paths:
            patterns = path_to_registry_pattern(path)
            if any(p in registry_tsx_content for p in patterns):
                covered += 1

        total_coverage = covered / len(all_paths) * 100
        print(f"\nTotal coverage: {covered}/{len(all_paths)} ({total_coverage:.0f}%)")
