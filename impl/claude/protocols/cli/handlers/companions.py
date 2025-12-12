"""
Daily Companion Commands - Tier 1 (0 tokens).

These are lightweight commands for daily use:
- pulse: 1-line project health
- ground: Parse statement and reflect structure
- breathe: Contemplative pause
- entropy: Show session chaos budget
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import cast


def _parse_args_simple(
    args: list[str], positional: str | None = None
) -> tuple[dict[str, object], str | None]:
    """
    Simple argument parser for companion commands.

    Returns (options, positional_value).
    """
    options = {
        "help": False,
        "format": "rich",
    }
    positional_value = None

    for i, arg in enumerate(args):
        if arg in ("--help", "-h"):
            options["help"] = True
        elif arg.startswith("--format="):
            options["format"] = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            positional_value = arg

    return options, positional_value


def _print_help(command: str, description: str, usage: str) -> None:
    """Print help for a companion command."""
    print(f"kgents {command} - {description}")
    print()
    print(f"USAGE: {usage}")
    print()
    print("OPTIONS:")
    print("  --format=FORMAT  Output format (rich, json)")
    print("  --help, -h       Show this help")


# =============================================================================
# pulse
# =============================================================================


def cmd_pulse(args: list[str]) -> int:
    """Handle pulse command: 1-line project health."""
    options, path_arg = _parse_args_simple(args, "path")

    if options["help"]:
        _print_help(
            "pulse",
            "1-line project health (0 tokens)",
            "kgents pulse [path]",
        )
        return 0

    path = Path(path_arg).expanduser().resolve() if path_arg else Path.cwd()

    # Late import - this is the lazy loading in action
    from protocols.cli.cli_types import (
        BudgetLevel,
        BudgetStatus,
        CLIContext,
        OutputFormat,
    )
    from protocols.cli.companions import CompanionsCLI

    async def run() -> int:
        ctx = CLIContext(
            output_format=OutputFormat(options["format"]),
            budget=BudgetStatus.from_level(BudgetLevel.MINIMAL),
        )
        cli = CompanionsCLI()
        result = await cli.pulse(path, ctx)

        if result.success and result.output:
            print(result.output.render())
        else:
            print(f"Error: {result.error}")

        return cast(int, result.exit_code)

    return asyncio.run(run())


# =============================================================================
# ground
# =============================================================================


def cmd_ground(args: list[str]) -> int:
    """Handle ground command: Parse statement and reflect structure."""
    options, statement = _parse_args_simple(args, "statement")

    if options["help"]:
        _print_help(
            "ground",
            "Parse statement and reflect structure (0 tokens)",
            'kgents ground "<statement>"',
        )
        return 0

    if not statement:
        print("Error: statement required")
        print('Usage: kgents ground "<statement>"')
        return 1

    from protocols.cli.cli_types import (
        BudgetLevel,
        BudgetStatus,
        CLIContext,
        OutputFormat,
    )
    from protocols.cli.companions import CompanionsCLI

    async def run() -> int:
        ctx = CLIContext(
            output_format=OutputFormat(options["format"]),
            budget=BudgetStatus.from_level(BudgetLevel.MINIMAL),
        )
        cli = CompanionsCLI()
        result = await cli.ground(statement, ctx)

        if result.success and result.output:
            print(result.output.render())
        else:
            print(f"Error: {result.error}")

        return cast(int, result.exit_code)

    return asyncio.run(run())


# =============================================================================
# breathe
# =============================================================================


def cmd_breathe(args: list[str]) -> int:
    """Handle breathe command: Contemplative pause."""
    options, _ = _parse_args_simple(args)

    if options["help"]:
        _print_help(
            "breathe",
            "Contemplative pause with gentle prompt (0 tokens)",
            "kgents breathe",
        )
        return 0

    from protocols.cli.cli_types import (
        BudgetLevel,
        BudgetStatus,
        CLIContext,
        OutputFormat,
    )
    from protocols.cli.companions import CompanionsCLI

    async def run() -> int:
        ctx = CLIContext(
            output_format=OutputFormat(options["format"]),
            budget=BudgetStatus.from_level(BudgetLevel.MINIMAL),
        )
        cli = CompanionsCLI()
        result = await cli.breathe(ctx)

        if result.success and result.output:
            print(result.output)
        else:
            print(f"Error: {result.error}")

        return cast(int, result.exit_code)

    return asyncio.run(run())


# =============================================================================
# entropy
# =============================================================================


def cmd_entropy(args: list[str]) -> int:
    """Handle entropy command: Show session chaos budget."""
    options, path_arg = _parse_args_simple(args, "path")

    if options["help"]:
        _print_help(
            "entropy",
            "Show session entropy/chaos budget (0 tokens)",
            "kgents entropy [path]",
        )
        return 0

    path = Path(path_arg).expanduser().resolve() if path_arg else Path.cwd()

    from protocols.cli.cli_types import (
        BudgetLevel,
        BudgetStatus,
        CLIContext,
        OutputFormat,
    )
    from protocols.cli.companions import CompanionsCLI

    async def run() -> int:
        ctx = CLIContext(
            output_format=OutputFormat(options["format"]),
            budget=BudgetStatus.from_level(BudgetLevel.MINIMAL),
        )
        cli = CompanionsCLI()
        result = await cli.entropy(path, ctx)

        if result.success and result.output:
            print(result.output.render())
        else:
            print(f"Error: {result.error}")

        return cast(int, result.exit_code)

    return asyncio.run(run())
