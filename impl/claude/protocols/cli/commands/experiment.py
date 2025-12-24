"""
kg experiment: Evidence-Gathering Experiments with Bayesian Stopping.

"Uncertainty triggers experiments, not guessing."

Commands:
    kg experiment generate --spec "..." [--n N] [--adaptive] [--confidence 0.95]
    kg experiment parse --input "..." --strategy "..." [--n N]
    kg experiment laws --target "..." --laws identity,associativity
    kg experiment history [--today] [--type TYPE]
    kg experiment resume <id>

This is Phase 3 of the Claude Code CLI Integration Strategy.

Philosophy:
    Every experiment gathers evidence.
    Every experiment emits witness marks.
    Bayesian stopping prevents wasteful over-testing.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_experiment(exp_dict: dict[str, Any], verbose: bool = False) -> None:
    """Print a single experiment."""
    console = _get_console()

    exp_id = exp_dict.get("id", "")[:12]
    exp_type = exp_dict.get("config", {}).get("type", "unknown")
    status = exp_dict.get("status", "unknown")
    created = exp_dict.get("created_at", "")

    # Format timestamp
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        ts_str = dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, AttributeError):
        ts_str = "???"

    # Get evidence if completed
    evidence = exp_dict.get("evidence")
    if evidence:
        success_rate = evidence.get("success_rate", 0.0)
        trials_total = evidence.get("trials_total", 0)
        result_str = f"{success_rate:.1%} ({trials_total} trials)"
    else:
        result_str = "in progress"

    if console:
        # Rich output
        status_style = {
            "completed": "green",
            "stopped": "yellow",
            "failed": "red",
            "running": "blue",
        }.get(status, "dim")

        console.print(
            f"  [{status_style}]{status:10s}[/{status_style}]  "
            f"[dim]{ts_str}[/dim]  {exp_id}  "
            f"[cyan]{exp_type:8s}[/cyan]  {result_str}"
        )
    else:
        # Plain text
        print(f"  {status:10s}  {ts_str}  {exp_id}  {exp_type:8s}  {result_str}")


def cmd_generate(args: list[str]) -> int:
    """Run code generation experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="kg experiment generate",
        description="Run code generation experiment via VoidHarness",
    )
    parser.add_argument("--spec", required=True, help="Code specification to implement")
    parser.add_argument("--n", type=int, default=10, help="Number of trials (default: 10)")
    parser.add_argument(
        "--adaptive", action="store_true", help="Use Bayesian adaptive stopping"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="Confidence threshold for stopping (default: 0.95)",
    )
    parser.add_argument(
        "--max-trials",
        type=int,
        default=100,
        help="Maximum trials (hard cap, default: 100)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1

    # Import services
    from services.experiment import GenerateConfig

    # Create config
    config = GenerateConfig(
        spec=parsed.spec,
        adaptive=parsed.adaptive,
        confidence_threshold=parsed.confidence,
        max_trials=parsed.max_trials,
        n=parsed.n,
    )

    # Run experiment (all async operations in single event loop)
    console = _get_console()
    if console and not parsed.json:
        with console.status(f"[bold blue]Running experiment with {parsed.n} trials..."):
            experiment = asyncio.run(_run_generate_and_save(config))
    else:
        experiment = asyncio.run(_run_generate_and_save(config))

    # Output
    if parsed.json:
        print(json.dumps(experiment.to_dict(), indent=2))
    else:
        if console:
            console.print()
            console.print(f"[green]Experiment {experiment.id} completed[/green]")
            if experiment.evidence:
                console.print(
                    f"  Success rate: {experiment.evidence.success_rate:.1%} "
                    f"({experiment.evidence.trials_success}/{experiment.evidence.trials_total})"
                )
                console.print(
                    f"  Mean confidence: {experiment.evidence.mean_confidence:.2f}"
                )
                if experiment.evidence.stopped_early:
                    console.print("  [yellow]Stopped early (Bayesian criterion)[/yellow]")
        else:
            print(f"\nExperiment {experiment.id} completed")
            if experiment.evidence:
                print(
                    f"  Success rate: {experiment.evidence.success_rate:.1%} "
                    f"({experiment.evidence.trials_success}/{experiment.evidence.trials_total})"
                )

    return 0


async def _run_generate_and_save(config: GenerateConfig):
    """Run generation experiment and save to store (async wrapper)."""
    from models.base import get_engine
    from models.experiment import ExperimentModel
    from services.experiment import ExperimentRunner
    from services.experiment.store import get_experiment_store

    # Ensure experiments table exists
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: ExperimentModel.__table__.create(sync_conn, checkfirst=True)
        )

    # Run experiment
    runner = ExperimentRunner(emit_marks=True)
    experiment = await runner.run(config)

    # Save to store
    store = get_experiment_store()
    await store.save(experiment)

    return experiment


