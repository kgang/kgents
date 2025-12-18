"""
Tests for void.hypnagogia AGENTESE path.

The hypnagogia node provides AGENTESE access to K-gent's dream cycle:
- void.hypnagogia.status - Current cycle state
- void.hypnagogia.wake - Trigger dream cycle
- void.hypnagogia.report - Last dream report
- void.hypnagogia.patterns - List patterns
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

import pytest

from protocols.agentese.contexts.void import (
    HypnagogiaNode,
    VoidContextResolver,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Fixtures
# =============================================================================


@dataclass
class MockDNA:
    """Mock Umwelt DNA."""

    name: str = "test_observer"
    archetype: str = "architect"


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing.

    Cast to Umwelt for type checking - implements required attributes.
    """

    dna: MockDNA = field(default_factory=MockDNA)


def _umwelt(mock: MockUmwelt) -> "Umwelt[Any, Any]":
    """Cast MockUmwelt to Umwelt for type checking."""
    return cast("Umwelt[Any, Any]", mock)


@pytest.fixture
def mock_observer() -> MockUmwelt:
    """Create a mock observer."""
    return MockUmwelt()


@pytest.fixture
def hypnagogia_node() -> HypnagogiaNode:
    """Create a HypnagogiaNode for testing."""
    return HypnagogiaNode()


@pytest.fixture
def void_resolver() -> VoidContextResolver:
    """Create a VoidContextResolver."""
    resolver = VoidContextResolver()
    resolver.__post_init__()
    return resolver


# =============================================================================
# Basic Tests
# =============================================================================


class TestHypnagogiaNode:
    """Tests for HypnagogiaNode."""

    def test_handle(self, hypnagogia_node: HypnagogiaNode) -> None:
        """Test handle property."""
        assert hypnagogia_node.handle == "void.hypnagogia"

    def test_affordances(self, hypnagogia_node: HypnagogiaNode) -> None:
        """Test affordances are available."""
        affordances = hypnagogia_node._get_affordances_for_archetype("any")
        assert "status" in affordances
        assert "wake" in affordances
        assert "report" in affordances
        assert "patterns" in affordances

    @pytest.mark.asyncio
    async def test_manifest(
        self, hypnagogia_node: HypnagogiaNode, mock_observer: MockUmwelt
    ) -> None:
        """Test manifest returns status."""
        result = await hypnagogia_node.manifest(_umwelt(mock_observer))
        # Access attributes via getattr to satisfy type checker
        assert "Hypnagogia" in getattr(result, "summary", "")
        assert getattr(result, "metadata", None) is not None

    @pytest.mark.asyncio
    async def test_status_aspect(
        self, hypnagogia_node: HypnagogiaNode, mock_observer: MockUmwelt
    ) -> None:
        """Test status aspect."""
        result = await hypnagogia_node._invoke_aspect("status", _umwelt(mock_observer))
        assert "interactions_buffered" in result
        assert "patterns_stored" in result
        assert "dreams_completed" in result

    @pytest.mark.asyncio
    async def test_patterns_aspect(
        self, hypnagogia_node: HypnagogiaNode, mock_observer: MockUmwelt
    ) -> None:
        """Test patterns aspect."""
        result = await hypnagogia_node._invoke_aspect("patterns", _umwelt(mock_observer))
        assert "patterns" in result
        assert "count" in result
        assert isinstance(result["patterns"], list)

    @pytest.mark.asyncio
    async def test_report_no_dreams(
        self, hypnagogia_node: HypnagogiaNode, mock_observer: MockUmwelt
    ) -> None:
        """Test report when no dreams have occurred."""
        result = await hypnagogia_node._invoke_aspect("report", _umwelt(mock_observer))
        # Either returns a report or an error
        assert "error" in result or "timestamp" in result


class TestVoidResolverHypnagogia:
    """Tests for hypnagogia via VoidContextResolver."""

    def test_resolve_hypnagogia(self, void_resolver: VoidContextResolver) -> None:
        """Test resolving void.hypnagogia."""
        node = void_resolver.resolve("hypnagogia", [])
        assert isinstance(node, HypnagogiaNode)

    @pytest.mark.asyncio
    async def test_invoke_via_resolver(
        self, void_resolver: VoidContextResolver, mock_observer: MockUmwelt
    ) -> None:
        """Test invoking hypnagogia via resolver."""
        node = void_resolver.resolve("hypnagogia", [])
        result = await node._invoke_aspect("status", _umwelt(mock_observer))
        assert "patterns_stored" in result
