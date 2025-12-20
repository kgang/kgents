"""
Tests for Token Registry.

Tests the TokenRegistry which is the single source of truth for token
definitions (AD-011). Validates token registration, recognition, and
the six core token types.

Feature: meaning-token-frontend
Requirements: 1.1, 1.6
"""

from __future__ import annotations

import re

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    TokenDefinition,
    TokenPattern,
)
from services.interactive_text.registry import (
    CORE_TOKEN_DEFINITIONS,
    TokenMatch,
    TokenRegistry,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    """Clear registry before each test."""
    TokenRegistry.clear()


# =============================================================================
# TokenRegistry Basic Tests
# =============================================================================


class TestTokenRegistryBasics:
    """Basic tests for TokenRegistry operations."""

    def test_register_token(self) -> None:
        """TokenRegistry can register a token definition."""
        defn = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(),
        )
        TokenRegistry.register(defn)

        result = TokenRegistry.get("test_token")
        assert result == defn

    def test_register_duplicate_raises(self) -> None:
        """Registering duplicate token name raises ValueError."""
        defn = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(),
        )
        TokenRegistry.register(defn)

        with pytest.raises(ValueError, match="already registered"):
            TokenRegistry.register(defn)

    def test_register_or_replace(self) -> None:
        """register_or_replace allows overwriting existing tokens."""
        defn1 = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(),
        )
        defn2 = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\d+")),
            affordances=(),
        )

        TokenRegistry.register(defn1)
        TokenRegistry.register_or_replace(defn2)

        result = TokenRegistry.get("test_token")
        assert result == defn2

    def test_unregister_token(self) -> None:
        """TokenRegistry can unregister a token."""
        defn = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(),
        )
        TokenRegistry.register(defn)

        assert TokenRegistry.unregister("test_token") is True
        assert TokenRegistry.get("test_token") is None

    def test_unregister_nonexistent(self) -> None:
        """Unregistering nonexistent token returns False."""
        assert TokenRegistry.unregister("nonexistent") is False

    def test_get_nonexistent(self) -> None:
        """Getting nonexistent token returns None."""
        assert TokenRegistry.get("nonexistent") is None

    def test_get_all(self) -> None:
        """get_all returns all registered tokens."""
        defn1 = TokenDefinition(
            name="token1",
            pattern=TokenPattern(name="t1", regex=re.compile(r"\w+")),
            affordances=(),
        )
        defn2 = TokenDefinition(
            name="token2",
            pattern=TokenPattern(name="t2", regex=re.compile(r"\d+")),
            affordances=(),
        )

        TokenRegistry.register(defn1)
        TokenRegistry.register(defn2)

        all_tokens = TokenRegistry.get_all()
        # Core tokens + our 2 custom tokens
        assert "token1" in all_tokens
        assert "token2" in all_tokens

    def test_clear(self) -> None:
        """clear removes all registered tokens."""
        defn = TokenDefinition(
            name="test_token",
            pattern=TokenPattern(name="test", regex=re.compile(r"\w+")),
            affordances=(),
        )
        TokenRegistry.register(defn)
        TokenRegistry.clear()

        # After clear, registry is empty (not even core tokens until accessed)
        assert TokenRegistry._tokens == {}


# =============================================================================
# Core Token Tests
# =============================================================================


