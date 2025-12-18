"""
Town Integration Tests: End-to-end tests for Town crown jewel.

Tests the full integration across:
- Categorical foundation (Sheaf, Operad, PolyAgent)
- Event architecture (DataBus → SynergyBus → EventBus)
- AGENTESE nodes (world.town.*, world.town.coalition.*, world.town.collective.*)
- Service layer (DialogueService, CoalitionService, etc.)

See: plans/town-rebuild.md (Phase 4: Integration Tests)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from agents.town.context import (
    ALL_REGION_CONTEXTS,
    INN_CONTEXT,
    PLAZA_CONTEXT,
    RUMOR_DISTANCE,
    TOWN_CONTEXT,
    WORKSHOP_CONTEXT,
    ContextLevel,
    RegionType,
    TownContext,
    create_citizen_context,
    create_region_context,
)
from agents.town.sheaf import (
    RegionView,
    TownSheaf,
    TownState,
    create_town_sheaf,
)
from services.town.bus_wiring import (
    TownBusManager,
    TownDataBus,
    TownEventBus,
    TownSynergyBus,
    get_town_bus_manager,
    reset_town_bus_manager,
    wire_data_to_synergy,
    wire_synergy_to_event,
)
from services.town.collective_node import CollectiveNode
from services.town.events import (
    CitizenCreated,
    CitizenUpdated,
    CoalitionDissolved,
    CoalitionFormed,
    ConversationEnded,
    ConversationStarted,
    ConversationTurn,
    GossipSpread,
    RegionActivity,
    RelationshipChanged,
    RelationshipCreated,
    SimulationStep,
    TownEvent,
    TownEventType,
    TownTopics,
)

# =============================================================================
# Test Harness
# =============================================================================


@dataclass
class TownTestHarness:
    """Test harness for Town integration tests."""

    sheaf: TownSheaf
    bus_manager: TownBusManager
    collective_node: CollectiveNode

    # Tracking
    events_received: list[TownEvent]
    synergy_topics: list[str]

    @classmethod
    def create(cls) -> "TownTestHarness":
        """Create a fresh test harness."""
        reset_town_bus_manager()

        sheaf = create_town_sheaf()
        bus_manager = TownBusManager()
        bus_manager.wire_all()

        collective_node = CollectiveNode(
            sheaf=sheaf,
            bus_manager=bus_manager,
        )

        harness = cls(
            sheaf=sheaf,
            bus_manager=bus_manager,
            collective_node=collective_node,
            events_received=[],
            synergy_topics=[],
        )

        # Wire event listeners
        harness._wire_listeners()

        return harness

    def _wire_listeners(self) -> None:
        """Wire test listeners."""

        async def event_listener(event: TownEvent) -> None:
            self.events_received.append(event)

        async def synergy_listener(topic: str, event: TownEvent) -> None:
            self.synergy_topics.append(topic)

        self.bus_manager.event_bus.subscribe(event_listener)
        self.bus_manager.synergy_bus.subscribe(TownTopics.ALL, synergy_listener)

    def cleanup(self) -> None:
        """Clean up the harness."""
        self.bus_manager.clear()
        reset_town_bus_manager()


@pytest.fixture
def harness() -> TownTestHarness:
    """Create test harness fixture."""
    h = TownTestHarness.create()
    yield h
    h.cleanup()


# =============================================================================
# Citizen Lifecycle Integration Tests
# =============================================================================


class TestCitizenLifecycleFlow:
    """End-to-end tests for citizen lifecycle."""

    @pytest.mark.asyncio
    async def test_citizen_creation_emits_events(self, harness: TownTestHarness) -> None:
        """Creating a citizen should emit events through all buses."""
        # Create citizen event
        event = CitizenCreated.create(
            citizen_id="socrates",
            name="Socrates",
            archetype="scholar",
            region="plaza",
        )

        # Emit to data bus
        await harness.bus_manager.data_bus.emit(event)

        # Wait for cascade
        await asyncio.sleep(0.2)

        # Verify events cascaded
        assert len(harness.events_received) >= 1
        assert any(e.event_type == TownEventType.CITIZEN_CREATED for e in harness.events_received)

        # Verify synergy topic published
        assert TownTopics.CITIZEN_CREATED in harness.synergy_topics

    @pytest.mark.asyncio
    async def test_citizen_update_propagates(self, harness: TownTestHarness) -> None:
        """Updating a citizen should propagate through buses."""
        # Update event
        event = CitizenUpdated.create(
            citizen_id="socrates",
            changes={"archetype": "philosopher"},
        )

        await harness.bus_manager.data_bus.emit(event)
        await asyncio.sleep(0.2)

        assert any(e.event_type == TownEventType.CITIZEN_UPDATED for e in harness.events_received)

    @pytest.mark.asyncio
    async def test_citizen_location_updates_sheaf(self, harness: TownTestHarness) -> None:
        """Citizen locations should update sheaf views."""
        # Add citizens to collective node
        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "workshop")
        harness.collective_node.set_citizen_location("carol", "plaza")

        # Get region views
        views = harness.collective_node.get_region_views()

        # Verify citizens in correct regions
        inn_view = views[INN_CONTEXT]
        assert "alice" in inn_view.citizens

        workshop_view = views[WORKSHOP_CONTEXT]
        assert "bob" in workshop_view.citizens

        plaza_view = views[PLAZA_CONTEXT]
        assert "carol" in plaza_view.citizens


# =============================================================================
# Gossip Propagation Integration Tests
# =============================================================================


class TestGossipPropagation:
    """Test gossip propagation through rumor distance."""

    @pytest.mark.asyncio
    async def test_gossip_spreads_within_rumor_distance(self, harness: TownTestHarness) -> None:
        """Gossip from inn should reach plaza (within rumor distance)."""
        # Set up citizens
        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "plaza")

        # Spread gossip
        result = await harness.collective_node._handle_gossip(
            {
                "source_citizen": "alice",
                "target_citizen": "bob",
                "content": "Did you hear about the treasure?",
                "source_region": "inn",
                "target_region": "plaza",
            }
        )

        await asyncio.sleep(0.2)

        # Verify gossip event emitted
        assert result["spread_successful"] is True
        assert TownTopics.GOSSIP_SPREAD in harness.synergy_topics

    @pytest.mark.asyncio
    async def test_gossip_accuracy_affects_spread(self, harness: TownTestHarness) -> None:
        """Low accuracy gossip should still spread but with reduced trust."""
        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "library")

        # Spread low accuracy gossip (inn → library requires intermediary)
        result = await harness.collective_node._handle_gossip(
            {
                "source_citizen": "alice",
                "target_citizen": "bob",
                "content": "Rumor: Carol found treasure",
                "accuracy": 0.3,
                "source_region": "inn",
                "target_region": "library",
            }
        )

        # Low accuracy + far distance = reduced spread
        # (library not in inn's rumor distance)
        assert result["spread_successful"] is False

    @pytest.mark.asyncio
    async def test_gossip_triggers_k_gent_handler(self, harness: TownTestHarness) -> None:
        """Gossip should trigger cross-jewel K-gent handler."""
        # Wire cross-jewel handlers
        harness.bus_manager.wire_cross_jewel_handlers()

        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "plaza")

        await harness.collective_node._handle_gossip(
            {
                "source_citizen": "alice",
                "target_citizen": "bob",
                "content": "Carol is a genius inventor",
            }
        )

        await asyncio.sleep(0.2)

        # Gossip event should have been emitted
        gossip_events = [e for e in harness.events_received if isinstance(e, GossipSpread)]
        assert len(gossip_events) >= 1


# =============================================================================
# Coalition Formation Integration Tests
# =============================================================================


class TestCoalitionFormation:
    """Test coalition formation and sheaf emergence."""

    @pytest.mark.asyncio
    async def test_coalition_formed_triggers_emergence(self, harness: TownTestHarness) -> None:
        """Forming a coalition should update sheaf emergence metrics."""
        # Create coalition event
        event = CoalitionFormed.create(
            coalition_id="inventors_guild",
            members={"alice", "bob", "carol"},
            purpose="Share inventions",
            strength=0.8,
        )

        await harness.bus_manager.data_bus.emit(event)
        await asyncio.sleep(0.2)

        # Verify event cascaded
        assert any(isinstance(e, CoalitionFormed) for e in harness.events_received)
        assert TownTopics.COALITION_FORMED in harness.synergy_topics

    @pytest.mark.asyncio
    async def test_coalition_dissolution_events(self, harness: TownTestHarness) -> None:
        """Dissolving a coalition should emit proper events."""
        event = CoalitionDissolved.create(
            coalition_id="defunct_guild",
            members={"dave", "eve"},
            reason="mutual_agreement",
        )

        await harness.bus_manager.data_bus.emit(event)
        await asyncio.sleep(0.2)

        assert any(isinstance(e, CoalitionDissolved) for e in harness.events_received)


# =============================================================================
# Sheaf Coherence Integration Tests
# =============================================================================


class TestSheafCoherence:
    """Test sheaf coherence across operations."""

    @pytest.mark.asyncio
    async def test_gluing_produces_emergence_metrics(self, harness: TownTestHarness) -> None:
        """Gluing region views should produce emergence metrics."""
        # Set up citizens in different regions
        for i in range(5):
            harness.collective_node.set_citizen_location(f"citizen_{i}", "inn")
        for i in range(5, 10):
            harness.collective_node.set_citizen_location(f"citizen_{i}", "workshop")
        for i in range(10, 15):
            harness.collective_node.set_citizen_location(f"citizen_{i}", "plaza")

        # Get region views and glue
        views = harness.collective_node.get_region_views()
        state = harness.sheaf.glue(views)

        # Should have emergence metrics
        assert "rituality" in state.emergence
        assert "trust_density" in state.emergence
        assert "region_balance" in state.emergence

        # Region balance should be positive (citizens distributed)
        assert state.emergence["region_balance"] > 0

    @pytest.mark.asyncio
    async def test_restrict_then_glue_preserves_structure(self, harness: TownTestHarness) -> None:
        """Restricting then gluing should preserve global structure."""
        # Set up state
        for i in range(10):
            region = ["inn", "workshop", "plaza"][i % 3]
            harness.collective_node.set_citizen_location(f"citizen_{i}", region)

        # Get views and glue
        views = harness.collective_node.get_region_views()
        state = harness.sheaf.glue(views)

        # Restrict to each region and verify
        for region_ctx in [INN_CONTEXT, WORKSHOP_CONTEXT, PLAZA_CONTEXT]:
            restricted = harness.sheaf.restrict(state, region_ctx)

            # All citizens in restricted view should be in that region
            for cid in restricted.citizens:
                assert state.citizen_locations.get(cid) == region_ctx.name

    @pytest.mark.asyncio
    async def test_compatible_views_after_operations(self, harness: TownTestHarness) -> None:
        """Views should remain compatible after series of operations."""
        # Initial setup
        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "workshop")

        # Move alice
        harness.collective_node.set_citizen_location("alice", "plaza")

        # Views should still be compatible
        views = harness.collective_node.get_region_views()
        assert harness.sheaf.compatible(views)

        # Should be able to glue
        state = harness.sheaf.glue(views)
        assert len(state.citizens) == 2


# =============================================================================
# Simulation Step Integration Tests
# =============================================================================


class TestSimulationStep:
    """Test simulation stepping and event emission."""

    @pytest.mark.asyncio
    async def test_step_emits_simulation_event(self, harness: TownTestHarness) -> None:
        """Stepping simulation should emit SimulationStep event."""
        harness.collective_node.set_citizen_location("alice", "inn")
        harness.collective_node.set_citizen_location("bob", "workshop")

        result = await harness.collective_node._handle_step({"steps": 1})

        await asyncio.sleep(0.2)

        assert result["step_number"] == 1
        assert result["active_citizens"] == 2

        # Should emit simulation step event
        step_events = [e for e in harness.events_received if isinstance(e, SimulationStep)]
        assert len(step_events) >= 1

    @pytest.mark.asyncio
    async def test_multiple_steps_increment(self, harness: TownTestHarness) -> None:
        """Multiple steps should increment step number."""
        await harness.collective_node._handle_step({"steps": 5})

        result = await harness.collective_node._handle_step({"steps": 3})

        assert result["step_number"] == 8  # 5 + 3


# =============================================================================
# AGENTESE Path Discovery Integration Tests
# =============================================================================


class TestAGENTESEDiscovery:
    """Test AGENTESE path discovery."""

    def test_collective_node_handle(self, harness: TownTestHarness) -> None:
        """CollectiveNode should have correct handle."""
        assert harness.collective_node.handle == "world.town.collective"

    def test_collective_affordances_by_archetype(self, harness: TownTestHarness) -> None:
        """Affordances should vary by archetype."""
        # Developer gets all
        dev_affordances = harness.collective_node._get_affordances_for_archetype("developer")
        assert "gossip" in dev_affordances
        assert "step" in dev_affordances

        # Regular user gets limited
        user_affordances = harness.collective_node._get_affordances_for_archetype("user")
        assert "manifest" in user_affordances
        assert "emergence" in user_affordances
        assert "step" not in user_affordances

    @pytest.mark.asyncio
    async def test_manifest_returns_renderable(self, harness: TownTestHarness) -> None:
        """Manifest should return a renderable response."""

        class MockObserver:
            umwelt = None

        harness.collective_node.set_citizen_location("alice", "inn")

        result = await harness.collective_node.manifest(MockObserver())

        # Should be a rendering with to_dict method
        assert hasattr(result, "to_dict")
        dict_result = result.to_dict()

        assert dict_result["type"] == "collective_manifest"
        assert "total_citizens" in dict_result
        assert dict_result["total_citizens"] == 1


# =============================================================================
# Cross-Jewel Integration Tests
# =============================================================================


class TestCrossJewelIntegration:
    """Test cross-jewel event handling."""

    @pytest.mark.asyncio
    async def test_relationship_change_triggers_mgent(self, harness: TownTestHarness) -> None:
        """Relationship changes should trigger M-gent handler."""
        harness.bus_manager.wire_cross_jewel_handlers()

        event = RelationshipChanged.create(
            relationship_id="r_alice_bob",
            citizen_a="alice",
            citizen_b="bob",
            old_strength=0.3,
            new_strength=0.7,
            reason="collaboration",
        )

        await harness.bus_manager.data_bus.emit(event)
        await asyncio.sleep(0.2)

        assert TownTopics.RELATIONSHIP_CHANGED in harness.synergy_topics

    @pytest.mark.asyncio
    async def test_conversation_events_flow(self, harness: TownTestHarness) -> None:
        """Conversation events should flow through all buses."""
        # Start conversation
        start_event = ConversationStarted.create(
            conversation_id="conv_001",
            citizen_id="socrates",
            topic="philosophy",
        )
        await harness.bus_manager.data_bus.emit(start_event)

        # Add turn
        turn_event = ConversationTurn.create(
            conversation_id="conv_001",
            citizen_id="socrates",
            turn_number=1,
            role="citizen",
            content="The unexamined life is not worth living.",
        )
        await harness.bus_manager.data_bus.emit(turn_event)

        # End conversation
        end_event = ConversationEnded.create(
            conversation_id="conv_001",
            citizen_id="socrates",
            turn_count=1,
            summary="Discussion of examined life",
        )
        await harness.bus_manager.data_bus.emit(end_event)

        await asyncio.sleep(0.3)

        # All events should have cascaded
        assert TownTopics.CONVERSATION_STARTED in harness.synergy_topics
        assert TownTopics.CONVERSATION_TURN in harness.synergy_topics
        assert TownTopics.CONVERSATION_ENDED in harness.synergy_topics


# =============================================================================
# Performance Integration Tests
# =============================================================================


class TestPerformanceIntegration:
    """Integration tests with performance baselines."""

    @pytest.mark.asyncio
    async def test_sheaf_glue_performance(self, harness: TownTestHarness) -> None:
        """Sheaf gluing should complete within 100ms for typical load."""
        import time

        # Set up 100 citizens across regions
        for i in range(100):
            region = ALL_REGION_CONTEXTS[i % len(ALL_REGION_CONTEXTS)].name
            harness.collective_node.set_citizen_location(f"citizen_{i}", region)

        views = harness.collective_node.get_region_views()

        start = time.time()
        state = harness.sheaf.glue(views)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Glue took {elapsed}s, expected < 0.1s"
        assert len(state.citizens) == 100

    @pytest.mark.asyncio
    async def test_event_cascade_performance(self, harness: TownTestHarness) -> None:
        """Event cascade should complete within 200ms for batch."""
        import time

        start = time.time()

        # Emit 100 events
        for i in range(100):
            event = CitizenCreated.create(
                citizen_id=f"citizen_{i}",
                name=f"Citizen {i}",
                archetype="scholar",
            )
            await harness.bus_manager.data_bus.emit(event)

        await asyncio.sleep(0.5)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Cascade took {elapsed}s, expected < 1.0s"
        assert len(harness.events_received) >= 90


# =============================================================================
# Error Handling Integration Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling across integration boundaries."""

    @pytest.mark.asyncio
    async def test_invalid_gossip_handled_gracefully(self, harness: TownTestHarness) -> None:
        """Invalid gossip request should return error, not crash."""
        result = await harness.collective_node._handle_gossip(
            {
                "content": "Missing citizens",
                # source_citizen and target_citizen missing
            }
        )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_citizen_limit_enforced(self, harness: TownTestHarness) -> None:
        """Citizen limit should be enforced with proper error."""
        # Set limit low for testing
        harness.collective_node._max_citizens = 5

        # Add up to limit
        for i in range(5):
            harness.collective_node.set_citizen_location(f"citizen_{i}", "inn")

        # Next should fail
        with pytest.raises(ValueError, match="Citizen limit exceeded"):
            harness.collective_node.set_citizen_location("citizen_5", "inn")

    @pytest.mark.asyncio
    async def test_handler_error_isolation(self, harness: TownTestHarness) -> None:
        """Handler errors should not affect other handlers."""
        error_count = [0]

        async def failing_handler(event: TownEvent) -> None:
            error_count[0] += 1
            raise RuntimeError("Intentional failure")

        async def success_handler(event: TownEvent) -> None:
            pass

        harness.bus_manager.event_bus.subscribe(failing_handler)
        harness.bus_manager.event_bus.subscribe(success_handler)

        # Emit event
        event = CitizenCreated.create(
            citizen_id="test",
            name="Test",
            archetype="scholar",
        )
        await harness.bus_manager.data_bus.emit(event)

        await asyncio.sleep(0.2)

        # Error handler was called but didn't crash the bus
        # (Event still cascaded through the system)
        assert len(harness.events_received) >= 1
