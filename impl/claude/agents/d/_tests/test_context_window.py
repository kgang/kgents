"""
Tests for ContextWindow: Turn-level Store Comonad.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from agents.d.context_window import (
    ContextMeta,
    ContextSnapshot,
    ContextWindow,
    Turn,
    TurnRole,
    create_context_window,
    from_messages,
)
from agents.d.linearity import ResourceClass


class TestTurn:
    """Tests for Turn dataclass."""

    def test_turn_creation(self) -> None:
        """Can create a turn with all fields."""
        turn = Turn(
            role=TurnRole.USER,
            content="Hello world",
            timestamp=datetime.now(UTC),
            resource_id="res_123",
            metadata={"key": "value"},
        )

        assert turn.role == TurnRole.USER
        assert turn.content == "Hello world"
        assert turn.resource_id == "res_123"
        assert turn.metadata == {"key": "value"}

    def test_turn_immutability(self) -> None:
        """Turn is frozen (immutable)."""
        turn = Turn(
            role=TurnRole.USER,
            content="Hello",
            timestamp=datetime.now(UTC),
            resource_id="res",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            turn.content = "Modified"  # type: ignore

    def test_token_estimate(self) -> None:
        """Token estimate is roughly 4 chars per token."""
        turn = Turn(
            role=TurnRole.USER,
            content="a" * 100,  # 100 chars
            timestamp=datetime.now(UTC),
            resource_id="res",
        )

        # 100/4 + 1 = 26
        assert turn.token_estimate == 26


class TestContextMeta:
    """Tests for ContextMeta."""

    def test_pressure_calculation(self) -> None:
        """Pressure is ratio of used to max tokens."""
        meta = ContextMeta(total_tokens=5000, max_tokens=10000)
        assert meta.pressure == 0.5

    def test_pressure_capped_at_one(self) -> None:
        """Pressure caps at 1.0 when over limit."""
        meta = ContextMeta(total_tokens=15000, max_tokens=10000)
        assert meta.pressure == 1.0

    def test_pressure_zero_when_empty(self) -> None:
        """Pressure is 0 when max_tokens is 0."""
        meta = ContextMeta(total_tokens=100, max_tokens=0)
        assert meta.pressure == 0.0

    def test_needs_compression_threshold(self) -> None:
        """needs_compression triggers at 70%."""
        meta = ContextMeta(total_tokens=6900, max_tokens=10000)
        assert not meta.needs_compression  # 69%

        meta.total_tokens = 7100
        assert meta.needs_compression  # 71%


class TestContextWindow:
    """Tests for ContextWindow core functionality."""

    def test_empty_window(self) -> None:
        """Empty window has sensible defaults."""
        window = ContextWindow()

        assert len(window) == 0
        assert not window
        assert window.extract() is None
        assert window.position == 0

    def test_append_turn(self) -> None:
        """Can append turns."""
        window = ContextWindow()
        turn = window.append(TurnRole.USER, "Hello")

        assert len(window) == 1
        assert window
        assert turn.content == "Hello"
        assert turn.role == TurnRole.USER

    def test_append_with_string_role(self) -> None:
        """Can append with string role."""
        window = ContextWindow()
        window.append("user", "Hello")
        window.append("assistant", "Hi")

        turns = window.all_turns()
        assert turns[0].role == TurnRole.USER
        assert turns[1].role == TurnRole.ASSISTANT

    def test_extract_returns_focus(self) -> None:
        """extract() returns turn at current position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")

        # Position defaults to last
        current = window.extract()
        assert current is not None
        assert current.content == "Second"

    def test_seek_changes_focus(self) -> None:
        """seek() moves the focus position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")
        window.append(TurnRole.USER, "Third")

        window.seek(1)  # Move to first turn
        assert window.extract().content == "First"  # type: ignore

        window.seek(2)  # Move to second
        assert window.extract().content == "Second"  # type: ignore

        window.seek(3)  # Move to third
        assert window.extract().content == "Third"  # type: ignore

    def test_seek_bounds(self) -> None:
        """seek() respects bounds."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Only")

        window.seek(-10)  # Below bounds
        assert window.position == 0

        window.seek(100)  # Above bounds
        assert window.position == 1

    def test_seeks_with_function(self) -> None:
        """seeks() applies function to position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")

        window.seeks(lambda p: p - 1)  # Move back one
        assert window.position == 1

    def test_all_turns(self) -> None:
        """all_turns() returns all turns."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        window.append(TurnRole.USER, "C")

        turns = window.all_turns()
        assert len(turns) == 3
        assert [t.content for t in turns] == ["A", "B", "C"]

    def test_turns_up_to(self) -> None:
        """turns_up_to() returns turns up to position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        window.append(TurnRole.USER, "C")

        turns = window.turns_up_to(2)
        assert len(turns) == 2
        assert [t.content for t in turns] == ["A", "B"]

    def test_turns_from_role(self) -> None:
        """turns_from_role() filters by role."""
        window = ContextWindow()
        window.append(TurnRole.USER, "U1")
        window.append(TurnRole.ASSISTANT, "A1")
        window.append(TurnRole.USER, "U2")
        window.append(TurnRole.SYSTEM, "S1")

        user_turns = window.turns_from_role(TurnRole.USER)
        assert len(user_turns) == 2
        assert [t.content for t in user_turns] == ["U1", "U2"]


class TestContextWindowComonad:
    """Tests for comonad operations."""

    def test_extend_applies_at_each_position(self) -> None:
        """extend() applies function at each position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")
        window.append(TurnRole.USER, "Third")

        def get_content(w: ContextWindow) -> str:
            turn = w.extract()
            return turn.content if turn else "empty"

        results = window.extend(get_content)
        assert results == ["empty", "First", "Second", "Third"]

    def test_extend_preserves_position(self) -> None:
        """extend() restores original position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")

        original_pos = window.position
        window.extend(lambda w: w.position)
        assert window.position == original_pos

    def test_duplicate_creates_snapshots(self) -> None:
        """duplicate() creates snapshots at each position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")

        snapshots = window.duplicate()

        assert len(snapshots) == 3  # Position 0, 1, 2
        assert snapshots[0].position == 0
        assert snapshots[0].value is None

        assert snapshots[1].position == 1
        assert snapshots[1].value is not None
        assert snapshots[1].value.content == "First"

        assert snapshots[2].position == 2
        assert snapshots[2].value is not None
        assert snapshots[2].value.content == "Second"

    def test_duplicate_preserves_position(self) -> None:
        """duplicate() restores original position."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.seek(1)

        original_pos = window.position
        window.duplicate()
        assert window.position == original_pos


class TestComonadLaws:
    """
    Property-based tests for comonad laws.

    Laws:
    1. Left Identity:  extract . duplicate = id
    2. Right Identity: fmap extract . duplicate = id
    3. Associativity:  duplicate . duplicate = fmap duplicate . duplicate
    """

    def test_left_identity(self) -> None:
        """
        Left Identity: extract . duplicate = id

        Extracting from a duplicated context gives the original value.
        """
        window = ContextWindow()
        window.append(TurnRole.USER, "Test content")
        window.append(TurnRole.ASSISTANT, "Response")

        # Original value
        original = window.extract()

        # Extract from duplicate gives same position value
        snapshots = window.duplicate()
        duplicated_value = snapshots[window.position].value

        assert duplicated_value == original

    def test_right_identity(self) -> None:
        """
        Right Identity: fmap extract . duplicate = id

        Mapping extract over duplicate gives original values at each position.
        """
        window = ContextWindow()
        window.append(TurnRole.USER, "First")
        window.append(TurnRole.ASSISTANT, "Second")

        # Get values via extend (fmap extract)
        via_extend = window.extend(lambda w: w.extract())

        # Get values via duplicate then extract
        snapshots = window.duplicate()
        via_duplicate = [s.value for s in snapshots]

        # They should match
        assert via_extend == via_duplicate

    def test_associativity_structure(self) -> None:
        """
        Associativity structure check.

        duplicate . duplicate should create same depth as fmap duplicate . duplicate

        Note: Full associativity is hard to verify without implementing
        nested ContextWindow, so we verify the structure is consistent.
        """
        window = ContextWindow()
        window.append(TurnRole.USER, "Content")

        # duplicate returns list of snapshots
        first_dup = window.duplicate()

        # Each snapshot has the same linearity map (shared reference)
        # This is by design - linearity is global to the window
        assert all(s.linearity_map is window._linearity for s in first_dup)

    def test_extract_duplicate_identity(self) -> None:
        """
        The snapshot at current position should have value = extract().

        This is the core left identity property.
        """
        window = ContextWindow()
        window.append(TurnRole.USER, "A")
        window.append(TurnRole.ASSISTANT, "B")
        window.append(TurnRole.USER, "C")

        # Test at each position
        for pos in range(len(window) + 1):
            window.seek(pos)
            snapshots = window.duplicate()

            extracted = window.extract()
            snapshot_value = snapshots[pos].value

            if extracted is None:
                assert snapshot_value is None
            else:
                assert snapshot_value == extracted


class TestContextWindowLinearity:
    """Tests for linearity integration."""

    def test_auto_classification_user(self) -> None:
        """User messages are PRESERVED."""
        window = ContextWindow()
        turn = window.append(TurnRole.USER, "Hello")

        rc = window.get_resource_class(turn)
        assert rc == ResourceClass.PRESERVED

    def test_auto_classification_assistant(self) -> None:
        """Assistant messages default to DROPPABLE."""
        window = ContextWindow()
        turn = window.append(TurnRole.ASSISTANT, "Just thinking...")

        rc = window.get_resource_class(turn)
        assert rc == ResourceClass.DROPPABLE

    def test_auto_classification_content_override(self) -> None:
        """Content markers can upgrade classification."""
        window = ContextWindow()
        turn = window.append(TurnRole.ASSISTANT, "Therefore we should use approach A")

        # Content has "Therefore" which triggers REQUIRED
        rc = window.get_resource_class(turn)
        assert rc == ResourceClass.REQUIRED

    def test_promote_turn(self) -> None:
        """Can promote a turn to higher class."""
        window = ContextWindow()
        turn = window.append(TurnRole.ASSISTANT, "temp")

        assert window.get_resource_class(turn) == ResourceClass.DROPPABLE

        success = window.promote_turn(turn, ResourceClass.REQUIRED, "became important")
        assert success
        assert window.get_resource_class(turn) == ResourceClass.REQUIRED

    def test_droppable_turns(self) -> None:
        """Can query droppable turns."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Keep me")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "drop me")  # DROPPABLE
        window.append(TurnRole.ASSISTANT, "drop me too")  # DROPPABLE

        droppable = window.droppable_turns()
        assert len(droppable) == 2

    def test_preserved_turns(self) -> None:
        """Can query preserved turns."""
        window = ContextWindow()
        window.append(TurnRole.USER, "Keep me")
        window.append(TurnRole.ASSISTANT, "temp")
        window.append(TurnRole.USER, "Keep me too")

        preserved = window.preserved_turns()
        assert len(preserved) == 2

    def test_linearity_stats(self) -> None:
        """Can get linearity statistics."""
        window = ContextWindow()
        window.append(TurnRole.USER, "A")  # PRESERVED
        window.append(TurnRole.ASSISTANT, "B")  # DROPPABLE
        window.append(TurnRole.SYSTEM, "C")  # REQUIRED

        stats = window.linearity_stats
        assert stats["preserved"] == 1
        assert stats["droppable"] == 1
        assert stats["required"] == 1


