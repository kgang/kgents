"""Tests for Town Events module."""

from __future__ import annotations

import time

import pytest

from services.town.events import (
    # Citizen events
    CitizenCreated,
    CitizenDeactivated,
    CitizenUpdated,
    CoalitionDissolved,
    CoalitionFormed,
    ConversationEnded,
    # Conversation events
    ConversationStarted,
    ConversationTurn,
    ForceApplied,
    # Social events
    GossipSpread,
    InhabitEnded,
    # Inhabit events
    InhabitStarted,
    RegionActivity,
    RelationshipChanged,
    # Relationship events
    RelationshipCreated,
    # Simulation events
    SimulationStep,
    TownEvent,
    TownEventType,
    TownTopics,
)


class TestTownEventType:
    """Tests for TownEventType enum."""

    def test_all_types_exist(self) -> None:
        """All expected event types should exist."""
        assert TownEventType.CITIZEN_CREATED
        assert TownEventType.CITIZEN_UPDATED
        assert TownEventType.CONVERSATION_STARTED
        assert TownEventType.CONVERSATION_TURN
        assert TownEventType.RELATIONSHIP_CHANGED
        assert TownEventType.GOSSIP_SPREAD
        assert TownEventType.COALITION_FORMED
        assert TownEventType.INHABIT_STARTED
        assert TownEventType.SIMULATION_STEP

    def test_types_are_unique(self) -> None:
        """Each event type should have a unique value."""
        values = [t.value for t in TownEventType]
        assert len(values) == len(set(values))


class TestCitizenCreated:
    """Tests for CitizenCreated event."""

    def test_create_basic(self) -> None:
        """Basic creation should work."""
        event = CitizenCreated.create(
            citizen_id="c1",
            name="Alice",
            archetype="scholar",
        )
        assert event.citizen_id == "c1"
        assert event.name == "Alice"
        assert event.archetype == "scholar"
        assert event.event_type == TownEventType.CITIZEN_CREATED

    def test_create_with_traits(self) -> None:
        """Creation with traits should work."""
        event = CitizenCreated.create(
            citizen_id="c1",
            name="Alice",
            archetype="scholar",
            traits={"curiosity": 0.9, "patience": 0.7},
        )
        assert len(event.traits) == 2
        assert ("curiosity", 0.9) in event.traits

    def test_event_id_is_unique(self) -> None:
        """Each event should have a unique ID."""
        e1 = CitizenCreated.create("c1", "A", "x")
        e2 = CitizenCreated.create("c2", "B", "y")
        assert e1.event_id != e2.event_id

    def test_timestamp_is_recent(self) -> None:
        """Timestamp should be recent."""
        event = CitizenCreated.create("c1", "A", "x")
        now = time.time()
        assert abs(event.timestamp - now) < 1.0

    def test_is_frozen(self) -> None:
        """Event should be immutable."""
        event = CitizenCreated.create("c1", "A", "x")
        with pytest.raises(AttributeError):
            event.name = "Changed"  # type: ignore

    def test_causal_parent(self) -> None:
        """Causal parent should be stored."""
        event = CitizenCreated.create(
            citizen_id="c1",
            name="A",
            archetype="x",
            causal_parent="parent-123",
        )
        assert event.causal_parent == "parent-123"


class TestCitizenUpdated:
    """Tests for CitizenUpdated event."""

    def test_create_with_changes(self) -> None:
        """Should store changes as tuples."""
        event = CitizenUpdated.create(
            citizen_id="c1",
            changes={"description": "New desc", "traits": {"x": 1}},
        )
        assert event.citizen_id == "c1"
        assert len(event.changes) == 2
        assert event.event_type == TownEventType.CITIZEN_UPDATED


class TestConversationTurn:
    """Tests for ConversationTurn event."""

    def test_create_basic(self) -> None:
        """Basic creation should work."""
        event = ConversationTurn.create(
            conversation_id="conv-1",
            citizen_id="c1",
            turn_number=0,
            role="user",
            content="Hello!",
        )
        assert event.conversation_id == "conv-1"
        assert event.turn_number == 0
        assert event.role == "user"
        assert event.content == "Hello!"

    def test_with_sentiment_emotion(self) -> None:
        """Should store sentiment and emotion."""
        event = ConversationTurn.create(
            conversation_id="conv-1",
            citizen_id="c1",
            turn_number=1,
            role="citizen",
            content="Hi there!",
            sentiment="positive",
            emotion="happy",
        )
        assert event.sentiment == "positive"
        assert event.emotion == "happy"


class TestRelationshipChanged:
    """Tests for RelationshipChanged event."""

    def test_create_with_strengths(self) -> None:
        """Should store strength changes."""
        event = RelationshipChanged.create(
            relationship_id="rel-1",
            citizen_a="alice",
            citizen_b="bob",
            old_strength=0.5,
            new_strength=0.8,
            reason="positive_interaction",
        )
        assert event.old_strength == 0.5
        assert event.new_strength == 0.8
        assert event.reason == "positive_interaction"


