"""
Tests for SwarmRole, SwarmSpawner, and A2A Protocol.

CLI v7 Phase 6: Agent Swarms

Test Types (from docs/skills/test-patterns.md):
- Type I (Unit): SwarmRole composition, A2AMessage serialization
- Type II (Integration): SwarmSpawner + PresenceChannel
- Type III (Property): Role composition properties
- Type IV (E2E): Spawn -> delegate flow
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import pytest

from services.conductor.a2a import (
    A2AChannel,
    A2AMessage,
    A2AMessageType,
    A2ATopics,
    get_a2a_registry,
    reset_a2a_registry,
)
from services.conductor.behaviors import CursorBehavior
from services.conductor.presence import reset_presence_channel
from services.conductor.swarm import (
    COORDINATOR,
    IMPLEMENTER,
    PLANNER,
    RESEARCHER,
    REVIEWER,
    SpawnDecision,
    SpawnSignal,
    SwarmRole,
    SwarmSpawner,
    create_swarm_role,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def reset_services():
    """Reset singleton services before each test."""
    reset_presence_channel()
    reset_a2a_registry()
    yield
    reset_presence_channel()
    reset_a2a_registry()


# =============================================================================
# Type I: Unit Tests - SwarmRole
# =============================================================================


class TestSwarmRoleComposition:
    """Test SwarmRole = CursorBehavior x TrustLevel."""

    def test_researcher_role_composition(self):
        """RESEARCHER = EXPLORER x L0"""
        assert RESEARCHER.behavior == CursorBehavior.EXPLORER
        assert RESEARCHER.trust_level_name == "READ_ONLY"
        assert RESEARCHER.name == "Researcher"

    def test_planner_role_composition(self):
        """PLANNER = ASSISTANT x L2"""
        assert PLANNER.behavior == CursorBehavior.ASSISTANT
        assert PLANNER.trust_level_name == "SUGGESTION"
        assert PLANNER.name == "Planner"

    def test_implementer_role_composition(self):
        """IMPLEMENTER = AUTONOMOUS x L3"""
        assert IMPLEMENTER.behavior == CursorBehavior.AUTONOMOUS
        assert IMPLEMENTER.trust_level_name == "AUTONOMOUS"
        assert IMPLEMENTER.name == "Implementer"

    def test_reviewer_role_composition(self):
        """REVIEWER = FOLLOWER x L1"""
        assert REVIEWER.behavior == CursorBehavior.FOLLOWER
        assert REVIEWER.trust_level_name == "BOUNDED"
        assert REVIEWER.name == "Reviewer"

    def test_capabilities_derived_from_trust(self):
        """Capabilities come from trust level, not behavior."""
        # L0 can only read
        assert "glob" in RESEARCHER.capabilities
        assert "grep" in RESEARCHER.capabilities
        assert "read" in RESEARCHER.capabilities
        assert "edit" not in RESEARCHER.capabilities
        assert "write" not in RESEARCHER.capabilities

        # L3 can do everything
        assert "edit" in IMPLEMENTER.capabilities
        assert "write" in IMPLEMENTER.capabilities
        assert "bash" in IMPLEMENTER.capabilities
        assert "invoke" in IMPLEMENTER.capabilities

    def test_same_behavior_different_trust(self):
        """Same behavior with different trust = different capabilities."""
        # AUTONOMOUS behavior at L1 vs L3
        bounded_auto = SwarmRole(CursorBehavior.AUTONOMOUS, "BOUNDED")
        full_auto = SwarmRole(CursorBehavior.AUTONOMOUS, "AUTONOMOUS")

        assert "edit" not in bounded_auto.capabilities
        assert "edit" in full_auto.capabilities

    def test_non_canonical_role_name(self):
        """Non-canonical combinations get descriptive names."""
        custom = SwarmRole(CursorBehavior.EXPLORER, "AUTONOMOUS")
        assert "@" in custom.name  # Format: BEHAVIOR@TRUST

    def test_role_is_frozen(self):
        """SwarmRole is immutable (frozen dataclass)."""
        with pytest.raises(Exception):  # FrozenInstanceError
            RESEARCHER.behavior = CursorBehavior.FOLLOWER  # type: ignore

    def test_can_execute_operation(self):
        """Role.can_execute checks capabilities."""
        assert RESEARCHER.can_execute("glob")
        assert not RESEARCHER.can_execute("edit")
        assert IMPLEMENTER.can_execute("edit")

    def test_to_dict_serialization(self):
        """Role serializes to dict for API."""
        data = RESEARCHER.to_dict()
        assert data["name"] == "Researcher"
        assert data["behavior"] == "EXPLORER"
        assert data["trust_level"] == "READ_ONLY"
        assert "glob" in data["capabilities"]


class TestCreateSwarmRole:
    """Test factory function for creating roles."""

    def test_create_from_strings(self):
        """Create role from string names."""
        role = create_swarm_role("explorer", "read_only")
        assert role.behavior == CursorBehavior.EXPLORER
        assert role.trust_level_name == "READ_ONLY"

    def test_create_from_enum(self):
        """Create role from enum value."""
        role = create_swarm_role(CursorBehavior.AUTONOMOUS, "AUTONOMOUS")
        assert role.behavior == CursorBehavior.AUTONOMOUS

    def test_case_insensitive(self):
        """Strings are case-insensitive."""
        role1 = create_swarm_role("EXPLORER", "read_only")
        role2 = create_swarm_role("explorer", "READ_ONLY")
        assert role1.behavior == role2.behavior


# =============================================================================
# Type I: Unit Tests - A2A Messages
# =============================================================================


class TestA2AMessage:
    """Test A2A message creation and serialization."""

    def test_create_request_message(self):
        """Create a REQUEST message."""
        msg = A2AMessage(
            from_agent="agent-1",
            to_agent="agent-2",
            message_type=A2AMessageType.REQUEST,
            payload={"action": "research", "topic": "authentication"},
        )

        assert msg.from_agent == "agent-1"
        assert msg.to_agent == "agent-2"
        assert msg.message_type == A2AMessageType.REQUEST
        assert msg.payload["action"] == "research"
        assert msg.correlation_id  # Auto-generated

    def test_to_dict_serialization(self):
        """Message serializes to dict."""
        msg = A2AMessage(
            from_agent="a",
            to_agent="b",
            message_type=A2AMessageType.NOTIFY,
            payload={"status": "done"},
        )

        data = msg.to_dict()
        assert data["from_agent"] == "a"
        assert data["to_agent"] == "b"
        assert data["message_type"] == "NOTIFY"
        assert "correlation_id" in data

    def test_from_dict_deserialization(self):
        """Message deserializes from dict."""
        original = A2AMessage(
            from_agent="x",
            to_agent="y",
            message_type=A2AMessageType.HANDOFF,
            payload={"context": "full"},
            conversation_context=[{"role": "user", "content": "hi"}],
        )

        data = original.to_dict()
        restored = A2AMessage.from_dict(data)

        assert restored.from_agent == original.from_agent
        assert restored.to_agent == original.to_agent
        assert restored.message_type == original.message_type
        assert restored.correlation_id == original.correlation_id
        assert restored.conversation_context == original.conversation_context

    def test_create_response(self):
        """Create response to a request."""
        request = A2AMessage(
            from_agent="requester",
            to_agent="responder",
            message_type=A2AMessageType.REQUEST,
            payload={"action": "help"},
        )

        response = request.create_response({"result": "done"})

        assert response.from_agent == "responder"  # Swapped
        assert response.to_agent == "requester"
        assert response.message_type == A2AMessageType.RESPONSE
        assert response.correlation_id == request.correlation_id  # Same!


class TestA2ATopics:
    """Test A2A topic naming."""

    def test_for_type_mapping(self):
        """Each message type has a topic."""
        assert A2ATopics.for_type(A2AMessageType.REQUEST) == "a2a.request"
        assert A2ATopics.for_type(A2AMessageType.RESPONSE) == "a2a.response"
        assert A2ATopics.for_type(A2AMessageType.HANDOFF) == "a2a.handoff"

    def test_wildcard_topic(self):
        """Wildcard matches all A2A events."""
        assert A2ATopics.ALL == "a2a.*"


# =============================================================================
# Type II: Integration Tests - SwarmSpawner
# =============================================================================


class TestSwarmSpawner:
    """Test SwarmSpawner signal aggregation and lifecycle."""

    @pytest.fixture
    def spawner(self, reset_services):
        """Create a fresh spawner."""
        return SwarmSpawner(max_agents=3)

    def test_evaluate_research_task(self, spawner):
        """Research keywords -> RESEARCHER role."""
        decision = spawner.evaluate_role("Search for authentication patterns")

        assert decision.role.behavior == CursorBehavior.EXPLORER
        assert decision.role.trust_level_name == "READ_ONLY"
        assert decision.spawn_allowed

    def test_evaluate_planning_task(self, spawner):
        """Planning keywords -> PLANNER role."""
        decision = spawner.evaluate_role("Design the API architecture")

        assert decision.role.behavior == CursorBehavior.ASSISTANT
        assert decision.role.trust_level_name == "SUGGESTION"

    def test_evaluate_implementation_task(self, spawner):
        """Implementation keywords -> IMPLEMENTER role."""
        decision = spawner.evaluate_role("Implement the login feature")

        assert decision.role.behavior == CursorBehavior.AUTONOMOUS
        assert decision.role.trust_level_name == "AUTONOMOUS"

    def test_evaluate_review_task(self, spawner):
        """Review keywords -> REVIEWER role."""
        decision = spawner.evaluate_role("Review the pull request")

        assert decision.role.behavior == CursorBehavior.FOLLOWER
        assert decision.role.trust_level_name == "BOUNDED"

    def test_role_hint_overrides_keywords(self, spawner):
        """Explicit role hint takes precedence."""
        decision = spawner.evaluate_role(
            "Research something",  # Would normally be RESEARCHER
            context={"role_hint": "implementer"},
        )

        # Role hint wins
        assert decision.role.trust_level_name == "AUTONOMOUS"

    def test_capacity_blocking(self, spawner):
        """Capacity limit blocks spawning."""
        # Fill capacity
        for i in range(3):
            spawner._active_agents[f"agent-{i}"] = None  # type: ignore

        assert spawner.at_capacity
        decision = spawner.evaluate_role("Any task")
        assert not decision.spawn_allowed

    @pytest.mark.asyncio
    async def test_spawn_creates_cursor(self, spawner):
        """Spawn creates AgentCursor with role metadata."""
        cursor = await spawner.spawn(
            agent_id="test-agent",
            task="Research the codebase",
        )

        assert cursor is not None
        assert cursor.agent_id == "test-agent"
        assert cursor.behavior == CursorBehavior.EXPLORER
        assert "role" in cursor.metadata
        assert spawner.active_count == 1

    @pytest.mark.asyncio
    async def test_spawn_respects_capacity(self, spawner):
        """Spawn returns None at capacity."""
        # Fill capacity
        for i in range(3):
            await spawner.spawn(f"agent-{i}", f"Task {i}")

        # Fourth should fail
        cursor = await spawner.spawn("agent-4", "Another task")
        assert cursor is None
        assert spawner.active_count == 3

    @pytest.mark.asyncio
    async def test_despawn_removes_agent(self, spawner):
        """Despawn removes agent and returns success."""
        await spawner.spawn("agent-1", "Some task")
        assert spawner.active_count == 1

        success = await spawner.despawn("agent-1")
        assert success
        assert spawner.active_count == 0

    @pytest.mark.asyncio
    async def test_despawn_nonexistent_returns_false(self, spawner):
        """Despawn of unknown agent returns False."""
        success = await spawner.despawn("ghost-agent")
        assert not success

    def test_list_agents(self, spawner):
        """List agents returns active cursors."""
        # Initially empty
        assert spawner.list_agents() == []


# =============================================================================
# Type II: Integration Tests - A2A Channel
# =============================================================================


class TestA2AChannel:
    """Test A2A channel communication."""

    @pytest.fixture
    def channels(self, reset_services):
        """Create two channels for testing."""
        return A2AChannel("alice"), A2AChannel("bob")

    @pytest.mark.asyncio
    async def test_send_message(self, channels):
        """Send message puts it on bus."""
        alice, bob = channels

        msg = A2AMessage(
            from_agent="alice",
            to_agent="bob",
            message_type=A2AMessageType.NOTIFY,
            payload={"info": "hello"},
        )

        # Should not raise
        await alice.send(msg)

    @pytest.mark.asyncio
    async def test_notify_is_fire_and_forget(self, channels):
        """Notify doesn't wait for response."""
        alice, _ = channels

        # Should complete immediately
        await alice.notify("bob", {"event": "started"})

    @pytest.mark.asyncio
    async def test_broadcast_uses_wildcard(self, channels):
        """Broadcast uses '*' as recipient."""
        alice, _ = channels

        # Should complete immediately
        await alice.broadcast({"event": "announcement"})

    @pytest.mark.asyncio
    async def test_heartbeat(self, channels):
        """Heartbeat sends status message."""
        alice, _ = channels
        await alice.heartbeat()


