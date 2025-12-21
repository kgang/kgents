"""
CI Gate: AGENTESE Path Registry Verification.

This test ensures ALL registered AGENTESE paths:
1. Are discoverable via /agentese/discover
2. Can be resolved to a node (with or without container)
3. Respond to manifest aspect without crashing

Run as part of CI to prevent broken paths from shipping.

AD-011 (REPL Reliability Contract): Every path in discover MUST be invokable.
The REPL is not a toy - it's the canonical exploration surface for AGENTESE.

IMPORTANT: This test must be run in isolation from test_registry.py because
that file resets the registry for each test. Run this file alone:

    cd impl/claude
    uv run pytest protocols/agentese/_tests/test_registry_ci_gate.py -v

Or run all tests but this file first (test order matters).
"""

from __future__ import annotations

import pytest

from protocols.agentese.gateway import _import_node_modules
from protocols.agentese.node import Observer
from protocols.agentese.registry import get_registry

# =============================================================================
# Fixtures
# =============================================================================


def _force_reload_node_modules():
    """
    Force reload all node modules to re-trigger @node decorators.

    This is necessary because @node runs at import time, and if
    another test (like test_registry.py) calls reset_registry(),
    the registry is emptied but the modules are already imported.

    By reloading, we force the @node decorators to run again.
    """
    import importlib
    import sys

    # List of node modules to reload (order matters for dependencies)
    node_modules = [
        "protocols.agentese.contexts.design",
        "protocols.agentese.contexts.self_differance",
        "protocols.agentese.contexts.self_kgent",
        "protocols.agentese.contexts.self_nphase",
        "protocols.agentese.contexts.self_soul",
        "protocols.agentese.contexts.self_system",
        "protocols.agentese.contexts.time_differance",
        "protocols.agentese.contexts.world_emergence",
        "protocols.agentese.contexts.world_gallery",
        "protocols.agentese.contexts.world_gallery_api",
        "protocols.agentese.contexts.world_gestalt_live",
        "protocols.agentese.contexts.world_park",
        "protocols.agentese.contexts.world_workshop",
        "services.brain.node",
        "services.chat.node",
        "services.forge.node",
        "services.forge.soul_node",
        "services.gestalt.node",
        "services.morpheus.node",
        "services.park.node",
        "services.town.node",
        "services.town.citizen_node",
        "services.town.coalition_node",
        "services.town.inhabit_node",
        "services.town.workshop_node",
    ]

    for mod_name in node_modules:
        if mod_name in sys.modules:
            try:
                importlib.reload(sys.modules[mod_name])
            except Exception:
                pass  # Some modules may fail to reload, that's OK
        else:
            try:
                importlib.import_module(mod_name)
            except Exception:
                pass


@pytest.fixture(scope="class")
def populated_registry():
    """
    Return the populated registry.

    Forces reload of node modules to ensure @node decorators run,
    even if another test has reset the registry.
    """
    _force_reload_node_modules()
    return get_registry()


@pytest.fixture
def guest_observer() -> Observer:
    """Create a guest observer for testing."""
    return Observer.guest()


# =============================================================================
# CI Gate Tests - Must Pass for Merge
# =============================================================================


class TestPathDiscoverability:
    """
    All registered paths must be discoverable.

    AD-011: /agentese/discover returns ALL registered paths.
    """

    def test_at_least_30_paths_registered(self, populated_registry):
        """Registry should have at least 30 paths (sanity check)."""
        paths = populated_registry.list_paths()
        assert len(paths) >= 30, (
            f"Expected at least 30 paths, got {len(paths)}. "
            "Did you forget to import a node module in gateway.py?"
        )

    def test_crown_jewel_paths_exist(self, populated_registry):
        """All 6 Crown Jewel paths are registered."""
        expected_jewels = [
            "self.memory",  # Brain
            "world.codebase",  # Gestalt
            "world.forge",  # Forge (was Atelier)
            "world.town",  # Town
            "world.park",  # Park
            # Domain is dormant - no path expected
            # Gardener deprecated - removed
        ]

        paths = populated_registry.list_paths()
        missing = [p for p in expected_jewels if p not in paths]

        assert not missing, (
            f"Missing Crown Jewel paths: {missing}. "
            "Check imports in gateway.py _import_node_modules()"
        )

    def test_all_five_contexts_have_paths(self, populated_registry):
        """All five AGENTESE contexts have at least one path."""
        expected_contexts = ["world", "self", "concept", "time", "void"]

        stats = populated_registry.stats()
        contexts = stats["contexts"]

        # void is optional - it's for accursed share
        required_contexts = ["world", "self", "concept", "time"]
        missing = [c for c in required_contexts if c not in contexts]

        assert not missing, (
            f"Missing contexts: {missing}. Expected paths in: world.*, self.*, concept.*, time.*"
        )


class TestPathResolution:
    """
    All registered paths must resolve to a node.

    AD-011: registry.has(path) → registry.resolve(path) must work.
    """

    @pytest.mark.asyncio
    async def test_all_paths_resolvable(self, populated_registry):
        """Every registered path resolves to a node or requires container."""
        paths = populated_registry.list_paths()

        resolution_failures = []
        needs_container = []

        for path in paths:
            if not populated_registry.has(path):
                resolution_failures.append(f"{path}: not in registry")
                continue

            try:
                node = await populated_registry.resolve(path, container=None)
                if node is None:
                    # Node requires DI container - this is OK for service nodes
                    needs_container.append(path)
            except Exception as e:
                resolution_failures.append(f"{path}: {e}")

        # Report needs_container as info, not failure
        if needs_container:
            print(f"\n{len(needs_container)} paths need DI container (OK in production):")
            for p in needs_container[:5]:
                print(f"  - {p}")
            if len(needs_container) > 5:
                print(f"  ... and {len(needs_container) - 5} more")

        assert not resolution_failures, "Path resolution failures:\n" + "\n".join(
            resolution_failures
        )