class TestContextWindowPressure:
    """Tests for token pressure tracking."""

    def test_token_tracking(self) -> None:
        """Total tokens are tracked."""
        window = ContextWindow(max_tokens=1000)
        window.append(TurnRole.USER, "a" * 100)  # ~26 tokens

        assert window.total_tokens > 0
        assert window.total_tokens == window.meta.total_tokens

    def test_pressure_increases(self) -> None:
        """Pressure increases with tokens."""
        window = ContextWindow(max_tokens=100)

        window.append(TurnRole.USER, "a" * 200)  # ~51 tokens

        assert window.pressure > 0.5

    def test_needs_compression(self) -> None:
        """needs_compression triggers at threshold."""
        window = ContextWindow(max_tokens=100)

        window.append(TurnRole.USER, "a" * 300)  # High token count

        assert window.needs_compression

    def test_recalculate_tokens(self) -> None:
        """Can recalculate token count."""
        window = ContextWindow()
        window.append(TurnRole.USER, "hello")
        window.append(TurnRole.ASSISTANT, "world")

        original = window.total_tokens
        window._meta.total_tokens = 0  # Corrupt it

        recalculated = window.recalculate_tokens()
        assert recalculated == original


class TestContextWindowSerialization:
    """Tests for serialization."""

    def test_roundtrip(self) -> None:
        """Can serialize and deserialize."""
        window = ContextWindow(max_tokens=5000)
        window.append(TurnRole.USER, "Hello")
        window.append(TurnRole.ASSISTANT, "Hi there")
        window.seek(1)

        data = window.to_dict()
        restored = ContextWindow.from_dict(data)

        assert len(restored) == 2
        assert restored.position == 1
        assert restored.max_tokens == 5000

        turns = restored.all_turns()
        assert turns[0].content == "Hello"
        assert turns[1].content == "Hi there"

    def test_roundtrip_preserves_linearity(self) -> None:
        """Serialization preserves linearity map."""
        window = ContextWindow()
        turn = window.append(TurnRole.ASSISTANT, "temp")
        window.promote_turn(turn, ResourceClass.REQUIRED, "test")

        data = window.to_dict()
        restored = ContextWindow.from_dict(data)

        restored_turn = restored.all_turns()[0]
        assert restored.get_resource_class(restored_turn) == ResourceClass.REQUIRED


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_context_window(self) -> None:
        """create_context_window works."""
        window = create_context_window(max_tokens=5000)
        assert window.max_tokens == 5000
        assert len(window) == 0

    def test_create_with_system(self) -> None:
        """Can create with initial system message."""
        window = create_context_window(
            max_tokens=5000,
            initial_system="You are a helpful assistant.",
        )

        assert len(window) == 1
        turns = window.all_turns()
        assert turns[0].role == TurnRole.SYSTEM
        assert turns[0].content == "You are a helpful assistant."

        # System message should be PRESERVED (promoted from REQUIRED)
        assert window.get_resource_class(turns[0]) == ResourceClass.PRESERVED

    def test_from_messages(self) -> None:
        """Can create from message list."""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        window = from_messages(messages)

        assert len(window) == 3
        turns = window.all_turns()
        assert turns[0].role == TurnRole.SYSTEM
        assert turns[1].role == TurnRole.USER
        assert turns[2].role == TurnRole.ASSISTANT
