"""Tests for Collective AGENTESE Node."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.town.context import ALL_REGION_CONTEXTS, RegionType
from agents.town.sheaf import TownSheaf, create_town_sheaf
from services.town.bus_wiring import TownBusManager
from services.town.collective_node import (
    CollectiveManifestRendering,
    CollectiveManifestResponse,
    CollectiveNode,
    EmergenceRendering,
    EmergenceResponse,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sheaf() -> TownSheaf:
    """Create a fresh sheaf for each test."""
    return create_town_sheaf()


@pytest.fixture
def bus_manager() -> TownBusManager:
    """Create a fresh bus manager for each test."""
    manager = TownBusManager()
    manager.wire_all()
    return manager


@pytest.fixture
def node(sheaf: TownSheaf, bus_manager: TownBusManager) -> CollectiveNode:
    """Create a fresh node for each test."""
    return CollectiveNode(sheaf=sheaf, bus_manager=bus_manager)


# =============================================================================
# Rendering Tests
# =============================================================================


class TestCollectiveManifestRendering:
    """Tests for CollectiveManifestRendering."""

    def test_to_dict(self) -> None:
        """to_dict should return proper structure."""
        response = CollectiveManifestResponse(
            total_citizens=10,
            total_regions=7,
            active_regions=3,
            emergence_score=0.65,
            rituality=0.7,
            trust_density=0.5,
            region_balance=0.8,
        )
        rendering = CollectiveManifestRendering(response=response)

        result = rendering.to_dict()

        assert result["type"] == "collective_manifest"
        assert result["total_citizens"] == 10
        assert result["active_regions"] == 3
        assert result["emergence_score"] == 0.65

    def test_to_text(self) -> None:
        """to_text should return formatted string."""
        response = CollectiveManifestResponse(
            total_citizens=10,
            total_regions=7,
            active_regions=3,
            emergence_score=0.65,
            rituality=0.7,
            trust_density=0.5,
            region_balance=0.8,
        )
        rendering = CollectiveManifestRendering(response=response)

        result = rendering.to_text()

        assert "Town Collective Status" in result
        assert "Citizens: 10" in result
        assert "Emergence Score:" in result


class TestEmergenceRendering:
    """Tests for EmergenceRendering."""

    def test_to_dict(self) -> None:
        """to_dict should return emergence metrics."""
        response = EmergenceResponse(
            culture_motifs=[{"type": "triangle", "count": 3}],
            rituality=0.6,
            trust_density=0.4,
            coalition_overlap=0.2,
            region_balance=0.9,
            motif_count=1,
        )
        rendering = EmergenceRendering(response=response)

        result = rendering.to_dict()

        assert result["type"] == "emergence"
        assert result["rituality"] == 0.6
        assert result["motif_count"] == 1

    def test_to_text(self) -> None:
        """to_text should show metrics."""
        response = EmergenceResponse(
            culture_motifs=[{"type": "triangle", "count": 3}],
            rituality=0.6,
            trust_density=0.4,
            coalition_overlap=0.2,
            region_balance=0.9,
            motif_count=1,
        )
        rendering = EmergenceRendering(response=response)

        result = rendering.to_text()

        assert "Emergence Metrics" in result
        assert "triangle" in result


# =============================================================================
# CollectiveNode Initialization Tests
# =============================================================================


class TestCollectiveNodeInit:
    """Tests for CollectiveNode initialization."""

    def test_default_init(self) -> None:
        """Should initialize with defaults."""
        node = CollectiveNode()
        assert node._sheaf is not None
        assert node._bus_manager is not None

    def test_custom_sheaf(self, sheaf: TownSheaf) -> None:
        """Should accept custom sheaf."""
        node = CollectiveNode(sheaf=sheaf)
        assert node._sheaf is sheaf

    def test_handle_property(self, node: CollectiveNode) -> None:
        """Handle should return correct path."""
        assert node.handle == "world.town.collective"


# =============================================================================
# State Management Tests
# =============================================================================


class TestCollectiveNodeState:
    """Tests for state management."""

    def test_set_citizen_location(self, node: CollectiveNode) -> None:
        """Should track citizen locations."""
        node.set_citizen_location("alice", "inn")
        node.set_citizen_location("bob", "workshop")

        assert node._citizen_locations["alice"] == "inn"
        assert node._citizen_locations["bob"] == "workshop"

    def test_record_conversation(self, node: CollectiveNode) -> None:
        """Should track region activity."""
        node.record_conversation("inn")
        node.record_conversation("inn")
        node.record_conversation("plaza")

        assert node._region_activity["inn"] == 2
        assert node._region_activity["plaza"] == 1

    def test_get_region_views(self, node: CollectiveNode) -> None:
        """Should build region views from state."""
        node.set_citizen_location("alice", "inn")
        node.set_citizen_location("bob", "inn")
        node.set_citizen_location("carol", "workshop")

        views = node.get_region_views()

        assert len(views) == len(ALL_REGION_CONTEXTS)

        # Find inn view
        inn_view = None
        for ctx, view in views.items():
            if ctx.name == "inn":
                inn_view = view
                break

        assert inn_view is not None
        assert "alice" in inn_view.citizens
        assert "bob" in inn_view.citizens


# =============================================================================
# Affordances Tests
# =============================================================================


class TestCollectiveNodeAffordances:
    """Tests for archetype-specific affordances."""

    def test_developer_affordances(self, node: CollectiveNode) -> None:
        """Developer should have full access."""
        affordances = node._get_affordances_for_archetype("developer")

        assert "manifest" in affordances
        assert "gossip" in affordances
        assert "step" in affordances

    def test_researcher_affordances(self, node: CollectiveNode) -> None:
        """Researcher should have gossip but not step."""
        affordances = node._get_affordances_for_archetype("researcher")

        assert "gossip" in affordances
        assert "step" not in affordances

    def test_default_affordances(self, node: CollectiveNode) -> None:
        """Default should have read-only."""
        affordances = node._get_affordances_for_archetype("visitor")

        assert "manifest" in affordances
        assert "emergence" in affordances
        assert "gossip" not in affordances


# =============================================================================
# Manifest Tests
# =============================================================================


class TestCollectiveNodeManifest:
    """Tests for manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_empty_state(self, node: CollectiveNode) -> None:
        """Manifest with empty state should work."""
        observer = MagicMock()
        result = await node.manifest(observer)

        assert isinstance(result, CollectiveManifestRendering)
        assert result.response.total_citizens == 0

    @pytest.mark.asyncio
    async def test_manifest_with_citizens(self, node: CollectiveNode) -> None:
        """Manifest should count citizens."""
        node.set_citizen_location("alice", "inn")
        node.set_citizen_location("bob", "workshop")

        observer = MagicMock()
        result = await node.manifest(observer)

        assert result.response.total_citizens == 2
        assert result.response.active_regions == 2


