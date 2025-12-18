"""
Wave 1 Stress Tests for Turn: Property-based and boundary tests.

Visionary UX Flows TEST Phase (N-Phase 8 of 11).
Tests Turn projectors under various input conditions.
"""

from __future__ import annotations

import json

import pytest
from hypothesis import given, settings, strategies as st

from protocols.api.turn import Turn, turns_to_json, turns_to_markdown

# =============================================================================
# PROPERTY-BASED TESTS (Hypothesis)
# =============================================================================


class TestTurnProperties:
    """Property-based tests for Turn invariants."""

    @given(st.text(), st.text(), st.floats(min_value=0, max_value=1e15, allow_nan=False))
    def test_turn_projector_consistency(self, speaker: str, content: str, ts: float) -> None:
        """All projectors produce consistent output for same input."""
        turn = Turn(speaker=speaker, content=content, timestamp=ts)
        cli1 = turn.to_cli()
        cli2 = turn.to_cli()
        assert cli1 == cli2  # Deterministic

    @given(st.text(min_size=0, max_size=100), st.text(min_size=0, max_size=1000))
    def test_turn_cli_contains_speaker_and_content(self, speaker: str, content: str) -> None:
        """CLI output always contains speaker and content."""
        turn = Turn(speaker=speaker, content=content, timestamp=0.0)
        cli = turn.to_cli()
        assert speaker in cli
        assert content in cli

    @given(
        st.text(min_size=0, max_size=50),
        st.text(min_size=0, max_size=500),
        st.floats(min_value=0, max_value=1e10, allow_nan=False, allow_infinity=False),
    )
    def test_turn_json_roundtrip(self, speaker: str, content: str, ts: float) -> None:
        """Turn JSON is valid and contains all fields."""
        turn = Turn(speaker=speaker, content=content, timestamp=ts)
        json_dict = turn.to_json()

        # Should be serializable
        json_str = json.dumps(json_dict)
        parsed = json.loads(json_str)

        assert parsed["speaker"] == speaker
        assert parsed["content"] == content
        assert parsed["timestamp"] == ts

    @given(st.text(min_size=0, max_size=100), st.text(min_size=0, max_size=500))
    def test_turn_marimo_is_html(self, speaker: str, content: str) -> None:
        """marimo output is always valid HTML structure."""
        turn = Turn(speaker=speaker, content=content, timestamp=0.0)
        html = turn.to_marimo()

        assert "<div" in html
        assert "</div>" in html

    @given(st.text(min_size=0, max_size=50), st.text(min_size=0, max_size=200))
    def test_turn_sse_format(self, speaker: str, content: str) -> None:
        """SSE output always follows SSE format."""
        turn = Turn(speaker=speaker, content=content, timestamp=0.0)
        sse = turn.to_sse()

        assert sse.startswith("data: ")
        assert sse.endswith("\n\n")

        # Extract and parse JSON
        json_part = sse[6:-2]
        parsed = json.loads(json_part)
        assert "speaker" in parsed

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=0, max_size=50),
            min_size=0,
            max_size=10,
        )
    )
    def test_turn_with_meta_preserves_original(self, extra_meta: dict[str, str]) -> None:
        """with_meta creates new Turn without modifying original."""
        original = Turn(speaker="user", content="Hi", timestamp=0.0, meta={"key": "val"})
        updated = original.with_meta(**extra_meta)

        # Original unchanged
        assert original.meta == {"key": "val"}

        # Updated has merged meta
        for k, v in extra_meta.items():
            assert updated.meta[k] == v
        assert updated.meta.get("key") == "val"

    @given(st.integers(min_value=1, max_value=200))
    def test_turn_summarize_length(self, max_len: int) -> None:
        """summarize respects max_length parameter."""
        long_content = "A" * 500
        turn = Turn(speaker="user", content=long_content, timestamp=0.0)
        summary = turn.summarize(max_length=max_len)

        # Content portion should be at most max_len + "..."
        content_start_idx = summary.index("]: ") + 3
        content_portion = summary[content_start_idx:]

        if len(long_content) > max_len:
            assert content_portion.endswith("...")
            # Truncated content (without ...) should be max_len
            assert len(content_portion) == max_len + 3


class TestTurnsToMarkdownProperties:
    """Property-based tests for turns_to_markdown."""

    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),
                st.text(min_size=0, max_size=100),
            ),
            min_size=0,
            max_size=20,
        )
    )
    def test_turns_to_markdown_contains_all_speakers(
        self, turn_data: list[tuple[str, str]]
    ) -> None:
        """Markdown output contains all speakers."""
        turns = [
            Turn(speaker=speaker, content=content, timestamp=float(i))
            for i, (speaker, content) in enumerate(turn_data)
        ]
        md = turns_to_markdown(turns)

        for speaker, _ in turn_data:
            if speaker:  # Non-empty speakers should appear
                assert speaker in md


class TestTurnsToJsonProperties:
    """Property-based tests for turns_to_json."""

    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),
                st.text(min_size=0, max_size=100),
            ),
            min_size=0,
            max_size=20,
        )
    )
    def test_turns_to_json_length_matches(self, turn_data: list[tuple[str, str]]) -> None:
        """JSON list has same length as input."""
        turns = [
            Turn(speaker=speaker, content=content, timestamp=float(i))
            for i, (speaker, content) in enumerate(turn_data)
        ]
        result = turns_to_json(turns)

        assert len(result) == len(turns)


# =============================================================================
# STRESS TESTS
# =============================================================================