class TestGossipSpread:
    """Tests for GossipSpread event."""

    def test_create_basic(self) -> None:
        """Basic gossip event."""
        event = GossipSpread.create(
            source_citizen="alice",
            target_citizen="bob",
            rumor_content="Carol found treasure",
        )
        assert event.source_citizen == "alice"
        assert event.target_citizen == "bob"
        assert event.accuracy == 1.0  # Default accurate

    def test_with_accuracy(self) -> None:
        """Gossip with accuracy."""
        event = GossipSpread.create(
            source_citizen="alice",
            target_citizen="bob",
            rumor_content="Exaggerated tale",
            accuracy=0.3,
        )
        assert event.accuracy == 0.3


class TestCoalitionFormed:
    """Tests for CoalitionFormed event."""

    def test_create_with_members(self) -> None:
        """Should store members as frozenset."""
        event = CoalitionFormed.create(
            coalition_id="coal-1",
            members={"alice", "bob", "carol"},
            purpose="research",
        )
        assert event.coalition_id == "coal-1"
        assert len(event.members) == 3
        assert "alice" in event.members
        assert isinstance(event.members, frozenset)

    def test_members_from_set_and_frozenset(self) -> None:
        """Should accept both set and frozenset."""
        e1 = CoalitionFormed.create("c1", {"a", "b"})
        e2 = CoalitionFormed.create("c2", frozenset(["a", "b"]))
        assert e1.members == e2.members


class TestInhabitEvents:
    """Tests for Inhabit events."""

    def test_inhabit_started(self) -> None:
        """InhabitStarted should store mode."""
        event = InhabitStarted.create(
            user_id="user-1",
            citizen_id="c1",
            inhabit_mode="full",
        )
        assert event.inhabit_mode == "full"

    def test_inhabit_ended(self) -> None:
        """InhabitEnded should store duration."""
        event = InhabitEnded.create(
            user_id="user-1",
            citizen_id="c1",
            duration_seconds=3600.0,
            actions_taken=15,
        )
        assert event.duration_seconds == 3600.0
        assert event.actions_taken == 15

    def test_force_applied(self) -> None:
        """ForceApplied should track consent debt."""
        event = ForceApplied.create(
            user_id="user-1",
            citizen_id="c1",
            action="say_something",
            severity=0.3,
            debt_after=0.5,
        )
        assert event.severity == 0.3
        assert event.debt_after == 0.5


class TestSimulationEvents:
    """Tests for Simulation events."""

    def test_simulation_step(self) -> None:
        """SimulationStep should track step metrics."""
        event = SimulationStep.create(
            step_number=42,
            active_citizens=10,
            interactions=5,
            coalitions_changed=2,
        )
        assert event.step_number == 42
        assert event.active_citizens == 10
        assert event.interactions == 5

    def test_region_activity(self) -> None:
        """RegionActivity should track region metrics."""
        event = RegionActivity.create(
            region="inn",
            citizen_count=5,
            activity_type="gathering",
            details="Evening social",
        )
        assert event.region == "inn"
        assert event.activity_type == "gathering"


class TestTownTopics:
    """Tests for TownTopics constants."""

    def test_citizen_topics_exist(self) -> None:
        """Citizen topics should be defined."""
        assert TownTopics.CITIZEN_CREATED == "town.citizen.created"
        assert TownTopics.CITIZEN_UPDATED == "town.citizen.updated"

    def test_social_topics_exist(self) -> None:
        """Social topics should be defined."""
        assert TownTopics.GOSSIP_SPREAD == "town.social.gossip"
        assert TownTopics.COALITION_FORMED == "town.social.coalition.formed"

    def test_wildcard_topics(self) -> None:
        """Wildcard topics should be defined."""
        assert TownTopics.ALL == "town.*"
        assert TownTopics.CITIZEN_ALL == "town.citizen.*"
        assert TownTopics.SOCIAL_ALL == "town.social.*"

    def test_all_topics_start_with_town(self) -> None:
        """All topics should start with 'town.'."""
        topics = [
            TownTopics.CITIZEN_CREATED,
            TownTopics.CONVERSATION_TURN,
            TownTopics.GOSSIP_SPREAD,
            TownTopics.SIMULATION_STEP,
        ]
        for topic in topics:
            assert topic.startswith("town.")


class TestEventHashability:
    """Tests for event hashability (required for sets/dicts)."""

    def test_citizen_created_hashable(self) -> None:
        """CitizenCreated should be hashable."""
        event = CitizenCreated.create("c1", "A", "x")
        events = {event}
        assert len(events) == 1

    def test_conversation_turn_hashable(self) -> None:
        """ConversationTurn should be hashable."""
        event = ConversationTurn.create("conv", "c1", 0, "user", "Hi")
        events = {event}
        assert len(events) == 1

    def test_coalition_formed_hashable(self) -> None:
        """CoalitionFormed should be hashable."""
        event = CoalitionFormed.create("coal", {"a", "b"})
        events = {event}
        assert len(events) == 1
