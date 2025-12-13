"""
Tests for Turn - The Causal Event in Turn-gents Protocol.

Tests verify:
1. Turn creation and type hierarchy (Turn IS-A Event)
2. TurnType enum completeness
3. State hashing behavior
4. Confidence and entropy_cost bounds
5. YieldTurn approval flow
6. Turn-specific predicates (is_observable, is_blocking, etc.)
7. Serialization/deserialization compatibility
8. Integration with TheWeave (backwards compatibility)
"""

from __future__ import annotations

import pytest

from ..event import Event
from ..trace_monoid import TraceMonoid
from ..turn import Turn, TurnType, YieldTurn, _hash_state
from ..weave import TheWeave


class TestTurnType:
    """Tests for TurnType enum."""

    def test_five_turn_types_exist(self) -> None:
        """All five turn types are defined."""
        assert TurnType.SPEECH is not None
        assert TurnType.ACTION is not None
        assert TurnType.THOUGHT is not None
        assert TurnType.YIELD is not None
        assert TurnType.SILENCE is not None

    def test_exactly_five_types(self) -> None:
        """No more, no less—avoid taxonomy explosion."""
        assert len(TurnType) == 5

    def test_turn_types_are_distinct(self) -> None:
        """Each type has unique value."""
        values = [t.value for t in TurnType]
        assert len(values) == len(set(values))


class TestTurnCreation:
    """Tests for Turn creation and basic properties."""

    def test_create_turn_basic(self) -> None:
        """Create a basic turn with minimal args."""
        turn = Turn.create_turn(
            content="Hello",
            source="agent-a",
            turn_type=TurnType.SPEECH,
        )

        assert turn.content == "Hello"
        assert turn.source == "agent-a"
        assert turn.turn_type == TurnType.SPEECH
        assert turn.id is not None
        assert turn.timestamp > 0

    def test_create_turn_with_state(self) -> None:
        """Create a turn with state hashes."""
        turn = Turn.create_turn(
            content="Action",
            source="agent-b",
            turn_type=TurnType.ACTION,
            state_pre={"mode": "idle"},
            state_post={"mode": "active"},
        )

        assert turn.state_hash_pre != "empty"
        assert turn.state_hash_post != "empty"
        assert turn.state_hash_pre != turn.state_hash_post

    def test_create_turn_with_confidence(self) -> None:
        """Confidence is stored and clamped."""
        turn = Turn.create_turn(
            content="Maybe",
            source="agent-c",
            turn_type=TurnType.THOUGHT,
            confidence=0.75,
        )
        assert turn.confidence == 0.75

    def test_confidence_clamped_high(self) -> None:
        """Confidence > 1.0 is clamped to 1.0."""
        turn = Turn.create_turn(
            content="Overconfident",
            source="agent-c",
            turn_type=TurnType.SPEECH,
            confidence=1.5,
        )
        assert turn.confidence == 1.0

    def test_confidence_clamped_low(self) -> None:
        """Confidence < 0.0 is clamped to 0.0."""
        turn = Turn.create_turn(
            content="Underconfident",
            source="agent-c",
            turn_type=TurnType.SPEECH,
            confidence=-0.5,
        )
        assert turn.confidence == 0.0

    def test_entropy_cost_nonnegative(self) -> None:
        """Entropy cost cannot be negative."""
        turn = Turn.create_turn(
            content="Free lunch?",
            source="agent-d",
            turn_type=TurnType.SILENCE,
            entropy_cost=-1.0,
        )
        assert turn.entropy_cost == 0.0

    def test_create_turn_with_custom_id(self) -> None:
        """Custom turn ID is preserved."""
        turn = Turn.create_turn(
            content="Custom",
            source="agent-e",
            turn_type=TurnType.SPEECH,
            turn_id="custom-id-123",
        )
        assert turn.id == "custom-id-123"


