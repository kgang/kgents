"""
Witness Handler: The 8th Crown Jewel CLI interface.

"The ghost is not a haunting—it's a witnessing that becomes a doing."

The Witness observes developer activity and builds trust over time:
- manifest: Show witness health and daemon status
- thoughts: Stream of observations
- trust: Trust level for git users
- start: Start background daemon
- stop: Stop background daemon
- capture: Manually capture a thought

Trust Levels:
- L0 READ_ONLY: Observe only, no suggestions
- L1 BOUNDED: Make bounded suggestions (file-scoped)
- L2 PROACTIVE: Make proactive suggestions (project-scoped)
- L3 AUTONOMOUS: Execute approved action patterns

Usage:
    kg witness                  # Show witness status (manifest)
    kg witness manifest         # Show witness health + daemon status
    kg witness thoughts         # Show recent thought stream
    kg witness thoughts -n 20   # Show 20 most recent thoughts
    kg witness trust <email>    # Show trust level for git user
    kg witness start            # Start background daemon
    kg witness stop             # Stop background daemon
    kg witness capture "text"   # Manually capture a thought

AGENTESE Paths:
    self.witness.manifest       # Witness status
    self.witness.thoughts       # Thought stream
    self.witness.trust          # Trust level query
    self.witness.capture        # Capture thought
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# AGENTESE Path Mapping
# =============================================================================


WITNESS_SUBCOMMAND_MAP = {
    "manifest": "self.witness.manifest",
    "status": "self.witness.status",
    "thoughts": "self.witness.thoughts",
    "trust": "self.witness.trust",
    "capture": "self.witness.capture",
    "logs": None,  # File-based, not AGENTESE
    "start": None,  # Daemon management, not AGENTESE
    "stop": None,  # Daemon management, not AGENTESE
}


# =============================================================================
# Async Helpers
# =============================================================================


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously, handling running event loops."""
    try:
        asyncio.get_running_loop()
        # If we get here, an event loop is already running
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running event loop, safe to use asyncio.run
        return asyncio.run(coro)


# =============================================================================
# Help
# =============================================================================


