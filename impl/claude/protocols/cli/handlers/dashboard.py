"""
Dashboard Handler: Real-time system health TUI.

A live metrics dashboard showing K-gent, Metabolism, Flux, and Triad health
with recent AGENTESE traces. Updates in real-time at configurable intervals.

Usage:
    kg dashboard          # Launch dashboard (live metrics)
    kg dashboard --demo   # Launch with demo data
    kg dashboard --help   # Show help

Options:
    --demo              Use demo data instead of live metrics
    --interval <secs>   Refresh interval in seconds (default: 1.0)
    --help, -h          Show this help

Keybindings (in dashboard):
    q       Quit
    r       Force refresh
    d       Toggle demo mode
    1-4     Focus panel (K-gent, Metabolism, Flux, Triad)

Example:
    kg dashboard
    -> Shows live 4-panel dashboard with real-time updates

Philosophy: "Make the system's metabolism visible."
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for dashboard command."""
    print(__doc__)
    print()
    print("PANELS:")
    print("  K-GENT      Mode, garden patterns, interactions, last dream")
    print("  METABOLISM  Pressure, temperature, fever state, sparkline history")
    print("  FLUX        Events/sec, queue depth, active agents, throughput")
    print("  TRIAD       Database health (PostgreSQL, Qdrant, Redis), CDC lag")
    print()
    print("TRACES:")
    print("  Shows recent AGENTESE path invocations with latency")
    print()
    print("OPTIONS:")
    print("  --demo              Use randomized demo data (no live services)")
    print("  --interval <secs>   Metric collection interval (default: 1.0)")
    print("  --help, -h          Show this help")


def cmd_dashboard(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Real-time System Health Dashboard.

    Displays live metrics from all kgents subsystems in a TUI.

    Panels:
    - K-gent: Soul mode, garden patterns, interaction count
    - Metabolism: Pressure gauge, temperature, fever state
    - Flux: Event throughput, queue depth, active agents
    - Triad: Database health (PostgreSQL, Qdrant, Redis)

    Plus a recent traces panel showing AGENTESE invocations.
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("dashboard", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    demo_mode = "--demo" in args

    # Parse interval
    refresh_interval = 1.0
    for i, arg in enumerate(args):
        if arg == "--interval" and i + 1 < len(args):
            try:
                refresh_interval = float(args[i + 1])
            except ValueError:
                print(f"Invalid interval: {args[i + 1]}")
                return 1

    # Check if Textual is available
    try:
        import textual  # noqa: F401
    except ImportError:
        print("Dashboard requires Textual. Install with:")
        print("  pip install textual")
        print()
        print("For now, here's a text summary of metrics:")
        return _fallback_dashboard(demo_mode, ctx)

    # Run the TUI dashboard
    try:
        from agents.i.screens.dashboard import DashboardApp

        app = DashboardApp(demo_mode=demo_mode, refresh_interval=refresh_interval)
        app.run()
        return 0

    except ImportError as e:
        print(f"Failed to import dashboard: {e}")
        return 1
    except Exception as e:
        print(f"Dashboard error: {e}")
        return 1


def _fallback_dashboard(demo_mode: bool, ctx: "InvocationContext | None") -> int:  # noqa: C901
    """
    Fallback text-based dashboard when Textual is not available.

    Shows a single snapshot of metrics in text format.
    """
    import asyncio

    from agents.i.data.dashboard_collectors import (
        DashboardMetrics,
        collect_metrics,
        create_demo_metrics,
    )

    async def get_metrics() -> DashboardMetrics:
        if demo_mode:
            return create_demo_metrics()
        else:
            return await collect_metrics()

    try:
        metrics = asyncio.run(get_metrics())
    except Exception as e:
        print(f"Failed to collect metrics: {e}")
        return 1

    # Print text summary
    print()
    print("╭─── kgents dashboard (text mode) ───╮")
    print("│                                     │")

    # K-gent
    print("│ K-GENT                              │")
    if metrics.kgent.is_online:
        print(f"│   Mode: {metrics.kgent.mode.upper():<28}│")
        print(
            f"│   Garden: {metrics.kgent.garden_patterns} patterns ({metrics.kgent.garden_trees} trees) │"
        )
        print(f"│   Dream: {metrics.kgent.dream_age_str:<27}│")
    else:
        print("│   [offline]                         │")
    print("│                                     │")

    # Metabolism
    print("│ METABOLISM                          │")
    if metrics.metabolism.is_online:
        pct = int(metrics.metabolism.pressure * 100)
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"│   Pressure: {bar} {pct}%        │")
        fever = "FEVER!" if metrics.metabolism.in_fever else "No"
        print(f"│   Fever: {fever:<28}│")
    else:
        print("│   [offline]                         │")
    print("│                                     │")

    # Flux
    print("│ FLUX                                │")
    if metrics.flux.is_online:
        print(
            f"│   Events/sec: {metrics.flux.events_per_second:.1f}                  │"
        )
        print(f"│   Queue: {metrics.flux.queue_depth} pending                 │")
    else:
        print("│   [offline]                         │")
    print("│                                     │")

    # Triad
    print("│ TRIAD                               │")
    if metrics.triad.is_online:
        print(f"│   Status: {metrics.triad.status_text:<26}│")
        overall = int(metrics.triad.overall * 100)
        print(f"│   Overall: {overall}%                       │")
    else:
        print("│   [offline]                         │")
    print("│                                     │")

    # Traces
    print("│ RECENT TRACES                       │")
    if metrics.traces:
        for trace in metrics.traces[:3]:
            line = trace.render(show_timestamp=False)[:35]
            print(f"│   {line:<34}│")
    else:
        print("│   (no traces)                       │")

    print("│                                     │")
    print("╰─────────────────────────────────────╯")
    print()
    print("Install Textual for full TUI: pip install textual")

    return 0
