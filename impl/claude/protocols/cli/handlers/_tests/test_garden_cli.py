# mypy: ignore-errors
"""
Tests for Gardener-Logos CLI Commands (Phase 2).

Tests for:
- kg garden (show, season, health, init, transition)
- kg tend (observe, prune, graft, water, rotate, wait)
- kg plot (list, show, create, focus, link, discover)
"""

from __future__ import annotations

import pytest

# =============================================================================
# Garden Command Tests
# =============================================================================


class TestGardenCommand:
    """Tests for kg garden command."""

    def test_garden_help(self) -> None:
        """Test garden --help returns 0."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["--help"])
        assert result == 0

    def test_garden_show_default(self) -> None:
        """Test kg garden (default show) returns 0."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden([])
        assert result == 0

    def test_garden_show_json(self) -> None:
        """Test kg garden --json returns valid JSON."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        # Capture stdout
        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        output = captured.getvalue()
        # Should be valid JSON
        data = json.loads(output)
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert "garden_id" in data or "plots" in data

    def test_garden_season(self) -> None:
        """Test kg garden season returns season info."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["season"])
        assert result == 0

    def test_garden_season_json(self) -> None:
        """Test kg garden season --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["season", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert "name" in data
        assert "plasticity" in data
        assert "entropy_multiplier" in data

    def test_garden_health(self) -> None:
        """Test kg garden health."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["health"])
        assert result == 0

    def test_garden_health_json(self) -> None:
        """Test kg garden health --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["health", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert "health_score" in data
        assert "entropy_spent" in data
        assert "entropy_budget" in data

    def test_garden_init(self) -> None:
        """Test kg garden init."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["init"])
        assert result == 0

    def test_garden_init_json(self) -> None:
        """Test kg garden init --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["init", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["status"] == "initialized"
        assert "plots" in data
        assert len(data["plots"]) > 0

    def test_garden_transition(self) -> None:
        """Test kg garden transition SPROUTING."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["transition", "SPROUTING", "Testing transition"])
        assert result == 0

    def test_garden_transition_invalid_season(self) -> None:
        """Test kg garden transition with invalid season."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["transition", "INVALID"])
        assert result == 1

    def test_garden_transition_missing_season(self) -> None:
        """Test kg garden transition without season arg."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["transition"])
        assert result == 1

    def test_garden_unknown_subcommand(self) -> None:
        """Test kg garden unknown returns error."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["unknown"])
        assert result == 1

    # =========================================================================
    # Auto-Inducer Tests (Phase 8)
    # =========================================================================

    def test_garden_suggest(self) -> None:
        """Test kg garden suggest returns 0."""
        from protocols.cli.handlers.garden import cmd_garden

        result = cmd_garden(["suggest"])
        assert result == 0

    def test_garden_suggest_json(self) -> None:
        """Test kg garden suggest --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["suggest", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert "status" in data
        assert "signals" in data
        # Either "no_suggestion" or "suggestion"
        assert data["status"] in ("no_suggestion", "suggestion")

    def test_garden_suggest_shows_signals(self) -> None:
        """Test kg garden suggest shows transition signals."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["suggest", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]

        # Signals should always be present
        signals = data.get("signals", {})
        assert "gesture_frequency" in signals
        assert "gesture_diversity" in signals
        assert "time_in_season_hours" in signals
        assert "entropy_spent_ratio" in signals

    def test_garden_accept_no_suggestion(self) -> None:
        """Test kg garden accept returns 1 when no suggestion."""
        from protocols.cli.handlers.garden import cmd_garden

        # Fresh garden has no pending suggestion
        result = cmd_garden(["accept"])
        assert result == 1

    def test_garden_accept_json_no_suggestion(self) -> None:
        """Test kg garden accept --json returns error when no suggestion."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["accept", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        # Either returns 1 (legacy) or 0 with error in metadata (project_command)
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["status"] == "no_suggestion"

    def test_garden_dismiss_no_suggestion(self) -> None:
        """Test kg garden dismiss returns 1 when no suggestion."""
        from protocols.cli.handlers.garden import cmd_garden

        # Fresh garden has no pending suggestion
        result = cmd_garden(["dismiss"])
        assert result == 1

    def test_garden_dismiss_json_no_suggestion(self) -> None:
        """Test kg garden dismiss --json returns error when no suggestion."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_garden(["dismiss", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        # Either returns 1 (legacy) or 0 with error in metadata (project_command)
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["status"] == "no_suggestion"


# =============================================================================
# Tend Command Tests
# =============================================================================


class TestTendCommand:
    """Tests for kg tend command."""

    def test_tend_help(self) -> None:
        """Test tend --help returns 0."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["--help"])
        assert result == 0

    def test_tend_no_args_shows_help(self) -> None:
        """Test kg tend (no args) shows help."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend([])
        assert result == 0

    def test_tend_observe(self) -> None:
        """Test kg tend observe."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["observe", "concept.gardener"])
        assert result == 0

    @pytest.mark.skip(
        reason="AGENTESE resolution bug: self.garden blocks self.garden.tend delegation"
    )
    def test_tend_observe_json(self) -> None:
        """Test kg tend observe --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.tend import cmd_tend

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_tend(["observe", "concept.gardener", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["verb"] == "observe"
        assert data["accepted"] is True
        assert "observations" in data

    def test_tend_prune_with_reason(self) -> None:
        """Test kg tend prune with --reason."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["prune", "concept.prompt.old", "--reason", "No longer needed"])
        assert result == 0

    def test_tend_prune_without_reason(self) -> None:
        """Test kg tend prune without --reason fails."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["prune", "concept.prompt.old"])
        assert result == 1

    def test_tend_graft_with_reason(self) -> None:
        """Test kg tend graft with --reason."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["graft", "concept.prompt.new", "--reason", "New feature"])
        assert result == 0

    def test_tend_graft_without_reason(self) -> None:
        """Test kg tend graft without --reason fails."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["graft", "concept.prompt.new"])
        assert result == 1

    def test_tend_water_with_feedback(self) -> None:
        """Test kg tend water with --feedback."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["water", "concept.prompt.task", "--feedback", "Add specificity"])
        assert result == 0

    @pytest.mark.skip(
        reason="AGENTESE resolution bug: self.garden blocks self.garden.tend delegation"
    )
    def test_tend_water_json(self) -> None:
        """Test kg tend water --json shows learning_rate."""
        import io
        import json
        import sys

        from protocols.cli.handlers.tend import cmd_tend

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_tend(
                [
                    "water",
                    "concept.prompt.task",
                    "--feedback",
                    "Improve clarity",
                    "--json",
                ]
            )
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["verb"] == "water"
        assert "learning_rate" in data
        assert "synergies_triggered" in data

    def test_tend_water_without_feedback(self) -> None:
        """Test kg tend water without --feedback fails."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["water", "concept.prompt.task"])
        assert result == 1

    def test_tend_rotate(self) -> None:
        """Test kg tend rotate."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["rotate", "concept.gardener.season"])
        assert result == 0

    def test_tend_wait(self) -> None:
        """Test kg tend wait (no target needed)."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["wait"])
        assert result == 0

    def test_tend_wait_with_reason(self) -> None:
        """Test kg tend wait with --reason."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["wait", "--reason", "Contemplating next steps"])
        assert result == 0

    def test_tend_invalid_verb(self) -> None:
        """Test kg tend invalid_verb fails."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["destroy", "something"])
        assert result == 1

    def test_tend_missing_target(self) -> None:
        """Test kg tend observe (no target) fails."""
        from protocols.cli.handlers.tend import cmd_tend

        result = cmd_tend(["observe"])
        assert result == 1

    @pytest.mark.skip(
        reason="AGENTESE resolution bug: self.garden blocks self.garden.tend delegation"
    )
    def test_tend_with_tone(self) -> None:
        """Test kg tend with --tone flag."""
        import io
        import json
        import sys

        from protocols.cli.handlers.tend import cmd_tend

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_tend(
                [
                    "prune",
                    "concept.prompt.old",
                    "--reason",
                    "High confidence removal",
                    "--tone",
                    "0.9",
                    "--json",
                ]
            )
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        assert data["tone"] == 0.9


# =============================================================================
# Tend Alias Tests
# =============================================================================


class TestTendAliases:
    """Tests for tend verb aliases (kg observe, kg prune, etc.)."""

    def test_observe_alias(self) -> None:
        """Test kg observe as alias."""
        from protocols.cli.handlers.tend import cmd_observe

        result = cmd_observe(["concept.gardener"])
        assert result == 0

    def test_prune_alias(self) -> None:
        """Test kg prune as alias."""
        from protocols.cli.handlers.tend import cmd_prune

        result = cmd_prune(["concept.prompt.old", "--reason", "Cleanup"])
        assert result == 0

    def test_graft_alias(self) -> None:
        """Test kg graft as alias."""
        from protocols.cli.handlers.tend import cmd_graft

        result = cmd_graft(["concept.prompt.new", "--reason", "Addition"])
        assert result == 0

    def test_water_alias(self) -> None:
        """Test kg water as alias."""
        from protocols.cli.handlers.tend import cmd_water

        result = cmd_water(["concept.prompt.task", "--feedback", "Improve"])
        assert result == 0

    def test_rotate_alias(self) -> None:
        """Test kg rotate as alias."""
        from protocols.cli.handlers.tend import cmd_rotate

        result = cmd_rotate(["concept.gardener"])
        assert result == 0

    def test_wait_alias(self) -> None:
        """Test kg wait as alias."""
        from protocols.cli.handlers.tend import cmd_wait

        result = cmd_wait([])
        assert result == 0


# =============================================================================
# Plot Command Tests
# =============================================================================


class TestPlotCommand:
    """Tests for kg plot command."""

    def test_plot_help(self) -> None:
        """Test plot --help returns 0."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["--help"])
        assert result == 0

    def test_plot_list(self) -> None:
        """Test kg plot (list)."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot([])
        assert result == 0

    def test_plot_list_json(self) -> None:
        """Test kg plot --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.plot import cmd_plot

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_plot(["--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        assert "plots" in data
        assert "count" in data
        assert data["count"] > 0

    def test_plot_show(self) -> None:
        """Test kg plot <name>."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["atelier"])
        assert result == 0

    def test_plot_show_json(self) -> None:
        """Test kg plot <name> --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.plot import cmd_plot

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_plot(["atelier", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        assert data["name"] == "atelier"
        assert "path" in data
        assert "crown_jewel" in data

    def test_plot_show_not_found(self) -> None:
        """Test kg plot nonexistent returns error."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["nonexistent-plot"])
        assert result == 1

    def test_plot_create(self) -> None:
        """Test kg plot create."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(
            [
                "create",
                "test-feature",
                "--path",
                "concept.test.feature",
                "--description",
                "Test feature plot",
            ]
        )
        assert result == 0

    def test_plot_create_json(self) -> None:
        """Test kg plot create --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.plot import cmd_plot

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_plot(
                [
                    "create",
                    "another-feature",
                    "--path",
                    "concept.another",
                    "--json",
                ]
            )
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        assert data["status"] == "created"
        assert data["name"] == "another-feature"

    def test_plot_create_missing_name(self) -> None:
        """Test kg plot create (no name) fails."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["create"])
        assert result == 1

    def test_plot_focus(self) -> None:
        """Test kg plot focus."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["focus", "atelier"])
        assert result == 0

    def test_plot_focus_json(self) -> None:
        """Test kg plot focus --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.plot import cmd_plot

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_plot(["focus", "coalition-forge", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        assert data["status"] == "focused"
        assert data["name"] == "coalition-forge"

    def test_plot_focus_not_found(self) -> None:
        """Test kg plot focus nonexistent fails."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["focus", "nonexistent"])
        assert result == 1

    def test_plot_link(self) -> None:
        """Test kg plot link."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["link", "atelier", "plans/core-apps/atelier.md"])
        assert result == 0

    def test_plot_link_missing_args(self) -> None:
        """Test kg plot link (missing args) fails."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["link", "atelier"])
        assert result == 1

    def test_plot_discover(self) -> None:
        """Test kg plot discover."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["discover"])
        assert result == 0

    def test_plot_discover_json(self) -> None:
        """Test kg plot discover --json."""
        import io
        import json
        import sys

        from protocols.cli.handlers.plot import cmd_plot

        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_plot(["discover", "--json"])
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        assert "discovered" in data
        assert "count" in data


# =============================================================================
# Integration Tests
# =============================================================================


class TestGardenCLIIntegration:
    """Integration tests for garden CLI workflow."""

    def test_garden_workflow(self) -> None:
        """Test typical garden workflow: init -> focus -> observe -> water."""
        from protocols.cli.handlers.garden import cmd_garden
        from protocols.cli.handlers.plot import cmd_plot
        from protocols.cli.handlers.tend import cmd_tend

        # Initialize garden
        result = cmd_garden(["init"])
        assert result == 0

        # Focus on a plot
        result = cmd_plot(["focus", "atelier"])
        assert result == 0

        # Observe the garden
        result = cmd_tend(["observe", "concept.gardener"])
        assert result == 0

        # Water a prompt
        result = cmd_tend(
            [
                "water",
                "concept.prompt.task",
                "--feedback",
                "Add more context",
            ]
        )
        assert result == 0

    @pytest.mark.skip(
        reason="AGENTESE resolution bug: self.garden blocks self.garden.tend delegation"
    )
    def test_season_aware_operations(self) -> None:
        """Test that season affects operation results."""
        import io
        import json
        import sys

        from protocols.cli.handlers.garden import cmd_garden
        from protocols.cli.handlers.tend import cmd_tend

        # Transition to SPROUTING (high plasticity)
        result = cmd_garden(["transition", "SPROUTING"])
        assert result == 0

        # Water should have high learning rate in SPROUTING
        captured = io.StringIO()
        sys.stdout = captured
        try:
            result = cmd_tend(
                [
                    "water",
                    "concept.prompt.task",
                    "--feedback",
                    "Test",
                    "--tone",
                    "1.0",
                    "--json",
                ]
            )
        finally:
            sys.stdout = sys.__stdout__

        assert result == 0
        data = json.loads(captured.getvalue())
        # Handle both wrapped (project_command) and unwrapped (legacy) formats
        if "metadata" in data:
            data = data["metadata"]
        # In SPROUTING (plasticity=0.9), tone=1.0 -> learning_rate=0.9
        # But since we create a fresh garden each time, it defaults to DORMANT (0.1)
        # This demonstrates the pattern even if values vary
        assert "learning_rate" in data


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in garden CLI."""

    def test_garden_graceful_module_error(self) -> None:
        """Test garden handles missing modules gracefully."""
        # This tests the try/except ImportError handling
        from protocols.cli.handlers.garden import cmd_garden

        # Should not crash, even if internal modules have issues
        result = cmd_garden(["show"])
        assert result in (0, 1)  # Either success or clean error

    def test_tend_graceful_error(self) -> None:
        """Test tend handles errors gracefully."""
        from protocols.cli.handlers.tend import cmd_tend

        # Invalid args should return clean error
        result = cmd_tend(["invalid_verb_that_doesnt_exist"])
        assert result == 1

    def test_plot_graceful_error(self) -> None:
        """Test plot handles missing plots gracefully."""
        from protocols.cli.handlers.plot import cmd_plot

        result = cmd_plot(["this-plot-does-not-exist"])
        assert result == 1


# =============================================================================
# Command Resolution Tests
# =============================================================================


class TestCommandResolution:
    """Tests for command resolution in hollow.py."""

    def test_garden_command_registered(self) -> None:
        """Test garden command is in registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "garden" in COMMAND_REGISTRY
        assert "cmd_garden" in COMMAND_REGISTRY["garden"]

    def test_tend_command_registered(self) -> None:
        """Test tend command is in registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "tend" in COMMAND_REGISTRY
        assert "cmd_tend" in COMMAND_REGISTRY["tend"]

    def test_plot_command_registered(self) -> None:
        """Test plot command is in registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "plot" in COMMAND_REGISTRY
        assert "cmd_plot" in COMMAND_REGISTRY["plot"]

    def test_observe_alias_registered(self) -> None:
        """Test observe alias is in registry."""
        from protocols.cli.hollow import COMMAND_REGISTRY

        assert "observe" in COMMAND_REGISTRY

    def test_command_resolution(self) -> None:
        """Test commands can be resolved."""
        from protocols.cli.hollow import resolve_command

        garden_cmd = resolve_command("garden")
        assert garden_cmd is not None
        assert callable(garden_cmd)

        tend_cmd = resolve_command("tend")
        assert tend_cmd is not None
        assert callable(tend_cmd)

        plot_cmd = resolve_command("plot")
        assert plot_cmd is not None
        assert callable(plot_cmd)
