"""
Tests for the explore CLI handler.

Verifies:
- Subcommand routing (start, navigate, budget, evidence, trail, commit, loops, reset)
- State management (singleton harness)
- JSON output mode
- Help text
"""

from __future__ import annotations

import json
from io import StringIO
import sys

import pytest


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_harness():
    """Reset harness before each test."""
    from protocols.cli.handlers.explore import reset_harness
    reset_harness()
    yield
    reset_harness()


# =============================================================================
# Help and Basic Routing
# =============================================================================


def test_help_flag(capsys):
    """Test that --help shows help text."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["--help"])
    assert result == 0

    captured = capsys.readouterr()
    assert "kg explore" in captured.out
    assert "USAGE:" in captured.out
    assert "start" in captured.out
    assert "navigate" in captured.out


def test_no_args_shows_status(capsys):
    """Test that no args shows status (with no active exploration message)."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore([])
    assert result == 0

    captured = capsys.readouterr()
    assert "Exploration State" in captured.out or "No active exploration" in captured.out


# =============================================================================
# Start Subcommand
# =============================================================================


def test_start_creates_harness(capsys):
    """Test that 'start' creates a new exploration."""
    from protocols.cli.handlers.explore import cmd_explore, has_active_harness

    assert not has_active_harness()

    result = cmd_explore(["start", "world.brain.core"])
    assert result == 0

    assert has_active_harness()

    captured = capsys.readouterr()
    assert "Exploration Started" in captured.out
    assert "world.brain.core" in captured.out


def test_start_with_preset(capsys):
    """Test that 'start' respects preset flag."""
    from protocols.cli.handlers.explore import cmd_explore, get_or_create_harness

    result = cmd_explore(["start", "test.path", "--preset", "quick"])
    assert result == 0

    harness = get_or_create_harness()
    # Quick budget has lower limits
    assert harness.budget.max_steps <= 20


def test_start_requires_path(capsys):
    """Test that 'start' without path shows usage."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["start"])
    assert result == 1

    captured = capsys.readouterr()
    assert "Usage:" in captured.out


# =============================================================================
# Navigate Subcommand
# =============================================================================


def test_navigate_requires_active_harness(capsys):
    """Test that 'navigate' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["navigate", "tests"])
    assert result == 1

    captured = capsys.readouterr()
    assert "No active exploration" in captured.out


def test_navigate_requires_edge(capsys):
    """Test that 'navigate' requires edge argument."""
    from protocols.cli.handlers.explore import cmd_explore

    # Start an exploration first
    cmd_explore(["start", "test.path"])

    result = cmd_explore(["navigate"])
    assert result == 1

    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_navigate_after_start(capsys):
    """Test navigation after starting exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["navigate", "child"])

    # Navigation may fail due to mock graph, but shouldn't error
    assert result in (0, 1)


# =============================================================================
# Budget Subcommand
# =============================================================================


def test_budget_requires_active_harness(capsys):
    """Test that 'budget' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["budget"])
    assert result == 1


def test_budget_shows_breakdown(capsys):
    """Test that 'budget' shows budget info after start."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["budget"])
    assert result == 0

    captured = capsys.readouterr()
    assert "Budget" in captured.out
    assert "Steps" in captured.out


def test_budget_json_output(capsys):
    """Test that 'budget --json' outputs valid JSON."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    capsys.readouterr()  # Discard start output

    result = cmd_explore(["budget", "--json"])
    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "steps" in data
    assert "nodes" in data


# =============================================================================
# Evidence Subcommand
# =============================================================================


def test_evidence_requires_active_harness(capsys):
    """Test that 'evidence' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["evidence"])
    assert result == 1


def test_evidence_shows_empty_state(capsys):
    """Test that 'evidence' shows message when no evidence collected."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["evidence"])
    assert result == 0

    captured = capsys.readouterr()
    assert "Evidence" in captured.out


def test_evidence_json_output(capsys):
    """Test that 'evidence --json' outputs valid JSON."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    capsys.readouterr()  # Discard start output

    result = cmd_explore(["evidence", "--json"])
    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total" in data
    assert "evidence" in data


# =============================================================================
# Trail Subcommand
# =============================================================================


def test_trail_requires_active_harness(capsys):
    """Test that 'trail' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["trail"])
    assert result == 1


