"""
Tests for Town AGENTESE Node.

Verifies that TownNode:
1. Registers with @node("world.town")
2. Provides correct affordances by archetype
3. Routes aspects to TownPersistence methods
4. Integrates with AGENTESE gateway
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from protocols.agentese.node import AgentMeta, Observer
from protocols.agentese.registry import get_registry, repopulate_registry, reset_registry

# === Fixtures ===


@pytest.fixture(autouse=True)
def clean_registry():
    """
    Reset registry before each test, repopulate after.

    CRITICAL for pytest-xdist: Without repopulation, tests on the same
    worker that run after this test will see an empty registry, breaking
    canary tests and any test that relies on global node registration.

    See: protocols/agentese/_tests/test_xdist_node_registry_canary.py
    """
    reset_registry()
    yield
    # Repopulate registry for subsequent tests on this worker
    # NOTE: repopulate_registry() scans sys.modules for @node classes
    # _import_node_modules() won't work because imports are cached
    repopulate_registry()


@pytest.fixture
def mock_persistence():
    """Create a mock TownPersistence."""
    from services.town import (
        CitizenView,
        ConversationView,
        RelationshipView,
        TownStatus,
        TurnView,
    )

    persistence = MagicMock()

    # Mock manifest
    persistence.manifest = AsyncMock(
        return_value=TownStatus(
            total_citizens=25,
            active_citizens=20,
            total_conversations=100,
            active_conversations=5,
            total_relationships=45,
            storage_backend="sqlite",
        )
    )

    # Mock citizen operations
    sample_citizen = CitizenView(
        id="citizen-abc123",
        name="Socrates",
        archetype="dialectic",
        description="The philosopher of Athens",
        traits={"curiosity": 0.9, "wisdom": 0.85},
        is_active=True,
        interaction_count=42,
        last_interaction="2025-01-01T12:00:00",
        created_at="2025-01-01T00:00:00",
    )

    persistence.get_citizen = AsyncMock(return_value=sample_citizen)
    persistence.get_citizen_by_name = AsyncMock(return_value=sample_citizen)
    persistence.list_citizens = AsyncMock(return_value=[sample_citizen])
    persistence.create_citizen = AsyncMock(return_value=sample_citizen)
    persistence.update_citizen = AsyncMock(return_value=sample_citizen)

    # Mock conversation operations
    sample_turn = TurnView(
        id="turn-xyz789",
        turn_number=0,
        role="user",
        content="Hello Socrates",
        sentiment="positive",
        emotion="curious",
        created_at="2025-01-01T12:00:00",
    )

    sample_conversation = ConversationView(
        id="conv-def456",
        citizen_id="citizen-abc123",
        citizen_name="Socrates",
        topic="Philosophy",
        summary="Discussion about virtue",
        turn_count=5,
        is_active=True,
        created_at="2025-01-01T11:00:00",
        turns=[sample_turn],
    )

    persistence.start_conversation = AsyncMock(return_value=sample_conversation)
    persistence.add_turn = AsyncMock(return_value=sample_turn)
    persistence.get_dialogue_history = AsyncMock(return_value=[sample_conversation])

    # Mock relationship operations
    sample_relationship = RelationshipView(
        id="rel-ghi789",
        citizen_a_id="citizen-abc123",
        citizen_b_id="citizen-xyz789",
        relationship_type="student",
        strength=0.8,
        interaction_count=10,
        notes="Philosophical debates",
    )

    persistence.get_relationships = AsyncMock(return_value=[sample_relationship])

    return persistence


@pytest.fixture
def town_node(mock_persistence):
    """Create a TownNode with mock persistence."""
    from services.town.node import TownNode

    return TownNode(town_persistence=mock_persistence)


# === Test Registration ===


class TestTownNodeRegistration:
    """Tests for TownNode AGENTESE registration."""

    def test_node_has_metadata_marker(self):
        """TownNode has @node metadata marker."""
        from protocols.agentese.registry import NODE_MARKER, get_node_metadata
        from services.town.node import TownNode

        assert hasattr(TownNode, NODE_MARKER)

        meta = get_node_metadata(TownNode)
        assert meta is not None
        assert meta.path == "world.town"
        assert "town_persistence" in meta.dependencies

    def test_node_class_can_be_registered(self):
        """TownNode can be manually registered with registry."""
        from protocols.agentese.registry import get_node_metadata
        from services.town.node import TownNode

        registry = get_registry()
        meta = get_node_metadata(TownNode)
        assert meta is not None

        registry._register_class("world.town", TownNode, meta)

        assert registry.has("world.town")
        cls = registry.get("world.town")
        assert cls is TownNode

    def test_node_handle_matches_path(self, mock_persistence):
        """TownNode.handle matches @node path."""
        from protocols.agentese.registry import get_node_metadata
        from services.town.node import TownNode

        node = TownNode(town_persistence=mock_persistence)
        meta = get_node_metadata(TownNode)

        assert node.handle == "world.town"
        assert meta is not None
        assert meta.path == node.handle

    def test_node_requires_persistence(self):
        """TownNode requires town_persistence argument (for proper DI fallback)."""
        from services.town.node import TownNode

        with pytest.raises(TypeError):
            TownNode()


# === Test Handle ===


class TestTownNodeHandle:
    """Tests for TownNode.handle property."""

    def test_handle_is_world_town(self, town_node):
        """Handle returns 'world.town'."""
        assert town_node.handle == "world.town"


# === Test Affordances ===


class TestTownNodeAffordances:
    """Tests for TownNode affordances by archetype."""

    def test_developer_affordances(self, town_node):
        """Developer gets full affordances including mutations."""
        meta = AgentMeta(name="test", archetype="developer")
        affordances = town_node.affordances(meta)

        # Full access
        assert "citizen.list" in affordances
        assert "citizen.get" in affordances
        assert "citizen.create" in affordances
        assert "citizen.update" in affordances
        assert "converse" in affordances
        assert "turn" in affordances
        assert "history" in affordances
        assert "relationships" in affordances
        assert "gossip" in affordances
        assert "step" in affordances

    def test_guest_affordances(self, town_node):
        """Guest gets read-only affordances."""
        meta = AgentMeta(name="test", archetype="guest")
        affordances = town_node.affordances(meta)

        # Read access
        assert "citizen.list" in affordances
        assert "citizen.get" in affordances
        assert "history" in affordances
        assert "relationships" in affordances

        # No mutations
        assert "citizen.create" not in affordances
        assert "citizen.update" not in affordances
        assert "converse" not in affordances

    def test_researcher_affordances(self, town_node):
        """Researcher gets read + conversation access."""
        meta = AgentMeta(name="test", archetype="researcher")
        affordances = town_node.affordances(meta)

        # Read and conversation access
        assert "citizen.list" in affordances
        assert "citizen.get" in affordances
        assert "converse" in affordances
        assert "turn" in affordances

        # No admin mutations
        assert "citizen.create" not in affordances
        assert "gossip" not in affordances

    def test_base_affordances_included(self, town_node):
        """All archetypes get base affordances."""
        meta = AgentMeta(name="test", archetype="guest")
        affordances = town_node.affordances(meta)

        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances
        assert "help" in affordances


# === Test Manifest ===


class TestTownNodeManifest:
    """Tests for TownNode.manifest() aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_rendering(self, town_node, mock_persistence):
        """Manifest returns TownManifestRendering."""
        from services.town.node import TownManifestRendering

        observer = Observer.test()
        result = await town_node.manifest(observer)

        assert isinstance(result, TownManifestRendering)
        mock_persistence.manifest.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_manifest_to_dict(self, town_node):
        """Manifest rendering converts to dict."""
        observer = Observer.test()
        result = await town_node.manifest(observer)

        data = result.to_dict()
        assert data["type"] == "town_manifest"
        assert data["total_citizens"] == 25
        assert data["active_citizens"] == 20
        assert data["total_relationships"] == 45

    @pytest.mark.asyncio
    async def test_manifest_to_text(self, town_node):
        """Manifest rendering converts to text."""
        observer = Observer.test()
        result = await town_node.manifest(observer)

        text = result.to_text()
        assert "Town Status" in text
        assert "Citizens:" in text


