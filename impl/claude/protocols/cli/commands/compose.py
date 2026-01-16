"""
Compose Command: Chain kg operations with unified witnessing.

"Every step leaves a mark. Every composition tells a story."

Usage:
    kg compose "audit spec/foo.md --principles" "probe identity --target X"
    kg compose --save "validation" "audit X" "probe Y"
    kg compose --run "validation"
    kg compose --history
    kg compose --list

Philosophy:
    A single kg command is atomic. A composition is molecular.
    The composition trace provides the causal narrative connecting
    all steps from stimulus to outcome.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 5)
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_composition_result(
    composition: Any,
    json_mode: bool = False,
    verbose: bool = False,
) -> None:
    """Print composition result in human or JSON format."""
    from services.compose.types import CompositionStatus

    if json_mode:
        print(json.dumps(composition.to_dict(), indent=2))
        return

    # Human-readable output
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()
        use_rich = True
    except ImportError:
        console = None
        use_rich = False

    # Header
    status_color = (
        "green" if composition.all_succeeded else "red" if composition.any_failed else "yellow"
    )
    status_symbol = "✓" if composition.all_succeeded else "✗" if composition.any_failed else "⊙"

    if use_rich and console:
        title = f"{status_symbol} Composition: {composition.name or composition.id[:12]}"
        console.print(f"\n[bold {status_color}]{title}[/bold {status_color}]")
        console.print(f"[dim]Status: {composition.status.value}[/dim]")
        console.print(f"[dim]Duration: {composition.duration_ms:.0f}ms[/dim]")
        console.print(
            f"[dim]Steps: {composition.success_count} succeeded, {composition.failure_count} failed, {composition.skipped_count} skipped[/dim]"
        )
        if composition.trace_id:
            console.print(f"[dim]Trace: {composition.trace_id[:12]}...[/dim]")
        console.print()
    else:
        print(f"\n{status_symbol} Composition: {composition.name or composition.id[:12]}")
        print(f"Status: {composition.status.value}")
        print(f"Duration: {composition.duration_ms:.0f}ms")
        print(
            f"Steps: {composition.success_count} succeeded, {composition.failure_count} failed, {composition.skipped_count} skipped"
        )
        if composition.trace_id:
            print(f"Trace: {composition.trace_id[:12]}...")
        print()

    # Results table
    if verbose and composition.results:
        if use_rich and console:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Step", width=6)
            table.add_column("Command", ratio=2)
            table.add_column("Status", width=10)
            table.add_column("Duration", width=10)

            for i, result in enumerate(composition.results):
                step = composition.steps[i] if i < len(composition.steps) else None
                command = step.command if step else "?"
                command_short = command[:40] + "..." if len(command) > 40 else command

                if result.skipped:
                    status = "[yellow]SKIPPED[/yellow]"
                elif result.success:
                    status = "[green]✓[/green]"
                else:
                    status = "[red]✗[/red]"

                table.add_row(
                    str(result.step_index),
                    command_short,
                    status,
                    f"{result.duration_ms:.0f}ms",
                )

            console.print(table)
            console.print()
        else:
            print("Steps:")
            print("─" * 60)
            for i, result in enumerate(composition.results):
                step = composition.steps[i] if i < len(composition.steps) else None
                command = step.command if step else "?"

                status_str = "SKIPPED" if result.skipped else "✓" if result.success else "✗"
                print(f"  [{result.step_index}] {status_str} {command[:50]}")
                print(f"       {result.duration_ms:.0f}ms")
                if result.error:
                    print(f"       Error: {result.error}")
            print()


def cmd_compose(args: list[str], ctx: InvocationContext | None = None) -> int:
    """
    Handle 'kg compose' command.

    Modes:
    - Execute: kg compose "cmd1" "cmd2" ...
    - Save: kg compose --save <name> "cmd1" "cmd2"
    - Run saved: kg compose --run <name>
    - History: kg compose --history
    - List saved: kg compose --list
    """
    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse global flags
    json_mode = "--json" in args
    verbose = "--verbose" in args or "-v" in args
    continue_on_failure = "--continue" in args
    dry_run = "--dry-run" in args
    save_name: str | None = None
    run_name: str | None = None
    import_file: str | None = None
    export_file: str | None = None
    show_history = "--history" in args
    show_list = "--list" in args
    timeout_seconds: float | None = None

    # Parse --save and --run
    i = 0
    commands = []
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            i += 1
        elif arg in ("--verbose", "-v"):
            i += 1
        elif arg == "--continue":
            i += 1
        elif arg == "--dry-run":
            i += 1
        elif arg == "--save" and i + 1 < len(args):
            save_name = args[i + 1]
            i += 2
        elif arg == "--run" and i + 1 < len(args):
            run_name = args[i + 1]
            i += 2
        elif arg == "--import" and i + 1 < len(args):
            import_file = args[i + 1]
            i += 2
        elif arg == "--export" and i + 1 < len(args):
            export_file = args[i + 1]
            i += 2
        elif arg == "--timeout" and i + 1 < len(args):
            try:
                timeout_seconds = float(args[i + 1])
            except ValueError:
                print(f"Error: Invalid timeout value: {args[i + 1]}")
                return 1
            i += 2
        elif arg == "--history":
            i += 1
        elif arg == "--list":
            i += 1
        elif not arg.startswith("-"):
            commands.append(arg)
            i += 1
        else:
            i += 1

    # Import from YAML
    if import_file:
        return _cmd_import(
            import_file,
            export_file,
            dry_run,
            json_mode,
            verbose,
            continue_on_failure,
            timeout_seconds,
        )

    # Export to YAML
    if export_file and commands:
        return _cmd_export(commands, save_name, export_file, json_mode)

    # Show list of saved compositions
    if show_list:
        return _cmd_list(json_mode)

    # Show composition history
    if show_history:
        return _cmd_history(json_mode, verbose)

    # Run saved composition
    if run_name:
        return _cmd_run(run_name, json_mode, verbose, continue_on_failure, timeout_seconds)

    # Execute composition from commands
    if not commands:
        if json_mode:
            print(json.dumps({"error": "No commands provided"}))
        else:
            print("Error: No commands provided")
            _print_help()
        return 1

    return _cmd_execute(
        commands, save_name, json_mode, verbose, continue_on_failure, timeout_seconds, dry_run
    )


def _cmd_execute(
    commands: list[str],
    save_name: str | None,
    json_mode: bool,
    verbose: bool,
    continue_on_failure: bool,
    timeout_seconds: float | None,
    dry_run: bool = False,
) -> int:
    """Execute a composition from command list."""
    from services.compose import Composition, execute_composition
    from services.compose.store import get_composition_store

    # Create composition
    composition = Composition.from_commands(commands, name=save_name)

    # Dry-run mode: just show what would be executed
    if dry_run:
        if json_mode:
            print(json.dumps(composition.to_dict(), indent=2))
        else:
            try:
                from rich.console import Console
                from rich.table import Table

                console = Console()
                console.print(
                    f"\n[bold cyan]Dry Run: {composition.name or composition.id[:12]}[/bold cyan]"
                )
                console.print(f"[dim]Would execute {len(composition.steps)} steps[/dim]\n")

                table = Table(show_header=True, header_style="bold")
                table.add_column("Step", width=6)
                table.add_column("Command", ratio=1)
                table.add_column("Depends On", width=15)

                for step in composition.steps:
                    deps = ", ".join(str(d) for d in step.depends_on) if step.depends_on else "none"
                    table.add_row(str(step.index), step.command, deps)

                console.print(table)
                console.print()
            except ImportError:
                print(f"\nDry Run: {composition.name or composition.id[:12]}")
                print(f"Would execute {len(composition.steps)} steps\n")
                for step in composition.steps:
                    deps = ", ".join(str(d) for d in step.depends_on) if step.depends_on else "none"
                    print(f"  [{step.index}] {step.command} (depends: {deps})")
                print()
        return 0

    # Execute
    try:

        async def _execute_and_save() -> "Composition":
            comp = await execute_composition(
                composition,
                continue_on_failure=continue_on_failure,
                verbose=verbose,
                timeout_seconds=timeout_seconds,
            )
            # Save if named (skip if database not initialized)
            if save_name:
                try:
                    store = get_composition_store()
                    await store.save(comp)
                except Exception as e:
                    if verbose:
                        print(f"[compose] Warning: Could not save composition: {e}")
            return comp

        composition = asyncio.run(_execute_and_save())
    except Exception as e:
        if json_mode:
            print(json.dumps({"error": f"Execution failed: {e}"}))
        else:
            print(f"Error executing composition: {e}")
        return 1

    # Output result
    _print_composition_result(composition, json_mode, verbose)

    return 0 if composition.all_succeeded else 1


def _cmd_run(
    name: str,
    json_mode: bool,
    verbose: bool,
    continue_on_failure: bool,
    timeout_seconds: float | None,
) -> int:
    """Run a saved composition by name."""
    from services.compose import execute_composition
    from services.compose.store import get_composition_store
    from services.compose.types import Composition

    async def _get_and_run() -> "Composition | None":
        store = get_composition_store()
        saved = await store.get_by_name(name)

        if not saved:
            if json_mode:
                print(json.dumps({"error": f"Composition '{name}' not found"}))
            else:
                print(f"Error: Composition '{name}' not found")
                named = await store.list_named()
                print(f"\nAvailable compositions: {', '.join(named)}")
            return None

        # Create a new composition with the same steps
        composition = Composition.from_commands(
            saved.commands,
            name=f"{name} (run)",
        )

        # Execute
        return await execute_composition(
            composition,
            continue_on_failure=continue_on_failure,
            verbose=verbose,
            timeout_seconds=timeout_seconds,
        )

    try:
        composition = asyncio.run(_get_and_run())
        if composition is None:
            return 1
    except Exception as e:
        if json_mode:
            print(json.dumps({"error": f"Execution failed: {e}"}))
        else:
            print(f"Error executing composition: {e}")
        return 1

    # Output result
    _print_composition_result(composition, json_mode, verbose)

    return 0 if composition.all_succeeded else 1


def _cmd_history(json_mode: bool, verbose: bool) -> int:
    """Show composition history."""
    from services.compose.store import get_composition_store

    async def _get_history() -> list[Any]:
        store = get_composition_store()
        return await store.history(limit=20)

    history = asyncio.run(_get_history())

    if json_mode:
        print(json.dumps([c.to_dict() for c in history], indent=2))
        return 0

    if not history:
        print("No compositions in history.")
        return 0

    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        use_rich = True
    except ImportError:
        console = None
        use_rich = False

    if use_rich and console:
        console.print("\n[bold]Composition History[/bold]")
        console.print("[dim]" + "─" * 60 + "[/dim]")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Time", width=16)
        table.add_column("Name", width=20)
        table.add_column("Status", width=12)
        table.add_column("Steps", width=8)
        table.add_column("Duration", width=10)

        for comp in history:
            time_str = comp.created_at.strftime("%m-%d %H:%M") if comp.created_at else "???"
            name = comp.name or comp.id[:12]
            status = comp.last_status or "unknown"
            steps = f"{comp.last_success_count or 0}/{len(comp.commands)}"
            duration = f"{comp.last_duration_ms or 0:.0f}ms"

            # Determine color based on last execution
            if comp.last_success_count == len(comp.commands):
                status_color = "green"
            elif comp.last_failure_count and comp.last_failure_count > 0:
                status_color = "red"
            else:
                status_color = "yellow"

            table.add_row(
                time_str,
                name,
                f"[{status_color}]{status}[/{status_color}]",
                steps,
                duration,
            )

        console.print(table)
        console.print()
    else:
        print("\nComposition History")
        print("─" * 60)
        for comp in history:
            time_str = comp.created_at.strftime("%m-%d %H:%M") if comp.created_at else "???"
            name = comp.name or comp.id[:12]
            status = comp.last_status or "unknown"
            steps = f"{comp.last_success_count or 0}/{len(comp.commands)}"
            duration = f"{comp.last_duration_ms or 0:.0f}ms"
            print(f"  {time_str}  {name:20}  {status:12}  {steps} steps  {duration}")
        print()

    return 0


def _cmd_list(json_mode: bool) -> int:
    """List saved compositions."""
    from services.compose.store import get_composition_store

    async def _get_all() -> tuple[list[str], dict[str, Any] | None]:
        store = get_composition_store()
        named = await store.list_named()

        if not named:
            return named, None

        # Get details for all compositions
        details: dict[str, Any] = {}
        for name in named:
            comp = await store.get_by_name(name)
            if comp:
                details[name] = comp

        return named, details

    named, comp_details = asyncio.run(_get_all())

    if json_mode:
        if comp_details:
            compositions = [comp.to_dict() for comp in comp_details.values()]
            print(json.dumps(compositions, indent=2))
        else:
            print(json.dumps([], indent=2))
        return 0

    if not named:
        print("No saved compositions.")
        print('\nSave a composition with: kg compose --save <name> "cmd1" "cmd2"')
        return 0

    try:
        from rich.console import Console

        console = Console()
        use_rich = True
    except ImportError:
        console = None
        use_rich = False

    if use_rich and console and comp_details:
        console.print("\n[bold]Saved Compositions[/bold]")
        console.print("[dim]" + "─" * 60 + "[/dim]")
        for name in sorted(named):
            comp = comp_details.get(name)
            if comp:
                console.print(f"  [cyan]{name}[/cyan]")
                console.print(f"    {len(comp.commands)} commands")
                for i, cmd in enumerate(comp.commands[:3]):
                    console.print(f"      {i + 1}. {cmd[:50]}")
                if len(comp.commands) > 3:
                    console.print(f"      ... and {len(comp.commands) - 3} more")
        console.print()
    elif comp_details:
        print("\nSaved Compositions")
        print("─" * 60)
        for name in sorted(named):
            comp = comp_details.get(name)
            if comp:
                print(f"  {name}")
                print(f"    {len(comp.commands)} commands")
                for i, cmd in enumerate(comp.commands[:3]):
                    print(f"      {i + 1}. {cmd[:50]}")
                if len(comp.commands) > 3:
                    print(f"      ... and {len(comp.commands) - 3} more")
        print()

    return 0


def _cmd_import(
    import_file: str,
    export_file: str | None,
    dry_run: bool,
    json_mode: bool,
    verbose: bool,
    continue_on_failure: bool,
    timeout_seconds: float | None,
) -> int:
    """Import composition from YAML and optionally execute."""
    from pathlib import Path

    from services.compose import Composition, execute_composition

    # Read YAML file
    try:
        yaml_content = Path(import_file).read_text()
    except FileNotFoundError:
        print(f"Error: File not found: {import_file}")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    # Parse composition
    try:
        composition = Composition.from_yaml(yaml_content)
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return 1

    # If export specified, export and exit
    if export_file:
        return _cmd_export_composition(composition, export_file, json_mode)

    # Otherwise execute
    return _cmd_execute(
        [s.command for s in composition.steps],
        composition.name,
        json_mode,
        verbose,
        continue_on_failure,
        timeout_seconds,
        dry_run,
    )


def _cmd_export(
    commands: list[str],
    name: str | None,
    export_file: str,
    json_mode: bool,
) -> int:
    """Export composition to YAML."""
    from services.compose import Composition

    composition = Composition.from_commands(commands, name=name)
    return _cmd_export_composition(composition, export_file, json_mode)


def _cmd_export_composition(composition: Any, export_file: str, json_mode: bool) -> int:
    """Export a composition to YAML file."""
    from pathlib import Path

    try:
        yaml_content = composition.to_yaml()
        Path(export_file).write_text(yaml_content)

        if not json_mode:
            print(f"Composition exported to: {export_file}")
        return 0
    except Exception as e:
        if json_mode:
            print(json.dumps({"error": f"Export failed: {e}"}))
        else:
            print(f"Error exporting composition: {e}")
        return 1


def _print_help() -> None:
    """Print compose command help."""
    help_text = """
