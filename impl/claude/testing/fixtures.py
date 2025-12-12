"""
Type-safe fixture factory for kgents tests.

Philosophy: Mock types should satisfy mypy without verbose cast() boilerplate.

Usage:
    from testing.fixtures import as_umwelt

    # In test code (replaces cast("Umwelt[Any, Any]", mock))
    observer = as_umwelt(MockUmwelt())

    # In fixtures
    @pytest.fixture
    def observer() -> Umwelt[Any, Any]:
        return as_umwelt(MockUmwelt())
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from bootstrap.types import Agent
    from bootstrap.umwelt import Umwelt


def as_umwelt(mock: Any) -> Umwelt[Any, Any]:
    """
    Cast a mock to Umwelt[Any, Any].

    Convenience function for the most common cast pattern in AGENTESE tests.
    Replaces verbose `cast("Umwelt[Any, Any]", mock)` patterns.

    Args:
        mock: A MockUmwelt or similar mock object

    Returns:
        The mock cast as Umwelt[Any, Any]

    Example:
        # Old pattern:
        result = await node.manifest(cast("Umwelt[Any, Any]", MockUmwelt()))

        # New pattern:
        result = await node.manifest(as_umwelt(MockUmwelt()))
    """
    return cast("Umwelt[Any, Any]", mock)


def as_agent(mock: Any) -> Agent[Any, Any]:
    """
    Cast a mock to Agent[Any, Any].

    Convenience function for agent-related tests.

    Args:
        mock: A mock agent object

    Returns:
        The mock cast as Agent[Any, Any]
    """
    return cast("Agent[Any, Any]", mock)


__all__ = [
    "as_umwelt",
    "as_agent",
]