# === Test Citizen Operations ===


class TestTownNodeCitizenList:
    """Tests for world.town.citizen.list aspect."""

    @pytest.mark.asyncio
    async def test_citizen_list_calls_persistence(self, town_node, mock_persistence):
        """Citizen list invokes persistence.list_citizens()."""
        observer = Observer.test()
        await town_node.invoke("citizen.list", observer, active_only=True, limit=10)

        mock_persistence.list_citizens.assert_awaited_once_with(
            active_only=True,
            archetype=None,
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_citizen_list_returns_results(self, town_node):
        """Citizen list returns structured results."""
        observer = Observer.test()
        result = await town_node.invoke("citizen.list", observer)

        assert result["type"] == "citizen_list"
        assert result["total"] == 1
        assert len(result["citizens"]) == 1
        assert result["citizens"][0]["name"] == "Socrates"


class TestTownNodeCitizenGet:
    """Tests for world.town.citizen.get aspect."""

    @pytest.mark.asyncio
    async def test_citizen_get_by_id(self, town_node, mock_persistence):
        """Citizen get by ID invokes persistence.get_citizen()."""
        observer = Observer.test()
        await town_node.invoke("citizen.get", observer, citizen_id="citizen-abc123")

        mock_persistence.get_citizen.assert_awaited_once_with("citizen-abc123")

    @pytest.mark.asyncio
    async def test_citizen_get_by_name(self, town_node, mock_persistence):
        """Citizen get by name invokes persistence.get_citizen_by_name()."""
        observer = Observer.test()
        await town_node.invoke("citizen.get", observer, name="Socrates")

        mock_persistence.get_citizen_by_name.assert_awaited_once_with("Socrates")

    @pytest.mark.asyncio
    async def test_citizen_get_returns_rendering(self, town_node):
        """Citizen get returns CitizenRendering dict."""
        observer = Observer.test()
        result = await town_node.invoke("citizen.get", observer, name="Socrates")

        assert result["type"] == "citizen"
        assert result["name"] == "Socrates"
        assert result["archetype"] == "dialectic"

    @pytest.mark.asyncio
    async def test_citizen_get_without_id_or_name(self, town_node):
        """Citizen get without ID or name returns error."""
        observer = Observer.test()
        result = await town_node.invoke("citizen.get", observer)

        assert "error" in result


class TestTownNodeCitizenCreate:
    """Tests for world.town.citizen.create aspect."""

    @pytest.mark.asyncio
    async def test_citizen_create_calls_persistence(self, town_node, mock_persistence):
        """Citizen create invokes persistence.create_citizen()."""
        observer = Observer.test()
        await town_node.invoke(
            "citizen.create",
            observer,
            name="Plato",
            archetype="dialectic",
            description="Student of Socrates",
            traits={"wisdom": 0.9},
        )

        mock_persistence.create_citizen.assert_awaited_once_with(
            name="Plato",
            archetype="dialectic",
            description="Student of Socrates",
            traits={"wisdom": 0.9},
        )

    @pytest.mark.asyncio
    async def test_citizen_create_without_name(self, town_node):
        """Citizen create without name returns error."""
        observer = Observer.test()
        result = await town_node.invoke("citizen.create", observer, archetype="poet")

        assert "error" in result


class TestTownNodeCitizenUpdate:
    """Tests for world.town.citizen.update aspect."""

    @pytest.mark.asyncio
    async def test_citizen_update_calls_persistence(self, town_node, mock_persistence):
        """Citizen update invokes persistence.update_citizen()."""
        observer = Observer.test()
        await town_node.invoke(
            "citizen.update",
            observer,
            citizen_id="citizen-abc123",
            description="New description",
            is_active=False,
        )

        mock_persistence.update_citizen.assert_awaited_once_with(
            citizen_id="citizen-abc123",
            description="New description",
            traits=None,
            is_active=False,
        )


# === Test Conversation Operations ===


class TestTownNodeConverse:
    """Tests for world.town.converse aspect."""

    @pytest.mark.asyncio
    async def test_converse_by_citizen_id(self, town_node, mock_persistence):
        """Converse by citizen ID invokes persistence.start_conversation()."""
        observer = Observer.test()
        await town_node.invoke(
            "converse",
            observer,
            citizen_id="citizen-abc123",
            topic="Philosophy",
        )

        mock_persistence.start_conversation.assert_awaited_once_with(
            citizen_id="citizen-abc123",
            topic="Philosophy",
        )

    @pytest.mark.asyncio
    async def test_converse_by_name(self, town_node, mock_persistence):
        """Converse by name resolves citizen first."""
        observer = Observer.test()
        await town_node.invoke(
            "converse",
            observer,
            name="Socrates",
            topic="Virtue",
        )

        mock_persistence.get_citizen_by_name.assert_awaited_once_with("Socrates")
        mock_persistence.start_conversation.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_converse_returns_conversation(self, town_node):
        """Converse returns ConversationRendering dict."""
        observer = Observer.test()
        result = await town_node.invoke("converse", observer, name="Socrates")

        assert result["type"] == "conversation"
        assert result["citizen_name"] == "Socrates"


class TestTownNodeTurn:
    """Tests for world.town.turn aspect."""

    @pytest.mark.asyncio
    async def test_turn_calls_persistence(self, town_node, mock_persistence):
        """Turn invokes persistence.add_turn()."""
        observer = Observer.test()
        await town_node.invoke(
            "turn",
            observer,
            conversation_id="conv-def456",
            role="user",
            content="What is virtue?",
            sentiment="curious",
        )

        mock_persistence.add_turn.assert_awaited_once_with(
            conversation_id="conv-def456",
            role="user",
            content="What is virtue?",
            sentiment="curious",
            emotion=None,
        )

    @pytest.mark.asyncio
    async def test_turn_without_content(self, town_node):
        """Turn without content returns error."""
        observer = Observer.test()
        result = await town_node.invoke(
            "turn",
            observer,
            conversation_id="conv-def456",
        )

        assert "error" in result


class TestTownNodeHistory:
    """Tests for world.town.history aspect."""

    @pytest.mark.asyncio
    async def test_history_calls_persistence(self, town_node, mock_persistence):
        """History invokes persistence.get_dialogue_history()."""
        observer = Observer.test()
        await town_node.invoke(
            "history",
            observer,
            citizen_id="citizen-abc123",
            limit=20,
        )

        mock_persistence.get_dialogue_history.assert_awaited_once_with(
            citizen_id="citizen-abc123",
            limit=20,
        )

    @pytest.mark.asyncio
    async def test_history_returns_conversations(self, town_node):
        """History returns conversation list."""
        observer = Observer.test()
        result = await town_node.invoke("history", observer, name="Socrates")

        assert "conversations" in result
        assert len(result["conversations"]) == 1


# === Test Relationship Operations ===


class TestTownNodeRelationships:
    """Tests for world.town.relationships aspect."""

    @pytest.mark.asyncio
    async def test_relationships_calls_persistence(self, town_node, mock_persistence):
        """Relationships invokes persistence.get_relationships()."""
        observer = Observer.test()
        await town_node.invoke("relationships", observer, citizen_id="citizen-abc123")

        mock_persistence.get_relationships.assert_awaited_once_with("citizen-abc123")

    @pytest.mark.asyncio
    async def test_relationships_returns_list(self, town_node):
        """Relationships returns RelationshipListRendering dict."""
        observer = Observer.test()
        result = await town_node.invoke("relationships", observer, name="Socrates")

        assert result["type"] == "relationship_list"
        assert result["count"] == 1


# === Test Simulation Operations ===


class TestTownNodeSimulation:
    """Tests for simulation aspects (gossip, step)."""

    @pytest.mark.asyncio
    async def test_gossip_returns_not_implemented(self, town_node):
        """Gossip returns not-implemented message (future work)."""
        observer = Observer.test()
        result = await town_node.invoke("gossip", observer)

        assert "message" in result
        assert "not yet implemented" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_step_returns_not_implemented(self, town_node):
        """Step returns not-implemented message (future work)."""
        observer = Observer.test()
        result = await town_node.invoke("step", observer)

        assert "message" in result
        assert "not yet implemented" in result["message"].lower()


# === Test Unknown Aspects ===


class TestTownNodeUnknownAspect:
    """Tests for unknown aspect handling."""

    @pytest.mark.asyncio
    async def test_unknown_aspect_returns_error(self, town_node):
        """Unknown aspects return error dict."""
        observer = Observer.test()
        result = await town_node.invoke("unknown_aspect", observer)

        assert "error" in result
        assert "unknown_aspect" in result["error"].lower()


# === Test Rendering Classes ===


class TestTownRenderings:
    """Tests for TownNode rendering classes."""

    def test_citizen_rendering_to_dict(self, mock_persistence):
        """CitizenRendering.to_dict() produces correct structure."""
        from services.town import CitizenView
        from services.town.node import CitizenRendering

        citizen = CitizenView(
            id="test-id",
            name="Test Citizen",
            archetype="test",
            description="Test description",
            traits={"trait": 0.5},
            is_active=True,
            interaction_count=10,
            last_interaction=None,
            created_at="2025-01-01T00:00:00",
        )

        rendering = CitizenRendering(citizen=citizen)
        data = rendering.to_dict()

        assert data["type"] == "citizen"
        assert data["name"] == "Test Citizen"
        assert data["archetype"] == "test"

    def test_citizen_rendering_to_text(self):
        """CitizenRendering.to_text() produces readable output."""
        from services.town import CitizenView
        from services.town.node import CitizenRendering

        citizen = CitizenView(
            id="test-id",
            name="Test Citizen",
            archetype="philosopher",
            description="A deep thinker",
            traits={"wisdom": 0.9},
            is_active=True,
            interaction_count=42,
            last_interaction=None,
            created_at="2025-01-01T00:00:00",
        )

        rendering = CitizenRendering(citizen=citizen)
        text = rendering.to_text()

        assert "Test Citizen" in text
        assert "philosopher" in text
        assert "active" in text.lower()

    def test_citizen_list_rendering_to_dict(self):
        """CitizenListRendering.to_dict() produces correct structure."""
        from services.town import CitizenView
        from services.town.node import CitizenListRendering

        citizens = [
            CitizenView(
                id=f"citizen-{i}",
                name=f"Citizen {i}",
                archetype="test",
                description=None,
                traits={},
                is_active=True,
                interaction_count=i,
                last_interaction=None,
                created_at="2025-01-01T00:00:00",
            )
            for i in range(3)
        ]

        rendering = CitizenListRendering(citizens=citizens, total=3)
        data = rendering.to_dict()

        assert data["type"] == "citizen_list"
        assert data["total"] == 3
        assert len(data["citizens"]) == 3

    def test_conversation_rendering_to_dict(self):
        """ConversationRendering.to_dict() produces correct structure."""
        from services.town import ConversationView, TurnView
        from services.town.node import ConversationRendering

        turns = [
            TurnView(
                id="turn-1",
                turn_number=0,
                role="user",
                content="Hello",
                sentiment=None,
                emotion=None,
                created_at="2025-01-01T00:00:00",
            )
        ]

        conversation = ConversationView(
            id="conv-1",
            citizen_id="citizen-1",
            citizen_name="Test",
            topic="Greeting",
            summary=None,
            turn_count=1,
            is_active=True,
            created_at="2025-01-01T00:00:00",
            turns=turns,
        )

        rendering = ConversationRendering(conversation=conversation)
        data = rendering.to_dict()

        assert data["type"] == "conversation"
        assert data["citizen_name"] == "Test"
        assert len(data["turns"]) == 1
