"""
Canary Test: NodeRegistry xdist Race Condition Detection.

This test catches registry state pollution in parallel test execution for
AGENTESE nodes. It complements the OperadRegistry canary.

## The Problem

NodeRegistry is a module-level singleton populated by @node decorators:

```python
@node("world.codebase")
class GestaltNode(BaseLogosNode):
    ...
```

The @node decorator runs at import time and registers the path. In xdist:
- Workers import different modules in different orders
- Some workers may not import a service's node.py at all
- Tests checking registry.has("world.codebase") fail inconsistently

## The Solution Pattern

```python
# In conftest.py (e.g., protocols/agentese/_tests/conftest.py)

@pytest.fixture(scope="session", autouse=True)
def ensure_all_nodes_imported():
    '''Import all node modules at session start.'''
    from protocols.agentese.gateway import _import_node_modules
    _import_node_modules()
```

Key difference from OperadRegistry:
- Nodes use _import_node_modules() which imports all services
- This function already exists in gateway.py
- Just need to call it at session start

## This Canary Test

Verifies NodeRegistry is properly populated across all workers.
Failure in parallel = fixture not reaching all workers.
"""

from __future__ import annotations

import pytest

from protocols.agentese.registry import get_registry

# =============================================================================
# Canary Tests
# =============================================================================


class TestXdistNodeRegistryCanary:
    """
    Canary tests for xdist NodeRegistry state.

    Detect if session fixture failed to populate the registry.
    """

    # Crown Jewel paths that should always be present
    CROWN_JEWEL_PATHS = [
        "self.memory",  # Brain
        "self.chat",  # Chat
        "world.codebase",  # Gestalt
        "world.town",  # Town
        "world.park",  # Park
        "world.forge",  # Forge
        "world.morpheus",  # Morpheus
    ]

    def test_registry_not_empty(self) -> None:
        """
        CANARY: NodeRegistry should never be empty.

        If empty, ensure_all_nodes_imported() fixture didn't run.
        """
        registry = get_registry()
        paths = registry.list_paths()

        assert len(paths) > 0, (
            "NodeRegistry is empty! "
            "The session fixture ensure_all_nodes_imported() didn't run. "
            "Check protocols/agentese/_tests/conftest.py"
        )

    def test_crown_jewels_present(self) -> None:
        """
        CANARY: All Crown Jewel paths should be registered.

        These are the core service nodes that must always be available.
        """
        registry = get_registry()

        missing = []
        for path in self.CROWN_JEWEL_PATHS:
            if not registry.has(path):
                missing.append(path)

        assert not missing, (
            f"Missing Crown Jewel paths: {missing}. "
            "The session fixture may be incomplete or not running."
        )

    def test_registry_count_reasonable(self) -> None:
        """
        CANARY: Should have at least 20 paths (we have 50+).

        Low count = partial imports. Very high = possible pollution.
        """
        registry = get_registry()
        paths = registry.list_paths()
        count = len(paths)

        assert count >= 20, (
            f"Only {count} AGENTESE paths registered (expected 20+). Present: {paths[:10]}..."
        )

        # Sanity upper bound
        assert count < 200, f"Unusually high path count: {count}. Possible test pollution."

    def test_gestalt_node_present(self) -> None:
        """
        CANARY: world.codebase (GestaltNode) must be registered.

        This was the specific path that failed in the original issue.
        """
        registry = get_registry()
        assert registry.has("world.codebase"), (
            "world.codebase not registered! "
            "GestaltNode failed to register. "
            "Check that ensure_all_nodes_imported() imports services.gestalt"
        )


class TestXdistNodeRegistryDiagnostics:
    """Diagnostic tests for debugging parallel issues."""

    def test_print_registry_state(self) -> None:
        """Print current NodeRegistry state for debugging."""
        import os

        registry = get_registry()
        paths = sorted(registry.list_paths())
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")

        print(f"\n=== NODE REGISTRY STATE (worker: {worker_id}) ===")
        print(f"Total paths: {len(paths)}")
        print(f"Contexts: {set(p.split('.')[0] for p in paths if '.' in p)}")
        print(f"Sample paths: {paths[:15]}...")

        assert len(paths) >= 1, "Registry completely empty"

    def test_print_contracts_coverage(self) -> None:
        """Print contract coverage for debugging."""
        import os

        registry = get_registry()
        all_contracts = registry.get_all_contracts()
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")

        print(f"\n=== CONTRACT COVERAGE (worker: {worker_id}) ===")
        print(f"Paths with contracts: {len(all_contracts)}")
        print(f"Paths: {list(all_contracts.keys())}")

        # Sanity
        assert len(all_contracts) >= 5, "Too few contracts"


class TestNodeRegistryRegressionGuard:
    """Regression guards for specific xdist issues."""

    def test_gestalt_not_lost(self) -> None:
        """
        Regression: world.codebase was missing in some workers.

        Root cause: GestaltNode only imported when running gestalt tests.
        Other workers never imported services.gestalt.node.

        Fix: ensure_all_nodes_imported() calls _import_node_modules()
        which imports all service node modules.
        """
        registry = get_registry()
        assert registry.has("world.codebase"), (
            "world.codebase missing! Fixed by ensure_all_nodes_imported() "
            "in protocols/agentese/_tests/conftest.py"
        )

    def test_brain_node_present(self) -> None:
        """
        Regression guard: self.memory (BrainNode) should be present.

        BrainNode is imported via services.brain.node.
        """
        registry = get_registry()
        assert registry.has("self.memory"), "self.memory (BrainNode) missing"

    def test_all_town_nodes_present(self) -> None:
        """
        Regression: Town nodes were partially present.

        Town has multiple nodes (town, citizen, coalition, etc.).
        If one is present, all should be present.
        """
        town_paths = [
            "world.town",
            "world.town.citizen",
            "world.town.coalition",
        ]

        registry = get_registry()
        present = [p for p in town_paths if registry.has(p)]
        missing = [p for p in town_paths if not registry.has(p)]

        # Either all or none (partial is the bug)
        if present and missing:
            pytest.fail(f"Partial Town node registration! Present: {present}, Missing: {missing}")

        assert len(present) == len(town_paths), f"Missing Town nodes: {missing}"


# =============================================================================
# Integration with OperadRegistry Canary
# =============================================================================


class TestCrossRegistryConsistency:
    """
    Verify both registries are populated in the same worker.

    If OperadRegistry is populated but NodeRegistry isn't (or vice versa),
    the conftest.py fixtures aren't coordinated.
    """

    def test_both_registries_populated(self) -> None:
        """Both OperadRegistry and NodeRegistry should be populated."""
        from agents.operad.core import OperadRegistry

        operads = OperadRegistry.all_operads()
        registry = get_registry()
        nodes = registry.list_paths()

        operad_count = len(operads)
        node_count = len(nodes)

        # Both should be populated
        assert operad_count > 0, "OperadRegistry empty but checking NodeRegistry"
        assert node_count > 0, "NodeRegistry empty but OperadRegistry has data"

        # Both should have reasonable counts
        assert operad_count >= 10, f"OperadRegistry underpopulated: {operad_count}"
        assert node_count >= 20, f"NodeRegistry underpopulated: {node_count}"
