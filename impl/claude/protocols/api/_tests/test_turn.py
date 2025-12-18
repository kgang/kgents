"""Tests for Turn dataclass and projectors."""

from __future__ import annotations

import json

import pytest

from protocols.api.turn import Turn, turns_to_json, turns_to_markdown


class TestTurnBasics:
    """Basic Turn tests."""

    def test_turn_is_frozen(self) -> None:
        """Turn is immutable."""
        turn = Turn(speaker="user", content="Hello", timestamp=1.0)
        with pytest.raises(Exception):  # FrozenInstanceError
            turn.speaker = "other"  # type: ignore[misc]

    def test_turn_stores_speaker(self) -> None:
        """Turn stores speaker correctly."""
        turn = Turn(speaker="kgent", content="Hi", timestamp=0.0)
        assert turn.speaker == "kgent"

    def test_turn_stores_content(self) -> None:
        """Turn stores content correctly."""
        turn = Turn(speaker="user", content="Hello world!", timestamp=0.0)
        assert turn.content == "Hello world!"

    def test_turn_stores_timestamp(self) -> None:
        """Turn stores timestamp correctly."""
        turn = Turn(speaker="user", content="Hi", timestamp=1734200000.0)
        assert turn.timestamp == 1734200000.0

    def test_turn_default_meta(self) -> None:
        """Turn has empty dict as default meta."""
        turn = Turn(speaker="user", content="Hi", timestamp=0.0)
        assert turn.meta == {}

    def test_turn_custom_meta(self) -> None:
        """Turn accepts custom metadata."""
        turn = Turn(
            speaker="assistant",
            content="Response",
            timestamp=0.0,
            meta={"confidence": 0.9, "model": "gpt-4"},
        )
        assert turn.meta["confidence"] == 0.9
        assert turn.meta["model"] == "gpt-4"


class TestTurnProjectors:
    """Tests for Turn projection methods."""

    @pytest.fixture
    def sample_turn(self) -> Turn:
        """Create a sample turn for testing."""
        return Turn(
            speaker="kgent",
            content="Hello! How can I help?",
            timestamp=1734200000.0,
            meta={"session_id": "abc123"},
        )

    def test_to_cli_format(self, sample_turn: Turn) -> None:
        """to_cli produces [speaker]: content format."""
        result = sample_turn.to_cli()
        assert result == "[kgent]: Hello! How can I help?"

    def test_to_cli_preserves_content(self, sample_turn: Turn) -> None:
        """CLI output contains full content."""
        assert "Hello! How can I help?" in sample_turn.to_cli()

    def test_to_json_returns_dict(self, sample_turn: Turn) -> None:
        """to_json returns a dictionary."""
        result = sample_turn.to_json()
        assert isinstance(result, dict)

    def test_to_json_has_all_fields(self, sample_turn: Turn) -> None:
        """JSON output has all Turn fields."""
        result = sample_turn.to_json()
        assert result["speaker"] == "kgent"
        assert result["content"] == "Hello! How can I help?"
        assert result["timestamp"] == 1734200000.0
        assert result["meta"]["session_id"] == "abc123"

    def test_to_json_str_is_valid_json(self, sample_turn: Turn) -> None:
        """to_json_str produces valid JSON string."""
        result = sample_turn.to_json_str()
        parsed = json.loads(result)
        assert parsed["speaker"] == "kgent"

    def test_to_marimo_returns_html(self, sample_turn: Turn) -> None:
        """to_marimo returns HTML string."""
        result = sample_turn.to_marimo()
        assert "<div" in result
        assert "kgent" in result
        assert "Hello! How can I help?" in result

    def test_to_marimo_has_styling(self, sample_turn: Turn) -> None:
        """marimo output has inline styles."""
        result = sample_turn.to_marimo()
        assert "style=" in result
        assert "background:" in result

    def test_to_sse_format(self, sample_turn: Turn) -> None:
        """to_sse produces SSE-formatted string."""
        result = sample_turn.to_sse()
        assert result.startswith("data: ")
        assert result.endswith("\n\n")

    def test_to_sse_contains_json(self, sample_turn: Turn) -> None:
        """SSE data field contains valid JSON."""
        result = sample_turn.to_sse()
        json_part = result[6:-2]  # Strip "data: " and "\n\n"
        parsed = json.loads(json_part)
        assert parsed["speaker"] == "kgent"


