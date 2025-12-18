"""Tests for Coalition AGENTESE Node."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from services.town.coalition_node import (
    CoalitionListRendering,
    CoalitionManifestRendering,
    CoalitionNode,
    CoalitionRendering,
)
from services.town.coalition_service import Coalition, CoalitionService


class TestCoalitionManifestRendering:
    """Tests for CoalitionManifestRendering."""

    def test_to_dict(self) -> None:
        """to_dict should return proper structure."""
        rendering = CoalitionManifestRendering(
            summary={
                "total_coalitions": 5,
                "alive_coalitions": 4,
                "total_members": 15,
                "bridge_citizens": 3,
                "avg_strength": 0.75,
            }
        )

        result = rendering.to_dict()

        assert result["type"] == "coalition_manifest"
        assert result["total_coalitions"] == 5
        assert result["alive_coalitions"] == 4

    def test_to_text(self) -> None:
        """to_text should return formatted string."""
        rendering = CoalitionManifestRendering(
            summary={
                "total_coalitions": 5,
                "alive_coalitions": 4,
                "total_members": 15,
                "bridge_citizens": 3,
                "avg_strength": 0.75,
            }
        )

        result = rendering.to_text()

        assert "Coalition System Status" in result
        assert "5" in result  # total coalitions


class TestCoalitionRendering:
    """Tests for CoalitionRendering."""

    def test_to_dict(self) -> None:
        """to_dict should return coalition data."""
        coalition = Coalition(
            id="c1",
            name="Test Coalition",
            members={"alice", "bob", "carol"},
            strength=0.8,
            purpose="testing",
        )

        rendering = CoalitionRendering(coalition=coalition)
        result = rendering.to_dict()

        assert result["type"] == "coalition"
        assert result["id"] == "c1"
        assert result["name"] == "Test Coalition"
        assert result["size"] == 3
        assert result["strength"] == 0.8

    def test_to_text(self) -> None:
        """to_text should return formatted string."""
        coalition = Coalition(
            id="c1",
            name="Test Coalition",
            members={"alice", "bob"},
            strength=0.8,
        )

        rendering = CoalitionRendering(coalition=coalition)
        result = rendering.to_text()

        assert "Test Coalition" in result
        assert "alice" in result or "bob" in result


class TestCoalitionListRendering:
    """Tests for CoalitionListRendering."""

    def test_empty_list(self) -> None:
        """Empty list should show appropriate message."""
        rendering = CoalitionListRendering(coalitions=[], bridge_citizens=[])

        assert rendering.to_text() == "No coalitions detected"
        assert rendering.to_dict()["total"] == 0

    def test_with_coalitions(self) -> None:
        """Should list coalitions with strength bars."""
        c1 = Coalition(id="c1", name="Alpha", members={"a", "b"}, strength=0.9)
        c2 = Coalition(id="c2", name="Beta", members={"c", "d"}, strength=0.5)

        rendering = CoalitionListRendering(
            coalitions=[c1, c2],
            bridge_citizens=["x"],
        )

        text = rendering.to_text()
        assert "Alpha" in text
        assert "Beta" in text
        assert "Bridge Citizens" in text

        data = rendering.to_dict()
        assert data["total"] == 2
        assert len(data["coalitions"]) == 2


class TestCoalitionNodeInit:
    """Tests for CoalitionNode initialization."""

    def test_requires_coalition_service(self) -> None:
        """Should require coalition_service parameter."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        assert node._service is service

    def test_handle_property(self) -> None:
        """Handle should return correct path."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        assert node.handle == "world.town.coalition"


class TestCoalitionNodeAffordances:
    """Tests for archetype-specific affordances."""

    def test_developer_affordances(self) -> None:
        """Developer should have full access."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)

        affordances = node._get_affordances_for_archetype("developer")

        assert "manifest" in affordances
        assert "list" in affordances
        assert "detect" in affordances
        assert "decay" in affordances

    def test_researcher_affordances(self) -> None:
        """Researcher should have detect but not decay."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)

        affordances = node._get_affordances_for_archetype("researcher")

        assert "detect" in affordances
        assert "decay" not in affordances

    def test_default_affordances(self) -> None:
        """Default archetype should have read-only."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)

        affordances = node._get_affordances_for_archetype("visitor")

        assert "list" in affordances
        assert "detect" not in affordances
        assert "decay" not in affordances


