"""
Ghost Handler: Living Filesystem projection.

DevEx V4 Phase 2 - The Sensorium.

Projects system state to .kgents/ghost/ for peripheral awareness.
Open thought_stream.md in a split pane to watch the system think.

Usage:
    kgents ghost              # One-shot projection
    kgents ghost --daemon     # Start background daemon (3-min interval)
    kgents ghost --show       # Show current ghost state
    kgents ghost --thought    # Add manual thought to stream

Files in .kgents/ghost/:
    thought_stream.md   - System narrative / inner monologue
    tension_map.json    - Spec/impl mismatches, volatility
    health.status       - One-line status for IDE
    context.json        - Current context summary

Example:
    $ kgents ghost
    [GHOST] Projected to .kgents/ghost/
      thought_stream.md  (3 entries)
      tension_map.json   (0 tensions)
      health.status      cortex:healthy surprise:0.23

    # Then open in split pane:
    $ code .kgents/ghost/thought_stream.md
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def cmd_ghost(args: list[str]) -> int:
    """
    Project system state to .kgents/ghost/ files.

    Creates a Living Filesystem for peripheral awareness.
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    daemon_mode = "--daemon" in args
    show_mode = "--show" in args
    thought_mode = "--thought" in args

    if help_mode:
        print(__doc__)
        return 0

    # Get project root
    from protocols.cli.hollow import find_kgents_root

    project_root = find_kgents_root()
    if project_root is None:
        project_root = Path.cwd()

    if daemon_mode:
        return _run_daemon(project_root)
    elif show_mode:
        return _show_ghost(project_root)
    elif thought_mode:
        return _add_thought(project_root, args)
    else:
        return asyncio.run(_project_once(project_root))


async def _project_once(project_root: Path) -> int:
    """One-shot projection."""
    from protocols.cli.devex.ghost_writer import create_ghost_writer

    writer = create_ghost_writer(project_root)

    # Try to configure with available integrations
    _configure_writer(writer)

    # Add a projection thought
    writer.add_thought(
        "Manual projection triggered via CLI",
        source="cli",
        tags=["projection"],
    )

    projection = await writer.project()

    # Output
    ghost_dir = project_root / ".kgents" / "ghost"
    print(f"[GHOST] Projected to {ghost_dir}/")
    print(f"  thought_stream.md  ({len(projection.thoughts)} entries)")
    print(f"  tension_map.json   ({len(projection.tensions)} tensions)")
    print(f"  health.status      {projection.health_line}")
    print()
    print("Open thought_stream.md in a split pane for peripheral awareness.")

    return 0


def _run_daemon(project_root: Path) -> int:
    """Run daemon in foreground."""
    from protocols.cli.devex.ghost_writer import create_ghost_writer

    writer = create_ghost_writer(project_root, interval_seconds=180.0)
    _configure_writer(writer)

    print("[GHOST] Starting daemon (Ctrl+C to stop)")
    print("  Interval: 3 minutes")
    print(f"  Directory: {project_root / '.kgents' / 'ghost'}")
    print()

    writer.add_thought(
        "Daemon started",
        source="ghost",
        tags=["lifecycle"],
    )

    try:
        asyncio.run(_daemon_main(writer))
    except KeyboardInterrupt:
        print("\n[GHOST] Daemon stopped")
        return 0

    return 0


async def _daemon_main(writer) -> None:
    """Async daemon main loop."""
    # Initial projection
    await writer.project()
    print("[GHOST] Initial projection complete")

    # Start daemon loop
    await writer.start_daemon()

    # Keep running until interrupted
    while True:
        await asyncio.sleep(1)


def _show_ghost(project_root: Path) -> int:
    """Show current ghost state."""
    import json

    ghost_dir = project_root / ".kgents" / "ghost"

    if not ghost_dir.exists():
        print("[GHOST] No ghost directory found")
        print(f"  Run 'kgents ghost' to create {ghost_dir}/")
        return 0

    print(f"[GHOST] {ghost_dir}/")
    print()

    # Health status
    health_path = ghost_dir / "health.status"
    if health_path.exists():
        print(f"Health: {health_path.read_text().strip()}")
        print()

    # Context
    context_path = ghost_dir / "context.json"
    if context_path.exists():
        try:
            context = json.loads(context_path.read_text())
            print(f"Last projection: {context.get('timestamp', 'unknown')}")
            print(f"Projection count: {context.get('projection_count', 0)}")
            if "hydrate_current" in context:
                print(f"HYDRATE: {context['hydrate_current']}")
            print()
        except Exception:
            pass

    # Tension summary
    tension_path = ghost_dir / "tension_map.json"
    if tension_path.exists():
        try:
            data = json.loads(tension_path.read_text())
            summary = data.get("summary", {})
            total = summary.get("total", 0)
            if total > 0:
                high = summary.get("high", 0)
                medium = summary.get("medium", 0)
                low = summary.get("low", 0)
                print(f"Tensions: {total} (high:{high} med:{medium} low:{low})")
                print()
        except Exception:
            pass

    # Recent thoughts
    thought_path = ghost_dir / "thought_stream.md"
    if thought_path.exists():
        content = thought_path.read_text()
        lines = [l for l in content.split("\n") if l.startswith("- *")]
        if lines:
            print("Recent thoughts:")
            for line in lines[:5]:
                print(f"  {line}")
        print()

    return 0


def _add_thought(project_root: Path, args: list[str]) -> int:
    """Add a manual thought to the stream."""
    from protocols.cli.devex.ghost_writer import create_ghost_writer

    # Extract thought content from args
    content_args = [a for a in args if not a.startswith("-")]
    if not content_args:
        print("Usage: kgents ghost --thought <message>")
        return 1

    content = " ".join(content_args)

    writer = create_ghost_writer(project_root)
    writer.add_thought(content, source="user", tags=["manual"])

    # Project to persist
    asyncio.run(writer.project())

    print(f"[GHOST] Added thought: {content}")
    return 0


def _configure_writer(writer) -> None:
    """Try to configure writer with available integrations."""
    from protocols.cli.hollow import get_lifecycle_state

    state = get_lifecycle_state()
    if state is None:
        return

    try:
        writer.configure(
            synapse=getattr(state, "synapse", None),
            observer=getattr(state, "cortex_observer", None),
            field=getattr(state, "semantic_field", None),
        )
    except Exception:
        pass