# =============================================================================
# Gossip Tests
# =============================================================================


class TestCollectiveNodeGossip:
    """Tests for gossip aspect."""

    @pytest.mark.asyncio
    async def test_gossip_basic(self, node: CollectiveNode) -> None:
        """Basic gossip should work."""
        observer = MagicMock()

        result = await node._invoke_aspect(
            "gossip",
            observer,
            source_citizen="alice",
            target_citizen="bob",
            content="Carol found treasure",
        )

        assert "event_id" in result
        assert result["source_citizen"] == "alice"
        assert result["target_citizen"] == "bob"
        assert result["spread_successful"]

    @pytest.mark.asyncio
    async def test_gossip_requires_citizens(self, node: CollectiveNode) -> None:
        """Gossip should require source and target."""
        observer = MagicMock()

        result = await node._invoke_aspect("gossip", observer, content="test")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_gossip_with_accuracy(self, node: CollectiveNode) -> None:
        """Gossip should accept accuracy parameter."""
        observer = MagicMock()

        result = await node._invoke_aspect(
            "gossip",
            observer,
            source_citizen="alice",
            target_citizen="bob",
            content="rumor",
            accuracy=0.3,
        )

        assert "event_id" in result

    @pytest.mark.asyncio
    async def test_gossip_emits_event(self, node: CollectiveNode) -> None:
        """Gossip should emit to bus."""
        received = []

        async def handler(event):
            received.append(event)

        node._bus_manager.data_bus.subscribe_all(handler)

        observer = MagicMock()
        await node._invoke_aspect(
            "gossip",
            observer,
            source_citizen="alice",
            target_citizen="bob",
            content="news",
        )

        import asyncio

        await asyncio.sleep(0.01)

        assert len(received) == 1