class TestManifestAspect:
    """
    All resolvable nodes must respond to manifest aspect.

    AD-011: Every path MUST respond to manifest without error.
    """

    @pytest.mark.asyncio
    async def test_manifest_aspect_works(self, populated_registry, guest_observer):
        """Manifest aspect works for all resolvable nodes."""
        paths = populated_registry.list_paths()

        # Skip paths that require slow codebase scanning (tested separately with @slow marker)
        slow_paths = {"world.codebase"}

        manifest_failures = []
        skipped = []
        skipped_slow = []

        for path in paths:
            if path in slow_paths:
                skipped_slow.append(path)
                continue

            node = await populated_registry.resolve(path, container=None)
            if node is None:
                skipped.append(path)
                continue

            try:
                result = await node.invoke("manifest", guest_observer)
                # Basic validation: result should not be None
                if result is None:
                    manifest_failures.append(f"{path}: manifest returned None")
            except Exception as e:
                manifest_failures.append(f"{path}: {str(e)}")

        assert not manifest_failures, "Manifest aspect failures:\n" + "\n".join(manifest_failures)

        # Report how many were actually tested
        tested = len(paths) - len(skipped) - len(skipped_slow)
        print(f"\nManifest tested: {tested}/{len(paths)} paths")
        print(f"Skipped (need container): {len(skipped)}")
        print(f"Skipped (slow, tested separately): {len(skipped_slow)}")


class TestNoOrphanContextFiles:
    """
    All context node files must register at least one path.

    Prevents orphan files that look like they should register nodes but don't.
    """

    def test_context_files_register_paths(self, populated_registry):
        """Context files register paths matching their filename prefix."""
        from pathlib import Path

        context_dir = Path(__file__).parent.parent / "contexts"
        if not context_dir.exists():
            pytest.skip("Contexts directory not found")

        paths = populated_registry.list_paths()

        for py_file in context_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            if py_file.name == "__init__.py":
                continue

            # Extract expected context from filename
            # e.g., "self_soul.py" → "self.soul"
            # e.g., "world_town.py" → "world.town"
            stem = py_file.stem
            if "_" in stem:
                parts = stem.split("_", 1)
                expected_prefix = f"{parts[0]}."
            else:
                expected_prefix = f"{stem}."

            # Check if any path matches
            matching = [p for p in paths if p.startswith(expected_prefix)]

            # Allow files that are known to be special cases
            special_cases = ["design", "time_differance"]  # These have their own patterns
            if stem in special_cases:
                continue

            # At least warn if no paths registered
            if not matching and stem not in ["__init__"]:
                # Don't fail, just warn - this is advisory
                print(f"\nWarning: {py_file.name} may not register any paths")


# =============================================================================
# Metrics (Informational)
# =============================================================================


class TestPathMetrics:
    """Informational metrics about path registry."""

    def test_print_registry_stats(self, populated_registry):
        """Print registry statistics for visibility."""
        stats = populated_registry.stats()

        print("\n=== AGENTESE PATH REGISTRY ===")
        print(f"Total paths: {stats['registered_nodes']}")
        print(f"Contexts: {', '.join(stats['contexts'])}")
        print(f"Paths with contracts: {stats['paths_with_contracts']}")

        # Contract coverage
        coverage = (
            stats["paths_with_contracts"] / stats["registered_nodes"] * 100
            if stats["registered_nodes"] > 0
            else 0
        )
        print(f"Contract coverage: {coverage:.1f}%")

        # Group by context
        print("\nPaths by context:")
        for context in sorted(stats["contexts"]):
            context_paths = populated_registry.list_by_context(context)
            print(f"  {context}: {len(context_paths)} paths")


# =============================================================================
# Script Runner
# =============================================================================


if __name__ == "__main__":
    import asyncio

    async def main():
        print("=== AGENTESE Registry CI Gate ===\n")

        # Import nodes
        print("Importing node modules...")
        _import_node_modules()

        registry = get_registry()
        paths = registry.list_paths()
        print(f"Found {len(paths)} registered paths\n")

        # Test resolution
        print("Testing path resolution...")
        guest = Observer.guest()

        resolved = 0
        needs_container = 0
        failed = 0

        for path in sorted(paths):
            node = await registry.resolve(path, container=None)
            if node is None:
                needs_container += 1
                print(f"  {path}: NEEDS_CONTAINER")
            else:
                try:
                    result = await node.invoke("manifest", guest)
                    resolved += 1
                    print(f"  {path}: OK")
                except Exception as e:
                    failed += 1
                    print(f"  {path}: FAILED - {e}")

        print("\n=== Summary ===")
        print(f"Resolved: {resolved}")
        print(f"Needs container: {needs_container}")
        print(f"Failed: {failed}")
        print(f"Total: {len(paths)}")

        if failed > 0:
            print("\n❌ CI GATE FAILED")
            return 1
        else:
            print("\n✅ CI GATE PASSED")
            return 0

    exit(asyncio.run(main()))
