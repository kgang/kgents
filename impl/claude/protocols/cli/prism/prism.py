"""
Prism - Auto-constructive CLI from agent introspection.

The Prism reflects an agent's exposed methods into a CLI parser,
using type hints to generate argument specifications automatically.

See: spec/protocols/prism.md
"""

from __future__ import annotations

import argparse
import inspect
import json
from typing import TYPE_CHECKING, Any, Callable, get_type_hints

from .decorator import get_expose_meta
from .type_mapping import TypeRegistry

if TYPE_CHECKING:
    from .protocol import CLICapable


class Prism:
    """
    Auto-construct argparse from CLICapable agents.

    The Prism uses Python introspection to:
    1. Discover exposed commands via get_exposed_commands()
    2. Extract type hints from method signatures
    3. Map type hints to argparse argument configurations
    4. Handle sync/async methods transparently

    Example:
        cli = GrammarianCLI()
        prism = Prism(cli)
        exit_code = prism.dispatch_sync(["reify", "Calendar Management"])
    """

    def __init__(self, agent: CLICapable):
        """
        Initialize Prism with a CLICapable agent.

        Args:
            agent: An object implementing the CLICapable protocol.
        """
        self.agent = agent
        self._parser: argparse.ArgumentParser | None = None

    def build_parser(self) -> argparse.ArgumentParser:
        """
        Generate argparse.ArgumentParser from agent introspection.

        Creates a parser with:
        - Main parser named after genus
        - Subparsers for each exposed command
        - Arguments derived from method signatures

        Returns:
            Configured ArgumentParser ready for parsing.
        """
        if self._parser is not None:
            return self._parser

        # Main parser
        self._parser = argparse.ArgumentParser(
            prog=f"kgents {self.agent.genus_name}",
            description=self.agent.cli_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Create subparsers for commands
        subparsers = self._parser.add_subparsers(
            dest="command",
            title="commands",
            metavar="<command>",
        )

        # Add each exposed command
        commands = self.agent.get_exposed_commands()
        for name, method in commands.items():
            meta = get_expose_meta(method)

            # Even without @expose, we can still add the command
            help_text = meta.help if meta else f"Execute {name}"
            hidden = meta.hidden if meta else False

            if hidden:
                continue

            # Create subparser for this command
            epilog = None
            if meta and meta.examples:
                epilog = "Examples:\n  " + "\n  ".join(meta.examples)

            cmd_parser = subparsers.add_parser(
                name,
                help=help_text,
                description=method.__doc__,
                epilog=epilog,
                formatter_class=argparse.RawDescriptionHelpFormatter,
            )

            # Add format option to each subcommand
            cmd_parser.add_argument(
                "--format",
                choices=["rich", "json"],
                default="rich",
                help="Output format (default: rich)",
            )

            # Add aliases if specified
            if meta and meta.aliases:
                for alias in meta.aliases:
                    subparsers.add_parser(
                        alias,
                        help=f"Alias for {name}",
                        parents=[cmd_parser],
                        add_help=False,
                    )

            # Add arguments from method signature
            self._add_arguments(cmd_parser, method)

        return self._parser

    def _add_arguments(self, parser: argparse.ArgumentParser, method: Callable[..., Any]) -> None:
        """
        Add argparse arguments from method signature.

        Analyzes the method's type hints and signature to generate
        appropriate argparse arguments.

        Args:
            parser: The subparser to add arguments to.
            method: The method to analyze.
        """
        try:
            hints = get_type_hints(method)
        except Exception:
            hints = {}

        sig = inspect.signature(method)

        for param_name, param in sig.parameters.items():
            # Skip self, cls, and return type marker
            if param_name in ("self", "cls", "return"):
                continue

            # Skip **kwargs and *args
            if param.kind in (
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ):
                continue

            # Get type hint
            param_type = hints.get(param_name, str)
            has_default = param.default is not inspect.Parameter.empty
            default_value = param.default if has_default else None

            # Get argparse kwargs from type mapping
            kwargs = TypeRegistry.map(param_type, has_default=has_default)

            # Handle boolean flags specially
            is_bool = TypeRegistry.is_flag_type(param_type)

            # Determine if positional or optional
            is_optional = has_default or TypeRegistry.is_optional(param_type)

            if is_bool:
                # Boolean flags are always optional with --prefix
                parser.add_argument(
                    f"--{param_name}",
                    action="store_true",
                    default=default_value if has_default else False,
                    help=f"Enable {param_name}",
                )
            elif is_optional:
                # Optional arguments get -- prefix
                kwargs["default"] = default_value
                kwargs.pop("required", None)  # Optional args aren't required

                # Don't pass action for non-bool types
                kwargs.pop("action", None)

                parser.add_argument(f"--{param_name}", **kwargs)
            else:
                # Required positional arguments
                # Remove keys that don't apply to positionals
                kwargs.pop("required", None)
                kwargs.pop("default", None)
                kwargs.pop("action", None)

                parser.add_argument(param_name, **kwargs)

    async def dispatch(self, args: list[str]) -> int:
        """
        Parse arguments and invoke the appropriate method.

        Handles:
        - Argument parsing with generated parser
        - Sync vs async method detection
        - Result formatting (JSON or rich)
        - Error handling with exit codes

        Args:
            args: Command line arguments (without program name).

        Returns:
            Exit code (0 for success, non-zero for errors).
        """
        parser = self.build_parser()

        # Handle help for main command
        if not args or args[0] in ("--help", "-h"):
            parser.print_help()
            return 0

        try:
            parsed = parser.parse_args(args)
        except SystemExit as e:
            # argparse calls sys.exit on error
            return e.code if isinstance(e.code, int) else 1

        # Check if a command was specified
        if not parsed.command:
            parser.print_help()
            return 0

        # Get the method to call
        commands = self.agent.get_exposed_commands()

        # Handle aliases - check if this is an alias
        method = commands.get(parsed.command)
        if method is None:
            # Check aliases
            for name, m in commands.items():
                meta = get_expose_meta(m)
                if meta and parsed.command in meta.aliases:
                    method = m
                    break

        if method is None:
            print(f"Unknown command: {parsed.command}")
            return 1

        # Extract kwargs (excluding parser metadata)
        kwargs = {
            k: v
            for k, v in vars(parsed).items()
            if k not in ("command", "format") and v is not None
        }

        # Handle empty list defaults
        sig = inspect.signature(method)
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if param_name not in kwargs:
                if param.default is not inspect.Parameter.empty:
                    kwargs[param_name] = param.default

        try:
            # Call the method (handle sync/async)
            if inspect.iscoroutinefunction(method):
                result = await method(**kwargs)
            else:
                result = method(**kwargs)

            # Format output
            output_format = getattr(parsed, "format", "rich")
            self._output_result(result, output_format)

            return 0

        except KeyboardInterrupt:
            print("\n  Interrupted.")
            return 130
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def dispatch_sync(self, args: list[str]) -> int:
        """
        Synchronous wrapper for dispatch.

        Use this in CLI entry points where async isn't available.

        Args:
            args: Command line arguments.

        Returns:
            Exit code from dispatch.
        """
        import asyncio

        return asyncio.run(self.dispatch(args))

    def _output_result(self, result: Any, format: str) -> None:
        """
        Output the result in the requested format.

        Args:
            result: The result from the method call.
            format: Either "json" or "rich".
        """
        if result is None:
            return

        if format == "json":
            if isinstance(result, dict):
                print(json.dumps(result, indent=2, default=str))
            elif isinstance(result, list):
                print(json.dumps(result, indent=2, default=str))
            else:
                print(json.dumps({"result": str(result)}, indent=2))
        else:
            # Rich format - pretty print
            if isinstance(result, dict):
                self._print_dict_rich(result)
            elif isinstance(result, list):
                self._print_list_rich(result)
            else:
                print(result)

    def _print_dict_rich(self, data: dict[str, Any], indent: int = 0) -> None:
        """Pretty print a dictionary."""
        prefix = "  " * indent
        print()
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{prefix}  {key}:")
                self._print_dict_rich(value, indent + 2)
            elif isinstance(value, list):
                print(f"{prefix}  {key}:")
                for item in value[:10]:
                    print(f"{prefix}    - {item}")
                if len(value) > 10:
                    print(f"{prefix}    ... and {len(value) - 10} more")
            else:
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 100:
                    str_value = str_value[:100] + "..."
                print(f"{prefix}  {key}: {str_value}")
        print()

    def _print_list_rich(self, data: list[Any]) -> None:
        """Pretty print a list."""
        print()
        for i, item in enumerate(data[:20]):
            if isinstance(item, dict):
                # Print first few keys
                summary = ", ".join(f"{k}={v}" for k, v in list(item.items())[:3])
                print(f"  [{i + 1}] {summary}")
            else:
                print(f"  [{i + 1}] {item}")
        if len(data) > 20:
            print(f"  ... and {len(data) - 20} more")
        print()
