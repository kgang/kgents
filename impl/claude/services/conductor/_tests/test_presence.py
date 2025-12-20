"""
Tests for Agent Presence module.

CLI v7 Phase 3: Agent Presence

Following T-gent taxonomy:
- Type I (Unit): State properties, transitions, serialization
- Type II (Integration): Channel broadcast, subscribe
- Type III (Property): State cycle validity, animation bounds
"""

from __future__ import annotations

import asyncio
from datetime import datetime

import pytest
from hypothesis import given, settings, strategies as st

from services.conductor.presence import (
    AgentCursor,
    CircadianPhase,
    CursorState,
    PresenceChannel,
    PresenceEventType,
    PresenceUpdate,
    get_presence_channel,
    render_presence_footer,
    reset_presence_channel,
)

# =============================================================================
# Type I: Unit Tests - CursorState
# =============================================================================


class TestCursorStateProperties:
    """Test CursorState enum properties (Pattern #2)."""

    def test_all_states_have_emoji(self):
        """Every state has an emoji."""
        for state in CursorState:
            assert len(state.emoji) > 0, f"{state.name} missing emoji"

    def test_all_states_have_color(self):
        """Every state has a CLI color."""
        for state in CursorState:
            assert len(state.color) > 0, f"{state.name} missing color"

    def test_all_states_have_tailwind_color(self):
        """Every state has a Tailwind CSS class."""
        for state in CursorState:
            assert state.tailwind_color.startswith("text-"), (
                f"{state.name} tailwind_color should start with 'text-'"
            )

    def test_animation_speed_in_range(self):
        """Animation speed is between 0.0 and 1.0."""
        for state in CursorState:
            assert 0.0 <= state.animation_speed <= 1.0, f"{state.name} animation_speed out of range"

    def test_all_states_have_description(self):
        """Every state has a human-readable description."""
        for state in CursorState:
            assert len(state.description) > 0, f"{state.name} missing description"

    def test_waiting_is_slowest(self):
        """WAITING state should have slowest animation."""
        waiting_speed = CursorState.WAITING.animation_speed
        for state in CursorState:
            if state != CursorState.WAITING:
                assert state.animation_speed >= waiting_speed, (
                    f"WAITING should be slowest, but {state.name} is slower"
                )

    def test_exploring_is_fastest(self):
        """EXPLORING state should have fastest animation."""
        exploring_speed = CursorState.EXPLORING.animation_speed
        for state in CursorState:
            assert state.animation_speed <= exploring_speed, (
                f"EXPLORING should be fastest, but {state.name} is faster"
            )


class TestCursorStateTransitions:
    """Test CursorState transition graph (Pattern #9)."""

    def test_all_states_have_transitions(self):
        """Every state has at least one valid transition."""
        for state in CursorState:
            assert len(state.can_transition_to) > 0, f"{state.name} has no valid transitions"

    def test_waiting_can_transition_to_active_states(self):
        """WAITING can wake up to any active state."""
        waiting = CursorState.WAITING
        assert CursorState.FOLLOWING in waiting.can_transition_to
        assert CursorState.EXPLORING in waiting.can_transition_to
        assert CursorState.WORKING in waiting.can_transition_to

    def test_working_can_complete_to_suggesting(self):
        """WORKING can complete with a suggestion."""
        assert CursorState.SUGGESTING in CursorState.WORKING.can_transition_to

    def test_working_can_pause_to_waiting(self):
        """WORKING can pause back to WAITING."""
        assert CursorState.WAITING in CursorState.WORKING.can_transition_to

    def test_suggesting_returns_to_following_or_waiting(self):
        """SUGGESTING leads to either FOLLOWING or WAITING."""
        suggesting = CursorState.SUGGESTING
        assert CursorState.FOLLOWING in suggesting.can_transition_to
        assert CursorState.WAITING in suggesting.can_transition_to

    def test_can_transition_method(self):
        """can_transition() method works correctly."""
        waiting = CursorState.WAITING
        assert waiting.can_transition(CursorState.WORKING) is True
        assert waiting.can_transition(CursorState.SUGGESTING) is False

    def test_no_self_transitions(self):
        """States cannot transition to themselves."""
        for state in CursorState:
            assert state not in state.can_transition_to, (
                f"{state.name} can transition to itself (invalid)"
            )