class TestTurnStress:
    """Stress tests for Turn under load."""

    def test_turn_1000_projections(self) -> None:
        """Turn handles 1000 projections to each format."""
        turn = Turn(
            speaker="assistant",
            content="This is a test response with some content.",
            timestamp=1734200000.0,
            meta={"session": "test123"},
        )

        for _ in range(1000):
            _ = turn.to_cli()
            _ = turn.to_json()
            _ = turn.to_json_str()
            _ = turn.to_marimo()
            _ = turn.to_sse()
            _ = turn.summarize()

    def test_turns_to_markdown_1000_turns(self) -> None:
        """turns_to_markdown handles 1000 turns."""
        turns = [
            Turn(speaker=f"user{i % 10}", content=f"Message {i}", timestamp=float(i))
            for i in range(1000)
        ]
        md = turns_to_markdown(turns)

        assert "user0" in md
        assert "user9" in md
        assert "Message 999" in md

    def test_turns_to_json_1000_turns(self) -> None:
        """turns_to_json handles 1000 turns."""
        turns = [
            Turn(speaker=f"user{i % 10}", content=f"Message {i}", timestamp=float(i))
            for i in range(1000)
        ]
        result = turns_to_json(turns)

        assert len(result) == 1000
        assert result[999]["content"] == "Message 999"

    def test_turn_with_meta_chaining(self) -> None:
        """Turn.with_meta can be chained many times."""
        turn = Turn(speaker="user", content="Hi", timestamp=0.0)

        for i in range(100):
            turn = turn.with_meta(**{f"key{i}": f"value{i}"})

        assert len(turn.meta) == 100
        assert turn.meta["key99"] == "value99"


# =============================================================================
# BOUNDARY VALUE TESTS
# =============================================================================


class TestTurnBoundaryValues:
    """Boundary value tests for Turn edge cases."""

    def test_turn_newlines_in_content(self) -> None:
        """Turn handles newlines in content."""
        turn = Turn(speaker="user", content="Line 1\nLine 2\nLine 3", timestamp=0.0)
        cli = turn.to_cli()
        assert "Line 1\nLine 2\nLine 3" in cli

    def test_turn_tabs_in_content(self) -> None:
        """Turn handles tabs in content."""
        turn = Turn(speaker="user", content="Col1\tCol2\tCol3", timestamp=0.0)
        assert "\t" in turn.to_cli()

    def test_turn_special_chars_in_speaker(self) -> None:
        """Turn handles special characters in speaker."""
        turn = Turn(speaker="user<>&\"'", content="Hi", timestamp=0.0)
        # Should not crash
        _ = turn.to_cli()
        _ = turn.to_marimo()
        _ = turn.to_json()

    def test_turn_html_in_content(self) -> None:
        """Turn handles HTML in content (not escaped in CLI)."""
        turn = Turn(speaker="user", content="<script>alert('xss')</script>", timestamp=0.0)
        cli = turn.to_cli()
        assert "<script>" in cli  # CLI is plain text

    def test_turn_null_bytes_in_content(self) -> None:
        """Turn handles null bytes in content."""
        turn = Turn(speaker="user", content="Hello\x00World", timestamp=0.0)
        cli = turn.to_cli()
        assert "Hello" in cli

    def test_turn_backslash_in_content(self) -> None:
        """Turn handles backslashes in content."""
        turn = Turn(speaker="user", content="path\\to\\file", timestamp=0.0)
        json_out = turn.to_json()
        assert json_out["content"] == "path\\to\\file"

    def test_turn_quotes_in_content(self) -> None:
        """Turn handles quotes in content."""
        turn = Turn(speaker="user", content='He said "Hello"', timestamp=0.0)
        json_str = turn.to_json_str()
        parsed = json.loads(json_str)
        assert parsed["content"] == 'He said "Hello"'

    def test_turn_max_float_timestamp(self) -> None:
        """Turn handles maximum float timestamp."""
        import sys

        turn = Turn(speaker="user", content="Hi", timestamp=sys.float_info.max)
        json_out = turn.to_json()
        assert json_out["timestamp"] == sys.float_info.max

    def test_turn_complex_meta(self) -> None:
        """Turn handles complex nested metadata."""
        complex_meta = {
            "nested": {"deep": {"value": 42}},
            "list": [1, 2, 3],
            "bool": True,
            "none": None,
        }
        turn = Turn(speaker="user", content="Hi", timestamp=0.0, meta=complex_meta)
        json_out = turn.to_json()

        assert json_out["meta"]["nested"]["deep"]["value"] == 42
        assert json_out["meta"]["list"] == [1, 2, 3]


# =============================================================================
# DETERMINISM VERIFICATION
# =============================================================================


class TestTurnDeterminism:
    """Verify Turn operations are fully deterministic."""

    @given(
        st.text(),
        st.text(),
        st.floats(min_value=0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_repeated_cli_identical(self, speaker: str, content: str, ts: float) -> None:
        """Multiple to_cli calls return identical results."""
        turn = Turn(speaker=speaker, content=content, timestamp=ts)
        results = [turn.to_cli() for _ in range(10)]
        assert all(r == results[0] for r in results)

    @given(
        st.text(),
        st.text(),
        st.floats(min_value=0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_repeated_json_identical(self, speaker: str, content: str, ts: float) -> None:
        """Multiple to_json calls return identical results."""
        turn = Turn(speaker=speaker, content=content, timestamp=ts)
        results = [turn.to_json() for _ in range(10)]
        assert all(r == results[0] for r in results)

    @given(st.text(), st.text())
    @settings(max_examples=50)
    def test_repeated_marimo_identical(self, speaker: str, content: str) -> None:
        """Multiple to_marimo calls return identical results."""
        turn = Turn(speaker=speaker, content=content, timestamp=0.0)
        results = [turn.to_marimo() for _ in range(10)]
        assert all(r == results[0] for r in results)