class TestTurnWithMeta:
    """Tests for Turn.with_meta() immutable update."""

    def test_with_meta_returns_new_turn(self) -> None:
        """with_meta returns a new Turn, not modified original."""
        original = Turn(speaker="user", content="Hi", timestamp=0.0)
        updated = original.with_meta(edited=True)

        assert updated is not original
        assert original.meta == {}
        assert updated.meta["edited"] is True

    def test_with_meta_preserves_original_fields(self) -> None:
        """with_meta preserves speaker, content, timestamp."""
        original = Turn(speaker="user", content="Hello", timestamp=123.0)
        updated = original.with_meta(flag=True)

        assert updated.speaker == "user"
        assert updated.content == "Hello"
        assert updated.timestamp == 123.0

    def test_with_meta_merges_existing_meta(self) -> None:
        """with_meta merges with existing metadata."""
        original = Turn(
            speaker="user",
            content="Hi",
            timestamp=0.0,
            meta={"key1": "value1"},
        )
        updated = original.with_meta(key2="value2")

        assert updated.meta["key1"] == "value1"
        assert updated.meta["key2"] == "value2"

    def test_with_meta_can_override(self) -> None:
        """with_meta can override existing meta values."""
        original = Turn(
            speaker="user",
            content="Hi",
            timestamp=0.0,
            meta={"version": 1},
        )
        updated = original.with_meta(version=2)

        assert updated.meta["version"] == 2


class TestTurnSummarize:
    """Tests for Turn.summarize() method."""

    def test_summarize_short_content(self) -> None:
        """Short content is not truncated."""
        turn = Turn(speaker="user", content="Hello", timestamp=0.0)
        assert turn.summarize() == "[user]: Hello"

    def test_summarize_long_content_truncated(self) -> None:
        """Long content is truncated with ellipsis."""
        turn = Turn(speaker="user", content="A" * 100, timestamp=0.0)
        result = turn.summarize(max_length=20)

        assert len(result) < 100
        assert "..." in result
        assert result.startswith("[user]: ")

    def test_summarize_custom_length(self) -> None:
        """summarize respects custom max_length."""
        turn = Turn(speaker="user", content="Hello World!", timestamp=0.0)
        result = turn.summarize(max_length=5)
        assert result == "[user]: Hello..."


class TestTurnTUIOutput:
    """Tests for TUI (Rich Text) output."""

    def test_to_tui_works_with_rich(self) -> None:
        """to_tui returns Rich Text when available."""
        turn = Turn(speaker="user", content="Hello", timestamp=0.0)
        result = turn.to_tui()

        # Should return something (Rich Text or fallback string)
        assert result is not None

    def test_to_tui_contains_speaker_and_content(self) -> None:
        """TUI output contains speaker and content."""
        turn = Turn(speaker="assistant", content="Response", timestamp=0.0)
        result = turn.to_tui()

        # Convert to string for assertion (works for both Rich and fallback)
        result_str = str(result)
        assert "assistant" in result_str
        assert "Response" in result_str


class TestConversationHelpers:
    """Tests for conversation helper functions."""

    @pytest.fixture
    def conversation(self) -> list[Turn]:
        """Sample conversation."""
        return [
            Turn(speaker="user", content="What is Python?", timestamp=1.0),
            Turn(speaker="assistant", content="A programming language.", timestamp=2.0),
            Turn(speaker="user", content="Thanks!", timestamp=3.0),
        ]

    def test_turns_to_markdown(self, conversation: list[Turn]) -> None:
        """turns_to_markdown produces Markdown format."""
        result = turns_to_markdown(conversation)

        assert "**user**:" in result
        assert "**assistant**:" in result
        assert "What is Python?" in result
        assert "A programming language." in result

    def test_turns_to_json(self, conversation: list[Turn]) -> None:
        """turns_to_json produces list of dicts."""
        result = turns_to_json(conversation)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["speaker"] == "user"
        assert result[1]["speaker"] == "assistant"

    def test_turns_to_json_is_serializable(self, conversation: list[Turn]) -> None:
        """turns_to_json output is JSON-serializable."""
        result = turns_to_json(conversation)
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        assert len(parsed) == 3


class TestTurnDeterminism:
    """Tests ensuring Turn operations are deterministic."""

    def test_same_inputs_same_cli_output(self) -> None:
        """Same Turn produces same CLI output."""
        turn1 = Turn(speaker="user", content="Hello", timestamp=1.0)
        turn2 = Turn(speaker="user", content="Hello", timestamp=1.0)

        assert turn1.to_cli() == turn2.to_cli()

    def test_same_inputs_same_json_output(self) -> None:
        """Same Turn produces same JSON output."""
        turn1 = Turn(speaker="user", content="Hello", timestamp=1.0, meta={"x": 1})
        turn2 = Turn(speaker="user", content="Hello", timestamp=1.0, meta={"x": 1})

        assert turn1.to_json() == turn2.to_json()

    def test_same_inputs_same_marimo_output(self) -> None:
        """Same Turn produces same marimo output."""
        turn1 = Turn(speaker="user", content="Hello", timestamp=1.0)
        turn2 = Turn(speaker="user", content="Hello", timestamp=1.0)

        assert turn1.to_marimo() == turn2.to_marimo()
