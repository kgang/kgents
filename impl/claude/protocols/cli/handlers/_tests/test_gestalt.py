"""
Tests for gestalt CLI handler.

Session: F-gent Crown Jewels Integration (Phase 4)

Tests cover:
- Basic gestalt commands
- Research exploration (Phase 4: Gestalt + ResearchFlow)
- Hypothesis tree operations
"""

from __future__ import annotations

from typing import Generator

import pytest

from protocols.cli.handlers.gestalt import (
    Hypothesis,
    ResearchState,
    _get_state,
    _reset_state,
    cmd_gestalt,
)


@pytest.fixture(autouse=True)
def isolate_gestalt() -> Generator[None, None, None]:
    """Reset gestalt state between tests."""
    yield
    _reset_state()


# =============================================================================
# Basic Command Tests
# =============================================================================


class TestGestaltHelp:
    """Tests for gestalt --help."""

    def test_help_returns_zero(self) -> None:
        """--help should return 0."""
        result = cmd_gestalt(["--help"])
        assert result == 0

    def test_help_short_returns_zero(self) -> None:
        """-h should return 0."""
        result = cmd_gestalt(["-h"])
        assert result == 0


class TestGestaltStatus:
    """Tests for gestalt status command."""

    def test_status_default_no_research(self) -> None:
        """Default command (no args) shows status."""
        result = cmd_gestalt([])
        assert result == 0

    def test_status_explicit(self) -> None:
        """Explicit status command works."""
        result = cmd_gestalt(["status"])
        assert result == 0

    def test_status_json(self) -> None:
        """Status with --json returns structured output."""
        result = cmd_gestalt(["--json"])
        assert result == 0


# =============================================================================
# Research Exploration Tests (Phase 4)
# =============================================================================


class TestGestaltExplore:
    """Tests for gestalt explore command."""

    def test_explore_creates_research(self) -> None:
        """Explore creates a new research exploration."""
        result = cmd_gestalt(["explore", "What patterns exist in the codebase?"])
        assert result == 0

        state = _get_state()
        assert state.question == "What patterns exist in the codebase?"
        assert len(state.hypotheses) == 1

    def test_explore_requires_question(self) -> None:
        """Explore without question shows error."""
        result = cmd_gestalt(["explore"])
        assert result == 1

    def test_explore_empty_question_shows_error(self) -> None:
        """Explore with empty question shows error."""
        result = cmd_gestalt(["explore", "   "])
        assert result == 1

    def test_explore_multiple_words(self) -> None:
        """Explore joins multiple args into question."""
        result = cmd_gestalt(["explore", "What", "is", "the", "architecture?"])
        assert result == 0

        state = _get_state()
        assert state.question == "What is the architecture?"

    def test_explore_creates_root_hypothesis(self) -> None:
        """Explore creates a root hypothesis."""
        cmd_gestalt(["explore", "Test question"])

        state = _get_state()
        assert len(state.hypotheses) == 1
        root = state.hypotheses[0]
        assert root.parent_id is None
        assert root.depth == 0
        assert root.status == "open"


class TestGestaltBranch:
    """Tests for gestalt branch command."""

    def test_branch_requires_exploration(self) -> None:
        """Branch without active exploration shows error."""
        result = cmd_gestalt(["branch", "Some hypothesis"])
        assert result == 1

    def test_branch_adds_hypothesis(self) -> None:
        """Branch adds a new hypothesis."""
        cmd_gestalt(["explore", "Test question"])
        result = cmd_gestalt(["branch", "The system uses layered architecture"])
        assert result == 0

        state = _get_state()
        assert len(state.hypotheses) == 2
        new_hyp = state.hypotheses[1]
        assert new_hyp.content == "The system uses layered architecture"
        assert new_hyp.depth == 1

    def test_branch_requires_hypothesis_text(self) -> None:
        """Branch without hypothesis text shows error."""
        cmd_gestalt(["explore", "Test question"])
        result = cmd_gestalt(["branch"])
        assert result == 1

    def test_branch_sets_focus(self) -> None:
        """Branch updates current focus to new hypothesis."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "First hypothesis"])
        cmd_gestalt(["branch", "Second hypothesis"])

        state = _get_state()
        # Focus should be on the latest hypothesis
        assert state.current_focus_id == state.hypotheses[-1].id

    def test_branch_increments_depth(self) -> None:
        """Branching from a branch increments depth."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "Depth 1"])
        cmd_gestalt(["branch", "Depth 2"])

        state = _get_state()
        assert state.hypotheses[0].depth == 0  # Root
        assert state.hypotheses[1].depth == 1
        assert state.hypotheses[2].depth == 2


