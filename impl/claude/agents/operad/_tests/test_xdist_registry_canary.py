"""
Canary Test: OperadRegistry xdist Race Condition Detection.

This test exists to catch registry state pollution in parallel test execution.
It should ALWAYS be run with other tests to detect cross-test interference.

## The Problem

Global singletons like OperadRegistry use class-level state that persists
across the Python process lifetime. In pytest-xdist parallel execution:

1. Each worker is a separate process with independent Python state
2. Module-level registrations (OperadRegistry.register(...)) run once at import
3. Different test files import different modules in different orders
4. Workers may have different registry states based on import order

## The Solution Pattern

```python
# In conftest.py at the appropriate level (e.g., agents/conftest.py)

@pytest.fixture(scope="session", autouse=True)
def ensure_all_operads_imported():
    '''Import all operads at session start to ensure consistent state.'''
    from agents.town.operad import TOWN_OPERAD  # noqa: F401
    from agents.brain.operad import BRAIN_OPERAD  # noqa: F401
    # ... etc
```

Key insights:
- scope="session": Runs once per worker process at session start
- autouse=True: Applies to all tests automatically
- Import (don't reset): Module-level registration only runs once per process
- Conftest placement: Must be in a parent directory of all affected tests

## Why NOT Reset + Re-import

The naive approach of reset() + re-import DOESN'T WORK because:
1. Python caches modules in sys.modules
2. Re-importing a cached module doesn't re-execute module-level code
3. OperadRegistry.register(...) is module-level code
4. After reset(), re-import leaves registry empty

## This Canary Test

This test verifies that the session fixture properly populated the registry.
If it fails in parallel execution but passes individually, the fixture is
not reaching all workers.

Run verification:
    # Should pass - includes local conftest.py
    uv run pytest agents/operad/_tests/test_xdist_registry_canary.py -v

    # Should also pass - uses agents/conftest.py
    uv run pytest agents/operad/_tests/test_xdist_registry_canary.py -n 5 -v

    # The real test - run with other tests
    uv run pytest agents/ -n 5 -q --tb=no | grep -E "(PASSED|FAILED).*canary"
"""

from __future__ import annotations

import pytest

from agents.operad.core import OperadRegistry

# =============================================================================
# Canary Tests
# =============================================================================


class TestXdistRegistryCanary:
    """
    Canary tests for xdist registry state.

    These tests detect if the session fixture failed to populate the registry.
    A failure here indicates the conftest.py fixture isn't reaching this worker.
    """

    # Minimum expected operads (conservative - always present)
    MINIMUM_EXPECTED = [
        "AgentOperad",  # Always registered in core.py
        "TownOperad",
        "FlowOperad",
        "BrainOperad",
        "DirectorOperad",
        "AtelierOperad",
    ]

    def test_registry_not_empty(self) -> None:
        """
        CANARY: Registry should never be empty in any worker.

        If this fails, the session fixture didn't run before this test.
        Check that agents/conftest.py has ensure_all_operads_imported().
        """
        registered = OperadRegistry.all_operads()
        assert len(registered) > 0, (
            "OperadRegistry is empty! "
            "The session fixture ensure_all_operads_imported() didn't run. "
            "Check agents/conftest.py"
        )

    def test_minimum_operads_present(self) -> None:
        """
        CANARY: Core operads should always be registered.

        If this fails with only 'AgentOperad' present, the session fixture
        didn't import all operad modules.
        """
        registered = OperadRegistry.all_operads()

        missing = [name for name in self.MINIMUM_EXPECTED if name not in registered]
        assert not missing, (
            f"Missing operads: {missing}. "
            f"Present: {list(registered.keys())}. "
            "The session fixture may be incomplete."
        )

    def test_registry_count_reasonable(self) -> None:
        """
        CANARY: Should have at least 10 operads (we have ~15+ registered).

        A low count suggests partial imports. A very high count suggests
        test pollution (operads registered by tests not cleaned up).
        """
        registered = OperadRegistry.all_operads()
        count = len(registered)

        assert count >= 10, (
            f"Only {count} operads registered (expected 10+). Session fixture may be incomplete."
        )

        # Upper bound sanity check (we shouldn't have 50+ operads)
        assert count < 50, (
            f"Unusually high operad count: {count}. "
            "Possible test pollution or duplicate registrations."
        )

    def test_agent_operad_always_first(self) -> None:
        """
        CANARY: AgentOperad should always be present (registered in core.py).

        If even AgentOperad is missing, something is fundamentally broken
        with the import system.
        """
        registered = OperadRegistry.all_operads()
        assert "AgentOperad" in registered, (
            "AgentOperad not registered! This is registered at module level "
            "in agents/operad/core.py and should ALWAYS be present."
        )