kg compose - Chain kg operations with unified witnessing

"Every step leaves a mark. Every composition tells a story."

USAGE:
  kg compose <cmd1> <cmd2> ...           Execute commands in sequence
  kg compose --save <name> <cmd1> ...    Save composition for reuse
  kg compose --run <name>                Run saved composition
  kg compose --history                   Show execution history
  kg compose --list                      List saved compositions
  kg compose --import <file>             Import and run from YAML
  kg compose --export <file> <cmd1> ...  Export composition to YAML

OPTIONS:
  --continue                Continue on failure (default: exit on first failure)
  --verbose, -v             Show step-by-step progress
  --json                    Output as JSON
  --dry-run                 Preview composition without executing
  --timeout <seconds>       Timeout per step in seconds

EXAMPLES:
  # Execute a composition
  kg compose "audit spec/witness.md --principles" "probe health --jewel witness"

  # Save for reuse
  kg compose --save "validate-witness" \\
    "audit spec/protocols/witness.md --full" \\
    "probe identity --target services/witness"

  # Run saved composition
  kg compose --run "validate-witness"

  # Continue on failure
  kg compose --continue "audit spec/a.md" "audit spec/b.md" "audit spec/c.md"

  # Dry-run mode
  kg compose --dry-run "audit spec/witness.md" "probe health"

  # With timeout
  kg compose --timeout 30 "audit spec/witness.md" "probe health"

  # Export to YAML
  kg compose --export my-composition.yaml "audit spec/witness.md" "probe health"

  # Import from YAML
  kg compose --import my-composition.yaml

  # View history
  kg compose --history
  kg compose --list

COMPOSITION TRACE:
  Each composition creates a unified trace linking all step marks.
  View the trace with: kg witness show --trace <trace_id>

PHILOSOPHY:
  A single kg command is atomic. A composition is molecular.
  The trace provides the causal narrative from stimulus to outcome.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 5)
"""
    print(help_text.strip())


__all__ = ["cmd_compose"]