def test_trail_shows_steps(capsys):
    """Test that 'trail' shows navigation trail."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["trail"])
    assert result == 0

    captured = capsys.readouterr()
    assert "Trail" in captured.out
    assert "test.path" in captured.out


def test_trail_json_output(capsys):
    """Test that 'trail --json' outputs valid JSON."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    capsys.readouterr()  # Discard start output

    result = cmd_explore(["trail", "--json"])
    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "steps" in data
    # Check correct field names (node, edge_taken not node_path, edge)
    if data["steps"]:
        step = data["steps"][0]
        assert "node" in step
        assert "edge_taken" in step


# =============================================================================
# Commit Subcommand
# =============================================================================


def test_commit_requires_active_harness(capsys):
    """Test that 'commit' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["commit", "test claim"])
    assert result == 1


def test_commit_requires_claim(capsys):
    """Test that 'commit' requires claim argument."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["commit"])
    assert result == 1

    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_commit_attempt(capsys):
    """Test commit attempt (may fail due to insufficient evidence)."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["commit", "test claim", "--level", "tentative"])

    # May succeed or fail based on evidence, but should not error
    assert result in (0, 1)


# =============================================================================
# Loops Subcommand
# =============================================================================


def test_loops_requires_active_harness(capsys):
    """Test that 'loops' requires active exploration."""
    from protocols.cli.handlers.explore import cmd_explore

    result = cmd_explore(["loops"])
    assert result == 1


def test_loops_shows_status(capsys):
    """Test that 'loops' shows loop detection status."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    result = cmd_explore(["loops"])
    assert result == 0

    captured = capsys.readouterr()
    assert "Loop" in captured.out
    assert "Warnings" in captured.out


def test_loops_json_output(capsys):
    """Test that 'loops --json' outputs valid JSON."""
    from protocols.cli.handlers.explore import cmd_explore

    cmd_explore(["start", "test.path"])
    capsys.readouterr()  # Discard start output

    result = cmd_explore(["loops", "--json"])
    assert result == 0

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "warnings" in data
    assert "halted" in data


# =============================================================================
# Reset Subcommand
# =============================================================================


def test_reset_clears_harness(capsys):
    """Test that 'reset' clears the active harness."""
    from protocols.cli.handlers.explore import cmd_explore, has_active_harness

    cmd_explore(["start", "test.path"])
    assert has_active_harness()

    result = cmd_explore(["reset"])
    assert result == 0
    assert not has_active_harness()

    captured = capsys.readouterr()
    assert "Reset" in captured.out


# =============================================================================
# State Management
# =============================================================================


def test_harness_persists_across_calls():
    """Test that harness state persists between cmd_explore calls."""
    from protocols.cli.handlers.explore import cmd_explore, get_or_create_harness

    cmd_explore(["start", "test.path"])
    harness1 = get_or_create_harness()

    cmd_explore(["budget"])
    harness2 = get_or_create_harness()

    assert harness1 is harness2


def test_start_resets_harness():
    """Test that 'start' with new path creates fresh harness."""
    from protocols.cli.handlers.explore import cmd_explore, get_or_create_harness

    cmd_explore(["start", "path.one"])
    harness1 = get_or_create_harness()

    cmd_explore(["start", "path.two"])
    harness2 = get_or_create_harness()

    assert harness1 is not harness2


# =============================================================================
# Integration with Exploration Module
# =============================================================================


def test_harness_has_expected_attributes():
    """Test that created harness has expected attributes."""
    from protocols.cli.handlers.explore import cmd_explore, get_or_create_harness

    cmd_explore(["start", "test.path"])
    harness = get_or_create_harness()

    # Check essential attributes
    assert hasattr(harness, "budget")
    assert hasattr(harness, "loop_detector")
    assert hasattr(harness, "evidence_collector")
    assert hasattr(harness, "trail")
    assert hasattr(harness, "focus")
    assert hasattr(harness, "get_state")


def test_budget_presets():
    """Test that budget presets work correctly."""
    from protocols.cli.handlers.explore import cmd_explore, get_or_create_harness, reset_harness

    # Quick preset
    cmd_explore(["start", "test.path", "--preset", "quick"])
    harness_quick = get_or_create_harness()
    quick_max = harness_quick.budget.max_steps

    reset_harness()

    # Thorough preset
    cmd_explore(["start", "test.path", "--preset", "thorough"])
    harness_thorough = get_or_create_harness()
    thorough_max = harness_thorough.budget.max_steps

    # Thorough should have more steps than quick
    assert thorough_max > quick_max