class TestXdistRegistryDiagnostics:
    """
    Diagnostic tests that print useful debugging info.

    These don't assert (except for sanity), but print state for debugging.
    """

    def test_print_registry_state(self) -> None:
        """Print current registry state for debugging parallel issues."""
        import os

        registered = OperadRegistry.all_operads()

        # Get worker ID if running under xdist
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")

        print(f"\n=== REGISTRY STATE (worker: {worker_id}) ===")
        print(f"Total operads: {len(registered)}")
        print(f"Operads: {sorted(registered.keys())}")

        # Sanity assert so test isn't skipped
        assert len(registered) >= 1, "Registry completely empty"


# =============================================================================
# Regression Guard
# =============================================================================


class TestRegistryRegressionGuard:
    """
    Regression guards for specific xdist issues we've encountered.

    Each test documents a specific failure mode we've fixed.
    """

    def test_town_operad_not_lost(self) -> None:
        """
        Regression: TownOperad was missing in some workers.

        Root cause: tests/test_registry_ci_gate.py called import_all_operads()
        at module level, but that only ran in workers that imported that file.
        Other workers never got TownOperad.

        Fix: Move import to session-scoped fixture in agents/conftest.py.
        """
        operad = OperadRegistry.get("TownOperad")
        assert operad is not None, (
            "TownOperad missing! This regression was fixed by adding "
            "ensure_all_operads_imported() fixture to agents/conftest.py"
        )

    def test_flow_operads_all_present(self) -> None:
        """
        Regression: Flow operads (Chat, Research, Collaboration) were missing.

        These are all registered in agents/f/operad.py. If one is present,
        all should be present.
        """
        flow_operads = ["FlowOperad", "ChatOperad", "ResearchOperad", "CollaborationOperad"]

        registered = OperadRegistry.all_operads()
        present = [name for name in flow_operads if name in registered]
        missing = [name for name in flow_operads if name not in registered]

        # Either all or none (partial is the bug)
        assert len(missing) == 0 or len(present) == 0, (
            f"Partial flow operad registration detected! "
            f"Present: {present}, Missing: {missing}. "
            "This indicates import ordering issues."
        )

        # Should have all
        assert len(present) == 4, f"Missing flow operads: {missing}"


# =============================================================================
# How to Debug xdist Registry Issues
# =============================================================================

"""
## Debugging Checklist

1. **Run the canary alone**:
   ```
   uv run pytest agents/operad/_tests/test_xdist_registry_canary.py -v
   ```
   Should pass. If it fails, the session fixture itself is broken.

2. **Run canary with xdist**:
   ```
   uv run pytest agents/operad/_tests/test_xdist_registry_canary.py -n 5 -v
   ```
   Should pass. If it fails, the fixture isn't running in all workers.

3. **Run canary with other agent tests**:
   ```
   uv run pytest agents/ -n 5 -q --tb=line | grep canary
   ```
   Should pass. If it fails, check conftest.py placement.

4. **Check which conftest.py applies**:
   ```
   uv run pytest agents/operad/_tests/test_xdist_registry_canary.py --collect-only -q
   ```
   Look at "collected" output - it should show which conftest files were loaded.

5. **Print registry state per worker**:
   Run test_print_registry_state with -s flag:
   ```
   uv run pytest agents/operad/_tests/test_xdist_registry_canary.py::TestXdistRegistryDiagnostics -n 5 -s -v
   ```
   Each worker should print the same list of operads.

## Common Issues

1. **Fixture in wrong conftest.py**: Move to parent directory
2. **Missing autouse=True**: Fixture doesn't run automatically
3. **scope="function" instead of "session"**: Runs too late, per-test
4. **Reset before import**: Clears registry, re-import doesn't refill it
5. **Import at module level in test file**: Only runs for that file's workers

## The Golden Rule

For module-level singleton registries:
- NEVER reset (re-import won't re-register)
- ALWAYS use scope="session" fixtures
- ALWAYS place fixture in parent conftest.py of ALL affected tests
"""