# =============================================================================
# Type I: Unit Tests - CircadianPhase
# =============================================================================


class TestCircadianPhase:
    """Test CircadianPhase enum (Pattern #11)."""

    def test_from_hour_covers_24_hours(self):
        """Every hour maps to a phase."""
        for hour in range(24):
            phase = CircadianPhase.from_hour(hour)
            assert isinstance(phase, CircadianPhase)

    def test_dawn_hours(self):
        """Dawn is 5-9."""
        for hour in [5, 6, 7, 8]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.DAWN

    def test_morning_hours(self):
        """Morning is 9-12."""
        for hour in [9, 10, 11]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.MORNING

    def test_noon_hours(self):
        """Noon is 12-14."""
        for hour in [12, 13]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.NOON

    def test_afternoon_hours(self):
        """Afternoon is 14-17."""
        for hour in [14, 15, 16]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.AFTERNOON

    def test_dusk_hours(self):
        """Dusk is 17-20."""
        for hour in [17, 18, 19]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.DUSK

    def test_evening_hours(self):
        """Evening is 20-23."""
        for hour in [20, 21, 22]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.EVENING

    def test_night_hours(self):
        """Night is 23-5."""
        for hour in [23, 0, 1, 2, 3, 4]:
            assert CircadianPhase.from_hour(hour) == CircadianPhase.NIGHT

    def test_tempo_modifier_in_range(self):
        """Tempo modifier is between 0.0 and 1.0."""
        for phase in CircadianPhase:
            assert 0.0 <= phase.tempo_modifier <= 1.0

    def test_warmth_in_range(self):
        """Warmth is between 0.0 and 1.0."""
        for phase in CircadianPhase:
            assert 0.0 <= phase.warmth <= 1.0

    def test_morning_is_most_energetic(self):
        """Morning has highest tempo modifier."""
        morning_tempo = CircadianPhase.MORNING.tempo_modifier
        for phase in CircadianPhase:
            assert phase.tempo_modifier <= morning_tempo

    def test_dusk_is_warmest(self):
        """Dusk has highest warmth."""
        dusk_warmth = CircadianPhase.DUSK.warmth
        for phase in CircadianPhase:
            assert phase.warmth <= dusk_warmth


# =============================================================================
# Type I: Unit Tests - AgentCursor
# =============================================================================


class TestAgentCursor:
    """Test AgentCursor dataclass."""

    def test_create_cursor(self):
        """Basic cursor creation."""
        cursor = AgentCursor(
            agent_id="test-agent",
            display_name="Test Agent",
            state=CursorState.WORKING,
            activity="Processing...",
        )
        assert cursor.agent_id == "test-agent"
        assert cursor.display_name == "Test Agent"
        assert cursor.state == CursorState.WORKING
        assert cursor.activity == "Processing..."

    def test_cursor_delegates_emoji(self):
        """Cursor emoji comes from state."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.SUGGESTING,
            activity="Has idea",
        )
        assert cursor.emoji == CursorState.SUGGESTING.emoji

    def test_cursor_delegates_color(self):
        """Cursor color comes from state."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.EXPLORING,
            activity="Looking around",
        )
        assert cursor.color == CursorState.EXPLORING.color

    def test_effective_animation_speed(self):
        """Animation speed is modulated by circadian phase."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="...",
        )
        # Speed should be base * tempo_modifier
        base_speed = CursorState.WORKING.animation_speed
        tempo = CircadianPhase.current().tempo_modifier
        expected = base_speed * tempo
        assert cursor.effective_animation_speed == expected

    def test_transition_to_valid(self):
        """Valid transition changes state."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WAITING,
            activity="...",
        )
        assert cursor.transition_to(CursorState.WORKING) is True
        assert cursor.state == CursorState.WORKING

    def test_transition_to_invalid(self):
        """Invalid transition is rejected."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WAITING,
            activity="...",
        )
        # WAITING cannot directly go to SUGGESTING
        assert cursor.transition_to(CursorState.SUGGESTING) is False
        assert cursor.state == CursorState.WAITING  # Unchanged

    def test_update_activity(self):
        """Activity update works."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="Old activity",
        )
        old_time = cursor.last_update
        cursor.update_activity("New activity", focus_path="self.memory")
        assert cursor.activity == "New activity"
        assert cursor.focus_path == "self.memory"
        assert cursor.last_update >= old_time

    def test_to_cli_basic(self):
        """CLI rendering works."""
        cursor = AgentCursor(
            agent_id="k-gent",
            display_name="K-gent",
            state=CursorState.FOLLOWING,
            activity="watching",
        )
        cli = cursor.to_cli()
        assert "👁️" in cli
        assert "K-gent" in cli
        assert "watching" in cli

    def test_to_cli_with_focus_path(self):
        """CLI includes focus path."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="reading",
            focus_path="self.memory.manifest",
        )
        cli = cursor.to_cli()
        assert "[self.memory.manifest]" in cli

    def test_to_cli_teaching_mode(self):
        """Teaching mode shows transitions."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="...",
        )
        cli = cursor.to_cli(teaching_mode=True)
        assert "State: WORKING" in cli
        assert "can transition to:" in cli

    def test_to_dict_roundtrip(self):
        """Serialization/deserialization roundtrip."""
        original = AgentCursor(
            agent_id="test",
            display_name="Test Agent",
            state=CursorState.EXPLORING,
            activity="Looking",
            focus_path="world.file",
            metadata={"key": "value"},
        )
        data = original.to_dict()
        restored = AgentCursor.from_dict(data)

        assert restored.agent_id == original.agent_id
        assert restored.display_name == original.display_name
        assert restored.state == original.state
        assert restored.activity == original.activity
        assert restored.focus_path == original.focus_path
        assert restored.metadata == original.metadata