class TestCoreTokens:
    """Tests for the six core token types."""

    def test_six_core_tokens_defined(self) -> None:
        """Exactly six core token types are defined."""
        assert len(CORE_TOKEN_DEFINITIONS) == 6

    def test_core_token_names(self) -> None:
        """Core tokens have expected names."""
        names = {defn.name for defn in CORE_TOKEN_DEFINITIONS}
        expected = {
            "agentese_path",
            "task_checkbox",
            "image",
            "code_block",
            "principle_ref",
            "requirement_ref",
        }
        assert names == expected

    def test_agentese_path_pattern(self) -> None:
        """AGENTESE path pattern matches valid paths."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "agentese_path")

        # Valid paths
        assert defn.pattern.regex.search("`world.town.citizen`")
        assert defn.pattern.regex.search("`self.memory.capture`")
        assert defn.pattern.regex.search("`concept.agent.compose`")
        assert defn.pattern.regex.search("`void.entropy.sample`")
        assert defn.pattern.regex.search("`time.witness.crystallize`")

        # Invalid paths (no match)
        assert not defn.pattern.regex.search("`invalid.path`")
        assert not defn.pattern.regex.search("world.town.citizen")  # No backticks

    def test_task_checkbox_pattern(self) -> None:
        """Task checkbox pattern matches GitHub-style checkboxes."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "task_checkbox")

        # Unchecked
        match = defn.pattern.regex.search("- [ ] Task description")
        assert match
        assert match.group(1) == " "
        assert match.group(2) == "Task description"

        # Checked
        match = defn.pattern.regex.search("- [x] Completed task")
        assert match
        assert match.group(1) == "x"

        # Uppercase X
        match = defn.pattern.regex.search("- [X] Also completed")
        assert match
        assert match.group(1) == "X"

    def test_image_pattern(self) -> None:
        """Image pattern matches markdown images."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "image")

        match = defn.pattern.regex.search("![Alt text](path/to/image.png)")
        assert match
        assert match.group(1) == "Alt text"
        assert match.group(2) == "path/to/image.png"

        # Empty alt text
        match = defn.pattern.regex.search("![](image.jpg)")
        assert match
        assert match.group(1) == ""

    def test_code_block_pattern(self) -> None:
        """Code block pattern matches fenced code blocks."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "code_block")

        text = "```python\nprint('hello')\n```"
        match = defn.pattern.regex.search(text)
        assert match
        assert match.group(1) == "python"
        assert "print" in match.group(2)

        # No language
        text = "```\ncode here\n```"
        match = defn.pattern.regex.search(text)
        assert match
        assert match.group(1) == ""

    def test_principle_ref_pattern(self) -> None:
        """Principle reference pattern matches [P1], [P2], etc."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "principle_ref")

        match = defn.pattern.regex.search("[P1]")
        assert match
        assert match.group(1) == "1"

        match = defn.pattern.regex.search("[P42]")
        assert match
        assert match.group(1) == "42"

    def test_requirement_ref_pattern(self) -> None:
        """Requirement reference pattern matches [R1], [R1.2], etc."""
        defn = next(d for d in CORE_TOKEN_DEFINITIONS if d.name == "requirement_ref")

        match = defn.pattern.regex.search("[R1]")
        assert match
        assert match.group(1) == "1"

        match = defn.pattern.regex.search("[R1.2]")
        assert match
        assert match.group(1) == "1.2"

        match = defn.pattern.regex.search("[R12.34]")
        assert match
        assert match.group(1) == "12.34"

    def test_core_tokens_have_affordances(self) -> None:
        """All core tokens have at least one affordance."""
        for defn in CORE_TOKEN_DEFINITIONS:
            assert len(defn.affordances) > 0, f"{defn.name} has no affordances"

    def test_core_tokens_have_projectors(self) -> None:
        """All core tokens have projectors for cli, web, json."""
        for defn in CORE_TOKEN_DEFINITIONS:
            assert "cli" in defn.projectors, f"{defn.name} missing cli projector"
            assert "web" in defn.projectors, f"{defn.name} missing web projector"
            assert "json" in defn.projectors, f"{defn.name} missing json projector"


# =============================================================================
# Token Recognition Tests
# =============================================================================


class TestTokenRecognition:
    """Tests for token recognition in text."""

    def test_recognize_single_token(self) -> None:
        """recognize finds a single token in text."""
        text = "Check out `world.town.citizen` for details."
        matches = TokenRegistry.recognize(text)

        agentese_matches = [m for m in matches if m.definition.name == "agentese_path"]
        assert len(agentese_matches) == 1
        assert agentese_matches[0].text == "`world.town.citizen`"

    def test_recognize_multiple_tokens(self) -> None:
        """recognize finds multiple tokens in text."""
        text = """
        - [ ] First task
        - [x] Second task
        Check `self.memory.capture` for more.
        """
        matches = TokenRegistry.recognize(text)

        task_matches = [m for m in matches if m.definition.name == "task_checkbox"]
        agentese_matches = [m for m in matches if m.definition.name == "agentese_path"]

        assert len(task_matches) == 2
        assert len(agentese_matches) == 1

    def test_recognize_ordered_by_position(self) -> None:
        """recognize returns matches ordered by position."""
        text = "`world.a` then `self.b` then `concept.c`"
        matches = TokenRegistry.recognize(text)

        agentese_matches = [m for m in matches if m.definition.name == "agentese_path"]
        assert len(agentese_matches) == 3

        # Should be in order of appearance
        assert agentese_matches[0].start < agentese_matches[1].start
        assert agentese_matches[1].start < agentese_matches[2].start

    def test_recognize_empty_text(self) -> None:
        """recognize returns empty list for empty text."""
        matches = TokenRegistry.recognize("")
        # May have some matches from core tokens, but no actual content matches
        assert all(m.start == m.end for m in matches) or len(matches) == 0

    def test_recognize_no_tokens(self) -> None:
        """recognize returns empty list when no tokens match."""
        text = "Just plain text with no special tokens."
        matches = TokenRegistry.recognize(text)

        # Filter out any zero-length matches
        real_matches = [m for m in matches if m.start < m.end]
        assert len(real_matches) == 0

    def test_token_match_properties(self) -> None:
        """TokenMatch has correct properties."""
        text = "See `world.town.citizen` here"
        matches = TokenRegistry.recognize(text)

        agentese_match = next(m for m in matches if m.definition.name == "agentese_path")

        assert agentese_match.text == "`world.town.citizen`"
        assert agentese_match.start == text.index("`world")
        assert agentese_match.end == agentese_match.start + len("`world.town.citizen`")
        assert len(agentese_match.groups) > 0


# =============================================================================
# Property-Based Tests
# =============================================================================


@st.composite
def text_with_agentese_paths(draw: st.DrawFn) -> tuple[str, int]:
    """Generate text containing AGENTESE paths."""
    context = draw(st.sampled_from(["world", "self", "concept", "void", "time"]))
    segments = draw(st.lists(
        st.from_regex(r"[a-z_][a-z0-9_]*", fullmatch=True),
        min_size=1,
        max_size=3,
    ))
    path = f"`{context}.{'.'.join(segments)}`"

    # Wrap in some text
    prefix = draw(st.text(min_size=0, max_size=20, alphabet="abcdefghijklmnop "))
    suffix = draw(st.text(min_size=0, max_size=20, alphabet="abcdefghijklmnop "))

    return f"{prefix}{path}{suffix}", 1


class TestTokenRecognitionProperties:
    """Property-based tests for token recognition."""

    @given(data=text_with_agentese_paths())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_agentese_paths_recognized(self, data: tuple[str, int]) -> None:
        """AGENTESE paths in text are always recognized."""
        text, expected_count = data
        matches = TokenRegistry.recognize(text)

        agentese_matches = [m for m in matches if m.definition.name == "agentese_path"]
        assert len(agentese_matches) >= expected_count

    @given(text=st.text(min_size=0, max_size=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_recognize_never_crashes(self, text: str) -> None:
        """recognize never crashes on any input."""
        # Should not raise any exception
        matches = TokenRegistry.recognize(text)
        assert isinstance(matches, list)

    @given(text=st.text(min_size=0, max_size=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_matches_within_bounds(self, text: str) -> None:
        """All matches are within text bounds."""
        matches = TokenRegistry.recognize(text)

        for match in matches:
            assert 0 <= match.start <= len(text)
            assert 0 <= match.end <= len(text)
            assert match.start <= match.end