async def _get_experiments(parsed):
    """Get experiments from store (async wrapper)."""
    from models.base import get_engine
    from models.experiment import ExperimentModel
    from services.experiment.store import get_experiment_store

    # Ensure experiments table exists
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: ExperimentModel.__table__.create(sync_conn, checkfirst=True)
        )

    store = get_experiment_store()

    if parsed.today:
        return await store.list_today()
    elif parsed.type:
        return await store.list_by_type(parsed.type, limit=parsed.limit)
    else:
        return await store.list_recent(limit=parsed.limit)


async def _get_experiment(experiment_id: str):
    """Get experiment by ID (async wrapper)."""
    from models.base import get_engine
    from models.experiment import ExperimentModel
    from services.experiment.store import get_experiment_store

    # Ensure experiments table exists
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: ExperimentModel.__table__.create(sync_conn, checkfirst=True)
        )

    store = get_experiment_store()
    return await store.get(experiment_id)


def cmd_history(args: list[str]) -> int:
    """Show experiment history."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="kg experiment history", description="Show experiment history"
    )
    parser.add_argument("--today", action="store_true", help="Show only today's experiments")
    parser.add_argument("--type", help="Filter by experiment type")
    parser.add_argument("--limit", type=int, default=20, help="Limit results (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1

    # Get experiments (all async operations in single event loop)
    experiments = asyncio.run(_get_experiments(parsed))

    # Output
    if parsed.json:
        print(json.dumps([e.to_dict() for e in experiments], indent=2))
    else:
        console = _get_console()
        if console:
            title = "Today's Experiments" if parsed.today else "Recent Experiments"
            if parsed.type:
                title = f"{parsed.type.title()} Experiments"

            console.print()
            console.print(f"[bold]{title}[/bold]")
            console.print()

        if not experiments:
            if console:
                console.print("[dim]No experiments found[/dim]")
            else:
                print("No experiments found")
        else:
            for exp in experiments:
                _print_experiment(exp.to_dict())

        if console:
            console.print()

    return 0


def cmd_resume(args: list[str]) -> int:
    """Resume an experiment."""
    if not args:
        print("Usage: kg experiment resume <experiment_id>")
        return 1

    experiment_id = args[0]

    # Get experiment (all async operations in single event loop)
    experiment = asyncio.run(_get_experiment(experiment_id))

    if not experiment:
        console = _get_console()
        if console:
            console.print(f"[red]Experiment {experiment_id} not found[/red]")
        else:
            print(f"Experiment {experiment_id} not found")
        return 1

    # TODO: Implement experiment resumption
    print(f"Resumption not yet implemented for {experiment_id}")
    print(f"Type: {experiment.config.type.value}")
    print(f"Status: {experiment.status.value}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Experiment command entry point."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("kg experiment - Evidence-Gathering Experiments")
        print()
        print("Commands:")
        print('  generate --spec "..."       Run code generation experiment')
        print("  history [--today]           Show experiment history")
        print("  resume <id>                 Resume an experiment")
        print()
        print("Examples:")
        print('  kg experiment generate --spec "def add(a, b): return a + b" --n 10')
        print("  kg experiment generate --spec \"...\" --adaptive --confidence 0.95")
        print("  kg experiment history --today")
        return 0

    subcommand = argv[0]
    remaining = argv[1:]

    if subcommand == "generate":
        return cmd_generate(remaining)
    elif subcommand == "history":
        return cmd_history(remaining)
    elif subcommand == "resume":
        return cmd_resume(remaining)
    elif subcommand == "parse":
        print("Parse experiments not yet implemented")
        return 1
    elif subcommand == "laws":
        print("Law experiments not yet implemented")
        return 1
    else:
        print(f"Unknown subcommand: {subcommand}")
        print('Run "kg experiment" for usage')
        return 1


# Alias for compose executor compatibility
cmd_experiment = main


if __name__ == "__main__":
    sys.exit(main())