class TestTurnIsEvent:
    """Tests that Turn IS-A Event (type hierarchy)."""

    def test_turn_isinstance_event(self) -> None:
        """Turn is an instance of Event."""
        turn = Turn.create_turn(
            content="Test",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        assert isinstance(turn, Event)

    def test_turn_has_event_fields(self) -> None:
        """Turn has all Event fields."""
        turn = Turn.create_turn(
            content="Test",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        # Event fields
        assert hasattr(turn, "id")
        assert hasattr(turn, "content")
        assert hasattr(turn, "timestamp")
        assert hasattr(turn, "source")

    def test_turn_is_frozen(self) -> None:
        """Turn is immutable (frozen dataclass)."""
        turn = Turn.create_turn(
            content="Immutable",
            source="agent",
            turn_type=TurnType.SPEECH,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            turn.content = "Mutated"  # type: ignore

    def test_turn_is_hashable(self) -> None:
        """Turn can be used in sets."""
        turn1 = Turn.create_turn(
            content="A",
            source="agent",
            turn_type=TurnType.SPEECH,
            turn_id="turn-1",
        )
        turn2 = Turn.create_turn(
            content="B",
            source="agent",
            turn_type=TurnType.ACTION,
            turn_id="turn-2",
        )

        turn_set = {turn1, turn2}
        assert len(turn_set) == 2


class TestTurnFromEvent:
    """Tests for lifting Events to Turns."""

    def test_from_event_preserves_fields(self) -> None:
        """from_event preserves Event's core fields."""
        event = Event.create(
            content="Original",
            source="agent-x",
            event_id="event-123",
            timestamp=1000.0,
        )

        turn = Turn.from_event(event, TurnType.SPEECH)

        assert turn.id == "event-123"
        assert turn.content == "Original"
        assert turn.source == "agent-x"
        assert turn.timestamp == 1000.0
        assert turn.turn_type == TurnType.SPEECH

    def test_from_event_adds_turn_fields(self) -> None:
        """from_event adds Turn-specific fields."""
        event = Event.create(content="Data", source="agent")

        turn = Turn.from_event(
            event,
            TurnType.ACTION,
            state_pre={"x": 1},
            confidence=0.8,
            entropy_cost=0.1,
        )

        assert turn.state_hash_pre != "empty"
        assert turn.confidence == 0.8
        assert turn.entropy_cost == 0.1


class TestTurnPredicates:
    """Tests for Turn type predicates."""

    def test_speech_is_observable(self) -> None:
        """SPEECH turns are observable."""
        turn = Turn.create_turn("Hi", "a", TurnType.SPEECH)
        assert turn.is_observable() is True

    def test_thought_not_observable(self) -> None:
        """THOUGHT turns are NOT observable by default."""
        turn = Turn.create_turn("Thinking...", "a", TurnType.THOUGHT)
        assert turn.is_observable() is False

    def test_yield_is_blocking(self) -> None:
        """YIELD turns block until resolved."""
        turn = Turn.create_turn("Approve?", "a", TurnType.YIELD)
        assert turn.is_blocking() is True

    def test_non_yield_not_blocking(self) -> None:
        """Non-YIELD turns don't block."""
        for tt in [
            TurnType.SPEECH,
            TurnType.ACTION,
            TurnType.THOUGHT,
            TurnType.SILENCE,
        ]:
            turn = Turn.create_turn("X", "a", tt)
            assert turn.is_blocking() is False

    def test_action_is_effectful(self) -> None:
        """ACTION turns have side effects."""
        turn = Turn.create_turn("Do it", "a", TurnType.ACTION)
        assert turn.is_effectful() is True

    def test_speech_not_effectful(self) -> None:
        """SPEECH turns don't have side effects."""
        turn = Turn.create_turn("Say it", "a", TurnType.SPEECH)
        assert turn.is_effectful() is False

    def test_action_requires_governance(self) -> None:
        """ACTION turns require governance review."""
        turn = Turn.create_turn("Delete all", "a", TurnType.ACTION)
        assert turn.requires_governance() is True

    def test_yield_requires_governance(self) -> None:
        """YIELD turns require governance review."""
        turn = Turn.create_turn("May I?", "a", TurnType.YIELD)
        assert turn.requires_governance() is True

    def test_speech_no_governance(self) -> None:
        """SPEECH turns don't require governance."""
        turn = Turn.create_turn("Hello", "a", TurnType.SPEECH)
        assert turn.requires_governance() is False


class TestYieldTurn:
    """Tests for YieldTurn approval flow."""

    def test_create_yield_turn(self) -> None:
        """Create a YieldTurn requesting approval."""
        yield_turn = YieldTurn.create_yield(
            content="Delete user?",
            source="agent-delete",
            yield_reason="Destructive action",
            required_approvers={"k-gent", "human"},
        )

        assert yield_turn.turn_type == TurnType.YIELD
        assert yield_turn.yield_reason == "Destructive action"
        assert yield_turn.required_approvers == frozenset({"k-gent", "human"})
        assert yield_turn.approved_by == frozenset()

    def test_yield_not_approved_initially(self) -> None:
        """YieldTurn starts not approved."""
        yield_turn = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"approver"},
        )
        assert yield_turn.is_approved() is False

    def test_yield_approve_single(self) -> None:
        """Single approval works."""
        yield_turn = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"approver"},
        )

        approved = yield_turn.approve("approver")

        assert approved.is_approved() is True
        assert "approver" in approved.approved_by

    def test_yield_approve_multiple(self) -> None:
        """Multiple approvals required."""
        yield_turn = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"alice", "bob"},
        )

        # One approval not enough
        partial = yield_turn.approve("alice")
        assert partial.is_approved() is False
        assert partial.pending_approvers() == frozenset({"bob"})

        # Both approvals complete it
        complete = partial.approve("bob")
        assert complete.is_approved() is True
        assert complete.pending_approvers() == frozenset()

    def test_yield_approve_invalid_approver_raises(self) -> None:
        """Approving with non-required approver raises."""
        yield_turn = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"alice"},
        )

        with pytest.raises(ValueError, match="not in required_approvers"):
            yield_turn.approve("eve")

    def test_yield_is_immutable(self) -> None:
        """approve() returns new instance (immutable)."""
        original = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"alice"},
        )

        approved = original.approve("alice")

        # Original unchanged
        assert original.is_approved() is False
        assert approved.is_approved() is True

    def test_yield_isinstance_turn(self) -> None:
        """YieldTurn is an instance of Turn."""
        yield_turn = YieldTurn.create_yield(
            content="X",
            source="a",
            yield_reason="Test",
            required_approvers={"alice"},
        )
        assert isinstance(yield_turn, Turn)
        assert isinstance(yield_turn, Event)