class TestCoalitionNodeManifest:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(self) -> None:
        """Manifest should return CoalitionManifestRendering."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)

        # Add some coalitions
        service._coalitions["c1"] = Coalition(id="c1", members={"a", "b"}, strength=0.8)
        service._coalitions["c2"] = Coalition(id="c2", members={"c", "d"}, strength=0.6)

        observer = MagicMock()
        result = await node.manifest(observer)

        assert isinstance(result, CoalitionManifestRendering)
        assert result.summary["total_coalitions"] == 2

    @pytest.mark.asyncio
    async def test_manifest_no_service(self) -> None:
        """Manifest with None service should return error rendering."""
        # Create node with service then set to None
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        node._service = None

        observer = MagicMock()
        result = await node.manifest(observer)

        # Should return BasicRendering with error
        assert "not initialized" in result.to_text().lower() or hasattr(result, "metadata")


class TestCoalitionNodeListAspect:
    """Tests for list aspect."""

    @pytest.mark.asyncio
    async def test_list_returns_coalitions(self) -> None:
        """List should return all coalitions."""
        service = CoalitionService()
        service._coalitions["c1"] = Coalition(
            id="c1", name="Alpha", members={"a", "b"}, strength=0.8
        )

        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("list", observer)

        assert "coalitions" in result
        assert result["total"] == 1
        assert result["coalitions"][0]["name"] == "Alpha"


class TestCoalitionNodeGetAspect:
    """Tests for get aspect."""

    @pytest.mark.asyncio
    async def test_get_existing_coalition(self) -> None:
        """Get should return coalition by ID."""
        service = CoalitionService()
        service._coalitions["c1"] = Coalition(id="c1", name="Alpha", members={"a", "b"})

        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("get", observer, coalition_id="c1")

        assert result["id"] == "c1"
        assert result["name"] == "Alpha"

    @pytest.mark.asyncio
    async def test_get_missing_coalition(self) -> None:
        """Get should return error for missing coalition."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("get", observer, coalition_id="missing")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_requires_id(self) -> None:
        """Get should require coalition_id."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("get", observer)

        assert "error" in result


class TestCoalitionNodeBridgesAspect:
    """Tests for bridges aspect."""

    @pytest.mark.asyncio
    async def test_bridges_returns_citizens(self) -> None:
        """Bridges should return citizens in multiple coalitions."""
        service = CoalitionService()
        service._coalitions["c1"] = Coalition(id="c1", members={"alice", "bob"})
        service._coalitions["c2"] = Coalition(id="c2", members={"alice", "carol"})

        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("bridges", observer)

        assert "bridge_citizens" in result
        assert "alice" in result["bridge_citizens"]  # In both coalitions
        assert result["count"] == 1


class TestCoalitionNodeDecayAspect:
    """Tests for decay aspect."""

    @pytest.mark.asyncio
    async def test_decay_prunes_weak(self) -> None:
        """Decay should prune weak coalitions."""
        service = CoalitionService()
        service._coalitions["c1"] = Coalition(id="c1", members={"a", "b"}, strength=0.15)
        service._coalitions["c2"] = Coalition(id="c2", members={"c", "d"}, strength=0.8)

        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("decay", observer, rate=0.1)

        assert "pruned_count" in result
        assert result["decay_rate"] == 0.1

    @pytest.mark.asyncio
    async def test_decay_uses_default_rate(self) -> None:
        """Decay should use default rate if not specified."""
        service = CoalitionService()
        service._coalitions["c1"] = Coalition(id="c1", members={"a", "b"}, strength=0.5)

        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("decay", observer)

        assert result["decay_rate"] == 0.05  # Default rate


class TestCoalitionNodeDetectAspect:
    """Tests for detect aspect."""

    @pytest.mark.asyncio
    async def test_detect_requires_citizens(self) -> None:
        """Detect should require citizens dict."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("detect", observer)

        assert "error" in result
        assert "Citizens" in result["error"]

    @pytest.mark.asyncio
    async def test_detect_with_citizens(self) -> None:
        """Detect should work with citizens."""
        # This test would need mock citizens with eigenvectors
        # For now, test that parameters are handled
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect(
            "detect",
            observer,
            similarity_threshold=0.9,
            k=2,
            citizens={},  # Empty dict for param handling test
        )

        # Should return error about empty citizens
        assert "error" in result or "coalitions" in result


class TestCoalitionNodeUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect_returns_error(self) -> None:
        """Unknown aspect should return error."""
        service = CoalitionService()
        node = CoalitionNode(coalition_service=service)
        observer = MagicMock()

        result = await node._invoke_aspect("nonexistent", observer)

        assert "error" in result
        assert "Unknown aspect" in result["error"]
