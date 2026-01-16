"""
Tests for the unified help template system.

These tests verify:
1. HelpSpec creation and serialization
2. Plain text rendering
3. JSON rendering
4. Decorator functionality
5. Helper functions
"""

from __future__ import annotations

import json

import pytest

from protocols.cli.help_template import (
    BRAIN_HELP_EXAMPLE,
    COMMON_FLAGS,
    DOCS_HELP_EXAMPLE,
    HelpSpec,
    OutputMode,
    help_spec,
    make_common_spec,
    render_command_help,
    render_help,
    show_help_for,
    with_help,
)


class TestHelpSpec:
    """Tests for HelpSpec dataclass."""

    def test_create_basic_spec(self) -> None:
        """Can create a basic HelpSpec."""
        spec = HelpSpec(
            name="test",
            description="A test command",
            usage="kg test [options]",
        )

        assert spec.name == "test"
        assert spec.description == "A test command"
        assert spec.usage == "kg test [options]"
        assert spec.philosophy is None
        assert spec.subcommands == ()
        assert spec.flags == ()
        assert spec.examples == ()

    def test_create_full_spec(self) -> None:
        """Can create a fully populated HelpSpec."""
        spec = HelpSpec(
            name="full",
            description="A full test command",
            usage="kg full [action] [options]",
            philosophy="Test philosophy",
            subcommands=(("action1", "First action"),),
            flags=(("--flag", "type", "Description"),),
            examples=("kg full action1",),
            agentese_paths=("test.path",),
            related=("other",),
            footer="Test footer",
        )

        assert spec.name == "full"
        assert spec.philosophy == "Test philosophy"
        assert len(spec.subcommands) == 1
        assert len(spec.flags) == 1
        assert len(spec.examples) == 1
        assert len(spec.agentese_paths) == 1
        assert len(spec.related) == 1
        assert spec.footer == "Test footer"

    def test_spec_is_immutable(self) -> None:
        """HelpSpec is frozen (immutable)."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
        )

        with pytest.raises(AttributeError):
            spec.name = "changed"  # type: ignore[misc]

    def test_to_dict(self) -> None:
        """HelpSpec can be converted to dict."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            subcommands=(("cmd", "Command"),),
            flags=(("--flag", "str", "Flag desc"),),
            examples=("kg test cmd",),
        )

        d = spec.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test"
        assert d["usage"] == "kg test"
        assert len(d["subcommands"]) == 1
        assert d["subcommands"][0]["name"] == "cmd"
        assert d["subcommands"][0]["description"] == "Command"
        assert len(d["flags"]) == 1
        assert d["flags"][0]["flag"] == "--flag"
        assert d["flags"][0]["type"] == "str"
        assert len(d["examples"]) == 1


class TestRenderHelp:
    """Tests for render_help function."""

    def test_render_plain(self) -> None:
        """Renders plain text correctly."""
        spec = HelpSpec(
            name="test",
            description="A test command",
            usage="kg test [options]",
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "kg test - A test command" in output
        assert "USAGE" in output
        assert "kg test [options]" in output

    def test_render_plain_with_philosophy(self) -> None:
        """Philosophy quote appears in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            philosophy="Test philosophy quote",
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert '"Test philosophy quote"' in output

    def test_render_plain_with_subcommands(self) -> None:
        """Subcommands table appears in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            subcommands=(
                ("action1", "First action"),
                ("action2", "Second action"),
            ),
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "COMMANDS" in output
        assert "action1" in output
        assert "First action" in output
        assert "action2" in output
        assert "Second action" in output

    def test_render_plain_with_flags(self) -> None:
        """Flags table appears in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            flags=(
                ("--help", "", "Show help"),
                ("--output", "path", "Output directory"),
            ),
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "OPTIONS" in output
        assert "--help" in output
        assert "Show help" in output
        assert "--output" in output
        assert "<path>" in output

    def test_render_plain_with_examples(self) -> None:
        """Examples appear in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            examples=(
                "kg test run",
                "kg test check --verbose",
            ),
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "EXAMPLES" in output
        assert "$ kg test run" in output
        assert "$ kg test check --verbose" in output

    def test_render_plain_with_agentese_paths(self) -> None:
        """AGENTESE paths appear in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            agentese_paths=(
                "test.path.one",
                "test.path.two",
            ),
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "AGENTESE PATHS" in output
        assert "test.path.one" in output
        assert "test.path.two" in output

    def test_render_plain_with_related(self) -> None:
        """Related commands appear in plain output."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            related=("other", "another"),
        )

        output = render_help(spec, mode=OutputMode.PLAIN)

        assert "SEE ALSO" in output
        assert "kg other" in output
        assert "kg another" in output

    def test_render_json(self) -> None:
        """Renders valid JSON."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
            subcommands=(("cmd", "Command"),),
        )

        output = render_help(spec, mode=OutputMode.JSON)

        # Should be valid JSON
        data = json.loads(output)

        assert data["name"] == "test"
        assert data["description"] == "Test"
        assert len(data["subcommands"]) == 1


class TestRenderCommandHelp:
    """Tests for render_command_help function."""

    def test_render_command_help_basic(self, capsys: pytest.CaptureFixture[str]) -> None:
        """render_command_help prints to stdout."""
        render_command_help(
            name="test",
            description="A test command",
            usage="kg test",
        )

        captured = capsys.readouterr()
        assert "kg test - A test command" in captured.out
        assert "USAGE" in captured.out

    def test_render_command_help_full(self, capsys: pytest.CaptureFixture[str]) -> None:
        """render_command_help handles all options."""
        render_command_help(
            name="test",
            description="Test",
            usage="kg test [options]",
            subcommands=[("cmd", "Command")],
            flags=[("--flag", "type", "Description")],
            examples=["kg test cmd"],
            agentese_paths=["test.path"],
            philosophy="Test philosophy",
            related=["other"],
            footer="Test footer",
        )

        captured = capsys.readouterr()
        assert '"Test philosophy"' in captured.out
        assert "COMMANDS" in captured.out
        assert "OPTIONS" in captured.out
        assert "EXAMPLES" in captured.out
        assert "AGENTESE PATHS" in captured.out
        assert "SEE ALSO" in captured.out
        assert "Test footer" in captured.out


class TestDecorators:
    """Tests for decorator functions."""

    def test_help_spec_decorator(self) -> None:
        """@help_spec attaches spec to function."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
        )

        @help_spec(spec)
        def my_func(args: list[str], ctx: None = None) -> int:
            return 0

        assert hasattr(my_func, "_help_spec")
        assert my_func._help_spec == spec  # type: ignore[attr-defined]

    def test_show_help_for(self, capsys: pytest.CaptureFixture[str]) -> None:
        """show_help_for prints help from attached spec."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
        )

        @help_spec(spec)
        def my_func(args: list[str], ctx: None = None) -> int:
            return 0

        result = show_help_for(my_func)

        assert result == 0
        captured = capsys.readouterr()
        assert "kg test - Test" in captured.out

    def test_show_help_for_no_spec(self, capsys: pytest.CaptureFixture[str]) -> None:
        """show_help_for returns 1 if no spec attached."""

        def my_func(args: list[str], ctx: None = None) -> int:
            return 0

        result = show_help_for(my_func)

        assert result == 1
        captured = capsys.readouterr()
        assert "No help available" in captured.out

    def test_with_help_decorator_handles_help_flag(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """@with_help decorator handles --help flag."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
        )

        @with_help(spec)
        def my_func(args: list[str], ctx: None = None) -> int:
            print("Function executed")
            return 42

        # Test --help
        result = my_func(["--help"])
        assert result == 0
        captured = capsys.readouterr()
        assert "kg test - Test" in captured.out
        assert "Function executed" not in captured.out

        # Test -h
        result = my_func(["-h"])
        assert result == 0

    def test_with_help_decorator_normal_execution(self, capsys: pytest.CaptureFixture[str]) -> None:
        """@with_help decorator passes through normal execution."""
        spec = HelpSpec(
            name="test",
            description="Test",
            usage="kg test",
        )

        @with_help(spec)
        def my_func(args: list[str], ctx: None = None) -> int:
            print(f"Args: {args}")
            return 42

        result = my_func(["arg1", "arg2"])

        assert result == 42
        captured = capsys.readouterr()
        assert "Args: ['arg1', 'arg2']" in captured.out