# =============================================================================
# Type I: Unit Tests - PresenceUpdate
# =============================================================================


class TestPresenceUpdate:
    """Test PresenceUpdate event."""

    def test_create_update(self):
        """Basic update creation."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="...",
        )
        update = PresenceUpdate(
            event_type=PresenceEventType.CURSOR_JOINED,
            agent_id="x",
            cursor=cursor,
        )
        assert update.event_type == PresenceEventType.CURSOR_JOINED
        assert update.cursor == cursor

    def test_update_to_dict(self):
        """Update serialization."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=CursorState.WORKING,
            activity="...",
        )
        update = PresenceUpdate(
            event_type=PresenceEventType.STATE_CHANGED,
            agent_id="x",
            cursor=cursor,
            old_state=CursorState.WAITING,
            new_state=CursorState.WORKING,
        )
        data = update.to_dict()

        assert data["event_type"] == "state_changed"
        assert data["agent_id"] == "x"
        assert data["old_state"] == "WAITING"
        assert data["new_state"] == "WORKING"
        assert data["cursor"] is not None


# =============================================================================
# Type II: Integration Tests - PresenceChannel
# =============================================================================


class TestPresenceChannel:
    """Integration tests for PresenceChannel."""

    @pytest.fixture
    def channel(self):
        """Create fresh channel for each test."""
        reset_presence_channel()
        return PresenceChannel()

    @pytest.fixture
    def sample_cursor(self):
        """Sample cursor for testing."""
        return AgentCursor(
            agent_id="test-agent",
            display_name="Test Agent",
            state=CursorState.WORKING,
            activity="Testing",
        )

    @pytest.mark.asyncio
    async def test_join_adds_cursor(self, channel, sample_cursor):
        """Join adds cursor to active list."""
        await channel.join(sample_cursor)
        assert len(channel.active_cursors) == 1
        assert channel.get_cursor("test-agent") == sample_cursor

    @pytest.mark.asyncio
    async def test_leave_removes_cursor(self, channel, sample_cursor):
        """Leave removes cursor from active list."""
        await channel.join(sample_cursor)
        result = await channel.leave("test-agent")
        assert result is True
        assert len(channel.active_cursors) == 0
        assert channel.get_cursor("test-agent") is None

    @pytest.mark.asyncio
    async def test_leave_nonexistent_returns_false(self, channel):
        """Leave returns False for unknown agent."""
        result = await channel.leave("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_broadcast_updates_cursor(self, channel, sample_cursor):
        """Broadcast updates cursor state."""
        await channel.join(sample_cursor)

        updated = AgentCursor(
            agent_id="test-agent",
            display_name="Test Agent",
            state=CursorState.SUGGESTING,
            activity="Has suggestion",
        )
        await channel.broadcast(updated)

        stored = channel.get_cursor("test-agent")
        assert stored is not None
        assert stored.state == CursorState.SUGGESTING
        assert stored.activity == "Has suggestion"

    @pytest.mark.asyncio
    async def test_subscribe_receives_updates(self, channel, sample_cursor):
        """Subscriber receives updates."""
        received: list[PresenceUpdate] = []

        async def subscriber():
            async for update in channel.subscribe():
                received.append(update)
                if len(received) >= 2:
                    break

        # Start subscriber in background
        task = asyncio.create_task(subscriber())

        # Give subscriber time to start
        await asyncio.sleep(0.01)

        # Broadcast events
        await channel.join(sample_cursor)

        updated = AgentCursor(
            agent_id="test-agent",
            display_name="Test Agent",
            state=CursorState.SUGGESTING,
            activity="Changed",
        )
        await channel.broadcast(updated)

        # Wait for subscriber
        await asyncio.wait_for(task, timeout=1.0)

        assert len(received) == 2
        assert received[0].event_type == PresenceEventType.CURSOR_JOINED
        assert received[1].event_type == PresenceEventType.STATE_CHANGED

    @pytest.mark.asyncio
    async def test_broadcast_returns_subscriber_count(self, channel, sample_cursor):
        """Broadcast returns number of notified subscribers."""
        # No subscribers initially
        count = await channel.broadcast(sample_cursor)
        assert count == 0

        # Add a subscriber
        async def sub():
            async for _ in channel.subscribe():
                break

        task = asyncio.create_task(sub())
        await asyncio.sleep(0.01)

        count = await channel.broadcast(sample_cursor)
        assert count == 1

        # Clean up
        await channel.leave(sample_cursor.agent_id)
        await asyncio.wait_for(task, timeout=1.0)

    @pytest.mark.asyncio
    async def test_get_presence_snapshot(self, channel):
        """Snapshot returns current state."""
        cursor1 = AgentCursor(
            agent_id="agent-1",
            display_name="Agent 1",
            state=CursorState.WORKING,
            activity="...",
        )
        cursor2 = AgentCursor(
            agent_id="agent-2",
            display_name="Agent 2",
            state=CursorState.FOLLOWING,
            activity="...",
        )

        await channel.join(cursor1)
        await channel.join(cursor2)

        snapshot = await channel.get_presence_snapshot()

        assert snapshot["count"] == 2
        assert len(snapshot["cursors"]) == 2
        assert "phase" in snapshot
        assert "tempo_modifier" in snapshot


# =============================================================================
# Type II: Integration Tests - Singleton
# =============================================================================


class TestPresenceChannelSingleton:
    """Test singleton management."""

    def test_get_presence_channel_singleton(self):
        """get_presence_channel returns same instance."""
        reset_presence_channel()
        channel1 = get_presence_channel()
        channel2 = get_presence_channel()
        assert channel1 is channel2

    def test_reset_presence_channel(self):
        """reset_presence_channel creates new instance."""
        channel1 = get_presence_channel()
        reset_presence_channel()
        channel2 = get_presence_channel()
        assert channel1 is not channel2


# =============================================================================
# Type II: Integration Tests - CLI Footer
# =============================================================================


class TestPresenceFooter:
    """Test CLI presence footer rendering."""

    def test_empty_cursors_returns_empty(self):
        """No cursors = no footer."""
        result = render_presence_footer([])
        assert result == ""

    def test_single_cursor(self):
        """Single cursor renders correctly."""
        cursor = AgentCursor(
            agent_id="k",
            display_name="K-gent",
            state=CursorState.WORKING,
            activity="thinking",
        )
        result = render_presence_footer([cursor])

        assert "Active Agents" in result
        assert "K-gent" in result
        assert "thinking" in result
        assert "⚡" in result  # WORKING emoji

    def test_multiple_cursors(self):
        """Multiple cursors all render."""
        cursors = [
            AgentCursor(
                agent_id="a",
                display_name="Agent A",
                state=CursorState.FOLLOWING,
                activity="watching",
            ),
            AgentCursor(
                agent_id="b",
                display_name="Agent B",
                state=CursorState.EXPLORING,
                activity="exploring",
            ),
        ]
        result = render_presence_footer(cursors)

        assert "Agent A" in result
        assert "Agent B" in result
        assert "watching" in result
        assert "exploring" in result

    def test_teaching_mode(self):
        """Teaching mode adds state info."""
        cursor = AgentCursor(
            agent_id="k",
            display_name="K",
            state=CursorState.SUGGESTING,
            activity="...",
        )
        result = render_presence_footer([cursor], teaching_mode=True)

        assert "State: SUGGESTING" in result
        assert "can transition to:" in result


# =============================================================================
# Type III: Property-Based Tests
# =============================================================================


class TestCursorStateProperties_Hypothesis:
    """Property-based tests for CursorState."""

    @given(st.sampled_from(list(CursorState)))
    def test_all_transitions_are_valid_states(self, state: CursorState):
        """All transitions point to valid CursorState values."""
        for target in state.can_transition_to:
            assert isinstance(target, CursorState)

    @given(st.sampled_from(list(CursorState)))
    def test_animation_speed_is_float(self, state: CursorState):
        """Animation speed is always a float."""
        assert isinstance(state.animation_speed, float)

    @given(st.sampled_from(list(CursorState)))
    @settings(max_examples=50)
    def test_state_is_reachable_from_waiting(self, target: CursorState):
        """Every state is reachable from WAITING (within 2 steps)."""
        if target == CursorState.WAITING:
            return  # WAITING is starting point

        # Direct from WAITING?
        if target in CursorState.WAITING.can_transition_to:
            return

        # Two hops from WAITING?
        for intermediate in CursorState.WAITING.can_transition_to:
            if target in intermediate.can_transition_to:
                return

        # All states should be reachable within 2 hops
        # SUGGESTING is reachable via WORKING or FOLLOWING
        assert target in (
            CursorState.WAITING.can_transition_to
            | CursorState.WORKING.can_transition_to
            | CursorState.FOLLOWING.can_transition_to
            | CursorState.EXPLORING.can_transition_to
        )


class TestCircadianPhaseProperties_Hypothesis:
    """Property-based tests for CircadianPhase."""

    @given(st.integers(min_value=0, max_value=23))
    def test_all_hours_map_to_phase(self, hour: int):
        """Every hour (0-23) maps to exactly one phase."""
        phase = CircadianPhase.from_hour(hour)
        assert isinstance(phase, CircadianPhase)

    @given(st.sampled_from(list(CircadianPhase)))
    def test_tempo_warmth_complementary(self, phase: CircadianPhase):
        """Tempo and warmth shouldn't both be extreme simultaneously."""
        # This is a design heuristic: very fast + very warm would be chaotic
        tempo = phase.tempo_modifier
        warmth = phase.warmth
        # Not a hard rule, but verify reasonable bounds
        assert tempo + warmth <= 2.0  # Sum can't exceed 2


class TestAgentCursorProperties_Hypothesis:
    """Property-based tests for AgentCursor."""

    @given(
        st.text(min_size=1, max_size=50),
        st.text(min_size=1, max_size=50),
        st.sampled_from(list(CursorState)),
        st.text(min_size=1, max_size=100),
    )
    def test_cursor_serialization_roundtrip(
        self,
        agent_id: str,
        display_name: str,
        state: CursorState,
        activity: str,
    ):
        """Any cursor can be serialized and deserialized."""
        cursor = AgentCursor(
            agent_id=agent_id,
            display_name=display_name,
            state=state,
            activity=activity,
        )
        data = cursor.to_dict()
        restored = AgentCursor.from_dict(data)

        assert restored.agent_id == cursor.agent_id
        assert restored.state == cursor.state

    @given(st.sampled_from(list(CursorState)), st.sampled_from(list(CursorState)))
    def test_transition_is_deterministic(self, start: CursorState, target: CursorState):
        """Transition result is deterministic."""
        cursor = AgentCursor(
            agent_id="x",
            display_name="X",
            state=start,
            activity="...",
        )
        result1 = cursor.state.can_transition(target)

        cursor2 = AgentCursor(
            agent_id="y",
            display_name="Y",
            state=start,
            activity="...",
        )
        result2 = cursor2.state.can_transition(target)

        assert result1 == result2  # Same state, same transition logic
