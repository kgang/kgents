"""
Test configuration for Living Docs tests.

Provides module-scoped fixtures for test performance optimization.
The teaching index is pre-populated once per module and shared across tests.

AGENTESE: concept.docs.test

Teaching:
    gotcha: The teaching index is populated lazily. If you need to test
            cache behavior, use clear_teaching_index() in your test setup.
            (Evidence: test_teaching.py::test_index_lifecycle)

    gotcha: Tests that modify teaching fixtures should use function-scoped
            fixtures instead of module-scoped to avoid cross-test pollution.
            (Evidence: test_hydrator.py::test_isolated_context)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from services.living_docs.hydrator import HydrationContext, Hydrator
    from services.living_docs.teaching import TeachingResult


# =============================================================================
# Module-Scoped Teaching Index
# =============================================================================


@pytest.fixture(scope="module", autouse=True)
def _populate_teaching_index_at_module_start() -> None:
    """
    Pre-populate the teaching index when the test module loads.

    This ensures:
    1. The expensive codebase scan happens once per module
    2. All tests in the module share the same cached index
    3. Test timing is predictable (scan cost is amortized)

    The autouse=True ensures this runs before ANY test in the module.
    """
    from services.living_docs.teaching import get_teaching_index

    # Force population (this is the expensive call, done once)
    get_teaching_index()


@pytest.fixture(scope="module")
def teaching_index() -> list["TeachingResult"]:
    """
    Get the pre-populated teaching index.

    Use this fixture when you need to access teaching results directly
    without going through the Hydrator.

    Example:
        def test_teaching_count(teaching_index):
            assert len(teaching_index) > 0
    """
    from services.living_docs.teaching import get_teaching_index

    return get_teaching_index()


@pytest.fixture
def fresh_teaching_index() -> list["TeachingResult"]:
    """
    Get a freshly-populated teaching index (function-scoped).

    Use this fixture when you need to test cache invalidation or
    when your test modifies docstrings and needs to see the changes.

    WARNING: This is slower than teaching_index. Use sparingly.
    """
    from services.living_docs.teaching import clear_teaching_index, get_teaching_index

    clear_teaching_index()
    return get_teaching_index(force_refresh=True)


# =============================================================================
# Cached Hydrator Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def hydrator() -> "Hydrator":
    """
    Get a cached Hydrator instance (module-scoped).

    Uses the module-level teaching index, so all hydrate() calls
    are fast (no codebase scanning).

    Example:
        def test_hydrate_returns_context(hydrator):
            ctx = hydrator.hydrate("brain persistence")
            assert ctx.task == "brain persistence"
    """
    from services.living_docs.hydrator import Hydrator

    return Hydrator()


@pytest.fixture
def fresh_hydrator() -> "Hydrator":
    """
    Get a fresh Hydrator instance (function-scoped).

    Use this when you need isolated Hydrator state or when
    testing Hydrator construction behavior.
    """
    from services.living_docs.hydrator import Hydrator

    return Hydrator()


# =============================================================================
# Pre-Computed Hydration Results (for common keywords)
# =============================================================================


@pytest.fixture(scope="module")
def common_hydration_results(hydrator: "Hydrator") -> dict[str, "HydrationContext"]:
    """
    Pre-computed hydration results for common test keywords.

    This caches the results of hydrating common keywords, further
    reducing test time for tests that just need to verify hydration output.

    Available keys: "brain", "agentese", "projector", "witness", "town"
    """
    return {
        "brain": hydrator.hydrate("brain persistence"),
        "agentese": hydrator.hydrate("agentese node"),
        "projector": hydrator.hydrate("wasm projector"),
        "witness": hydrator.hydrate("witness mark"),
        "town": hydrator.hydrate("town citizen"),
    }


# =============================================================================
# Test Path Utilities
# =============================================================================


@pytest.fixture(scope="module")
def living_docs_path() -> Path:
    """Path to the living_docs service directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="module")
def impl_claude_path() -> Path:
    """Path to impl/claude directory."""
    return Path(__file__).parent.parent.parent.parent
