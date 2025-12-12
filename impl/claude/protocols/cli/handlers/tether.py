"""
Tether Handler: Attach to running agents with signal forwarding.

The debuggability crisis resolved: Ctrl+C actually stops the agent.

Usage:
    kgents tether <agent>           # Attach to agent
    kgents tether <agent> --debug   # Attach with debugpy on :5678
    kgents tether <agent> --port N  # Custom debug port

Options:
    --debug       Enable debugpy injection for remote debugging
    --port PORT   Debug port (default: 5678)

Example:
    $ kgents tether b-gent
    [tether] Attached to b-gent-deployment-xyz
    [tether] Ctrl+C will stop the agent

    # Press Ctrl+C
    ^C
    [tether] Forwarding SIGTERM to b-gent-deployment-xyz...
    [tether] SIGTERM delivered
    [tether] Detached from b-gent-deployment-xyz

    $ kgents tether b-gent --debug
    [tether] Debugger listening on localhost:5678
    [tether] Attached to b-gent-deployment-xyz
    # Connect VSCode debugger to localhost:5678

Principle alignment:
    - Transparent Infrastructure: The developer feels like the agent runs locally
    - Debuggability: Stack traces appear in your terminal
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any


def cmd_tether(args: list[str]) -> int:
    """
    Attach to a running agent with signal forwarding.

    Dispatches to tether protocol.
    """
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    # Parse args
    options = _parse_args(args)

    if options.get("error"):
        print(f"Error: {options['error']}")
        return 1

    agent = options.get("agent")
    if not agent:
        print("Error: Agent name required")
        print("Usage: kgents tether <agent> [--debug] [--port PORT]")
        return 1

    return asyncio.run(
        _cmd_tether(
            agent,
            debug=options.get("debug", False),
            port=options.get("port"),
        )
    )


async def _cmd_tether(
    agent: str,
    debug: bool = False,
    port: int | None = None,
) -> int:
    """Execute the tether command."""
    try:
        from infra.k8s import ClusterStatus, KindCluster
        from infra.k8s.tether import TetherState, create_tether
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure infra.k8s is properly installed")
        return 1

    # Check cluster
    cluster = KindCluster()
    if cluster.status() != ClusterStatus.RUNNING:
        print("K-Terrarium not running. Run 'kgents infra init' first.")
        return 1

    def on_state_change(state: TetherState) -> None:
        """Handle state changes."""
        if state == TetherState.ERROR:
            print("[tether] Connection error")

    tether = create_tether(on_state_change=on_state_change)

    print("K-Terrarium Tether")
    print("=" * 40)

    try:
        result = await tether.attach(
            agent_id=agent,
            debug=debug,
            debug_port=port,
        )

        if result.success:
            print(f"\n{result.message}")
            return 0
        else:
            print(f"\nFailed: {result.message}")
            return 1

    except KeyboardInterrupt:
        # This is expected - the tether handles it
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


def _parse_args(args: list[str]) -> dict[str, Any]:
    """Parse command line arguments."""
    options: dict[str, Any] = {}
    i = 0

    while i < len(args):
        arg = args[i]

        if arg == "--debug":
            options["debug"] = True
            i += 1
        elif arg == "--port":
            if i + 1 >= len(args):
                options["error"] = "--port requires a number"
                return options
            try:
                options["port"] = int(args[i + 1])
            except ValueError:
                options["error"] = f"Invalid port: {args[i + 1]}"
                return options
            i += 2
        elif arg.startswith("-"):
            options["error"] = f"Unknown option: {arg}"
            return options
        else:
            # Agent name
            options["agent"] = arg
            i += 1

    return options
