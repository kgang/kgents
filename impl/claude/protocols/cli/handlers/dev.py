"""
Dev Handler: Live reload development for K-Terrarium agents.

Start agents in dev mode with source mounted and file watching for
automatic reload on code changes.

Usage:
    kgents dev <agent>             # Start agent in dev mode
    kgents dev <agent> --attach    # Attach for interactive debugging
    kgents dev --stop              # Stop all dev mode pods
    kgents dev --stop <agent>      # Stop specific dev pod
    kgents dev --status            # Show dev mode status

Options:
    --attach      Attach to container shell for debugging
    --stop        Stop dev mode (all agents or specific one)
    --status      Show status of all dev mode pods
    --source PATH Override source directory to mount

Example:
    $ kgents dev b-gent
    Starting B-gent in dev mode...
    Dev pod created: b-gent-dev
    Waiting for pod to be ready...
    Streaming logs (Ctrl+C to stop)...

    [dev] Starting B-gent in dev mode...
    [dev] Watching /app/agents for changes...

    # Edit impl/claude/agents/b/main.py
    [dev] Changed: main.py
    [dev] Reloading...
    [dev] Starting agent...

    $ kgents dev --status
    Dev Mode Status
    ================
    b-gent-dev    B    Running    Ready

    $ kgents dev --stop
    Stopped 1 dev pod(s): b-gent-dev
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any


def cmd_dev(args: list[str]) -> int:
    """Start agent in dev mode with live reload."""
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    # Parse args
    options = _parse_args(args)

    if options.get("error"):
        print(f"Error: {options['error']}")
        return 1

    # Handle --status
    if options.get("status"):
        return asyncio.run(_cmd_status())

    # Handle --stop
    if options.get("stop"):
        return asyncio.run(_cmd_stop(options.get("agent")))

    # Start dev mode
    agent = options.get("agent")
    if not agent:
        print("Error: Agent name required")
        print("Usage: kgents dev <agent> [--attach]")
        return 1

    return asyncio.run(
        _cmd_start(
            agent,
            attach=options.get("attach", False),
            source=options.get("source"),
        )
    )


async def _cmd_start(
    agent: str,
    attach: bool = False,
    source: str | None = None,
) -> int:
    """Start agent in dev mode."""
    try:
        from infra.k8s.dev_mode import create_dev_mode

        from infra.k8s import ClusterStatus, KindCluster
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure infra.k8s is properly installed")
        return 1

    # Check cluster
    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("Cluster not running. Run 'kgents infra init' first.")
        return 1

    def on_progress(msg: str) -> None:
        print(msg)

    dev = create_dev_mode(on_progress=on_progress)

    source_path = Path(source) if source else None

    print("K-Terrarium Dev Mode")
    print("=" * 40)

    try:
        result = await dev.start(
            genus=agent,
            attach=attach,
            source_path=source_path,
        )

        if result.success:
            print(f"\n{result.message}")
            return 0
        else:
            print(f"\nFailed: {result.message}")
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted. Dev pod still running.")
        print(f"Stop with: kgents dev --stop {agent}")
        return 0


async def _cmd_stop(agent: str | None = None) -> int:
    """Stop dev mode."""
    try:
        from infra.k8s.dev_mode import create_dev_mode
    except ImportError as e:
        print(f"Import error: {e}")
        return 1

    def on_progress(msg: str) -> None:
        print(msg)

    dev = create_dev_mode(on_progress=on_progress)

    if agent:
        print(f"Stopping {agent} dev mode...")
    else:
        print("Stopping all dev mode pods...")

    result = await dev.stop(agent)

    print(result.message)
    return 0 if result.success else 1


async def _cmd_status() -> int:
    """Show dev mode status."""
    try:
        from infra.k8s.dev_mode import create_dev_mode
    except ImportError as e:
        print(f"Import error: {e}")
        return 1

    dev = create_dev_mode()
    pods = await dev.status()

    print("Dev Mode Status")
    print("=" * 40)

    if not pods:
        print("No dev pods running")
        return 0

    # Header
    print(f"{'NAME':<18} {'GENUS':<6} {'PHASE':<12} {'READY'}")
    print("-" * 40)

    # Rows
    for pod in pods:
        ready_str = "Ready" if pod.get("ready") else "Not Ready"
        print(
            f"{pod.get('name', 'unknown'):<18} "
            f"{pod.get('genus', '?'):<6} "
            f"{pod.get('phase', 'Unknown'):<12} "
            f"{ready_str}"
        )

    return 0


def _parse_args(args: list[str]) -> dict[str, Any]:
    """Parse command line arguments."""
    options: dict[str, Any] = {}
    i = 0

    while i < len(args):
        arg = args[i]

        if arg == "--attach":
            options["attach"] = True
            i += 1
        elif arg == "--stop":
            options["stop"] = True
            i += 1
        elif arg == "--status":
            options["status"] = True
            i += 1
        elif arg == "--source":
            if i + 1 >= len(args):
                options["error"] = "--source requires a path"
                return options
            options["source"] = args[i + 1]
            i += 2
        elif arg.startswith("-"):
            options["error"] = f"Unknown option: {arg}"
            return options
        else:
            # Agent name
            options["agent"] = arg
            i += 1

    return options