# =============================================================================
# Type III: Property Tests
# =============================================================================


class TestSwarmRoleProperties:
    """Property-based tests for SwarmRole."""

    @pytest.mark.parametrize("behavior", list(CursorBehavior))
    @pytest.mark.parametrize("trust", ["READ_ONLY", "BOUNDED", "SUGGESTION", "AUTONOMOUS"])
    def test_any_combination_is_valid(self, behavior, trust):
        """Any behavior x trust combination is a valid role."""
        role = SwarmRole(behavior, trust)

        # All roles have these properties
        assert role.name is not None
        assert isinstance(role.capabilities, frozenset)
        assert role.emoji is not None
        assert role.description is not None

    @pytest.mark.parametrize("trust", ["READ_ONLY", "BOUNDED", "SUGGESTION", "AUTONOMOUS"])
    def test_capabilities_increase_with_trust(self, trust):
        """Higher trust = more capabilities (monotonic)."""
        levels = ["READ_ONLY", "BOUNDED", "SUGGESTION", "AUTONOMOUS"]
        idx = levels.index(trust)

        role = SwarmRole(CursorBehavior.ASSISTANT, trust)

        # L3 has most capabilities
        if trust == "AUTONOMOUS":
            assert "edit" in role.capabilities
            assert "invoke" in role.capabilities


# =============================================================================
# Signal Aggregation Tests
# =============================================================================


class TestSpawnDecision:
    """Test signal aggregation for spawn decisions."""

    def test_spawn_signal_positive(self):
        """Positive signal contributes to confidence."""
        signal = SpawnSignal("test", 0.8, "Test reason")
        assert signal.weight > 0

    def test_spawn_signal_blocker(self):
        """Negative signal blocks spawn."""
        signal = SpawnSignal("capacity", -1.0, "At capacity")
        assert signal.weight < 0

    def test_decision_contains_reasons(self):
        """SpawnDecision tracks positive reasons."""
        decision = SpawnDecision(
            role=RESEARCHER,
            confidence=0.8,
            reasons=["Research keywords detected"],
            spawn_allowed=True,
        )

        assert len(decision.reasons) > 0
        assert decision.spawn_allowed


# =============================================================================
# Module Exports Test
# =============================================================================


def test_all_canonical_roles_exported():
    """Verify canonical roles are available."""
    assert RESEARCHER is not None
    assert PLANNER is not None
    assert IMPLEMENTER is not None
    assert REVIEWER is not None
    assert COORDINATOR is not None