class TestStateHashing:
    """Tests for state hashing behavior."""

    def test_empty_state_hash(self) -> None:
        """None state produces 'empty' hash."""
        assert _hash_state(None) == "empty"

    def test_dict_state_hash(self) -> None:
        """Dict state produces hash."""
        h = _hash_state({"key": "value"})
        assert h != "empty"
        assert len(h) == 16  # Truncated SHA256

    def test_same_state_same_hash(self) -> None:
        """Same state produces same hash."""
        state = {"x": 1, "y": 2}
        h1 = _hash_state(state)
        h2 = _hash_state(state)
        assert h1 == h2

    def test_different_state_different_hash(self) -> None:
        """Different states produce different hashes."""
        h1 = _hash_state({"a": 1})
        h2 = _hash_state({"b": 2})
        assert h1 != h2

    def test_unhashable_state(self) -> None:
        """Unhashable state produces 'unhashable'."""

        class Unhashable:
            def __repr__(self) -> str:
                raise RuntimeError("Cannot repr")

        h = _hash_state(Unhashable())
        assert h == "unhashable"


class TestTurnWeaveIntegration:
    """Tests that Turn works with TheWeave unchanged."""

    @pytest.mark.asyncio
    async def test_turn_in_weave(self) -> None:
        """Turn can be recorded in TheWeave."""
        weave = TheWeave()

        turn = Turn.create_turn(
            content="Hello from Turn",
            source="agent-t",
            turn_type=TurnType.SPEECH,
        )

        # TheWeave.record() creates Event internally, but we can
        # work with the underlying monoid directly
        weave.monoid.append_mut(turn)

        assert len(weave) == 1
        assert turn.id in weave

    @pytest.mark.asyncio
    async def test_turn_in_trace_monoid(self) -> None:
        """Turn works with TraceMonoid operations."""
        monoid: TraceMonoid[str] = TraceMonoid()

        turn1 = Turn.create_turn(
            content="First",
            source="agent-1",
            turn_type=TurnType.SPEECH,
            turn_id="turn-1",
        )
        turn2 = Turn.create_turn(
            content="Second",
            source="agent-2",
            turn_type=TurnType.ACTION,
            turn_id="turn-2",
        )

        monoid.append_mut(turn1)
        monoid.append_mut(turn2, depends_on={"turn-1"})

        # Linearize works
        linear = monoid.linearize()
        assert len(linear) == 2
        assert linear[0].id == "turn-1"
        assert linear[1].id == "turn-2"

    @pytest.mark.asyncio
    async def test_turn_project(self) -> None:
        """Turn projection works via TraceMonoid.project()."""
        monoid: TraceMonoid[str] = TraceMonoid()

        turn_a = Turn.create_turn("A", "agent-a", TurnType.SPEECH, turn_id="a")
        turn_b = Turn.create_turn("B", "agent-b", TurnType.ACTION, turn_id="b")

        monoid.append_mut(turn_a)
        monoid.append_mut(turn_b)

        # Project to agent-a sees only their turn
        projection = monoid.project("agent-a")
        assert len(projection) == 1
        assert projection[0].id == "a"

    @pytest.mark.asyncio
    async def test_turn_dependency_graph(self) -> None:
        """Turn dependencies tracked in braid()."""
        monoid: TraceMonoid[str] = TraceMonoid()

        t1 = Turn.create_turn("1", "a", TurnType.SPEECH, turn_id="t1")
        t2 = Turn.create_turn("2", "b", TurnType.ACTION, turn_id="t2")
        t3 = Turn.create_turn("3", "a", TurnType.THOUGHT, turn_id="t3")

        monoid.append_mut(t1)
        monoid.append_mut(t2)
        monoid.append_mut(t3, depends_on={"t1", "t2"})

        braid = monoid.braid()

        # t3 depends on t1 and t2
        deps = braid.get_dependencies("t3")
        assert deps == {"t1", "t2"}

        # t1 and t2 are concurrent (no deps between them)
        assert braid.are_concurrent("t1", "t2")

    @pytest.mark.asyncio
    async def test_turn_knot(self) -> None:
        """Knot synchronization works with Turns."""
        monoid: TraceMonoid[str] = TraceMonoid()

        t1 = Turn.create_turn("1", "agent-a", TurnType.SPEECH, turn_id="t1")
        t2 = Turn.create_turn("2", "agent-b", TurnType.SPEECH, turn_id="t2")

        monoid.append_mut(t1)
        monoid.append_mut(t2)

        # Create knot at t1 and t2
        knot = monoid.knot({"t1", "t2"})

        assert knot.source == "weave"
        assert knot.id.startswith("knot-")


class TestTurnGenericContent:
    """Tests that Turn[T] works with various content types."""

    def test_turn_string_content(self) -> None:
        """Turn with string content."""
        turn: Turn[str] = Turn.create_turn("text", "a", TurnType.SPEECH)
        assert turn.content == "text"

    def test_turn_dict_content(self) -> None:
        """Turn with dict content."""
        data = {"action": "click", "target": "button"}
        turn: Turn[dict[str, str]] = Turn.create_turn(data, "a", TurnType.ACTION)
        assert turn.content == data

    def test_turn_int_content(self) -> None:
        """Turn with int content."""
        turn: Turn[int] = Turn.create_turn(42, "a", TurnType.THOUGHT)
        assert turn.content == 42

    def test_turn_none_content(self) -> None:
        """Turn with None content (like SILENCE)."""
        turn: Turn[None] = Turn.create_turn(None, "a", TurnType.SILENCE)
        assert turn.content is None