class TestMakeCommonSpec:
    """Tests for make_common_spec helper."""

    def test_includes_common_flags(self) -> None:
        """make_common_spec includes standard flags."""
        spec = make_common_spec(
            name="test",
            description="Test",
            usage="kg test",
        )

        flag_names = [f[0] for f in spec.flags]
        assert "--help, -h" in flag_names
        assert "--json" in flag_names
        assert "--trace" in flag_names

    def test_adds_extra_flags(self) -> None:
        """make_common_spec adds extra flags after common ones."""
        spec = make_common_spec(
            name="test",
            description="Test",
            usage="kg test",
            extra_flags=[
                ("--custom", "value", "Custom flag"),
            ],
        )

        flag_names = [f[0] for f in spec.flags]
        assert "--custom" in flag_names
        # Common flags should still be present
        assert "--help, -h" in flag_names


class TestExampleSpecs:
    """Tests for pre-built example specs."""

    def test_brain_help_example_renders(self) -> None:
        """BRAIN_HELP_EXAMPLE renders without error."""
        output = render_help(BRAIN_HELP_EXAMPLE, mode=OutputMode.PLAIN)

        assert "brain" in output
        assert "memory" in output.lower()

    def test_docs_help_example_renders(self) -> None:
        """DOCS_HELP_EXAMPLE renders without error."""
        output = render_help(DOCS_HELP_EXAMPLE, mode=OutputMode.PLAIN)

        assert "docs" in output
        assert "documentation" in output.lower()

    def test_example_specs_have_all_sections(self) -> None:
        """Example specs have populated sections."""
        assert BRAIN_HELP_EXAMPLE.philosophy is not None
        assert len(BRAIN_HELP_EXAMPLE.subcommands) > 0
        assert len(BRAIN_HELP_EXAMPLE.flags) > 0
        assert len(BRAIN_HELP_EXAMPLE.examples) > 0
        assert len(BRAIN_HELP_EXAMPLE.agentese_paths) > 0
        assert len(BRAIN_HELP_EXAMPLE.related) > 0
        assert BRAIN_HELP_EXAMPLE.footer is not None


class TestCommonFlags:
    """Tests for COMMON_FLAGS constant."""

    def test_common_flags_includes_help(self) -> None:
        """COMMON_FLAGS includes --help."""
        flag_names = [f[0] for f in COMMON_FLAGS]
        assert any("--help" in f for f in flag_names)

    def test_common_flags_includes_json(self) -> None:
        """COMMON_FLAGS includes --json."""
        flag_names = [f[0] for f in COMMON_FLAGS]
        assert any("--json" in f for f in flag_names)

    def test_common_flags_includes_trace(self) -> None:
        """COMMON_FLAGS includes --trace."""
        flag_names = [f[0] for f in COMMON_FLAGS]
        assert any("--trace" in f for f in flag_names)
