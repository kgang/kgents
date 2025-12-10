"""Tests for Prism auto-constructor."""

from __future__ import annotations

import io
import sys
from typing import Callable

import pytest

from protocols.cli.prism import CLICapable, Prism, expose


class MockAgent:
    """Mock agent for testing Prism."""

    @property
    def genus_name(self) -> str:
        return "mock"

    @property
    def cli_description(self) -> str:
        return "Mock agent for testing"

    def get_exposed_commands(self) -> dict[str, Callable]:
        return {
            "greet": self.greet,
            "add": self.add,
            "echo": self.echo,
            "async_cmd": self.async_cmd,
        }

    @expose(help="Greet someone", examples=["kgents mock greet Alice"])
    def greet(self, name: str, loud: bool = False) -> dict:
        """Greet a person by name."""
        greeting = f"Hello, {name}!"
        if loud:
            greeting = greeting.upper()
        return {"greeting": greeting}

    @expose(help="Add two numbers")
    def add(self, a: int, b: int = 0) -> dict:
        """Add two integers."""
        return {"result": a + b}

    @expose(help="Echo a message")
    def echo(self, message: str, count: int = 1) -> dict:
        """Echo a message multiple times."""
        return {"messages": [message] * count}

    @expose(help="Async command")
    async def async_cmd(self, value: str) -> dict:
        """An async command."""
        return {"async_value": value}


class TestPrismInit:
    """Tests for Prism initialization."""

    def test_init_with_cli_capable(self):
        """Prism accepts CLICapable agent."""
        agent = MockAgent()
        prism = Prism(agent)

        assert prism.agent is agent
        assert prism._parser is None

    def test_isinstance_check(self):
        """MockAgent satisfies CLICapable."""
        agent = MockAgent()
        assert isinstance(agent, CLICapable)


class TestPrismBuildParser:
    """Tests for build_parser method."""

    def test_build_parser_creates_parser(self):
        """build_parser creates an ArgumentParser."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        assert parser is not None
        assert parser.prog == "kgents mock"

    def test_build_parser_cached(self):
        """build_parser returns same parser on subsequent calls."""
        prism = Prism(MockAgent())
        parser1 = prism.build_parser()
        parser2 = prism.build_parser()

        assert parser1 is parser2

    def test_parser_has_format_option(self):
        """Parser includes --format option."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        # Parse with format option
        args = parser.parse_args(["greet", "Alice", "--format", "json"])
        assert args.format == "json"

    def test_parser_has_subcommands(self):
        """Parser has subcommands for exposed methods."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        # Should be able to parse each command
        args = parser.parse_args(["greet", "Alice"])
        assert args.command == "greet"

        args = parser.parse_args(["add", "5"])
        assert args.command == "add"


class TestPrismArgumentGeneration:
    """Tests for argument generation from type hints."""

    def test_positional_required_arg(self):
        """Required args become positional."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        # 'name' is required in greet
        args = parser.parse_args(["greet", "World"])
        assert args.name == "World"

    def test_optional_arg_with_default(self):
        """Args with defaults become --options."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        # 'loud' has default=False
        args = parser.parse_args(["greet", "Alice"])
        assert args.loud is False

        args = parser.parse_args(["greet", "Alice", "--loud"])
        assert args.loud is True

    def test_int_type_conversion(self):
        """int type hints convert argument."""
        prism = Prism(MockAgent())
        parser = prism.build_parser()

        args = parser.parse_args(["add", "5", "--b", "3"])
        assert args.a == 5
        assert args.b == 3


class TestPrismDispatch:
    """Tests for dispatch method."""

    @pytest.mark.asyncio
    async def test_dispatch_sync_command(self):
        """dispatch calls sync methods correctly."""
        prism = Prism(MockAgent())
        exit_code = await prism.dispatch(["greet", "Alice", "--format", "json"])

        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_dispatch_async_command(self):
        """dispatch calls async methods correctly."""
        prism = Prism(MockAgent())
        exit_code = await prism.dispatch(["async_cmd", "test", "--format", "json"])

        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_dispatch_help(self):
        """dispatch shows help for --help."""
        prism = Prism(MockAgent())

        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            exit_code = await prism.dispatch(["--help"])
        finally:
            sys.stdout = old_stdout

        assert exit_code == 0
        output = captured.getvalue()
        assert "mock" in output.lower()

    @pytest.mark.asyncio
    async def test_dispatch_empty_args(self):
        """dispatch shows help for empty args."""
        prism = Prism(MockAgent())

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            exit_code = await prism.dispatch([])
        finally:
            sys.stdout = old_stdout

        assert exit_code == 0

    @pytest.mark.asyncio
    async def test_dispatch_unknown_command(self):
        """dispatch returns error for unknown command."""
        prism = Prism(MockAgent())

        # argparse will print error and call sys.exit
        exit_code = await prism.dispatch(["unknown_cmd"])
        assert exit_code != 0


class TestPrismDispatchSync:
    """Tests for dispatch_sync method."""

    def test_dispatch_sync_wrapper(self):
        """dispatch_sync wraps async dispatch."""
        prism = Prism(MockAgent())

        # Should work without asyncio.run
        exit_code = prism.dispatch_sync(["greet", "Alice", "--format", "json"])
        assert exit_code == 0


class TestPrismOutput:
    """Tests for output formatting."""

    @pytest.mark.asyncio
    async def test_json_output(self):
        """--format=json produces JSON output."""
        prism = Prism(MockAgent())

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await prism.dispatch(["greet", "Alice", "--format", "json"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert '"greeting"' in output
        assert "Alice" in output

    @pytest.mark.asyncio
    async def test_rich_output(self):
        """--format=rich produces formatted output."""
        prism = Prism(MockAgent())

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            await prism.dispatch(["greet", "Alice", "--format", "rich"])
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        assert "greeting" in output
        assert "Alice" in output


class TestPrismEdgeCases:
    """Tests for edge cases."""

    def test_agent_without_commands(self):
        """Prism works with agent with no commands."""

        class EmptyAgent:
            @property
            def genus_name(self) -> str:
                return "empty"

            @property
            def cli_description(self) -> str:
                return "Empty agent"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {}

        prism = Prism(EmptyAgent())
        parser = prism.build_parser()
        assert parser is not None

    def test_method_without_expose(self):
        """Methods without @expose still work."""

        class PartialAgent:
            @property
            def genus_name(self) -> str:
                return "partial"

            @property
            def cli_description(self) -> str:
                return "Partial agent"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {"bare": self.bare}

            def bare(self, arg: str) -> dict:
                return {"arg": arg}

        prism = Prism(PartialAgent())
        parser = prism.build_parser()

        args = parser.parse_args(["bare", "test"])
        assert args.arg == "test"


class TestPrismAliases:
    """Tests for command aliases."""

    def test_command_with_aliases(self):
        """Commands with aliases are accessible."""

        class AliasAgent:
            @property
            def genus_name(self) -> str:
                return "alias"

            @property
            def cli_description(self) -> str:
                return "Alias test"

            def get_exposed_commands(self) -> dict[str, Callable]:
                return {"list": self.list_items}

            @expose(help="List items", aliases=["ls", "l"])
            def list_items(self) -> dict:
                return {"items": [1, 2, 3]}

        prism = Prism(AliasAgent())
        parser = prism.build_parser()

        # Main command works
        args = parser.parse_args(["list"])
        assert args.command == "list"