class TestGestaltTree:
    """Tests for gestalt tree command."""

    def test_tree_no_research(self) -> None:
        """Tree with no active research returns gracefully."""
        result = cmd_gestalt(["tree"])
        assert result == 0

    def test_tree_shows_hypotheses(self) -> None:
        """Tree shows the hypothesis tree."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "H1"])
        cmd_gestalt(["branch", "H2"])

        result = cmd_gestalt(["tree"])
        assert result == 0

    def test_tree_json(self) -> None:
        """Tree with --json returns structured output."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "H1"])

        result = cmd_gestalt(["tree", "--json"])
        assert result == 0


class TestGestaltSynthesize:
    """Tests for gestalt synthesize command."""

    def test_synthesize_requires_exploration(self) -> None:
        """Synthesize without active exploration shows error."""
        result = cmd_gestalt(["synthesize"])
        assert result == 1

    def test_synthesize_requires_multiple_hypotheses(self) -> None:
        """Synthesize requires at least 2 hypotheses."""
        cmd_gestalt(["explore", "Test question"])
        result = cmd_gestalt(["synthesize"])
        assert result == 1

    def test_synthesize_works_with_hypotheses(self) -> None:
        """Synthesize works with multiple hypotheses."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "H1"])
        cmd_gestalt(["branch", "H2"])

        result = cmd_gestalt(["synthesize"])
        assert result == 0

        state = _get_state()
        assert state.synthesis is not None


class TestGestaltReset:
    """Tests for gestalt reset command."""

    def test_reset_clears_state(self) -> None:
        """Reset clears all research state."""
        cmd_gestalt(["explore", "Test question"])
        cmd_gestalt(["branch", "H1"])

        result = cmd_gestalt(["reset"])
        assert result == 0

        state = _get_state()
        assert state.question is None
        assert len(state.hypotheses) == 0


@pytest.mark.slow  # Real codebase scan can timeout in CI
class TestGestaltCodebase:
    """Tests for gestalt codebase command."""

    @pytest.mark.slow
    def test_codebase_returns_zero(self) -> None:
        """Codebase command returns 0."""
        # This may take time for first scan - marked slow for CI
        result = cmd_gestalt(["codebase"])
        assert result == 0


class TestGestaltErrorPaths:
    """Tests for error handling."""

    def test_unknown_subcommand(self) -> None:
        """Unknown subcommand returns error."""
        result = cmd_gestalt(["unknown_cmd"])
        assert result == 1


# =============================================================================
# State Management Tests
# =============================================================================


class TestResearchState:
    """Tests for ResearchState dataclass."""

    def test_default_state(self) -> None:
        """Default state has no question."""
        state = ResearchState()
        assert state.question is None
        assert state.hypotheses == []
        assert state.synthesis is None

    def test_hypothesis_creation(self) -> None:
        """Hypothesis can be created with required fields."""
        h = Hypothesis(
            id="test123",
            content="Test hypothesis",
            parent_id=None,
            depth=0,
            status="open",
        )
        assert h.id == "test123"
        assert h.content == "Test hypothesis"
        assert h.status == "open"
        assert h.evidence == []
