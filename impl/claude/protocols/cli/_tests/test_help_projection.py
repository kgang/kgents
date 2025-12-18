"""
Tests for Help Projection System (Wave 3).

Tests that help is correctly derived from AGENTESE affordances.
"""

from __future__ import annotations

import pytest


class TestHelpProjector:
    """Tests for HelpProjector."""

    def test_project_node_returns_command_help(self) -> None:
        """Projecting a node path returns CommandHelp structure."""
        from protocols.cli.help_projector import CommandHelp, create_help_projector

        projector = create_help_projector()
        result = projector.project("self.memory")

        assert isinstance(result, CommandHelp)
        assert result.path == "self.memory"
        assert result.title  # Has a title
        assert isinstance(result.usage, list)
        assert isinstance(result.flags, list)

    def test_project_derives_title(self) -> None:
        """Title is derived from NODE_TITLES mapping."""
        from protocols.cli.help_projector import create_help_projector

        projector = create_help_projector()
        result = projector.project("self.memory")

        # Should include "Brain" in title
        assert "Brain" in result.title

    def test_project_includes_common_flags(self) -> None:
        """Common flags are always included."""
        from protocols.cli.help_projector import create_help_projector

        projector = create_help_projector()
        result = projector.project("self.memory")

        flag_names = [f for f, _ in result.flags]
        assert "--json" in flag_names
        assert "--help, -h" in flag_names

    def test_project_unknown_path_returns_fallback(self) -> None:
        """Unknown paths return a basic CommandHelp."""
        from protocols.cli.help_projector import create_help_projector

        projector = create_help_projector()
        result = projector.project("unknown.path")

        assert result.path == "unknown.path"
        # Should still have basic structure
        assert isinstance(result.flags, list)


class TestHelpRenderer:
    """Tests for HelpRenderer."""

    def test_render_plain_produces_text(self) -> None:
        """Plain rendering produces readable text."""
        from protocols.cli.help_projector import CommandHelp
        from protocols.cli.help_renderer import render_help

        help_obj = CommandHelp(
            path="test.path",
            title="Test Command",
            description="A test command",
            usage=["kg test action"],
            flags=[("--flag", "A flag")],
            examples=["kg test example"],
        )

        result = render_help(help_obj, use_rich=False)

        assert "Test Command" in result
        assert "test.path" in result
        assert "A test command" in result
        assert "kg test action" in result
        assert "--flag" in result

    def test_render_json_produces_valid_json(self) -> None:
        """JSON rendering produces valid JSON."""
        import json

        from protocols.cli.help_projector import CommandHelp
        from protocols.cli.help_renderer import render_help

        help_obj = CommandHelp(
            path="test.path",
            title="Test Command",
            description="A test command",
        )

        result = render_help(help_obj, json_output=True)
        parsed = json.loads(result)

        assert parsed["path"] == "test.path"
        assert parsed["title"] == "Test Command"
        assert parsed["description"] == "A test command"

    def test_render_command_list_plain(self) -> None:
        """Command list rendering works."""
        from protocols.cli.help_renderer import render_command_list

        commands = [
            ("brain", "self.memory", "Memory operations"),
            ("soul", "self.soul", "Soul operations"),
        ]

        result = render_command_list(commands, use_rich=False)

        assert "brain" in result
        assert "soul" in result
        assert "self.memory" in result


class TestGlobalHelp:
    """Tests for global help output."""

    def test_global_help_includes_crown_jewels(self) -> None:
        """Global help includes Crown Jewels family."""
        from protocols.cli.help_global import render_global_help

        result = render_global_help(use_rich=False)

        assert "Crown Jewels" in result
        assert "brain" in result
        assert "soul" in result
        assert "town" in result

    def test_global_help_includes_forest(self) -> None:
        """Global help includes Forest Protocol family."""
        from protocols.cli.help_global import render_global_help

        result = render_global_help(use_rich=False)

        assert "Forest Protocol" in result
        assert "forest" in result
        assert "garden" in result

    def test_global_help_includes_joy(self) -> None:
        """Global help includes Joy Commands family."""
        from protocols.cli.help_global import render_global_help

        result = render_global_help(use_rich=False)

        assert "Joy Commands" in result
        assert "oblique" in result

    def test_global_help_includes_examples(self) -> None:
        """Global help includes example commands."""
        from protocols.cli.help_global import render_global_help

        result = render_global_help(use_rich=False)

        assert "Examples" in result
        assert "kg brain capture" in result

    def test_show_global_help_returns_zero(self) -> None:
        """show_global_help returns exit code 0."""
        import io
        import sys

        from protocols.cli.help_global import show_global_help

        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = show_global_help()
        finally:
            sys.stdout = old_stdout

        assert result == 0
        assert len(captured.getvalue()) > 0


class TestPathToCommandMapping:
    """Tests for path <-> command mappings."""

    def test_path_to_command_known_paths(self) -> None:
        """Known paths map to correct commands."""
        from protocols.cli.help_projector import PATH_TO_COMMAND

        assert PATH_TO_COMMAND["self.memory"] == "brain"
        assert PATH_TO_COMMAND["self.soul"] == "soul"
        assert PATH_TO_COMMAND["world.town"] == "town"

    def test_node_titles_have_entries(self) -> None:
        """NODE_TITLES has entries for known nodes."""
        from protocols.cli.help_projector import NODE_TITLES

        assert "self.memory" in NODE_TITLES
        assert "self.soul" in NODE_TITLES
        assert "world.town" in NODE_TITLES

    def test_node_emojis_match_titles(self) -> None:
        """NODE_EMOJIS has entries matching NODE_TITLES."""
        from protocols.cli.help_projector import NODE_EMOJIS, NODE_TITLES

        for path in NODE_TITLES:
            assert path in NODE_EMOJIS, f"Missing emoji for {path}"


class TestHelpProjectorIntegration:
    """Integration tests for help projection."""

    def test_full_help_flow(self) -> None:
        """Full flow from path to rendered help."""
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project("self.memory")
        rendered = render_help(help_obj, use_rich=False)

        # Should have all expected sections
        assert "Brain" in rendered
        assert "self.memory" in rendered
        assert "Commands:" in rendered or "kg" in rendered
        assert "Flags:" in rendered
        assert "--json" in rendered

    def test_help_for_nested_path(self) -> None:
        """Help works for nested paths like self.forest.garden."""
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project("self.forest.garden")
        rendered = render_help(help_obj, use_rich=False)

        assert help_obj.path == "self.forest.garden"
        assert len(rendered) > 0
