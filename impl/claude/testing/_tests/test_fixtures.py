"""
Tests for type-safe fixture factory.

Validates that as_umwelt and helpers work correctly with mypy.
"""

from typing import Any

import pytest

from bootstrap.umwelt import Umwelt
from protocols.agentese._tests.conftest import MockUmwelt
from testing.fixtures import as_umwelt


class TestAsUmwelt:
    """Test as_umwelt convenience function."""

    def test_as_umwelt_returns_same_object(self) -> None:
        """as_umwelt returns the exact same object."""
        mock = MockUmwelt()
        result = as_umwelt(mock)
        # The cast doesn't change the object identity at runtime
        assert result.dna == mock.dna

    def test_as_umwelt_preserves_functionality(self) -> None:
        """as_umwelt preserves mock's methods and attributes."""
        mock = MockUmwelt(archetype="architect")
        result = as_umwelt(mock)

        # Should still have dna attribute
        assert hasattr(result, "dna")
        assert result.dna.archetype == "architect"

    @pytest.mark.asyncio
    async def test_as_umwelt_async_methods_work(self) -> None:
        """Async methods on cast object still work."""
        mock = MockUmwelt()
        result: Umwelt[Any, Any] = as_umwelt(mock)

        # Should be able to call async methods
        state = await result.get()
        assert isinstance(state, dict)

    @pytest.mark.asyncio
    async def test_as_umwelt_in_async_context(self) -> None:
        """as_umwelt works in async test contexts."""
        mock = MockUmwelt(archetype="poet")
        observer = as_umwelt(mock)

        # Should work in async calls
        state = await observer.get()
        assert state["agent"] == "test_agent"


class TestIntegrationPatterns:
    """Test common integration patterns with fixture helpers."""

    def test_fixture_pattern_inline(self) -> None:
        """Common inline usage pattern."""
        # Old pattern: cast("Umwelt[Any, Any]", MockUmwelt())
        # New pattern:
        observer: Umwelt[Any, Any] = as_umwelt(MockUmwelt())

        assert observer.dna.archetype == "default"

    def test_multiple_observers(self) -> None:
        """Creating multiple typed observers."""
        architect = as_umwelt(MockUmwelt(archetype="architect"))
        poet = as_umwelt(MockUmwelt(archetype="poet"))

        assert architect.dna.archetype == "architect"
        assert poet.dna.archetype == "poet"

    @pytest.mark.asyncio
    async def test_logos_invoke_pattern(self) -> None:
        """Pattern used in logos.invoke calls."""
        from protocols.agentese._tests.conftest import MockNode

        node = MockNode(handle="test.node")
        observer = as_umwelt(MockUmwelt())

        # This is the pattern that replaces:
        # await node.manifest(cast("Umwelt[Any, Any]", mock))
        result = await node.manifest(observer)
        assert result is not None
