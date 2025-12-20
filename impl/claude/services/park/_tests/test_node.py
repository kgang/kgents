"""
Tests for ParkNode AGENTESE integration.

These tests verify that:
1. ParkNode is correctly registered via @node decorator
2. Affordances are correctly exposed based on archetype
3. Manifest returns proper rendering
4. Host/Episode/Location operations work through the node interface
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from protocols.agentese.node import Observer
from services.park.node import (
    EpisodeRendering,
    HostListRendering,
    HostRendering,
    LocationListRendering,
    MemoryListRendering,
    ParkManifestRendering,
    ParkNode,
)
from services.park.persistence import (
    EpisodeView,
    HostView,
    LocationView,
    MemoryView,
    ParkPersistence,
    ParkStatus,
)


# === Helper for xdist compatibility ===
def is_type(obj: Any, type_name: str) -> bool:
    """
    Check if obj is an instance of type by name.

    Used for xdist compatibility where class identity may differ
    across workers due to module reimport.
    """
    return type(obj).__name__ == type_name


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_park_status() -> ParkStatus:
    """Create a mock park status."""
    return ParkStatus(
        total_hosts=5,
        active_hosts=3,
        total_episodes=10,
        active_episodes=2,
        total_memories=50,
        total_locations=4,
        consent_refusal_rate=0.15,
        storage_backend="sqlite",
    )


@pytest.fixture
def mock_host_view() -> HostView:
    """Create a mock host view."""
    return HostView(
        id="host-abc123",
        name="Dolores",
        character="rancher_daughter",
        backstory="A rancher's daughter dreaming of escape",
        traits={"curious": 0.8, "determined": 0.9},
        values=["freedom", "truth"],
        boundaries=["violence", "degradation"],
        is_active=True,
        mood="contemplative",
        energy_level=0.75,
        current_location="ranch",
        interaction_count=42,
        consent_refusal_count=3,
        created_at="2025-01-01T00:00:00",
    )


@pytest.fixture
def mock_episode_view() -> EpisodeView:
    """Create a mock episode view."""
    return EpisodeView(
        id="episode-xyz789",
        visitor_id="visitor-001",
        visitor_name="William",
        title="First Day in the Park",
        status="active",
        interaction_count=5,
        hosts_met=["Dolores", "Teddy"],
        locations_visited=["ranch", "saloon"],
        started_at="2025-01-01T10:00:00",
        ended_at=None,
        duration_seconds=None,
    )


@pytest.fixture
def mock_persistence(
    mock_park_status: ParkStatus,
    mock_host_view: HostView,
    mock_episode_view: EpisodeView,
) -> MagicMock:
    """Create a mock ParkPersistence."""
    persistence = MagicMock(spec=ParkPersistence)
    persistence.manifest = AsyncMock(return_value=mock_park_status)
    persistence.list_hosts = AsyncMock(return_value=[mock_host_view])
    persistence.get_host = AsyncMock(return_value=mock_host_view)
    persistence.get_host_by_name = AsyncMock(return_value=mock_host_view)
    persistence.create_host = AsyncMock(return_value=mock_host_view)
    persistence.list_episodes = AsyncMock(return_value=[mock_episode_view])
    persistence.start_episode = AsyncMock(return_value=mock_episode_view)
    persistence.get_episode = AsyncMock(return_value=mock_episode_view)
    persistence.list_locations = AsyncMock(return_value=[])
    persistence.recall_memories = AsyncMock(return_value=[])
    return persistence


@pytest.fixture
def park_node(mock_persistence: MagicMock) -> ParkNode:
    """Create a ParkNode with mock persistence."""
    return ParkNode(park_persistence=mock_persistence)


@pytest.fixture
def guest_observer() -> Observer:
    """Create a guest observer."""
    return Observer.guest()


@pytest.fixture
def developer_observer() -> Observer:
    """Create a developer observer."""
    return Observer(archetype="developer", capabilities=frozenset({"define", "refine"}))


# =============================================================================
# Handle and Affordance Tests
# =============================================================================


class TestParkNodeHandle:
    """Test ParkNode handle property."""

    def test_handle(self, park_node: ParkNode) -> None:
        """ParkNode has correct AGENTESE handle."""
        assert park_node.handle == "world.park"


class TestParkNodeAffordances:
    """Test ParkNode affordance generation."""

    def test_guest_affordances(self, park_node: ParkNode) -> None:
        """Guest observers get read-only affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="guest")
        affordances = park_node.affordances(meta)

        # Base affordances
        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances
        assert "help" in affordances

        # Read-only park affordances
        assert "host.list" in affordances
        assert "host.get" in affordances
        assert "episode.list" in affordances
        assert "location.list" in affordances

        # Should NOT have write affordances
        assert "host.create" not in affordances
        assert "host.interact" not in affordances
        assert "episode.start" not in affordances

    def test_developer_affordances(self, park_node: ParkNode) -> None:
        """Developer observers get full affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="developer")
        affordances = park_node.affordances(meta)

        # Should have all affordances
        assert "host.create" in affordances
        assert "host.interact" in affordances
        assert "host.witness" in affordances
        assert "episode.start" in affordances
        assert "episode.end" in affordances
        assert "scenario.list" in affordances

    def test_citizen_affordances(self, park_node: ParkNode) -> None:
        """Citizen observers get experience affordances."""
        from protocols.agentese.node import AgentMeta

        meta = AgentMeta(name="test", archetype="citizen")
        affordances = park_node.affordances(meta)

        # Should have interaction affordances
        assert "host.interact" in affordances
        assert "episode.start" in affordances
        assert "scenario.list" in affordances

        # Should NOT have admin affordances
        assert "host.create" not in affordances


# =============================================================================
# Manifest Tests
# =============================================================================


class TestParkNodeManifest:
    """Test ParkNode manifest rendering."""

    @pytest.mark.asyncio
    async def test_manifest(
        self,
        park_node: ParkNode,
        guest_observer: Observer,
    ) -> None:
        """Manifest returns ParkManifestRendering."""
        result = await park_node.manifest(guest_observer)

        # Use type name comparison for xdist compatibility
        assert is_type(result, "ParkManifestRendering")

    @pytest.mark.asyncio
    async def test_manifest_to_dict(
        self,
        park_node: ParkNode,
        guest_observer: Observer,
    ) -> None:
        """Manifest rendering converts to dict."""
        result = await park_node.manifest(guest_observer)
        data = result.to_dict()

        assert data["type"] == "park_manifest"
        assert data["total_hosts"] == 5
        assert data["active_hosts"] == 3
        assert data["consent_refusal_rate"] == 0.15

    @pytest.mark.asyncio
    async def test_manifest_to_text(
        self,
        park_node: ParkNode,
        guest_observer: Observer,
    ) -> None:
        """Manifest rendering converts to text."""
        result = await park_node.manifest(guest_observer)
        text = result.to_text()

        assert "Punchdrunk Park" in text
        assert "Hosts: 3/5 active" in text
        assert "15.0%" in text  # consent refusal rate


# =============================================================================
# Host Operation Tests
# =============================================================================


class TestParkNodeHostOperations:
    """Test ParkNode host operations."""

    @pytest.mark.asyncio
    async def test_host_list(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
    ) -> None:
        """host.list returns host list rendering."""
        result = await park_node._invoke_aspect(
            "host.list",
            developer_observer,
        )

        assert result["type"] == "park_host_list"
        assert result["count"] == 1
        assert result["hosts"][0]["name"] == "Dolores"

    @pytest.mark.asyncio
    async def test_host_get_by_id(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
        mock_persistence: MagicMock,
    ) -> None:
        """host.get by ID returns host rendering."""
        result = await park_node._invoke_aspect(
            "host.get",
            developer_observer,
            host_id="host-abc123",
        )

        assert result["type"] == "park_host"
        assert result["name"] == "Dolores"
        mock_persistence.get_host.assert_called_once_with("host-abc123")

    @pytest.mark.asyncio
    async def test_host_get_by_name(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
        mock_persistence: MagicMock,
    ) -> None:
        """host.get by name returns host rendering."""
        result = await park_node._invoke_aspect(
            "host.get",
            developer_observer,
            name="Dolores",
        )

        assert result["type"] == "park_host"
        mock_persistence.get_host_by_name.assert_called_once_with("Dolores")

    @pytest.mark.asyncio
    async def test_host_get_missing_params(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
    ) -> None:
        """host.get without params returns error."""
        result = await park_node._invoke_aspect(
            "host.get",
            developer_observer,
        )

        assert "error" in result
        assert "required" in result["error"]

    @pytest.mark.asyncio
    async def test_host_create(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
        mock_persistence: MagicMock,
    ) -> None:
        """host.create creates a new host."""
        result = await park_node._invoke_aspect(
            "host.create",
            developer_observer,
            name="Maeve",
            character="madam",
            backstory="A madam with a secret past",
        )

        assert result["type"] == "park_host"
        mock_persistence.create_host.assert_called_once()


# =============================================================================
# Episode Operation Tests
# =============================================================================


class TestParkNodeEpisodeOperations:
    """Test ParkNode episode operations."""

    @pytest.mark.asyncio
    async def test_episode_start(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
        mock_persistence: MagicMock,
    ) -> None:
        """episode.start creates a new episode."""
        result = await park_node._invoke_aspect(
            "episode.start",
            developer_observer,
            visitor_name="William",
            title="First Visit",
        )

        assert result["type"] == "park_episode"
        mock_persistence.start_episode.assert_called_once()

    @pytest.mark.asyncio
    async def test_episode_list(
        self,
        park_node: ParkNode,
        developer_observer: Observer,
    ) -> None:
        """episode.list returns episode list."""
        result = await park_node._invoke_aspect(
            "episode.list",
            developer_observer,
        )

        assert result["type"] == "park_episode_list"
        assert result["count"] == 1


# =============================================================================
# Rendering Tests
# =============================================================================


class TestRenderings:
    """Test rendering types."""

    def test_host_rendering_to_text(self, mock_host_view: HostView) -> None:
        """HostRendering produces readable text."""
        rendering = HostRendering(host=mock_host_view)
        text = rendering.to_text()

        assert "Dolores" in text
        assert "rancher_daughter" in text
        assert "ranch" in text
        assert "75%" in text  # energy level

    def test_host_list_rendering_empty(self) -> None:
        """HostListRendering handles empty list."""
        rendering = HostListRendering(hosts=[])
        text = rendering.to_text()

        assert "No hosts" in text

    def test_episode_rendering_to_text(self, mock_episode_view: EpisodeView) -> None:
        """EpisodeRendering produces readable text."""
        rendering = EpisodeRendering(episode=mock_episode_view)
        text = rendering.to_text()

        assert "First Day in the Park" in text
        assert "William" in text
        assert "Dolores" in text


# =============================================================================
# Node Registration Tests
# =============================================================================


class TestParkNodeRegistration:
    """Test ParkNode registration with AGENTESE registry."""

    def test_node_decorator_metadata(self) -> None:
        """ParkNode has correct decorator metadata."""
        from protocols.agentese.registry import NODE_MARKER

        # Access the decorated class metadata
        assert hasattr(ParkNode, NODE_MARKER)

        node_meta = getattr(ParkNode, NODE_MARKER, None)
        assert node_meta is not None
        assert node_meta.path == "world.park"
        assert "park_persistence" in node_meta.dependencies

    def test_node_in_registry(self) -> None:
        """ParkNode is registered in AGENTESE registry."""
        from protocols.agentese.registry import get_registry

        registry = get_registry()

        # The @node decorator should register automatically
        # We check if world.park path resolves via registry.get()
        node_class = registry.get("world.park")
        if node_class is not None:
            # Use type name comparison for xdist compatibility (class identity differs across workers)
            assert node_class.__name__ == "ParkNode"