def print_help() -> None:
    """Print witness command help."""
    help_text = """
kg witness - The Witnessing Ghost (8th Crown Jewel)

"The ghost is not a haunting—it's a witnessing that becomes a doing."

Commands:
  kg witness                    Show witness status (alias for manifest)
  kg witness manifest           Show witness health + daemon status
  kg witness status             Show bus stats + uptime
  kg witness logs               Tail witness log file
  kg witness logs -n 50         Show last 50 log lines
  kg witness thoughts           Show recent thought stream
  kg witness thoughts -n 20     Show 20 most recent thoughts
  kg witness trust <email>      Show trust level for git user
  kg witness start              Start background daemon
  kg witness stop               Stop background daemon
  kg witness capture "text"     Manually capture a thought

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  -n, --limit N                 Limit results (default: 10 for logs, 10 for thoughts)
  -f, --follow                  Follow log output (like tail -f)

Trust Levels:
  L0 READ_ONLY                  Observe only, no suggestions
  L1 BOUNDED                    Make bounded suggestions (file-scoped)
  L2 PROACTIVE                  Make proactive suggestions (project-scoped)
  L3 AUTONOMOUS                 Execute approved action patterns

AGENTESE Paths:
  self.witness.manifest         Witness status
  self.witness.status           Bus stats + uptime
  self.witness.thoughts         Thought stream
  self.witness.trust            Trust level query
  self.witness.capture          Capture thought

Daemon:
  The witness daemon runs in the background, watching for git events.
  PID file: ~/.kgents/witness.pid
  Log file: ~/.kgents/witness.log

Examples:
  kg witness                    # Quick status check
  kg witness status             # Detailed bus stats
  kg witness logs -n 20         # Recent log entries
  kg witness logs -f            # Follow log in real-time
  kg witness thoughts           # What has the witness observed?
  kg witness trust user@email   # What trust level does this user have?
  kg witness start              # Start watching
  kg witness stop               # Stop watching
  kg witness capture "Noticed pattern X in auth module"
"""
    print(help_text.strip())


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_witness(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Witness: The 8th Crown Jewel - Observing Developer Activity.

    kg witness - Trust-building observation and eventual assistance.
    """
    # Parse args
    if "--help" in args or "-h" in args:
        print_help()
        return 0

    # Parse path visibility flags
    args, show_paths, trace_mode = parse_path_flags(args)
    apply_path_flags(show_paths, trace_mode)

    json_output = "--json" in args
    args = [a for a in args if a != "--json"]

    # Parse follow flag (-f or --follow)
    follow = "-f" in args or "--follow" in args
    args = [a for a in args if a not in ("-f", "--follow")]

    # Parse limit option (-n or --limit)
    limit = 10
    clean_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-n", "--limit") and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif arg.startswith("-"):
            i += 1  # Skip other flags
        else:
            clean_args.append(arg)
            i += 1

    # Get subcommand
    subcommand = clean_args[0].lower() if clean_args else "manifest"

    # Run async handler
    result: int = _run_async(
        _async_route(
            subcommand,
            clean_args[1:],
            json_output,
            limit=limit,
            follow=follow,
            ctx=ctx,
        )
    )
    return result


async def _async_route(
    subcommand: str,
    args: list[str],
    json_output: bool,
    limit: int = 10,
    follow: bool = False,
    ctx: Any = None,
) -> int:
    """Route to appropriate witness handler."""
    try:
        match subcommand:
            case "manifest":
                return await _handle_manifest(json_output, ctx)
            case "status":
                return await _handle_status(json_output, ctx)
            case "logs":
                return await _handle_logs(json_output, limit, follow, ctx)
            case "thoughts":
                return await _handle_thoughts(args, json_output, limit, ctx)
            case "trust":
                return await _handle_trust(args, json_output, ctx)
            case "start":
                return await _handle_start(json_output, ctx)
            case "stop":
                return await _handle_stop(json_output, ctx)
            case "capture":
                return await _handle_capture(args, json_output, ctx)
            case _:
                print(f"Unknown subcommand: {subcommand}")
                print("Use 'kg witness --help' for usage")
                return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


# =============================================================================
# Handler: manifest
# =============================================================================


async def _handle_manifest(json_output: bool, ctx: Any) -> int:
    """Handle witness manifest command - show health + daemon status."""
    display_path_header(
        path="self.witness.manifest",
        aspect="manifest",
        effects=["STATUS_RETRIEVED"],
    )

    from services.bootstrap import get_service
    from services.witness.daemon import get_daemon_status

    # Get persistence status
    try:
        persistence = await get_service("witness_persistence")
        status = await persistence.manifest()
    except Exception as e:
        # Graceful degradation if persistence not available
        status = None
        print(f"  (persistence unavailable: {e})")

    # Get daemon status
    daemon_status = get_daemon_status()

    if json_output:
        import json

        output = {
            "daemon": daemon_status,
            "persistence": {
                "total_thoughts": status.total_thoughts if status else 0,
                "total_actions": status.total_actions if status else 0,
                "trust_count": status.trust_count if status else 0,
                "reversible_actions": status.reversible_actions if status else 0,
                "storage_backend": status.storage_backend if status else "unknown",
            }
            if status
            else None,
        }
        print(json.dumps(output, indent=2))
    else:
        # Rich output
        daemon_icon = "" if daemon_status["running"] else ""
        daemon_label = (
            f"Running (PID: {daemon_status['pid']})" if daemon_status["running"] else "Stopped"
        )

        print()
        print(" Witness Status (8th Crown Jewel)")
        print("" * 45)
        print(f"  Daemon:       {daemon_icon} {daemon_label}")

        if status:
            print(f"  Thoughts:     {status.total_thoughts}")
            print(f"  Actions:      {status.total_actions}")
            print(f"  Trust Records:{status.trust_count}")
            print(f"  Reversible:   {status.reversible_actions}")
            print("" * 45)
            print(f"  Backend:      {status.storage_backend}")
        else:
            print("  (persistence data unavailable)")
            print("" * 45)

        if daemon_status["running"]:
            print("   Watching for git events...")
        else:
            print("   Run 'kg witness start' to begin observation")

        print()

    return 0


# =============================================================================
# Handler: status (bus stats + uptime)
# =============================================================================


async def _handle_status(json_output: bool, ctx: Any) -> int:
    """Handle witness status command - show bus stats and uptime."""
    display_path_header(
        path="self.witness.status",
        aspect="manifest",
        effects=["STATUS_RETRIEVED"],
    )

    from pathlib import Path

    from services.witness.bus import get_witness_bus_manager
    from services.witness.daemon import get_daemon_status

    # Get daemon status
    daemon_status = get_daemon_status()

    # Get bus stats
    bus_manager = get_witness_bus_manager()
    bus_stats = bus_manager.stats

    # Calculate uptime from PID file modification time
    uptime_str = "N/A"
    if daemon_status["running"]:
        pid_file = Path(daemon_status["pid_file"])
        if pid_file.exists():
            import time
            from datetime import datetime

            mtime = pid_file.stat().st_mtime
            uptime_secs = time.time() - mtime
            hours, remainder = divmod(int(uptime_secs), 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                uptime_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                uptime_str = f"{minutes}m {seconds}s"
            else:
                uptime_str = f"{seconds}s"

    if json_output:
        import json

        output = {
            "daemon": daemon_status,
            "uptime": uptime_str,
            "bus_stats": {
                "synergy_bus": bus_stats.get("synergy_bus", {}),
                "event_bus": bus_stats.get("event_bus", {}),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        daemon_icon = "🟢" if daemon_status["running"] else "🔴"
        daemon_label = (
            f"Running (PID: {daemon_status['pid']})" if daemon_status["running"] else "Stopped"
        )

        synergy_stats = bus_stats.get("synergy_bus", {})
        event_stats = bus_stats.get("event_bus", {})

        print()
        print("👁 Witness Status")
        print("─" * 50)
        print(f"  Daemon:         {daemon_icon} {daemon_label}")
        print(f"  Uptime:         {uptime_str}")
        print()
        print("📡 SynergyBus (Cross-Jewel)")
        print("─" * 50)
        print(f"  Events emitted: {synergy_stats.get('total_emitted', 0)}")
        print(f"  Topic handlers: {synergy_stats.get('topic_count', 0)}")
        print(f"  Wildcard subs:  {synergy_stats.get('wildcard_count', 0)}")
        print(f"  Errors:         {synergy_stats.get('total_errors', 0)}")
        print()
        print("📺 EventBus (UI Fan-out)")
        print("─" * 50)
        print(f"  Events emitted: {event_stats.get('total_emitted', 0)}")
        print(f"  Subscribers:    {event_stats.get('subscriber_count', 0)}")
        print(f"  Dropped:        {event_stats.get('dropped_count', 0)}")
        print()

        if not daemon_status["running"]:
            print("💡 Run 'kg witness start' to begin observation")
            print()

    return 0


# =============================================================================
# Handler: logs
# =============================================================================


async def _handle_logs(json_output: bool, limit: int, follow: bool, ctx: Any) -> int:
    """Handle witness logs command - tail the witness log file."""
    import sys
    import time
    from pathlib import Path

    log_file = Path.home() / ".kgents" / "witness.log"

    if not log_file.exists():
        if json_output:
            import json

            print(json.dumps({"error": "Log file not found", "path": str(log_file)}))
        else:
            print()
            print("📄 No log file found")
            print(f"   Path: {log_file}")
            print("   Run 'kg witness start' to create logs")
            print()
        return 1

    if json_output:
        import json

        lines = log_file.read_text().splitlines()
        tail_lines = lines[-limit:] if len(lines) > limit else lines
        output = {
            "path": str(log_file),
            "total_lines": len(lines),
            "showing": len(tail_lines),
            "lines": tail_lines,
        }
        print(json.dumps(output, indent=2))
        return 0

    # Rich output
    print()
    print(f"📜 Witness Logs ({log_file})")
    print("─" * 60)

    if follow:
        # Follow mode - like tail -f
        print(f"   Following log (Ctrl+C to stop)...")
        print("─" * 60)

        try:
            with open(log_file, "r") as f:
                # Go to end of file
                f.seek(0, 2)

                while True:
                    line = f.readline()
                    if line:
                        print(line, end="")
                    else:
                        time.sleep(0.5)
        except KeyboardInterrupt:
            print()
            print("─" * 60)
            print("   Stopped following.")
            print()
    else:
        # Show last N lines
        lines = log_file.read_text().splitlines()
        tail_lines = lines[-limit:] if len(lines) > limit else lines

        if not tail_lines:
            print("   (empty log file)")
        else:
            for line in tail_lines:
                print(f"  {line}")

        print("─" * 60)
        print(f"   Showing {len(tail_lines)} of {len(lines)} lines")
        print()

    return 0


# =============================================================================
# Handler: thoughts
# =============================================================================


async def _handle_thoughts(args: list[str], json_output: bool, limit: int, ctx: Any) -> int:
    """Handle witness thoughts command - show recent thought stream."""
    display_path_header(
        path="self.witness.thoughts",
        aspect="witness",
        effects=["THOUGHTS_RETRIEVED"],
    )

    from services.bootstrap import get_service

    try:
        persistence = await get_service("witness_persistence")
        thoughts = await persistence.get_thoughts(limit=limit)
    except Exception as e:
        print(f"Error retrieving thoughts: {e}")
        return 1

    if json_output:
        import json

        output = {
            "count": len(thoughts),
            "thoughts": [
                {
                    "content": t.content,
                    "source": t.source,
                    "tags": list(t.tags),
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in thoughts
            ],
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        if not thoughts:
            print()
            print(" No thoughts yet")
            print("  The witness is still observing...")
            print("  Run 'kg witness start' to begin watching")
            print()
        else:
            print()
            print(f" Recent Thoughts ({len(thoughts)})")
            print("" * 50)

            for t in thoughts:
                time_str = t.timestamp.strftime("%H:%M")
                source_tag = f"[{t.source}]"
                # Truncate content for display
                content = t.content[:60] + "..." if len(t.content) > 60 else t.content
                print(f"  {time_str} {source_tag:10} {content}")

            print()

    return 0


# =============================================================================
# Handler: trust
# =============================================================================


async def _handle_trust(args: list[str], json_output: bool, ctx: Any) -> int:
    """Handle witness trust command - show trust level for git user."""
    display_path_header(
        path="self.witness.trust",
        aspect="manifest",
        effects=["TRUST_RETRIEVED"],
    )

    if not args:
        print("Error: git email required")
        print("Usage: kg witness trust <git_email>")
        return 1

    git_email = args[0]

    from services.bootstrap import get_service

    try:
        persistence = await get_service("witness_persistence")
        trust = await persistence.get_trust_level(git_email)
    except Exception as e:
        print(f"Error retrieving trust: {e}")
        return 1

    if json_output:
        import json

        output = {
            "email": git_email,
            "trust_level": trust.trust_level.name,
            "trust_level_value": trust.trust_level.value,
            "raw_level": trust.raw_level,
            "observation_count": trust.observation_count,
            "successful_operations": trust.successful_operations,
            "confirmed_suggestions": trust.confirmed_suggestions,
            "total_suggestions": trust.total_suggestions,
            "acceptance_rate": trust.acceptance_rate,
            "decay_applied": trust.decay_applied,
            "last_active": trust.last_active.isoformat(),
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        # Trust level visualization
        level_icons = {
            0: " L0 READ_ONLY",
            1: " L1 BOUNDED",
            2: " L2 PROACTIVE",
            3: " L3 AUTONOMOUS",
        }
        level_desc = {
            0: "Observe only, no suggestions",
            1: "Make bounded suggestions (file-scoped)",
            2: "Make proactive suggestions (project-scoped)",
            3: "Execute approved action patterns",
        }

        level_value = trust.trust_level.value
        icon = level_icons.get(level_value, f" L{level_value}")
        desc = level_desc.get(level_value, "Unknown")

        print()
        print(f"  Trust Level: {icon}")
        print("" * 40)
        print(f"  {desc}")
        print("" * 40)

        # Progress to next level (if not L3)
        if level_value < 3:
            next_level = level_value + 1
            # Calculate progress (simplified heuristic)
            if level_value == 0:
                obs_target = 100
                obs_progress = min(trust.observation_count, obs_target) / obs_target
                print(f"  Progress to L{next_level}:")
                bar = "" * int(obs_progress * 10) + "" * (10 - int(obs_progress * 10))
                print(
                    f"    Observations: {trust.observation_count}/{obs_target} {bar} {obs_progress:.0%}"
                )
            elif level_value == 1:
                ops_target = 50
                ops_progress = min(trust.successful_operations, ops_target) / ops_target
                print(f"  Progress to L{next_level}:")
                bar = "" * int(ops_progress * 10) + "" * (10 - int(ops_progress * 10))
                print(
                    f"    Successful ops: {trust.successful_operations}/{ops_target} {bar} {ops_progress:.0%}"
                )
            elif level_value == 2:
                if trust.total_suggestions > 0:
                    acc_progress = trust.acceptance_rate
                else:
                    acc_progress = 0.0
                print(f"  Progress to L{next_level}:")
                bar = "" * int(acc_progress * 10) + "" * (10 - int(acc_progress * 10))
                print(f"    Acceptance rate: {acc_progress:.0%} {bar}")

            print("" * 40)

        print(f"  Observations:    {trust.observation_count}")
        print(f"  Successful ops:  {trust.successful_operations}")
        print(f"  Suggestions:     {trust.confirmed_suggestions}/{trust.total_suggestions}")

        if trust.decay_applied:
            print()
            print("   Trust decay applied (inactivity)")

        print()

    return 0


# =============================================================================
# Handler: start
# =============================================================================


async def _handle_start(json_output: bool, ctx: Any) -> int:
    """Handle witness start command - start background daemon."""
    from services.witness.daemon import check_daemon_status, start_daemon

    # Check if already running
    is_running, existing_pid = check_daemon_status()
    if is_running:
        if json_output:
            import json

            print(json.dumps({"status": "already_running", "pid": existing_pid}))
        else:
            print(f" Witness already running (PID: {existing_pid})")
        return 0

    # Start daemon
    try:
        pid = start_daemon()

        if json_output:
            import json

            print(json.dumps({"status": "started", "pid": pid}))
        else:
            print(f" Witness started (PID: {pid})")
            print("   Watching for git events...")
            print("   Log: ~/.kgents/witness.log")

        return 0

    except Exception as e:
        if json_output:
            import json

            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print(f" Failed to start witness: {e}")
        return 1


# =============================================================================
# Handler: stop
# =============================================================================


async def _handle_stop(json_output: bool, ctx: Any) -> int:
    """Handle witness stop command - stop background daemon."""
    from services.witness.daemon import check_daemon_status, stop_daemon

    # Check if running
    is_running, pid = check_daemon_status()
    if not is_running:
        if json_output:
            import json

            print(json.dumps({"status": "not_running"}))
        else:
            print(" Witness not running")
        return 0

    # Stop daemon
    success = stop_daemon()

    if json_output:
        import json

        print(json.dumps({"status": "stopped" if success else "error", "pid": pid}))
    else:
        if success:
            print(f" Witness stopped (was PID: {pid})")
        else:
            print(f" Failed to stop witness (PID: {pid})")

    return 0 if success else 1


# =============================================================================
# Handler: capture
# =============================================================================


async def _handle_capture(args: list[str], json_output: bool, ctx: Any) -> int:
    """Handle witness capture command - manually capture a thought."""
    display_path_header(
        path="self.witness.capture",
        aspect="define",
        effects=["THOUGHT_CAPTURED"],
    )

    if not args:
        print("Error: content required")
        print('Usage: kg witness capture "your observation here"')
        return 1

    content = " ".join(args).strip()
    if not content:
        print("Error: content cannot be empty")
        return 1

    from services.bootstrap import get_service
    from services.witness.polynomial import Thought

    try:
        persistence = await get_service("witness_persistence")

        thought = Thought(
            content=content,
            source="cli",
            tags=("manual", "cli"),
        )

        result = await persistence.save_thought(thought)

        if json_output:
            import json

            output = {
                "status": "captured",
                "thought_id": result.thought_id,
                "content": result.content[:100],
                "source": result.source,
                "tags": result.tags,
            }
            print(json.dumps(output, indent=2))
        else:
            print(f" Captured: {content[:50]}...")
            print(f"   ID: {result.thought_id}")
            print(f"   Source: {result.source}")

        return 0

    except Exception as e:
        if json_output:
            import json

            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print(f" Failed to capture thought: {e}")
        return 1


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "cmd_witness",
    "print_help",
]