# =============================================================================
# Emergence Tests
# =============================================================================


class TestCollectiveNodeEmergence:
    """Tests for emergence aspect."""

    @pytest.mark.asyncio
    async def test_emergence_empty(self, node: CollectiveNode) -> None:
        """Emergence with no state should return zeros."""
        observer = MagicMock()

        result = await node._invoke_aspect("emergence", observer)

        assert "rituality" in result
        assert "trust_density" in result
        assert result["motif_count"] == 0

    @pytest.mark.asyncio
    async def test_emergence_with_citizens(self, node: CollectiveNode) -> None:
        """Emergence should compute metrics from citizens."""
        node.set_citizen_location("alice", "inn")
        node.set_citizen_location("bob", "inn")
        node.set_citizen_location("carol", "workshop")

        observer = MagicMock()
        result = await node._invoke_aspect("emergence", observer)

        assert "region_balance" in result


# =============================================================================
# Activity Tests
# =============================================================================


class TestCollectiveNodeActivity:
    """Tests for activity aspect."""

    @pytest.mark.asyncio
    async def test_activity_empty(self, node: CollectiveNode) -> None:
        """Activity with no data should show quiet regions."""
        observer = MagicMock()

        result = await node._invoke_aspect("activity", observer)

        assert "regions" in result
        assert len(result["regions"]) == len(ALL_REGION_CONTEXTS)
        assert result["total_activity"] == 0

    @pytest.mark.asyncio
    async def test_activity_with_conversations(self, node: CollectiveNode) -> None:
        """Activity should track conversations."""
        node.record_conversation("inn")
        node.record_conversation("inn")
        node.record_conversation("inn")
        node.record_conversation("plaza")

        observer = MagicMock()
        result = await node._invoke_aspect("activity", observer)

        assert result["total_activity"] == 4
        assert result["most_active_region"] == "inn"

    @pytest.mark.asyncio
    async def test_activity_levels(self, node: CollectiveNode) -> None:
        """Activity levels should be computed correctly."""
        # Make inn bustling
        for _ in range(15):
            node.record_conversation("inn")

        observer = MagicMock()
        result = await node._invoke_aspect("activity", observer)

        inn_activity = next(r for r in result["regions"] if r["region"] == "inn")
        assert inn_activity["activity_level"] == "bustling"


# =============================================================================
# Step Tests
# =============================================================================


class TestCollectiveNodeStep:
    """Tests for simulation step aspect."""

    @pytest.mark.asyncio
    async def test_step_advances(self, node: CollectiveNode) -> None:
        """Step should advance step number."""
        observer = MagicMock()

        result = await node._invoke_aspect("step", observer)

        assert result["step_number"] == 1
        assert "events_emitted" in result

    @pytest.mark.asyncio
    async def test_multiple_steps(self, node: CollectiveNode) -> None:
        """Multiple steps should accumulate."""
        observer = MagicMock()

        await node._invoke_aspect("step", observer, steps=3)

        assert node._step_number == 3

    @pytest.mark.asyncio
    async def test_step_emits_events(self, node: CollectiveNode) -> None:
        """Step should emit SimulationStep events."""
        received = []

        async def handler(event):
            received.append(event)

        node._bus_manager.data_bus.subscribe_all(handler)

        observer = MagicMock()
        await node._invoke_aspect("step", observer, steps=2)

        import asyncio

        await asyncio.sleep(0.01)

        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_step_counts_citizens(self, node: CollectiveNode) -> None:
        """Step should count active citizens."""
        node.set_citizen_location("alice", "inn")
        node.set_citizen_location("bob", "workshop")

        observer = MagicMock()
        result = await node._invoke_aspect("step", observer)

        assert result["active_citizens"] == 2


# =============================================================================
# Unknown Aspect Tests
# =============================================================================


class TestCollectiveNodeUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect_error(self, node: CollectiveNode) -> None:
        """Unknown aspect should return error."""
        observer = MagicMock()

        result = await node._invoke_aspect("nonexistent", observer)

        assert "error" in result
        assert "Unknown aspect" in result["error"]
